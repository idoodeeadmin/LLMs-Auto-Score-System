import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from server.services.openai_grading import score_with_openai

Q5_RUBRIC_NAME = "การแปลง Infix Expression เป็น Prefix และ Postfix Expression"
Q5_RUBRIC_DESC = (
    "โจทย์ให้แสดงวิธีการแปลง Infix Expression: A + (B * (C - (D / (F * 2)))) เป็น Prefix และ Postfix ด้วยมือ (คะแนนเต็ม 1.00 คะแนน)\n"
    "ประเมินแยก 2 ส่วนตามภาพเฉลยแม่แบบอย่างเคร่งครัด:\n\n"
    "ส่วนที่ 1: การหา Prefix Expression (คะแนนเต็ม 0.50 คะแนน)\n"
    "• ได้ 0.50 คะแนน: แสดงขั้นตอนถูกต้องและได้คำตอบสุดท้ายคือ + A * B - C / D * F 2 (หรือเขียนติดกัน +A*B-C/D*F2)\n"
    "• ได้ 0.00 คะแนน: คำตอบผิดหลักการทั้งหมด ไม่แสดงวิธีทำ หรือไม่ได้ทำ\n\n"
    "ส่วนที่ 2: การหา Postfix Expression (คะแนนเต็ม 0.50 คะแนน)\n"
    "• ได้ 0.50 คะแนน: แสดงขั้นตอนถูกต้องและได้คำตอบสุดท้ายคือ A B C D F 2 * / - * + (หรือเขียนติดกัน ABCDF2*/-*+)\n"
    "• ได้ 0.00 คะแนน: คำตอบผิดหลักการทั้งหมด ไม่แสดงวิธีทำ หรือไม่ได้ทำ\n\n"
    "(คะแนนรวมคือผลบวกของส่วนที่ 1 และ 2: 1.00, 0.50 หรือ 0.00 คะแนน โดยมีกรณีพิเศษ 0.25 เฉพาะผู้ที่แสดงวิธีทำมาถูกทางเกือบหมด)"
)

Q5_RUBRICS = [
    {
        "name": Q5_RUBRIC_NAME,
        "score": 1.0,
        "description": Q5_RUBRIC_DESC,
    }
]

Q5_QUESTION_TEXT = (
    "จงแสดงวิธีการหา Infix Expression ต่อไปนี้ให้เป็น Prefix Expression และ Postfix Expression ด้วยมือ (1 คะแนน)\n"
    "นิพจน์: A + (B * (C - (D / (F * 2))))"
)

Q5_ANSWER_KEY = (
    "เฉลยวิธีทำและคำตอบมาตรฐานตามภาพแม่แบบ:\n"
    "1. Prefix Expression (0.50 คะแนน): คำตอบสุดท้ายคือ + A * B - C / D * F 2\n"
    "2. Postfix Expression (0.50 คะแนน): คำตอบสุดท้ายคือ A B C D F 2 * / - * +\n"
    "รวมคะแนน: 1.00 (ถูกทั้งสองฝั่ง), 0.50 (ถูกฝั่งเดียว), 0.00 (ผิดทั้งสองฝั่ง)"
)

KEY_IMG_PATH = ROOT / "public" / "answer-keys" / "q5-infix-prefix-postfix-answer-key.png"
key_img_bytes = KEY_IMG_PATH.read_bytes()

DEMO_SAMPLES = [
    {
        "id": "DS-137",
        "file": "LINE_ALBUM_Photo2.1_260918_1.jpg",
        "expected_score": 1.00,
        "note": "ตัวแทนกลุ่มคำตอบสมบูรณ์ (ถูกทั้ง Prefix และ Postfix)"
    },
    {
        "id": "DS-156",
        "file": "LINE_ALBUM_Photo2.1_260918_20.jpg",
        "expected_score": 0.50,
        "note": "ตัวแทนกลุ่มคำตอบถูกฝั่งเดียว (Prefix ถูก แต่ Postfix ผิด)"
    },
    {
        "id": "DS-167",
        "file": "LINE_ALBUM_Photo2.1_260918_31.jpg",
        "expected_score": 0.00,
        "note": "ตัวแทนกลุ่มคำตอบไม่ถูกต้อง (ลอกโจทย์เดิม ไม่มีคำตอบสุดท้าย)"
    }
]

async def main():
    print("================================================================================")
    print("ส่งตรวจคำตอบข้อ 5 ผ่านฟังก์ชันแม่แบบหลัก `score_with_openai()`")
    print(f"ภาพแม่แบบเฉลย: {KEY_IMG_PATH.name} (ขนาด {len(key_img_bytes):,} bytes)")
    print("================================================================================\n")

    for item in DEMO_SAMPLES:
        sample_path = ROOT / "ชุดข้อสอบใหม่" / "photo_clean_ชุดที่2" / item["file"]
        student_img_bytes = sample_path.read_bytes()

        print(f"--------------------------------------------------------------------------------")
        print(f"กำลังส่งตรวจ: {item['id']} ({item['file']})")
        print(f"คำอธิบายกลุ่มตัวอย่าง: {item['note']}")
        print(f"คะแนนของอาจารย์ผู้สอน (Ground Truth): {item['expected_score']:.2f} คะแนน")
        print(f"--------------------------------------------------------------------------------")

        res = await score_with_openai(
            question_text=Q5_QUESTION_TEXT,
            answer_text="",
            max_score=1.0,
            answer_key=Q5_ANSWER_KEY,
            rubrics=Q5_RUBRICS,
            image_bytes_list=[student_img_bytes],
            image_mime_list=["image/jpeg"],
            answer_key_image_bytes_list=[key_img_bytes],
            answer_key_image_mime_list=["image/png"],
            strict_rubric_enforcement=True,
        )

        ai_score = float(res.get("score", 0.0))
        conf = res.get("confidence", "unknown")
        tf = res.get("teacher_feedback", "").strip()
        sf = res.get("student_feedback", "").strip()
        trans = res.get("transcription", "").strip()

        match = (ai_score == item["expected_score"])
        status_text = "MATCH (ตรงกันเป๊ะ!)" if match else f"DIFF ({ai_score - item['expected_score']:+.2f})"

        print(f"-> ผลการประเมินจาก score_with_openai:")
        print(f"   * คะแนน AI: {ai_score:.2f} คะแนน  [{status_text}]")
        print(f"   * ระดับความมั่นใจ: {conf}")
        if trans:
            print(f"   * ข้อความที่อ่านได้จากภาพ (Transcription):\n     {trans}")
        print(f"   * เหตุผลสำหรับผู้สอน (Teacher Feedback):\n     {tf}")
        print(f"   * คำแนะนำสำหรับนักเรียน (Student Feedback):\n     {sf}\n")

if __name__ == "__main__":
    asyncio.run(main())
