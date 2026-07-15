<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" alt="License" />
</div>

<br />

<div align="center">
  <h1 align="center">Evaly: LLMs Auto Score System</h1>
  <p align="center">
    <strong>ระบบตรวจข้อสอบอัตโนมัติด้วย AI พร้อมระบบจัดการห้องเรียน</strong>
    <br />
    <br />
    <a href="#features">ฟีเจอร์หลัก</a>
    ·
    <a href="#tech-stack">เทคโนโลยีที่ใช้</a>
    ·
    <a href="#getting-started">วิธีการติดตั้ง</a>
    ·
    <a href="#system-architecture">สถาปัตยกรรมระบบ</a>
  </p>
</div>

---

## About The Project

**Evaly** เป็นระบบจัดการการศึกษาที่นำเอาความสามารถของ **Google Gemini Pro** มาช่วยในการตรวจข้อสอบแบบเขียนตอบ (Essay) จุดประสงค์หลักคือเพื่อลดภาระของผู้สอนในการตรวจข้อสอบ ระบบสามารถให้คะแนน, วิเคราะห์ลายมือจากรูปภาพ, สร้างเกณฑ์การให้คะแนน (Rubrics) อัตโนมัติ และให้คำแนะนำแก่นักเรียนเป็นรายบุคคลได้

สามารถเข้าชมได้บน https://llms-auto-score-systems.netlify.app/  
อาจช้าไปบ้างเพราะเป๋นบริการฟรีทั้ง backend เเละ frontend

<br/>

## Screenshots (ภาพตัวอย่าง)

<table>
  <tr>
    <td align="center">
      <img src="public/screenshots/register.png" alt="Register Page" width="400"/>
      <br />
      <b>หน้าสมัครสมาชิก</b>
    </td>
    <td align="center">
      <img src="public/screenshots/home.png" alt="Login Page" width="400"/>
      <br />
      <b>หน้าแรก / เข้าสู่ระบบ</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="public/screenshots/dashboard.png" alt="Dashboard Page" width="400"/>
      <br />
      <b>หน้าแดชบอร์ด</b>
    </td>
    <td align="center">
      <img src="public/screenshots/profile.png" alt="Profile Page" width="400"/>
      <br />
      <b>โปรไฟล์ส่วนตัว</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="public/screenshots/room-detail.png" alt="Room Detail Page" width="400"/>
      <br />
      <b>รายละเอียดห้องเรียน</b>
    </td>
    <td align="center">
      <img src="public/screenshots/create-exam.png" alt="Create Exam Page" width="400"/>
      <br />
      <b>สร้างข้อสอบ</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="public/screenshots/exam-view.png" alt="Exam View Page" width="400"/>
      <br />
      <b>รายละเอียดข้อสอบ</b>
    </td>
    <td align="center">
      <img src="public/screenshots/exam-analytics.png" alt="Exam Analytics Page" width="400"/>
      <br />
      <b>วิเคราะห์คะแนนสอบ</b>
    </td>
  </tr>
</table>

<br/>

## Features

- **AI Auto-Grading**: ตรวจข้อสอบด้วย AI พร้อมให้ความเห็นและบอกระดับความมั่นใจของ AI (Confidence Score)
- **Multimodal Support**: รองรับการส่งคำตอบแบบพิมพ์ข้อความ หรือจะถ่ายรูปกระดาษคำตอบที่เป็นลายมือมาส่งก็ได้
- **Auto-rubric Generation**: ช่วยดึงข้อมูลและสร้างเกณฑ์การให้คะแนนจากโจทย์โดยอัตโนมัติ
- **Classroom Management**: จัดการห้องเรียน รายชื่อนักเรียน และประกาศในห้องได้ครบ
- **Real-time Notifications**: แจ้งเตือนสถานะต่างๆ ทันทีผ่าน WebSockets
- **Cloud Storage**: จัดเก็บรูปภาพด้วย Cloudinary

<br/>

## Tech Stack

### Frontend
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) 

### Backend & AI
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

### Database & Real-time
![TiDB](https://img.shields.io/badge/TiDB-MySQL_Compatible-000000?style=for-the-badge&logo=mysql&logoColor=white) ![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white) ![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101)

### Infrastructure
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

<br/>

## Getting Started

### 1. โคลนโปรเจกต์และตั้งค่า
```bash
git clone https://github.com/idoodeeadmin/LLMs-Auto-Score-System.git
cd LLMs-Auto-Score-System
cp .env.example .env
```
*(อย่าลืมแก้ไขไฟล์ `.env` เพื่อใส่ API Keys ที่จำเป็น เช่น Gemini API และ Database URL)*

### 2. รันด้วย Docker (แนะนำ)
สามารถเปิดทุกส่วนของระบบขึ้นมาได้พร้อมกันด้วยคำสั่งเดียว:
```bash
docker compose up --build
```
- **หน้าเว็บ (Frontend):** `http://localhost`
- **API (Backend):** `http://localhost:8000`

### 3. รันแบบแยกส่วน
ถ้าไม่ใช้ Docker สามารถติดตั้งและรันผ่าน pnpm ได้โดยตรง:
```bash
pnpm install
pnpm dev:all
```
*(คำสั่ง `dev:all` จะช่วยเปิดทั้ง Frontend, Backend และ Socket ขึ้นมาพร้อมกัน)*

<br/>

---

## System Architecture

ระบบถูกออกแบบมาเป็น Microservices เพื่อให้แก้ไขและดูแลได้ง่าย โดยแบ่งออกเป็นส่วนหลักๆ ดังนี้:

### 1. Client Layer (Frontend)
- **React 18 SPA:** พัฒนาด้วย Vite
- **Real-time Listener:** เชื่อมต่อกับ Socket.io เพื่อรับการแจ้งเตือนแบบเรียลไทม์

### 2. Application Layer (Backend Services)
- **Core API (FastAPI):** ทำหน้าที่จัดการ Business Logic ทั้งหมด (เช่น ระบบสมาชิก, ห้องเรียน, การสอบ) ประมวลผลแบบ Asynchronous
- **Real-time Server (Node.js & Socket.io):** แยกออกมาดูแลเรื่อง WebSocket โดยเฉพาะ เพื่อลดภาระของ API หลักเวลาที่มีคนใช้งานเยอะๆ

### 3. AI & External Services
- **Google Gemini Pro:** รับหน้าที่ประมวลผลข้อความและอ่านลายมือจากรูปภาพเพื่อนำมาตรวจให้คะแนน
- **Cloudinary:** จัดการฝากไฟล์รูปภาพทั้งหมด
- **Firebase Auth:** จัดการการล็อกอินและยืนยันตัวตนผ่าน Google

### 4. Data Layer (Database)
- **TiDB (MySQL-compatible):** ใช้จัดการข้อมูลทั้งหมด 

### การทำงานของการตรวจข้อสอบ
1. **Submission:** นักเรียนส่งคำตอบเข้ามาในระบบ (เป็นตัวอักษรหรือไฟล์ภาพ)
2. **Preprocessing:** ระบบอัปโหลดรูปภาพขึ้น Cloudinary และเตรียมคำสั่ง (prompt) 
3. **AI Inference:** ส่งโจทย์, เกณฑ์การให้คะแนน และคำตอบของนักเรียน ไปให้ Google Gemini
4. **Evaluation:** Gemini วิเคราะห์และประเมินผลคำตอบ พร้อมให้คำแนะนำเพิ่มเติม
5. **Storage & Notify:** ระบบเซฟข้อมูลลง TiDB และสั่งให้ Socket.io แจ้งเตือนผู้สอนว่าตรวจข้อสอบเสร็จแล้ว

---

<div align="center">
  <p>Made with ❤️ by the Evaly Team</p>
</div>
