import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone

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

GENEROUS_RUBRIC_Q3 = [
    {
        "name": "การเปรียบเทียบ Linked List vs Array และข้อดีข้อเสีย",
        "score": 1.0,
        "description": (
            "เกณฑ์การประเมินแบบใจดีและให้ประโยชน์แก่ผู้เรียน (Generous Grading & Benefit of the Doubt):\n"
            "มุ่งเน้นการจับประเด็นความเข้าใจ ไม่หักคะแนนจุกจิก ยอมรับภาษาพูดและการอธิบายตามความเข้าใจของผู้เรียน อะไรที่พอตีความเชื่อมโยงได้ ให้คะแนนสนับสนุนผู้เรียนทันที:\n\n"
            "- 1.00 คะแนน: มีการพูดถึงความต่างเรื่องขนาด/การจัดเก็บ (เช่น Array ขนาดคงที่/Fix size ส่วน Linked List ยืดหยุ่น/เพิ่มลดได้/ไม่จำกัด) และ มีการกล่าวถึงข้อดีหรือข้อเสียอย่างน้อย 1-2 ด้าน (เช่น เข้าถึงเร็ว/ช้า, ประหยัด/เปลืองพื้นที่, ขยายได้/ขยายยาก หรือภาษาทั่วไป เช่น อิสระกว่า/ลบง่ายกว่า) หรือตอบมีโครงสร้างชัดเจน ให้คะแนนเต็ม 1.00 ทันที\n"
            "- 0.75 คะแนน: อธิบายความแตกต่างเรื่องขนาดได้ชัดเจน หรือมีการพูดถึงข้อดีข้อเสียที่สื่อความหมายได้ดี แม้จะไม่ได้พูดครบทุกมิติ\n"
            "- 0.50 คะแนน: มีสาระที่ถูกต้องหรือพอตีความได้ 1 ประเด็น เช่น พูดถึงเรื่องขนาดคงที่/Dynamic อย่างใดอย่างหนึ่ง, หรือพูดถึงข้อดี/ข้อเสียทั่วไป (เช่น เข้าถึงช้า/เร็ว, ค้นหายาก/ง่าย, สับสน, ยืดหยุ่น)\n"
            "- 0.25 คะแนน: มีข้อความที่ถูกเพียงเล็กน้อยมาก หรือพูดถึงเฉพาะ Stack/Queue (LIFO/FIFO) โดยแทบไม่ได้พูดถึง Array/Linked List\n"
            "- 0.00 คะแนน: ส่งกระดาษเปล่า ไม่ตอบ หรือเขียนข้อความที่ไม่เกี่ยวข้องกับโจทย์เลย\n\n"
            "**ระดับคะแนนที่ให้ได้คือ 1.00, 0.75, 0.50, 0.25 หรือ 0.00 คะแนนเท่านั้น**"
        )
    }
]

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 3]
    assert len(items) == 34 and all(x['answer_type'] == 'text' for x in items)

    q = EXAM_QUESTIONS[3]
    rubrics = GENEROUS_RUBRIC_Q3

    print(f"=== Grading Question 3 with Generous / Lenient Rubric ({len(items)} students) ===")
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
    print("=== SUMMARY RESULTS (GENEROUS RUBRIC) ===")
    print(f"Total Students:        {len(results)}")
    print(f"Exact Match:           {exact_count}/34 ({exact_count/34*100:.2f}%)")
    print(f"Tolerance <= 0.25:     {tol_025_count}/34 ({tol_025_count/34*100:.2f}%)")
    print(f"Tolerance <= 0.50:     {tol_050_count}/34 ({tol_050_count/34*100:.2f}%)")
    print(f"MAE (Mean Abs Error):  {mae:.4f}")
    print(f"QWK (step=0.25):       {qwk:.4f} ({get_agreement_interpretation(qwk)['level_th']})")

    # Save artifact
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q3-generous-eval-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)
    out_file = folder / 'q3_generous_results.json'
    out_file.write_text(json.dumps({'summary': {
        'exact_count': exact_count, 'exact_pct': exact_count/34*100,
        'tolerance_0_25_pct': tol_025_count/34*100, 'tolerance_0_50_pct': tol_050_count/34*100,
        'mae': mae, 'qwk': qwk
    }, 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Saved results to: {out_file}")

if __name__ == '__main__':
    asyncio.run(main())
