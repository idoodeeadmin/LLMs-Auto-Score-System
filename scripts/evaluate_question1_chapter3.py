"""Evaluate Question 1 with Chapter 3 original rubric (ภาพรวม 1.0 + วิธีเรียกใช้งาน 1.0)."""
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

CHAPTER3_Q1_META = {
    "question_no": 1,
    "type": "text",
    "topic": "Row-major vs Column-major",
    "max_score": 2.0,
    "question_text": "จงอธิบายความแตกต่างระหว่าง Row-major order และ Column-major order พร้อมระบุวิธีการเรียกหรือเข้าถึงข้อมูลใน Array 2 มิติ",
    "answer_key": (
        "Row-major order คือการจัดเก็บข้อมูลเรียงตามแถว (แนวนอน) วิธีการเรียกหรือเข้าถึงคือแถวก่อนหลัก (ซ้ายไปขวา) "
        "ส่วน Column-major order คือการจัดเก็บข้อมูลเรียงตามคอลัมน์ (แนวตั้ง) วิธีการเรียกหรือเข้าถึงคือหลักก่อนแถว (บนลงล่าง) "
        "ต่างกันที่การจัดเก็บข้อมูลในหน่วยความจำและสูตรคำนวณตำแหน่ง address"
    ),
    "rubrics": [
        {
            "name": "อธิบายความแตกต่างในภาพรวม",
            "score": 1.0,
            "description": "อธิบายความแตกต่างของ Row-major และ Column-major ในมุมมองภาพรวม เช่น การจัดเก็บข้อมูลเรียงตามแนวนอน vs แนวตั้ง หรือเรียงตามแถว vs ตามคอลัมน์ หรือต่างกันที่สูตร address ในการจัดเก็บ"
        },
        {
            "name": "ระบุวิธีการเรียกใช้งานหรือลำดับการเข้าถึง Array",
            "score": 1.0,
            "description": "ต้องบอกวิธีการเรียกใช้งานหรือทิศทางการเข้าถึง Array เช่น Row-major คือแถวก่อนหลัก (นับซ้ายไปขวา) และ Column-major คือหลักก่อนแถว (นับบนลงล่าง) ถึงจะได้อีก 1.0 คะแนน"
        }
    ]
}

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    assert len(items) == 34 and all(x['answer_type'] == 'text' for x in items)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q1-evaluation-chapter3-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)
    
    report = {
        'question_no': 1,
        'model': OPENAI_MODEL,
        'prompt_version': PROMPT_VERSION,
        'rubric_source': 'Chapter3LLMTest.tsx (ภาพรวม 1.0 + วิธีเรียก 1.0)',
        'started_at': datetime.now(timezone.utc).isoformat(),
        'expected_count': len(items),
        'max_score': CHAPTER3_Q1_META['max_score'],
        'rubrics': CHAPTER3_Q1_META['rubrics'],
        'results': [],
        'failures': []
    }
    
    def save():
        (folder / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        
    sem = asyncio.Semaphore(4)
    
    async def grade(item):
        async with sem:
            result = await score_with_openai(
                question_text=CHAPTER3_Q1_META['question_text'],
                answer_text=item['student_answer'],
                max_score=CHAPTER3_Q1_META['max_score'],
                answer_key=CHAPTER3_Q1_META['answer_key'],
                rubrics=CHAPTER3_Q1_META['rubrics']
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
            print(f"{item['sample_id']} | Human: {item['human_score']} | AI: {result['score']}", flush=True)
            return True

    print(f"Starting Q1 evaluation with Chapter 3 rubric at {folder}...", flush=True)
    if not await grade(items[0]):
        raise SystemExit("First request failed; stopping.")
        
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
    
    print("\n=== SUMMARY ===")
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2), flush=True)

if __name__ == '__main__':
    asyncio.run(main())
