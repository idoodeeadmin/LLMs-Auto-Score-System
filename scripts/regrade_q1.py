import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from scripts.run_dataset_benchmark import load_dataset
from server.services.openai_grading import score_with_openai

# Concise, effective pedagogical rubric for Question 1
Q1_RUBRIC = [
    {
        "name": "Row-major vs Column-major",
        "score": 2.0,
        "description": (
            "ประเมินการอธิบายความแตกต่างของ Row-major vs Column-major (คะแนนเต็ม 2.0 คะแนน: ให้ได้เฉพาะ 2.0, 1.0 หรือ 0.0):\n\n"
            "• 2.0 คะแนน: อธิบายความต่างได้ชัดเจนทั้งสองฝั่ง ว่า Row-major คือการจัดเก็บ/เรียงลำดับตามแนวแถว (Row/แนวนอน) และ Column-major คือการจัดเก็บ/เรียงลำดับตามแนวคอลัมน์ (Column/แนวตั้ง/หลัก) หรือระบุลำดับการไล่ดัชนี index / การคำนวณตำแหน่ง address ได้ถูกต้อง (ให้อนุโลมภาษาพูด ไม่เน้นศัพท์วิชาการ)\n\n"
            "• 1.0 คะแนน: อธิบายถูกต้องเพียงฝั่งใดฝั่งหนึ่ง หรือระบุเพียงนิยามเบื้องต้น (เช่น บอกเพียงแถวแนวนอน/คอลัมน์แนวตั้ง แต่ไม่ได้อธิบายการจัดเก็บข้อมูล) หรือคำอธิบายยังไม่สมบูรณ์\n\n"
            "• 0.0 คะแนน: ตอบผิดหลักการทั้งหมด ไม่ตอบ หรือตอบไม่เกี่ยวข้องกับโครงสร้างข้อมูล Array\n\n"
            "(เน้นเจตนาและความเข้าใจของนิสิตเป็นหลัก ให้อนุโลมสำนวนภาษาพูดของนิสิต)"
        ),
        "allowed_scores": [0.0, 1.0, 2.0]
    }
]

ANSWER_KEY = (
    "Row-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือการคำนวณตำแหน่ง address ในหน่วยความจำโดยเรียงตามแนวแถว (Row/แนวนอน) ก่อน "
    "ส่วน Column-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือการคำนวณตำแหน่ง address ในหน่วยความจำโดยเรียงตามแนวคอลัมน์ (Column/แนวตั้ง/หลัก) ก่อน "
    "ต่างกันที่ลำดับและมิติการเข้าถึงข้อมูลในหน่วยความจำ"
)

async def run_q1_regrade():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    print(f"Starting Q1 regrade for {len(items)} students...", flush=True)
    
    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text=it['question_content'],
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=Q1_RUBRIC,
                allowed_scores=[0.0, 1.0, 2.0]
            )
            s = res['score']
            h = it['human_score']
            diff = round(s - h, 2)
            match = "MATCH" if diff == 0.0 else f"diff={diff:+.1f}"
            print(f"{it['sample_id']} | Human: {h:.1f} | AI: {s:.1f} | {match}", flush=True)
            return {
                'sample_id': it['sample_id'],
                'human': h,
                'ai': s,
                'diff': diff,
                'confidence': res.get('confidence', 'medium'),
                'teacher_feedback': res.get('teacher_feedback', ''),
                'student_feedback': res.get('student_feedback', ''),
                'answer': it['student_answer']
            }

    results = await asyncio.gather(*(grade_one(it) for it in items))
    results.sort(key=lambda x: x['sample_id'])

    exact = sum(1 for r in results if r['diff'] == 0.0)
    diff05 = sum(1 for r in results if abs(r['diff']) <= 0.5)
    mae = sum(abs(r['diff']) for r in results) / len(results)

    output_path = ROOT / 'artifacts' / 'q1_regrade_results.json'
    output_path.write_text(json.dumps({
        'exact': exact,
        'diff05': diff05,
        'total': len(results),
        'mae': round(mae, 4),
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n==========================================")
    print(f"Q1 Regrade Summary:")
    print(f"Exact Match: {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.5: {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE: {mae:.4f}")
    print(f"Saved results to {output_path}")
    print(f"==========================================")

if __name__ == '__main__':
    asyncio.run(run_q1_regrade())
