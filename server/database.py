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
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
