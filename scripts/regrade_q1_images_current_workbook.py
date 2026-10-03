"""Grade Q1 cleaned images with the same production template as Q1 text."""
import asyncio
import hashlib
import json
import os
import sys
import types
from datetime import datetime
from pathlib import Path

import openpyxl
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(ROOT / ".env")
# This standalone batch uses only exam_policy.count_answer_words. The desktop
# Python bundle lacks the web server's compiled FastAPI dependency.
if "fastapi" not in sys.modules:
    fastapi_stub = types.ModuleType("fastapi")
    fastapi_stub.HTTPException = type("HTTPException", (Exception,), {})
    sys.modules["fastapi"] = fastapi_stub
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

async def main():
    source = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"
    images = ROOT / "docs_and_tests" / "q1_image_cleaned"
    wb = openpyxl.load_workbook(source, read_only=True, data_only=True)
    rows = [r for r in wb["ชุดข้อสอบ_dataset"].values if len(r) > 7 and r[1] == 1 and str(r[0]).startswith("DS-")]
    rubric_rows = [r for r in wb["Exam_Rubrics"].values if len(r) > 5 and r[0] == 1]
    rubrics = [dict(name=r[3], score=float(r[4]), description=r[5], allowed_scores=[0, 1]) for r in rubric_rows]
    assert len(rows) == 34 and len(rubrics) == 2
    assert all(r[4] == "text" for r in rows)
    selected = {s.strip() for s in os.getenv("Q1_IMAGE_IDS", "").split(",") if s.strip()}
    if selected:
        rows = [r for r in rows if r[0] in selected]
        assert len(rows) == len(selected)
    rows = rows[:int(os.getenv("Q1_IMAGE_LIMIT", "34"))]
    paths = {r[0]: next(images.glob(f"{r[0]}_*.jpg")) for r in rows}
    assert len(list(images.glob("DS-*.jpg"))) == 34

    out = ROOT / "docs_and_tests" / ("q1_image_regrade_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json")
    report = dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  image_directory=str(images), model=OPENAI_MODEL, prompt_version=PROMPT_VERSION,
                  function="server.services.openai_grading.score_with_openai", rubric=rubrics,
                  answer_key=None, input_modality="image_only", results=[])
    sem = asyncio.Semaphore(3)
    def save():
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    async def grade(row):
        async with sem:
            path = paths[row[0]]
            raw = path.read_bytes()
            try:
                result = await score_with_openai(question_text=str(row[3]), answer_text="",
                    max_score=2.0, rubrics=rubrics, allowed_scores=[0.0, 1.0, 2.0],
                    image_bytes_list=[raw], image_mime_list=["image/jpeg"])
                ok = not result.get("metrics", {}).get("manual_review_required", False)
                error = None
            except Exception as exc:
                result, ok, error = None, False, str(exc)
            report["results"].append(dict(sample_id=row[0], image=path.name,
                image_sha256=hashlib.sha256(raw).hexdigest(), human_score=row[6],
                text_ai_score=row[7], success=ok, error=error, result=result))
            save()
            print(f"{row[0]}: {'OK' if ok else 'FAILED'} score={result['score'] if result else None}", flush=True)

    print(f"Model={OPENAI_MODEL}; count={len(rows)}; output={out}", flush=True)
    await asyncio.gather(*(grade(r) for r in rows))
    report["results"].sort(key=lambda r: r["sample_id"])
    valid = [r for r in report["results"] if r["success"]]
    report["summary"] = dict(completed=len(valid), total=len(rows),
        image_teacher_exact=sum(r["human_score"] == r["result"]["score"] for r in valid),
        image_text_exact=sum(r["text_ai_score"] == r["result"]["score"] for r in valid),
        image_teacher_mae=sum(abs(r["human_score"]-r["result"]["score"]) for r in valid)/len(valid) if valid else None)
    save()
    print(json.dumps(report["summary"]), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
