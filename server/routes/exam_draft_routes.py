import base64
import json

from fastapi import APIRouter, Depends, HTTPException

from server.database import get_db_connection
from server.models import ExamDraftSave
from server.utils import get_current_user, upload_to_cloudinary, validate_upload_file


router = APIRouter(prefix='/api/rooms/{room_id}/exam-drafts', tags=['Exam drafts'])


def require_room_teacher(cursor, room_id, user):
    if user.get('role') != 'teacher':
        raise HTTPException(403, 'Only teachers can manage exam drafts')
    cursor.execute('SELECT id FROM rooms WHERE id = ? AND teacher_id = ?', (room_id, user['id']))
    if not cursor.fetchone():
        raise HTTPException(404, 'Room not found or unauthorized')


def draft_images(questions_json):
    allowed = set()
    try:
        for question in json.loads(questions_json or '[]'):
            allowed.update(question.get('question_images_base64') or [])
    except (TypeError, json.JSONDecodeError):
        pass
    return allowed


def persist_images(images, teacher_id, draft_id, allowed):
    paths = []
    for image in images or []:
        if image in allowed:
            paths.append(image)
            continue
        try:
            header, encoded = image.split(',', 1)
            if not header.startswith('data:') or not header.endswith(';base64'):
                raise ValueError
            mime = header[5:].split(';')[0]
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError):
            raise HTTPException(422, 'ภาพโจทย์ไม่ถูกต้อง กรุณาแนบภาพใหม่')
        validate_upload_file(raw, content_type=mime)
        url = upload_to_cloudinary(raw, folder=f'exam-drafts/{teacher_id}/{draft_id}')
        if not url:
            raise HTTPException(502, 'บันทึกภาพโจทย์ไม่สำเร็จ')
        paths.append(url)
    return paths


def normalized_questions(payload, teacher_id, draft_id, allowed=()):
    result = []
    for question in payload.questions:
        result.append({
            'text': question.text,
            'score': question.score,
            'answer_key': question.answer_key,
            'rubrics': question.rubrics or [],
            'order_index': question.order_index,
            'question_images_base64': persist_images(question.question_images_base64, teacher_id, draft_id, allowed),
        })
    return result


def serialize(row):
    item = dict(row)
    try:
        item['questions'] = json.loads(item.get('questions') or '[]')
    except (TypeError, json.JSONDecodeError):
        item['questions'] = []
    return item


@router.get('')
def list_drafts(room_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        require_room_teacher(cursor, room_id, user)
        cursor.execute('''SELECT id, title, description, start_date, end_date, is_randomized, questions, created_at, updated_at
                          FROM exam_drafts WHERE room_id = ? AND teacher_id = ?
                          ORDER BY updated_at DESC, id DESC''', (room_id, user['id']))
        return [serialize(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@router.post('', status_code=201)
def create_draft(room_id: int, payload: ExamDraftSave, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        require_room_teacher(cursor, room_id, user)
        cursor.execute('''INSERT INTO exam_drafts
                          (room_id, teacher_id, title, description, start_date, end_date, is_randomized, questions)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (room_id, user['id'], payload.title, payload.description, payload.start_date,
                        payload.end_date, payload.is_randomized, '[]'))
        draft_id = cursor.lastrowid
        questions = normalized_questions(payload, user['id'], draft_id)
        cursor.execute('UPDATE exam_drafts SET questions = ? WHERE id = ?',
                       (json.dumps(questions, ensure_ascii=False), draft_id))
        conn.commit()
        cursor.execute('SELECT * FROM exam_drafts WHERE id = ?', (draft_id,))
        return serialize(cursor.fetchone())
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.put('/{draft_id}')
def update_draft(room_id: int, draft_id: int, payload: ExamDraftSave, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        require_room_teacher(cursor, room_id, user)
        cursor.execute('SELECT questions FROM exam_drafts WHERE id = ? AND room_id = ? AND teacher_id = ?',
                       (draft_id, room_id, user['id']))
        current = cursor.fetchone()
        if not current:
            raise HTTPException(404, 'ไม่พบแบบร่าง')
        questions = normalized_questions(payload, user['id'], draft_id, draft_images(current['questions']))
        cursor.execute('''UPDATE exam_drafts SET title = ?, description = ?, start_date = ?, end_date = ?,
                          is_randomized = ?, questions = ?, updated_at = CURRENT_TIMESTAMP
                          WHERE id = ? AND room_id = ? AND teacher_id = ?''',
                       (payload.title, payload.description, payload.start_date, payload.end_date, payload.is_randomized,
                        json.dumps(questions, ensure_ascii=False),
                        draft_id, room_id, user['id']))
        conn.commit()
        cursor.execute('SELECT * FROM exam_drafts WHERE id = ?', (draft_id,))
        return serialize(cursor.fetchone())
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.delete('/{draft_id}')
def delete_draft(room_id: int, draft_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        require_room_teacher(cursor, room_id, user)
        cursor.execute('DELETE FROM exam_drafts WHERE id = ? AND room_id = ? AND teacher_id = ?',
                       (draft_id, room_id, user['id']))
        if cursor.rowcount == 0:
            raise HTTPException(404, 'ไม่พบแบบร่าง')
        conn.commit()
        return {'message': 'Draft deleted'}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
