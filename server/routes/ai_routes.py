from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File, Form, Request, Query, BackgroundTasks
from fastapi.responses import Response, StreamingResponse
import pymysql
import json
import csv
import io
import time
import asyncio
from typing import Optional, List

from server.database import get_db_connection
from server.auth import get_password_hash, verify_password, create_access_token, decode_token
from server.models import *
from server.services.ai_service import _USE_GEMINI, _genai_client, _GEMINI_MODEL
from server.utils import check_rate_limit, upload_to_cloudinary, get_current_user, log_audit_action, grading_queue, trigger_socket_notify, get_image_bytes
from google.genai import types as genai_types

router = APIRouter(prefix="/api/gemini", tags=["Ai Routes"])

@router.post('/generate-rubric')
async def generate_rubric(req: GenerateRubricRequest, user: dict=Depends(get_current_user)):
    """Generate Answer Key and Rubrics automatically based on question and total score."""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can generate rubrics')
    if not _USE_GEMINI or not _genai_client:
        raise HTTPException(status_code=503, detail='Gemini AI is not configured or unavailable')
    tone_instruction = ''
    if req.tone == 'simple':
        tone_instruction = 'เน้นความถูกต้องของคำตอบเป็นหลัก ไม่แบ่งเกณฑ์ย่อยเยอะ ขอแค่คำตอบถูกต้องตามประเด็นสำคัญก็ได้คะแนนเต็มทันที เหมาะสำหรับการตรวจแบบรวดเร็วที่เน้นผลลัพธ์'
    elif req.tone == 'academic':
        tone_instruction = 'ใช้ภาษาเชิงวิชาการอย่างเป็นทางการ มีความละเอียดและแม่นยำสูง เน้นความถูกต้องทางเทคนิคและหลักการที่สมบูรณ์'
    else:
        tone_instruction = 'ใช้ภาษาที่เป็นกลาง มีความชัดเจนและครอบคลุมประเด็นสำคัญอย่างสมดุล'
    prompt = f'\n    You are an expert exam setter and grader.\n    Given the following question (text and/or images) and its maximum score, generate a comprehensive "Answer Key" (ธงคำตอบ)\n    and a detailed "Rubrics" (เกณฑ์การให้คะแนน) broken down into specific criteria.\n    The total score of all rubrics MUST equal exactly {req.total_score}.\n    \n    TONE/LEVEL: {req.tone.upper()}\n    Instruction for tone: {tone_instruction}\n    \n    If question text is empty, look at the attached images to understand the question.\n    \n    Output MUST be valid JSON matching this schema:\n    {{\n        "answer_key": "String (detailed correct answer model in Thai)",\n        "rubrics": [\n            {{\n                "name": "String (short criteria name, e.g. ความถูกต้อง, การอธิบาย, โครงสร้างโค้ด)",\n                "description": "String (what is expected to get this score)",\n                "score": Number (float or int)\n            }}\n        ]\n    }}\n    \n    Question Text: {req.question_text}\n    Total Score: {req.total_score}\n    '
    try:
        import base64, re as _re
        contents: list = [prompt]
        if req.question_images_base64:
            for img_data in req.question_images_base64:
                try:
                    if img_data.startswith('data:'):
                        match = _re.match('data:(?P<mime>[^;]+);base64,(?P<data>.+)', img_data)
                        if match:
                            mime = match.group('mime')
                            data = base64.b64decode(match.group('data'))
                            contents.append(genai_types.Part.from_bytes(data=data, mime_type=mime))
                    else:
                        data = await get_image_bytes(img_data)
                        if data:
                            ext = img_data.split('.')[-1].lower()
                            mime = 'image/png' if ext == 'png' else 'image/webp' if ext == 'webp' else 'image/jpeg'
                            contents.append(genai_types.Part.from_bytes(data=data, mime_type=mime))
                except Exception as e:
                    print(f'[Generate Rubric Image Error] {e}')
                    continue
        response = _genai_client.models.generate_content(model=_GEMINI_MODEL, contents=contents, config=genai_types.GenerateContentConfig(response_mime_type='application/json'))
        result_text = response.text
        if result_text.startswith('```json'):
            result_text = result_text.strip('```json').strip('```').strip()
        elif result_text.startswith('```'):
            result_text = result_text.strip('```').strip()
        data = json.loads(result_text)
        return data
    except Exception as e:
        print(f'[Gemini Error in Generate Rubric]: {e}')
        raise HTTPException(status_code=500, detail='Failed to generate rubric via AI')

