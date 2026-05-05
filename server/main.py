from server.utils import grading_queue
from server.services.ai_service import grading_worker
import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, Header, UploadFile, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .database import get_db_connection, init_db
from .auth import get_password_hash, verify_password, create_access_token, decode_token
from .models import *
import pymysql
import random
import string
import os
import json as json_module_top
import csv
import io
import statistics
from dotenv import load_dotenv
import aiofiles
import httpx
import time
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
load_dotenv()
cloudinary.config(cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'), api_key=os.getenv('CLOUDINARY_API_KEY'), api_secret=os.getenv('CLOUDINARY_API_SECRET'), secure=True)
app = FastAPI(title='Evaly API')
from server.routes import auth_routes, room_routes, exam_routes, notification_routes, question_bank_routes, ai_routes, system_routes
app.include_router(auth_routes.router)
app.include_router(room_routes.router)
app.include_router(exam_routes.router)
app.include_router(notification_routes.router)
app.include_router(question_bank_routes.router)
app.include_router(ai_routes.router)
app.include_router(system_routes.router)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.on_event('startup')
async def startup_event():
    print("[Startup] Initializing database...")
    init_db()
    print("[Startup] Database initialized.")
    os.makedirs('uploads', exist_ok=True)
    print("[Startup] Starting grading worker...")
    asyncio.create_task(grading_worker())
    print("[Startup] Recovering pending submissions...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, exam_id, student_id FROM submissions WHERE status = 'submitted'")
    pending = cursor.fetchall()
    for row in pending:
        cursor.execute('SELECT room_id FROM exams WHERE id = ?', (row['exam_id'],))
        exam_row = cursor.fetchone()
        if exam_row:
            await grading_queue.put({'submission_id': row['id'], 'room_id': exam_row['room_id'], 'exam_id': row['exam_id'], 'user_id': row['student_id']})
    conn.close()
    if pending:
        print(f'[Startup] Recovered {len(pending)} pending submissions into grading queue')
    print("[Startup] Startup complete.")
try:
    app.mount('/uploads', StaticFiles(directory='uploads'), name='uploads')
    app.mount('/api/uploads', StaticFiles(directory='uploads'), name='api_uploads')
except Exception:
    pass
REQUEST_LOGS = {}


from fastapi import Request
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)