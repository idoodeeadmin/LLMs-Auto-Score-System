import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.run_dataset_benchmark import load_dataset, calculate_mae, calculate_qwk
from server.services.openai_grading import score_with_openai

Q4_BINARY_RUBRIC = [
    {
        "name": "ความถูกต้องของ Binary Search Tree (BST)",
        "score": 1.0,
        "description": (
            "ประเมินภาพวาด Binary Search Tree จากข้อมูล: 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99 (ให้เลือกได้เฉพาะ 1.0 หรือ 0.0 คะแนนเท่านั้น):\n\n"
            "• 1.0 คะแนน: โครงสร้าง BST ถูกต้องครบทั้ง 12 โหนดตามหลักการ BST (โหนดซ้าย < โหนดแม่ < โหนดขวา):\n"
            "  - Root คือ 9 (ซ้าย 5, ขวา 16)\n"
            "  - ใต้ 16 มี 10 ทางซ้าย, 76 ทางขวา\n"
            "  - ใต้ 10 มี 13 ทางขวา\n"
            "  - ใต้ 13 มี 11 ทางซ้าย, 15 ทางขวา\n"
            "  - ใต้ 76 มี 58 ทางซ้าย, 92 ทางขวา\n"
            "  - ใต้ 92 มี 80 ทางซ้าย, 99 ทางขวา\n"
            "  (ให้อนุโลมความสวยงาม ลายมือ ความยาว/มุมเอียงของกิ่ง และรอยร่างดินสอส่วนเกิน ขอเพียงโครงสร้างและค่าของโหนดสื่อสารได้ถูกต้อง)\n\n"
            "• 0.0 คะแนน: ผิดหลักการ BST เช่น วางตำแหน่งโหนดผิด, สลับกิ่งซ้าย-ขวา, โหนดแตกกิ่งเกิน 2 กิ่ง, ตัวเลขตกหล่นไม่ครบ 12 โหนด, หรือไม่วาดคำตอบ"
        ),
        "allowed_scores": [0.0, 1.0]
    }
]

Q4_QUESTION_TEXT = (
    "จากข้อมูลต่อไปนี้จงนำไปสร้างเป็น Binary search tree (1 คะแนน)\n"
    "9 16 10 76 5 13 58 92 11 15 80 99"
)

Q4_ANSWER_KEY = (
    "เฉลยโครงสร้าง Binary Search Tree (BST) ที่ถูกต้องสมบูรณ์:\n"
    "- Root คือ 9\n"
    "  - กิ่งซ้าย: 5\n"
    "  - กิ่งขวา: 16\n"
    "    - ใต้ 16 กิ่งซ้าย: 10\n"
    "      - ใต้ 10 กิ่งขวา: 13 (กิ่งซ้ายว่าง)\n"
    "        - ใต้ 13 กิ่งซ้าย: 11\n"
    "        - ใต้ 13 กิ่งขวา: 15\n"
    "    - ใต้ 16 กิ่งขวา: 76\n"
    "      - ใต้ 76 กิ่งซ้าย: 58\n"
    "      - ใต้ 76 กิ่งขวา: 92\n"
    "        - ใต้ 92 กิ่งซ้าย: 80\n"
    "        - ใต้ 92 กิ่งขวา: 99\n"
    "รวมทั้งหมด 12 โหนด โดยทุกโหนดลูกทางซ้ายต้องมีค่าน้อยกว่าโหนดแม่ และลูกทางขวาต้องมีค่ามากกว่าโหนดแม่"
)

async def run_q4_binary():
    items = [x for x in load_dataset() if x['question_no'] == 4]
    print(f"Starting Q4 Binary Regrade (0 or 1 only) for {len(items)} students...", flush=True)

    sem = asyncio.Semaphore(4)
    async def grade_one(it):
        async with sem:
            img_bytes = None
            if it['student_img_path'] and os.path.exists(it['student_img_path']):
                with open(it['student_img_path'], 'rb') as f:
                    img_bytes = f.read()

            res = await score_with_openai(
                question_text=Q4_QUESTION_TEXT,
                answer_text=it['student_answer'] or '',
                max_score=1.0,
                answer_key=Q4_ANSWER_KEY,
                rubrics=Q4_BINARY_RUBRIC,
                image_bytes_list=[img_bytes] if img_bytes else None,
                image_mime_list=["image/jpeg"] if img_bytes else None,
                allowed_scores=[0.0, 1.0]
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
                'confidence': res.get('confidence', 'high'),
                'teacher_feedback': res.get('teacher_feedback', ''),
                'student_feedback': res.get('student_feedback', ''),
            }

    results = await asyncio.gather(*(grade_one(it) for it in items))
    results.sort(key=lambda x: x['sample_id'])

    truth = [r['human'] for r in results]
    predicted = [r['ai'] for r in results]

    exact = sum(1 for r in results if r['diff'] == 0.0)
    diff05 = sum(1 for r in results if abs(r['diff']) <= 0.5)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=1.0, max_score=1.0)

    out_file = ROOT / 'artifacts' / 'q4_binary_eval_results.json'
    out_file.write_text(json.dumps({
        'exact': exact,
        'diff05': diff05,
        'total': len(results),
        'mae': mae,
        'qwk': qwk,
        'results': results
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n==========================================")
    print("Q4 BINARY (0 or 1 only) SUMMARY:")
    print(f"Exact Match:      {exact}/{len(results)} ({exact/len(results)*100:.1f}%)")
    print(f"Diff <= 0.5:      {diff05}/{len(results)} ({diff05/len(results)*100:.1f}%)")
    print(f"MAE:              {mae:.4f}")
    print(f"QWK:              {qwk:.4f}")
    print("==========================================")

if __name__ == '__main__':
    asyncio.run(run_q4_binary())
