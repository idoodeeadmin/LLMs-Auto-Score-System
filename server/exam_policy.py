"""Shared server rules for text answers and exam windows."""
import re
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from pythainlp.tokenize import word_tokenize

MAX_ANSWER_WORDS = 300
MAX_ANSWER_CHARACTERS = 30000
MAX_ANSWER_IMAGES = 10
SUBMISSION_GRACE_SECONDS = 60


def count_answer_words(text: str) -> int:
    # NewMM segments Thai without requiring spaces. Punctuation is not a word.
    tokens = word_tokenize(text, engine="newmm", keep_whitespace=False)
    return sum(1 if any("\u0e01" <= char <= "\u0e5b" and char.isalnum() for char in token)
               else len(re.findall(r"[^\W_]+", token, flags=re.UNICODE)) for token in tokens)


def validate_answer_text(text: str) -> int:
    if len(text) > MAX_ANSWER_CHARACTERS:
        raise HTTPException(422, "คำตอบยาวเกินขนาดที่ระบบรองรับ")
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
    now = now or datetime.now(timezone.utc)
    try:
        start, end = parse_exam_time(exam.get("start_date")), parse_exam_time(exam.get("end_date"))
    except (ValueError, TypeError):
        raise HTTPException(409, "เวลาสอบไม่ถูกต้อง กรุณาติดต่อผู้สอน")
    if start and now < start:
        raise HTTPException(403, "ยังไม่ถึงเวลาเริ่มสอบ")
    if end and now > end + timedelta(seconds=SUBMISSION_GRACE_SECONDS):
        raise HTTPException(403, "เลยกำหนดเวลาส่งคำตอบข้อสอบแล้ว")
