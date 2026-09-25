import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / ".venv/Lib/site-packages"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.run_dataset_benchmark import EXAM_QUESTIONS, calculate_mae, calculate_qwk, load_dataset
from server.services.openai_grading import OPENAI_MODEL, PROMPT_VERSION, score_with_openai


Q5_RUBRICS = [
    {
        "name": "ตำแหน่ง array ถูกต้อง",
        "score": 1.0,
        "description": (
            "ให้ตรวจเป็น 2 ส่วนแล้วรวมคะแนน ห้ามสร้างคะแนนหรือเงื่อนไขอื่นเพิ่ม: "
            "ส่วนที่ 1 index 0–19 ได้ 0.75 คะแนนเมื่อถูกครบทุกตำแหน่งตามแนวคำตอบ "
            "ผิด 1 ตำแหน่งพอดีได้ 0.25 คะแนน และผิดตั้งแต่ 2 ตำแหน่งขึ้นไปได้ 0 คะแนน "
            "ส่วนที่ 2 index 20–30 ได้เพิ่ม 0.25 คะแนนต่อเมื่อมีค่า 11, 15, 80, 99 อยู่ครบและถูกตำแหน่ง "
            "พร้อมช่องว่างอื่นถูกต้องทั้งหมด หากไม่มีการตอบช่วง index 20–30 หรือผิดแม้แต่ 1 ตำแหน่งในช่วงนี้ ให้ 0 คะแนนในส่วนที่ 2 ทันที "
            "คะแนนสุดท้ายคือผลรวมของส่วนที่ 1 และส่วนที่ 2 เท่านั้น"
        ),
    }
]

Q5_ANSWER_KEY = (
    "เฉลยการแทน Binary Search Tree ใน Array (เริ่ม index ที่ 0): "
    "0=9, 1=5, 2=16, 5=10, 6=76, 12=13, 13=58, 14=92, "
    "25=11, 26=15, 29=80, 30=99; ตำแหน่งอื่นว่าง. "
    "หากเริ่ม index ที่ 1 ให้เลื่อนตำแหน่งทั้งหมดเพิ่ม 1 แต่ค่ากับโครงสร้างต้องตรงกันทุกจุด."
)
Q5_ANSWER_KEY_IMAGE = ROOT / "public" / "answer-keys" / "q5-array-bst-answer-key.png"


async def main():
    items = [x for x in load_dataset() if x["question_no"] == 5]
    assert len(items) == 34 and all(x["student_img_path"] for x in items)
    assert Q5_ANSWER_KEY_IMAGE.is_file(), f"Answer-key image missing: {Q5_ANSWER_KEY_IMAGE}"
    answer_key_image_bytes = Q5_ANSWER_KEY_IMAGE.read_bytes()
    offset = max(0, int(os.getenv("Q5_OFFSET", "0")))
    limit = int(os.getenv("Q5_LIMIT", "0"))
    items = items[offset:]
    if limit:
        items = items[:limit]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = ROOT / "artifacts" / f"q5-holistic-rubric-eval-{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)
    results = []
    concurrency = max(1, int(os.getenv("Q5_CONCURRENCY", "2")))
    sem = asyncio.Semaphore(concurrency)
    print(f"Grading {len(items)} answers with concurrency={concurrency}", flush=True)

    async def grade_one(item):
        async with sem:
            image_path = ROOT / item["student_img_path"]
            image_bytes = image_path.read_bytes()
            result = None
            for _attempt in range(2):
                result = await score_with_openai(
                    question_text=(
                        item["question_content"]
                        + "\nบริบทของ Tree ที่โจทย์ข้อ 4 อ้างถึง: "
                        + EXAM_QUESTIONS[4]["question_text"]
                        + "\nให้ใช้บริบทนี้ช่วยตรวจว่าค่าที่นักเรียนวางใน Array สอดคล้องกับ Tree หรือไม่ โดยไม่ต้องยึดรูปแบบการเขียนหรือหมายเลข index แบบเดียว หากนักเรียนเลือกวิธี index ที่สอดคล้องกัน"
                    ),
                    answer_text=item["student_answer"],
                    max_score=1.0,
                    answer_key=Q5_ANSWER_KEY,
                    rubrics=Q5_RUBRICS,
                    image_bytes_list=[image_bytes],
                    image_mime_list=["image/jpeg"],
                    answer_key_image_bytes_list=[answer_key_image_bytes],
                    answer_key_image_mime_list=["image/png"],
                    allowed_scores=[0.0, 0.25, 0.50, 0.75, 1.00],
                    # Rubric นี้เป็นเกณฑ์เดียวที่อธิบายคะแนนรวมไว้ใน description
                    # จึงไม่บังคับ rubric_scores แยกซ้ำอีกชั้น ซึ่งทำให้ score รวม
                    # ขัดกับคะแนนย่อยและถูกปฏิเสธเป็น ValueError ได้
                    enforce_rubric_sum=False,
                    strict_rubric_enforcement=True,
                )
                if not str(result.get("feedback", "")).startswith("ไม่สามารถเชื่อมต่อ"):
                    break
            human = float(item["human_score"])
            ai = float(result.get("score", 0.0))
            results.append({
                "sample_id": item["sample_id"], "row": item["row"],
                "human_score": human, "ai_score": ai,
                "diff": round(ai - human, 2), "exact": ai == human,
                "confidence": result.get("confidence", "unknown"),
                "feedback": result.get("feedback", ""),
                "rubric_breakdown": result.get("rubric_breakdown"),
            })
            print(f"Completed {item['sample_id']}", flush=True)

    await asyncio.gather(*(grade_one(item) for item in items))
    results.sort(key=lambda x: x["row"])
    truth = [x["human_score"] for x in results]
    predicted = [x["ai_score"] for x in results]
    exact = sum(x["exact"] for x in results)
    tol25 = sum(abs(x["diff"]) <= 0.25 for x in results)
    tol50 = sum(abs(x["diff"]) <= 0.50 for x in results)
    summary = {
        "total": len(results), "exact_count": exact, "exact_pct": round(exact / len(results) * 100, 2),
        "tolerance_0_25_count": tol25, "tolerance_0_25_pct": round(tol25 / len(results) * 100, 2),
        "tolerance_0_50_count": tol50, "tolerance_0_50_pct": round(tol50 / len(results) * 100, 2),
        "mae": round(calculate_mae(truth, predicted), 4),
        "qwk": round(calculate_qwk(truth, predicted, step=0.25, max_score=1.0), 4),
        "over_count": sum(x["ai_score"] > x["human_score"] for x in results),
        "under_count": sum(x["ai_score"] < x["human_score"] for x in results),
        "match_count": exact,
        "over_sum": round(sum(max(0, x["diff"]) for x in results), 2),
        "under_sum": round(sum(max(0, -x["diff"]) for x in results), 2),
    }
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(), "model": OPENAI_MODEL,
        "prompt_version": PROMPT_VERSION, "question_no": 5,
        "question_text": items[0]["question_content"], "answer_key": Q5_ANSWER_KEY,
        "answer_key_image": str(Q5_ANSWER_KEY_IMAGE.relative_to(ROOT)),
        "rubrics": Q5_RUBRICS, "summary": summary, "results": results,
    }
    path = folder / "q5_holistic_rubric_all34_results.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"JSON Report saved to: {path}")


if __name__ == "__main__":
    asyncio.run(main())
