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

USER_RUBRIC_Q2 = [
    {
        "name": "ส่วนการอธิบายเหตุผล",
        "score": 1.5,
        "description": (
            "- 1.5: อธิบายพอให้เข้าใจได้ว่า ทำไม O(n log n) จึงเหมาะกับข้อมูลขนาดใหญ่กว่า O(n^2) เช่น เร็วกว่าเพราะทำงานน้อยกว่า, n^2 ทำงานเยอะเมื่อข้อมูลเพิ่ม, loop ซ้อนทำให้ช้า, แบ่งข้อมูลแล้วลดงาน ฯลฯ ไม่จำเป็นต้องอธิบายถูกต้องทางทฤษฎีทุกคำ ถ้าแก่นเหตุผลยังเข้าใจได้ ให้ 1.5\n"
            "- 1.0: บอกว่า O(n log n) เร็วกว่า / มีประสิทธิภาพกว่า / ใช้เวลาน้อยกว่า และมีคำขยายเล็กน้อย แต่ยังไม่ได้อธิบายเหตุผลชัดว่าทำไม\n"
            "- 0.5: คำอธิบายกำกวม ผิดบางส่วน หรือแทบมีแค่ข้อสรุป แต่ยังพอตีความได้ว่านักศึกษาเข้าใจว่า O(n log n) เหมาะกับข้อมูลใหญ่กว่า\n"
            "- 0: ไม่อธิบายเหตุผลเลย, ตอบไม่เกี่ยว หรือผิดจนไม่เหลือแก่นของคำตอบ"
        )
    },
    {
        "name": "ตัวอย่าง Algorithm",
        "score": 0.5,
        "description": "- 0.5: มีการยกตัวอย่าง Algorithm ที่เกี่ยวข้อง เช่น Merge Sort/Merge, Quick Sort, Bubble Sort, Insertion Sort, Selection Sort ฯลฯ เพื่อประกอบการเปรียบเทียบ\n- 0: ไม่ยกตัวอย่าง หรือสิ่งที่ยกมาไม่สามารถถือว่าเป็น Algorithm ที่เกี่ยวข้องได้"
    }
]

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 2][20:]
    assert len(items) == 14 and all(x['answer_type'] == 'text' for x in items)

    q = EXAM_QUESTIONS[2]
    q['topic'] = "อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลใหญ่กว่า O(n^2) และยกตัวอย่าง Algorithm"
    rubrics = USER_RUBRIC_Q2
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q2-user-rubric-eval-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)

    print(f"=== Grading Question 2 with User Proposed Rubric (remaining {len(items)} students) ===")
    print(f"Model: {OPENAI_MODEL} | Prompt Version: {PROMPT_VERSION}")
    print(f"Topic: {q['topic']}")
    print(f"Rubric: 5 Levels [2.0, 1.5, 1.0, 0.5, 0.0]")
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
            review = res.get('metrics', {}).get('manual_review_required', False)
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
                'manual_review_required': review,
                'feedback': res.get('feedback', ''),
            }
            results.append(entry)
            status = "MATCH" if ai_score == h_score else f"DIFF ({diff:+0.1f})"
            print(f"[{entry['sample_id']}] Human={h_score:0.1f} | AI={ai_score:0.1f} | Conf={conf:6s} | {status} | Review={review}")
            return entry

    # Run all students
    tasks = [grade_one(item) for item in items]
    await asyncio.gather(*tasks)

    # Sort by row
    results.sort(key=lambda x: x['row'])

    truth = [r['human_score'] for r in results]
    predicted = [r['ai_score'] for r in results]
    exact_count = sum(r['exact'] for r in results)
    tol_count = sum(abs(r['diff']) <= 0.5 for r in results)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=0.5, max_score=2.0)

    conf_dist = {'high': 0, 'medium': 0, 'low': 0, 'other': 0}
    for r in results:
        conf_dist[r['confidence']] = conf_dist.get(r['confidence'], 0) + 1

    summary = {
        'total': len(results),
        'exact_count': exact_count,
        'exact_pct': round((exact_count / len(results)) * 100, 2),
        'tolerance_0_5_count': tol_count,
        'tolerance_0_5_pct': round((tol_count / len(results)) * 100, 2),
        'mae': round(mae, 4),
        'qwk': round(qwk, 4),
        'qwk_interpretation': get_agreement_interpretation(qwk),
        'confidence_distribution': conf_dist,
    }

    full_output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'question_no': 2,
        'topic': q['topic'],
        'rubrics': rubrics,
        'summary': summary,
        'results': results,
    }

    output_path = folder / 'q2_user_rubric_results.json'
    output_path.write_text(json.dumps(full_output, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n" + "=" * 65)
    print("=== SUMMARY RESULTS WITH USER RUBRIC ===")
    print(f"Total Students:        {summary['total']}")
    print(f"Exact Match:           {summary['exact_count']}/{summary['total']} ({summary['exact_pct']}%)")
    print(f"Tolerance <= 0.5:      {summary['tolerance_0_5_count']}/{summary['total']} ({summary['tolerance_0_5_pct']}%)")
    print(f"MAE (Mean Abs Error):  {summary['mae']}")
    print(f"QWK (Quadratic Kappa): {summary['qwk']} ({summary['qwk_interpretation']['level_th']})")
    print(f"Confidence Breakdown:  High={conf_dist.get('high', 0)}, Medium={conf_dist.get('medium', 0)}, Low={conf_dist.get('low', 0)}")
    print(f"JSON Report saved to: {output_path}")

if __name__ == '__main__':
    asyncio.run(main())
