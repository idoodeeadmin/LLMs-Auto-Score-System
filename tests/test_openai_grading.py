import asyncio
from unittest.mock import AsyncMock

import pytest

from server.services import openai_grading


class _FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "output": [{"content": [{"type": "output_text", "text": '{"score":4.5,"confidence":"high","feedback":"คำตอบถูกต้อง","transcription":"LIFO"}'}]}]
        }


class _FakeClient:
    def __init__(self, captured):
        self.captured = captured

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def post(self, url, **kwargs):
        self.captured.update(url=url, **kwargs)
        return _FakeResponse()


def test_grading_uses_luna_responses_api_and_structured_output(monkeypatch):
    captured = {}
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setattr(openai_grading.httpx, "AsyncClient", lambda **_kwargs: _FakeClient(captured))

    result = asyncio.run(openai_grading.score_with_openai(
        question_text="อธิบาย Stack", answer_text="ทำงานแบบ LIFO", max_score=5,
        answer_key="LIFO", rubrics=[{"name": "ความถูกต้อง", "score": 5}],
        image_bytes_list=[b"student-image"], image_mime_list=["image/png"],
    ))

    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["json"]["model"] == "gpt-5.6-luna"
    assert captured["json"]["store"] is False
    assert captured["json"]["text"]["format"]["type"] == "json_schema"
    assert any(part["type"] == "input_image" for part in captured["json"]["input"][0]["content"])
    assert result["score"] == 4.5
    assert result["confidence"] == "high"
    assert result["transcription"] == "LIFO"
    assert result["metrics"]["provider"] == "openai"


def test_grading_falls_back_to_manual_review_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="โจทย์", answer_text="คำตอบ", max_score=10,
    ))
    assert result["score"] == 0
    assert result["confidence"] == "low"
    assert "อาจารย์ผู้สอน" in result["feedback"]


@pytest.mark.parametrize("confidence,requires_review", [
    ("high", False), ("medium", True), ("low", True),
])
def test_grading_review_flag_includes_medium_confidence(confidence, requires_review):
    transport = AsyncMock(return_value={
        "score": 1, "confidence": confidence,
        "teacher_feedback": "ตรวจคำตอบแล้ว", "student_feedback": "คำแนะนำ",
        "transcription": "",
    })
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="อธิบาย Stack", answer_text="LIFO", max_score=1,
        _api_key_available=True, _transport=transport,
    ))
    assert result["metrics"]["manual_review_required"] is requires_review


def test_image_prompt_separates_legibility_from_score():
    transport = AsyncMock(return_value={
        "score": 0.5, "confidence": "medium",
        "teacher_feedback": "ตัวเลขท้ายบรรทัดอ่านไม่ชัด ควรตรวจต้นฉบับซ้ำ",
        "student_feedback": "ตรวจคำตอบแล้ว", "transcription": "ผลคือ [อ่านไม่ชัด]",
    })
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="โจทย์", answer_text="", max_score=1,
        image_bytes_list=[b"student-image"], image_mime_list=["image/png"],
        _api_key_available=True, _transport=transport,
    ))
    prompt = transport.await_args.args[0][0]["text"]
    assert "[อ่านไม่ชัด]" in prompt
    assert "แยกจากความมั่นใจในการตัดสินคะแนน" in prompt
    assert "ห้ามยกระดับ confidence เพราะคำตอบดูถูกหลักวิชา" in prompt
    assert "หากข้อความหรือภาพตีความได้มากกว่าหนึ่งทาง" in prompt
    assert result["metrics"]["manual_review_required"] is True


def test_text_prompt_lowers_confidence_when_score_is_ambiguous():
    transport = AsyncMock(return_value={
        "score": 1.0, "confidence": "medium",
        "teacher_feedback": "ตีความได้สองทาง อาจได้ 1 หรือ 2 คะแนน",
        "student_feedback": "อธิบายเหตุผลให้ชัดเจนขึ้น", "transcription": "",
    })
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="อธิบายเหตุผล", answer_text="ตอบกำกวม", max_score=2,
        _api_key_available=True, _transport=transport,
    ))
    prompt = transport.await_args.args[0][0]["text"]
    assert 'grading_uncertainty เป็น "borderline" และ confidence เป็น "medium" ทันที' in prompt
    assert 'grading_uncertainty เป็น "insufficient_evidence" และ confidence เป็น "low"' in prompt
    assert "grading_uncertainty" in transport.await_args.args[1]["required"]
    assert "คำตอบผิดหรือไม่ครบอย่างชัดเจน" in prompt
    assert result["metrics"]["manual_review_required"] is True


def test_clear_image_with_ambiguous_score_does_not_claim_image_is_blurry():
    transport = AsyncMock(return_value={
        "score": 1.0, "confidence": "medium", "handwriting_status": "clear",
        "teacher_feedback": "ตีความได้สองทาง อาจได้ 1 หรือ 2 คะแนน",
        "student_feedback": "อธิบายเหตุผลให้ชัดเจนขึ้น", "transcription": "ตอบชัดเจน",
    })
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="อธิบายเหตุผล", answer_text="", max_score=2,
        image_bytes_list=[b"student-image"], image_mime_list=["image/png"],
        _api_key_available=True, _transport=transport,
    ))
    assert result["confidence"] == "medium"
    assert result["metrics"]["manual_review_required"] is True
    assert "การตัดสินคะแนนตามเกณฑ์ยังไม่แน่ชัด" in result["teacher_feedback"]
    assert "ลายมือหรือรูปภาพมีความชัดเจนน้อย" not in result["teacher_feedback"]


@pytest.mark.parametrize("uncertainty,expected", [
    ("clear", "high"), ("borderline", "medium"),
    ("insufficient_evidence", "low"),
])
def test_grading_uncertainty_caps_confidence(uncertainty, expected):
    transport = AsyncMock(return_value={
        "score": 1.0, "confidence": "high", "grading_uncertainty": uncertainty,
        "teacher_feedback": "ตรวจตามเกณฑ์แล้ว", "student_feedback": "คำแนะนำ",
        "transcription": "",
    })
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="โจทย์", answer_text="คำตอบ", max_score=2,
        _api_key_available=True, _transport=transport,
    ))
    assert result["confidence"] == expected
    assert result["metrics"]["manual_review_required"] is (expected != "high")
    if expected != "high":
        assert "การตัดสินคะแนนตามเกณฑ์ยังไม่แน่ชัด" in result["teacher_feedback"]


def test_unreadable_marker_prevents_high_confidence():
    transport = AsyncMock(return_value={
        "score": 0.5, "confidence": "high", "teacher_feedback": "ตรวจคำตอบแล้ว",
        "student_feedback": "คำแนะนำ", "transcription": "คำตอบ [อ่านไม่ชัด]",
    })
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="โจทย์", answer_text="", max_score=1,
        image_bytes_list=[b"student-image"], image_mime_list=["image/png"],
        _api_key_available=True, _transport=transport,
    ))
    assert result["confidence"] == "medium"
    assert result["metrics"]["manual_review_required"] is True
    assert "ตรวจภาพต้นฉบับ" in result["teacher_feedback"]


def test_pure_text_answer_does_not_double_count_transcription():
    # 200 words text (using single-segment word 'ตอบ')
    answer = "ตอบ " * 200
    # Simulate LLM echoing answer into transcription when no images exist
    transport = AsyncMock(return_value={
        "score": 5, "confidence": "high", "teacher_feedback": "ตรวจคำตอบแล้ว",
        "student_feedback": "คำแนะนำ", "transcription": answer,
    })
    result = asyncio.run(openai_grading.score_with_openai(
        question_text="โจทย์", answer_text=answer, max_score=5,
        image_bytes_list=None, image_mime_list=None,
        _api_key_available=True, _transport=transport,
    ))
    assert result["metrics"]["word_limit_exceeded"] is False
    assert result["metrics"]["answer_word_count"] == 200
    assert "เกิน 300 คำ" not in result["teacher_feedback"]
