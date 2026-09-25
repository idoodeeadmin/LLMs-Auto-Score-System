"""Evaluate Question 2 with pedagogical rubric (1.5 explanation + 0.5 example)."""
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

Q2_META = {
    "question_no": 2,
    "type": "text",
    "topic": "O(n log n) vs O(n^2) Complexity",
    "max_score": 2.0,
    "question_text": "อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลใหญ่กว่า O(n^2) และยกตัวอย่าง Algorithm",
    "answer_key": (
        "เหตุผล: เมื่อข้อมูลมีขนาดใหญ่ขึ้น อัตราการเติบโตของเวลาในการประมวลผล (Growth rate) ของ O(n log n) จะเพิ่มขึ้นช้ากว่า O(n^2) มาก "
        "โดย O(n^2) มักเกิดจากลูปซ้อนลูป (Nested loops) ทำให้จำนวนรอบการทำงานเพิ่มขึ้นเป็นกำลังสอง เช่น ข้อมูล 1,000 ตัว n^2 ต้องทำ 1,000,000 รอบ "
        "ขณะที่ O(n log n) มักใช้หลักการแบ่งแยกและเอาชนะ (Divide and Conquer) หรือการตัดทอนข้อมูล ทำให้ประมวลผลเร็วกว่าและประหยัดเวลากว่ามาก\n"
        "ตัวอย่าง Algorithm: O(n log n) เช่น Merge Sort, Quick Sort, Heap Sort และ O(n^2) เช่น Bubble Sort, Selection Sort, Insertion Sort"
    ),
    "rubrics": [
        {
            "name": "เหตุผลการเติบโตและประสิทธิภาพ (Growth Rate & Mechanism)",
            "score": 1.5,
            "description": (
                "อธิบายเหตุผลว่าทำไม O(n log n) จึงเหมาะกับข้อมูลขนาดใหญ่กว่า O(n^2):\n"
                "- ได้ 1.5 คะแนน: อธิบายชัดเจนเรื่องอัตราการเติบโตของเวลาที่ช้ากว่ามาก, การใช้รอบการทำงานน้อยกว่า, หรือกลไกเช่น Nested Loop ใน n^2 เทียบกับการแบ่งข้อมูล/Recursive ใน n log n\n"
                "- ได้ 1.0 คะแนน: อธิบายได้เบื้องต้น เช่น ระบุว่าประหยัดเวลา/เร็วกว่า/ตัดข้อมูล แต่คำอธิบายยังสั้นหรือไม่ลงลึก\n"
                "- ได้ 0.0 คะแนน: ตอบผิดหลักการ หรือไม่ตอบ"
            )
        },
        {
            "name": "ตัวอย่าง Algorithm",
            "score": 0.5,
            "description": (
                "ยกตัวอย่าง Algorithm ที่สอดคล้องอย่างน้อย 1 อัลกอริทึม:\n"
                "- ได้ 0.5 คะแนน: ยกตัวอย่าง O(n log n) เช่น Merge Sort, Quick Sort, Heap Sort หรือ O(n^2) เช่น Bubble Sort, Insertion Sort, Selection Sort ได้ถูกต้อง\n"
                "- ได้ 0.0 คะแนน: ไม่ได้ยกตัวอย่าง หรือยกตัวอย่างไม่ถูกต้อง"
            )
        }
    ]
}

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 2]
    assert len(items) == 34 and all(x['answer_type'] == 'text' for x in items)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q2-evaluation-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)
    
    report = {
        'question_no': 2,
        'model': OPENAI_MODEL,
        'prompt_version': PROMPT_VERSION,
        'started_at': datetime.now(timezone.utc).isoformat(),
        'expected_count': len(items),
        'max_score': 2.0,
        'rubrics': Q2_META['rubrics'],
        'results': [],
        'failures': []
    }
    
    def save():
        (folder / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        
    sem = asyncio.Semaphore(4)
    
    async def grade(item):
        async with sem:
            result = await score_with_openai(
                question_text=Q2_META['question_text'],
                answer_text=item['student_answer'],
                max_score=2.0,
                answer_key=Q2_META['answer_key'],
                rubrics=Q2_META['rubrics']
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
            print(f"{item['sample_id']} | Human: {item['human_score']} | AI: {result['score']}", flush=True)
            return True

    print(f"Starting Q2 evaluation at {folder}...", flush=True)
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
    
    print("\n=== SUMMARY QUESTION 2 ===")
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2), flush=True)

if __name__ == '__main__':
    asyncio.run(main())
