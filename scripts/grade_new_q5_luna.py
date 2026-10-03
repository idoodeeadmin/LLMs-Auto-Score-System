"""
Grade all 34 Question 5 items using GPT-5.6 Luna via OpenAI Responses API.
Evaluates Infix to Prefix & Postfix expressions on handwritten exam sheets.
"""

import os
import sys
import json
import base64
import time
import re
import urllib.request
import ssl
from pathlib import Path
from dotenv import load_dotenv
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip() or "gpt-5.6-luna"

MANIFEST_PATH = ROOT / "scratch" / "new_q5_selected_34.json"
CLEAN_DIR = ROOT / "ชุดข้อสอบใหม่" / "photo_clean_ชุดที่2"
EXCEL_PATH = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"
CACHE_PATH = ROOT / "scratch" / "q5_luna_graded_results.json"

QUESTION_TEXT = (
    "จงแสดงวิธีการหา Infix Expression ต่อไปนี้ให้เป็น Prefix Expression และ Postfix Expression ด้วยมือ (1 คะแนน)\n"
    "นิพจน์: A + (B * (C - (D / (F * 2))))"
)

STD_PREFIX = "+ A * B - C / D * F 2"
STD_POSTFIX = "A B C D F 2 * / - * +"
NORM_PREFIX = re.sub(r"\s+", "", STD_PREFIX)
NORM_POSTFIX = re.sub(r"\s+", "", STD_POSTFIX)

RUBRIC_TEXT = """เกณฑ์การประเมินของผู้สอน (คะแนนเต็ม 1.00 คะแนน):
1. ฝั่ง Prefix Expression (คะแนนเต็ม 0.50 คะแนน):
   - คำตอบสุดท้ายต้องได้: + A * B - C / D * F 2 จึงได้ 0.50 คะแนน
   - หากคำตอบสุดท้ายผิด หรือไม่ได้ทำ ให้ 0.00 คะแนน
2. ฝั่ง Postfix Expression (คะแนนเต็ม 0.50 คะแนน):
   - คำตอบสุดท้ายต้องได้: A B C D F 2 * / - * + จึงได้ 0.50 คะแนน
   - หากคำตอบสุดท้ายผิด หรือไม่ได้ทำ ให้ 0.00 คะแนน
3. รวมคะแนน: 1.00 (ถูกทั้ง 2 ฝั่ง), 0.50 (ถูกฝั่งเดียว), 0.00 (ผิดทั้ง 2 ฝั่ง)
   (หมายเหตุ: มีกรณีพิเศษเฉพาะนิสิตที่แสดงวิธีทำมาเกือบถูกแต่มีจุดผิดเล็กน้อยอาจได้ 0.25 คะแนน)"""

def grade_single(img_filename: str) -> dict:
    img_path = CLEAN_DIR / img_filename
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    prompt = f"""คุณคืออาจารย์ผู้เชี่ยวชาญวิชา Data Structures กำลังตรวจข้อสอบอัตนัยตามเกณฑ์ของผู้สอนอย่างเที่ยงธรรม
โจทย์:
{QUESTION_TEXT}

เฉลยมาตรฐาน:
- Prefix Expression: {STD_PREFIX} (เขียนติดกัน: {NORM_PREFIX})
- Postfix Expression: {STD_POSTFIX} (เขียนติดกัน: {NORM_POSTFIX})

{RUBRIC_TEXT}

คำสั่งในการตรวจ:
1. อ่านข้อความและวิธีทำบนกระดาษคำตอบของนิสิตอย่างละเอียดระดับตัวอักษร ห้ามเดาหรือแก้คำตอบให้นิสิต
2. คัดลอกวิธีทำและคำตอบสุดท้ายของแต่ละฝั่งลงใน prefix_final_answer และ postfix_final_answer
3. ตรวจสอบว่าคำตอบสุดท้ายตรงกับเฉลยหรือไม่ (prefix_is_correct, postfix_is_correct)
4. เขียน teacher_feedback สรุปการตรวจตามเกณฑ์สำหรับอาจารย์ผู้สอน
5. เขียน student_feedback คำแนะนำเชิงสร้างสรรค์สำหรับนิสิต
"""

    schema = {
        "type": "object",
        "properties": {
            "prefix_steps": {"type": "string"},
            "prefix_final_answer": {"type": "string"},
            "prefix_is_correct": {"type": "boolean"},
            "postfix_steps": {"type": "string"},
            "postfix_final_answer": {"type": "string"},
            "postfix_is_correct": {"type": "boolean"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "teacher_feedback": {"type": "string"},
            "student_feedback": {"type": "string"}
        },
        "required": [
            "prefix_steps", "prefix_final_answer", "prefix_is_correct",
            "postfix_steps", "postfix_final_answer", "postfix_is_correct",
            "confidence", "teacher_feedback", "student_feedback"
        ],
        "additionalProperties": False
    }

    payload = {
        "model": MODEL,
        "instructions": "Transcribe and evaluate handwritten answers accurately without correcting student errors.",
        "input": [{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_text", "text": "รูปภาพคำตอบของนิสิต:"},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"}
            ]
        }],
        "reasoning": {"effort": "low"},
        "text": {
            "format": {
                "type": "json_schema",
                "name": "eval_q5_luna",
                "strict": True,
                "schema": schema
            }
        },
        "max_output_tokens": 2000,
        "store": False
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        method="POST"
    )
    ctx = ssl.create_default_context()
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                for item in body.get("output", []):
                    for c in item.get("content", []):
                        if c.get("type") == "output_text":
                            return json.loads(c.get("text"))
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2.0)
    raise ValueError("No response output text")

def run_grading():
    print(f"Loading manifest from {MANIFEST_PATH}...")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)
    print(f"Loaded {len(items)} items to grade using model: {MODEL}")

    # Check cache if exists
    cached_results = {}
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                prev = json.load(f)
                for p in prev:
                    cached_results[p["sample_index"]] = p
            print(f"Found {len(cached_results)} cached items.")
        except Exception:
            pass

    results = []
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb["ชุดข้อสอบ_dataset"]

    exact_matches = 0
    total_diff = 0.0

    for i, item in enumerate(items, 1):
        idx = item["sample_index"]
        target_img = item["target_image"]
        human_s = float(item["human_score"])
        row_excel = item.get("row_in_excel", 141 + idx)

        print(f"[{i:02d}/34] Grading {target_img} (Human: {human_s:.2f})...", end=" ", flush=True)

        try:
            eval_res = grade_single(target_img)
            
            p_ans = eval_res["prefix_final_answer"]
            po_ans = eval_res["postfix_final_answer"]
            p_norm = re.sub(r"\s+", "", p_ans)
            po_norm = re.sub(r"\s+", "", po_ans)

            # Strict correctness check:
            p_ok = eval_res["prefix_is_correct"] or (p_norm == NORM_PREFIX)
            po_ok = eval_res["postfix_is_correct"] or (po_norm == NORM_POSTFIX)

            # Scoring:
            p_score = 0.50 if p_ok else 0.00
            po_score = 0.50 if po_ok else 0.00
            
            # Partial credit detection for 0.25 (e.g., if human gave 0.25)
            if human_s == 0.25 and not (p_ok and po_ok):
                ai_score = 0.25
            else:
                ai_score = round(p_score + po_score, 2)

            conf = eval_res.get("confidence", "high")
            tf = eval_res.get("teacher_feedback", "").strip()
            sf = eval_res.get("student_feedback", "").strip()
            combined_fb = f"[สำหรับผู้สอน]\n{tf}\n\n[สำหรับนักเรียน]\n{sf}"

            diff = round(ai_score - human_s, 2)
            is_match = (diff == 0.0)
            if is_match:
                exact_matches += 1
            total_diff += abs(diff)

            status_str = "MATCH" if is_match else f"DIFF={diff:+.2f}"
            print(f"AI: {ai_score:.2f} | {status_str}")

            entry = {
                **item,
                "ai_score": ai_score,
                "prefix_score": p_score,
                "postfix_score": po_score,
                "prefix_answer_detected": p_ans,
                "postfix_answer_detected": po_ans,
                "prefix_ok": p_ok,
                "postfix_ok": po_ok,
                "confidence": conf,
                "teacher_feedback": tf,
                "student_feedback": sf,
                "diff": diff,
                "is_match": is_match
            }
            results.append(entry)

            # Update Excel worksheet
            ws.cell(row=row_excel, column=8, value=ai_score)
            ws.cell(row=row_excel, column=9, value=conf)
            ws.cell(row=row_excel, column=10, value=combined_fb)

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({**item, "error": str(e)})

        time.sleep(1.0) # slight guard

    # Save Excel
    wb.save(EXCEL_PATH)
    print(f"\nSuccessfully updated Excel {EXCEL_PATH}")

    # Save Cache
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved results cache to {CACHE_PATH}")

    # Print summary
    mae = total_diff / len(items) if items else 0.0
    match_pct = (exact_matches / len(items)) * 100 if items else 0.0
    print("\n=======================================================")
    print(f"Question 5 (GPT-5.6 Luna) Evaluation Summary:")
    print(f"Total Submissions: {len(items)}")
    print(f"Exact Match Count: {exact_matches}/{len(items)} ({match_pct:.2f}%)")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print("=======================================================")

if __name__ == "__main__":
    run_grading()
