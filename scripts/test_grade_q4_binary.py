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

RUBRIC_Q4_BINARY = [
    {
        "name": "ความถูกต้องของโครงสร้าง Binary Search Tree (BST)",
        "score": 1.0,
        "description": (
            "ประเมินภาพวาด Binary Search Tree (BST) จากข้อมูล: 9 16 10 76 5 13 58 92 11 15 80 99\n\n"
            "ให้คะแนนเป็น **1 หรือ 0 เท่านั้น** ไม่มีคะแนนกึ่งกลาง\n\n"
            "- **1 คะแนน**: วาด BST ถูกต้องครบถ้วน ครบ 12 โหนด และทุกโหนดเป็นไปตามหลัก BST "
            "(ค่าลูกซ้าย < แม่ < ค่าลูกขวา) อย่างสมบูรณ์ ยอมรับกริดเส้นประกอบหรือวงกลมเพิ่มเติม "
            "ขอเพียงตัวเลขทุกโหนดถูกต้องและเชื่อมโยงถูกทิศทางครบทุกโหนด\n\n"
            "- **0 คะแนน**: ทุกกรณีที่ไม่ผ่านเกณฑ์ข้างต้น ได้แก่:\n"
            "  * วาดไม่ครบ / วาดไม่เสร็จ / มีวงกลมว่างเปล่าที่ยังไม่ได้ใส่ค่า\n"
            "  * วางโหนดผิดตำแหน่ง ผิดหลัก BST แม้เพียงโหนดเดียว\n"
            "  * ไม่มีคำตอบ หรือวาดมั่ว\n\n"
            "**ห้ามให้คะแนน 0.25, 0.5, 0.75 หรือทศนิยมอื่น — ให้ได้แค่ 1 หรือ 0 เท่านั้น**"
        )
    }
]


def load_upright_image_bytes(img_path: str, max_side: int = 1200) -> bytes:
    img = Image.open(img_path)
    if img.height > img.width:
        img = img.rotate(-90, expand=True)
    # Resize to reduce payload size
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
    print(f"=== Q4 Binary Rubric Test (0 or 1 only) — {len(items)} students ===")
    print(f"Model: {OPENAI_MODEL}  Prompt: {PROMPT_VERSION}\n")

    results = []
    exact = 0
    total = len(items)

    for item in items:
        sid = item['sample_id']
        human_raw = item['human_score']
        # Round: 0.25 -> 0, anything < 1 -> 0, 1 -> 1
        human_binary = 1.0 if human_raw >= 1.0 else 0.0

        img_bytes = load_upright_image_bytes(item['student_img_path'])
        result = await score_with_openai(
            question_text=q['question_text'],
            answer_text=item['student_answer'] or '',
            max_score=1.0,
            rubrics=RUBRIC_Q4_BINARY,
            image_bytes_list=[img_bytes],
            image_mime_list=["image/jpeg"],
        )

        ai_raw = result.get('total_score', 0.0)
        ai_binary = 1.0 if ai_raw >= 0.5 else 0.0

        match = "✓" if ai_binary == human_binary else "✗"
        if ai_binary == human_binary:
            exact += 1

        results.append({
            'sid': sid,
            'human_raw': human_raw,
            'human_binary': human_binary,
            'ai_raw': ai_raw,
            'ai_binary': ai_binary,
            'match': match,
        })

        print(f"{match} {sid}  human={human_binary:.0f} (raw={human_raw})  ai={ai_binary:.0f} (raw={ai_raw})")

    print(f"\n{'='*55}")
    print(f"Exact Match (Binary): {exact}/{total} = {exact/total*100:.2f}%")

    # Mismatches
    mismatches = [r for r in results if r['match'] == '✗']
    if mismatches:
        print(f"\nMismatches ({len(mismatches)}):")
        for r in mismatches:
            print(f"  {r['sid']}: human={r['human_binary']:.0f} vs ai={r['ai_binary']:.0f}  (human_raw={r['human_raw']})")
    else:
        print("\n🎉 Perfect score — no mismatches!")

    # QWK
    human_scores = [r['human_binary'] for r in results]
    ai_scores = [r['ai_binary'] for r in results]
    try:
        qwk = calculate_qwk(human_scores, ai_scores)
        print(f"QWK: {qwk:.4f}")
    except Exception as e:
        print(f"QWK error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
