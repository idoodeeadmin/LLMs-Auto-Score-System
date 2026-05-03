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
from server.utils import check_rate_limit, upload_to_cloudinary, get_current_user, log_audit_action, grading_queue, trigger_socket_notify

router = APIRouter(prefix="/api/question-bank", tags=["Question Bank Routes"])

@router.get('')
async def list_question_bank(user: dict=Depends(get_current_user)):
    """Teacher lists their own question bank."""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Teachers only')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM question_bank WHERE owner_id = ? ORDER BY created_at DESC', (user['id'],))
    items = cursor.fetchall()
    conn.close()
    result = []
    for item in items:
        d = dict(item)
        if d.get('rubrics'):
            try:
                d['rubrics'] = json.loads(d['rubrics'])
            except Exception:
                d['rubrics'] = []
        result.append(d)
    return result

@router.post('')
async def create_question_bank(body: QuestionBankCreate, user: dict=Depends(get_current_user)):
    """Teacher adds a question to their bank."""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Teachers only')
    conn = get_db_connection()
    cursor = conn.cursor()
    rubrics_json = json.dumps(body.rubrics, ensure_ascii=False) if body.rubrics else None
    cursor.execute('INSERT INTO question_bank (owner_id, text, score, answer_key, rubrics, tags) VALUES (?, ?, ?, ?, ?, ?)', (user['id'], body.text, body.score, body.answer_key, rubrics_json, body.tags))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {'id': new_id, 'message': 'Question saved to bank'}

@router.delete('/{question_id}')
async def delete_question_bank(question_id: int, user: dict=Depends(get_current_user)):
    """Teacher deletes a question from their bank."""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Teachers only')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM question_bank WHERE id = ? AND owner_id = ?', (question_id, user['id']))
    conn.commit()
    conn.close()
    return {'message': 'Deleted'}

@router.post('/save-from-exam')
async def save_questions_from_exam(room_id: int, exam_id: int, user: dict=Depends(get_current_user)):
    """Teacher saves all questions from an exam into their question bank."""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Teachers only')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM rooms WHERE id = ? AND owner_id = ?', (room_id, user['id']))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail='Unauthorized')
    cursor.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,))
    questions = cursor.fetchall()
    saved = 0
    for q in questions:
        cursor.execute('INSERT INTO question_bank (owner_id, text, score, answer_key, rubrics, tags) VALUES (?, ?, ?, ?, ?, ?)', (user['id'], q['text'], q['score'], q['answer_key'], q['rubrics'], None))
        saved += 1
    conn.commit()
    conn.close()
    return {'message': f'บันทึก {saved} ข้อลงคลังเรียบร้อยแล้ว', 'saved': saved}

