=======================================================
   EVALY: LLMs AUTO SCORE SYSTEM (ระบบตรวจข้อสอบ AI)
=======================================================

ยินดีต้อนรับสู่โปรเจกต์ Evaly ระบบตรวจข้อสอบอัตโนมัติด้วย AI

[ วิธีการรันโปรเจกต์ด่วน ]
-------------------------------------------------------
1. หากมี Docker:
   พิมพ์คำสั่ง: docker compose up --build

2. หากรันแบบปกติ (Manual):
   - Frontend: pnpm install -> pnpm dev (พอร์ต 5173)
   - Backend: pip install -r server/requirements.txt -> uvicorn server.main:app (พอร์ต 8001)
   - Socket: cd server-node -> pnpm install -> pnpm dev (พอร์ต 3001)

[ ข้อมูลทางเทคนิค ]
-------------------------------------------------------
- Frontend: React + Vite + TailwindCSS
- Backend: FastAPI (Python)
- Socket: Node.js
- Database: TiDB (MySQL)
- AI: Google Gemini Pro
- Storage: Cloudinary (เก็บรูปภาพบน Cloud)

[ การทดสอบระบบ ]
-------------------------------------------------------
- พิมพ์คำสั่ง: pytest tests/  เพื่อทดสอบ API
- ระบบมี CI/CD ผ่าน GitHub Actions ตรวจสอบโค้ดอัตโนมัติทุกครั้งที่ Push

*** สำคัญ: อย่าลืมตั้งค่าไฟล์ .env ก่อนเริ่มรันระบบ ***

-------------------------------------------------------
อ่านรายละเอียดฉบับเต็มได้ที่ไฟล์: README.md
-------------------------------------------------------
