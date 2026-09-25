import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from scripts.run_dataset_benchmark import load_dataset
from server.services.openai_grading import score_with_openai

# Shortest & Most Effective 2-Part Rubric
SHORT_2PART_RUBRIC = [
    {
        "name": "ส่วนที่ 1: การอธิบายเหตุผล",
        "score": 1.5,
        "description": (
            "ประเมินเหตุผลว่าทำไม O(n log n) เหมาะกับข้อมูลขนาดใหญ่กว่า O(n^2):\n"
            "- 1.5 คะแนน: อธิบายแก่นเหตุผลได้ (เช่น เวลา/รอบโตช้ากว่า, n^2 เป็นลูปซ้อนทำให้ช้า, n log n แบ่งข้อมูล/recursive) ให้อนุโลมภาษาพูด\n"
            "- 1.0 คะแนน: ตอบถูกเบื้องต้น เช่น ระบุว่าเร็วกว่า/เสถียรกว่า หรือยกตัวอย่างตัวเลขคำนวณเปรียบเทียบ\n"
            "- 0.0 คะแนน: ตอบผิดหลักการ หรือไม่ตอบ"
        ),
        "allowed_scores": [0.0, 1.0, 1.5]
    },
    {
        "name": "ส่วนที่ 2: ตัวอย่าง Algorithm",
        "score": 0.5,
        "description": (
            "ยกตัวอย่าง Algorithm ที่เกี่ยวข้องอย่างน้อย 1 ตัวอย่าง (เช่น Merge Sort, Quick Sort, Bubble Sort ฯลฯ):\n"
            "- 0.5 คะแนน: ยกตัวอย่างอัลกอริทึมได้ถูกต้อง\n"
            "- 0.0 คะแนน: ไม่ได้ยกตัวอย่าง หรือยกตัวอย่างผิด"
        ),
        "allowed_scores": [0.0, 0.5]
    }
]

ANSWER_KEY = (
    'เหตุผล: เมื่อข้อมูลมีขนาดใหญ่ขึ้น อัตราการเติบโตของเวลาในการประมวลผล (Growth rate) ของ O(n log n) จะเพิ่มขึ้นช้ากว่า O(n^2) มาก '
    'โดย O(n^2) มักเกิดจากลูปซ้อนลูป (Nested loops) ทำให้จำนวนรอบการทำงานเพิ่มขึ้นเป็นกำลังสอง เช่น ข้อมูล 1,000 ตัว n^2 ต้องทำ 1,000,000 รอบ '
    'ขณะที่ O(n log n) มักใช้หลักการแบ่งแยกและเอาชนะ (Divide and Conquer) หรือการตัดทอนข้อมูล ทำให้ประมวลผลเร็วกว่าและประหยัดเวลากว่ามาก\n'
    'ตัวอย่าง Algorithm: O(n log n) เช่น Merge Sort, Quick Sort, Heap Sort และ O(n^2) เช่น Bubble Sort, Selection Sort, Insertion Sort'
)

async def test_short_2part():
    items = [x for x in load_dataset() if x['question_no'] == 2]
    print(f"Testing Short 2-Part Rubric on {len(items)} items...", flush=True)
    
    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text='อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลใหญ่กว่า O(n^2) และยกตัวอย่าง Algorithm',
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=SHORT_2PART_RUBRIC
            )
            s = res['score']
            h = it['human_score']
            diff = round(s - h, 2)
            match = "MATCH" if diff == 0.0 else f"diff={diff:+.1f}"
            print(f"{it['sample_id']} | Human: {h:.1f} | AI: {s:.1f} | {match}", flush=True)
            return {
                'sample_id': it['sample_id'],
                'human': h,
                'ai': s,
                'diff': diff,
                'confidence': res.get('confidence', 'medium'),
                'teacher_feedback': res.get('teacher_feedback', ''),
                'student_feedback': res.get('student_feedback', ''),
                'answer': it['student_answer']
            }

    results = await asyncio.gather(*(grade_one(it) for it in items))
    results.sort(key=lambda x: x['sample_id'])

    exact = sum(1 for r in results if r['diff'] == 0.0)
    diff05 = sum(1 for r in results if abs(r['diff']) <= 0.5)
    mae = sum(abs(r['diff']) for r in results) / len(results)

    output_path = ROOT / 'artifacts' / 'q2_short_2part_results.json'
    output_path.write_text(json.dumps({
        'exact': exact,
        'diff05': diff05,
        'total': len(results),
        'mae': round(mae, 4),
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n==========================================")
    print(f"Short 2-Part Summary:")
    print(f"Exact Match: {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.5: {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE: {mae:.4f}")
    print(f"Saved results to {output_path}")
    print(f"==========================================")

if __name__ == '__main__':
    asyncio.run(test_short_2part())
