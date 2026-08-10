import os
import json as json_module_top
import asyncio
import httpx
import time
import cloudinary
import cloudinary.uploader
import random
import string
import aiofiles
from fastapi import Header, HTTPException, Depends, Request
from typing import Optional

from server.database import get_db_connection
from server.auth import decode_token

def upload_to_cloudinary(file_bytes, folder='evaly', public_id=None):
    try:
        upload_result = cloudinary.uploader.upload(file_bytes, folder=folder, public_id=public_id, resource_type='auto')
        return upload_result.get('secure_url')
    except Exception as e:
        print(f'[Cloudinary] Upload error: {e}')
        return None

async def get_image_bytes(path_or_url: str):
    if not path_or_url:
        return None
    if path_or_url.startswith('http'):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(path_or_url, timeout=10.0)
                if resp.status_code == 200:
                    return resp.content
                return None
        except Exception as e:
            print(f'[Grading Worker] Failed to fetch URL {path_or_url}: {e}')
            return None
    else:
        local_path = path_or_url.lstrip('/')
        if os.path.exists(local_path):
            try:
                async with aiofiles.open(local_path, 'rb') as f:
                    return await f.read()
            except Exception as e:
                print(f'[Grading Worker] Failed to read local {local_path}: {e}')
                return None
        return None

grading_queue = asyncio.Queue()

# --- CSV Formula Injection Prevention ---
_CSV_DANGEROUS_CHARS = ('=', '+', '-', '@', '\t', '\r')

def sanitize_csv_value(value):
    """Prevent CSV formula injection by prefixing dangerous starting characters with a single quote."""
    if value and isinstance(value, str) and value[0] in _CSV_DANGEROUS_CHARS:
        return "'" + value
    return value

# --- File Upload Validation ---
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

def validate_upload_file(file_bytes: bytes, content_type: str = None, max_size: int = None, allowed_types: set = None):
    """Validate uploaded file size and MIME type. Raises HTTPException on failure."""
    effective_max = max_size or MAX_UPLOAD_SIZE
    effective_types = allowed_types or ALLOWED_IMAGE_TYPES
    if len(file_bytes) > effective_max:
        max_mb = effective_max / (1024 * 1024)
        raise HTTPException(status_code=413, detail=f'File too large. Maximum size is {max_mb:.0f}MB')
    if content_type and content_type not in effective_types:
        raise HTTPException(status_code=400, detail=f'Unsupported file type: {content_type}. Allowed: {", ".join(effective_types)}')

REQUEST_LOGS = {}

def check_rate_limit(ip: str, limit: int=10, window: int=60):
    """Simple IP-based rate limiter (default: 10 requests per minute)"""
    if not ip:
        ip = "unknown"
    now = time.time()
    if ip not in REQUEST_LOGS:
        REQUEST_LOGS[ip] = []
    REQUEST_LOGS[ip] = [t for t in REQUEST_LOGS[ip] if now - t < window]
    if len(REQUEST_LOGS[ip]) >= limit:
        return False
    REQUEST_LOGS[ip].append(now)
    return True

async def trigger_socket_notify(user_id: int, notify_type: str, message: str, data: dict=None):
    """Bridge to Node.js Socket server to emit real-time notifications and save to DB"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        link = data.get('link', '') if data else ''
        import json as json_module
        data_str = json_module.dumps(data) if data else None
        cursor.execute("INSERT INTO notifications (user_id, type, message, link, data) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, notify_type, message, link, data_str))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'[Notification DB Error] {e}')

    socket_url = f"http://localhost:{os.getenv('SOCKET_PORT', '3001')}/emit-notification"
    socket_secret = os.getenv('SOCKET_INTERNAL_SECRET', '')
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                socket_url,
                json={'userId': user_id, 'type': notify_type, 'message': message, 'data': data or {}},
                headers={'X-Internal-Secret': socket_secret},
                timeout=2.0
            )
    except Exception:
        # Node.js WebSocket server is offline or unreachable - notification is safely saved in DB
        pass

def get_current_user(request: Request, authorization: Optional[str]=Header(None)):
    token = None
    # Priority 1: httpOnly cookie
    if request and hasattr(request, 'cookies'):
        token = request.cookies.get('access_token')
    # Priority 2: Authorization header (fallback for socket/external API)
    if not token:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Invalid token')
        token = authorization.split(' ')[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    email = payload.get('sub')
    token_version = payload.get('token_version', 0)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, name, role, student_id, avatar_url, is_verified, token_version FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.get('token_version', 0) != token_version:
        raise HTTPException(status_code=401, detail='Session expired or revoked')
    return dict(user)

def generate_class_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join((random.choice(characters) for _ in range(length)))


_FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _FIREBASE_CREDENTIALS_PATH and (not os.path.isabs(_FIREBASE_CREDENTIALS_PATH)):
    _FIREBASE_CREDENTIALS_PATH = os.path.join(_PROJECT_ROOT, _FIREBASE_CREDENTIALS_PATH)
_firebase_app = None
auth = None
_FIREBASE_JSON = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON', '')
if _FIREBASE_JSON:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth
    auth = firebase_auth
    try:
        cred_dict = json_module_top.loads(_FIREBASE_JSON)
        cred = credentials.Certificate(cred_dict)
        _firebase_app = firebase_admin.initialize_app(cred)
        print('[Firebase] Admin SDK initialized successfully from environment variable')
    except Exception as e:
        print(f'[Firebase] Failed to initialize Admin SDK from ENV: {e}')
elif _FIREBASE_CREDENTIALS_PATH and os.path.exists(_FIREBASE_CREDENTIALS_PATH):
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth
    auth = firebase_auth
    try:
        cred = credentials.Certificate(_FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        print('[Firebase] Admin SDK initialized successfully from file')
    except Exception as e:
        print(f'[Firebase] Failed to initialize Admin SDK from file: {e}')

def _distribution_buckets(scores: list[float], total_score: float) -> dict:
    if total_score <= 0:
        return {'0-24': 0, '25-49': 0, '50-74': 0, '75-100': 0}
    buckets = {'0-24': 0, '25-49': 0, '50-74': 0, '75-100': 0}
    for s in scores:
        pct = max(0.0, min(100.0, float(s) / float(total_score) * 100.0))
        if pct < 25:
            buckets['0-24'] += 1
        elif pct < 50:
            buckets['25-49'] += 1
        elif pct < 75:
            buckets['50-74'] += 1
        else:
            buckets['75-100'] += 1
    return buckets

