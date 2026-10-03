import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
sys.stdout.reconfigure(encoding="utf-8")

from server.services.openai_grading import score_with_openai, OPENAI_MODEL

Q4_QUESTION_TEXT = (
    "จากข้อมูลต่อไปนี้จงนำไปสร้างเป็น Binary search tree (1 คะแนน)\n"
    "9 16 10 76 5 13 58 92 11 15 80 99"
)

Q4_ANSWER_KEY = (
    "เฉลยโครงสร้าง Binary Search Tree (BST) ที่ถูกต้องสมบูรณ์:\n"
    "- ลำดับการนำเข้าข้อมูลคือ: 9 16 10 76 5 13 58 92 11 15 80 99\n"
    "- Root ต้องเป็น 9 เท่านั้น (เพราะ 9 เป็นข้อมูลตัวแรกที่ถูก insert)\n"
    "- กิ่งซ้ายของ 9 คือ 5, กิ่งขวาของ 9 คือ 16\n"
    "- ใต้ 16 มี 10 (ซ้าย) และ 76 (ขวา)\n"
    "- ใต้ 10 มี 13 (ขวา)\n"
    "- ใต้ 13 มี 11 (ซ้าย) และ 15 (ขวา)\n"
    "- ใต้ 76 มี 58 (ซ้าย เป็น Leaf) และ 92 (ขวา)\n"
    "- ใต้ 92 มี 80 (ซ้าย) และ 99 (ขวา)\n"
    "- หากโหนดรากไม่ใช่ 9 หรือวางโหนดผิด ให้ 0.00 คะแนนทันที"
)

Q4_RUBRIC = [
    {
        "name": "ความถูกต้องของ Binary Search Tree (BST 12 โหนด)",
        "score": 1.0,
        "description": (
            "ประเมินภาพวาด Binary Search Tree จากข้อมูล: 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99 (เลือกได้เฉพาะ 1.0 หรือ 0.0 คะแนนเท่านั้น):\n"
            "• โหนดแรก 9 ต้องเป็นราก (Root) เท่านั้น หากโหนดรากไม่ใช่ 9 (เช่น เอา 16 หรือตัวอื่นไปเป็นราก) ให้ 0.00 คะแนนทันที\n"
            "• เส้นเชื่อมทุกกิ่งต้องถูกต้องตามหลัก BST\n"
            "• 1.0 คะแนน: โครงสร้างและเส้นเชื่อมถูกต้องครบถ้วนทั้ง 12 โหนด\n"
            "• 0.0 คะแนน: วางโหนดผิดตำแหน่ง, โหนดรากผิด, เส้นเชื่อมต่อผิดกิ่ง, หรือไม่วาดคำตอบ"
        ),
        "allowed_scores": [0.0, 1.0]
    }
]

async def run_single_test():
    img_path = ROOT / "public/screenshots/q4_audit/clean_DS-107.jpg"
    print(f"Testing DS-107 image: {img_path}")
    print(f"Model: {OPENAI_MODEL}")
    
    with open(img_path, "rb") as f:
        img_bytes = f.read()

    print("\n--- Sending request to OpenAI API with new Master Prompt ---")
    result = await score_with_openai(
        question_text=Q4_QUESTION_TEXT,
        answer_text="",
        max_score=1.0,
        answer_key=Q4_ANSWER_KEY,
        rubrics=Q4_RUBRIC,
        image_bytes_list=[img_bytes],
        image_mime_list=["image/jpeg"],
        allowed_scores=[0.0, 1.0],
        strict_rubric_enforcement=True
    )

    print("\n================== RESULT ==================")
    print(f"Score: {result.get('score')} / 1.0 (Human Score: 0.0)")
    print(f"Confidence: {result.get('confidence')}")
    print(f"Teacher Feedback:\n{result.get('teacher_feedback')}")
    print(f"\nStudent Feedback:\n{result.get('student_feedback')}")
    print(f"\nTranscription:\n{result.get('transcription')}")
    print("============================================")

if __name__ == "__main__":
    asyncio.run(run_single_test())
