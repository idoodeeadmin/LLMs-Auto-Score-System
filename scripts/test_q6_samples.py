import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / '.env')
from server.services.openai_grading import score_with_openai

Q6_RUBRIC_NAME = 'ความถูกต้องของการแปลง General Tree เป็น Binary Tree (Left-Child Right-Sibling)'
Q6_RUBRIC_DESC = (
    'ประเมินตามโครงสร้างและความถูกต้องของการแปลง General Tree เป็น Binary Tree ตามหลักการ Left-Child Right-Sibling (LCRS) จากโจทย์ 10 โหนด (1 ถึง 10) ดังนี้:\n\n'
    '- ได้ 1.00 คะแนน: แปลงโครงสร้าง Binary Tree ได้ถูกต้องสมบูรณ์ครบทั้ง 10 โหนด ตามหลัก LCRS:\n'
    '  * Root คือ 1 โดยมีกิ่งซ้าย (Left Child) เป็น 2 และกิ่งขวาว่าง (ไม่มี sibling)\n'
    '  * โหนด 2 มีกิ่งซ้ายเป็น 5 (ลูกคนแรก) และกิ่งขวาเป็น 3 (พี่น้องถัดไป)\n'
    '  * ใต้กิ่ง 5: มีกิ่งขวาเป็น 6 -> โหนด 6 มีกิ่งขวาเป็น 7 (ทั้ง 5, 6, 7 ไม่มีกิ่งซ้าย)\n'
    '  * โหนด 3 ไม่มีกิ่งซ้าย และมีกิ่งขวาเป็น 4 (พี่น้องถัดไป)\n'
    '  * โหนด 4 มีกิ่งซ้ายเป็น 8 (ลูกคนแรก) และไม่มีกิ่งขวา\n'
    '  * ใต้กิ่ง 8: มีกิ่งขวาเป็น 9 -> โหนด 9 มีกิ่งขวาเป็น 10 (ทั้ง 8, 9, 10 ไม่มีกิ่งซ้าย)\n'
    '  (อนุโลมความสวยงาม ความยาว หรือมุมเอียงของกิ่ง หากความสัมพันธ์กิ่งซ้าย/ขวาสื่อสารได้ถูกต้องครบถ้วน)\n\n'
    '- ได้ 0.00 คะแนน: โครงสร้างไม่ถูกต้อง มีข้อผิดพลาดในตำแหน่งกิ่ง ผิดหลักการ Left-Child Right-Sibling (LCRS) หรือไม่วาดคำตอบ:\n'
    '  * วางโหนด 3 เป็นกิ่งขวาของโหนด 1 โดยตรง (โหนด 1 ไม่มีพี่น้อง ห้ามมีกิ่งขวา โหนด 3 ต้องเป็นกิ่งขวาของ 2)\n'
    '  * วางโหนด 4 หรือ 3 เป็นกิ่งซ้ายของ 2 หรือนำ 4 ไปต่อกับ 1 โดยตรง\n'
    '  * วาดเป็นเส้นตรงซิกแซกเรียงเดี่ยว หรือเขียนเฉพาะตัวเลขเรียงกันโดยไม่วาดโครงสร้างต้นไม้\n'
    '  * ไม่วาดคำตอบ หรือระบุว่าไม่สามารถแปลงได้\n'
    '  * โครงสร้างแตกกิ่งไม่เป็นไปตามความสัมพันธ์แบบ Left-Child Right-Sibling\n\n'
    '(ระดับคะแนนที่ให้ได้คือ 1.00 หรือ 0.00 คะแนนเท่านั้น ห้ามให้คะแนนเป็นเศษทศนิยมอื่น ต้องระบุ teacher_feedback แจกแจงเหตุผลและจุดถูก/ผิดตามเกณฑ์ LCRS สำหรับผู้สอนอย่างละเอียด และระบุ student_feedback เป็นคำแนะนำพัฒนาการเรียนรู้สำหรับนักเรียน)'
)

Q6_RUBRICS = [{'name': Q6_RUBRIC_NAME, 'score': 1.0, 'description': Q6_RUBRIC_DESC}]
Q6_QUESTION_TEXT = 'จงแปลง tree ต่อไปนี้ให้เป็น Binary Tree (1 คะแนน)\nข้อมูล General Tree: โหนด 1 เป็น Root มีลูก 3 ตัวคือ 2, 3, 4 เรียงจากซ้ายไปขวา; โหนด 2 มีลูก 3 ตัวคือ 5, 6, 7; โหนด 3 ไม่มีลูก (Leaf); โหนด 4 มีลูก 3 ตัวคือ 8, 9, 10'
Q6_ANSWER_KEY = (
    'เฉลยโครงสร้าง Binary Tree ตามหลักการ Left-Child Right-Sibling (LCRS):\n'
    '- 1 (Root): กิ่งซ้ายคือ 2, กิ่งขวาว่าง (null)\n'
    '- 2: กิ่งซ้ายคือ 5, กิ่งขวาคือ 3\n'
    '- 5: กิ่งซ้ายว่าง, กิ่งขวาคือ 6\n'
    '- 6: กิ่งซ้ายว่าง, กิ่งขวาคือ 7\n'
    '- 7: เป็น Leaf (กิ่งซ้ายว่าง, กิ่งขวาว่าง)\n'
    '- 3: กิ่งซ้ายว่าง, กิ่งขวาคือ 4\n'
    '- 4: กิ่งซ้ายคือ 8, กิ่งขวาว่าง\n'
    '- 8: กิ่งซ้ายว่าง, กิ่งขวาคือ 9\n'
    '- 9: กิ่งซ้ายว่าง, กิ่งขวาคือ 10\n'
    '- 10: เป็น Leaf (กิ่งซ้ายว่าง, กิ่งขวาว่าง)'
)

KEY_IMG_PATH = ROOT / 'public' / 'answer-keys' / 'q6-lcrs-binary-tree-answer-key.png'
key_img_bytes = KEY_IMG_PATH.read_bytes()

async def test_samples():
    test_cases = [
        (2, 1.0),   # Student 2: Human gave 1.0
        (12, 0.0),  # Student 12: Human gave 0.0 (misconception: 3 right of 1)
        (21, 1.0),  # Student 21: Human gave 1.0 (blue ink, correct)
        (24, 0.0),  # Student 24: Human gave 0.0 (text: child > 3)
    ]
    img_dir = ROOT / 'ชุดข้อสอบใหม่' / 'photo_clean_ชุดที่3'
    for idx, expected in test_cases:
        img_p = img_dir / f'LINE_ALBUM_Photo2.2_260918_{idx}.jpg'
        res = await score_with_openai(
            question_text=Q6_QUESTION_TEXT,
            answer_text='',
            max_score=1.0,
            answer_key=Q6_ANSWER_KEY,
            rubrics=Q6_RUBRICS,
            image_bytes_list=[img_p.read_bytes()],
            image_mime_list=['image/jpeg'],
            answer_key_image_bytes_list=[key_img_bytes],
            answer_key_image_mime_list=['image/png'],
            strict_rubric_enforcement=True,
        )
        ai_score = res.get('score')
        match = (float(ai_score) == float(expected))
        print(f"Student {idx:2d}: Human={expected:.2f} | AI={float(ai_score):.2f} | Match={'MATCH 🟢' if match else 'DIFF 🟠'}")
        print("  Teacher FB:", str(res.get('teacher_feedback'))[:150], "...")
        print("  Student FB:", str(res.get('student_feedback'))[:150], "...")
        print()

if __name__ == '__main__':
    asyncio.run(test_samples())
