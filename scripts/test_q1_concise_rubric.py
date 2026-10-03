# -*- coding: utf-8 -*-
"""
Test Question 1 with a very short, concise rubric that lets AI reason on its own.
"""
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from scripts.run_dataset_benchmark import load_dataset, calculate_mae, calculate_qwk
from server.services.openai_grading import score_with_openai

# Very concise rubric: "ปล่อยให้ AI คิดเอง"
Q1_CONCISE_RUBRIC = [
    {
        "name": "Row-major vs Column-major",
        "score": 2.0,
        "description": (
            "ประเมินความเข้าใจความต่างของ Row-major และ Column-major (คะแนนเต็ม 2.00 คะแนน):\n"
            "• 2.00 คะแนน: อธิบายความต่างได้ถูกต้องครบทั้ง 2 ฝั่ง (Row-major อิงตามแถว/แนวนอน และ Column-major อิงตามคอลัมน์/แนวตั้ง)\n"
            "• 1.00 คะแนน: อธิบายถูกต้องเพียงฝั่งเดียว หรือบอกเพียงความเข้าใจเบื้องต้นสั้นๆ\n"
            "• 0.00 คะแนน: ตอบผิดทั้งหมด หรือไม่ตอบ"
        ),
        "allowed_scores": [0.0, 1.0, 2.0]
    }
]

ANSWER_KEY = (
    "Row-major คือการจัดเก็บหรือเข้าถึงข้อมูลตามแถว (แนวนอน) "
    "ส่วน Column-major คือการจัดเก็บหรือเข้าถึงข้อมูลตามคอลัมน์ (แนวตั้ง)"
)

async def test_q1_concise():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    print(f"Testing Q1 Concise Rubric for {len(items)} students...", flush=True)

    sem = asyncio.Semaphore(5)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text=it['question_content'],
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=Q1_CONCISE_RUBRIC,
                allowed_scores=[0.0, 1.0, 2.0]
            )
            s = float(res['score'])
            h = float(it['human_score'])
            diff = round(s - h, 2)
            match = "EXACT MATCH" if diff == 0.0 else f"diff={diff:+.1f}"
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

    truth = [r['human'] for r in results]
    predicted = [r['ai'] for r in results]

    exact = sum(1 for r in results if r['diff'] == 0.0)
    diff05 = sum(1 for r in results if abs(r['diff']) <= 0.5)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=1.0, max_score=2.0)

    print("\n==========================================")
    print("Q1 CONCISE RUBRIC SUMMARY:")
    print(f"Exact Match:      {exact}/{len(results)} ({exact/len(results)*100:.2f}%)")
    print(f"Diff <= 0.5:      {diff05}/{len(results)} ({diff05/len(results)*100:.2f}%)")
    print(f"MAE:              {mae:.4f}")
    print(f"QWK:              {qwk:.4f}")
    print("==========================================")

    print("\nDiscrepancies:")
    for r in results:
        if r['diff'] != 0:
            print(f"  {r['sample_id']} | Human: {r['human']} | AI: {r['ai']} | Ans: {repr(r['answer'][:60])}")

if __name__ == '__main__':
    asyncio.run(test_q1_concise())
