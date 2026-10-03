"""Transcribe clean Q3 answer images using the production confidence rule."""
import asyncio
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
from scripts.regrade_corrected_q2_q3_answers import OPENAI_MODEL, PROMPT_VERSION
from server.services.openai_grading import _image_content, request_structured_output
from server.services.gemini_grading import GEMINI_MODEL, request_gemini_structured_output

SOURCE = ROOT / "server/services/openai_grading.py"
REFERENCE = ROOT / "docs_and_tests/q3_transcription_review/q3_transcriptions_reviewed.json"
IMAGES = ROOT / "ชุดข้อสอบใหม่/photo_clean_text3"
PROVIDER = os.getenv("Q3_READING_PROVIDER", "openai").strip().lower()
assert PROVIDER in {"openai", "gemini"}
MODEL = GEMINI_MODEL if PROVIDER == "gemini" else OPENAI_MODEL
TRANSPORT = request_gemini_structured_output if PROVIDER == "gemini" else request_structured_output
OUT = ROOT / "docs_and_tests/q3_transcription_review" / (
    "q3_gemini_handwriting_reading_pilot.json" if PROVIDER == "gemini" and os.getenv("Q3_READING_ONLY_ID")
    else "q3_gemini_handwriting_reading_results.json" if PROVIDER == "gemini"
    else "q3_handwriting_reading_results.json"
)
confidence_rule = re.search(r'4\. ตรวจสอบความชัดเจนของลายมือ[^\n]+', SOURCE.read_text(encoding="utf-8"))
assert confidence_rule, "Production confidence rule was not found"
CONFIDENCE_RULE = confidence_rule.group(0)

PROMPT = f"""คุณกำลังถอดข้อความคำตอบลายมือจากภาพ ไม่ได้ตรวจให้คะแนน
ถอดข้อความตามที่เห็นเท่านั้น ห้ามตีความ เรียบเรียง แก้คำผิด หรือเติมคำที่ไม่ปรากฏในภาพ
ถ้าบางคำอ่านไม่ได้ ให้เขียน [อ่านไม่ชัด] ณ ตำแหน่งนั้น ห้ามเดาคำ
ไม่ต้องคัดลอกข้อความโจทย์ หมายเลขข้อ คะแนนหรือรอยตรวจของผู้สอน หรือข้อความพิมพ์บนกระดาษ
รักษาลำดับบรรทัดของคำตอบและสัญลักษณ์ที่มีความหมาย

ใช้เกณฑ์ความมั่นใจเดียวกับ prompt แม่แบบจริงของระบบ:
{CONFIDENCE_RULE}

รายงาน confidence เป็น high, medium หรือ low ตามความชัดเจนในการอ่านคำตอบ
ถ้าเป็น medium หรือ low ให้อธิบายจุดที่ไม่ชัดและแจ้งให้ผู้สอนทบทวนใน teacher_feedback
ถ้าเป็น high ให้ teacher_feedback อธิบายสั้น ๆ ว่าอ่านได้ชัด
ตอบกลับเป็น JSON ตาม schema เท่านั้น"""

SCHEMA = {"type": "object", "properties": {
    "transcription": {"type": "string"},
    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    "teacher_feedback": {"type": "string"},
}, "required": ["transcription", "confidence", "teacher_feedback"], "additionalProperties": False}


async def main():
    refs = json.loads(REFERENCE.read_text(encoding="utf-8"))
    assert len(refs) == 34 and len({x["id"] for x in refs}) == 34
    for item in refs:
        assert (IMAGES / item["image"]).is_file()
        assert item["status"] == "done" and item["transcription"].strip()
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "provider": PROVIDER, "model": MODEL,
              "prompt_version": PROMPT_VERSION, "method": "transcription_only",
              "transport": f"{TRANSPORT.__module__}.{TRANSPORT.__name__}",
              "production_confidence_rule": CONFIDENCE_RULE, "prompt": PROMPT,
              "reference_sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest(), "results": []}
    only = os.getenv("Q3_READING_ONLY_ID", "").strip()
    if only:
        refs = [x for x in refs if x["id"] == only]
        assert len(refs) == 1
    sem = asyncio.Semaphore(3)

    async def run(item):
        async with sem:
            path = IMAGES / item["image"]
            raw = path.read_bytes()
            mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
            try:
                result = await TRANSPORT(
                    [{"type": "input_text", "text": PROMPT}, _image_content(raw, mime)],
                    SCHEMA, "handwriting_transcription", max_output_tokens=2500)
                success = (result.get("confidence") in ("high", "medium", "low")
                           and isinstance(result.get("transcription"), str)
                           and bool(result["transcription"].strip()))
                error = None
            except Exception as exc:
                result, success, error = None, False, f"{type(exc).__name__}: {exc}"
            entry = {"sample_id": item["id"], "image": item["image"],
                     "image_sha256": hashlib.sha256(raw).hexdigest(),
                     "human_reference": item["transcription"], "human_note": item.get("note", ""),
                     "success": success, "error": error, "result": result}
            report["results"].append(entry)
            OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(item["id"], "success", success, "confidence", result.get("confidence") if result else "-", flush=True)

    print("model", MODEL, "count", len(refs), "output", OUT, flush=True)
    await asyncio.gather(*(run(item) for item in refs))
    report["results"].sort(key=lambda x: x["sample_id"])
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("completed", sum(x["success"] for x in report["results"]), "of", len(refs), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
