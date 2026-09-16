import os
import sys
import asyncio
import json
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

from server.services.openai_grading import OPENAI_MODEL as _OPENAI_MODEL, score_with_openai, _fallback_score

from server.database import get_db_connection
from server.utils import get_image_bytes, trigger_socket_notify, grading_queue

async def grading_worker():
    while True:
        task = await grading_queue.get()
        conn = None
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
                missing_image = False
                img_list = []
                img_mime_list = []
                image_paths_json = ans['image_paths']
                if image_paths_json:
                    import json
                    paths = json.loads(image_paths_json)
                    for path in paths:
                        raw_bytes = await get_image_bytes(path)
                        if not raw_bytes:
                            missing_image = True
                        if raw_bytes:
                            img_list.append(raw_bytes)
                            if path.endswith('.png'):
                                mime = 'image/png'
                            elif path.endswith('.webp'):
                                mime = 'image/webp'
                            elif path.endswith('.gif'):
                                mime = 'image/gif'
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
                            if not qb:
                                missing_image = True
                            if qb:
                                q_img_list.append(qb)
                                q_img_mime_list.append('image/png' if qp.endswith('.png') else 'image/webp' if qp.endswith('.webp') else 'image/gif' if qp.endswith('.gif') else 'image/jpeg')
                    except Exception:
                        missing_image = True
                elif q.get('image_path'):
                    qp = q['image_path']
                    qb = await get_image_bytes(qp)
                    if not qb:
                        missing_image = True
                    if qb:
                        q_img_list.append(qb)
                        q_img_mime_list.append('image/png' if qp.endswith('.png') else 'image/webp' if qp.endswith('.webp') else 'image/gif' if qp.endswith('.gif') else 'image/jpeg')
                rubrics_data = None
                if q.get('rubrics'):
                    try:
                        rubrics_data = json.loads(q['rubrics'])
                    except Exception:
                        rubrics_data = None
                
                safe_print(f"\n[Question ID: {q_id}] Question: {q.get('text') or '(See Attachment)'}")
                safe_print(f"Student Answer: {answer_text or '(Handwritten Image)'}")
                safe_print(f"Max Score: {q['score']} Points")

                if missing_image:
                    ai_result = _fallback_score(q['score'])
                    ai_result['feedback'] = 'ไม่สามารถอ่านภาพแนบได้ครบ กรุณาให้ผู้สอนตรวจภาพต้นฉบับและประเมินด้วยตนเอง'
                else:
                    ai_result = await score_with_openai(question_text=q.get('text') or '', answer_text=answer_text, max_score=q['score'], answer_key=q.get('answer_key'), rubrics=rubrics_data, image_bytes_list=img_list, image_mime_list=img_mime_list, q_image_bytes_list=q_img_list, q_image_mime_list=q_img_mime_list)
                total_ai_score += ai_result['score']
                confidences.append(ai_result['confidence'])
                q_metrics = json.dumps({**ai_result.get('metrics', {}), 'transcription': ai_result.get('transcription', '')}, ensure_ascii=False)
                cursor.execute('UPDATE submission_answers SET ai_score = ?, ai_feedback = ?, ai_confidence = ?, quality_metrics = ? WHERE id = ?', (ai_result['score'], ai_result['feedback'], ai_result['confidence'], q_metrics, ans['id']))

                safe_print(f"AI Result ({_OPENAI_MODEL}): Score = {ai_result['score']} / {q['score']} | Confidence = {ai_result['confidence']}")
                safe_print(f"AI Feedback: {ai_result['feedback']}")
                safe_print("----------------------------------------------------------------------")

            cursor.execute('SELECT ai_confidence FROM submission_answers WHERE submission_id = ?', (submission_id,))
            all_confidences = [row['ai_confidence'] for row in cursor.fetchall()]
            new_status = 'needs_review' if not all_confidences or 'low' in all_confidences else 'ready'
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
                        data={'exam_id': exam_id, 'room_id': room_id, 'link': f'/room/{room_id}/exam/{exam_id}/review'}
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
                        data={'exam_id': exam_id, 'room_id': room_id, 'link': f'/room/{room_id}/exam/{exam_id}/review'}
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
                            data={'exam_id': exam_id, 'room_id': room_id, 'link': f'/room/{room_id}/exam/{exam_id}/review'}
                        )
                        grading_worker._last_notify[key] = now
            conn.close()
            conn = None
            print(f'[Grading Worker] Finished submission {submission_id}')
        except Exception as e:
            print(f'[Grading Worker] Error processing task: {e}')
            import traceback
            traceback.print_exc()
        finally:
            if conn is not None:
                conn.close()
            grading_queue.task_done()

# Backward-compatible import for existing Chapter 3 endpoint names.
score_with_gemini = score_with_openai

