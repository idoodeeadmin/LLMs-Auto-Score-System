import asyncio
import json
import mimetypes
import sys
from pathlib import Path

import openpyxl
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from server.services.openai_grading import score_with_openai

EXCEL = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"
OUT = ROOT / "artifacts" / "text_answer_image_transcriptions.json"
QUESTIONS = {
    1: ("อธิบายความต่างของ Row-major vs Column-major", 2.0, [0.0, 1.0, 2.0]),
    2: ("อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลใหญ่กว่า O(n^2) และยกตัวอย่าง Algorithm", 2.0, [0.0, 0.5, 1.0, 1.5, 2.0]),
    3: ("การใช้ลิ้งค์ลิสต์เป็นสแตกและคิวจะแตกต่างจากการใช้อาร์เรย์อย่างไร และมีข้อดีข้อเสียอย่างไร", 1.0, [0.0, 0.25, 0.5, 0.75, 1.0]),
}


def rubric_for(question_no):
    return [{"name": "ถอดคำตอบตามภาพ", "score": QUESTIONS[question_no][1], "description": "ห้ามใช้ rubric เพื่อตีความหรือสรุปคำตอบ ให้ถอดข้อความที่มองเห็นตามลำดับเดิมเท่านั้น หากเป็นตารางหรือภาพวาดให้ใช้คำกำกับสั้น ๆ ในวงเล็บเหลี่ยม", "allowed_scores": QUESTIONS[question_no][2]}]


async def main():
    wb = openpyxl.load_workbook(EXCEL, data_only=True)
    ws = wb["ชุดข้อสอบ_dataset"]
    items = []
    for q in (1, 2, 3):
        files = sorted((ROOT / f"ชุดข้อสอบใหม่/photo_clean_text{q}").glob("*.jpg"))
        if len(files) != 34:
            raise RuntimeError(f"Q{q} expected 34 images, found {len(files)}")
        for index, path in enumerate(files):
            row = 6 + (q - 1) * 34 + index
            items.append({"sample_id": ws.cell(row, 1).value, "question_no": q, "image": path})

    sem = asyncio.Semaphore(4)

    async def one(item):
        async with sem:
            q, (question, maximum, allowed) = item["question_no"], QUESTIONS[item["question_no"]]
            result = await score_with_openai(
                question_text=question,
                answer_text="",
                max_score=maximum,
                rubrics=rubric_for(q),
                image_bytes_list=[item["image"].read_bytes()],
                image_mime_list=[mimetypes.guess_type(item["image"].name)[0] or "image/jpeg"],
                allowed_scores=allowed,
                strict_rubric_enforcement=False,
            )
            return {"sample_id": item["sample_id"], "question_no": q, "image": str(item["image"].relative_to(ROOT)), "transcription": result.get("transcription", ""), "confidence": result.get("confidence"), "error": bool(result.get("metrics", {}).get("manual_review_required"))}

    results = await asyncio.gather(*(one(item) for item in items))
    results.sort(key=lambda x: (x["question_no"], x["sample_id"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source": str(EXCEL.relative_to(ROOT)), "count": len(results), "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {OUT} ({len(results)} records)")


if __name__ == "__main__":
    asyncio.run(main())
