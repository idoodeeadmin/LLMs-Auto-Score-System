import sqlite3
import os

DB_PATH = "dev.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        student_id TEXT
    )
    ''')
    
    # Create Rooms table
    # class_code is a unique 6-character code used by students to join.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        section TEXT,
        class_code TEXT UNIQUE NOT NULL,
        owner_id INTEGER,
        FOREIGN KEY (owner_id) REFERENCES users (id)
    )
    ''')
    
    # Create Enrollments table (Students joining rooms)
    # Using CASCADE so if a room is deleted, student enrollments are also removed.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE,
        UNIQUE(user_id, room_id)
    )
    ''')

    # Create Exams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        total_score REAL DEFAULT 0,
        start_date TEXT,
        end_date TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
    )
    ''')

    # Create Questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        score REAL DEFAULT 0,
        answer_key TEXT,
        rubrics TEXT,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
    )
    ''')

    # Create Submissions table (one per student per exam)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        status TEXT DEFAULT 'missing',
        total_score REAL DEFAULT 0,
        submitted_at DATETIME,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(exam_id, student_id)
    )
    ''')

    # Create Submission Answers table (one per question per submission)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS submission_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        answer_text TEXT,
        ai_score REAL DEFAULT 0,
        ai_feedback TEXT,
        ai_confidence TEXT DEFAULT 'medium',
        teacher_score REAL,
        teacher_comment TEXT,
        FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
        UNIQUE(submission_id, question_id)
    )
    ''')

    # Create Password Resets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # Create Email Verifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()

    # Migration: add graded_by_ai column to submissions if not exists
    try:
        cursor.execute("ALTER TABLE submissions ADD COLUMN graded_by_ai INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Migration: add image_path column to submission_answers if not exists
    try:
        cursor.execute("ALTER TABLE submission_answers ADD COLUMN image_path TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Migration: add image_path column to questions if not exists
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN image_path TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Migration: add image_paths (JSON array) column to questions if not exists
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN image_paths TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Migration: add image_paths (JSON array) column to submission_answers if not exists
    try:
        cursor.execute("ALTER TABLE submission_answers ADD COLUMN image_paths TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Migration: add avatar_url column to users if not exists
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Migration: add is_verified column to users if not exists
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
        conn.commit()
        # Set all legacy users to verified = 1 to prevent locking them out
        cursor.execute("UPDATE users SET is_verified = 1 WHERE is_verified = 0")
        conn.commit()
        print("Legacy users successfully migrated to is_verified = 1")
    except Exception:
        pass  # Column already exists

    conn.close()

    # Ensure uploads directory exists
    import os
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(os.path.join("uploads", "questions"), exist_ok=True)
    os.makedirs(os.path.join("uploads", "avatars"), exist_ok=True)


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
