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
from server.services.openai_grading import OPENAI_MODEL, PROMPT_VERSION, score_with_openai


GENERATED = ROOT / "artifacts" / "q3-generate-rubric-20260923-032154" / "q3_generated_rubric.json"


async def main():
    generated = json.loads(GENERATED.read_text(encoding="utf-8"))
    rubrics = [{
        "name": "ความเข้าใจ Linked List เทียบกับ Array",
        "score": 1.0,
        "description": (
            "ประเมินภาพรวมของคำตอบ\n"
            "- 1.00: เปรียบเทียบ Linked List กับ Array ได้ชัด และมีข้อดีกับข้อเสียหรือข้อจำกัดที่พอเข้าใจได้ ไม่จำเป็นต้องอธิบายครบทุกประเด็นหรือกล่าวถึง Stack/Queue อย่างละเอียด\n"
            "- 0.75: เปรียบเทียบได้ชัด แต่มีเพียงข้อดีหรือข้อเสียด้านใดด้านหนึ่ง หรือยังขาดบางส่วน\n"
            "- 0.50: มีแก่นที่ถูกและเกี่ยวข้องอย่างน้อยหนึ่งประเด็น เช่น ขนาด การเพิ่ม/ลบ การเข้าถึง หรือความยืดหยุ่น แต่ยังตอบไม่ครบหรือค่อนข้างสับสน\n"
            "- 0.25: มีเพียงข้อความสั้นหรือคลุมเครือที่เกี่ยวข้องเล็กน้อย แต่ยังไม่แสดงความแตกต่างหรือข้อดีข้อเสียได้ชัด\n"
            "- 0: ไม่สามารถระบุสาระเกี่ยวกับความแตกต่างหรือข้อดีข้อเสียของ Linked List กับ Array ได้ เช่น อธิบายเพียง LIFO/FIFO หรือ Stack/Queue อย่างเดียว หรือกล่าวข้อดีทั่วไปที่ไม่รู้ว่าเป็นของโครงสร้างใด\n\n"
            "อย่าบังคับให้ 0.50 เป็นคะแนนเริ่มต้น ให้ใช้ 0 และ 1 ได้ทันทีเมื่อคำตอบเข้าเงื่อนไข และไม่ต้องหักคะแนนเพียงเพราะขาดรายละเอียดทางเทคนิคที่โจทย์ไม่ได้จำเป็นต้องใช้"
        ),
    }]
    assert len(rubrics) == 1 and sum(item["score"] for item in rubrics) == 1.0
    items = [x for x in load_dataset() if x["question_no"] == 3]
    assert len(items) == 34
    question = EXAM_QUESTIONS[3]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = ROOT / "artifacts" / f"q3-generated-rubric-eval-{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)
    results = []
    sem = asyncio.Semaphore(4)

    async def grade_one(item):
        async with sem:
            result = None
            for _attempt in range(2):
                result = await score_with_openai(
                    question_text=item["question_content"],
                    answer_text=item["student_answer"],
                    max_score=1.0,
                    answer_key=None,
                    rubrics=rubrics,
                    allowed_scores=[0.0, 0.25, 0.50, 0.75, 1.00],
                    enforce_rubric_sum=True,
                )
                if not str(result.get("feedback", "")).startswith("ไม่สามารถเชื่อมต่อ"):
                    break
            human = float(item["human_score"])
            breakdown = result.get("rubric_breakdown", [])
            ai = round(sum(float(part.get("score", 0)) for part in breakdown), 2)
            results.append({
                "sample_id": item["sample_id"], "row": item["row"],
                "human_score": human, "ai_score": ai,
                "diff": round(ai - human, 2), "exact": ai == human,
                "confidence": result.get("confidence", "unknown"),
                "rubric_breakdown": breakdown,
                "feedback": result.get("feedback", ""),
            })

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
    }
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(), "model": OPENAI_MODEL,
        "prompt_version": PROMPT_VERSION, "question_no": 3,
        "question_text": generated["question_text"], "answer_key": None,
        "rubrics": rubrics, "summary": summary, "results": results,
    }
    path = folder / "q3_holistic_rubric_all34_results.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for item in results:
        print(f"[{item['sample_id']}] Human={item['human_score']:.2f} | AI={item['ai_score']:.2f} | Conf={item['confidence']}")
    print(f"JSON Report saved to: {path}")


if __name__ == "__main__":
    asyncio.run(main())
