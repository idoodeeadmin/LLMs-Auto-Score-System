<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" alt="License" />
</div>

<br />

<div align="center">
  <h1 align="center">🚀 Evaly: LLMs Auto Score System</h1>
  <p align="center">
    <strong>ระบบตรวจข้อสอบอัตโนมัติด้วยพลังของ Generative AI พร้อมระบบจัดการห้องเรียนครบวงจร</strong>
    <br />
    <br />
    <a href="#-features">✨ ฟีเจอร์หลัก</a>
    ·
    <a href="#-tech-stack">🛠 เทคโนโลยี</a>
    ·
    <a href="#-getting-started">🚀 การติดตั้ง</a>
    ·
    <a href="#-system-architecture">📐 สถาปัตยกรรมระบบ</a>
  </p>
</div>

---

## 💡 About The Project

**Evaly** เป็นนวัตกรรมระบบจัดการการศึกษาที่ผสานรวมความสามารถของ **Google Gemini Pro (Generative AI)** เพื่อช่วยแบ่งเบาภาระของผู้สอนในการตรวจข้อสอบแบบบรรยาย (Essay) ระบบไม่เพียงแต่ให้คะแนนได้อย่างแม่นยำ แต่ยังสามารถวิเคราะห์ลายมือจากรูปภาพ สร้างเกณฑ์การให้คะแนน (Rubrics) อัตโนมัติ และให้ Feedback เชิงลึกแก่นักเรียนเป็นรายบุคคล

<br/>

## 📸 Screenshots (ตัวอย่างหน้าเว็บ)

<table>
  <tr>
    <td align="center">
      <img src="public/screenshots/register.png" alt="Register Page" width="400"/>
      <br />
      <b>หน้าสมัครสมาชิก (Register)</b>
    </td>
    <td align="center">
      <img src="public/screenshots/home.png" alt="Home/Login Page" width="400"/>
      <br />
      <b>หน้าแรก (Home / Login)</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="public/screenshots/dashboard.png" alt="Dashboard Page" width="400"/>
      <br />
      <b>หน้าแดชบอร์ดหลัก (Dashboard)</b>
    </td>
    <td align="center">
      <img src="public/screenshots/profile.png" alt="Profile Page" width="400"/>
      <br />
      <b>หน้าโปรไฟล์ส่วนตัว (Profile)</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="public/screenshots/room-detail.png" alt="Room Detail Page" width="400"/>
      <br />
      <b>หน้ารายละเอียดห้องเรียน (Room Detail)</b>
    </td>
    <td align="center">
      <img src="public/screenshots/create-exam.png" alt="Create Exam Page" width="400"/>
      <br />
      <b>หน้าสร้างข้อสอบ (Create Exam)</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="public/screenshots/exam-view.png" alt="Exam View Page" width="400"/>
      <br />
      <b>หน้ารายละเอียดข้อสอบ (Exam View)</b>
    </td>
    <td align="center">
      <img src="public/screenshots/exam-analytics.png" alt="Exam Analytics Page" width="400"/>
      <br />
      <b>หน้าวิเคราะห์คะแนนสอบ (Analytics)</b>
    </td>
  </tr>
</table>

<br/>

## ✨ Features (ฟีเจอร์เด่น)

- 🤖 **AI Auto-Grading**: ตรวจข้อสอบอัตโนมัติด้วย AI พร้อมให้ Feedback และวิเคราะห์ความมั่นใจ (Confidence Score)
- 📸 **Multimodal Support**: รองรับการส่งคำตอบทั้งรูปแบบข้อความ (Text) และอัปโหลด "รูปภาพลายมือ" (Vision OCR)
- 📝 **Auto-rubric Generation**: AI ช่วยสร้างเกณฑ์การให้คะแนน (Rubrics) และธงคำตอบอัตโนมัติจากโจทย์ ช่วยลดเวลาเตรียมสอน
- 🏫 **Classroom Management**: ระบบจัดการห้องเรียน, สมาชิก, และประกาศข่าวสาร
- ⚡ **Real-time Notifications**: แจ้งเตือนอัปเดตทันใจผ่านเทคโนโลยี WebSockets (Socket.io)
- ☁️ **Cloud Native**: จัดเก็บรูปภาพอย่างปลอดภัยบน Cloudinary และรองรับการทำ CI/CD 

<br/>

## 🛠 Tech Stack

### Frontend
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) 

### Backend & AI
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

### Database & Real-time
![TiDB](https://img.shields.io/badge/TiDB-MySQL_Compatible-000000?style=for-the-badge&logo=mysql&logoColor=white) ![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white) ![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101)

### Infrastructure
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

<br/>

## 🚀 Getting Started (วิธีการติดตั้ง)

### 1. คัดลอกโปรเจกต์และตั้งค่า Environment
```bash
git clone https://github.com/yourusername/LLMs-Auto-Score-System.git
cd LLMs-Auto-Score-System
cp .env.example .env
```
*(กรุณาแก้ไขไฟล์ `.env` โดยใส่ API Keys ที่จำเป็น เช่น Gemini API, Database URL)*

### 2. รันระบบด้วย Docker (แนะนำ 🌟)
รันทุกส่วนของระบบ (Frontend, Backend, Socket) ด้วยคำสั่งเดียว:
```bash
docker compose up --build
```
- **หน้าเว็บ (Frontend):** `http://localhost`
- **API (Backend):** `http://localhost:8000`

### 3. การรันแบบแยกส่วน (Manual Setup)
หากไม่ใช้ Docker สามารถรันผ่าน pnpm ได้โดยตรง:
```bash
pnpm install
pnpm dev:all   # รัน Frontend + Backend + Socket พร้อมกัน
```

<br/>

---

## 📐 System Architecture (สถาปัตยกรรมระบบ)

Evaly ถูกออกแบบมาให้เป็นระบบที่แยกส่วนการทำงาน (Microservices-oriented) เพื่อความยืดหยุ่นและรองรับการขยายตัว (Scalability) ในอนาคต โดยมีองค์ประกอบหลักดังนี้:

### 1. Client Layer (Frontend)
- **React 18 SPA (Single Page Application):** พัฒนาด้วย Vite มอบประสบการณ์ผู้ใช้ที่ลื่นไหล
- **State Management:** จัดการสถานะแอปพลิเคชันอย่างมีประสิทธิภาพ 
- **Real-time Listener:** เชื่อมต่อกับ Socket.io Client เพื่อรอรับการแจ้งเตือนแบบเรียลไทม์

### 2. Application Layer (Backend Services)
- **Core API (FastAPI):** เป็นหัวใจหลักในการจัดการ Business Logic ทั้งหมด (การจัดการผู้ใช้, ห้องเรียน, ข้อสอบ) ประมวลผลแบบ Asynchronous ทำให้รองรับ Request จำนวนมากได้พร้อมกัน
- **Real-time Server (Node.js & Socket.io):** แยกเซิร์ฟเวอร์สำหรับจัดการ WebSocket ออกมาโดยเฉพาะ เพื่อไม่ให้กระทบประสิทธิภาพของ API หลัก ทำหน้าที่ Broadcast การแจ้งเตือน

### 3. AI & External Services Layer
- **Google Gemini Pro:** รับหน้าที่ประมวลผล NLP และ Computer Vision (อ่านลายมือ) จากคำตอบของนักเรียน เปรียบเทียบกับ Rubrics และคืนผลลัพธ์เป็นโครงสร้าง (Structured Data)
- **Cloudinary:** จัดการการฝากไฟล์รูปภาพทั้งหมด พร้อมทำ Image Optimization ก่อนเก็บลงฐานข้อมูล
- **Firebase Auth:** จัดการการล็อกอินผ่าน Google เพื่อความปลอดภัยระดับ Enterprise

### 4. Data Layer (Database)
- **TiDB (MySQL-compatible):** ฐานข้อมูลแบบ Distributed SQL ที่รองรับการ Scale out ได้ง่าย และจัดการ Transaction ได้อย่างสมบูรณ์แบบ

### 🔄 Workflow การตรวจข้อสอบ (How AI Grading Works)
1. **Submission:** นักเรียนส่งคำตอบ (เป็นข้อความหรือรูปถ่ายลายมือ) เข้าสู่ระบบ
2. **Preprocessing:** ระบบ Backend นำรูปภาพอัปโหลดขึ้น Cloudinary และจัดเตรียม prompt
3. **AI Inference:** ส่งโจทย์, Rubrics, ธงคำตอบ และคำตอบของนักเรียน ไปให้ Google Gemini ประมวลผล
4. **Evaluation:** Gemini วิเคราะห์คำตอบ สร้าง Feedback และคำนวณ Confidence Score 
5. **Storage & Notify:** ระบบบันทึกผลลงฐานข้อมูล TiDB และยิง Webhook ไปหา Socket.io เพื่อแจ้งเตือนผู้สอนว่ามีข้อสอบรออนุมัติผล

---

<div align="center">
  <p>Made with ❤️ by the Evaly Team</p>
</div>
