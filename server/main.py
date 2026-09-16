import os
from dotenv import load_dotenv
load_dotenv()

import importlib

# Firebase downloads Google's public signing certificates when verifying an ID
# token. On Windows, use the OS trust store so local/root CAs trusted by the
# browser are also trusted by Python's HTTPS stack.
inject_into_ssl = None
for _mod_name in ("truststore", "pip._vendor.truststore"):
    try:
        _mod = importlib.import_module(_mod_name)
        inject_into_ssl = getattr(_mod, "inject_into_ssl", None)
        if inject_into_ssl:
            break
    except Exception:
        continue

if inject_into_ssl:
    inject_into_ssl()

from server.services.ai_service import grading_worker
from server.services.notification_service import deadline_notification_worker
import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, Header, UploadFile, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .database import get_db_connection, init_db
from .utils import grading_queue
from .models import *
import pymysql
import random
import string
import os
import json as json_module_top
import csv
import io
import statistics
import aiofiles
import httpx
import time
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

cloudinary.config(cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
 api_key=os.getenv('CLOUDINARY_API_KEY'), api_secret=os.getenv('CLOUDINARY_API_SECRET'),
 secure=True)
app = FastAPI(title='Evaly API')
from server.routes import auth_routes, room_routes, exam_routes, notification_routes, ai_routes, system_routes, benchmark_routes
app.include_router(auth_routes.router)
app.include_router(room_routes.router)
app.include_router(exam_routes.router)
app.include_router(notification_routes.router)
app.include_router(benchmark_routes.router)

app.include_router(ai_routes.router)
app.include_router(ai_routes.legacy_router)
app.include_router(system_routes.router)
default_origins = [
    'http://localhost:5173',
    'http://localhost:8080',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:8080',
    'https://llms-auto-score-systems.netlify.app',
    'https://llms-auto-score-system.netlify.app',
    'https://llms-auto-score-system.onrender.com',
]
custom_origins = [o.strip() for o in os.getenv('CORS_ORIGINS', '').split(',') if o.strip()]
_cors_origins = list(set(default_origins + custom_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r'https://.*\.netlify\.app|https://.*\.vercel\.app|https://.*\.onrender\.com',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.on_event('startup')
async def startup_event():
    print("[Startup] Initializing database...")
    init_db()
    print("[Startup] Database initialized.")
    os.makedirs('uploads', exist_ok=True)
    print("[Startup] Starting grading worker...")
    asyncio.create_task(grading_worker())
    print("[Startup] Starting deadline notification worker...")
    asyncio.create_task(deadline_notification_worker())
    print("[Startup] Recovering pending submissions...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, exam_id, user_id FROM submissions WHERE status IN ('submitted', 'grading')")
    pending = cursor.fetchall()
    for row in pending:
        cursor.execute('SELECT room_id FROM exams WHERE id = ?', (row['exam_id'],))
        exam_row = cursor.fetchone()
        if exam_row:
            await grading_queue.put({'submission_id': row['id'], 'room_id': exam_row['room_id'], 'exam_id': row['exam_id'], 'user_id': row['user_id']})
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
