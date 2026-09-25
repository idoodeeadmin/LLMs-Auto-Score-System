"""Evaluate Question 1 with refined rubric aligned with actual human grading."""
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

from scripts.run_dataset_benchmark import load_dataset, calculate_qwk, calculate_mae, calculate_confusion_matrix, get_agreement_interpretation
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

# Refined rubric for Question 1 aligned with human instructor grading
REFINED_Q1_META = {
    "question_no": 1,
    "type": "text",
    "topic": "Row-major vs Column-major",
    "max_score": 2.0,
    "question_text": "อธิบายความต่างของ Row-major vs Column-major",
    "answer_key": (
        "Row-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามแถว (Row หรือแนวนอน/ซ้ายไปขวา หรือเรียกแถวก่อนหลัก) "
        "ส่วน Column-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามคอลัมน์ (Column หรือแนวตั้ง/บนลงล่าง หรือเรียกหลักก่อนแถว) "
        "ทั้งสองแบบจัดเก็บแบบเชิงเส้นต่อเนื่องในหน่วยความจำ ต่างกันที่ลำดับการเรียงและสูตรการคำนวณหาตำแหน่ง Address ในหน่วยความจำ"
    ),
    "rubrics": [
        {
            "name": "Row-major",
            "score": 1.0,
            "description": (
                "อธิบาย Row-major ว่าเป็นการจัดเก็บข้อมูล ลำดับการเรียงตามแนวแถว (Row/แนวนอน/ซ้ายไปขวา) หรือเข้าถึงแถวก่อนหลัก (Row first) "
                "หรือสูตร address อิงแถว หรือหากอธิบายภาพรวมเชิงระบบว่าต่างกันที่สูตรคำนวณหาตำแหน่ง address/การจัดเก็บข้อมูล ให้ส่วนนี้ 1.0 คะแนน"
            )
        },
        {
            "name": "Column-major",
            "score": 1.0,
            "description": (
                "อธิบาย Column-major ว่าเป็นการจัดเก็บข้อมูล ลำดับการเรียงตามแนวคอลัมน์ (Column/แนวตั้ง/บนลงล่าง) หรือเข้าถึงหลักก่อนแถว (Column first) "
                "หรือสูตร address อิงคอลัมน์ หรือหากอธิบายภาพรวมเชิงระบบว่าต่างกันที่สูตรคำนวณหาตำแหน่ง address/การจัดเก็บข้อมูล ให้ส่วนนี้ 1.0 คะแนน"
            )
        }
    ]
}

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    assert len(items) == 34 and all(x['answer_type'] == 'text' for x in items)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q1-evaluation-refined-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)
    
    report = {
        'question_no': 1,
        'model': OPENAI_MODEL,
        'prompt_version': f'{PROMPT_VERSION}-refined-q1',
        'started_at': datetime.now(timezone.utc).isoformat(),
        'expected_count': len(items),
        'max_score': 2.0,
        'rubrics': REFINED_Q1_META['rubrics'],
        'results': [],
        'failures': []
    }
    
    def save():
        (folder / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    
    sem = asyncio.Semaphore(4)
    
    async def grade(item):
        async with sem:
            result = await score_with_openai(
                question_text=item['question_content'],
                answer_text=item['student_answer'],
                max_score=REFINED_Q1_META['max_score'],
                answer_key=REFINED_Q1_META['answer_key'],
                rubrics=REFINED_Q1_META['rubrics']
            )
            if 'answer_word_count' not in result.get('metrics', {}):
                report['failures'].append({'sample_id': item['sample_id'], 'reason': 'provider_or_processing_failure'})
                save()
                print(f"FAILED {item['sample_id']}", flush=True)
                return False
            
            report['results'].append({
                'sample_id': item['sample_id'],
                'row': item['row'],
                'answer': item['student_answer'],
                'human_score': item['human_score'],
                **result
            })
            save()
            print(f"{item['sample_id']} | Human: {item['human_score']} | AI: {result['score']} | Diff: {abs(item['human_score'] - result['score']):.1f}", flush=True)
            return True

    print(f"=== Starting Real AI Grading for Question 1 (34 students) ===")
    print(f"Output folder: {folder}")
    
    # Warm-up first sample to verify connectivity
    if not await grade(items[0]):
        raise SystemExit("First request failed; stopped execution.")
    
    # Grade remaining concurrently
    await asyncio.gather(*(grade(item) for item in items[1:]))
    
    report['results'].sort(key=lambda x: x['row'])
    results = report['results']
    truth = [r['human_score'] for r in results]
    predicted = [r['score'] for r in results]
    
    qwk_val = calculate_qwk(truth, predicted, step=0.5, max_score=2.0)
    mae_val = calculate_mae(truth, predicted)
    exact_cnt = sum(a == b for a, b in zip(truth, predicted))
    
    report['summary'] = {
        'successful': len(results),
        'failed': len(report['failures']),
        'mae': mae_val,
        'qwk_step_0_5': qwk_val,
        'agreement': get_agreement_interpretation(qwk_val),
        'exact_count': exact_cnt,
        'exact_pct': round((exact_cnt / len(results)) * 100, 2),
        'confusion_matrix': calculate_confusion_matrix(truth, predicted, [0, 0.5, 1, 1.5, 2])
    }
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    save()
    
    print("\n=== FINAL BENCHMARK SUMMARY ===")
    print(f"Total: {len(results)} samples")
    print(f"Exact Matches: {exact_cnt}/{len(results)} ({report['summary']['exact_pct']}%)")
    print(f"MAE: {mae_val}")
    print(f"QWK (step 0.5): {qwk_val} ({report['summary']['agreement']['level_th']})")
    print(f"Saved report to: {folder / 'results.json'}")

if __name__ == '__main__':
    asyncio.run(main())
