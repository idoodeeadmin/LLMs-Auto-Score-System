import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.database import get_db_connection

def test_query():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create a test user, room, and exam if they don't exist
        cursor.execute("INSERT IGNORE INTO users (id, email, password, name, role) VALUES (99999, 'test@test.com', 'pwd', 'test', 'student')")
        cursor.execute("INSERT IGNORE INTO rooms (id, name, class_code, teacher_id) VALUES (99999, 'Test Room', 'TEST01', 99999)")
        cursor.execute("INSERT IGNORE INTO exams (id, room_id, title) VALUES (99999, 99999, 'Test Exam')")
        cursor.execute("INSERT IGNORE INTO questions (id, exam_id, text) VALUES (99999, 99999, 'Test Q')")
        conn.commit()

        submission_id = 99999
        q_id = 99999
        answer_text = 'test answer'
        first_image_path = None
        image_paths_json = None

        cursor.execute("INSERT INTO submissions (id, exam_id, user_id, status) VALUES (99999, 99999, 99999, 'submitted') ON DUPLICATE KEY UPDATE status='submitted'")
        
        sql = """INSERT INTO submission_answers
                 (submission_id, question_id, answer_text, ai_score, ai_feedback, ai_confidence, image_paths)
               VALUES (?, ?, ?, 0, '', 'medium', ?)
               ON DUPLICATE KEY UPDATE
                 answer_text=VALUES(answer_text), image_paths=VALUES(image_paths)"""
        
        cursor.execute(sql, (submission_id, q_id, answer_text, image_paths_json))
        conn.commit()
        print("Success")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    finally:
        cursor.execute("DELETE FROM submission_answers WHERE submission_id=99999")
        cursor.execute("DELETE FROM submissions WHERE id=99999")
        cursor.execute("DELETE FROM questions WHERE id=99999")
        cursor.execute("DELETE FROM exams WHERE id=99999")
        cursor.execute("DELETE FROM rooms WHERE id=99999")
        cursor.execute("DELETE FROM users WHERE id=99999")
        conn.commit()
        conn.close()

if __name__ == '__main__':
    test_query()
