import io

tables = {
    "users (ข้อมูลผู้ใช้)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิงข้อมูลผู้ใช้", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "email", "type": "TEXT", "desc": "ที่อยู่อีเมล", "ex": "student@email.com", "const": "Unique, Not null"},
        {"col": "password", "type": "TEXT", "desc": "รหัสผ่านที่เข้ารหัสแล้ว (Hashed)", "ex": "pbkdf2:sha256...", "const": "Not null"},
        {"col": "name", "type": "TEXT", "desc": "ชื่อ-นามสกุล", "ex": "สมชาย ใจดี", "const": "Not null"},
        {"col": "role", "type": "TEXT", "desc": "ระดับสิทธิ์การใช้งาน (unassigned, teacher, student)", "ex": "student", "const": "Not null"},
        {"col": "student_id", "type": "TEXT", "desc": "รหัสนักศึกษา/รหัสประจำตัว", "ex": "64010123", "const": "Null"},
        {"col": "avatar_url", "type": "TEXT", "desc": "รูปโปรไฟล์ผู้ใช้", "ex": "avatar1.png", "const": "Null"},
        {"col": "is_verified", "type": "INTEGER", "desc": "สถานะการยืนยันอีเมล (0=ยัง, 1=ยืนยันแล้ว)", "ex": "1", "const": "Default 0"}
    ],
    "rooms (ข้อมูลห้องเรียน)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิงห้องเรียน", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "name", "type": "TEXT", "desc": "ชื่อห้องเรียน/รายวิชา", "ex": "วิศวกรรมซอฟต์แวร์ 101", "const": "Not null"},
        {"col": "section", "type": "TEXT", "desc": "กลุ่มเรียน (Section)", "ex": "Sec 1", "const": "Null"},
        {"col": "class_code", "type": "TEXT", "desc": "รหัสเข้าร่วมห้องเรียน", "ex": "XY89AB", "const": "Unique, Not null"},
        {"col": "owner_id", "type": "INTEGER", "desc": "รหัสผู้สร้างห้องเรียน (ผู้สอน)", "ex": "2", "const": "FK -> users(id), Null"}
    ],
    "enrollments (ข้อมูลการเข้าร่วมห้องเรียน)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิงการเข้าร่วม", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "user_id", "type": "INTEGER", "desc": "รหัสผู้ใช้ (นักเรียน)", "ex": "5", "const": "FK -> users(id), Not null, Unique (with room_id)"},
        {"col": "room_id", "type": "INTEGER", "desc": "รหัสห้องเรียน", "ex": "1", "const": "FK -> rooms(id), Not null, Unique (with user_id)"},
        {"col": "joined_at", "type": "DATETIME", "desc": "วันและเวลาที่เข้าร่วม", "ex": "2026-02-15 10:30:00", "const": "Default CURRENT_TIMESTAMP"}
    ],
    "exams (ข้อมูลแบบทดสอบ/ข้อสอบ)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิงข้อสอบ", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "room_id", "type": "INTEGER", "desc": "รหัสห้องเรียน", "ex": "1", "const": "FK -> rooms(id), Not null"},
        {"col": "title", "type": "TEXT", "desc": "หัวข้อข้อสอบ", "ex": "สอบกลางภาค", "const": "Not null"},
        {"col": "description", "type": "TEXT", "desc": "คำอธิบายข้อสอบ", "ex": "ข้อสอบอัตนัย 5 ข้อ", "const": "Null"},
        {"col": "total_score", "type": "REAL", "desc": "คะแนนเต็มรวม", "ex": "50.0", "const": "Default 0"},
        {"col": "start_date", "type": "TEXT", "desc": "วันเวลาที่เริ่มทำข้อสอบได้", "ex": "2026-03-01 09:00", "const": "Null"},
        {"col": "end_date", "type": "TEXT", "desc": "วันเวลาที่หมดเขตทำข้อสอบ", "ex": "2026-03-01 12:00", "const": "Null"},
        {"col": "created_at", "type": "DATETIME", "desc": "วันและเวลาที่สร้าง", "ex": "2026-02-20 14:00", "const": "Default CURRENT_TIMESTAMP"}
    ],
    "questions (ข้อมูลคำถาม)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิงคำถาม", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "exam_id", "type": "INTEGER", "desc": "รหัสข้อสอบ", "ex": "1", "const": "FK -> exams(id), Not null"},
        {"col": "text", "type": "TEXT", "desc": "เนื้อหาคำถาม/โจทย์", "ex": "จงอธิบายวัฏจักร SDLC", "const": "Not null"},
        {"col": "score", "type": "REAL", "desc": "คะแนนเต็มของข้อนี้", "ex": "10.0", "const": "Default 0"},
        {"col": "answer_key", "type": "TEXT", "desc": "แนวคำตอบ/เฉลย", "ex": "ประกอบด้วย Planning, Analysis...", "const": "Null"},
        {"col": "rubrics", "type": "TEXT", "desc": "เกณฑ์การให้คะแนนรูบริค (JSON)", "ex": "[{'criteria': 'ความถูกต้อง', 'score': 5}]", "const": "Null"},
        {"col": "order_index", "type": "INTEGER", "desc": "ลำดับของข้อคำถาม", "ex": "1", "const": "Default 0"},
        {"col": "image_path", "type": "TEXT", "desc": "รูปภาพประกอบโจทย์", "ex": "q1_img.png", "const": "Null"},
        {"col": "image_paths", "type": "TEXT", "desc": "รายการรูปภาพประกอบ (JSON Array)", "ex": "['img1.png', 'img2.png']", "const": "Null"}
    ],
    "submissions (ข้อมูลการส่งคำตอบ)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิงการส่งงาน", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "exam_id", "type": "INTEGER", "desc": "รหัสข้อสอบ", "ex": "1", "const": "FK -> exams(id), Not null, Unique (with student_id)"},
        {"col": "student_id", "type": "INTEGER", "desc": "รหัสนักเรียนที่ส่งคำตอบ", "ex": "5", "const": "FK -> users(id), Not null, Unique (with exam_id)"},
        {"col": "status", "type": "TEXT", "desc": "สถานะการส่ง (missing, submitted, graded)", "ex": "graded", "const": "Default 'missing'"},
        {"col": "total_score", "type": "REAL", "desc": "คะแนนรวมที่ได้รับ", "ex": "45.5", "const": "Default 0"},
        {"col": "submitted_at", "type": "DATETIME", "desc": "วันเวลาที่กดส่งคำตอบ", "ex": "2026-03-01 10:45:00", "const": "Null"},
        {"col": "graded_by_ai", "type": "INTEGER", "desc": "สถานะการประเมินด้วย AI (0=ยัง, 1=ประเมินแล้ว)", "ex": "1", "const": "Default 0"}
    ],
    "submission_answers (ข้อมูลคำตอบรายข้อ)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิงคำตอบรายข้อ", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "submission_id", "type": "INTEGER", "desc": "รหัสการส่งงานรวม", "ex": "1", "const": "FK -> submissions(id), Not null, Unique (with question_id)"},
        {"col": "question_id", "type": "INTEGER", "desc": "รหัสคำถาม", "ex": "1", "const": "FK -> questions(id), Not null, Unique (with submission_id)"},
        {"col": "answer_text", "type": "TEXT", "desc": "ข้อความคำตอบที่นักเรียนพิมพ์", "ex": "SDLC มี 5 ขั้นตอน...", "const": "Null"},
        {"col": "ai_score", "type": "REAL", "desc": "คะแนนที่ AI ประเมินได้", "ex": "8.5", "const": "Default 0"},
        {"col": "ai_feedback", "type": "TEXT", "desc": "คอมเมนต์อธิบายจาก AI", "ex": "ขาดการอธิบายขั้นตอนที่ 3", "const": "Null"},
        {"col": "ai_confidence", "type": "TEXT", "desc": "ระดับความมั่นใจของ AI (low, medium, high)", "ex": "high", "const": "Default 'medium'"},
        {"col": "teacher_score", "type": "REAL", "desc": "คะแนนที่ผู้สอนปรับแก้ขั้นสุดท้าย", "ex": "9.0", "const": "Null"},
        {"col": "teacher_comment", "type": "TEXT", "desc": "คอมเมนต์จากผู้สอน", "ex": "อธิบายได้ดีมาก แต่เพิ่มน้ำขิงหน่อย", "const": "Null"},
        {"col": "image_path", "type": "TEXT", "desc": "รูปภาพประกอบคำตอบ (ถ้ามี)", "ex": "ans_1.png", "const": "Null"},
        {"col": "image_paths", "type": "TEXT", "desc": "รายการรูปภาพประกอบคำตอบ (JSON Array)", "ex": "['ans_img1.png']", "const": "Null"}
    ],
    "password_resets (ข้อมูลคำขอรีเซ็ตรหัสผ่าน)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิง", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "user_id", "type": "INTEGER", "desc": "รหัสผู้ใช้งาน", "ex": "3", "const": "FK -> users(id), Not null"},
        {"col": "token", "type": "TEXT", "desc": "รหัสโทเคนสำหรับรีเซ็ต", "ex": "abc123xyz...", "const": "Unique, Not null"},
        {"col": "expires_at", "type": "DATETIME", "desc": "เวลาหมดอายุของโทเคน", "ex": "2026-02-16 12:00:00", "const": "Not null"}
    ],
    "email_verifications (ข้อมูลโทเคนยืนยันอีเมล)": [
        {"col": "id", "type": "INTEGER", "desc": "รหัสอ้างอิง", "ex": "1", "const": "PK, Auto Increment"},
        {"col": "user_id", "type": "INTEGER", "desc": "รหัสผู้ใช้งาน", "ex": "5", "const": "FK -> users(id), Not null"},
        {"col": "token", "type": "TEXT", "desc": "รหัสโทเคนสำหรับยืนยันอีเมล", "ex": "def456uvw...", "const": "Unique, Not null"},
        {"col": "expires_at", "type": "DATETIME", "desc": "เวลาหมดอายุของโทเคน", "ex": "2026-02-16 12:00:00", "const": "Not null"}
    ]
}

html_tables = ""
index = 1
for table_name, columns in tables.items():
    rows_html = ""
    for col in columns:
        rows_html += f'''
        <tr>
            <td>{col["col"]}</td>
            <td>{col["type"]}</td>
            <td>{col["desc"]}</td>
            <td>{col["ex"]}</td>
            <td>{col["const"]}</td>
        </tr>'''
    
    table_block = f'''
    <div style="page-break-inside: avoid;">
    <h3 style="color: #000; margin-top: 30px; font-weight: normal; margin-bottom: 10px;">ตารางที่ 3.{3 + index} {table_name}</h3>
    <table>
        <tr>
            <th style="width: 15%; background-color: #BFBFBF;">Column</th>
            <th style="width: 15%; background-color: #BFBFBF;">Type</th>
            <th style="width: 35%; background-color: #BFBFBF;">Description</th>
            <th style="width: 20%; background-color: #BFBFBF;">Example</th>
            <th style="width: 15%; background-color: #BFBFBF;">Constraint</th>
        </tr>
        {rows_html}
    </table>
    </div>
    '''
    html_tables += table_block
    index += 1

html_template = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>3.6 การออกแบบฐานข้อมูล (Database Design)</title>
    <style>
        body {{ font-family: 'Sarabun', Tahoma, sans-serif; padding: 40px; background-color: #ffffff; color: #000; max-width: 900px; margin: 0 auto; }}
        h2 {{ text-align: left; font-size: 18px; margin-bottom: 20px; font-weight: normal; color: #000; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 15px; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #000; padding: 10px 15px; vertical-align: top; text-align: left; }}
        th {{ font-weight: normal; }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <h2>3.6 การออกแบบฐานข้อมูล (Database Design)</h2>
    {html_tables}
</body>
</html>
'''

with io.open('database_dictionary_evaly.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
print("Generated database_dictionary_evaly.html successfully!")
