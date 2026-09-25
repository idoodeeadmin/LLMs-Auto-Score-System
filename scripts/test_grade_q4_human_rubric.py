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

from scripts.run_dataset_benchmark import load_dataset, calculate_qwk, EXAM_QUESTIONS
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

# Rubric แบบ "มนุษย์เขียน" — บอกหลักการ ไม่บอกเฉลยตำแหน่ง node
RUBRIC_Q4_HUMAN = [
    {
        "name": "ความถูกต้องของโครงสร้าง Binary Search Tree (BST)",
        "score": 1.0,
        "description": (
            "ประเมินภาพวาด Binary Search Tree ที่นักศึกษาสร้างจากข้อมูลที่กำหนด\n\n"
            "- 1.00 คะแนน: โครงสร้าง BST ถูกต้องสมบูรณ์ ใส่ข้อมูลครบทุกค่า "
            "และทุกโหนดเป็นไปตามคุณสมบัติ BST (ค่าในกิ่งซ้ายน้อยกว่าโหนดแม่ "
            "ค่าในกิ่งขวามากกว่าโหนดแม่) อย่างถูกต้องทุกจุด\n\n"
            "- 0.50 คะแนน: โครงสร้างส่วนใหญ่ถูกต้อง แต่มีจุดผิดพลาดเล็กน้อย "
            "เช่น node บางตัวอยู่ผิดฝั่ง หรือค่าสลับกัน 1-2 จุด\n\n"
            "- 0.25 คะแนน: วาดโครงสร้างได้บางส่วน แต่ยังไม่เสร็จสมบูรณ์ "
            "หรือมีข้อผิดพลาดหลายจุด\n\n"
            "- 0.00 คะแนน: ผิดหลักการ BST อย่างชัดเจน ข้อมูลขาดหายไปมาก "
            "หรือไม่มีคำตอบ\n\n"
            "คะแนนที่ให้ได้: 1.00, 0.50, 0.25 หรือ 0.00 เท่านั้น"
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
    items = [x for x in load_dataset() if x['question_no'] == 4]
    assert len(items) == 34

    q = EXAM_QUESTIONS[4]
    print(f"=== Q4 Human-style Rubric Test — {len(items)} students ===")
    print(f"Model: {OPENAI_MODEL}  Prompt: {PROMPT_VERSION}\n")

    results = []
    exact = 0
    total = len(items)

    for item in items:
        sid = item['sample_id']
        human = item['human_score']

        img_bytes = load_upright_image_bytes(item['student_img_path'])
        result = await score_with_openai(
            question_text=q['question_text'],
            answer_text=item['student_answer'] or '',
            max_score=1.0,
            rubrics=RUBRIC_Q4_HUMAN,
            image_bytes_list=[img_bytes],
            image_mime_list=["image/jpeg"],
        )

        ai = result.get('score', 0.0)
        match = "✓" if abs(ai - human) < 0.01 else "✗"
        if abs(ai - human) < 0.01:
            exact += 1

        results.append({'sid': sid, 'human': human, 'ai': ai, 'match': match})
        print(f"{match} {sid}  human={human}  ai={ai}  conf={result.get('confidence','?')}")

    print(f"\n{'='*55}")
    print(f"Exact Match: {exact}/{total} = {exact/total*100:.2f}%")

    mismatches = [r for r in results if r['match'] == '✗']
    if mismatches:
        print(f"\nMismatches ({len(mismatches)}):")
        for r in mismatches:
            print(f"  {r['sid']}: human={r['human']} vs ai={r['ai']}")

    human_scores = [r['human'] for r in results]
    ai_scores = [r['ai'] for r in results]
    try:
        qwk = calculate_qwk(human_scores, ai_scores)
        print(f"QWK: {qwk:.4f}")
    except Exception as e:
        print(f"QWK error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
