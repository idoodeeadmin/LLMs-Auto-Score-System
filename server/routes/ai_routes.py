"""OpenAI endpoints. The old /api/gemini prefix remains as a compatibility alias."""
import base64
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from server.models import GenerateRubricRequest
from server.utils import get_current_user, get_image_bytes, validate_upload_file
from server.exam_policy import count_answer_words, MAX_ANSWER_WORDS, MAX_ANSWER_CHARACTERS
from server.services.openai_grading import (
    generate_rubric_with_openai, score_with_openai, _get_openai_api_key, OPENAI_MODEL,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["OpenAI"])


@router.post('/generate-rubric')
async def generate_rubric(req: GenerateRubricRequest, user: dict = Depends(get_current_user)):
    if user['role'] != 'teacher':
        raise HTTPException(403, 'Only teachers can generate rubrics')
    if not _get_openai_api_key():
        raise HTTPException(503, 'OpenAI AI is not configured or unavailable')
    if not req.question_text.strip() and not req.question_images_base64:
        raise HTTPException(422, 'กรุณาระบุโจทย์หรือแนบภาพโจทย์')
    images = []
    for image in req.question_images_base64 or []:
        if image.startswith('data:'):
            try:
                header, encoded = image.split(',', 1)
                if not header.endswith(';base64'):
                    raise ValueError('Expected base64 image')
                mime = header[5:].split(';')[0]
                raw = base64.b64decode(encoded, validate=True)
            except (ValueError, TypeError):
                raise HTTPException(422, 'ข้อมูลภาพโจทย์ไม่ถูกต้อง')
        else:
            raw = await get_image_bytes(image)
            if raw:
                validate_upload_file(raw)
                import io
                from PIL import Image
                with Image.open(io.BytesIO(raw)) as loaded:
                    mime = Image.MIME[loaded.format]
        if not raw:
            raise HTTPException(422, 'ไม่สามารถอ่านภาพโจทย์ได้ กรุณาแนบภาพใหม่')
        validate_upload_file(raw, content_type=mime)
        images.append((raw, mime))
    try:
        return await generate_rubric_with_openai(req.question_text, req.total_score, req.tone, images)
    except Exception as error:
        logger.warning('OpenAI rubric generation failed: %s', type(error).__name__)
        raise HTTPException(502, 'สร้างเกณฑ์ด้วย OpenAI ไม่สำเร็จ กรุณาลองใหม่หรือกรอกเกณฑ์ด้วยตนเอง')


class WordCountRequest(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict, max_length=100)


@router.post('/answer-word-count')
async def answer_word_count(req: WordCountRequest, user: dict = Depends(get_current_user)):
    if any(len(text) > MAX_ANSWER_CHARACTERS for text in req.answers.values()):
        raise HTTPException(422, 'คำตอบยาวเกินขนาดที่ระบบรองรับ')
    return {'counts': {key: count_answer_words(text) for key, text in req.answers.items()}, 'limit': MAX_ANSWER_WORDS}


class LiveTestEvalRequest(BaseModel):
    question_text: str = Field(max_length=30000)
    answer_text: str = Field(max_length=MAX_ANSWER_CHARACTERS)
    max_score: float = Field(default=10.0, ge=0, allow_inf_nan=False)
    answer_key: Optional[str] = None
    rubrics: Optional[list[dict]] = None
    image_urls: list[str] = Field(default_factory=list, max_length=10)


@router.post('/test-grade')
async def test_grade_endpoint(req: LiveTestEvalRequest, user: dict = Depends(get_current_user)):
    if user['role'] != 'teacher':
        raise HTTPException(403, 'Only teachers can test AI grading')
    images, mimes = [], []
    for url in req.image_urls:
        raw = await get_image_bytes(url)
        if not raw:
            raise HTTPException(422, 'ไม่สามารถอ่านภาพคำตอบได้')
        validate_upload_file(raw)
        from PIL import Image
        import io
        with Image.open(io.BytesIO(raw)) as image:
            mime = Image.MIME[image.format]
        images.append(raw)
        mimes.append(mime)
    return await score_with_openai(**req.model_dump(exclude={'image_urls'}), image_bytes_list=images, image_mime_list=mimes)


@router.post('/live-test-eval')
async def live_test_eval(req: LiveTestEvalRequest, user: dict = Depends(get_current_user)):
    result = await test_grade_endpoint(req, user)
    return {'success': not result.get('metrics', {}).get('manual_review_required', False),
            'provider': 'openai', 'model': OPENAI_MODEL, 'result': result}


legacy_router = APIRouter(prefix="/api/gemini", include_in_schema=False)
legacy_router.add_api_route('/generate-rubric', generate_rubric, methods=['POST'])
legacy_router.add_api_route('/test-grade', test_grade_endpoint, methods=['POST'])
legacy_router.add_api_route('/live-test-eval', live_test_eval, methods=['POST'])
