# 🚀 Evaly: LLMs Auto Score System

Evaly เป็นระบบตรวจข้อสอบอัตโนมัติที่ใช้พลังของ Generative AI (Google Gemini) ในการวิเคราะห์และให้คะแนนคำตอบแบบบรรยาย (Essay) พร้อมระบบจัดการห้องเรียนที่ครบวงจร

## ✨ ฟีเจอร์เด่น (Key Features)
- **AI Auto-Grading**: ตรวจข้อสอบอัตโนมัติด้วย AI พร้อมให้ Feedback และวิเคราะห์ความมั่นใจ (Confidence Score)
- **Multimodal Support**: รองรับการส่งคำตอบทั้งรูปแบบข้อความและ "รูปภาพ" โดย AI สามารถอ่านลายมือจากรูปภาพมาตรวจได้
- **Auto-rubric Generation**: AI ช่วยสร้างเกณฑ์การให้คะแนน (Rubrics) และธงคำตอบอัตโนมัติจากโจทย์
- **Classroom Management**: ระบบจัดการห้องเรียน, สมาชิก, และประกาศข่าวสาร
- **Cloud Storage**: จัดเก็บรูปภาพทั้งหมดไว้บน Cloudinary อย่างปลอดภัย
- **Infrastructure Ready**: รองรับ Docker Compose และมีระบบ CI/CD (GitHub Actions) ตรวจสอบโค้ดอัตโนมัติ

---

## 🛠️ เทคโนโลยีที่ใช้ (Tech Stack)
- **Frontend**: React 18, Vite, TailwindCSS, Radix UI
- **Backend**: FastAPI (Python 3.11)
- **Real-time**: Node.js & Socket.io
- **Database**: TiDB (MySQL Compatible)
- **AI**: Google Gemini Pro (Vision & Text)
- **Storage**: Cloudinary

---

## 🚀 วิธีการรันโปรเจกต์ (Getting Started)

### วิธีที่ 1: รันผ่าน Docker (แนะนำ - ง่ายที่สุด)
หากคุณติดตั้ง Docker Desktop ไว้แล้ว สามารถรันทุกอย่างได้ด้วยคำสั่งเดียว:
```bash
docker compose up --build
```
- หน้าเว็บจะรันที่: `http://localhost` (พอร์ต 80)
- API จะรันที่: `http://localhost:8000`

### 🌐 การนำขึ้นระบบจริง (Deployment)
แนะนำให้ใช้บริการฟรีดังนี้:
1. **Frontend**: ใช้ **Netlify** (เชื่อมกับ GitHub และใช้ค่าตั้งค่าใน `netlify.toml`)
2. **Backend (API & Socket)**: ใช้ **Render.com** (เลือกสร้าง Web Service แบบ Docker)
   - *หมายเหตุ: Render Free Tier จะมีการ "หลับ" (Sleep) หากไม่มีการใช้งานเกิน 15 นาที และจะใช้เวลาตื่นประมาณ 30-50 วินาทีเมื่อมีคนเข้าใช้งานใหม่*


### วิธีที่ 2: รันแบบแยกส่วน (Manual Setup)
กรุณารันคำสั่งเหล่านี้ที่โฟลเดอร์หลัก (Root) ของโปรเจกต์:

1. **รันทุกอย่างพร้อมกัน (แนะนำ)**:
   ```bash
   pnpm dev:all
   ```
   *(คำสั่งเดียวรันทั้ง Frontend, Backend และ Socket Server)*

2. **รันแยกส่วน**:
   - **Frontend**:
     ```bash
     pnpm dev
     ```
   - **Backend**:
     ```bash
     pnpm dev:backend
     ```
   - **Socket Server**:
     ```bash
     pnpm dev:socket
     ```

---

## 🧪 การทดสอบ (Testing)
เรามีระบบ Automated Testing เพื่อความเสถียรของระบบ:
- **Run API Tests**: `pytest tests/`
- **GitHub Actions**: ทุกครั้งที่ Push โค้ด ระบบจะรันเทส Build และ Logic ให้บน Cloud อัตโนมัติ

---

## 📝 การตั้งค่า Environment (.env)
กรุณาตั้งค่าไฟล์ `.env` ที่รูทของโปรเจกต์ โดยดูตัวอย่างจาก `.env.example`:
- `GEMINI_API_KEY`: คีย์สำหรับ AI
- `CLOUDINARY_URL`: คีย์สำหรับที่เก็บรูปภาพ
- `TIDB_*`: ข้อมูลการเชื่อมต่อฐานข้อมูล

---
**Evaly** - พัฒนาด้วย ❤️ เพื่อยกระดับการศึกษาด้วย AI
