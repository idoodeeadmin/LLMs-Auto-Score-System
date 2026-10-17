# Evaly — LLMs Auto Score System

เว็บแอปสำหรับสร้างข้อสอบ ส่งคำตอบแบบข้อความหรือภาพ และใช้ Gemini ช่วยเสนอคะแนนพร้อมเหตุผล ผู้สอนตรวจทานและอนุมัติก่อนผู้เรียนเห็นผล

## เริ่มใช้งานในเครื่อง

ต้องมี Node.js, pnpm และ Python 3.11 ขึ้นไป

```bash
pnpm install
python -m pip install -r server/requirements.txt
```

คัดลอก `.env.example` เป็น `.env` แล้วใส่ค่าการเชื่อมต่อฐานข้อมูล, `GEMINI_API_KEY`, Firebase และ Cloudinary ตามบริการที่ใช้จริง เก็บ `.env` และไฟล์ service account ไว้ในเครื่องหรือ secret manager

เปิดแต่ละบริการคนละ terminal:

```bash
pnpm dev:backend
pnpm dev:socket
pnpm dev
```

หน้าเว็บอยู่ที่ `http://localhost:8080` ส่วน API อยู่ที่พอร์ต `8001` และ Socket.IO อยู่ที่พอร์ต `3001`

## ตรวจสอบก่อน deploy

```bash
pnpm typecheck
pnpm test
pnpm build
python -m pytest tests/
```

โค้ดหลักอยู่ใน `client/`, `server/`, `server-node/` และ `shared/` ภาพโจทย์หรือคำตอบที่อัปโหลดระหว่างใช้งานเก็บแยกจาก repository นี้
