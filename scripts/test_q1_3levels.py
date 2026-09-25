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

Q1_3LEVEL_RUBRIC = [
    {
        "name": "Row-major vs Column-major",
        "score": 2.0,
        "description": (
            "ประเมินการอธิบายความแตกต่างของ Row-major vs Column-major (ให้เลือกได้เฉพาะ 2.0, 1.0 หรือ 0.0 คะแนน):\n\n"
            "• 2.0 คะแนน: อธิบายความแตกต่างได้ชัดเจนทั้ง 2 ฝั่ง ว่า Row-major ยึดแนวแถว (Row/แนวนอน) ก่อน และ Column-major ยึดแนวคอลัมน์ (Column/แนวตั้ง/หลัก) ก่อน "
            "โดยครอบคลุมถึงลำดับการจัดเก็บข้อมูล, การคำนวณตำแหน่ง address, ลำดับการนับดัชนี (เช่น [i][j] vs [j][i]), หรือการอธิบายด้วยภาษาพูด/ความเข้าใจ เช่น 'คิดแถวเป็นหลัก vs คิดคอลัมน์เป็นหลัก', 'นับแถวก่อนหลัก vs หลักก่อนแถว', 'ซ้ายไปขวา vs บนลงล่าง' หรือ 'อิงแกน X vs แกน Y'\n\n"
            "• 1.0 คะแนน: อธิบายถูกต้องเพียงฝั่งใดฝั่งหนึ่ง หรือบอกเพียงนิยามเบื้องต้นสั้นๆ (เช่น บอกเพียงว่า Row คือแนวนอน/Column คือแนวตั้ง โดยไม่ได้เชื่อมโยงกับการจัดเก็บหรือการคำนวณ) หรือคำตอบสั้นมากแต่พอเห็นความพยายามแยกแถวกับคอลัมน์\n\n"
            "• 0.0 คะแนน: ตอบผิดหลักการ ไม่ตอบ หรือเขียนเฉพาะคีย์เวิร์ดลอยๆ โดยไม่มีเนื้อหาอธิบาย (เช่น 'คำนวณตำแหน่ง แนวตั้ง แนวนอน' หรือบอกเพียงชื่อภาษาโปรแกรม)"
        ),
        "allowed_scores": [0.0, 1.0, 2.0]
    }
]

ANSWER_KEY = (
    "Row-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามแถว (Row หรือแนวนอน/แกน X) "
    "ส่วน Column-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามคอลัมน์ (Column หรือแนวตั้ง/แกน Y) "
    "ต่างกันที่ลำดับและมิติการเรียงข้อมูลในหน่วยความจำ (ยอมรับคำอธิบายภาษาพูด เช่น คิดแถวก่อนหลัก/หลักก่อนแถว, ซ้ายไปขวา/บนลงล่าง, หรือ [i][j] vs [j][i])"
)

async def test_q1_3levels():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    print(f"Testing Q1 3-level rubric [0.0, 1.0, 2.0] for {len(items)} students...", flush=True)

    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text=it['question_content'],
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=Q1_3LEVEL_RUBRIC,
                allowed_scores=[0.0, 1.0, 2.0]
            )
            s = float(res['score'])
            h = float(it['human_score'])
            diff = round(s - h, 2)
            match = "EXACT MATCH" if diff == 0.0 else f"diff={diff:+.1f}"
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

    truth = [r['human'] for r in results]
    predicted = [r['ai'] for r in results]

    exact = sum(1 for r in results if r['diff'] == 0.0)
    diff05 = sum(1 for r in results if abs(r['diff']) <= 0.5)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=1.0, max_score=2.0)

    out_file = ROOT / 'artifacts' / 'q1_3level_test_results.json'
    out_file.write_text(json.dumps({
        'exact': exact,
        'diff05': diff05,
        'total': len(results),
        'mae': mae,
        'qwk': qwk,
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n==========================================")
    print("Q1 3-LEVEL RUBRIC [0, 1, 2] SUMMARY:")
    print(f"Exact Match:      {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.5:      {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE:              {mae:.4f}")
    print(f"QWK:              {qwk:.4f}")
    print("==========================================")

if __name__ == '__main__':
    asyncio.run(test_q1_3levels())
