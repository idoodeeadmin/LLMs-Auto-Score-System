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
from server.services.openai_grading import score_with_openai

Q5_RUBRIC_NAME = "ความถูกต้องของการแทนค่า Binary Search Tree ใน Array 1 มิติ"
Q5_RUBRIC_DESC = (
    "ประเมินเป็น 2 ส่วนแล้วนำคะแนนมารวมกันอย่างเคร่งครัด ห้ามให้คะแนนช่วยหรือคะแนนปลอบใจ:\n\n"
    "ส่วนที่ 1: ตรวจช่วง index 0–19 (คะแนนเต็ม 0.75 คะแนน)\n"
    "- ได้ 0.75 คะแนน: หากระบุตำแหน่ง 0=9, 1=5, 2=16, 5=10, 6=76, 12=13, 13=58, 14=92 และเว้นตำแหน่งอื่นว่าง ได้ถูกต้องครบถ้วนทั้งหมด "
    "(หรือหากนิสิตแปลงตำแหน่งสอดคล้องถูกต้องตามโครงสร้าง Tree ข้อ 4 ของตนเอง)\n"
    "- ได้ 0.25 คะแนน: หากระบุโครงสร้างหลักถูก แต่มีจุดผิดพลาดเพียง 1 ตำแหน่งพอดี\n"
    "- ได้ 0.00 คะแนน: หากผิดพลาดตั้งแต่ 2 ตำแหน่งขึ้นไป หรือเขียนตัวเลขเรียงติดกันในช่อง 0–11 โดยไม่เว้นตำแหน่งตามสูตร Tree ให้ 0 คะแนนในส่วนนี้ทันที\n\n"
    "ส่วนที่ 2: ตรวจช่วง index 20–30 (คะแนนเต็ม 0.25 คะแนน)\n"
    "- ได้เพิ่ม 0.25 คะแนน: หากระบุค่า 11, 15, 80, 99 (ที่ index 25, 26, 29, 30) และช่องว่างอื่นถูกต้องครบถ้วนทั้งหมด\n"
    "- ได้ 0.00 คะแนน: หากผิดพลาดแม้แต่ตำแหน่งเดียว หรือไม่มีการเขียนแสดงช่วง index 20–30\n\n"
    "(คะแนนรวมคือ ผลรวมของส่วนที่ 1 และส่วนที่ 2 โดยผลลัพธ์จะต้องเป็น 1.0, 0.75, 0.5, 0.25 หรือ 0.0 เท่านั้น)"
)

Q5_RUBRICS = [
    {
        "name": Q5_RUBRIC_NAME,
        "score": 1.0,
        "description": Q5_RUBRIC_DESC,
    }
]

Q5_QUESTION_TEXT = (
    "จากทรีในข้อ 4 นิสิตสามารถนำทรีนี้มาจากโดยใช้ Array 1 มิติ ได้ จงแสดงค่าตัวเลขใน Array (Array ไม่พอ เพิ่มเติมได้)\n"
    "บริบทของ Tree ที่โจทย์ข้อ 4 อ้างถึง: จงสร้าง Binary Search Tree จากข้อมูล: 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99"
)

Q5_ANSWER_KEY = (
    "เฉลยการแทน Binary Search Tree ใน Array (เริ่ม index ที่ 0): "
    "0=9, 1=5, 2=16, 5=10, 6=76, 12=13, 13=58, 14=92, "
    "25=11, 26=15, 29=80, 30=99; ตำแหน่งอื่นว่าง. "
    "หากเริ่ม index ที่ 1 ให้เลื่อนตำแหน่งทั้งหมดเพิ่ม 1 "
    "(1=9, 2=5, 3=16, 6=10, 7=76, 13=13, 14=58, 15=92, 26=11, 27=15, 30=80, 31=99) แต่ค่ากับโครงสร้างต้องตรงกันทุกจุด. "
    "หมายเหตุ: นิสิตสามารถแปลงตามทรีที่ตนเองวาดไว้ในข้อ 4 ได้อย่างสมเหตุสมผล หากตำแหน่งลูกสอดคล้องกับสูตร 2i+1, 2i+2"
)

KEY_IMG_PATH = ROOT / "public" / "answer-keys" / "q5-array-bst-answer-key.png"
key_img_bytes = KEY_IMG_PATH.read_bytes() if KEY_IMG_PATH.exists() else None

def calculate_qwk(y_true, y_pred, step=0.25, max_score=1.0):
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        return 0.0
    if y_true == y_pred:
        return 1.0
    k = int(round(max_score / step)) + 1
    w = [[((i - j) ** 2) / ((k - 1) ** 2) for j in range(k)] for i in range(k)]
    O = [[0] * k for _ in range(k)]
    hist_true = [0] * k
    hist_pred = [0] * k
    for t, p in zip(y_true, y_pred):
        i = max(0, min(k - 1, int(round(t / step))))
        j = max(0, min(k - 1, int(round(p / step))))
        O[i][j] += 1
        hist_true[i] += 1
        hist_pred[j] += 1
    N = len(y_true)
    E = [[hist_true[i] * hist_pred[j] / N for j in range(k)] for i in range(k)]
    num = sum(w[i][j] * O[i][j] for i in range(k) for j in range(k))
    den = sum(w[i][j] * E[i][j] for i in range(k) for j in range(k))
    return 1.0 - (num / den) if den != 0 else 0.0

async def main():
    excel_path = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"
    wb = openpyxl.load_workbook(excel_path)
    
    # 1. Update Exam_Rubrics Row 11
    ws_rubrics = wb["Exam_Rubrics"]
    ws_rubrics.cell(11, 4, Q5_RUBRIC_NAME)
    ws_rubrics.cell(11, 5, 1.0)
    ws_rubrics.cell(11, 6, Q5_RUBRIC_DESC)
    print("Updated Exam_Rubrics Row 11 with refined rubric.")
    
    # 2. Prepare all 34 rows for evaluation with dual feedback
    ws_dataset = wb["ชุดข้อสอบ_dataset"]
    rows = list(range(142, 176)) # 34 rows for Q5
    assert len(rows) == 34
    
    all_results = []
    to_evaluate = []
    
    for r in rows:
        sid = ws_dataset.cell(r, 1).value
        human_score = float(ws_dataset.cell(r, 7).value or 0.0)
        std_idx = r - 141
        img_name = f"LINE_ALBUM_Photo2.1_260918_{std_idx}.jpg"
        img_path = ROOT / "ชุดข้อสอบใหม่" / "photo_clean_ชุดที่2" / img_name
        
        to_evaluate.append({
            "row": r, "sample_id": sid, "human_score": human_score,
            "student_idx": std_idx, "img_name": img_name, "img_path": img_path
        })
            
    print(f"Evaluating all {len(to_evaluate)} answers with dual teacher & student feedback...")
    
    sem = asyncio.Semaphore(4)
    
    async def grade_one(item):
        async with sem:
            img_bytes = item["img_path"].read_bytes()
            print(f"Grading {item['sample_id']} (idx={item['student_idx']}) ...", flush=True)
            res = await score_with_openai(
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
            conf = res.get("confidence", "unknown")
            teacher_fb = res.get("teacher_feedback", "")
            student_fb = res.get("student_feedback", "")
            combined_fb = res.get("feedback", "")
            tr = res.get("transcription", "")
            diff = round(ai_score - item["human_score"], 2)
            match = (ai_score == item["human_score"])
            
            result_item = {
                "row": item["row"],
                "sample_id": item["sample_id"],
                "img_name": item["img_name"],
                "human_score": item["human_score"],
                "ai_score": ai_score,
                "diff": diff,
                "match": match,
                "confidence": conf,
                "teacher_feedback": teacher_fb,
                "student_feedback": student_fb,
                "feedback": combined_fb,
                "transcription": tr,
            }
            print(f"  -> {item['sample_id']}: Human={item['human_score']:.2f} | AI={ai_score:.2f} | Diff={diff:+.2f} | Match={'MATCH' if match else 'DIFF'}")
            return result_item

    tasks = [grade_one(item) for item in to_evaluate]
    evaluated_results = await asyncio.gather(*tasks)
    
    for res in evaluated_results:
        all_results.append(res)
        r = res["row"]
        ws_dataset.cell(r, 8, res["ai_score"])
        ws_dataset.cell(r, 9, res["confidence"])
        ws_dataset.cell(r, 10, res["feedback"])
        
    # Sort by row
    all_results.sort(key=lambda x: x["row"])
    
    # Save Excel
    wb.save(excel_path)
    print(f"\nSuccessfully saved updated workbook to {excel_path}!")
    
    # Save full JSON
    all_json_path = ROOT / "artifacts" / "q5_all34_evaluation_results.json"
    with open(all_json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"Saved complete evaluation JSON to {all_json_path}")
    
    # Calculate statistics
    y_true = [x["human_score"] for x in all_results]
    y_pred = [x["ai_score"] for x in all_results]
    exacts = sum(1 for x in all_results if x["match"])
    mae = sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)
    qwk = calculate_qwk(y_true, y_pred, step=0.25, max_score=1.0)
    
    print("\n" + "="*80)
    print("FINAL EVALUATION REPORT FOR QUESTION 5 (ALL 34 STUDENTS)")
    print("="*80)
    print(f"Total evaluated: {len(all_results)} answers")
    print(f"Exact Matches:   {exacts} / {len(all_results)} ({exacts / len(all_results) * 100:.2f}%)")
    print(f"MAE:             {mae:.4f}")
    print(f"QWK (Kappa):     {qwk:.4f}")
    print("="*80)
    
    # Print table
    print(f"\n{'Sample ID':<10} | {'Human':<6} | {'AI':<6} | {'Diff':<6} | {'Status':<8} | {'Confidence':<10}")
    print("-" * 65)
    for x in all_results:
        status = "EXACT" if x["match"] else f"{x['diff']:+.2f}"
        print(f"{x['sample_id']:<10} | {x['human_score']:<6.2f} | {x['ai_score']:<6.2f} | {x['diff']:<+6.2f} | {status:<8} | {x['confidence']:<10}")

if __name__ == "__main__":
    asyncio.run(main())
