# -*- coding: utf-8 -*-
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

from scripts.run_dataset_benchmark import load_dataset
from server.services.openai_grading import score_with_openai

Q1_RUBRIC_TEXT = (
    "2.00 คะแนน (เต็ม):\n"
    "อธิบายความแตกต่างครบทั้ง 2 ฝั่ง โดยต้องระบุ \"วิธีเรียกใช้งาน / ลำดับการเข้าถึง Array\" หรือ \"ยกตัวอย่างที่แสดงให้เห็นความต่างในการเรียก\" "
    "(เช่น ระบุว่า Row-major เรียกแถวก่อนหลัก vs Column-major เรียกหลักก่อนแถว, หรือแสดงตัวอย่างลำดับดัชนี/การเข้าถึงข้อมูลที่สะท้อนความต่างชัดเจน)\n\n"
    "1.00 คะแนน:\n"
    "ตอบได้เพียงมโนทัศน์กว้างๆ ว่าเป็น \"แนวนอน vs. แนวตั้ง\" (หรือบอกแค่นิยาม Row/Column) โดยไม่ได้อธิบายวิธีเรียกหรือไม่มีตัวอย่างการเข้าถึงข้อมูล "
    "หรืออธิบายวิธีเรียกถูกต้องเพียงฝั่งเดียว\n\n"
    "0.00 คะแนน:\n"
    "ไม่ตอบ หรือตอบไม่ถูกต้องตามหลักการทั้งหมดอย่างสิ้นเชิง"
)

Q1_RUBRIC = [
    {
        "name": "Row-major vs Column-major",
        "score": 2.0,
        "description": Q1_RUBRIC_TEXT,
        "allowed_scores": [0.0, 1.0, 2.0]
    }
]

ANSWER_KEY = (
    "Row-major คือการจัดเก็บหรือเข้าถึงข้อมูลตามแถว (แนวนอน) โดยเรียกแถวก่อนหลัก "
    "ส่วน Column-major คือการจัดเก็บหรือเข้าถึงข้อมูลตามคอลัมน์ (แนวตั้ง) โดยเรียกหลักก่อนแถว"
)

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    items = sorted(items, key=lambda x: x['sample_id'])[:10]
    print(f"Testing Q1 for the first {len(items)} students (DS-001 to DS-010)...\n")

    results = []
    for it in items:
        print(f"Grading {it['sample_id']}...", end=" ", flush=True)
        res = await score_with_openai(
            question_text=it['question_content'],
            answer_text=it['student_answer'],
            max_score=2.0,
            answer_key=ANSWER_KEY,
            rubrics=Q1_RUBRIC,
            allowed_scores=[0.0, 1.0, 2.0]
        )
        s = float(res['score'])
        h = float(it['human_score'])
        diff = round(s - h, 2)
        match_str = "MATCH" if diff == 0.0 else f"DIFF ({diff:+.1f})"
        print(f"Human: {h:.1f} | AI: {s:.1f} -> {match_str}")
        results.append({
            'sample_id': it['sample_id'],
            'student_answer': it['student_answer'],
            'human': h,
            'ai': s,
            'diff': diff,
            'confidence': res.get('confidence', 'medium'),
            'teacher_feedback': res.get('teacher_feedback', ''),
            'student_feedback': res.get('student_feedback', '')
        })

    print("\n" + "="*70)
    print("DETAILED RESULTS FOR FIRST 10 SAMPLES:")
    print("="*70)
    exact_count = sum(1 for r in results if r['diff'] == 0.0)
    for r in results:
        print(f"\n[{r['sample_id']}]")
        print(f"  คำตอบนิสิต: {repr(r['student_answer'])}")
        diff_str = f"ต่าง ({r['diff']:+.1f})" if r['diff'] != 0 else "ตรงกัน (Exact Match)"
        print(f"  คะแนนอาจารย์: {r['human']:.1f} | คะแนน AI: {r['ai']:.1f} | ผลลัพธ์: {diff_str}")
        print(f"  เหตุผล AI (ผู้สอน): {r['teacher_feedback']}")
        print(f"  ข้อเสนอแนะ AI (ผู้เรียน): {r['student_feedback']}")

    print("\n" + "="*70)
    print(f"SUMMARY: Exact Match = {exact_count}/10 ({exact_count*10}%)")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
