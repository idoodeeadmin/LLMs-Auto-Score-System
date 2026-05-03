# สรุปสถาปัตยกรรมและ Work Flow ของระบบ Evaly Score (LLMs-Auto-Score-System)

โปรเจคนี้เป็นระบบตรวจข้อสอบอัตนัยอัตโนมัติแบบครบวงจรที่มีสถาปัตยกรรมแบบ 3-Tier (Frontend, Backend, Real-time Server) ต่อไปนี้คือสรุปการทำงานของฟีเจอร์หลักทั้งหมด ตั้งแต่จุดเริ่มต้นจนจบกระบวนการ ทำงานที่ไฟล์ไหน และทำงานอย่างไร

---

## 1. ระบบยืนยันตัวตนและจัดการผู้ใช้ (Authentication & User Management)
**Flow การทำงาน:**
1. ผู้ใช้ (อาจารย์/นักเรียน) เข้าเว็บมาที่หน้าแรก (Landing/Login)
2. สมัครสมาชิกด้วย Email/Password ระบบจะ Hash รหัสผ่าน (PBKDF2) และส่ง Email ไปให้กดยืนยัน (SMTP) หรือเลือกล็อกอินผ่าน Google (Firebase)
3. เมื่อล็อกอินสำเร็จ Backend จะสร้างและคืนค่า JWT Token (อายุ 7 วัน) ให้ Frontend เก็บไว้เพื่อใช้แนบในการเรียก API ครั้งถัดไป

**ส่วนที่รับผิดชอบ:**
*   **Frontend:** `client/pages/Register.tsx`, `client/pages/Index.tsx`, `client/components/GoogleSignInButton.tsx`, `client/contexts/AuthContext.tsx`
*   **Backend:** `server/auth.py` (ระบบ JWT และ Hash), `server/main.py` (`/api/auth/*`)

---

## 2. ระบบจัดการห้องเรียนและประกาศ (Room & Announcement System)
**Flow การทำงาน:**
1. **อาจารย์** กดสร้างห้องเรียน ระบบหลังบ้านจะสุ่ม "Class Code 6 หลัก" ออกมา
2. **นักเรียน** นำ Class Code นี้ไปกรอกเพื่อ "Join" ห้องเรียน
3. ภายในห้องเรียน อาจารย์สามารถโพสต์ประกาศข่าวสาร (Announcements) โดยระบบมีกลไก Read Receipt เพื่อเช็คว่านักเรียนคนไหนเข้ามาอ่านประกาศแล้วบ้าง

**ส่วนที่รับผิดชอบ:**
*   **Frontend:** `client/pages/Home.tsx` (Dashboard), `client/pages/RoomDetail.tsx`
*   **Backend:** `server/main.py` (`/api/rooms/*` เช่น `POST /api/rooms/`, `POST /api/rooms/join`)

---

## 3. ระบบสร้างข้อสอบและตั้งเกณฑ์การตรวจ (Exam Creation & Rubrics)
**Flow การทำงาน:**
1. อาจารย์เข้าไปที่ห้องเรียน กดสร้างข้อสอบ สามารถตั้งเวลาเปิด-ปิดการสอบได้
2. อาจารย์อัปโหลดรูปภาพโจทย์ (เก็บเป็นไฟล์ผ่านโฟลเดอร์ uploads หรือ Cloudinary)
3. **ฟีเจอร์ AI Auto-rubric:** อาจารย์สามารถให้ AI ช่วยสร้างเกณฑ์คะแนนได้ โดยกดปุ่มให้ Frontend ยิง API ไปหา Gemini เพื่อร่างเกณฑ์
4. เมื่อสร้างข้อสอบเสร็จ ข้อสอบจะถูกนำไปเก็บใน Question Bank (คลังข้อสอบ) ด้วย เพื่อให้นำกลับมาใช้ซ้ำในห้องอื่นๆ ได้ง่ายขึ้น

**ส่วนที่รับผิดชอบ:**
*   **Frontend:** `client/pages/CreateExam.tsx`, `client/pages/EditExam.tsx` (ใช้ React Hook Form + Zod ตรวจสอบข้อมูล)
*   **Backend:** `server/main.py` (`POST /api/rooms/{room_id}/exams/` และ `POST /api/gemini/generate-rubric`)

---

## 4. ระบบการทำข้อสอบฝั่งนักเรียน (Student Exam Submission)
**Flow การทำงาน:**
1. นักเรียนกดเริ่มทำข้อสอบ ระบบจะเริ่มจับเวลา (Timer Countdown) แบบเรียลไทม์ฝั่งหน้าจอ
2. **Multimodal Input:** นักเรียนพิมพ์คำตอบ (จำกัด 300 คำ) หรืออัปโหลดภาพถ่ายลายมือ ควบคู่กันไปได้
3. **Auto-save Draft:** ระหว่างทำข้อสอบ Frontend จะยิง API ไปบันทึกข้อมูลเบื้องหลังเป็นระยะๆ เพื่อป้องกันอินเทอร์เน็ตหลุด
4. **Time Extension:** ถ้านักเรียนคนไหนต้องการเวลาเพิ่ม (เช่น เด็กพิเศษ หรือเน็ตมีปัญหา) อาจารย์สามารถแก้ไขเวลาหมดสอบเฉพาะบุคคลได้

**ส่วนที่รับผิดชอบ:**
*   **Frontend:** `client/pages/ExamView.tsx` (หน้ารอสอบ), `client/pages/ExamSubmit.tsx` (หน้าห้องสอบจริง ควบคุม Timer และ Draft)
*   **Backend:** `server/main.py` (`POST /.../submit` และ `POST /.../draft`)

---

## 5. หัวใจหลัก: ระบบตรวจอัตโนมัติด้วย AI (AI Grading Core System)
**Flow การทำงาน:**
1. ทันทีที่ส่งข้อสอบ ระบบจะนำ ข้อมูลโจทย์ + ภาพ/ข้อความคำตอบนักเรียน + เกณฑ์ Rubric ของอาจารย์ มัดรวมกัน
2. **Prompt Engineering:** โค้ดจะจัดรูปแบบข้อความสั่งการ AI (ใช้เทคนิค Chain-of-Thought เพื่อให้ AI คิดทีละสเต็ป และ Few-Shot เพื่อยกตัวอย่าง)
3. ข้อมูลถูกส่งไปที่ **Google Gemini 1.5 Flash/Pro API**
4. Gemini ประมวลผลและตอบกลับเป็นรูปแบบ JSON กลับมา ประกอบด้วย:
   *   คะแนนที่ได้
   *   ข้อเสนอแนะอธิบายเหตุผล (Feedback)
   *   ระดับความมั่นใจของ AI (Confidence Score: High/Med/Low) เพื่อเตือนอาจารย์หาก AI ไม่มั่นใจ
5. มี **Fallback Scoring** หาก API ของ Gemini ล่ม ระบบจะมี Rule-based สำรองให้คะแนนเบื้องต้นเพื่อให้ระบบเดินหน้าต่อได้

**ส่วนที่รับผิดชอบ:**
*   **Backend:** ฟังก์ชันที่เชื่อมต่อกับ `google-genai` ใน `server/main.py` (`/api/gemini/*` และระบบเบื้องหลังการ Submit)

---

## 6. ระบบตรวจสอบและอนุมัติผลโดยอาจารย์ (Teacher Review & Grading)
**Flow การทำงาน:**
1. อาจารย์เข้ามาดูรายการคำตอบของนักเรียนทุกคน
2. อาจารย์คลิกเข้าไปดูคะแนนและ Feedback ที่ AI ประเมินไว้ (Smart Grading)
3. อาจารย์สามารถแก้ไข (Override) คะแนนที่ AI ให้ได้ พร้อมกับใส่คอมเมนต์เพิ่มเติมของตัวเองลงไป
4. เมื่อพอใจ อาจารย์สามารถกดปุ่ม "อนุมัติ" (Approve) ซึ่งสามารถกดเลือกนักเรียนหลายคนเพื่ออนุมัติพร้อมกันได้ (Bulk Approve)

**ส่วนที่รับผิดชอบ:**
*   **Frontend:** `client/pages/RoomReview.tsx` (ดูภาพรวมการส่ง), `client/pages/StudentGrading.tsx` (หน้าตรวจข้อสอบรายบุคคล)
*   **Backend:** `server/main.py` (`PUT /.../approve` และ `POST /.../bulk-approve`)

---

## 7. ระบบการแจ้งเตือนแบบเรียลไทม์ (Real-time Notifications)
**Flow การทำงาน:**
1. เมื่อล็อกอินเสร็จ Client จะสร้าง WebSocket Connection ไปที่ Node.js Server อัตโนมัติ (`join_room` ด้วย User ID)
2. เมื่อเกิดเหตุการณ์สำคัญ (เช่น ข้อสอบใกล้หมดเวลา, ข้อสอบใหม่มา, หรืออาจารย์กดประกาศผลคะแนน)
3. Python FastAPI จะส่ง HTTP Request (Bridge) ไปบอก Node.js
4. Node.js จะกระจายสัญญาณผ่าน `Socket.io` ส่งตรงไปยังหน้าจอของผู้ใช้ (โชว์เป็น Toast Notification ป๊อปอัปขึ้นมาทันทีโดยไม่ต้องรีเฟรชหน้า)

**ส่วนที่รับผิดชอบ:**
*   **Frontend:** `client/contexts/AuthContext.tsx` (จัดการ Socket Connection), `client/hooks/use-toast.ts`
*   **Backend (Python):** ระบบยิง Request หลังบ้านเพื่อเตือน
*   **Socket Server (Node.js):** `server-node/index.js`

---

## 8. ระบบแสดงสถิติและส่งออกข้อมูล (Analytics & Export)
**Flow การทำงาน:**
1. **Analytics:** ระบบรวบรวมคะแนนมาทำกราฟแสดงการกระจายของคะแนน (Score Distribution), ค่าเฉลี่ย, และความยากง่ายของข้อสอบแต่ละข้อ
2. **Export ข้อมูล:** อาจารย์สามารถกดดาวน์โหลดคะแนนของนักเรียนทั้งห้องออกมาเป็นไฟล์ CSV หรือ Excel (.xlsx) ที่จัดหน้าตาเรียบร้อยและรองรับภาษาไทย 100%

**ส่วนที่รับผิดชอบ:**
*   **Frontend:** `client/pages/TeacherAnalytics.tsx`, `client/pages/RoomAnalytics.tsx` (ใช้ไลบรารี Recharts วาดกราฟ)
*   **Backend:** `server/main.py` (ใช้ `openpyxl` ในการสร้างไฟล์ Excel)
