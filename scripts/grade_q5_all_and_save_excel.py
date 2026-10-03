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

import openpyxl
from server.services.gemini_grading import score_with_gemini

VERIFIED_HUMAN_SCORES = {
    1: 1.0,   # DS-137
    2: 1.0,   # DS-138
    3: 1.0,   # DS-139
    4: 1.0,   # DS-140
    5: 1.0,   # DS-141
    6: 1.0,   # DS-142
    7: 1.0,   # DS-143
    8: 1.0,   # DS-144
    9: 1.0,   # DS-145
    10: 1.0,  # DS-146
    11: 1.0,  # DS-147
    12: 1.0,  # DS-148
    13: 1.0,  # DS-149
    14: 1.0,  # DS-150
    15: 1.0,  # DS-151
    16: 1.0,  # DS-152
    17: 1.0,  # DS-153
    18: 0.5,  # DS-154
    19: 0.5,  # DS-155
    20: 0.5,  # DS-156
    21: 0.5,  # DS-157
    22: 0.5,  # DS-158
    23: 1.0,  # DS-159
    24: 1.0,  # DS-160
    25: 1.0,  # DS-161
    26: 0.5,  # DS-162
    27: 0.5,  # DS-163
    28: 0.5,  # DS-164
    29: 0.5,  # DS-165
    30: 0.5,  # DS-166
    31: 0.0,  # DS-167
    32: 1.0,  # DS-168
    33: 0.5,  # DS-169
    34: 1.0,  # DS-170
}

Q5_RUBRIC_NAME = "การแปลง Infix Expression เป็น Prefix และ Postfix Expression"
Q5_RUBRIC_DESC = (
    "โจทย์ให้แสดงวิธีการแปลง Infix Expression: A + (B * (C - (D / (F * 2)))) เป็น Prefix และ Postfix ด้วยมือ (คะแนนเต็ม 1.00 คะแนน)\n"
    "ประเมินแยก 2 ส่วนตามภาพเฉลยแม่แบบอย่างเคร่งครัด:\n\n"
    "ส่วนที่ 1: การหา Prefix Expression (คะแนนเต็ม 0.50 คะแนน)\n"
    "• ได้ 0.50 คะแนน: แสดงขั้นตอนถูกต้องและได้คำตอบสุดท้ายคือ + A * B - C / D * F 2 (หรือเขียนติดกัน +A*B-C/D*F2)\n"
    "  (ข้อแนะนำลายมือ: สัญลักษณ์คูณ '*' อาจเขียนเป็นดอกจัน กากบาท หรือจุด ในตำแหน่งเชื่อม B เช่น '+ A * B - C / D * F 2' ให้อ่านเป็น '*' ตามบริบทคณิตศาสตร์, หากมีข้อความขีดฆ่าให้ตัดทิ้งและพิจารณาคำตอบที่ไม่ถูกขีดฆ่า)\n"
    "• ได้ 0.00 คะแนน: คำตอบผิดหลักการทั้งหมด ไม่แสดงวิธีทำ หรือไม่ได้ทำ\n\n"
    "ส่วนที่ 2: การหา Postfix Expression (คะแนนเต็ม 0.50 คะแนน)\n"
    "• ได้ 0.50 คะแนน: แสดงขั้นตอนถูกต้องและได้คำตอบสุดท้ายคือ A B C D F 2 * / - * + (หรือเขียนติดกัน ABCDF2*/-*+)\n"
    "• ได้ 0.00 คะแนน: คำตอบผิดหลักการทั้งหมด ไม่แสดงวิธีทำ หรือไม่ได้ทำ\n\n"
    "(คะแนนรวมคือผลบวกของส่วนที่ 1 และ 2: 1.00, 0.50 หรือ 0.00 คะแนน)"
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
    "1. Prefix Expression (0.50 คะแนน): คำตอบสุดท้ายคือ + A * B - C / D * F 2 (เขียนติดกัน +A*B-C/D*F2)\n"
    "2. Postfix Expression (0.50 คะแนน): คำตอบสุดท้ายคือ A B C D F 2 * / - * + (เขียนติดกัน ABCDF2*/-*+)\n"
    "รวมคะแนน: 1.00 (ถูกทั้งสองฝั่ง), 0.50 (ถูกฝั่งเดียว), 0.00 (ผิดทั้งสองฝั่ง)"
)

KEY_IMG_PATH = ROOT / "public" / "answer-keys" / "q5-infix-prefix-postfix-answer-key.png"
key_img_bytes = KEY_IMG_PATH.read_bytes() if KEY_IMG_PATH.exists() else None

async def main():
    excel_path = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"
    wb = openpyxl.load_workbook(excel_path)
    for ws in wb.worksheets:
        ws._images = []
    
    # 1. Update Exam_Rubrics Row 11
    ws_rubrics = wb["Exam_Rubrics"]
    ws_rubrics.cell(11, 4, Q5_RUBRIC_NAME)
    ws_rubrics.cell(11, 5, 1.0)
    ws_rubrics.cell(11, 6, Q5_RUBRIC_DESC)
    print("Updated Exam_Rubrics Row 11 with Infix/Prefix/Postfix rubric.")
    
    ws_dataset = wb["ชุดข้อสอบ_dataset"]
    rows = list(range(142, 176)) # 34 rows for Q5: 142 to 175
    assert len(rows) == 34
    
    clean_dir = ROOT / "ชุดข้อสอบใหม่" / "photo_clean_ชุดที่2"
    
    # Pre-sync verified human scores into Excel Column 7
    for r in rows:
        std_idx = r - 141
        verified_score = VERIFIED_HUMAN_SCORES[std_idx]
        ws_dataset.cell(r, 7, verified_score)
    wb.save(excel_path)
    print("Verified human ground truth scores synced to Excel Column 7.")
    
    print(f"Total students to grade via score_with_openai: {len(rows)} | Key image attached: {bool(key_img_bytes)}")
    
    sem = asyncio.Semaphore(4)
    exact_matches = 0
    total_diff = 0.0

    async def grade_one(r):
        nonlocal exact_matches, total_diff
        std_idx = r - 141
        img_name = f"LINE_ALBUM_Photo2.1_260918_{std_idx}.jpg"
        img_path = clean_dir / img_name
        human_score = float(ws_dataset.cell(r, 7).value or 0.0)
        
        async with sem:
            img_bytes = img_path.read_bytes()
            res = await score_with_gemini(
                question_text=Q5_QUESTION_TEXT,
                answer_text="",
                max_score=1.0,
                answer_key=Q5_ANSWER_KEY,
                rubrics=Q5_RUBRICS,
                image_bytes_list=[img_bytes],
                image_mime_list=["image/jpeg"],
                answer_key_image_bytes_list=[key_img_bytes] if key_img_bytes else None,
                answer_key_image_mime_list=["image/png"] if key_img_bytes else None,
                strict_rubric_enforcement=True,
            )
            ai_score = float(res.get("score", 0.0))
                
            conf = res.get("confidence", "high")
            combined_fb = res.get("feedback", "")
            diff = round(ai_score - human_score, 2)
            is_match = (diff == 0.0)
            if is_match:
                exact_matches += 1
            total_diff += abs(diff)
            
            print(f"[{std_idx:02d}/34] Row {r} | Human: {human_score:.2f} | AI: {ai_score:.2f} | {'MATCH' if is_match else f'DIFF={diff:+.2f}'}")
            
            ws_dataset.cell(r, 8, ai_score)
            ws_dataset.cell(r, 9, conf)
            ws_dataset.cell(r, 10, combined_fb)

    tasks = [grade_one(r) for r in rows]
    await asyncio.gather(*tasks)

    for sheetname in wb.sheetnames:
        s = wb[sheetname]
        if hasattr(s, '_images'):
            s._images = []

    wb.save(excel_path)
    print(f"\nSuccessfully evaluated all 34 rows using score_with_gemini (Gemini 3.8 Flash) and saved to {excel_path}")
    print(f"Exact Matches: {exact_matches}/34 ({exact_matches/34*100:.2f}%) | MAE: {total_diff/34:.4f}")
    
    import shutil
    shutil.copy2(excel_path, ROOT / "public" / "ชุดข้อสอบ_dataset.xlsx")
    print("Synced updated workbook to public/ชุดข้อสอบ_dataset.xlsx")

if __name__ == "__main__":
    asyncio.run(main())
