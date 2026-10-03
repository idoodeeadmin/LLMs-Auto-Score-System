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

Q4_VISUAL_KEY_PATH = str(ROOT / 'public/answer-keys/q4_bst_ground_truth.png')

Q4_PROMPT_RUBRIC = [
    {
        "name": "ความถูกต้องของ Binary Search Tree (BST 12 โหนด)",
        "score": 1.0,
        "description": (
            "ประเมินภาพวาด Binary Search Tree จากข้อมูล: 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99 (เลือกได้เฉพาะ 1.0 หรือ 0.0 คะแนนเท่านั้น):\n\n"
            "• ให้เปรียบเทียบภาพวาดของนักเรียนกับ [รูปภาพแนวคำตอบสำหรับใช้ตรวจ] ที่แนบมาอย่างละเอียดทีละเส้นเชื่อม:\n"
            "  1. โหนด 9 (สำคัญมาก): ต้องเป็นโหนดราก (Root บนสุด) เท่านั้น เพราะ 9 เป็นข้อมูลตัวแรกที่ถูกนำเข้า หากนักเรียนนำตัวอื่น เช่น 16 ไปเป็นโหนดราก ให้ถือว่าผิดโครงสร้าง BST ทันที และให้ 0.00 คะแนน\n"
            "  2. โหนด 15 (สำคัญที่สุด): ต้องเป็นลูกขวาของโหนด 13 เท่านั้น! หากเส้นเชื่อมของ 15 ลากไปต่อใต้ 58 หรือต่อผิดกิ่ง ให้ถือว่าผิดโครงสร้าง BST ทันที และให้ 0.00 คะแนน\n"
            "  3. โหนด 58: ต้องเป็น Leaf Node ไม่มีลูกหลานใดๆ ต่อลงมาทั้งสิ้น\n"
            "  4. โหนด 11: ต้องต่อเป็นลูกซ้ายของ 13 (ห้ามต่อตรงกับโหนด 10)\n"
            "  5. โหนด 16: ซ้าย 10, ขวา 76\n"
            "  6. โหนด 76: ซ้าย 58, ขวา 92 (92 มีซ้าย 80, ขวา 99)\n\n"
            "• 1.0 คะแนน: โครงสร้างและเส้นเชื่อมถูกต้องครบถ้วนตรงตามภาพเฉลยทั้ง 12 โหนด (อนุโลมความสวยงาม ลายมือ และรอยร่างจางๆ ขอเพียงเส้นเชื่อมและโหนดหลักถูกต้อง)\n"
            "• 0.0 คะแนน: วางโหนดผิดตำแหน่ง, โหนดรากไม่ใช่ 9, เส้นเชื่อมต่อผิดกิ่งแม้แต่กิ่งเดียว, สลับซ้าย-ขวา, ขาดโหนด, หรือไม่วาดคำตอบ"
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
    "- เปรียบเทียบภาพวาดนักเรียนกับภาพเฉลยแนวคำตอบที่แนบมา (Ground Truth Key Image)\n"
    "- Root = 9 (ซ้าย 5, ขวา 16)\n"
    "- ใต้ 16 มี 10 (ซ้าย) และ 76 (ขวา)\n"
    "- ใต้ 10 มี 13 (ขวา) เท่านั้น\n"
    "- ใต้ 13 มี 11 (ซ้าย) และ 15 (ขวา)\n"
    "- ใต้ 76 มี 58 (ซ้าย เป็น Leaf) และ 92 (ขวา)\n"
    "- ใต้ 92 มี 80 (ซ้าย) และ 99 (ขวา)\n"
    "- ข้อควรระวังพิเศษ: โหนด 15 ต้องต่อใต้ 13 เท่านั้น ห้ามต่อใต้ 58 เด็ดขาด"
)

async def main():
    with open(Q4_VISUAL_KEY_PATH, 'rb') as f:
        key_img_bytes = f.read()

    items = [x for x in load_dataset() if x['question_no'] == 4]
    print(f"==================================================", flush=True)
    print(f"Starting Q4 Regrade with Visual Answer Key for {len(items)} students...", flush=True)
    print(f"Visual Key: {Q4_VISUAL_KEY_PATH} ({len(key_img_bytes)} bytes)", flush=True)
    print(f"==================================================", flush=True)

    sem = asyncio.Semaphore(6)

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
                rubrics=Q4_PROMPT_RUBRIC,
                image_bytes_list=[img_bytes] if img_bytes else None,
                image_mime_list=["image/jpeg"] if img_bytes else None,
                answer_key_image_bytes_list=[key_img_bytes],
                answer_key_image_mime_list=["image/png"],
                allowed_scores=[0.0, 1.0],
                strict_rubric_enforcement=True
            )

            s = float(res['score'])
            h = float(it['human_score'])
            diff = round(s - h, 2)
            match = "EXACT MATCH" if diff == 0.0 else f"DIFF={diff:+.2f}"
            print(f"[{it['sample_id']}] Human: {h:.2f} | AI: {s:.2f} | {match}", flush=True)
            return {
                'sample_id': it['sample_id'],
                'human': h,
                'ai': s,
                'diff': diff,
                'confidence': res.get('confidence', 'high'),
                'teacher_feedback': res.get('teacher_feedback', ''),
                'student_feedback': res.get('student_feedback', ''),
                'student_img_path': it.get('student_img_path', '')
            }

    results = await asyncio.gather(*(grade_one(it) for it in items))
    results.sort(key=lambda x: x['sample_id'])

    truth = [r['human'] for r in results]
    predicted = [r['ai'] for r in results]
    exact_matches = sum(1 for r in results if r['diff'] == 0.0)
    total = len(results)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted)

    print("\n" + "=" * 50)
    print(f"Q4 Regrade with Visual Answer Key Results:")
    print(f"Exact Matches: {exact_matches}/{total} ({exact_matches/total*100:.2f}%)")
    print(f"MAE: {mae:.4f}")
    print(f"QWK: {qwk:.4f}")
    print("=" * 50)

    # Discrepancies list
    mismatches = [r for r in results if r['diff'] != 0.0]
    print(f"\nRemaining Mismatches ({len(mismatches)}):")
    for m in mismatches:
        print(f" - {m['sample_id']}: Human={m['human']:.2f}, AI={m['ai']:.2f}, diff={m['diff']:+.2f}")

    out_file = ROOT / 'public/q4_regrade_visual_key_results.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({
            'exact_matches': exact_matches,
            'total': total,
            'match_rate': round(exact_matches / total * 100, 2),
            'mae': round(mae, 4),
            'qwk': round(qwk, 4),
            'results': results,
            'mismatches': mismatches
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSaved results to {out_file}")

if __name__ == '__main__':
    asyncio.run(main())
