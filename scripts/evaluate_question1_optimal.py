"""Evaluate Question 1 with Optimal Human-Aligned Rubric."""
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

OPTIMAL_Q1_META = {
    "question_no": 1,
    "type": "text",
    "topic": "Row-major vs Column-major",
    "max_score": 2.0,
    "question_text": "อธิบายความต่างของ Row-major vs Column-major",
    "answer_key": (
        "ความแตกต่างระหว่าง Row-major และ Column-major สามารถอธิบายได้ในมิติใดมิติหนึ่งดังนี้:\n"
        "1. ลำดับการเข้าถึง: Row-major คือแถวก่อนหลัก (ซ้ายไปขวา) ส่วน Column-major คือหลักก่อนแถว (บนลงล่าง)\n"
        "2. การจัดเก็บข้อมูลใน Array/หน่วยความจำ: Row-major เก็บเรียงทีละแถว (แนวนอน) ส่วน Column-major เก็บเรียงทีละคอลัมน์ (แนวตั้ง)\n"
        "3. สูตรการคำนวณ Address: ต่างกันที่สูตรคำนวณตำแหน่ง Address ในหน่วยความจำอิงแถว vs อิงคอลัมน์\n"
        "4. ตัวอย่างลำดับดัชนี: แสดงลำดับสมาชิกเรียงตามแถว vs เรียงตามคอลัมน์ถูกต้อง"
    ),
    "rubrics": [
        {
            "name": "ความถูกต้องของการจำแนก Row-major vs Column-major",
            "score": 2.0,
            "description": (
                "เกณฑ์การให้คะแนนเต็ม 2.0 คะแนน:\n"
                "- ได้ 2.0 คะแนนเต็ม: อธิบายความแตกต่างของทั้ง 2 แบบได้ชัดเจนในมิติใดมิติหนึ่ง (ไม่จำเป็นต้องครบทุกมิติ) เช่น "
                "(1) ลำดับการเข้าถึงแถวก่อนหลัก vs หลักก่อนแถว, หรือ "
                "(2) การจัดเก็บข้อมูลของ Array ในแนวนอน/ตามแถว vs แนวตั้ง/ตามคอลัมน์, หรือ "
                "(3) การคำนวณตำแหน่ง Address ที่ใช้สูตรต่างกันตามแถว vs คอลัมน์, หรือ "
                "(4) ยกตัวอย่างลำดับดัชนี/ตัวเลขเปรียบเทียบชัดเจน\n"
                "- ได้ 1.0 คะแนน (คะแนนบางส่วน): "
                "(1) ตอบเฉพาะทิศทางพื้นฐานสั้นๆ เช่น ระบุเพียง Row คือแนวนอน และ Column คือแนวตั้ง โดยไม่มีคำว่า major หรือไม่อธิบายเรื่องการเก็บข้อมูล, หรือ "
                "(2) อธิบายถูกเพียงฝั่งเดียว (อีกฝั่งผิดหรือไม่ตอบ), หรือ "
                "(3) อธิบายถูกแต่มีข้อความผิดปะปน หรือระบุสูตร/ดัชนีคลาดเคลื่อน, หรือ "
                "(4) อธิบายวกวน ขาดความชัดเจน\n"
                "- ได้ 0.0 คะแนน: ตอบผิดหลักการชัดเจน (เช่น อ้างอิง Array 2D vs 3D, การคำนวณตรงๆ vs คูณ), เขียนเพียงคำโดดๆ ไม่มีประธานกริยา (เช่น 'คำนวณตำแหน่ง แนวตั้ง แนวนอน'), หรือไม่ตอบ"
            )
        }
    ]
}

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    assert len(items) == 34 and all(x['answer_type'] == 'text' for x in items)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q1-evaluation-optimal-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)
    
    report = {
        'question_no': 1,
        'model': OPENAI_MODEL,
        'prompt_version': PROMPT_VERSION,
        'rubric_source': 'Optimal Human-Aligned Holistic Rubric',
        'started_at': datetime.now(timezone.utc).isoformat(),
        'expected_count': len(items),
        'max_score': OPTIMAL_Q1_META['max_score'],
        'rubrics': OPTIMAL_Q1_META['rubrics'],
        'results': [],
        'failures': []
    }
    
    def save():
        (folder / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        
    sem = asyncio.Semaphore(4)
    
    async def grade(item):
        async with sem:
            result = await score_with_openai(
                question_text=OPTIMAL_Q1_META['question_text'],
                answer_text=item['student_answer'],
                max_score=OPTIMAL_Q1_META['max_score'],
                answer_key=OPTIMAL_Q1_META['answer_key'],
                rubrics=OPTIMAL_Q1_META['rubrics']
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

    print(f"Starting Q1 evaluation with Optimal rubric at {folder}...", flush=True)
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
