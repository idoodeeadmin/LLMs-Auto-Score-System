import pymysql
import pymysql.cursors
import os
import ssl
import certifi
from dotenv import load_dotenv

load_dotenv()

class MySQLCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, args=None):
        # Replace SQLite parameter placeholder '?' with MySQL's '%s'
        if args is not None:
            query = query.replace('?', '%s')
            return self.cursor.execute(query, args)
        return self.cursor.execute(query)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()

class MySQLConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return MySQLCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_db_connection():
    host = os.getenv("TIDB_HOST", "gateway01.ap-southeast-1.prod.aws.tidbcloud.com")
    port = int(os.getenv("TIDB_PORT", 4000))
    user = os.getenv("TIDB_USER", "4CtLwqCa3oUaTqQ.root")
    password = os.getenv("TIDB_PASSWORD", "")
    database = os.getenv("TIDB_DATABASE", "test")
    ca_path = os.getenv("TIDB_CA_PATH", "")

    # Configure SSL
    ssl_args = None
    if ca_path and os.path.exists(ca_path):
        ssl_args = {'ca': ca_path}
    else:
        # TiDB Serverless requires SSL. Use certifi's bundled CA if no custom CA path is provided.
        ssl_args = {'ca': certifi.where()}

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
        ssl=ssl_args
    )
    return MySQLConnectionWrapper(conn)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        student_id VARCHAR(100),
        avatar_url TEXT,
        is_verified TINYINT DEFAULT 0
    )
    ''')
    
    # Create Rooms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        section VARCHAR(100),
        class_code VARCHAR(50) UNIQUE NOT NULL,
        owner_id INTEGER,
        FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE SET NULL
    )
    ''')
    
    # Create Enrollments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
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
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        room_id INTEGER NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        total_score FLOAT DEFAULT 0,
        start_date VARCHAR(100),
        end_date VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
    )
    ''')

    # Create Questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        exam_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        score FLOAT DEFAULT 0,
        answer_key TEXT,
        rubrics TEXT,
        order_index INTEGER DEFAULT 0,
        image_path TEXT,
        image_paths TEXT,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
    )
    ''')

    # Create Submissions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        exam_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        status VARCHAR(50) DEFAULT 'missing',
        total_score FLOAT DEFAULT 0,
        submitted_at DATETIME,
        graded_by_ai TINYINT DEFAULT 0,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(exam_id, student_id)
    )
    ''')

    # Create Submission Answers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS submission_answers (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        submission_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        answer_text TEXT,
        ai_score FLOAT DEFAULT 0,
        ai_feedback TEXT,
        ai_confidence VARCHAR(50) DEFAULT 'medium',
        teacher_score FLOAT,
        teacher_comment TEXT,
        image_path TEXT,
        image_paths TEXT,
        FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
        UNIQUE(submission_id, question_id)
    )
    ''')

    # Create Password Resets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        user_id INTEGER NOT NULL,
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # Create Email Verifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_verifications (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        user_id INTEGER NOT NULL,
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()

    # In MySQL, adding a column that already exists will raise a pymysql.err.OperationalError
    def add_column_if_not_exists(table, column_def):
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
            conn.commit()
        except pymysql.err.OperationalError as e:
            # Error 1060 is "Duplicate column name"
            if e.args[0] != 1060:
                print(f"Error adding column: {e}")
        except Exception as e:
            pass

    add_column_if_not_exists("submissions", "graded_by_ai TINYINT DEFAULT 0")
    add_column_if_not_exists("submission_answers", "image_path TEXT")
    add_column_if_not_exists("questions", "image_path TEXT")
    add_column_if_not_exists("questions", "image_paths TEXT")
    add_column_if_not_exists("submission_answers", "image_paths TEXT")
    add_column_if_not_exists("users", "name VARCHAR(255) NOT NULL DEFAULT 'User'")
    add_column_if_not_exists("users", "student_id VARCHAR(100)")
    add_column_if_not_exists("users", "avatar_url TEXT")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_verified TINYINT DEFAULT 0")
        conn.commit()
        cursor.execute("UPDATE users SET is_verified = 1 WHERE is_verified = 0")
        conn.commit()
        print("Legacy users successfully migrated to is_verified = 1")
    except pymysql.err.OperationalError as e:
        pass
    except Exception:
        pass

    conn.close()

    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(os.path.join("uploads", "questions"), exist_ok=True)
    os.makedirs(os.path.join("uploads", "avatars"), exist_ok=True)

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
