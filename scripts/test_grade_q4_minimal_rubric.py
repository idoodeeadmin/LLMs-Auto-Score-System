import os
import sys
import json
import asyncio
from io import BytesIO
from pathlib import Path
from datetime import datetime
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

from scripts.run_dataset_benchmark import (
    load_dataset,
    calculate_qwk,
    calculate_mae,
    calculate_confusion_matrix,
    get_agreement_interpretation,
    EXAM_QUESTIONS,
)
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

# Minimal / Non-spoon-fed Rubric: AI must compute and verify the BST structure on its own
MINIMAL_RUBRIC_Q4 = [
    {
        "name": "ความถูกต้องของโครงสร้าง Binary Search Tree (BST)",
        "score": 1.0,
        "description": (
            "เกณฑ์การประเมินภาพวาด Binary Search Tree (BST) จากลำดับข้อมูลที่กำหนดในโจทย์ (คะแนนเต็ม 1.00):\n\n"
            "- 1.00 คะแนน: วาดโครงสร้าง Binary Search Tree ได้ถูกต้องสมบูรณ์ครบทั้ง 12 โหนดตามลำดับข้อมูลที่กำหนด โดยโหนดทุกตำแหน่งต้องสอดคล้องกับคุณสมบัติของ BST (Left < Parent < Right) อย่างถูกต้องทั้งหมด (ยอมรับหากมีเส้นโครงร่าง Full Tree หรือวงกลมกริดว่างเปล่าประกอบ)\n\n"
            "- 0.50 คะแนน: โครงสร้างส่วนใหญ่ถูกต้องตามลำดับและคุณสมบัติ BST แต่มีตำแหน่งโหนดสลับฝั่งซ้าย/ขวาผิด 1 จุด หรือเชื่อมโยงคลาดเคลื่อน 1 จุด\n\n"
            "- 0.25 คะแนน: โครงสร้างถูกต้องเพียงบางส่วน แต่วาดไม่เสร็จ มีวงกลมว่างเปล่าที่ไม่ได้เติมตัวเลข หรือมีข้อผิดพลาดหลายจุด\n\n"
            "- 0.00 คะแนน: ผิดหลักการ BST ขั้นพื้นฐานอย่างร้ายแรง (เช่น โหนดที่มีค่ามากกว่ารากกลับนำไปไว้กิ่งซ้าย, กิ่งแตกเกิน 2 กิ่งไม่ใช่ Binary Tree, มีโหนดตกหล่นขาดหาย, วาดมั่ว หรือไม่วาดคำตอบ)\n\n"
            "**ระดับคะแนนที่ให้ได้คือ 1.00, 0.50, 0.25 หรือ 0.00 คะแนนเท่านั้น ห้ามให้คะแนนเป็นเศษทศนิยมอื่น**"
        )
    }
]

# Minimal Answer Key without spelling out every node: AI must deduce the tree structure
MINIMAL_ANSWER_KEY_Q4 = (
    "Binary Search Tree ที่สร้างจากการแทรกข้อมูลตามลำดับ 9 16 10 76 5 13 58 92 11 15 80 99 "
    "โดยต้องรักษาคุณสมบัติของ Binary Search Tree ทุกโหนด (Left Subtree < Root < Right Subtree)"
)

def load_upright_image_bytes(img_path: str) -> bytes:
    img = Image.open(img_path)
    if img.height > img.width:
        img = img.rotate(90, expand=True)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=95)
    return buf.getvalue()

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 4]
    assert len(items) == 34 and all(x['answer_type'] == 'img' for x in items)

    q = EXAM_QUESTIONS[4]
    rubrics = MINIMAL_RUBRIC_Q4
    answer_key = MINIMAL_ANSWER_KEY_Q4

    print(f"=== Grading Question 4 with MINIMAL RUBRIC (AI Thinks for Itself) ===")
    print(f"Total students: {len(items)}")
    print(f"Model: {OPENAI_MODEL} | Prompt Version: {PROMPT_VERSION}")
    print(f"Topic: {q['topic']} | Max Score: {q['max_score']}")
    print("Rubric does NOT contain explicit node layout — AI must independently compute BST.")
    print("-" * 65)

    results = []
    sem = asyncio.Semaphore(4)

    async def grade_one(item):
        async with sem:
            img_bytes = load_upright_image_bytes(item['student_img_path'])
            res = await score_with_openai(
                question_text=q['question_text'],
                answer_text="",
                max_score=q['max_score'],
                answer_key=answer_key,
                rubrics=rubrics,
                image_bytes_list=[img_bytes],
                image_mime_list=["image/jpeg"],
            )
            h_score = item['human_score']
            ai_score = res.get('score', 0.0)
            conf = res.get('confidence', 'unknown')
            diff = round(ai_score - h_score, 2)
            entry = {
                'sample_id': item['sample_id'],
                'row': item['row'],
                'human_score': h_score,
                'ai_score': ai_score,
                'diff': diff,
                'exact': ai_score == h_score,
                'confidence': conf,
                'feedback': res.get('feedback', ''),
                'transcription': res.get('transcription', ''),
            }
            results.append(entry)
            status = "MATCH" if ai_score == h_score else f"DIFF ({diff:+0.2f})"
            print(f"[{entry['sample_id']}] Human={h_score:0.2f} | AI={ai_score:0.2f} | Conf={conf:6s} | {status}")
            return entry

    tasks = [grade_one(item) for item in items]
    await asyncio.gather(*tasks)

    results.sort(key=lambda x: x['row'])
    truth = [r['human_score'] for r in results]
    predicted = [r['ai_score'] for r in results]
    exact_count = sum(r['exact'] for r in results)
    tol_025_count = sum(abs(r['diff']) <= 0.25 for r in results)
    tol_050_count = sum(abs(r['diff']) <= 0.50 for r in results)
    mae = calculate_mae(truth, predicted)
    qwk = calculate_qwk(truth, predicted, step=0.25, max_score=1.0)

    print("\n" + "=" * 65)
    print("=== SUMMARY RESULTS (MINIMAL RUBRIC / AI THINKS FOR ITSELF) ===")
    print(f"Total Students:        {len(results)}")
    print(f"Exact Match:           {exact_count}/34 ({exact_count/34*100:.2f}%)")
    print(f"Tolerance <= 0.25:     {tol_025_count}/34 ({tol_025_count/34*100:.2f}%)")
    print(f"Tolerance <= 0.50:     {tol_050_count}/34 ({tol_050_count/34*100:.2f}%)")
    print(f"MAE (Mean Abs Error):  {mae:.4f}")
    print(f"QWK (step=0.25):       {qwk:.4f} ({get_agreement_interpretation(qwk)['level_th']})")

    # Save artifact
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    folder = ROOT / 'artifacts' / f'q4-minimal-rubric-eval-{timestamp}'
    folder.mkdir(parents=True, exist_ok=True)
    out_file = folder / 'q4_minimal_results.json'
    out_file.write_text(json.dumps({'summary': {
        'exact_count': exact_count, 'exact_pct': exact_count/34*100,
        'tolerance_0_25_pct': tol_025_count/34*100, 'tolerance_0_50_pct': tol_050_count/34*100,
        'mae': mae, 'qwk': qwk
    }, 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Saved results to: {out_file}")

if __name__ == '__main__':
    asyncio.run(main())
