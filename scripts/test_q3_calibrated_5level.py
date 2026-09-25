import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

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

# Refined 5-Level Rubric that aligns with actual human grading patterns
CALIBRATED_5LEVEL_RUBRIC = [
    {
        "name": "การเปรียบเทียบ Linked List vs Array และข้อดีข้อเสีย (5 ระดับ)",
        "score": 1.0,
        "description": (
            "เกณฑ์การให้คะแนนแบบ 5 ระดับ (1.00, 0.75, 0.50, 0.25, 0.00) สำหรับโจทย์การเปรียบเทียบ Linked List กับ Array ในการทำ Stack & Queue:\n\n"
            "- 1.00 คะแนน: ตอบประเด็นความแตกต่างเรื่องขนาดชัดเจน (Array ขนาดคงที่/จองพื้นที่แน่นอน ส่วน Linked List ขนาดปรับเปลี่ยนได้/Dynamic/ไม่ต้องระบุขนาด) และ ระบุทั้งข้อดีและข้อเสีย (เช่น ไม่จำกัดขนาด/ไม่เกิด overflow vs เข้าถึงช้ากว่า/เปลืองพื้นที่พอยน์เตอร์หรือเมมโมรี/จัดการซับซ้อนกว่า) แม้อธิบายกระชับหรือเป็นภาษาของตนเอง\n"
            "- 0.75 คะแนน: ตอบความแตกต่างเรื่องขนาดได้ชัดเจน แต่ระบุข้อดีหรือข้อเสียเพียงด้านเดียว (มีแค่ข้อดี หรือมีแค่ข้อเสีย) หรือระบุข้อดีข้อเสียทั้งสองด้านแต่คำอธิบายความแตกต่างยังไม่สมบูรณ์\n"
            "- 0.50 คะแนน: ตอบประเด็นใดประเด็นหนึ่งเพียงอย่างเดียว เช่น ตอบเฉพาะความแตกต่างเรื่องขนาด (Array ฟิกซ์ / Linked List ยืดหยุ่น) โดยไม่มีข้อดีข้อเสียเลย, หรือตอบเฉพาะข้อดีข้อเสียแต่ไม่ได้เปรียบเทียบโครงสร้างขนาด, หรือตอบถูกแต่มีจุดคลาดเคลื่อน/ภาษาไม่รัดกุม\n"
            "- 0.25 คะแนน: มีประเด็นถูกต้องเพียงเล็กน้อย เช่น ตอบเฉพาะนิยามของ Stack (LIFO) และ Queue (FIFO) หรือพูดถึงข้อดีข้อเสียแบบกว้างๆ ลอยๆ โดยไม่มีหลักการของ Array/Linked List\n"
            "- 0.00 คะแนน: ไม่ตอบ, ตอบไม่ตรงคำถาม, หรือเขียนคำตอบสั้นๆ ไม่เป็นสาระ/เข้าใจผิดอย่างสิ้นเชิง\n\n"
            "**ระดับคะแนนที่ให้ได้คือ 1.00, 0.75, 0.50, 0.25 หรือ 0.00 คะแนนเท่านั้น ห้ามให้เศษทศนิยมอื่น**"
        )
    }
]

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 3]
    q = EXAM_QUESTIONS[3]
    rubrics = CALIBRATED_5LEVEL_RUBRIC

    print(f"=== Testing Calibrated 5-Level Rubric for Q3 ({len(items)} students) ===")
    print(f"Model: {OPENAI_MODEL} | Prompt Version: {PROMPT_VERSION}")
    print("-" * 65)

    results = []
    sem = asyncio.Semaphore(4)

    async def grade_one(item):
        async with sem:
            res = await score_with_openai(
                question_text=item['question_content'],
                answer_text=item['student_answer'],
                max_score=q['max_score'],
                answer_key=q['answer_key'],
                rubrics=rubrics,
            )
            h_score = item['human_score']
            ai_score = res.get('score', 0.0)
            conf = res.get('confidence', 'unknown')
            diff = round(ai_score - h_score, 2)
            entry = {
                'sample_id': item['sample_id'],
                'row': item['row'],
                'answer': item['student_answer'],
                'human_score': h_score,
                'ai_score': ai_score,
                'diff': diff,
                'exact': ai_score == h_score,
                'confidence': conf,
                'feedback': res.get('feedback', ''),
            }
            results.append(entry)
            status = "MATCH" if ai_score == h_score else f"DIFF ({diff:+0.2f})"
            print(f"[{entry['sample_id']}] Human={h_score:0.2f} | AI={ai_score:0.2f} | Conf={conf:6s} | {status}")
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
    print("=== SUMMARY RESULTS (CALIBRATED 5-LEVEL) ===")
    print(f"Total Students:        {len(results)}")
    print(f"Exact Match:           {exact_count}/34 ({exact_count/34*100:.2f}%)")
    print(f"Tolerance <= 0.25:     {tol_025_count}/34 ({tol_025_count/34*100:.2f}%)")
    print(f"Tolerance <= 0.50:     {tol_050_count}/34 ({tol_050_count/34*100:.2f}%)")
    print(f"MAE (Mean Abs Error):  {mae:.4f}")
    print(f"QWK (step=0.25):       {qwk:.4f} ({get_agreement_interpretation(qwk)['level_th']})")

    # Save artifact
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q3-calibrated-5level-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)
    out_file = folder / 'q3_calibrated_results.json'
    out_file.write_text(json.dumps({'summary': {
        'exact_count': exact_count, 'exact_pct': exact_count/34*100,
        'tolerance_0_25_pct': tol_025_count/34*100, 'tolerance_0_50_pct': tol_050_count/34*100,
        'mae': mae, 'qwk': qwk
    }, 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Saved results to: {out_file}")

if __name__ == '__main__':
    asyncio.run(main())
