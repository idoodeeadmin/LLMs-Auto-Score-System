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

router = APIRouter(prefix="/api/notifications", tags=["Notification Routes"])

@router.get('')
async def get_notifications(user: dict=Depends(get_current_user)):
    """Return notifications for teachers and students."""
    from datetime import datetime, timezone, timedelta
    conn = get_db_connection()
    cursor = conn.cursor()
    now_utc = datetime.now(timezone.utc)
    notifications = []
    
    # Fetch from database (historical notifications)
    try:
        cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 50", (user['id'],))
        db_notifs = cursor.fetchall()
        for row in db_notifs:
            notif = {
                'id': row['id'],
                'type': row['type'],
                'message': row['message'],
                'link': row['link'],
                'is_read': bool(row['is_read']),
                'created_at': row['created_at'].isoformat() if row['created_at'] else None
            }
            if row.get('data'):
                try:
                    notif['data'] = json.loads(row['data'])
                except:
                    pass
            notifications.append(notif)
    except Exception as e:
        print(f"[Notifications] DB fetch error: {e}")

    if user['role'] == 'teacher':
        cursor.execute('\n            SELECT e.id AS exam_id, e.title AS exam_title, e.end_date,\n                   r.id AS room_id, r.name AS room_name\n            FROM exams e\n            JOIN rooms r ON e.room_id = r.id\n            WHERE r.teacher_id = ?\n            ', (user['id'],))
        exams = cursor.fetchall()
        for exam in exams:
            exam_id = exam['exam_id']
            exam_title = exam['exam_title']
            room_id = exam['room_id']
            room_name = exam['room_name']
            end_date_str = exam['end_date']
            deadline_passed = False
            if end_date_str:
                try:
                    deadline = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    if deadline.tzinfo is None:
                        deadline = deadline.replace(tzinfo=timezone.utc)
                    if now_utc > deadline:
                        deadline_passed = True
                except (ValueError, TypeError):
                    pass
            cursor.execute("\n                SELECT\n                    COUNT(*) AS total_submitted,\n                    SUM(CASE WHEN status IN ('ready','needs_review') THEN 1 ELSE 0 END) AS pending_review,\n                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved_count\n                FROM submissions WHERE exam_id = ?\n                ", (exam_id,))
            row = cursor.fetchone()
            total_submitted = row['total_submitted'] or 0
            pending_review = row['pending_review'] or 0
            approved_count = row['approved_count'] or 0
            if deadline_passed and pending_review > 0:
                notifications.append({'type': 'deadline_passed', 'exam_id': exam_id, 'exam_title': exam_title, 'room_id': room_id, 'room_name': room_name, 'message': f'[{room_name}] ชุดข้อสอบ "{exam_title}" หมดเวลาส่งแล้ว มีนักศึกษาส่งคำตอบ {total_submitted} คน รอตรวจ {pending_review} คน', 'link': f'/room/{room_id}/exam/{exam_id}/review'})
            if pending_review > 0:
                notifications.append({'type': 'ai_graded', 'exam_id': exam_id, 'exam_title': exam_title, 'room_id': room_id, 'room_name': room_name, 'message': f'[{room_name}] AI ประเมินผล "{exam_title}" เสร็จแล้ว รอการอนุมัติจากอาจารย์ {pending_review} คน (อนุมัติแล้ว {approved_count}/{total_submitted} คน)', 'link': f'/room/{room_id}/exam/{exam_id}/review'})
    else:
        student_id = user['id']
        cursor.execute('\n            SELECT e.id AS exam_id, e.title AS exam_title,\n                   e.start_date, e.end_date,\n                   r.id AS room_id, r.name AS room_name\n            FROM exams e\n            JOIN rooms r ON e.room_id = r.id\n            JOIN enrollments en ON en.room_id = r.id\n            WHERE en.user_id = ?\n            ', (student_id,))
        exams = cursor.fetchall()
        for exam in exams:
            exam_id = exam['exam_id']
            exam_title = exam['exam_title']
            room_id = exam['room_id']
            room_name = exam['room_name']
            start_str = exam['start_date']
            end_str = exam['end_date']
            start_dt = end_dt = None
            try:
                if start_str:
                    start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=timezone.utc)
                if end_str:
                    end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                    if end_dt.tzinfo is None:
                        end_dt = end_dt.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass
            cursor.execute('SELECT id, status FROM submissions WHERE exam_id = ? AND user_id = ?', (exam_id, student_id))
            submission = cursor.fetchone()
            has_submitted = submission is not None
            sub_status = submission['status'] if submission else None
            exam_open = (start_dt is None or now_utc >= start_dt) and (end_dt is None or now_utc <= end_dt)
            if exam_open and (not has_submitted):
                notifications.append({'type': 'new_exam', 'exam_id': exam_id, 'exam_title': exam_title, 'room_id': room_id, 'room_name': room_name, 'message': f'[{room_name}] มีข้อสอบใหม่ "{exam_title}" เปิดรับการส่งแล้ว!', 'link': f'/room/{room_id}/exam/{exam_id}'})
            if exam_open and (not has_submitted) and end_dt:
                time_left = end_dt - now_utc
                if timedelta(0) < time_left < timedelta(hours=24):
                    hours_left = int(time_left.total_seconds() // 3600)
                    mins_left = int(time_left.total_seconds() % 3600 // 60)
                    time_str = f'{hours_left} ชั่วโมง {mins_left} นาที' if hours_left > 0 else f'{mins_left} นาที'
                    notifications.append({'type': 'deadline_soon', 'exam_id': exam_id, 'exam_title': exam_title, 'room_id': room_id, 'room_name': room_name, 'message': f'[{room_name}] "{exam_title}" ใกล้หมดเวลา! เหลืออีก {time_str}', 'link': f'/room/{room_id}/exam/{exam_id}'})
            if has_submitted and sub_status == 'approved':
                notifications.append({'type': 'result_published', 'exam_id': exam_id, 'exam_title': exam_title, 'room_id': room_id, 'room_name': room_name, 'message': f'[{room_name}] อาจารย์ประกาศผล "{exam_title}" แล้ว กดเพื่อดูคะแนนของคุณ', 'link': f'/room/{room_id}/exam/{exam_id}'})
    conn.close()
    return notifications

