"""Evaluate Question 1 without rubrics (rubrics=None)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

import asyncio
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from scripts.run_dataset_benchmark import load_dataset, calculate_qwk, calculate_mae, calculate_confusion_matrix
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

Q1_QUESTION_TEXT = "อธิบายความต่างของ Row-major vs Column-major"
Q1_ANSWER_KEY = (
    "Row-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามแถว (Row หรือแนวนอน/แกน X) "
    "ส่วน Column-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามคอลัมน์ (Column หรือแนวตั้ง/แกน Y) "
    "ต่างกันที่ลำดับและมิติการเรียงข้อมูลในหน่วยความจำ"
)

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    folder = ROOT / 'artifacts' / f'q1-evaluation-no-rubric-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
    folder.mkdir(parents=True, exist_ok=True)
    
    report = {
        'question_no': 1,
        'model': OPENAI_MODEL,
        'prompt_version': PROMPT_VERSION,
        'rubric_source': 'None (No Rubrics provided)',
        'started_at': datetime.now(timezone.utc).isoformat(),
        'expected_count': len(items),
        'max_score': 2.0,
        'rubrics': None,
        'results': [],
        'failures': []
    }
    
    def save():
        (folder / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        
    sem = asyncio.Semaphore(4)
    
    async def grade(item):
        async with sem:
            result = await score_with_openai(
                question_text=Q1_QUESTION_TEXT,
                answer_text=item['student_answer'],
                max_score=2.0,
                answer_key=Q1_ANSWER_KEY,
                rubrics=None  # NO RUBRIC
            )
            
            if 'answer_word_count' not in result.get('metrics', {}):
                report['failures'].append({'sample_id': item['sample_id'], 'reason': 'failure'})
                save()
                return False
                
            report['results'].append({
                'sample_id': item['sample_id'],
                'row': item['row'],
                'answer': item['student_answer'],
                'human_score': item['human_score'],
                **result
            })
            save()
            print(f"{item['sample_id']} | Human: {item['human_score']} | AI (No Rubric): {result['score']}", flush=True)
            return True

    print(f"Starting Q1 evaluation WITHOUT rubrics at {folder}...", flush=True)
    if not await grade(items[0]):
        raise SystemExit("First request failed.")
        
    await asyncio.gather(*(grade(item) for item in items[1:]))
    
    report['results'].sort(key=lambda x: x['row'])
    results = report['results']
    truth = [r['human_score'] for r in results]
    predicted = [r['score'] for r in results]
    
    exact_count = sum(a == b for a, b in zip(truth, predicted))
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=0.5, max_score=2.0)
    
    report['summary'] = {
        'successful': len(results),
        'failed': len(report['failures']),
        'mae': round(mae, 4),
        'qwk_step_0_5': round(qwk, 4),
        'exact_count': exact_count,
        'exact_percentage': round((exact_count / len(results)) * 100, 2),
        'confusion_matrix': calculate_confusion_matrix(truth, predicted, [0, 0.5, 1, 1.5, 2])
    }
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    save()
    
    print("\n=== SUMMARY WITHOUT RUBRIC ===")
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2), flush=True)

if __name__ == '__main__':
    asyncio.run(main())
