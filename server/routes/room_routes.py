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
from server.utils import check_rate_limit, upload_to_cloudinary, get_current_user, grading_queue, trigger_socket_notify, generate_class_code, _distribution_buckets
import statistics
router = APIRouter(prefix='/api/rooms', tags=['Room Routes'])

@router.post('')
async def create_room(room: RoomCreate, user: dict=Depends(get_current_user)):
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can create rooms')
    conn = get_db_connection()
    cursor = conn.cursor()
    class_code = generate_class_code()
    try:
        cursor.execute('INSERT INTO rooms (name, section, class_code, teacher_id) VALUES (?, ?, ?, ?)', (room.name, room.section, class_code, user['id']))
        conn.commit()
        new_room_id = cursor.lastrowid
    except pymysql.err.IntegrityError:
        conn.close()
        raise HTTPException(status_code=500, detail='Failed to generate unique class code. Try again.')
    cursor.execute('SELECT * FROM rooms WHERE id = ?', (new_room_id,))
    new_room = dict(cursor.fetchone())
    conn.close()
    return new_room

@router.get('')
async def get_rooms(user: dict=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if user['role'] == 'teacher':
        cursor.execute('SELECT * FROM rooms WHERE teacher_id = ?', (user['id'],))
        rooms = cursor.fetchall()
    else:
        cursor.execute('\n            SELECT r.* FROM rooms r\n            JOIN enrollments e ON r.id = e.room_id\n            WHERE e.user_id = ?\n        ', (user['id'],))
        rooms = cursor.fetchall()
    conn.close()
    return [dict(room) for room in rooms]

@router.put('/{room_id}')
async def update_room(room_id: int, room_data: RoomCreate, user: dict=Depends(get_current_user)):
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can edit rooms')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    existing_room = cursor.fetchone()
    if not existing_room:
        conn.close()
        raise HTTPException(status_code=404, detail='Room not found or unauthorized')
    cursor.execute('UPDATE rooms SET name = ?, section = ? WHERE id = ?', (room_data.name, room_data.section, room_id))
    conn.commit()
    conn.close()
    return {'message': 'Room updated successfully'}

@router.delete('/{room_id}')
async def delete_room(request: Request, room_id: int, user: dict=Depends(get_current_user)):
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can delete rooms')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail='Room not found or unauthorized')
    cursor.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
    conn.commit()
    conn.close()
    return {'message': 'Room deleted successfully'}

@router.post('/join')
async def join_room(request: JoinRoomRequest, user: dict=Depends(get_current_user)):
    if user['role'] != 'student':
        raise HTTPException(status_code=403, detail='Only students can join rooms')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM rooms WHERE class_code = ?', (request.class_code.upper(),))
    room = cursor.fetchone()
    if not room:
        conn.close()
        raise HTTPException(status_code=404, detail='รหัสห้องไม่ถูกต้อง (Invalid class code)')
    room_id = room['id']
    cursor.execute('SELECT id FROM enrollments WHERE user_id = ? AND room_id = ?', (user['id'], room_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail='คุณอยู่ในห้องนี้แล้ว (Already joined)')
    cursor.execute('INSERT INTO enrollments (user_id, room_id) VALUES (?, ?)', (user['id'], room_id))
    conn.commit()
    cursor.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
    joined_room = dict(cursor.fetchone())
    conn.close()
    return joined_room

@router.get('/{room_id}')
async def get_room(room_id: int, user: dict=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if user['role'] == 'teacher':
        cursor.execute('SELECT * FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    else:
        cursor.execute('\n            SELECT r.* FROM rooms r\n            JOIN enrollments e ON r.id = e.room_id\n            WHERE r.id = ? AND e.user_id = ?\n        ', (room_id, user['id']))
    room = cursor.fetchone()
    conn.close()
    if not room:
        raise HTTPException(status_code=404, detail='Room not found or unauthorized')
    return dict(room)

@router.get('/{room_id}/members')
async def get_room_members(room_id: int, user: dict=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if user['role'] == 'teacher':
        cursor.execute('SELECT id FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    else:
        cursor.execute('SELECT room_id FROM enrollments WHERE room_id = ? AND user_id = ?', (room_id, user['id']))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail='Unauthorized')
    cursor.execute('SELECT u.id, u.name, u.email, u.student_id FROM users u JOIN rooms r ON u.id = r.teacher_id WHERE r.id = ?', (room_id,))
    teacher_row = cursor.fetchone()
    teacher = {**dict(teacher_row), 'role': 'teacher', 'joined_at': None} if teacher_row else None
    cursor.execute('\n        SELECT u.id, u.name, u.email, u.student_id, e.joined_at\n        FROM users u\n        JOIN enrollments e ON u.id = e.user_id\n        WHERE e.room_id = ?\n        ORDER BY e.joined_at DESC\n    ', (room_id,))
    members = cursor.fetchall()
    conn.close()
    result = []
    if teacher:
        result.append({**teacher, 'role': 'teacher'})
    for m in members:
        result.append({**dict(m), 'role': 'student'})
    return result

@router.post('/{room_id}/announcements')
async def create_announcement(room_id: int, ann: AnnouncementCreate, user: dict=Depends(get_current_user)):
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can create announcements')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail='Room not found or unauthorized')
    cursor.execute('INSERT INTO announcements (room_id, teacher_id, title, content) VALUES (?, ?, ?, ?)', (room_id, user['id'], ann.title, ann.content))
    ann_id = cursor.lastrowid
    conn.commit()
    cursor.execute('SELECT user_id FROM enrollments WHERE room_id = ?', (room_id,))
    students = cursor.fetchall()
    for s in students:
        await trigger_socket_notify(user_id=s['user_id'], notify_type='new_announcement', message=f'มีประกาศใหม่ในห้องเรียน: {ann.title}', data={'room_id': room_id, 'announcement_id': ann_id})
    conn.close()
    return {'id': ann_id, 'message': 'Announcement created successfully'}

@router.get('/{room_id}/announcements')
async def list_announcements(room_id: int, user: dict=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if user['role'] == 'teacher':
        cursor.execute('SELECT id FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    else:
        cursor.execute('SELECT room_id FROM enrollments WHERE room_id = ? AND user_id = ?', (room_id, user['id']))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail='Unauthorized')
    if user['role'] == 'student':
        cursor.execute('\n            SELECT a.*, (SELECT 1 FROM announcement_reads ar WHERE ar.announcement_id = a.id AND ar.user_id = ?) as is_read\n            FROM announcements a\n            WHERE a.room_id = ?\n            ORDER BY a.created_at DESC\n        ', (user['id'], room_id))
    else:
        cursor.execute('\n            SELECT a.*, (SELECT COUNT(*) FROM announcement_reads ar WHERE ar.announcement_id = a.id) as read_count\n            FROM announcements a\n            WHERE a.room_id = ?\n            ORDER BY a.created_at DESC\n        ', (room_id,))
    anns = cursor.fetchall()
    conn.close()
    return [dict(a) for a in anns]

@router.get('/{room_id}/export-summary-csv')
async def export_room_summary_csv(room_id: int, user: dict=Depends(get_current_user)):
    """Teacher exports overall room summary (all exams) to CSV"""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can export summary')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    room_row = cursor.fetchone()
    if not room_row:
        conn.close()
        raise HTTPException(status_code=403, detail='Unauthorized')
    room_name = room_row['name']
    cursor.execute('SELECT id, title, total_score FROM exams WHERE room_id = ? ORDER BY created_at ASC', (room_id,))
    exams = cursor.fetchall()
    exam_ids = [e['id'] for e in exams]
    exam_titles = [e['title'] for e in exams]
    cursor.execute('\n        SELECT u.id, u.name, u.email, u.student_id\n        FROM enrollments e\n        JOIN users u ON e.user_id = u.id\n        WHERE e.room_id = ?\n        ORDER BY u.name ASC\n    ', (room_id,))
    students = cursor.fetchall()
    cursor.execute('\n        SELECT exam_id, user_id, total_score\n        FROM submissions\n        WHERE exam_id IN (SELECT id FROM exams WHERE room_id = ?)\n    ', (room_id,))
    submissions_list = cursor.fetchall()
    scores_map = {}
    for sub in submissions_list:
        sid = sub['user_id']
        eid = sub['exam_id']
        if sid not in scores_map:
            scores_map[sid] = {}
        scores_map[sid][eid] = sub['total_score']
    conn.close()
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Name'] + exam_titles + ['Total Cumulative Score'])
    for s in students:
        row = [s['user_id'], s['name']]
        cumulative_total = 0
        for eid in exam_ids:
            score = scores_map.get(s['id'], {}).get(eid, 0)
            row.append(score)
            cumulative_total += score or 0
        row.append(cumulative_total)
        writer.writerow(row)
    content = output.getvalue()
    filename = f"Summary_{room_name.replace(' ', '_')}.csv"
    return StreamingResponse(iter([content]), media_type='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}'})

@router.get('/{room_id}/analytics')
async def get_room_analytics(room_id: int, user: dict=Depends(get_current_user)):
    """Teacher room-level analytics across all exams."""
    if user['role'] != 'teacher':
        raise HTTPException(status_code=403, detail='Only teachers can view analytics')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, teacher_id FROM rooms WHERE id = ?', (room_id,))
    room = cursor.fetchone()
    if not room:
        conn.close()
        raise HTTPException(status_code=404, detail='Room not found')
    if str(room['teacher_id']) != str(user['id']):
        conn.close()
        raise HTTPException(status_code=403, detail=f"Unauthorized: owner={room['teacher_id']} != user={user['id']}")
    cursor.execute("\n        SELECT\n            e.id,\n            e.title,\n            e.total_score,\n            COUNT(CASE WHEN s.status IS NOT NULL AND s.status != 'missing' THEN 1 END) AS submitted_count,\n            COUNT(CASE WHEN s.status = 'approved' THEN 1 END) AS approved_count,\n            AVG(CASE WHEN s.status = 'approved' THEN s.total_score ELSE NULL END) AS approved_mean\n        FROM exams e\n        LEFT JOIN submissions s ON s.exam_id = e.id\n        WHERE e.room_id = ?\n        GROUP BY e.id, e.title, e.total_score\n        ORDER BY e.created_at DESC\n    ", (room_id,))
    exams = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) AS total_students FROM enrollments WHERE room_id = ?', (room_id,))
    total_students = int(cursor.fetchone()['total_students'] or 0)
    cursor.execute("\n        SELECT s.total_score, e.total_score AS exam_total_score\n        FROM submissions s\n        JOIN exams e ON e.id = s.exam_id\n        WHERE e.room_id = ? AND s.status = 'approved'\n    ", (room_id,))
    room_approved_score_rows = cursor.fetchall()
    room_approved_scores = [float(r['total_score'] or 0) for r in room_approved_score_rows]
    room_approved_percents = []
    for r in room_approved_score_rows:
        exam_total = float(r['exam_total_score'] or 0)
        score = float(r['total_score'] or 0)
        pct = score / exam_total * 100.0 if exam_total > 0 else 0.0
        room_approved_percents.append(max(0.0, min(100.0, pct)))
    conn.close()
    exam_summaries = []
    for e in exams:
        submitted_count = int(e['submitted_count'] or 0)
        approved_count = int(e['approved_count'] or 0)
        total_score = float(e['total_score'] or 0)
        approved_mean = round(float(e['approved_mean'] or 0), 2)
        submission_rate = round(submitted_count / total_students * 100.0, 2) if total_students > 0 else 0.0
        mean_percent = round(approved_mean / total_score * 100.0, 2) if total_score > 0 else 0.0
        exam_summaries.append({'exam_id': e['id'], 'title': e['title'], 'total_score': total_score, 'submitted_count': submitted_count, 'approved_count': approved_count, 'approved_mean': approved_mean, 'missing_count': max(0, total_students - submitted_count), 'submission_rate': submission_rate, 'mean_percent': mean_percent})
    return {'total_students': total_students, 'exam_count': len(exam_summaries), 'overall_mean_score': round(statistics.mean(room_approved_scores), 2) if room_approved_scores else 0.0, 'overall_median_score': round(statistics.median(room_approved_scores), 2) if room_approved_scores else 0.0, 'overall_distribution': _distribution_buckets(room_approved_percents, 100.0), 'exam_summaries': exam_summaries}