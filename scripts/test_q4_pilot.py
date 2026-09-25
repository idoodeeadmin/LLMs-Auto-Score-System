import os
import sys
import asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

from scripts.run_dataset_benchmark import load_dataset, EXAM_QUESTIONS
from server.services.openai_grading import score_with_openai, OPENAI_MODEL

RUBRIC_Q4_TEST = [
    {
        "name": "ความถูกต้องของโครงสร้าง Binary Search Tree (BST)",
        "score": 1.0,
        "description": (
            "เกณฑ์การประเมินภาพวาด Binary Search Tree (BST) จากข้อมูล: 9 16 10 76 5 13 58 92 11 15 80 99 (คะแนนเต็ม 1.00):\n\n"
            "- 1.00 คะแนน: สร้าง Binary Search Tree ได้ถูกต้องสมบูรณ์ครบทั้ง 12 โหนด ยึดหลัก Left < Parent < Right ถูกต้องทุกจุด:\n"
            "  * Root คือ 9 (ซ้าย: 5)\n"
            "  * ขวาของ 9 คือ 16\n"
            "    - ซ้ายของ 16 คือ 10 -> ขวาของ 10 คือ 13 -> ซ้ายของ 13 คือ 11, ขวาของ 13 คือ 15\n"
            "    - ขวาของ 16 คือ 76 -> ซ้ายของ 76 คือ 58, ขวาของ 76 คือ 92 -> ซ้ายของ 92 คือ 80, ขวาของ 92 คือ 99\n"
            "  (ยอมรับหากมีเส้นร่างกริด Full Tree หรือวงกลมโครงเปล่าประกอบ)\n\n"
            "- 0.50 คะแนน: โครงสร้างหลักเกือบถูกต้อง แต่มีโหนดสลับฝั่งซ้าย/ขวาผิด 1 จุด หรือวางตำแหน่งคลาดเคลื่อนเล็กน้อย 1 จุด\n\n"
            "- 0.25 คะแนน: แสดงโครงสร้าง BST ได้ถูกต้องเพียงบางส่วน (เช่น ซีกขวาถูกบางส่วน) แต่โครงสร้างโดยรวมผิดหลายจุด หรือวาดไม่เสร็จ มีโหนดว่างเปล่าที่ไม่ได้เติมตัวเลข\n\n"
            "- 0.00 คะแนน: ผิดหลักการ BST ชัดเจน (เช่น วาง 10 ไปไว้กิ่งซ้ายของ 9 ซึ่ง 10 > 9 ผิดกฎ BST, ต้นไม้ไม่ใช่ Binary Tree มีกิ่งแตกเกิน 2 กิ่ง, โหนดหายไปหลายตัว, หรือวาดสุ่มโดยไม่ตรงกับข้อมูล)\n\n"
            "**ระดับคะแนนที่ให้ได้คือ 1.00, 0.50, 0.25 หรือ 0.00 คะแนนเท่านั้น ห้ามให้เศษทศนิยมอื่น**"
        )
    }
]

async def test_few():
    items = [x for x in load_dataset() if x['question_no'] == 4]
    test_ids = ['DS-103', 'DS-104', 'DS-105', 'DS-106', 'DS-121']
    test_items = [x for x in items if x['sample_id'] in test_ids]
    
    q = EXAM_QUESTIONS[4]
    
    print(f"Testing {len(test_items)} samples with model {OPENAI_MODEL}...")
    for it in test_items:
        img_path = it['student_img_path']
        with open(img_path, 'rb') as f:
            img_bytes = f.read()
            
        res = await score_with_openai(
            question_text=q['question_text'],
            answer_text="",
            max_score=q['max_score'],
            answer_key=q['answer_key'],
            rubrics=RUBRIC_Q4_TEST,
            image_bytes_list=[img_bytes],
            image_mime_list=["image/jpeg"]
        )
        print("=" * 60)
        print(f"[{it['sample_id']}] Human: {it['human_score']:.2f} | AI: {res.get('score')} | Conf: {res.get('confidence')}")
        print(f"Feedback: {res.get('feedback')}")
        print(f"Transcription: {res.get('transcription')}")

if __name__ == '__main__':
    asyncio.run(test_few())
