import os
import sys
import json
import asyncio
from io import BytesIO
from pathlib import Path
from datetime import datetime
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

from scripts.run_dataset_benchmark import (
    load_dataset,
    calculate_qwk,
    calculate_mae,
    calculate_confusion_matrix,
    get_agreement_interpretation,
    EXAM_QUESTIONS,
)
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

REFINED_RUBRIC_Q4 = [
    {
        "name": "ความถูกต้องของโครงสร้าง Binary Search Tree (BST)",
        "score": 1.0,
        "description": (
            "เกณฑ์การประเมินภาพวาด Binary Search Tree (BST) จากลำดับข้อมูลที่กำหนดในโจทย์ (คะแนนเต็ม 1.00):\n\n"
            "- 1.00 คะแนน: ครบ 12 โหนด ถูกต้องสมบูรณ์ทั้งหมด:\n"
            "  Root=9, ซ้าย=5, ขวา=16\n"
            "  16→ซ้าย=10→ขวา=13→(ซ้าย=11, ขวา=15)\n"
            "  16→ขวา=76→(ซ้าย=58, ขวา=92→(ซ้าย=80, ขวา=99))\n\n"
            "- 0.50 คะแนน: โครงสร้างส่วนใหญ่ถูกต้อง แต่ผิด 1 จุด\n\n"
            "- 0.25 คะแนน: โครงสร้างถูกต้องบางส่วน / วาดไม่เสร็จ\n\n"
            "- 0.00 คะแนน: ผิดหลักการ BST ขั้นพื้นฐาน หรือไม่มีคำตอบ\n\n"
            "**ระดับคะแนนที่ให้ได้คือ 1.00, 0.50, 0.25 หรือ 0.00 คะแนนเท่านั้น ห้ามให้คะแนนเป็นเศษทศนิยมอื่น**"
        ),
    }
]

def load_upright_image_bytes(img_path: str) -> bytes:
    img = Image.open(img_path)
    if img.height > img.width:
        img = img.rotate(90, expand=True)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=95)
    return buf.getvalue()

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 4]
    assert len(items) == 34 and all(x['answer_type'] == 'img' for x in items)

    q = EXAM_QUESTIONS[4]
    rubrics = REFINED_RUBRIC_Q4

    print(f"=== Grading Question 4 (User Refined Rubric - Cleaned) ===")
    print(f"Total students: {len(items)}")
    print(f"Model: {OPENAI_MODEL} | Prompt Version: {PROMPT_VERSION} | Reasoning: low")
    print("-" * 65)

    results = []
    sem = asyncio.Semaphore(4)

    async def grade_one(item):
        async with sem:
            img_bytes = load_upright_image_bytes(item['student_img_path'])
            res = await score_with_openai(
                question_text=q['question_text'],
                answer_text="",
                max_score=q['max_score'],
                answer_key=q['answer_key'],
                rubrics=rubrics,
                image_bytes_list=[img_bytes],
                image_mime_list=["image/jpeg"],
            )
            h_score = item['human_score']
            ai_score = res.get('score', 0.0)
            conf = res.get('confidence', 'unknown')
            diff = round(ai_score - h_score, 2)
            entry = {
                'sample_id': item['sample_id'],
                'row': item['row'],
                'human_score': h_score,
                'ai_score': ai_score,
                'diff': diff,
                'exact': ai_score == h_score,
                'confidence': conf,
                'feedback': res.get('feedback', ''),
                'transcription': res.get('transcription', ''),
            }
            results.append(entry)
            status = "MATCH" if ai_score == h_score else f"DIFF ({diff:+0.2f})"
            print(f"[{entry['sample_id']}] Human={h_score:0.2f} | AI={ai_score:0.2f} | Conf={conf:6s} | {status}", flush=True)
            return entry

    tasks = [grade_one(item) for item in items]
    await asyncio.gather(*tasks)

    results.sort(key=lambda x: x['row'])
    truth = [r['human_score'] for r in results]
    predicted = [r['ai_score'] for r in results]
    exact_count = sum(r['exact'] for r in results)
    tol_025_count = sum(abs(r['diff']) <= 0.25 for r in results)
    tol_050_count = sum(abs(r['diff']) <= 0.50 for r in results)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=0.25, max_score=1.0)

    print("\n" + "=" * 65)
    print("=== SUMMARY BENCHMARK RESULTS (Q4 Refined Rubric) ===")
    print(f"Exact Match:      {exact_count}/{len(results)} ({exact_count/len(results)*100:.2f}%)")
    print(f"Tolerance ±0.25:  {tol_025_count}/{len(results)} ({tol_025_count/len(results)*100:.2f}%)")
    print(f"Tolerance ±0.50:  {tol_050_count}/{len(results)} ({tol_050_count/len(results)*100:.2f}%)")
    print(f"MAE:              {mae:.4f}")
    print(f"QWK:              {qwk:.4f} ({get_agreement_interpretation(qwk)})")
    print("=" * 65)

if __name__ == '__main__':
    asyncio.run(main())
