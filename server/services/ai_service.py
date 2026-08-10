import os
import sys
import asyncio
import random
import json
import httpx
import json as json_module
import google.genai as genai
from google.genai import types as genai_types
from typing import Optional, List

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        try:
            msg = ' '.join(str(a) for a in args)
            sys.stdout.buffer.write(msg.encode('utf-8', errors='replace') + b'\n')
            sys.stdout.flush()
        except Exception:
            pass

def _get_genai_client():
    key = os.getenv('GEMINI_API_KEY', '').strip()
    if key and key != 'your-gemini-api-key-here':
        try:
            return genai.Client(api_key=key)
        except Exception as e:
            safe_print(f"[Gemini Client Error] {e}")
            return None
    return None

_genai_client = None
_USE_GEMINI = True
_GEMINI_MODEL = 'gemini-flash-latest'

from server.database import get_db_connection
from server.utils import get_image_bytes, trigger_socket_notify, grading_queue

async def grading_worker():
    while True:
        task = await grading_queue.get()
        try:
            submission_id = task.get('submission_id')
            room_id = task['room_id']
            exam_id = task['exam_id']
            user_id = task.get('user_id')
            specific_q_id = task.get('question_id')
            safe_print("\n======================================================================")
            safe_print(f"[Grading Worker] Processing Submission ID: {submission_id} (Exam: {exam_id}, Student: {user_id or 'Unknown'})")
            safe_print("======================================================================")
            conn = get_db_connection()

            cursor = conn.cursor()
            cursor.execute('SELECT * FROM submission_answers WHERE submission_id = ?', (submission_id,))
            answers = cursor.fetchall()
            cursor.execute('SELECT * FROM questions WHERE exam_id = ? ORDER BY order_index', (exam_id,))
            questions = {q['id']: dict(q) for q in cursor.fetchall()}
            total_ai_score = 0.0
            confidences = []
            for ans in answers:
                q_id = ans['question_id']
                if specific_q_id and q_id != specific_q_id:
                    continue
                q = questions.get(q_id)
                if not q:
                    continue
                answer_text = ans['answer_text'] or ''
                img_list = []
                img_mime_list = []
                image_paths_json = ans['image_paths']
                if image_paths_json:
                    import json
                    paths = json.loads(image_paths_json)
                    for path in paths:
                        raw_bytes = await get_image_bytes(path)
                        if raw_bytes:
                            img_list.append(raw_bytes)
                            if path.endswith('.png'):
                                mime = 'image/png'
                            elif path.endswith('.webp'):
                                mime = 'image/webp'
                            else:
                                mime = 'image/jpeg'
                            img_mime_list.append(mime)
                q_img_list = []
                q_img_mime_list = []
                q_image_paths = q.get('image_paths')
                if q_image_paths:
                    try:
                        q_paths = json.loads(q_image_paths)
                        for qp in q_paths:
                            qb = await get_image_bytes(qp)
                            if qb:
                                q_img_list.append(qb)
                                q_img_mime_list.append('image/png' if qp.endswith('.png') else 'image/webp' if qp.endswith('.webp') else 'image/jpeg')
                    except Exception:
                        pass
                elif q.get('image_path'):
                    qp = q['image_path']
                    qb = await get_image_bytes(qp)
                    if qb:
                        q_img_list.append(qb)
                        q_img_mime_list.append('image/png' if qp.endswith('.png') else 'image/webp' if qp.endswith('.webp') else 'image/jpeg')
                rubrics_data = None
                if q.get('rubrics'):
                    try:
                        rubrics_data = json.loads(q['rubrics'])
                    except Exception:
                        rubrics_data = None
                
                safe_print(f"\n[Question ID: {q_id}] Question: {q.get('text') or '(See Attachment)'}")
                safe_print(f"Student Answer: {answer_text or '(Handwritten Image)'}")
                safe_print(f"Max Score: {q['score']} Points")

                ai_result = await score_with_gemini(question_text=q.get('text') or '', answer_text=answer_text, max_score=q['score'], answer_key=q.get('answer_key'), rubrics=rubrics_data, image_bytes_list=img_list[:5], image_mime_list=img_mime_list[:5], q_image_bytes_list=q_img_list[:5], q_image_mime_list=q_img_mime_list[:5])
                total_ai_score += ai_result['score']
                confidences.append(ai_result['confidence'])
                q_metrics = json.dumps(ai_result.get('metrics', {})) if ai_result.get('metrics') else None
                cursor.execute('UPDATE submission_answers SET ai_score = ?, ai_feedback = ?, ai_confidence = ?, quality_metrics = ? WHERE id = ?', (ai_result['score'], ai_result['feedback'], ai_result['confidence'], q_metrics, ans['id']))

                safe_print(f"AI Result (Gemini): Score = {ai_result['score']} / {q['score']} | Confidence = {ai_result['confidence']}")
                safe_print(f"AI Feedback: {ai_result['feedback']}")
                safe_print("----------------------------------------------------------------------")

            new_status = 'needs_review' if 'low' in confidences else 'ready'
            cursor.execute('SELECT SUM(COALESCE(teacher_score, ai_score, 0)) as total FROM submission_answers WHERE submission_id = ?', (submission_id,))
            total_score_row = cursor.fetchone()
            new_total_score = total_score_row['total'] if total_score_row and total_score_row['total'] else 0.0
            cursor.execute('UPDATE submissions SET status = ?, total_score = ?, graded_by_ai = 1 WHERE id = ?', (new_status, round(new_total_score, 1), submission_id))
            safe_print(f"[Grading Worker] Completed Submission ID {submission_id}: Total Score = {round(new_total_score, 1)} | Status = {new_status}")
            safe_print("======================================================================\n")
            conn.commit()
            cursor.execute('SELECT r.teacher_id, r.name as room_name FROM rooms r WHERE r.id = ?', (room_id,))
            teacher_row = cursor.fetchone()
            if teacher_row:
                teacher_id = teacher_row['teacher_id']
                room_name = teacher_row['room_name']
                
                # 2. เมื่อ AI ไม่มั่นใจ (Notify for low confidence)
                if new_status == 'needs_review':
                    await trigger_socket_notify(
                        user_id=teacher_id,
                        notify_type='ai_alert',
                        message=f'[{room_name}] AI ไม่มั่นใจในผลตรวจข้อสอบบางส่วน โปรดตรวจสอบด้วยตนเอง',
                        data={'exam_id': exam_id, 'room_id': room_id}
                    )

                # 1. เมื่อข้อสอบมีนักเรียนส่งครบทุกคนเเละ ai ประเมินครบเเล้ว
                cursor.execute('SELECT COUNT(*) as count FROM enrollments WHERE room_id = ?', (room_id,))
                total_students = cursor.fetchone()['count']
                cursor.execute('SELECT COUNT(*) as count FROM submissions WHERE exam_id = ?', (exam_id,))
                total_submissions = cursor.fetchone()['count']
                cursor.execute('SELECT COUNT(*) as count FROM submissions WHERE exam_id = ? AND graded_by_ai = 1', (exam_id,))
                total_graded = cursor.fetchone()['count']

                if total_students > 0 and total_students == total_submissions == total_graded:
                    await trigger_socket_notify(
                        user_id=teacher_id,
                        notify_type='ai_complete',
                        message=f'[{room_name}] นักเรียนส่งครบทุกคนและ AI ตรวจเสร็จสิ้นทั้งหมดแล้ว!',
                        data={'exam_id': exam_id, 'room_id': room_id}
                    )
                else:
                    # Fallback to the debounced "item graded" notification if not complete yet
                    import time
                    now = time.time()
                    key = f"{teacher_id}_{exam_id}"
                    if not hasattr(grading_worker, "_last_notify"):
                        grading_worker._last_notify = {}
                    
                    last_time = grading_worker._last_notify.get(key, 0)
                    if now - last_time > 30:
                        await trigger_socket_notify(
                            user_id=teacher_id,
                            notify_type='ai_graded',
                            message=f'[{room_name}] AI กำลังตรวจข้อสอบ (มีรายการใหม่ตรวจเสร็จแล้ว)',
                            data={'exam_id': exam_id, 'room_id': room_id}
                        )
                        grading_worker._last_notify[key] = now
            conn.close()
            print(f'[Grading Worker] Finished submission {submission_id}')
        except Exception as e:
            print(f'[Grading Worker] Error processing task: {e}')
            import traceback
            traceback.print_exc()
        finally:
            grading_queue.task_done()

def _fallback_score(answer_text: str, max_score: float) -> dict:
    """Fallback when Gemini AI is unavailable or rate-limited."""
    return {
        'score': 0.0,
        'confidence': 'low',
        'feedback': 'ไม่สามารถเชื่อมต่อระบบ AI ประเมินผลได้ (หรือโควต้า AI ชั่วคราวเต็ม) ขอให้อาจารย์ผู้สอนตรวจสอบและประเมินคะแนนข้อนี้ด้วยตนเอง'
    }

async def score_with_gemini(question_text: str, answer_text: str, max_score: float, answer_key: Optional[str]=None, rubrics: Optional[list]=None, image_bytes_list: Optional[List[bytes]]=None, image_mime_list: Optional[List[str]]=None, q_image_bytes_list: Optional[List[bytes]]=None, q_image_mime_list: Optional[List[str]]=None) -> dict:
    """
    Score a student answer using Gemini AI.
    Returns: {score: float, confidence: 'high'|'medium'|'low', feedback: str}
    Falls back to rule-based scoring if Gemini is unavailable.
    """
    client = _get_genai_client()
    if not client:
        safe_print("[Gemini Info] Gemini API Key not configured or invalid, using fallback engine")
        return _fallback_score(answer_text, max_score)
    rubric_text = ''
    if rubrics:
        rubric_lines = []
        for r in rubrics:
            name = r.get('name') or r.get('label', '')
            score = r.get('score') or r.get('maxScore', '')
            desc = r.get('description', '')
            rubric_lines.append(f"- {name} ({score} คะแนน){(': ' + desc if desc else '')}")
        rubric_text = '\n'.join(rubric_lines)
    answer_key_section = ''
    if answer_key:
        answer_key_section = '## แนวคำตอบ\n' + answer_key + '\n'
    rubric_section = ''
    if rubric_text:
        rubric_section = '## เกณฑ์การให้คะแนน\n' + rubric_text + '\n'
    student_answer_section = answer_text.strip() if answer_text and answer_text.strip() else '(ไม่มีคำตอบแบบข้อความ)'
    q_text = question_text or '(ไม่มีข้อความโจทย์ - โปรดดูจากรูปภาพประกอบโจทย์)'
    prompt = f"""คุณคือคุณครูผู้เชี่ยวชาญในการตรวจข้อสอบอัตนัยวิชาโครงสร้างข้อมูล (Data Structures) กรุณาประเมินคำตอบของนักเรียนโดยเน้นที่ความถูกต้องของเนื้อหาเชิงเทคนิคเท่านั้น (ไม่ต้องสนใจความสละสลวยของภาษา)

## ข้อมูลโจทย์
ข้อความโจทย์: {q_text}
**สำคัญ**: หากข้อความโจทย์ว่างเปล่า ให้คุณวิเคราะห์เนื้อหาคำถามจากรูปภาพที่อยู่ในส่วนของ 'Question Images' ที่แนบไป

## คะแนนเต็ม
{max_score} คะแนน

{answer_key_section}{rubric_section}## ข้อมูลคำตอบของนักเรียน
ข้อความคำตอบ: {student_answer_section}
**สำคัญ**: หากนักเรียนส่งรูปภาพมาในส่วนของ 'Student Answer Images' ให้คุณวิเคราะห์คำตอบจากรูปภาพเหล่านั้นประกอบด้วย

## คำสั่งการตรวจอย่างเข้มงวด
1. วิเคราะห์โจทย์: ทำความเข้าใจสิ่งที่โจทย์ต้องการ
2. วิเคราะห์คำตอบ: ตรวจสอบคำตอบของนักเรียนว่าตรงตามความถูกต้องของหลักการหรือไม่
3. **ตรวจสอบความชัดเจนของลายมือและรูปภาพ (Handwriting Legibility Check)**:
   - หากรูปภาพลายมือของนักเรียนมีความหวัด ลายมืออ่านยาก ตัวอักษรซ้อนทับกัน ภาพเบลอ หรือก้ำกวมสูงเกินกว่าจะอ่านได้อย่างมั่นใจ 100%
   - คุณ **ต้อง** กำหนดค่า "confidence" เป็น "low" หรือ "medium" ทันที! (ห้ามตอบ "high" เด็ดขาดหากลายมืออ่านยากหรือภาพเบลอ)
   - พร้อมระบุใน "feedback" ว่า: "ลายมือหรือรูปภาพมีความหวัดและอ่านยากเกินไป ขอให้อาจารย์ผู้สอนตรวจสอบและประเมินคะแนนซ้ำด้วยตนเอง"
4. การให้คะแนน: พิจารณาคะแนนตามความถูกต้องเชิงเทคนิค

ตอบกลับเป็น JSON ที่มีรูปแบบดังนี้เท่านั้น (งดเว้นการพิมพ์ข้อความอื่นๆ นอก JSON):
{{
  "score": <คะแนนที่ได้ เป็นตัวเลขทศนิยม 1 ตำแหน่ง ระหว่าง 0 ถึง {max_score}>,
  "confidence": <"high" หากอ่านได้ชัดเจนและมั่นใจมาก, "medium" หากปานกลาง, "low" หากลายมืออ่านยาก ภาพเบลอ หรือไม่มั่นใจ>,
  "feedback": <คำอธิบายการให้คะแนนและชี้จุดผิดเชิงเทคนิคเป็นภาษาไทยที่กระชับและเข้าใจง่าย>
}}"""
    for attempt in range(3):
        try:
            contents: list = [prompt]
            if q_image_bytes_list and q_image_mime_list:
                contents.append('--- [Question Images] ---')
                for bts, mime in zip(q_image_bytes_list, q_image_mime_list):
                    contents.append(genai_types.Part.from_bytes(data=bts, mime_type=mime))
            if image_bytes_list and image_mime_list:
                contents.append('--- [Student Answer Images] ---')
                for bts, mime in zip(image_bytes_list, image_mime_list):
                    contents.append(genai_types.Part.from_bytes(data=bts, mime_type=mime))
            response = await client.aio.models.generate_content(model=_GEMINI_MODEL, contents=contents, config=genai_types.GenerateContentConfig(temperature=0.2, response_mime_type='application/json'))
            raw = response.text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
            data = json.loads(raw)
            score = float(data.get('score', 0))
            score = max(0.0, min(float(max_score), score))
            confidence = data.get('confidence', 'medium')
            if confidence not in ('high', 'medium', 'low'):
                confidence = 'medium'
            feedback = str(data.get('feedback', ''))
            return {'score': round(score, 1), 'confidence': confidence, 'feedback': feedback}
        except Exception as e:
            err_str = str(e)
            if attempt < 2 and ('429' in err_str or 'RESOURCE_EXHAUSTED' in err_str or 'Quota' in err_str):
                safe_print(f"[Gemini Rate Limit] 429 Quota Exceeded. Retrying in 4 seconds... (Attempt {attempt + 1}/3)")
                await asyncio.sleep(4)
                continue
            safe_print(f'[Gemini Error] {e} — falling back to heuristic')
            return _fallback_score(answer_text, max_score)

