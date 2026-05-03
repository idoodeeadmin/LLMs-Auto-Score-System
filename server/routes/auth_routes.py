from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File, Form, Request
import pymysql
import uuid
import smtplib
from datetime import datetime, timezone, timedelta
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from server.database import get_db_connection
from server.auth import get_password_hash, verify_password, create_access_token, decode_token
from server.models import *
from server.utils import check_rate_limit, _firebase_app, auth, upload_to_cloudinary, get_current_user, log_audit_action
import firebase_admin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post('/register')
async def register(user: UserRegister, request: Request):
    client_ip = request.client.host if request.client else 'unknown'
    if not check_rate_limit(client_ip, limit=5, window=3600):
        raise HTTPException(status_code=429, detail='Too many registration attempts. Please try again later.')
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = get_password_hash(user.password)
    try:
        cursor.execute('INSERT INTO users (email, password, name, role, student_id, is_verified) VALUES (?, ?, ?, ?, ?, 0)', (user.email, hashed_password, user.name, 'unassigned', None))
        user_id = cursor.lastrowid
        import uuid
        from datetime import datetime, timezone, timedelta
        import os, smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        token = uuid.uuid4().hex
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        cursor.execute('INSERT INTO email_verifications (user_id, token, expires_at) VALUES (?, ?, ?)', (user_id, token, expires_at))
        conn.commit()
    except pymysql.err.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail='Email already registered')
    verify_link = f'http://localhost:8080/verify-email?token={token}'
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port_str = os.getenv('SMTP_PORT', '587')
    smtp_port = int(smtp_port_str) if smtp_port_str else 587
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    dev_verify_link = None
    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = f'Evaly Score <{smtp_user}>'
            msg['To'] = user.email
            msg['Subject'] = 'ยืนยันบัญชีอีเมล Evaly Score (Verify Email)'
            body = f'\n            <h2>ยินดีต้อนรับสู่ Evaly Score</h2>\n            <p>กรุณาคลิกที่ลิงก์ด้านล่างเพื่อยืนยันบัญชีอีเมลของคุณ (ลิงก์มีอายุการใช้งาน 24 ชั่วโมง):</p>\n            <p><a href="{verify_link}">{verify_link}</a></p>\n            '
            msg.attach(MIMEText(body, 'html'))
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f'\n[Verify Email Error] Failed to send email: {e}')
            dev_verify_link = verify_link
    else:
        dev_verify_link = verify_link
    conn.close()
    if dev_verify_link:
        print(f'\n========== VERIFY EMAIL ==========')
        print(f'Verify Link: {dev_verify_link}')
        print(f'==================================\n')
    return {'message': 'สมัครสมาชิกสำเร็จ กรุณาตรวจสอบอีเมลเพื่อยืนยันบัญชีของคุณ', 'dev_verify_link': dev_verify_link}

@router.post('/login', response_model=TokenResponse)
async def login(user_data: UserLogin, request: Request):
    client_ip = request.client.host if request.client else 'unknown'
    if not check_rate_limit(client_ip, limit=10, window=60):
        raise HTTPException(status_code=429, detail='Too many login attempts. Please wait a minute.')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (user_data.email,))
    user = cursor.fetchone()
    conn.close()
    if not user or not verify_password(user_data.password, user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password', headers={'WWW-Authenticate': 'Bearer'})
    access_token = create_access_token(data={'sub': user['email'], 'token_version': user.get('token_version', 0)})
    client_ip = request.client.host if request.client else 'unknown'
    log_audit_action(user['id'], 'LOGIN', None, 'User logged in via email', client_ip)
    user_dict = dict(user)
    user_info = {'id': user_dict['id'], 'email': user_dict['email'], 'name': user_dict['name'], 'role': user_dict['role'], 'studentId': user_dict.get('student_id'), 'avatarUrl': user_dict.get('avatar_url'), 'is_verified': user_dict.get('is_verified', 0)}
    return {'access_token': access_token, 'token_type': 'bearer', 'user': user_info}

@router.get('/me')
async def get_me(user: dict=Depends(get_current_user)):
    return {'id': user['id'], 'email': user['email'], 'name': user['name'], 'role': user['role'], 'studentId': user['student_id'], 'avatarUrl': user.get('avatar_url', None), 'is_verified': user.get('is_verified', 0)}

@router.put('/profile')
async def update_profile(name: str=Form(None), password: str=Form(None), avatar: UploadFile=File(None), user: dict=Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    update_fields = []
    params = []
    avatar_filename = user.get('avatar_url')
    
    if avatar:
        file_content = await avatar.read()
        avatar_url = upload_to_cloudinary(file_content, folder='avatars')
        if avatar_url:
            avatar_filename = avatar_url

    if name:
        update_fields.append('name = ?')
        params.append(name)
    if password:
        update_fields.append('password = ?')
        params.append(get_password_hash(password))
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
    return {'message': 'Profile updated successfully', 'avatarUrl': avatar_filename}

@router.post('/set-role')
async def set_role(req: SetRoleRequest, user: dict=Depends(get_current_user)):
    if user['role'] != 'unassigned':
        raise HTTPException(status_code=400, detail='Role already set')
    if req.role not in ['teacher', 'student']:
        raise HTTPException(status_code=400, detail='Invalid role')
    if req.role == 'student' and (not req.student_id):
        raise HTTPException(status_code=400, detail='Student ID is required for students')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET role = ?, student_id = ? WHERE id = ?', (req.role, req.student_id, user['id']))
        conn.commit()
    except pymysql.err.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {'message': 'Role updated successfully', 'role': req.role, 'student_id': req.student_id}

@router.post('/forgot-password')
async def forgot_password(req: ForgotPasswordRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, student_id FROM users WHERE email = ?', (req.email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {'message': 'If that email exists, a password reset link has been generated.'}
    if req.name or req.student_id:
        is_owner = False
        if req.name and user['name'] and (req.name.strip().lower() == user['name'].strip().lower()):
            is_owner = True
        elif req.student_id and user['student_id'] and (req.student_id.strip().lower() == user['student_id'].strip().lower()):
            is_owner = True
        if not is_owner:
            conn.close()
            raise HTTPException(status_code=400, detail='คุณไม่ใช่เจ้าของบัญชี ชื่อหรือรหัสนิสิตไม่ตรงกับฐานข้อมูล')
        import uuid
        from datetime import datetime, timezone, timedelta
        token = uuid.uuid4().hex
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        cursor.execute('DELETE FROM password_resets WHERE user_id = ?', (user['id'],))
        cursor.execute('INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)', (user['id'], token, expires_at))
        conn.commit()
        conn.close()
        return {'message': 'ยืนยันตัวตนสำเร็จ!', 'reset_token': token}
    import uuid
    from datetime import datetime, timezone, timedelta
    token = uuid.uuid4().hex
    now_utc = datetime.now(timezone.utc)
    expires_at = (now_utc + timedelta(hours=1)).isoformat()
    cursor.execute('DELETE FROM password_resets WHERE user_id = ?', (user['id'],))
    cursor.execute('INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)', (user['id'], token, expires_at))
    conn.commit()
    conn.close()
    reset_link = f'http://localhost:8080/reset-password?token={token}'
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import os
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port_str = os.getenv('SMTP_PORT', '587')
    smtp_port = int(smtp_port_str) if smtp_port_str else 587
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    error_msg = None
    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = f'Evaly Score <{smtp_user}>'
            msg['To'] = req.email
            msg['Subject'] = 'รีเซ็ตรหัสผ่าน Evaly Score (Password Reset)'
            body = f'\n            <h2>รีเซ็ตรหัสผ่าน Evaly Score</h2>\n            <p>เราได้รับการร้องขอให้รีเซ็ตรหัสผ่านสำหรับบัญชีของคุณ</p>\n            <p>กรุณาคลิกที่ลิงก์ด้านล่างเพื่อตั้งรหัสผ่านใหม่ (ลิงก์นี้มีอายุการใช้งาน 1 ชั่วโมง):</p>\n            <p><a href="{reset_link}">{reset_link}</a></p>\n            <p><br>หากคุณไม่ได้ร้องขอการรีเซ็ตรหัสผ่านนี้ กรุณาเพิกเฉยต่ออีเมลฉบับนี้</p>\n            '
            msg.attach(MIMEText(body, 'html'))
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            print(f'\n[Email Sent] Password reset link sent to {req.email}')
            return {'message': 'ส่งลิงก์สำหรับรีเซ็ตรหัสผ่านไปยังอีเมลของคุณแล้ว กรุณาตรวจสอบกล่องข้อความ'}
        except Exception as e:
            print(f'\n[Email Error] Failed to send email: {e}')
            error_msg = str(e)
    print(f'\n========== FORGOT PASSWORD ==========')
    print(f'Request for: {req.email}')
    print(f'Reset Link: {reset_link}')
    if error_msg:
        print(f'SMTP Error: {error_msg}')
    elif not smtp_host:
        print('Note: SMTP variables not configured in .env')
    print(f'======================================\n')
    return {'message': 'รหัสสำหรับการทดสอบ (Dev Mode): ระบบยังไม่ได้ตั้งค่า Email SMTP', 'dev_reset_link': reset_link}

@router.post('/reset-password')
async def reset_password(req: ResetPasswordRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM password_resets WHERE token = ?', (req.token,))
    reset_record = cursor.fetchone()
    if not reset_record:
        conn.close()
        raise HTTPException(status_code=400, detail='Invalid or expired reset token')
    from datetime import datetime, timezone
    try:
        expires_at_str = reset_record['expires_at']
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
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
    client_ip = req.client.host if getattr(req, 'client', None) else 'unknown'
    log_audit_action(reset_record['user_id'], 'PASSWORD_RESET', None, 'User reset their password (all sessions revoked)', client_ip)
    cursor.execute('DELETE FROM password_resets WHERE id = ?', (reset_record['id'],))
    conn.commit()
    conn.close()
    return {'message': 'Password has been successfully reset'}

@router.delete('/account')
async def delete_account(user: dict=Depends(get_current_user)):
    """Permanently delete user account and all associated data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE id = ?', (user['id'],))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail='User not found')
    cursor.execute('DELETE FROM users WHERE id = ?', (user['id'],))
    conn.commit()
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
        expires_at_str = record['expires_at']
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
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
async def resend_verification(req: ResendVerificationRequest):
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
    import uuid
    from datetime import datetime, timezone, timedelta
    import os, smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    token = uuid.uuid4().hex
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    cursor.execute('DELETE FROM email_verifications WHERE user_id = ?', (user['id'],))
    cursor.execute('INSERT INTO email_verifications (user_id, token, expires_at) VALUES (?, ?, ?)', (user['id'], token, expires_at))
    conn.commit()
    conn.close()
    verify_link = f'http://localhost:8080/verify-email?token={token}'
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port_str = os.getenv('SMTP_PORT', '587')
    smtp_port = int(smtp_port_str) if smtp_port_str else 587
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    dev_verify_link = None
    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = f'Evaly Score <{smtp_user}>'
            msg['To'] = req.email
            msg['Subject'] = 'ส่งซ้ำ - ยืนยันบัญชีอีเมล Evaly Score (Verify Email)'
            body = f'\n            <h2>ยินดีต้อนรับสู่ Evaly Score</h2>\n            <p>กรุณาคลิกที่ลิงก์ด้านล่างเพื่อยืนยันบัญชีอีเมลของคุณ (ลิงก์มีอายุการใช้งาน 24 ชั่วโมง):</p>\n            <p><a href="{verify_link}">{verify_link}</a></p>\n            '
            msg.attach(MIMEText(body, 'html'))
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            print(f'\n[Email Sent] Verification link resent to {req.email}')
            return {'message': 'ส่งลิงก์ยืนยันอีเมลสำเร็จ กรุณาตรวจสอบกล่องข้อความ'}
        except Exception as e:
            print(f'\n[Email Error] Failed to send email: {e}')
            dev_verify_link = verify_link
    else:
        dev_verify_link = verify_link
    if dev_verify_link:
        print(f'\n========== VERIFY EMAIL ==========')
        print(f'Verify Link: {dev_verify_link}')
        print(f'==================================\n')
        return {'message': 'Dev Mode', 'dev_verify_link': dev_verify_link}
    return {'message': 'หากมีบัญชีนี้ในระบบ ลิงก์ยืนยันจะถูกส่งไปที่อีเมลของคุณ'}

@router.post('/firebase-login', response_model=TokenResponse)
async def firebase_login(request: FirebaseLoginRequest, req: Request):
    """
    Verify Firebase ID token and either:
    - Find existing user by email and log them in
    - Create new user account if email doesn't exist (default to 'student' role)
    """
    if not _firebase_app:
        raise HTTPException(status_code=500, detail='Firebase Admin SDK not configured')
    try:
        decoded_token = auth.verify_id_token(request.firebase_token)
        email = decoded_token.get('email')
        display_name = decoded_token.get('name', decoded_token.get('display_name', 'User'))
        google_picture = decoded_token.get('picture', None)
        if not email:
            raise HTTPException(status_code=400, detail='Email not available from Google account')
    except auth.InvalidIdTokenError as e:
        print(f'[Firebase] Invalid token: {e}')
        raise HTTPException(status_code=401, detail='Invalid Firebase token')
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail='Firebase token has expired')
    except Exception as e:
        print(f'[Firebase Verify Error] {e}')
        raise HTTPException(status_code=401, detail='Failed to verify Firebase token')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user:
        user_dict = dict(user)
        existing_avatar = user_dict.get('avatar_url')
        if google_picture and google_picture != existing_avatar:
            cursor.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (google_picture, user_dict['id']))
            conn.commit()
        conn.close()
        access_token = create_access_token(data={'sub': email, 'token_version': user.get('token_version', 0)})
        client_ip = req.client.host if getattr(req, 'client', None) else 'unknown'
        log_audit_action(user['id'], 'LOGIN', None, 'User logged in via Firebase', client_ip)
        user_info = {'id': user_dict['id'], 'email': user_dict['email'], 'name': user_dict['name'], 'role': user_dict['role'], 'studentId': user_dict.get('student_id'), 'avatarUrl': google_picture or existing_avatar}
        return {'access_token': access_token, 'token_type': 'bearer', 'user': user_info}
    try:
        cursor.execute('INSERT INTO users (email, password, name, role, student_id, avatar_url, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?)', (email, f"firebase_{decoded_token.get('uid', '')}", display_name, 'unassigned', None, google_picture, 1))
        conn.commit()
        new_user_id = cursor.lastrowid
    except pymysql.err.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail='Email already registered')
    user_info = {'id': new_user_id, 'email': email, 'name': display_name, 'role': 'unassigned', 'studentId': None, 'avatarUrl': google_picture}
    access_token = create_access_token(data={'sub': email, 'token_version': 0})
    client_ip = req.client.host if getattr(req, 'client', None) else 'unknown'
    log_audit_action(new_user_id, 'REGISTER', None, 'User registered via Firebase', client_ip)
    conn.close()
    return {'access_token': access_token, 'token_type': 'bearer', 'user': user_info}

@router.post('/link-google')
async def link_google(request: FirebaseLoginRequest, current_user: dict=Depends(get_current_user)):
    if not _firebase_app:
        raise HTTPException(status_code=500, detail='Firebase SDK ไม่พร้อมใช้งาน')
    try:
        decoded_token = auth.verify_id_token(request.firebase_token)
        google_picture = decoded_token.get('picture', None)
    except Exception as e:
        raise HTTPException(status_code=401, detail='ยืนยันบัญชี Google ไม่สำเร็จ')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_verified = 1 WHERE id = ?', (current_user['id'],))
    if google_picture and (not current_user.get('avatar_url')):
        cursor.execute('UPDATE users SET avatar_url = ? WHERE id = ?', (google_picture, current_user['id']))
    conn.commit()
    conn.close()
    return {'message': 'เชื่อมโยงบัญชี Google สำเร็จ'}

