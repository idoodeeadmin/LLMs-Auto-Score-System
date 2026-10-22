from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File, Form, Request, Response
import pymysql
import uuid
import smtplib
import asyncio
from datetime import datetime, timezone, timedelta
import os
import secrets
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from server.database import get_db_connection
from server.auth import get_password_hash, verify_password, create_access_token, decode_token
from server.models import *
from server.utils import check_rate_limit, get_firebase_auth, upload_to_cloudinary, get_current_user, validate_upload_file

_IS_DEV_MODE = os.getenv('APP_ENV', 'development').lower() == 'development'

def _is_local_dev(request: Request) -> bool:
    """Never expose development verification secrets from a public server."""
    loopback = {'localhost', '127.0.0.1', '::1'}
    client_host = request.client.host if request.client else None
    return _IS_DEV_MODE and request.url.hostname in loopback and client_host in loopback

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def _get_client_ip(request: Request) -> str:
    if not request:
        return "unknown"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if getattr(request, "client", None) else "unknown"

def _send_smtp_email_sync(to_email: str, subject: str, html_body: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_port_str = os.getenv("SMTP_PORT", "587")
    smtp_port = int(smtp_port_str) if smtp_port_str else 587

    if not (smtp_host and smtp_user and smtp_password):
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = f"Evaly Score <{smtp_user}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        # Strict 5.0 second socket timeout prevents cloud outbound firewall blocks from hanging
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=5.0)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"[Email Sent] Successfully sent email to {to_email}")
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send email to {to_email} via SMTP ({smtp_host}:{smtp_port}): {e}")
        return False

@router.post('/register')
async def register(user: UserRegister, request: Request):
    client_ip = _get_client_ip(request)
    if not check_rate_limit(client_ip, limit=30, window=3600):
        raise HTTPException(status_code=429, detail='Too many registration attempts. Please try again later.')

    require_verification = os.getenv('REQUIRE_EMAIL_VERIFICATION', 'false').lower() in ('true', '1')
    # Standard registration via email/password always starts with is_verified = 0 until verified
    initial_is_verified = 0

    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = get_password_hash(user.password)
    try:
        cursor.execute(
            'INSERT INTO users (email, password, name, role, student_id, avatar_url, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user.email, hashed_password, user.name, user.role or 'unassigned', user.student_id, user.avatar_url, initial_is_verified)
        )
        user_id = cursor.lastrowid
        token = uuid.uuid4().hex
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        cursor.execute('INSERT INTO email_verifications (user_id, token, expires_at) VALUES (?, ?, ?)', (user_id, token, expires_at))
        conn.commit()
    except pymysql.err.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail='Email already registered')
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')
    finally:
        try:
            conn.close()
        except Exception:
            pass

    frontend_url = os.getenv('FRONTEND_URL', 'https://llms-auto-score-systems.netlify.app').rstrip('/')
    verify_link = f'{frontend_url}/verify-email?token={token}'

    smtp_host = os.getenv('SMTP_HOST')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if smtp_host and smtp_user and smtp_password:
        body = f"""
            <h2>ยินดีต้อนรับสู่ Evaly Score</h2>
            <p>กรุณาคลิกที่ลิงก์ด้านล่างเพื่อยืนยันบัญชีอีเมลของคุณ (ลิงก์มีอายุการใช้งาน 24 ชั่วโมง):</p>
            <p><a href="{verify_link}">{verify_link}</a></p>
        """
        # Non-blocking async background task so registration responds in milliseconds
        asyncio.create_task(asyncio.to_thread(_send_smtp_email_sync, user.email, 'ยืนยันบัญชีอีเมล Evaly Score (Verify Email)', body))

    if _is_local_dev(request):
        print(f'\n========== VERIFY EMAIL ==========')
        print(f'Verify Link: {verify_link}')
        print(f'==================================\n')

    msg_str = 'สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ' if initial_is_verified else 'สมัครสมาชิกสำเร็จ กรุณาตรวจสอบอีเมลเพื่อยืนยันบัญชีของคุณ'
    response = {'message': msg_str}
    if _is_local_dev(request):
        response['dev_verify_link'] = verify_link
    return response

@router.post('/login', response_model=TokenResponse)
async def login(user_data: UserLogin, request: Request, response: Response):
    client_ip = _get_client_ip(request)
    if not check_rate_limit(client_ip, limit=15, window=60):
        raise HTTPException(status_code=429, detail='Too many login attempts. Please wait a minute.')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (user_data.email,))
    user = cursor.fetchone()
    conn.close()
    if not user or not verify_password(user_data.password, user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password',
         headers={'WWW-Authenticate': 'Bearer'})

    require_verification = os.getenv('REQUIRE_EMAIL_VERIFICATION', 'false').lower() in ('true', '1')
    if not user.get('is_verified') and not _is_local_dev(request) and require_verification:
        raise HTTPException(status_code=403, detail='กรุณายืนยันอีเมลก่อนเข้าสู่ระบบ (Please verify your email before logging in)')

    access_token = create_access_token(data={'sub': user['email'], 'token_version': user.get('token_version', 0)})
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60*60*24*7, samesite="lax", path="/")
    user_dict = dict(user)
    user_info = {'id': user_dict['id'], 'email': user_dict['email'], 'name': user_dict['name'], 'role': user_dict['role'],
     'studentId': user_dict.get('student_id'),
     'avatarUrl': user_dict.get('avatar_url'), 'is_verified': user_dict.get('is_verified', 0)}
    return {'access_token': access_token, 'token_type': 'bearer', 'user': user_info}

@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {'message': 'Logged out successfully'}


@router.post('/socket-token')
async def create_socket_token(user: dict = Depends(get_current_user)):
    """Issue a short-lived, signed identity for the notification socket handshake."""
    return {'socket_token': create_access_token(
        {'user_id': user['id'], 'purpose': 'notifications'},
        expires_delta=timedelta(minutes=5),
    )}

@router.get('/me')
async def get_me(user: dict=Depends(get_current_user)):
    return {'id': user['id'], 'email': user['email'], 'name': user['name'], 'role': user['role'],
     'studentId': user['student_id'],
     'avatarUrl': user.get('avatar_url', None), 'is_verified': user.get('is_verified', 0),
     'googleEmail': user.get('google_email', None), 'isGoogleLinked': bool(user.get('google_id'))}

@router.post('/profile/request-password-otp')
async def request_profile_password_otp(request: Request, user: dict = Depends(get_current_user)):
    """Generate and send 6-digit OTP to user's email for password change verification"""
    email = user.get('email')
    if not email:
        raise HTTPException(status_code=400, detail='ไม่พบบัญชีอีเมลของผู้ใช้งาน')
    if not _is_local_dev(request) and not all(os.getenv(key) for key in ('SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD')):
        raise HTTPException(status_code=503, detail='ระบบส่งอีเมลยังไม่พร้อมใช้งาน กรุณาลองใหม่ภายหลัง')

    client_ip = _get_client_ip(request)
    if not check_rate_limit(f"otp_profile:{user['id']}:{client_ip}", limit=5, window=300):
        raise HTTPException(status_code=429, detail="คุณขอรหัส OTP ถี่เกินไป กรุณารอสักครู่แล้วลองใหม่อีกครั้ง")

    otp_code = f"{secrets.randbelow(900000) + 100000}"
    now_utc = datetime.now(timezone.utc)
    expires_at = (now_utc + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM password_resets WHERE user_id = ? AND token LIKE ?", (user['id'], 'otp:%'))
        cursor.execute(
            "INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user['id'], f"otp:{otp_code}", expires_at)
        )
        conn.commit()
    except pymysql.err.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()

    subject = "รหัส OTP สำหรับยืนยันการเปลี่ยนรหัสผ่าน (Evaly Score)"
    html_body = f"""
        <div style="font-family: system-ui, -apple-system, sans-serif; max-width: 500px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <h2 style="color: #0f695b; margin-top: 0; font-size: 20px;">ยืนยันการเปลี่ยนรหัสผ่าน</h2>
            <p style="color: #334155; line-height: 1.5;">เราได้รับการร้องขอให้เปลี่ยนรหัสผ่านสำหรับบัญชี <b>{email}</b></p>
            <p style="color: #334155; line-height: 1.5;">กรุณานำรหัส OTP 6 หลักด้านล่างนี้ไปกรอกในหน้าโปรไฟล์เพื่อยืนยัน:</p>
            <div style="background: #f0fdf4; border: 1px dashed #86efac; padding: 18px; text-align: center; border-radius: 8px; margin: 20px 0;">
                <span style="font-size: 34px; font-weight: bold; letter-spacing: 8px; color: #166534; font-family: monospace;">{otp_code}</span>
            </div>
            <p style="color: #64748b; font-size: 13px; margin-bottom: 4px;">• รหัส OTP นี้มีอายุการใช้งาน 15 นาที</p>
            <p style="color: #64748b; font-size: 13px; margin-top: 0;">• หากคุณไม่ได้เป็นผู้ร้องขอ กรุณาละเว้นอีเมลฉบับนี้</p>
        </div>
    """
    if not _is_local_dev(request):
        delivered = await asyncio.to_thread(_send_smtp_email_sync, email, subject, html_body)
        if not delivered:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM password_resets WHERE user_id = ? AND token = ?', (user['id'], f'otp:{otp_code}'))
            conn.commit()
            conn.close()
            raise HTTPException(status_code=503, detail='ส่งอีเมลยืนยันไม่สำเร็จ กรุณาลองใหม่ภายหลัง')
    else:
        print(f'[Profile password OTP, development only] User ID: {user["id"]}, code: {otp_code}')

    response = {
        "message": f"ส่งรหัส OTP ไปยังอีเมล {email} เรียบร้อยแล้ว (รหัสมีอายุ 15 นาที)"
    }
    if _is_local_dev(request):
        response["dev_otp"] = otp_code
    return response

@router.put('/profile')
async def update_profile(
    request: Request,
    name: str = Form(None),
    student_id: str = Form(None),
    password: str = Form(None),
    otp: str = Form(None),
    avatar: UploadFile = File(None),
    user: dict = Depends(get_current_user)
):
    profile_form = await request.form()
    if 'student_id' in profile_form:
        student_id = str(profile_form['student_id']).strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    update_fields = []
    params = []
    avatar_filename = user.get('avatar_url')

    if avatar:
        file_content = await avatar.read()
        validate_upload_file(file_content, content_type=avatar.content_type)
        avatar_url = upload_to_cloudinary(file_content, folder='avatars')
        if avatar_url:
            avatar_filename = avatar_url

    if name:
        update_fields.append('name = ?')
        params.append(name)
    if student_id is not None:
        update_fields.append('student_id = ?')
        params.append(student_id.strip() or None)

    if password:
        cleaned_password = password.strip()
        if len(cleaned_password) < 8:
            conn.close()
            raise HTTPException(status_code=400, detail="รหัสผ่านใหม่ต้องมีความยาวอย่างน้อย 8 ตัวอักษร")

        if not otp or not otp.strip():
            conn.close()
            raise HTTPException(status_code=400, detail="กรุณากรอกรหัส OTP ที่ได้รับทางอีเมลเพื่อยืนยันการเปลี่ยนรหัสผ่าน")
        if not check_rate_limit(f"otp_profile_verify:{user['id']}", limit=10, window=900):
            conn.close()
            raise HTTPException(status_code=429, detail='ลองรหัส OTP มากเกินไป กรุณารอสักครู่แล้วลองใหม่')

        otp_cleaned = otp.strip()
        cursor.execute(
            "SELECT id, expires_at FROM password_resets WHERE user_id = ? AND token = ? ORDER BY id DESC LIMIT 1",
            (user['id'], f"otp:{otp_cleaned}")
        )
        otp_record = cursor.fetchone()
        if not otp_record:
            conn.close()
            raise HTTPException(status_code=400, detail="รหัส OTP ไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง")

        expires_at = otp_record['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            cursor.execute("DELETE FROM password_resets WHERE id = ?", (otp_record['id'],))
            conn.commit()
            conn.close()
            raise HTTPException(status_code=400, detail="รหัส OTP หมดอายุแล้ว กรุณาขอรหัสใหม่")

        cursor.execute("DELETE FROM password_resets WHERE user_id = ? AND token LIKE ?", (user['id'], 'otp:%'))
        update_fields.append('password = ?')
        params.append(get_password_hash(cleaned_password))
        update_fields.append('token_version = token_version + 1')

    if avatar_filename and avatar_filename != user.get('avatar_url'):
        update_fields.append('avatar_url = ?')
        params.append(avatar_filename)
    if update_fields:
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        params.append(user['id'])
        try:
            cursor.execute(query, tuple(params))
            conn.commit()
        except pymysql.err.Error as e:
            conn.close()
            raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {
        'message': 'Profile updated successfully',
        'avatarUrl': avatar_filename,
        'studentId': (student_id or None) if student_id is not None else user.get('student_id')
    }

@router.post('/set-role')
async def set_role(req: SetRoleRequest, user: dict=Depends(get_current_user)):
    if user['role'] != 'unassigned':
        raise HTTPException(status_code=400, detail='Role already set')
    if req.role not in ['teacher', 'student']:
        raise HTTPException(status_code=400, detail='Invalid role')
    if not req.identity_id:
        raise HTTPException(status_code=400, detail='Identity ID is required')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET role = ?, student_id = ? WHERE id = ?', (req.role, req.identity_id, user['id']))
        conn.commit()
    except pymysql.err.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {'message': 'Role updated successfully', 'role': req.role, 'identity_id': req.identity_id}

@router.post('/forgot-password')
async def forgot_password(req: ForgotPasswordRequest):
    if not check_rate_limit(f"password_reset:{req.email.lower().strip()}", limit=5, window=3600):
        raise HTTPException(status_code=429, detail='ขอรีเซ็ตรหัสผ่านถี่เกินไป กรุณารอสักครู่')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, student_id, email, google_email, is_verified FROM users WHERE email = ? OR google_email = ?', (req.email, req.email))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {'message': 'หากบัญชีนี้มีอีเมลที่ยืนยันแล้ว ระบบจะส่งลิงก์รีเซ็ตให้'}
    if req.name or req.student_id:
        name_matches = bool(req.name and user['name'] and req.name.strip().lower() == user['name'].strip().lower())
        id_matches = bool(req.student_id and user['student_id'] and req.student_id.strip().lower() == user['student_id'].strip().lower())
        if not (name_matches or id_matches):
            conn.close()
            raise HTTPException(status_code=400, detail='คุณไม่ใช่เจ้าของบัญชี ชื่อหรือรหัสนิสิตไม่ตรงกับฐานข้อมูล')
    recovery_email = user['google_email'] or (user['email'] if user['is_verified'] else None)
    if not recovery_email:
        conn.close()
        raise HTTPException(status_code=400, detail='บัญชีนี้ยังไม่มีอีเมลที่ยืนยันแล้วสำหรับกู้คืนรหัสผ่าน')
    if not all(os.getenv(key) for key in ('SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD')):
        conn.close()
        raise HTTPException(status_code=503, detail='ระบบส่งอีเมลยังไม่พร้อมใช้งาน กรุณาลองใหม่ภายหลัง')
    import uuid
    token = uuid.uuid4().hex
    now_utc = datetime.now(timezone.utc)
    expires_at = (now_utc + timedelta(hours=1)).isoformat()
    cursor.execute('DELETE FROM password_resets WHERE user_id = ?', (user['id'],))
    cursor.execute('INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)', (user['id'], token, expires_at))
    conn.commit()
    conn.close()
    frontend_url = os.getenv('FRONTEND_URL', 'https://llms-auto-score-systems.netlify.app').rstrip('/')
    reset_link = f'{frontend_url}/reset-password?token={token}'
    body = f"""
        <h2>รีเซ็ตรหัสผ่าน Evaly Score</h2>
        <p>เราได้รับการร้องขอให้รีเซ็ตรหัสผ่านสำหรับบัญชีของคุณ</p>
        <p>กรุณาคลิกลิงก์ด้านล่างเพื่อตั้งรหัสผ่านใหม่ (ลิงก์มีอายุ 1 ชั่วโมง):</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>หากคุณไม่ได้ร้องขอ กรุณาเพิกเฉยต่ออีเมลฉบับนี้</p>
    """
    if not await asyncio.to_thread(_send_smtp_email_sync, recovery_email, 'รีเซ็ตรหัสผ่าน Evaly Score', body):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM password_resets WHERE user_id = ? AND token = ?', (user['id'], token))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=503, detail='ส่งอีเมลไม่สำเร็จ กรุณาลองใหม่ภายหลัง')
    return {'message': 'หากบัญชีนี้มีอีเมลที่ยืนยันแล้ว ระบบจะส่งลิงก์รีเซ็ตให้'}

@router.post('/reset-password')
async def reset_password(req: ResetPasswordRequest):
    if not re.fullmatch(r'[0-9a-f]{32}', req.token):
        raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM password_resets WHERE token = ?', (req.token,))
    reset_record = cursor.fetchone()
    if not reset_record:
        conn.close()
        raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    from datetime import datetime, timezone
    try:
        expires_at_value = reset_record['expires_at']
        expires_at = expires_at_value if isinstance(expires_at_value, datetime) else datetime.fromisoformat(expires_at_value.replace('Z', '+00:00'))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        if now_utc > expires_at:
            cursor.execute('DELETE FROM password_resets WHERE id = ?', (reset_record['id'],))
            conn.commit()
            conn.close()
            raise HTTPException(status_code=400, detail='Reset token has expired')
    except ValueError:
        pass
    hashed_password = get_password_hash(req.new_password)
    cursor.execute('UPDATE users SET password = ?, token_version = token_version + 1 WHERE id = ?', (hashed_password, reset_record['user_id']))
    client_ip = getattr(req, 'client', None)
    client_ip = client_ip.host if client_ip else 'unknown'
    cursor.execute('DELETE FROM password_resets WHERE id = ?', (reset_record['id'],))
    conn.commit()
    conn.close()
    return {'message': 'Password has been successfully reset'}

@router.post('/account/request-delete-otp')
async def request_delete_account_otp(request: Request, user: dict = Depends(get_current_user)):
    if not user.get('google_id'):
        raise HTTPException(status_code=400, detail='บัญชีนี้ต้องยืนยันด้วยรหัสผ่าน')
    if not _is_local_dev(request) and not all(os.getenv(key) for key in ('SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD')):
        raise HTTPException(status_code=503, detail='ระบบส่งอีเมลยังไม่พร้อมใช้งาน')
    if not check_rate_limit(f"otp_delete:{user['id']}:{_get_client_ip(request)}", limit=5, window=300):
        raise HTTPException(status_code=429, detail='ขอรหัส OTP ถี่เกินไป กรุณารอสักครู่')

    otp_code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM password_resets WHERE user_id = ? AND token LIKE ?", (user['id'], 'delete:%'))
        cursor.execute('INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)',
                       (user['id'], f'delete:{otp_code}', expires_at))
        conn.commit()
    finally:
        conn.close()

    email = user['email']
    subject = 'รหัส OTP สำหรับยืนยันการลบบัญชี Evaly'
    body = (f'<p>มีการขอลบบัญชี {email} อย่างถาวร</p>'
            f'<p>รหัสยืนยันของคุณคือ <b style="font-size:24px">{otp_code}</b></p>'
            '<p>รหัสมีอายุ 15 นาที หากไม่ได้เป็นผู้ร้องขอ กรุณาละเว้นอีเมลนี้</p>')
    if not _is_local_dev(request):
        if not await asyncio.to_thread(_send_smtp_email_sync, email, subject, body):
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM password_resets WHERE user_id = ? AND token = ?',
                               (user['id'], f'delete:{otp_code}'))
                conn.commit()
            finally:
                conn.close()
            raise HTTPException(status_code=503, detail='ส่งอีเมลยืนยันไม่สำเร็จ')
    else:
        print(f'[Delete account OTP, development only] User ID: {user["id"]}, code: {otp_code}')
    result = {'message': f'ส่งรหัส OTP ไปยัง {email} แล้ว'}
    if _is_local_dev(request):
        result['dev_otp'] = otp_code
    return result

@router.delete('/account')
async def delete_account(credentials: DeleteAccountRequest, user: dict=Depends(get_current_user)):
    """Permanently delete an account after fresh password or email OTP verification."""
    if not check_rate_limit(f"account_delete_verify:{user['id']}", limit=10, window=900):
        raise HTTPException(status_code=429, detail='ยืนยันตัวตนผิดหลายครั้ง กรุณารอสักครู่')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password, google_id FROM users WHERE id = ?', (user['id'],))
    account = cursor.fetchone()
    if not account:
        conn.close()
        raise HTTPException(status_code=404, detail='User not found')
    if account['google_id']:
        if not credentials.otp or not credentials.otp.isdigit() or len(credentials.otp) != 6:
            conn.close()
            raise HTTPException(status_code=400, detail='กรุณากรอกรหัส OTP 6 หลัก')
        cursor.execute('SELECT id, expires_at FROM password_resets WHERE user_id = ? AND token = ? ORDER BY id DESC LIMIT 1',
                       (user['id'], f'delete:{credentials.otp}'))
        record = cursor.fetchone()
        if not record:
            conn.close()
            raise HTTPException(status_code=400, detail='รหัส OTP ไม่ถูกต้อง')
        expires_at = record['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            conn.close()
            raise HTTPException(status_code=400, detail='รหัส OTP หมดอายุแล้ว')
    elif not credentials.password or not verify_password(credentials.password, account['password']):
        conn.close()
        raise HTTPException(status_code=400, detail='รหัสผ่านไม่ถูกต้อง')
    try:
        # rooms.teacher_id uses ON DELETE SET NULL, so remove the teacher's
        # rooms first; their exams and submissions cascade from the room.
        cursor.execute('DELETE FROM rooms WHERE teacher_id = ?', (user['id'],))
        cursor.execute('DELETE FROM users WHERE id = ?', (user['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return {'message': 'Account deleted successfully'}

@router.post('/verify-email')
async def verify_email(req: VerifyEmailRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM email_verifications WHERE token = ?', (req.token,))
    record = cursor.fetchone()
    if not record:
        conn.close()
        raise HTTPException(status_code=400, detail='ลิงก์ยืนยันไม่ถูกต้องหรือหมดอายุแล้ว')
    from datetime import datetime, timezone
    try:
        expires_at_value = record['expires_at']
        expires_at = expires_at_value if isinstance(expires_at_value, datetime) else datetime.fromisoformat(expires_at_value.replace('Z', '+00:00'))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            cursor.execute('DELETE FROM email_verifications WHERE id = ?', (record['id'],))
            conn.commit()
            conn.close()
            raise HTTPException(status_code=400, detail='ลิงก์ยืนยันหมดอายุแล้ว')
    except ValueError:
        pass
    cursor.execute('UPDATE users SET is_verified = 1 WHERE id = ?', (record['user_id'],))
    cursor.execute('DELETE FROM email_verifications WHERE user_id = ?', (record['user_id'],))
    conn.commit()
    conn.close()
    return {'message': 'ยืนยันอีเมลสำเร็จ'}

@router.post('/resend-verification')
async def resend_verification(req: ResendVerificationRequest, request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, is_verified FROM users WHERE email = ?', (req.email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {'message': 'หากมีบัญชีนี้ในระบบ ลิงก์ยืนยันจะถูกส่งไปที่อีเมลของคุณ'}
    if user['is_verified'] == 1:
        conn.close()
        raise HTTPException(status_code=400, detail='อีเมลนี้ได้รับการยืนยันแล้ว')
    if not _is_local_dev(request) and not all(os.getenv(key) for key in ('SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD')):
        conn.close()
        raise HTTPException(status_code=503, detail='ระบบส่งอีเมลยังไม่พร้อมใช้งาน กรุณาลองใหม่ภายหลัง')
    import uuid
    from datetime import datetime, timezone, timedelta
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    token = uuid.uuid4().hex
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    cursor.execute('DELETE FROM email_verifications WHERE user_id = ?', (user['id'],))
    cursor.execute('INSERT INTO email_verifications (user_id, token, expires_at) VALUES (?, ?, ?)', (user['id'], token, expires_at))
    conn.commit()
    conn.close()
    frontend_url = os.getenv('FRONTEND_URL', 'https://llms-auto-score-systems.netlify.app').rstrip('/')
    verify_link = f'{frontend_url}/verify-email?token={token}'
    smtp_host = os.getenv('SMTP_HOST')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    if smtp_host and smtp_user and smtp_password:
        body = f"""
            <h2>ยินดีต้อนรับสู่ Evaly Score</h2>
            <p>กรุณาคลิกที่ลิงก์ด้านล่างเพื่อยืนยันบัญชีอีเมลของคุณ (ลิงก์มีอายุการใช้งาน 24 ชั่วโมง):</p>
            <p><a href="{verify_link}">{verify_link}</a></p>
        """
        asyncio.create_task(asyncio.to_thread(_send_smtp_email_sync, req.email, 'ส่งซ้ำ - ยืนยันบัญชีอีเมล Evaly Score (Verify Email)', body))
        return {'message': 'ส่งลิงก์ยืนยันอีเมลสำเร็จ กรุณาตรวจสอบกล่องข้อความ'}

    if _is_local_dev(request):
        print(f'\n========== VERIFY EMAIL ==========')
        print(f'Verify Link: {verify_link}')
        print(f'==================================\n')
        return {'message': 'ส่งลิงก์ยืนยันอีเมลแล้ว', 'dev_verify_link': verify_link}
    raise HTTPException(status_code=503, detail='ระบบส่งอีเมลยังไม่พร้อมใช้งาน กรุณาลองใหม่ภายหลัง')

@router.post('/firebase-login', response_model=TokenResponse)
async def firebase_login(request: FirebaseLoginRequest, req: Request, res: Response):
    """
    Verify Firebase ID token and:
    - Rule: 1 Google Account -> Exactly 1 Web Account
    - If user exists by google_id or google_email or email, log in directly.
    - If brand new user, create user with role 'unassigned' so they select role.
    """
    firebase_auth = get_firebase_auth()
    if firebase_auth is None:
        raise HTTPException(status_code=503, detail='Firebase Admin SDK not configured')
    try:
        decoded_token = firebase_auth.verify_id_token(request.firebase_token)
        google_uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        display_name = decoded_token.get('name', decoded_token.get('display_name', 'User'))
        google_picture = decoded_token.get('picture', None)
        if not email or not google_uid:
            raise HTTPException(status_code=400, detail='Email not available from Google account')
    except firebase_auth.InvalidIdTokenError as e:
        print(f'[Firebase] Invalid token: {e}')
        raise HTTPException(status_code=401, detail='Invalid Firebase token')
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail='Firebase token has expired')
    except Exception as e:
        print(f'[Firebase Verify Error] {e}')
        raise HTTPException(status_code=401, detail='Failed to verify Firebase token')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Search for user already linked by google_id or google_email
    cursor.execute('SELECT * FROM users WHERE google_id = ? OR google_email = ?', (google_uid, email))
    user = cursor.fetchone()

    # 2. If not found by google_id/google_email, search by primary email
    if not user:
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            user_dict = dict(user)
            # If this existing user has a different google_id, block conflict
            if user_dict.get('google_id') and user_dict.get('google_id') != google_uid:
                conn.close()
                raise HTTPException(status_code=400, detail='อีเมลนี้ถูกผูกไว้กับบัญชี Google อื่นอยู่แล้ว')
            # Link this existing account to this Google account (1-to-1)
            cursor.execute('UPDATE users SET google_id = ?, google_email = ?, is_verified = 1 WHERE id = ?',
                           (google_uid, email, user_dict['id']))
            conn.commit()

    if user:
        user_dict = dict(user)
        # Ensure google_id/google_email is set on the user record if missing
        if not user_dict.get('google_id') or not user_dict.get('google_email'):
            cursor.execute('UPDATE users SET google_id = ?, google_email = ?, is_verified = 1 WHERE id = ?',
                           (google_uid, email, user_dict['id']))
            conn.commit()

        existing_avatar = user_dict.get('avatar_url')
        if google_picture and google_picture != existing_avatar:
            cursor.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (google_picture, user_dict['id']))
            conn.commit()
        conn.close()

        access_token = create_access_token(data={'sub': user_dict['email'], 'token_version': user_dict.get('token_version', 0)})
        res.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60*60*24*7, samesite="lax", path="/")
        user_info = {
            'id': user_dict['id'],
            'email': user_dict['email'],
            'name': user_dict['name'],
            'role': user_dict['role'],
            'studentId': user_dict.get('student_id'),
            'avatarUrl': google_picture or existing_avatar,
            'is_verified': user_dict.get('is_verified', 1),
            'googleEmail': email,
            'isGoogleLinked': True
        }
        return {'access_token': access_token, 'token_type': 'bearer', 'user': user_info}

    # 3. New user: Create new web account bound 1-to-1 with this Google account
    try:
        cursor.execute(
            'INSERT INTO users (email, password, name, role, student_id, avatar_url, is_verified, google_id, google_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (email, f"firebase_{google_uid}", display_name, 'unassigned', None, google_picture, 1, google_uid, email)
        )
        conn.commit()
        new_user_id = cursor.lastrowid
    except pymysql.err.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail='อีเมลนี้มีผู้ใช้งานในระบบแล้ว')

    user_info = {
        'id': new_user_id,
        'email': email,
        'name': display_name,
        'role': 'unassigned',
        'studentId': None,
        'avatarUrl': google_picture,
        'is_verified': 1,
        'googleEmail': email,
        'isGoogleLinked': True
    }
    access_token = create_access_token(data={'sub': email, 'token_version': 0})
    res.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60*60*24*7, samesite="lax", path="/")
    conn.close()
    return {'access_token': access_token, 'token_type': 'bearer', 'user': user_info}


@router.post('/link-google')
async def link_google(request: FirebaseLoginRequest, current_user: dict=Depends(get_current_user)):
    firebase_auth = get_firebase_auth()
    if firebase_auth is None:
        raise HTTPException(status_code=503, detail='Firebase SDK ไม่พร้อมใช้งาน')
    try:
        decoded_token = firebase_auth.verify_id_token(request.firebase_token)
        google_uid = decoded_token.get('uid')
        google_email = decoded_token.get('email')
        google_picture = decoded_token.get('picture', None)
        if not google_uid or not google_email:
            raise HTTPException(status_code=400, detail='ไม่พบบัญชีอีเมลจาก Google')
    except Exception as e:
        raise HTTPException(status_code=401, detail='ยืนยันบัญชี Google ไม่สำเร็จ')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Read the current link from the database while locking this account, so a
    # stale auth snapshot or concurrent request cannot replace its Google UID.
    cursor.execute('SELECT google_id, avatar_url FROM users WHERE id = ? FOR UPDATE', (current_user['id'],))
    linked_user = cursor.fetchone()
    if not linked_user:
        conn.close()
        raise HTTPException(status_code=404, detail='ไม่พบบัญชีผู้ใช้')
    if linked_user['google_id'] and linked_user['google_id'] != google_uid:
        conn.close()
        raise HTTPException(status_code=400, detail='บัญชีของคุณได้ผูกกับ Google อื่นไปแล้ว ไม่สามารถเปลี่ยนได้')

    # Rule: Google 1 account -> Exactly 1 web account.
    # Check if this Google account is already linked to ANY OTHER user
    cursor.execute('SELECT id, email, name FROM users WHERE (google_id = ? OR google_email = ?) AND id != ?',
                   (google_uid, google_email, current_user['id']))
    existing_link = cursor.fetchone()
    if existing_link:
        conn.close()
        raise HTTPException(status_code=400, detail='บัญชี Google นี้ถูกผูกกับบัญชีอื่นในระบบแล้ว (1 บัญชี Google ผูกได้ 1 บัญชีเว็บเท่านั้น)')

    cursor.execute('UPDATE users SET google_id = ?, google_email = ?, is_verified = 1 WHERE id = ?',
                   (google_uid, google_email, current_user['id']))
    if google_picture and (not linked_user['avatar_url']):
        cursor.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (google_picture, current_user['id']))
    conn.commit()
    conn.close()
    return {'message': 'เชื่อมโยงบัญชี Google สำเร็จ', 'googleEmail': google_email}
