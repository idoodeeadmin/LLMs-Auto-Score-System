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

# Calibrated 5-Level Rubric matching Teacher's strictness on 1.0 vs 1.5
RUBRIC_5_LEVEL_V2 = [
    {
        'name': 'การเปรียบเทียบความซับซ้อนและการยกตัวอย่าง (O(n log n) vs O(n^2))',
        'score': 2.0,
        'description': (
            'ประเมินตามระดับคะแนน 5 ระดับ (2.0, 1.5, 1.0, 0.5, 0.0) ดังนี้อย่างเคร่งครัด:\n\n'
            '• 2.0 คะแนน: อธิบายกลไกเหตุผลได้ชัดเจน (เช่น อัตราการเติบโตช้ากว่า, ลูปซ้อนใน n² เทียบกับการแบ่งย่อย/recursive ใน n log n, หรือเปรียบเทียบจำนวนรอบเมื่อข้อมูลใหญ่) และ มีการยกตัวอย่าง Algorithm ได้ถูกต้อง (เช่น Merge, Quick, Bubble)\n\n'
            '• 1.5 คะแนน:\n'
            '   - อธิบายกลไกเหตุผลเรื่องลูปซ้อน/การแบ่งข้อมูล/อัตราการทำงานได้ดี แต่ไม่ได้ยกตัวอย่าง Algorithm\n'
            '   - หรือ อธิบายกลไกเหตุผลได้ดี และยกตัวอย่าง Algorithm ถูกต้องแต่มีข้อบกพร่องเล็กน้อยในคำอธิบาย\n\n'
            '• 1.0 คะแนน:\n'
            '   - ระบุเพียงระดับทั่วไปว่า O(n log n) “เร็วกว่า / ดีกว่า / เสถียรกว่า / ซ้ำซ้อนน้อยกว่า / ประหยัดเวลากว่า” โดยไม่อธิบายกลไกลูปหรือการแบ่งข้อมูล แม้จะมีการยกตัวอย่าง Algorithm หรือสมมุติตัวเลขคำนวณ ก็ให้เพียง 1.0 คะแนนเท่านั้น (ห้ามปัดขึ้นเป็น 1.5 หากไม่มีการอธิบายกลไกเรื่องลูปหรือการตัดข้อมูล)\n\n'
            '• 0.5 คะแนน:\n'
            '   - ระบุได้เพียงชื่อตัวอย่าง Algorithm ที่เกี่ยวข้องอย่างถูกต้อง (เช่น เขียนเฉพาะ Merge Sort หรือ Quick Sort) โดยแทบไม่มีคำอธิบายเหตุผลเลย\n'
            '   - หรือ กล่าวถึงความซับซ้อน/ประสิทธิภาพเพียงฝั่งเดียวอย่างสั้นๆ โดยยังไม่เปรียบเทียบว่าทำไมจึงเหมาะกับข้อมูลใหญ่กว่า O(n²)\n\n'
            '• 0.0 คะแนน: ตอบผิดหลักการทั้งหมด ไม่ตอบ หรือไม่สามารถอธิบายความสัมพันธ์ได้เลย'
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

async def test_all_34():
    items = [x for x in load_dataset() if x['question_no'] == 2]
    print(f"Testing Calibrated 5-Level Rubric V2 on all {len(items)} items...", flush=True)
    
    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text='อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลใหญ่กว่า O(n^2) และยกตัวอย่าง Algorithm',
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=RUBRIC_5_LEVEL_V2,
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

    output_path = ROOT / 'artifacts' / 'q2_calibrated_5level_v2_results.json'
    output_path.write_text(json.dumps({
        'exact': exact,
        'diff05': diff05,
        'total': len(results),
        'mae': round(mae, 4),
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n==========================================")
    print(f"All 34 Summary (V2):")
    print(f"Exact Match: {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.5: {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE: {mae:.4f}")
    print(f"Saved results to {output_path}")
    print(f"==========================================")

if __name__ == '__main__':
    asyncio.run(test_all_34())
