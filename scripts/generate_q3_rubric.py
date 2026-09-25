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

from scripts.run_dataset_benchmark import EXAM_QUESTIONS
from server.services.openai_grading import OPENAI_MODEL, generate_rubric_with_openai


async def main():
    question = EXAM_QUESTIONS[3]["question_text"]
    result = await generate_rubric_with_openai(question, 1.0, tone="moderate")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = ROOT / "artifacts" / f"q3-generate-rubric-{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": OPENAI_MODEL,
        "question_no": 3,
        "question_text": question,
        "total_score": 1.0,
        "answer_key": result["answer_key"],
        "rubrics": result["rubrics"],
    }
    path = folder / "q3_generated_rubric.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"Saved to: {path}")


if __name__ == "__main__":
    asyncio.run(main())
