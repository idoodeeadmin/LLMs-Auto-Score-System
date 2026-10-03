"""Live smoke check for the Gemini grading transport; prints no credentials."""
import asyncio
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
# The bundled local Python is newer than the project's compiled Pydantic wheel.
# Reuse the grading smoke helper's word-count shim for this standalone check.
import scripts.regrade_corrected_q2_q3_answers  # noqa: F401,E402
from server.services.gemini_grading import (
    GEMINI_MODEL, generate_rubric_with_gemini, request_gemini_structured_output,
    score_with_gemini,
)


async def main():
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}},
              "required": ["ok"], "additionalProperties": False}
    try:
        result = await request_gemini_structured_output(
            [{"type": "input_text", "text": "Return ok=true as JSON."}], schema, "smoke")
        print("structured", result)
        rubric = await generate_rubric_with_gemini("อธิบายหลักการทำงานของ Stack", 1.0)
        print("rubric", len(rubric["rubrics"]), "total", sum(x["score"] for x in rubric["rubrics"]))
        scored = await score_with_gemini(
            question_text="Stack ทำงานแบบใด", answer_text="เข้าทีหลังออกก่อน (LIFO)",
            max_score=1.0, answer_key="Stack ทำงานแบบ LIFO",
            rubrics=[{"name": "LIFO", "score": 1.0, "description": "อธิบาย LIFO ได้ถูกต้อง"}],
            allowed_scores=[0.0, 1.0],
        )
        print("text_grade", scored["score"], scored["metrics"])
        image = ROOT / "ชุดข้อสอบใหม่/photo_clean_text3/IMG_2909.jpg"
        image_result = await score_with_gemini(
            question_text="อธิบายข้อดีข้อเสียของ Linked List เมื่อเทียบกับ Array",
            answer_text="", max_score=1.0,
            answer_key="Linked List ปรับขนาดได้ แต่เข้าถึงตำแหน่งโดยตรงช้ากว่า Array",
            rubrics=[{"name": "เปรียบเทียบ", "score": 1.0,
                      "description": "กล่าวถึงความยืดหยุ่นของขนาดและข้อเสียด้านการเข้าถึงข้อมูล"}],
            image_bytes_list=[image.read_bytes()], image_mime_list=["image/jpeg"],
            allowed_scores=[0.0, 0.5, 1.0],
        )
        print("image_grade", image_result["score"], image_result["metrics"])
        assert result == {"ok": True}
        assert scored["metrics"]["provider"] == "gemini" and not scored["metrics"]["manual_review_required"]
        assert image_result["metrics"]["provider"] == "gemini"
        print("model", GEMINI_MODEL, "smoke passed")
    except httpx.HTTPStatusError as error:
        print("HTTP", error.response.status_code)
        print(error.response.text[:1200])
        raise


if __name__ == "__main__":
    asyncio.run(main())
