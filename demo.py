import asyncio
from dotenv import load_dotenv

load_dotenv()
from server.services.ai_service import score_with_gemini

async def run_demo():
    print("🚀 เริ่มรัน AI Demo Grader (จำลองการตรวจข้อสอบแบบง่ายๆ)...")
    question_text = "จงอธิบายความแตกต่างระหว่าง Stack และ Queue"
    answer_key = "Stack คือ LIFO ส่วน Queue คือ FIFO"
    rubrics = [
        {"name": "อธิบาย Stack", "score": 2.5, "description": "LIFO"},
        {"name": "อธิบาย Queue", "score": 2.5, "description": "FIFO"}
    ]
    student_answer = "Stack เหมือนจานข้าววางซ้อนกันใบสุดท้ายหยิบก่อน ส่วน Queue เหมือนต่อแถวซื้อข้าว ใครมาก่อนได้ก่อน"
    max_score = 5.0

    print(f"\n📝 [โจทย์]: {question_text}")
    print(f"👦 [คำตอบของนักเรียน]: {student_answer}")
    print("\n🤖 กำลังให้ AI คิด... (รอสักครู่)\n")

    result = await score_with_gemini(
        question_text=question_text, answer_text=student_answer,
        max_score=max_score, answer_key=answer_key, rubrics=rubrics
    )

    print("================ ผลการตรวจจาก AI ==================")
    print(f"🎯 คะแนนที่ได้: {result['score']} / {max_score}")
    print(f"💬 Feedback:\n{result['feedback']}")
    print("===================================================")

if __name__ == '__main__':
    asyncio.run(run_demo())
