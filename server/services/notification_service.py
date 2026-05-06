import asyncio
import time
from datetime import datetime, timezone, timedelta
from server.database import get_db_connection
from server.utils import trigger_socket_notify

async def deadline_notification_worker():
    """
    Background worker that checks for exams that have just reached their deadline
    and notifies the teacher via real-time socket.
    """
    print("[Notification Worker] Starting deadline checker...")
    notified_exams = set() # Keep track of exams notified in this session
    
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            now_utc = datetime.now(timezone.utc)
            
            # Fetch all exams with an end date
            cursor.execute("""
                SELECT e.id, e.title, e.end_date, r.owner_id, r.id as room_id, r.name as room_name 
                FROM exams e 
                JOIN rooms r ON e.room_id = r.id 
                WHERE e.end_date IS NOT NULL
            """)
            exams = cursor.fetchall()
            
            for ex in exams:
                exam_id = ex['id']
                if exam_id in notified_exams:
                    continue
                
                try:
                    # Parse end_date
                    end_date_str = ex['end_date']
                    end_dt = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    if end_dt.tzinfo is None:
                        end_dt = end_dt.replace(tzinfo=timezone.utc)
                    
                    # If the deadline just passed (within the last 10 minutes)
                    # We check a 10-min window to account for server restarts or downtime
                    if timedelta(0) < (now_utc - end_dt) < timedelta(minutes=10):
                        print(f"[Notification Worker] Deadline passed for exam {exam_id}: {ex['title']}")
                        
                        await trigger_socket_notify(
                            user_id=ex['owner_id'],
                            notify_type='deadline_passed',
                            message=f"[{ex['room_name']}] ชุดข้อสอบ \"{ex['title']}\" หมดเวลาส่งแล้ว!",
                            data={'exam_id': exam_id, 'room_id': ex['room_id']}
                        )
                        notified_exams.add(exam_id)
                    
                    # If it passed a long time ago, just mark it as notified so we don't check it again in this session
                    elif (now_utc - end_dt) > timedelta(minutes=10):
                        notified_exams.add(exam_id)
                        
                except Exception as e:
                    # print(f"[Notification Worker] Error parsing date for exam {exam_id}: {e}")
                    continue
                    
            conn.close()
        except Exception as e:
            print(f"[Notification Worker] Error in loop: {e}")
        
        # Wait for 1 minute before next check
        await asyncio.sleep(60)
