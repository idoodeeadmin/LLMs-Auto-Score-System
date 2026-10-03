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
