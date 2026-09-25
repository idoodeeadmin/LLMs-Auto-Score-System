import os
import sys
import asyncio
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

from scripts.run_dataset_benchmark import load_dataset, EXAM_QUESTIONS
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

# mismatches from detailed rubric (88.24% run)
MISMATCH_IDS = {"DS-103", "DS-114", "DS-119", "DS-121"}

RUBRIC_Q4_TRIMMED = [
    {
        "name": "ความถูกต้องของโครงสร้าง Binary Search Tree (BST)",
        "score": 1.0,
        "description": (
            "เกณฑ์การประเมินภาพวาด Binary Search Tree (BST) จากข้อมูล: 9 16 10 76 5 13 58 92 11 15 80 99 (คะแนนเต็ม 1.00):\n\n"
            "- 1.00 คะแนน: วาดโครงสร้าง BST ได้ถูกต้องครบถ้วนทั้ง 12 โหนด ยึดหลัก Left < Parent < Right อย่างถูกต้องสมบูรณ์:\n"
            "  * Root คือ 9 (ลูกซ้ายคือ 5)\n"
            "  * ลูกขวาของ 9 คือ 16\n"
            "    - ลูกซ้ายของ 16 คือ 10 -> ลูกขวาของ 10 คือ 13 -> ลูกซ้ายของ 13 คือ 11, ลูกขวาของ 13 คือ 15\n"
            "    - ลูกขวาของ 16 คือ 76 -> ลูกซ้ายของ 76 คือ 58, ลูกขวาของ 76 คือ 92 -> ลูกซ้ายของ 92 คือ 80, ลูกขวาของ 92 คือ 99\n\n"
            "- 0.50 คะแนน: โครงสร้างส่วนใหญ่ถูกต้องตามคุณสมบัติ BST แต่มีตำแหน่งโหนดสลับฝั่งซ้าย/ขวาผิด 1 จุด หรือใส่ค่าสลับกัน 1 คู่\n\n"
            "- 0.25 คะแนน: โครงสร้างถูกต้องเพียงบางส่วน\n\n"
            "- 0.00 คะแนน: ผิดหลักการ BST หรือไม่มีคำตอบ\n\n"
            "**ระดับคะแนนที่ให้ได้คือ 1.00, 0.50, 0.25 หรือ 0.00 คะแนนเท่านั้น**"
        )
    }
]


def load_upright_image_bytes(img_path: str, max_side: int = 1200) -> bytes:
    img = Image.open(img_path)
    if img.height > img.width:
        img = img.rotate(-90, expand=True)
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()


async def main():
    all_items = [x for x in load_dataset() if x['question_no'] == 4]
    items = [x for x in all_items if x['sample_id'] in MISMATCH_IDS]
    q = EXAM_QUESTIONS[4]

    print(f"=== luna low — Trimmed Rubric — Mismatches — {len(items)} cases ===")
    print(f"Model: {OPENAI_MODEL}  Prompt: {PROMPT_VERSION}\n")

    for item in items:
        sid = item['sample_id']
        human = item['human_score']

        img_bytes = load_upright_image_bytes(item['student_img_path'])
        result = await score_with_openai(
            question_text=q['question_text'],
            answer_text=item['student_answer'] or '',
            max_score=1.0,
            rubrics=RUBRIC_Q4_TRIMMED,
            image_bytes_list=[img_bytes],
            image_mime_list=["image/jpeg"],
        )

        ai = result.get('score', 0.0)
        match = "✓ FIXED" if abs(ai - human) < 0.01 else "✗ still wrong"
        print(f"{match}  {sid}  human={human}  ai={ai}  conf={result.get('confidence','?')}")
        print(f"  Feedback: {result.get('feedback','')[:200]}\n")


if __name__ == '__main__':
    asyncio.run(main())
