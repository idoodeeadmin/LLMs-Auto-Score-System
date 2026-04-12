from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .database import get_db_connection, init_db
from .auth import get_password_hash, verify_password, create_access_token, decode_token
import sqlite3
import random
import string

app = FastAPI(title="Evaly API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str
    student_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RoomCreate(BaseModel):
    name: str
    section: Optional[str] = None

class JoinRoomRequest(BaseModel):
    class_code: str

# Dependencies
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = payload.get("sub")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, role, student_id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return dict(user)

# Auth Routes
@app.post("/api/auth/register")
async def register(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = get_password_hash(user.password)
    
    try:
        cursor.execute(
            "INSERT INTO users (email, password, name, role, student_id) VALUES (?, ?, ?, ?, ?)",
            (user.email, hashed_password, user.name, user.role, user.student_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()
        
    return {"message": "User registered successfully"}

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (user_data.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    user_info = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "studentId": user["student_id"]
    }
    
    return {"access_token": access_token, "token_type": "bearer", "user": user_info}

@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "studentId": user["student_id"]
    }

# Room Routes
def generate_class_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.post("/api/rooms")
async def create_room(room: RoomCreate, user: dict = Depends(get_current_user)):
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create rooms")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate unique class code
    class_code = generate_class_code()
    
    try:
        cursor.execute(
            "INSERT INTO rooms (name, section, class_code, owner_id) VALUES (?, ?, ?, ?)",
            (room.name, room.section, class_code, user["id"])
        )
        conn.commit()
        new_room_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=500, detail="Failed to generate unique class code. Try again.")
        
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (new_room_id,))
    new_room = dict(cursor.fetchone())
    conn.close()
    
    return new_room

@app.get("/api/rooms")
async def get_rooms(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if user["role"] == "teacher":
        cursor.execute("SELECT * FROM rooms WHERE owner_id = ?", (user["id"],))
        rooms = cursor.fetchall()
    else:
        cursor.execute('''
            SELECT r.* FROM rooms r
            JOIN enrollments e ON r.id = e.room_id
            WHERE e.user_id = ?
        ''', (user["id"],))
        rooms = cursor.fetchall()
        
    conn.close()
    return [dict(room) for room in rooms]

@app.put("/api/rooms/{room_id}")
async def update_room(room_id: int, room_data: RoomCreate, user: dict = Depends(get_current_user)):
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can edit rooms")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM rooms WHERE id = ? AND owner_id = ?", (room_id, user["id"]))
    existing_room = cursor.fetchone()
    
    if not existing_room:
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found or unauthorized")
        
    cursor.execute(
        "UPDATE rooms SET name = ?, section = ? WHERE id = ?",
        (room_data.name, room_data.section, room_id)
    )
    conn.commit()
    conn.close()
    
    return {"message": "Room updated successfully"}

@app.delete("/api/rooms/{room_id}")
async def delete_room(room_id: int, user: dict = Depends(get_current_user)):
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete rooms")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM rooms WHERE id = ? AND owner_id = ?", (room_id, user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found or unauthorized")
        
    cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Room deleted successfully"}

@app.post("/api/rooms/join")
async def join_room(request: JoinRoomRequest, user: dict = Depends(get_current_user)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can join rooms")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if code maps to a room
    cursor.execute("SELECT id FROM rooms WHERE class_code = ?", (request.class_code.upper(),))
    room = cursor.fetchone()
    if not room:
        conn.close()
        raise HTTPException(status_code=404, detail="รหัสห้องไม่ถูกต้อง (Invalid class code)")
        
    room_id = room["id"]
    
    # Check if already enrolled
    cursor.execute("SELECT id FROM enrollments WHERE user_id = ? AND room_id = ?", (user["id"], room_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="คุณอยู่ในห้องนี้แล้ว (Already joined)")
        
    cursor.execute("INSERT INTO enrollments (user_id, room_id) VALUES (?, ?)", (user["id"], room_id))
    conn.commit()
    
    # Fetch room info to return
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    joined_room = dict(cursor.fetchone())
    conn.close()
    
    return joined_room

@app.get("/api/rooms/{room_id}")
async def get_room(room_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if user["role"] == "teacher":
        cursor.execute("SELECT * FROM rooms WHERE id = ? AND owner_id = ?", (room_id, user["id"]))
    else:
        cursor.execute("""
            SELECT r.* FROM rooms r
            JOIN enrollments e ON r.id = e.room_id
            WHERE r.id = ? AND e.user_id = ?
        """, (room_id, user["id"]))
    
    room = cursor.fetchone()
    conn.close()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or unauthorized")
    
    return dict(room)

@app.get("/api/rooms/{room_id}/members")
async def get_room_members(room_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify access
    if user["role"] == "teacher":
        cursor.execute("SELECT id FROM rooms WHERE id = ? AND owner_id = ?", (room_id, user["id"]))
    else:
        cursor.execute("SELECT room_id FROM enrollments WHERE room_id = ? AND user_id = ?", (room_id, user["id"]))
    
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Get room owner (teacher)
    cursor.execute("SELECT u.id, u.name, u.email, u.student_id FROM users u JOIN rooms r ON u.id = r.owner_id WHERE r.id = ?", (room_id,))
    teacher_row = cursor.fetchone()
    teacher = {**dict(teacher_row), "role": "teacher", "joined_at": None} if teacher_row else None

    cursor.execute("""
        SELECT u.id, u.name, u.email, u.student_id, e.joined_at
        FROM users u
        JOIN enrollments e ON u.id = e.user_id
        WHERE e.room_id = ?
        ORDER BY e.joined_at DESC
    """, (room_id,))
    members = cursor.fetchall()
    conn.close()

    result = []
    if teacher:
        result.append({**teacher, "role": "teacher"})
    for m in members:
        result.append({**dict(m), "role": "student"})
    
    return result

# Exam Routes
import json as json_module

class QuestionInput(BaseModel):
    text: str
    score: float = 0
    answer_key: Optional[str] = None
    rubrics: Optional[list] = None
    order_index: int = 0

class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    total_score: float = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    questions: list[QuestionInput] = []

@app.post("/api/rooms/{room_id}/exams")
async def create_exam(room_id: int, exam: ExamCreate, user: dict = Depends(get_current_user)):
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create exams")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify room ownership
    cursor.execute("SELECT id FROM rooms WHERE id = ? AND owner_id = ?", (room_id, user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found or unauthorized")

    # Insert exam
    cursor.execute(
        "INSERT INTO exams (room_id, title, description, total_score, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)",
        (room_id, exam.title, exam.description, exam.total_score, exam.start_date, exam.end_date)
    )
    exam_id = cursor.lastrowid

    # Insert questions
    for q in exam.questions:
        rubrics_json = json_module.dumps(q.rubrics, ensure_ascii=False) if q.rubrics else None
        cursor.execute(
            "INSERT INTO questions (exam_id, text, score, answer_key, rubrics, order_index) VALUES (?, ?, ?, ?, ?, ?)",
            (exam_id, q.text, q.score, q.answer_key, rubrics_json, q.order_index)
        )

    conn.commit()
    cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
    new_exam = dict(cursor.fetchone())
    conn.close()

    return new_exam

@app.get("/api/rooms/{room_id}/exams")
async def list_exams(room_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify access
    if user["role"] == "teacher":
        cursor.execute("SELECT id FROM rooms WHERE id = ? AND owner_id = ?", (room_id, user["id"]))
    else:
        cursor.execute("SELECT room_id FROM enrollments WHERE room_id = ? AND user_id = ?", (room_id, user["id"]))

    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized")

    cursor.execute("SELECT * FROM exams WHERE room_id = ? ORDER BY created_at DESC", (room_id,))
    exams = cursor.fetchall()
    conn.close()

    return [dict(e) for e in exams]

@app.get("/api/rooms/{room_id}/exams/{exam_id}")
async def get_exam(room_id: int, exam_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM exams WHERE id = ? AND room_id = ?", (exam_id, room_id))
    exam = cursor.fetchone()
    if not exam:
        conn.close()
        raise HTTPException(status_code=404, detail="Exam not found")

    cursor.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY order_index", (exam_id,))
    questions = cursor.fetchall()
    conn.close()

    result = dict(exam)
    result["questions"] = []
    for q in questions:
        qd = dict(q)
        if qd.get("rubrics"):
            try:
                qd["rubrics"] = json_module.loads(qd["rubrics"])
            except Exception:
                qd["rubrics"] = []
        result["questions"].append(qd)

    return result

# Demo route
@app.get("/api/ping")
async def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
