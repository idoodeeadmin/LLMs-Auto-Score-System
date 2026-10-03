"""Shared server rules for text answers and exam windows."""
import re
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
try:
    from pythainlp.tokenize import word_tokenize
except ImportError:
    word_tokenize = None

MAX_ANSWER_WORDS = 300
MAX_ANSWER_CHARACTERS = 2500
MAX_SINGLE_TOKEN_CHARACTERS = 60
MAX_ANSWER_IMAGES = 10
SUBMISSION_GRACE_SECONDS = 60


import subprocess
import json
from pathlib import Path

WORD_COUNTER_SCRIPT = Path(__file__).resolve().parent / "services" / "word_counter.mjs"


def normalize_word_count_text(text: str) -> str:
    # Separate Thai script and Latin/alphanumeric boundaries
    norm = re.sub(r"([\u0E00-\u0E7F])([a-zA-Z0-9])", r"\1 \2", text)
    norm = re.sub(r"([a-zA-Z0-9])([\u0E00-\u0E7F])", r"\1 \2", norm)
    # Split nominalizing prefixes 'การ' and 'ความ' so counting adheres to morphemes / root words
    norm = re.sub(r"(การ|ความ)(?=[\u0E01-\u0E2E])", r"\1 ", norm)
    return norm


def count_answer_words(text: str) -> int:
    """Counts words using Node Intl.Segmenter for 100% exact parity with frontend, with fallback."""
    if not text or not text.strip():
        return 0
    try:
        proc = subprocess.run(
            ["node", str(WORD_COUNTER_SCRIPT)],
            input=text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=3,
            check=True
        )
        return int(proc.stdout.strip())
    except Exception:
        norm = normalize_word_count_text(text)
        if word_tokenize:
            tokens = word_tokenize(norm, engine="newmm", keep_whitespace=False)
            return sum(1 for token in tokens if re.search(r"[\u0E01-\u0E5B\w]", token))
        return len(re.findall(r"[\u0E00-\u0E7F]+|[a-zA-Z0-9_]+", norm))


def count_multiple_answers(answers: dict[str, str]) -> dict[str, int]:
    """Batch counts words for multiple answers via Node Intl.Segmenter in a single execution."""
    if not answers:
        return {}
    try:
        proc = subprocess.run(
            ["node", str(WORD_COUNTER_SCRIPT)],
            input=json.dumps(answers, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            check=True
        )
        return json.loads(proc.stdout.strip())
    except Exception:
        return {k: count_answer_words(v) for k, v in answers.items()}


def validate_answer_text(text: str) -> int:
    if len(text) > MAX_ANSWER_CHARACTERS:
        raise HTTPException(422, f"คำตอบยาวเกินขนาดที่ระบบรองรับ (ไม่เกิน {MAX_ANSWER_CHARACTERS} ตัวอักษร)")
    
    # Check for single tokens longer than MAX_SINGLE_TOKEN_CHARACTERS
    for token in text.split():
        if len(token) > MAX_SINGLE_TOKEN_CHARACTERS:
            raise HTTPException(422, "คำตอบมีข้อความที่ยาวผิดปกติหรืออาจเป็นข้อความสแปม กรุณาตรวจสอบคำตอบ")

    count = count_answer_words(text)
    if count > MAX_ANSWER_WORDS:
        raise HTTPException(422, f"คำตอบต้องไม่เกิน {MAX_ANSWER_WORDS} คำ (พบ {count} คำ)")
    return count


def parse_exam_time(value):
    if not value:
        return None
    dt = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
    # Existing stored dates without an offset use UTC.
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def ensure_submission_window(exam: dict, now=None):
    if exam.get("is_closed"):
        raise HTTPException(403, "ผู้สอนปิดรับคำตอบสำหรับแบบทดสอบนี้แล้ว")
    now = now or datetime.now(timezone.utc)
    try:
        start, end = parse_exam_time(exam.get("start_date")), parse_exam_time(exam.get("end_date"))
    except (ValueError, TypeError):
        raise HTTPException(409, "เวลาสอบไม่ถูกต้อง กรุณาติดต่อผู้สอน")
    if start and now < start:
        raise HTTPException(403, "ยังไม่ถึงเวลาเริ่มสอบ")
    if end and now > end + timedelta(seconds=SUBMISSION_GRACE_SECONDS):
        raise HTTPException(403, "เลยกำหนดเวลาส่งคำตอบข้อสอบแล้ว")
