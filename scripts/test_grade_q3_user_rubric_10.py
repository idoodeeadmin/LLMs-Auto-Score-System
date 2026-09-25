import asyncio
import json
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
from server.services.openai_grading import PROMPT_VERSION, OPENAI_MODEL, score_with_openai


USER_RUBRIC_Q3 = [
    {
        "name": "ภาพรวมคำตอบ Linked List กับ Array",
        "score": 1.00,
        "description": (
            "ประเมินภาพรวม ไม่ต้องแบ่งคะแนนเป็นองค์ประกอบแล้วนำมาบวกกัน\n"
            "พยายามตีความคำตอบในทางที่เป็นประโยชน์ต่อนักศึกษา หากมีแก่นที่เกี่ยวข้องให้คะแนนตามระดับความเข้าใจโดยรวม\n"
            "ข้อมูลส่วนเกินที่ผิดไม่ต้องหักทันที ถ้ายังมีแก่นที่ถูก\n"
            "LIFO/FIFO อย่างเดียวไม่เพียงพอ\n"
            "- 1.00: ตอบประเด็นได้ค่อนข้างครบ มีสาระที่เกี่ยวข้องหลายจุด เช่น อธิบายความแตกต่าง Linked List กับ Array และมีข้อดี/ข้อเสียที่เข้าใจได้ แม้มีรายละเอียดผิดบางส่วนก็ยังให้เต็มได้ถ้าแก่นโดยรวมชัด\n"
            "- 0.75: เข้าใจแก่นค่อนข้างดี มีการเปรียบเทียบที่ชัด และมีข้อดีหรือข้อเสียประกอบ แต่ยังขาดบางส่วนหรืออธิบายไม่ครบ\n"
            "- 0.50: มีอย่างน้อยหนึ่งประเด็นที่มีสาระและเกี่ยวข้อง เช่น Dynamic vs Fixed, เพิ่ม/ลบง่าย, เข้าถึงช้า, ใช้ pointer เพิ่ม ฯลฯ แต่คำตอบไม่ครบ คลุมเครือ หรือมีส่วนผิดค่อนข้างมาก\n"
            "- 0.25: มีแนวคิดที่เกี่ยวข้องเพียงเล็กน้อย/กำกวมมาก แต่ยังจับได้ว่าพยายามตอบเรื่องความแตกต่างหรือข้อดีข้อเสีย\n"
            "- 0.00: ไม่มีสาระที่ใช้ตอบโจทย์ได้ เช่น พูดเพียง LIFO/FIFO, อธิบาย Stack/Queue อย่างเดียว, คำตอบทั่วไปที่ไม่สามารถเชื่อมกับ Linked List vs Array ได้"
        ),
    },
]


async def main():
    items = [x for x in load_dataset() if x["question_no"] == 3][:10]
    assert len(items) == 10 and all(x["answer_type"] == "text" for x in items)
    question = EXAM_QUESTIONS[3]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = ROOT / "artifacts" / f"q3-user-rubric-eval-{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)

    print(f"=== Question 3: first 10 answers ===")
    print(f"Model: {OPENAI_MODEL} | Prompt Version: {PROMPT_VERSION}")
    print(f"Topic: {question['topic']} | Max score: {question['max_score']}")
    print("Rubric: Linked List vs Array 0.50 + Pros/Cons 0.50")
    print("-" * 70)

    results = []
    sem = asyncio.Semaphore(4)

    async def grade_one(item):
        async with sem:
            result = await score_with_openai(
                question_text=item["question_content"],
                answer_text=item["student_answer"],
                max_score=question["max_score"],
                answer_key=question["answer_key"],
                rubrics=USER_RUBRIC_Q3,
                allowed_scores=[0.0, 0.25, 0.50, 0.75, 1.00],
            )
            human = float(item["human_score"])
            ai = float(result.get("score", 0.0))
            entry = {
                "sample_id": item["sample_id"],
                "row": item["row"],
                "human_score": human,
                "ai_score": ai,
                "diff": round(ai - human, 2),
                "exact": ai == human,
                "confidence": result.get("confidence", "unknown"),
                "rubric_breakdown": result.get("rubric_breakdown", []),
                "feedback": result.get("feedback", ""),
            }
            results.append(entry)
            status = "MATCH" if entry["exact"] else f"DIFF ({entry['diff']:+.2f})"
            print(f"[{entry['sample_id']}] Human={human:.2f} | AI={ai:.2f} | Conf={entry['confidence']} | {status}")

    await asyncio.gather(*(grade_one(item) for item in items))
    results.sort(key=lambda x: x["row"])
    truth = [x["human_score"] for x in results]
    predicted = [x["ai_score"] for x in results]
    exact = sum(x["exact"] for x in results)
    tol25 = sum(abs(x["diff"]) <= 0.25 for x in results)
    tol50 = sum(abs(x["diff"]) <= 0.50 for x in results)
    summary = {
        "total": len(results),
        "exact_count": exact,
        "exact_pct": round(exact / len(results) * 100, 2),
        "tolerance_0_25_count": tol25,
        "tolerance_0_25_pct": round(tol25 / len(results) * 100, 2),
        "tolerance_0_50_count": tol50,
        "tolerance_0_50_pct": round(tol50 / len(results) * 100, 2),
        "mae": round(calculate_mae(truth, predicted), 4),
        "qwk": round(calculate_qwk(truth, predicted, step=0.25, max_score=1.0), 4),
    }
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question_no": 3,
        "model": OPENAI_MODEL,
        "prompt_version": PROMPT_VERSION,
        "topic": question["topic"],
        "rubrics": USER_RUBRIC_Q3,
        "summary": summary,
        "results": results,
    }
    path = folder / "q3_user_rubric_overall_first10_results.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"JSON Report saved to: {path}")


if __name__ == "__main__":
    asyncio.run(main())
