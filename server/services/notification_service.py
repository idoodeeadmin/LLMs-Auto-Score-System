import asyncio
import logging
from datetime import datetime, timezone, timedelta
from server.database import get_db_connection
from server.utils import trigger_socket_notify
from server.exam_policy import parse_exam_time

logger = logging.getLogger(__name__)


async def send_deadline_notifications(now=None):
    """One scheduler tick; persisted notices also suppress repeats after restart."""
    now = now or datetime.now(timezone.utc)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT e.id, e.title, e.start_date, e.end_date, r.teacher_id, r.id AS room_id, r.name AS room_name FROM exams e JOIN rooms r ON e.room_id = r.id WHERE e.end_date IS NOT NULL")
        exams = cursor.fetchall()
        for exam in exams:
            try:
                end = parse_exam_time(exam['end_date'])
                start = parse_exam_time(exam.get('start_date'))
            except (ValueError, TypeError):
                continue
            if not end or (start and now < start):
                continue
            remaining = end - now
            if timedelta(0) < remaining <= timedelta(minutes=5):
                kind = 'deadline_soon'
                cursor.execute("SELECT en.user_id FROM enrollments en LEFT JOIN submissions s ON s.exam_id = ? AND s.user_id = en.user_id WHERE en.room_id = ? AND (s.id IS NULL OR s.status = 'missing')", (exam['id'], exam['room_id']))
                recipients = [row['user_id'] for row in cursor.fetchall()]
                message = f"[{exam['room_name']}] ข้อสอบ {exam['title']} เหลือเวลาส่งไม่เกิน 5 นาที"
                link = f"/room/{exam['room_id']}/exam/{exam['id']}/submit"
            elif timedelta(minutes=-10) < remaining <= timedelta(0):
                kind, recipients = 'deadline_passed', [exam['teacher_id']]
                message = f"[{exam['room_name']}] ข้อสอบ {exam['title']} หมดเวลาส่งแล้ว"
                link = f"/room/{exam['room_id']}/exam/{exam['id']}/review"
            else:
                continue
            for user_id in recipients:
                cursor.execute("SELECT id FROM notifications WHERE user_id = ? AND type = ? AND link = ? AND JSON_UNQUOTE(JSON_EXTRACT(data, '$.deadline')) = ? LIMIT 1", (user_id, kind, link, end.isoformat()))
                if cursor.fetchone():
                    continue
                await trigger_socket_notify(user_id=user_id, notify_type=kind, message=message,
                    data={'room_id': exam['room_id'], 'exam_id': exam['id'], 'link': link, 'deadline': end.isoformat()})
    finally:
        conn.close()


async def deadline_notification_worker():
    while True:
        try:
            await send_deadline_notifications()
        except Exception:
            logger.exception('Deadline notification tick failed')
        await asyncio.sleep(30)
