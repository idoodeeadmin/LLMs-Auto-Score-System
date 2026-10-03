# -*- coding: utf-8 -*-
"""
Test Q1 with calibrated teacher-style rubric that encourages AI to reason holistically
rather than rigid keyword matching.
"""

import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from scripts.run_dataset_benchmark import load_dataset, calculate_mae, calculate_qwk
from server.services.openai_grading import score_with_openai

# New holistic, teacher-calibrated rubric for Question 1
Q1_TEACHER_CALIBRATED_RUBRIC = [
    {
        "name": "ความเข้าใจและการเปรียบเทียบ Row-major vs Column-major",
        "score": 2.0,
        "description": (
            "ประเมินความเข้าใจเชิงมโนทัศน์ (Conceptual Understanding) ของผู้เรียนตามสไตล์การตรวจจริงของอาจารย์ผู้สอน (ระดับคะแนน: 2.0, 1.0 หรือ 0.0 คะแนน):\n\n"
            "• ได้ 2.00 คะแนน (เต็ม): อธิบายความแตกต่างของทั้ง 2 ฝั่งในบริบทของโครงสร้าง Array หรือการจัดการข้อมูลได้ครบถ้วน (ทั้ง Row-major และ Column-major) ครอบคลุมกรณีใดกรณีหนึ่งต่อไปนี้:\n"
            "  1. ทิศทาง/มิติการจัดเก็บใน Array: ระบุว่า Row-major จัดเก็บ เรียง หรือแสดงผล Array ในแนวนอน (หรือตามแถว/แกน X/ซ้ายไปขวา) และ Column-major ในแนวตั้ง (หรือตามคอลัมน์/หลัก/แกน Y/บนลงล่าง) (เช่น 'Row-major เป็นแนวนอน Column-major เป็นแนวตั้ง' ในบริบท Array)\n"
            "  2. ลำดับการนับ/การเรียก/การคำนวณ: ระบุว่า Row-major จะอิง/เรียก/คิดแถวก่อนหลัก ส่วน Column-major จะอิง/เรียก/คิดหลัก(คอลัมน์)ก่อนแถว (เช่น 'คิดแถวเป็นหลัก vs คิดคอลัมน์เป็นหลัก', 'เรียกแถวก่อนหลัก vs เรียกหลักก่อนแถว', 'เอาแถวก่อน vs เอาคอลัมน์ก่อน')\n"
            "  3. การหา Address หรือลำดับดัชนี: ระบุว่า Row-major คำนวณหา address โดยเน้น/อิงแถว ส่วน Column-major อิงคอลัมน์ หรือระบุดัชนี 2 มิติว่า Row-major คือ (i, j) หรือ [i][j] ส่วน Column-major คือ (j, i) หรือ [j][i]\n\n"
            "• ได้ 1.00 คะแนน (คะแนนความเข้าใจบางส่วน / อนุโลมตามสไตล์อาจารย์ผู้สอน):\n"
            "  1. ตอบนิยามคำศัพท์ทั่วไปโดยไม่อิง Array: บอกเพียงความหมายของคำว่า Row และ Column ทั่วไป เช่น 'Row คือ แถวแนวนอน, Column คือ แถวแนวตั้ง' โดยไม่ได้กล่าวถึง Array หรือ -major (อาจารย์อนุโลมให้ 1 คะแนนสำหรับความเข้าใจพื้นฐาน)\n"
            "  2. ตอบสั้นมากและขาดการอธิบายกลไก: เช่น เขียนเพียง 'เริ่มเรียงจากฝั่งแถว / เริ่มเรียงจากฝั่งคอลัมน์', หรือเขียนแค่คู่ดัชนีตัวเลข [0][0],[0][1] ลอยๆ, หรือตอบสั้นๆ ว่าคิดที่แนวนอนก่อน/แนวตั้งก่อน โดยไม่อธิบายเชื่อมโยงความหมาย\n"
            "  3. อธิบายถูกต้องชัดเจนเพียงฝั่งใดฝั่งหนึ่ง แต่อีกฝั่งหนึ่งไม่ตอบ ตอบไม่ชัดเจน หรือไม่ครบ\n"
            "  4. มีข้อความที่เข้าใจผิดหรือสับสนปนอยู่: เช่น เขียนสูตรหรือลูปตัวแปรสับสนและกำกวม (เช่น อธิบายว่าสูตรต่างกันเล็กน้อยแต่ไม่บอกว่าต่างอย่างไร หรือระบุสูตร/ดัชนีคลาดเคลื่อน)\n\n"
            "• ได้ 0.00 คะแนน (ไม่ได้คะแนน):\n"
            "  1. ไม่ตอบ หรือตอบผิดหลักการทั้งหมดอย่างสิ้นเชิง\n"
            "  2. เขียนข้อความมั่วที่ไม่มีความหมายในทางโครงสร้างข้อมูล เช่น มโนว่าเป็น Array 3D vs 2D, หรือเขียนว่า 'ใช้แถวเป็นตัวตั้ง / ใช้คอลัมน์เป็นตัวตั้ง' ลอยๆ โดยไม่มีการอธิบายมิติ ลำดับ หรือทิศทางใดๆ\n"
            "  3. ตอบเรื่องอื่นที่ไม่เกี่ยวกับการจัดการข้อมูล หรือเขียนเฉพาะคีย์เวิร์ดลอยๆ เช่น 'คำนวณตำแหน่ง แนวตั้ง แนวนอน'"
        ),
        "allowed_scores": [0.0, 1.0, 2.0]
    }
]

ANSWER_KEY = (
    "Row-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามแถว (Row หรือแนวนอน/แกน X) ให้ครบแถวก่อน "
    "ส่วน Column-major คือการจัดเก็บข้อมูล ลำดับการเรียง หรือคำนวณตำแหน่ง address โดยอิงตามคอลัมน์ (Column หรือแนวตั้ง/แกน Y) ให้พบคอลัมน์ก่อน "
    "ต่างกันที่ลำดับและมิติการเรียงข้อมูลในหน่วยความจำ (ยอมรับทั้งคำอธิบายเชิงทฤษฎี ภาษาพูด เช่น คิดแถวก่อนหลัก/หลักก่อนแถว, หรือตัวอย่างดัชนี [i][j])"
)

async def test_q1():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    print(f"Testing Q1 Teacher-Calibrated Rubric for {len(items)} students...", flush=True)

    sem = asyncio.Semaphore(5)
    async def grade_one(it):
        async with sem:
            res = await score_with_openai(
                question_text=it['question_content'],
                answer_text=it['student_answer'],
                max_score=2.0,
                answer_key=ANSWER_KEY,
                rubrics=Q1_TEACHER_CALIBRATED_RUBRIC,
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

    out_file = ROOT / 'artifacts' / 'q1_teacher_calibrated_results.json'
    out_file.write_text(json.dumps({
        'exact': exact,
        'diff05': diff05,
        'total': len(results),
        'mae': mae,
        'qwk': qwk,
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n==========================================")
    print("Q1 TEACHER-CALIBRATED SUMMARY:")
    print(f"Exact Match:      {exact}/{len(results)} ({exact/len(results)*100:.2f}%)")
    print(f"Diff <= 0.5:      {diff05}/{len(results)} ({diff05/len(results)*100:.2f}%)")
    print(f"MAE:              {mae:.4f}")
    print(f"QWK:              {qwk:.4f}")
    print("==========================================")

    print("\nDiscrepancies:")
    for r in results:
        if r['diff'] != 0:
            print(f"  {r['sample_id']} | Human: {r['human']} | AI: {r['ai']} | Ans: {repr(r['answer'][:60])}")

if __name__ == '__main__':
    asyncio.run(test_q1())
