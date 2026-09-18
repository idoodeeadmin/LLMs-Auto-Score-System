import os
import json
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
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    if cloud_name:
        try:
            upload_result = cloudinary.uploader.upload(file_bytes, folder=folder, public_id=public_id, resource_type='auto')
            return upload_result.get('secure_url')
        except Exception as e:
            print(f'[Cloudinary] Upload error: {e}')
    
    # Local fallback for development / offline without Cloudinary
    try:
        import time, uuid
        from PIL import Image
        import io
        with Image.open(io.BytesIO(file_bytes)) as image:
            suffix = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "GIF": "gif"}.get(image.format, "jpg")
        filename = f"{public_id or uuid.uuid4().hex[:12]}_{int(time.time())}.{suffix}"
        rel_dir = os.path.join("uploads", folder.replace('/', os.sep))
        os.makedirs(rel_dir, exist_ok=True)
        file_path = os.path.join(rel_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return f"/uploads/{folder}/{filename}".replace('\\', '/')
    except Exception as e:
        print(f'[Upload Local] Error saving file: {e}')
        return None


async def get_image_bytes(path_or_url: str):
    """Read only this application's uploaded images or Cloudinary images."""
    from pathlib import Path
    from urllib.parse import urlparse
    if not path_or_url:
        return None
    try:
        parsed = urlparse(path_or_url)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme != 'https' or parsed.hostname != 'res.cloudinary.com':
                return None
            async with httpx.AsyncClient() as client:
                async with client.stream('GET', path_or_url, timeout=15.0) as response:
                    response.raise_for_status()
                    chunks = bytearray()
                    async for chunk in response.aiter_bytes():
                        chunks.extend(chunk)
                        if len(chunks) > MAX_UPLOAD_SIZE:
                            return None
                    return bytes(chunks)
        root = Path('uploads').resolve()
        target = Path(path_or_url.lstrip('/')).resolve()
        if not target.is_relative_to(root) or not target.is_file() or target.stat().st_size > MAX_UPLOAD_SIZE:
            return None
        async with aiofiles.open(target, 'rb') as file:
            return await file.read()
    except Exception:
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
    from PIL import Image, UnidentifiedImageError
    import io
    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            actual_type = Image.MIME.get(image.format)
            if actual_type not in effective_types or (content_type and actual_type != content_type):
                raise HTTPException(400, 'ชนิดไฟล์ไม่ตรงกับรูปภาพที่แนบ')
            if getattr(image, 'is_animated', False):
                raise HTTPException(400, 'กรุณาแนบภาพนิ่ง')
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(400, 'ไฟล์รูปภาพไม่ถูกต้องหรือมีขนาดภาพใหญ่เกินไป')


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


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_firebase_app = None
auth = None


def get_firebase_app():
    """Initialize Firebase Admin on first use and return its app.

    Environment values are read on every first-use attempt so importing this
    module before ``load_dotenv()`` cannot permanently cache an empty path.
    """
    global _firebase_app, auth
    if _firebase_app is not None:
        return _firebase_app
    
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth
    auth = firebase_auth
    
    # 1. Try environment variable JSON content
    firebase_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON', '').strip()
    if firebase_json:
        try:
            cred_dict = json.loads(firebase_json)
            _firebase_app = firebase_admin.initialize_app(credentials.Certificate(cred_dict))
            return _firebase_app
        except Exception as e:
            if 'already exists' in str(e):
                _firebase_app = firebase_admin.get_app()
                return _firebase_app
            
    # 2. Try explicit/default file paths. Relative paths are always resolved
    # from the project root, independent of the process working directory.
    configured_path = os.getenv('FIREBASE_CREDENTIALS_PATH', '').strip()
    if configured_path and not os.path.isabs(configured_path):
        configured_path = os.path.join(_PROJECT_ROOT, configured_path)
    candidate_paths = [
        configured_path,
        'llms-auto-score-systems-firebase-adminsdk-fbsvc-f81fe0b67f.json',
        os.path.join(_PROJECT_ROOT, 'llms-auto-score-systems-firebase-adminsdk-fbsvc-f81fe0b67f.json'),
        os.path.join(os.path.dirname(_PROJECT_ROOT), 'llms-auto-score-systems-firebase-adminsdk-fbsvc-f81fe0b67f.json')
    ]
    
    for path in candidate_paths:
        if path and os.path.exists(path):
            try:
                _firebase_app = firebase_admin.initialize_app(credentials.Certificate(path))
                print(f'[Firebase] Admin SDK initialized successfully from: {path}')
                return _firebase_app
            except Exception as e:
                if 'already exists' in str(e):
                    _firebase_app = firebase_admin.get_app()
                    return _firebase_app
                
    print('[Firebase] Service account is not configured. Set FIREBASE_CREDENTIALS_PATH or FIREBASE_SERVICE_ACCOUNT_JSON.')
    return None


def get_firebase_auth():
    """Return Firebase Auth only after the Admin app is initialized."""
    if get_firebase_app() is None:
        return None
    return auth

# Firebase is initialized lazily by the Google authentication routes.

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


