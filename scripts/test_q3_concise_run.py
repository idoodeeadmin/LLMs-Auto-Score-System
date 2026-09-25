import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from scripts.run_dataset_benchmark import load_dataset, calculate_mae, calculate_qwk
from server.services.openai_grading import score_with_openai

# Test 1: Concise 2-Part Component Rubric (Difference 0.5 + Pros/Cons 0.5)
Q3_COMPONENT_RUBRIC = [
    {
        "name": "ความแตกต่างเชิงโครงสร้าง (Comparison)",
        "score": 0.5,
        "description": (
            "ประเมินการเปรียบเทียบความแตกต่างระหว่าง Linked List กับ Array ในการทำ Stack/Queue (ให้ 0.5, 0.25 หรือ 0.0 คะแนน):\n"
            "• 0.50 คะแนน: อธิบายความแตกต่างของขนาด/โครงสร้างได้ชัดเจน เช่น Array มีขนาดคงที่ (Fixed size) หรือต้องระบุขนาดล่วงหน้า ส่วน Linked List มีขนาดปรับเปลี่ยนได้ (Dynamic size) ยืดหยุ่น หรือใช้ pointer/โหนดเชื่อมต่อ\n"
            "• 0.25 คะแนน: เข้าใจเบื้องต้น หรือตอบถูกเพียงฝั่งใดฝั่งหนึ่ง\n"
            "• 0.00 คะแนน: ไม่ได้เปรียบเทียบโครงสร้าง หรือตอบผิดหลักการ"
        ),
        "allowed_scores": [0.0, 0.25, 0.5]
    },
    {
        "name": "ข้อดีและข้อเสีย (Pros & Cons)",
        "score": 0.5,
        "description": (
            "ประเมินการระบุข้อดีและข้อเสีย (ให้ 0.5, 0.25 หรือ 0.0 คะแนน):\n"
            "• 0.50 คะแนน: ระบุทั้งข้อดีและข้อเสียได้สมเหตุสมผล เช่น Linked List ไม่จำกัดขนาด/ไม่เกิด overflow แต่เข้าถึงช้ากว่า/เปลือง pointer หรือ Array เข้าถึงเร็วแต่จำกัดขนาด/เสี่ยง overflow\n"
            "• 0.25 คะแนน: ระบุเฉพาะข้อดีอย่างเดียว หรือเฉพาะข้อเสียอย่างเดียว หรือข้อดีข้อเสียยังไม่ชัดเจน\n"
            "• 0.00 คะแนน: ไม่ได้ระบุข้อดีข้อเสีย หรือระบุผิดหลักการ"
        ),
        "allowed_scores": [0.0, 0.25, 0.5]
    }
]

ANSWER_KEY = (
    "ความแตกต่าง: Array มีขนาดคงที่ (Fixed/Static size) ต้องระบุขนาดล่วงหน้า จองพื้นที่ต่อเนื่อง "
    "ส่วน Linked List มีขนาดปรับเปลี่ยนได้แบบพลวัต (Dynamic size) ไม่จำกัดขนาดล่วงหน้า ใช้พอยน์เตอร์เชื่อมต่อโหนด\n"
    "ข้อดีข้อเสีย:\n"
    "- Linked List: ข้อดีคือยืดหยุ่น เพิ่ม/ลดข้อมูลง่าย ไม่เกิด Overflow; ข้อเสียคือเข้าถึงข้อมูลช้ากว่า (Sequential access) และสิ้นเปลืองเนื้อที่จัดเก็บ Pointer\n"
    "- Array: ข้อดีคือเข้าถึงข้อมูลได้เร็วโดยตรงด้วย Index O(1); ข้อเสียคือขยายขนาดยาก และเสี่ยงต่อ Overflow หากข้อมูลเกินขนาดที่จองไว้"
)

async def test_q3():
    items = [x for x in load_dataset() if x['question_no'] == 3]
    print(f"Testing Q3 Concise 2-Part Component Rubric for {len(items)} students...", flush=True)

    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text=it['question_content'],
                answer_text=it['student_answer'],
                max_score=1.0,
                answer_key=ANSWER_KEY,
                rubrics=Q3_COMPONENT_RUBRIC,
                allowed_scores=[0.0, 0.25, 0.5, 0.75, 1.0]
            )
            s = float(res['score'])
            h = float(it['human_score'])
            diff = round(s - h, 2)
            match = "EXACT MATCH" if diff == 0.0 else f"diff={diff:+.2f}"
            print(f"{it['sample_id']} | Human: {h:.2f} | AI: {s:.2f} | {match}", flush=True)
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

    truth = [r['human'] for r in results]
    predicted = [r['ai'] for r in results]

    exact = sum(1 for r in results if r['diff'] == 0.0)
    diff025 = sum(1 for r in results if abs(r['diff']) <= 0.25)
    diff05 = sum(1 for r in results if abs(r['diff']) <= 0.5)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=0.25, max_score=1.0)

    out_file = ROOT / 'artifacts' / 'q3_concise_test_results.json'
    out_file.write_text(json.dumps({
        'exact': exact,
        'diff025': diff025,
        'diff05': diff05,
        'total': len(results),
        'mae': mae,
        'qwk': qwk,
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n==========================================")
    print("Q3 CONCISE COMPONENT RUBRIC SUMMARY:")
    print(f"Exact Match:      {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.25:     {diff025}/{len(results)} ({diff025/len(results)*100:.1f}%)")
    print(f"Diff <= 0.50:     {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE:              {mae:.4f}")
    print(f"QWK:              {qwk:.4f}")
    print("==========================================")

if __name__ == '__main__':
    asyncio.run(test_q3())
