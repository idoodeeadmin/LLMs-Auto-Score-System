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

# Option A Calibrated 5-Level Rubric
RUBRIC_OPTION_A = [
    {
        'name': 'การเปรียบเทียบความซับซ้อนและการยกตัวอย่าง (O(n log n) vs O(n^2))',
        'score': 2.0,
        'description': (
            'ประเมินตามระดับคะแนน 5 ระดับ (2.0, 1.5, 1.0, 0.5, 0.0) ตามแนวทางการตรวจจริงของอาจารย์อย่างเคร่งครัด:\n\n'
            '• 2.0 คะแนน: อธิบายกลไกเชิงเทคนิคได้ชัดเจน (เช่น อัตราการเติบโตช้ากว่า, O(n²) มีลูปซ้อน/จำนวนรอบเพิ่มมหาศาลเมื่อ n โต เทียบกับ O(n log n) ที่ตัดทอน/แบ่งข้อมูล/recursive) และ มีการยกตัวอย่าง Algorithm ได้ถูกต้องอย่างน้อย 1 ตัวอย่าง (เช่น Merge Sort, Quick Sort, Bubble Sort) ห้ามกดเหลือ 1.5 หากมีทั้งกลไกและตัวอย่าง\n\n'
            '• 1.5 คะแนน:\n'
            '   - (กรณี 1): อธิบายกลไกเรื่องลูปซ้อน/การตัดแบ่งข้อมูล/อัตราการเติบโตได้ดี แต่ไม่ได้ยกตัวอย่าง Algorithm\n'
            '   - (กรณี 2): อธิบายกลไกได้ดี และยกตัวอย่าง Algorithm ถูกต้องแต่มีส่วนคลาดเคลื่อนเล็กน้อย\n\n'
            '• 1.0 คะแนน (สำคัญมาก - พฤติกรรมอาจารย์):\n'
            '   - อธิบายเพียงระดับทั่วไปว่า O(n log n) “เร็วกว่า / ดีกว่า / เสถียรกว่า / ซ้ำซ้อนน้อยกว่า / ประหยัดเวลากว่า” โดยไม่มีการอธิบายกลไกเชิงลึก (ไม่มีเรื่องลูปซ้อน ไม่มีการตัดแบ่งข้อมูล) แม้จะมีการยกตัวอย่าง Algorithm (เช่น Merge Sort หรือ Quick Sort) หรือมีการสมมุติตัวเลขคำนวณ n=10 ก็ตาม ให้ได้เพียง 1.0 คะแนนเท่านั้น (ห้ามปัดขึ้นเป็น 1.5 หากไม่มีการอธิบายกลไก)\n\n'
            '• 0.5 คะแนน: มีเพียงชื่อตัวอย่าง Algorithm ที่ถูกต้องลอยๆ (เช่น เขียนเฉพาะ Merge Sort หรือ Quick Sort) โดยไม่มีคำอธิบายเหตุผลใดๆ เลย หรือกล่าวถึงเพียงข้อความสั้นมากที่ไม่เปรียบเทียบความต่าง\n\n'
            '• 0.0 คะแนน: ตอบผิดหลักการทั้งหมด (เช่น บอกว่า n² เร็วกว่า), ไม่ตอบ, หรือตอบไม่เกี่ยวข้องกับโจทย์เลย (เช่น พูดเรื่องโยนเหรียญ)'
        ),
        'allowed_scores': [0.0, 0.5, 1.0, 1.5, 2.0]
    }
]

ANSWER_KEY = (
    'เหตุผล: เมื่อข้อมูลมีขนาดใหญ่ขึ้น อัตราการเติบโตของเวลาในการประมวลผล (Growth rate) ของ O(n log n) จะเพิ่มขึ้นช้ากว่า O(n^2) มาก '
    'โดย O(n^2) มักเกิดจากลูปซ้อนลูป (Nested loops) ทำให้จำนวนรอบการทำงานเพิ่มขึ้นเป็นกำลังสอง เช่น ข้อมูล 1,000 ตัว n^2 ต้องทำ 1,000,000 รอบ '
    'ขณะที่ O(n log n) มักใช้หลักการแบ่งแยกและเอาชนะ (Divide and Conquer) หรือการตัดทอนข้อมูล ทำให้ประมวลผลเร็วกว่าและประหยัดเวลากว่ามาก\n'
    'ตัวอย่าง Algorithm: O(n log n) เช่น Merge Sort, Quick Sort, Heap Sort และ O(n^2) เช่น Bubble Sort, Selection Sort, Insertion Sort'
)

async def test_option_a():
    items = [x for x in load_dataset() if x['question_no'] == 2]
    print(f"Running Option A on all {len(items)} items...", flush=True)
    
    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text='อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลใหญ่กว่า O(n^2) และยกตัวอย่าง Algorithm',
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=RUBRIC_OPTION_A,
                allowed_scores=[0.0, 0.5, 1.0, 1.5, 2.0]
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

    output_path = ROOT / 'artifacts' / 'q2_option_a_results.json'
    output_path.write_text(json.dumps({
        'exact': exact,
        'diff05': diff05,
        'total': len(results),
        'mae': round(mae, 4),
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n==========================================")
    print(f"Option A Summary:")
    print(f"Exact Match: {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.5: {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE: {mae:.4f}")
    print(f"Saved results to {output_path}")
    print(f"==========================================")

if __name__ == '__main__':
    asyncio.run(test_option_a())
