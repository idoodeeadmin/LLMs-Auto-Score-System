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
from server.utils import check_rate_limit, upload_to_cloudinary, get_current_user, grading_queue, trigger_socket_notify

router = APIRouter(prefix="", tags=["System Routes"])

@router.post('/api/announcements/{ann_id}/read')
async def mark_announcement_read(ann_id: int, user: dict=Depends(get_current_user)):
    if user['role'] != 'student':
        return {'message': 'Only students need read receipts'}
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO announcement_reads (announcement_id, user_id) VALUES (?, ?) ON DUPLICATE KEY UPDATE user_id=user_id', (ann_id, user['id']))
        conn.commit()
    except Exception as e:
        print(f'Error marking announcement read: {e}')
    conn.close()
    return {'message': 'Marked as read'}

@router.get('/api/announcements/{ann_id}/read-status')
async def get_announcement_read_status(ann_id: int, user: dict=Depends(get_current_user)):
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can view read status')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT room_id FROM announcements WHERE id = ?', (ann_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail='Announcement not found')
    room_id = row['room_id']
    cursor.execute('SELECT id FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail='Unauthorized')
    cursor.execute('\n        SELECT u.id, u.name, u.student_id, ar.read_at\n        FROM enrollments e\n        JOIN users u ON e.user_id = u.id\n        LEFT JOIN announcement_reads ar ON ar.announcement_id = ? AND ar.user_id = u.id\n        WHERE e.room_id = ?\n    ', (ann_id, room_id))
    status = cursor.fetchall()
    conn.close()
    return [dict(s) for s in status]

@router.get('/api/submissions/me')
async def get_all_my_submissions(user: dict=Depends(get_current_user)):
    """Student views all their submissions across all exams and rooms."""
    if user['role'] != 'student':
        raise HTTPException(status_code=403, detail='Only students can view their submission history')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("\n        SELECT\n            e.id AS exam_id, e.title AS exam_title, e.total_score AS exam_total_score,\n            r.id AS room_id, r.name AS room_name,\n            s.id AS submission_id, COALESCE(s.status, 'missing') AS status, \n            s.total_score AS submission_score, s.submitted_at\n        FROM enrollments en\n        JOIN rooms r ON en.room_id = r.id\n        JOIN exams e ON e.room_id = r.id\n        LEFT JOIN submissions s ON s.exam_id = e.id AND s.user_id = en.user_id\n        WHERE en.user_id = ?\n        ORDER BY COALESCE(s.submitted_at, e.created_at) DESC\n    ", (user['id'],))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

@router.get('/api/ping')
async def ping():
    return {'message': 'pong'}

