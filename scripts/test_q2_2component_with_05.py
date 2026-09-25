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

Q2_RUBRICS_WITH_05 = [
    {
        "name": "เหตุผลการเติบโตและประสิทธิภาพ (Growth Rate & Mechanism)",
        "score": 1.5,
        "description": (
            "อธิบายเหตุผลว่าทำไม O(n log n) จึงเหมาะกับข้อมูลขนาดใหญ่กว่า O(n^2):\n"
            "- ได้ 1.5 คะแนน: อธิบายชัดเจนเรื่องอัตราการเติบโตของเวลา/จำนวนรอบที่ช้ากว่ามาก, การใช้ลูปซ้อนใน n^2 เทียบกับการแบ่งข้อมูล/Recursive ใน n log n หรือเปรียบเทียบการเพิ่มขึ้นของจำนวนรอบเมื่อข้อมูลมีขนาดใหญ่ (ให้อนุโลมภาษาพูด)\n"
            "- ได้ 1.0 คะแนน: อธิบายแก่นได้เบื้องต้น เช่น ระบุว่าเร็วกว่า/ประหยัดเวลากว่า/ตัดทอนข้อมูล หรือยกตัวอย่างคำนวณตัวเลขเปรียบเทียบ แต่ยังไม่ได้อธิบายกลไกลูปหรืออัตราเติบโตเชิงลึก\n"
            "- ได้ 0.5 คะแนน: กล่าวถึงลักษณะ Big-O เพียงฝั่งเดียวสั้นๆ หรือมีเหตุผลบางส่วนแต่ยังไม่เชื่อมโยงชัดเจนว่าทำไมจึงเหมาะกับข้อมูลขนาดใหญ่\n"
            "- ได้ 0.0 คะแนน: ตอบผิดหลักการ หรือไม่ตอบ"
        ),
        "allowed_scores": [0.0, 0.5, 1.0, 1.5]
    },
    {
        "name": "ตัวอย่าง Algorithm",
        "score": 0.5,
        "description": (
            "ยกตัวอย่าง Algorithm ที่สอดคล้องอย่างน้อย 1 อัลกอริทึม:\n"
            "- ได้ 0.5 คะแนน: ยกตัวอย่าง Algorithm ได้ถูกต้อง เช่น O(n log n) ได้แก่ Merge Sort, Quick Sort, Heap Sort หรือ O(n^2) ได้แก่ Bubble Sort, Insertion Sort, Selection Sort (แม้จะยกตัวอย่างเพียงฝั่งเดียวแต่ถูกต้องก็ให้ได้)\n"
            "- ได้ 0.0 คะแนน: ไม่ได้ยกตัวอย่าง หรือยกตัวอย่างไม่ถูกต้อง"
        ),
        "allowed_scores": [0.0, 0.5]
    }
]

ANSWER_KEY = (
    "เหตุผล: เมื่อข้อมูลมีขนาดใหญ่ขึ้น อัตราการเติบโตของเวลาในการประมวลผล (Growth rate) ของ O(n log n) จะเพิ่มขึ้นช้ากว่า O(n^2) มาก "
    "โดย O(n^2) มักเกิดจากลูปซ้อนลูป (Nested loops) ทำให้จำนวนรอบการทำงานเพิ่มขึ้นเป็นกำลังสอง เช่น ข้อมูล 1,000 ตัว n^2 ต้องทำ 1,000,000 รอบ "
    "ขณะที่ O(n log n) มักใช้หลักการแบ่งแยกและเอาชนะ (Divide and Conquer) หรือการตัดทอนข้อมูล ทำให้ประมวลผลเร็วกว่าและประหยัดเวลากว่ามาก\n"
    "ตัวอย่าง Algorithm: O(n log n) เช่น Merge Sort, Quick Sort, Heap Sort และ O(n^2) เช่น Bubble Sort, Selection Sort, Insertion Sort"
)

async def test_2component():
    items = [x for x in load_dataset() if x['question_no'] == 2]
    print(f"Testing 2-Component Rubric (with 0.5 support) on {len(items)} items...", flush=True)
    
    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text="อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลใหญ่กว่า O(n^2) และยกตัวอย่าง Algorithm",
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=Q2_RUBRICS_WITH_05
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

    print(f"\n==========================================")
    print(f"2-Component (Supporting 0.5) Summary:")
    print(f"Exact Match: {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.5: {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE: {mae:.4f}")
    print(f"==========================================")

if __name__ == '__main__':
    asyncio.run(test_2component())
