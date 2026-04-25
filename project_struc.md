# Evaly Score - ระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วย LLMs

## 1. ภาพรวมระบบ (System Overview)

Evaly Score เป็นแอปพลิเคชัน Web-based สำหรับตรวจข้อสอบอัตนัยอัตโนมัติ โดยใช้เทคโนโลยี Multimodal Large Language Models (LLMs) รองรับการตรวจคำตอบทั้งแบบพิมพ์และลายมือ ระบบถูกออกแบบสำหรับวิชา Data Structures แต่สามารถขยายไปใช้กับวิชาอื่นได้

---

## 2. สถาปัตยกรรมระบบ (System Architecture)

### 2.1 สถาปัตยกรรมแบบ 3-Tier
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                 │
│  - React 18 + TypeScript                                    │
│  - React Router 6 (SPA)                                      │
│  - TailwindCSS 3 + Radix UI                                  │
│  - TanStack Query (React Query)                             │
│  - Socket.io Client (Real-time)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                          │
│  ┌─────────────────┐  ┌─────────────────┐                    │
│  │  FastAPI (Py)   │  │  Node.js Socket │                    │
│  │  Port: 8001     │  │  Port: 3001     │                    │
│  │  - REST API     │  │  - WebSocket    │                    │
│  │  - AI Grading   │  │  - Real-time    │                    │
│  │  - Auth JWT     │  │    Notifications│                    │
│  └─────────────────┘  └─────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  - SQLite (dev.db)                                          │
│  - Google Gemini API                                        │
│  - Firebase Auth (Google Sign-In)                           │
│  - SMTP (Email Service)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. ฟีเจอร์หลักตามประเภทผู้ใช้ (Features by User Type)

### 3.1 นักเรียน/ผู้เรียน (Student)

| ฟีเจอร์ | รายละเอียด | สถานะ |
|---------|-----------|--------|
| **3.1.1 สมัครสมาชิก** | ลงทะเบียนด้วย ชื่อ, นามสกุล, รหัสนักเรียน, Email, Password, รูป Profile (ไม่บังคับ) | [x] |
| **3.1.2 เข้าสู่ระบบ** | Email + Password และ Google Sign-In (Firebase Auth) | [x] |
| **3.1.3 ยืนยันอีเมล** | ระบบส่งลิงก์ยืนยันอีเมลผ่าน SMTP | [x] |
| **3.1.4 แก้ไขโปรไฟล์** | อัปเดต ชื่อ, นามสกุล, Password, รูป Profile | [x] |
| **3.1.5 เข้าร่วมห้องเรียน** | Join ด้วย Class Code 6 หลัก | [x] |
| **3.1.6 ออกจากห้องเรียน** | ลบการเข้าร่วมห้องเรียน | [x] |
| **3.1.7 ทำข้อสอบ** | 2 รูปแบบ: พิมพ์คำตอบ / อัปโหลดรูปภาพลายมือ | [x] |
| **3.1.8 จับเวลาสอบ** | Timer Countdown + แจ้งเตือนใกล้หมดเวลา | [x] |
| **3.1.9 ดูสถานะการส่ง** | ยังไม่ส่ง / ส่งแล้ว (รอตรวจ) / ตรวจแล้ว | [x] |
| **3.1.10 ดูผลคะแนน** | ดูคะแนนและข้อเสนอแนะหลังอาจารย์อนุมัติ | [x] |
| **3.1.11 ประวัติการสอบ** | ดูประวัติการทำข้อสอบย้อนหลังทุกห้องเรียน | [x] |
| **3.1.12 Real-time Notifications** | แจ้งเตือนเมื่อมีข้อสอบใหม่, ใกล้หมดเวลา, ประกาศผล | [x] |

### 3.2 อาจารย์/ผู้สอน (Teacher)

| ฟีเจอร์ | รายละเอียด | สถานะ |
|---------|-----------|--------|
| **3.2.1 สมัครสมาชิก** | ลงทะเบียนด้วย ชื่อ, นามสกุล, รหัสผู้สอน, Email, Password | [x] |
| **3.2.2 เข้าสู่ระบบ** | Email + Password และ Google Sign-In | [x] |
| **3.2.3 จัดการห้องเรียน** | เพิ่ม, ลบ, แก้ไขห้องเรียน + ดู Class Code | [x] |
| **3.2.4 ค้นหาห้องเรียน** | ค้นหาด้วยชื่อหรือรหัสห้อง | [x] |
| **3.2.5 จัดการข้อสอบ** | สร้าง, แก้ไข, ลบข้อสอบพร้อมโจทย์และธงคำตอบ | [x] |
| **3.2.6 กำหนดเวลาสอบ** | กำหนดวัน/เวลาเริ่มต้น - สิ้นสุด (ไม่บังคับ) | [x] |
| **3.2.7 อัปโหลดรูปโจทย์** | รองรับหลายรูปภาพต่อข้อ (base64 + จัดเก็บใน uploads) | [x] |
| **3.2.8 กำหนด Rubrics** | กำหนดเกณฑ์การให้คะแนนแบบละเอียด | [x] |
| **3.2.9 ตรวจสอบการส่ง** | ดูสถานะนักเรียนทุกคน (ส่งแล้ว/ยังไม่ส่ง) | [x] |
| **3.2.10 ตรวจคำตอบ** | ดูคำตอบนักเรียน พร้อม AI Score และ Feedback | [x] |
| **3.2.11 แก้ไขคะแนน** | แก้ไขคะแนนที่ AI ให้ + เพิ่มคอมเมนต์ส่วนตัว | [x] |
| **3.2.12 อนุมัติผล** | อนุมัติคะแนนเพื่อประกาศให้นักเรียนทราบ | [x] |
| **3.2.13 Bulk Approve** | อนุมัติหลายคนพร้อมกันใช้คะแนน AI | [x] |
| **3.2.14 สถิติและ Analytics** | ดูรายงานคะแนนเฉลี่ย, การกระจายคะแนน, ความยากของข้อ | [x] |
| **3.2.15 Export ข้อมูล** | ส่งออก CSV/XLSX รายงานคะแนน | [x] |

### 3.3 ระบบ AI Grading (Core System)

| ฟีเจอร์ | รายละเอียด | สถานะ |
|---------|-----------|--------|
| **3.3.1 Multimodal Scoring** | รองรับ Text + Image (Vision) ในครั้งเดียว | [x] |
| **3.3.2 Gemini AI** | ใช้ Google Gemini 1.5 Flash/Pro เป็นตัวตรวจ | [x] |
| **3.3.3 Prompt Engineering** | Chain-of-Thought + Few-Shot Prompting สำหรับ Data Structures | [x] |
| **3.3.4 Rubric-based** | ตรวจตามเกณฑ์รูบริคที่อาจารย์กำหนด | [x] |
| **3.3.5 Confidence Score** | ให้ค่าความมั่นใจ (high/medium/low) สำหรับแต่ละคำตอบ | [x] |
| **3.3.6 Fallback Scoring** | ระบบสำรองแบบ Rule-based เมื่อ AI ไม่พร้อมใช้งาน | [x] |
| **3.3.7 การแจ้งเตือน** | แจ้งเตือนอาจารย์เมื่อตรวจเสร็จหรือต้องตรวจเอง | [x] |
| **3.3.8 การจำกัดข้อความ** | รองรับคำตอบสูงสุด 300 คำต่อข้อ | [x] |

---

## 4. เทคโนโลยีและเทคนิค (Technologies & Techniques)

### 4.1 Frontend Stack

| เทคโนโลยี | รุ่น | วัตถุประสงค์ |
|-----------|------|--------------|
| React | 18.3.1 | UI Library |
| TypeScript | 5.9.2 | Type Safety |
| Vite | 7.1.2 | Build Tool |
| React Router DOM | 6.30.1 | SPA Routing |
| TailwindCSS | 3.4.17 | CSS Framework |
| Radix UI | latest | Headless UI Components |
| TanStack Query | 5.84.2 | Data Fetching & Caching |
| Socket.io Client | 4.8.3 | Real-time Communication |
| Firebase | 12.12.0 | Authentication (Google Sign-In) |
| Recharts | 2.12.7 | Data Visualization |
| Framer Motion | 12.23.12 | Animations |
| React Hook Form | 7.62.0 | Form Management |
| Zod | 3.25.76 | Schema Validation |
| date-fns | 4.1.0 | Date Manipulation |
| Lucide React | 0.539.0 | Icons |

### 4.2 Backend Stack

| เทคโนโลยี | รุ่น | วัตถุประสงค์ |
|-----------|------|--------------|
| FastAPI | latest | Python Web Framework |
| Uvicorn | latest | ASGI Server |
| SQLite | 3.x | Database |
| better-sqlite3 | 12.8.0 | SQLite Driver (Node) |
| python-jose | latest | JWT Handling |
| google-genai | latest | Gemini API Client |
| firebase-admin | latest | Firebase Admin SDK |
| python-dotenv | latest | Environment Variables |
| aiofiles | latest | Async File Operations |
| httpx | latest | HTTP Client |
| openpyxl | latest | XLSX Export |

### 4.3 Real-time & Socket Server

| เทคโนโลยี | รุ่น | วัตถุประสงค์ |
|-----------|------|--------------|
| Node.js | 18+ | Runtime |
| Express | 4.x | Web Framework |
| Socket.io | 4.x | WebSocket Server |
| CORS | latest | Cross-origin handling |

### 4.4 Security & Authentication

| เทคนิค/เทคโนโลยี | รายละเอียด |
|------------------|-----------|
| JWT (JSON Web Token) | Access Token อายุ 7 วัน |
| PBKDF2-SHA256 | Password Hashing (100,000 rounds) |
| Rate Limiting | IP-based limiting (login, register) |
| CORS | Cross-Origin Resource Sharing |
| Email Verification | 24-hour expiry token |
| Password Reset | 1-hour expiry token + self-service |
| Firebase Auth | Google Sign-In integration |

### 4.5 AI & Prompt Engineering

| เทคนิค | รายละเอียด |
|--------|-----------|
| Chain-of-Thought | ให้ AI คิดเป็นขั้นตอนก่อนตอบ |
| Few-Shot Prompting | ตัวอย่างการให้คะแนนในพรอมต์ |
| Multimodal Input | ส่งทั้งข้อความและรูปภาพ |
| Temperature Control | 0.2 (consistent scoring) |
| Confidence Scoring | วิเคราะห์ความมั่นใจของคำตอบ |
| Fallback Heuristic | กรณี AI ไม่พร้อมใช้งาน |

---

## 5. โครงสร้างฐานข้อมูล (Database Schema)

### 5.1 Entities

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │    rooms    │       │   exams     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK)     │──┐    │ id (PK)     │
│ email       │  │    │ name        │  │    │ room_id(FK) │
│ password    │  │    │ class_code  │  │    │ title       │
│ name        │  │    │ owner_id(FK)│  │    │ description │
│ role        │  │    │ section     │  │    │ total_score │
│ student_id  │  │    └─────────────┘  │    │ start_date  │
│ avatar_url  │  │           │           │    │ end_date    │
│ is_verified │  │           ▼           │    └─────────────┘
└─────────────┘  │    ┌─────────────┐    │           │
     │           │    │ enrollments │    │           ▼
     │           │    ├─────────────┤    │    ┌─────────────┐
     │           └───►│ user_id(FK) │    └───►│  questions  │
     │                │ room_id(FK) │         ├─────────────┤
     │                │ joined_at   │         │ id (PK)     │
     │                └─────────────┘         │ exam_id(FK) │
     │                                        │ text        │
     │                                        │ score       │
     │    ┌─────────────┐                     │ answer_key  │
     │    │ submissions │                     │ rubrics     │
     │    ├─────────────┤                     │ image_paths │
     └───►│ id (PK)     │◄────────────────────│ order_index │
          │ exam_id(FK) │                     └─────────────┘
          │ student_id   │                            │
          │ status       │                            ▼
          │ total_score  │                   ┌─────────────┐
          │ graded_by_ai │                   │submission_  │
          │ submitted_at │                   │  answers    │
          └─────────────┘                   ├─────────────┤
                                            │ id (PK)     │
┌──────────────────┐                        │ submission  │
│ password_resets  │                        │   _id(FK)   │
├──────────────────┤                        │ question_id │
│ id (PK)          │                        │ answer_text │
│ user_id(FK)      │                        │ ai_score    │
│ token            │                        │ ai_feedback │
│ expires_at       │                        │ ai_confidence│
└──────────────────┘                        │ teacher_score│
                                            │ teacher_comment│
┌──────────────────┐                       │ image_paths │
│email_verifications│                       └─────────────┘
├──────────────────┤
│ id (PK)          │
│ user_id(FK)      │
│ token            │
│ expires_at       │
└──────────────────┘
```

---

## 6. API Endpoints

### 6.1 Authentication (`/api/auth/*`)

| Method | Endpoint | คำอธิบาย |
|--------|----------|---------|
| POST | `/register` | สมัครสมาชิก + ส่งอีเมลยืนยัน |
| POST | `/login` | เข้าสู่ระบบ |
| POST | `/firebase-login` | เข้าสู่ระบบด้วย Google |
| POST | `/link-google` | เชื่อมโยงบัญชี Google |
| GET | `/me` | ดูข้อมูลผู้ใช้ปัจจุบัน |
| PUT | `/profile` | อัปเดตโปรไฟล์ |
| POST | `/forgot-password` | ขอรีเซ็ตรหัสผ่าน |
| POST | `/reset-password` | รีเซ็ตรหัสผ่านด้วย token |
| POST | `/verify-email` | ยืนยันอีเมล |
| POST | `/resend-verification` | ส่งอีเมลยืนยันอีกครั้ง |
| DELETE | `/account` | ลบบัญชี |

### 6.2 Rooms (`/api/rooms/*`)

| Method | Endpoint | คำอธิบาย |
|--------|----------|---------|
| POST | `/` | สร้างห้องเรียน |
| GET | `/` | ดูห้องเรียนทั้งหมด |
| PUT | `/{id}` | แก้ไขห้อง |
| DELETE | `/{id}` | ลบห้อง |
| POST | `/join` | เข้าร่วมห้องด้วย Class Code |
| GET | `/{id}` | ดูรายละเอียดห้อง |
| GET | `/{id}/members` | ดูสมาชิกในห้อง |
| GET | `/{id}/analytics` | ดูสถิติระดับห้อง |
| GET | `/{id}/export-summary-csv` | Export สรุปคะแนนทั้งห้อง |

### 6.3 Exams (`/api/rooms/{room_id}/exams/*`)

| Method | Endpoint | คำอธิบาย |
|--------|----------|---------|
| POST | `/` | สร้างข้อสอบ |
| GET | `/` | ดูข้อสอบทั้งหมดในห้อง |
| GET | `/{exam_id}` | ดูรายละเอียดข้อสอบ |
| PUT | `/{exam_id}` | แก้ไขข้อสอบ |
| DELETE | `/{exam_id}` | ลบข้อสอบ |
| POST | `/{exam_id}/submit` | ส่งคำตอบ (JSON) |
| POST | `/{exam_id}/submit-multipart` | ส่งคำตอบ (FormData + รูปภาพ) |
| GET | `/{exam_id}/submissions` | ดูรายการส่งทั้งหมด |
| GET | `/{exam_id}/submissions/me` | ดูคำตอบตัวเอง |
| GET | `/{exam_id}/submissions/{student_id}` | ดูคำตอบนักเรียน |
| PUT | `/{exam_id}/submissions/{student_id}/approve` | อนุมัติคะแนน |
| POST | `/{exam_id}/bulk-approve` | อนุมัติหลายคนพร้อมกัน |
| GET | `/{exam_id}/analytics` | ดูสถิติข้อสอบ |
| GET | `/{exam_id}/export-csv` | Export CSV |
| GET | `/{exam_id}/export?format=xlsx` | Export XLSX |

### 6.4 Notifications (`/api/notifications`)

| Method | Endpoint | คำอธิบาย |
|--------|----------|---------|
| GET | `/` | ดูการแจ้งเตือนทั้งหมด |

### 6.5 Socket Server (`server-node/index.js`)

| Event | Direction | คำอธิบาย |
|-------|-----------|---------|
| `join_room` | Client → Server | เข้าร่วมห้องแจ้งเตือน |
| `new_notification` | Server → Client | ส่งการแจ้งเตือน |
| `emit-notification` | Python → Node | Bridge ส่งการแจ้งเตือน |

---

## 7. โครงสร้างโปรเจค (Project Structure)

```
LLMs-Auto-Score-System-main/
├── client/                          # React Frontend
│   ├── pages/                       # Route Components
│   │   ├── Index.tsx               # Landing/Login Page
│   │   ├── Register.tsx            # Registration Page
│   │   ├── Home.tsx                # Dashboard (Teacher/Student)
│   │   ├── RoomDetail.tsx          # Room Detail View
│   │   ├── CreateExam.tsx          # Create Exam Form
│   │   ├── EditExam.tsx            # Edit Exam Form
│   │   ├── ExamView.tsx            # Student Exam View
│   │   ├── ExamSubmit.tsx          # Exam Submission
│   │   ├── RoomReview.tsx          # Teacher Review All
│   │   ├── StudentGrading.tsx      # Grade Individual Student
│   │   ├── TeacherAnalytics.tsx    # Exam Analytics
│   │   ├── RoomAnalytics.tsx       # Room Analytics
│   │   ├── ExamScoreboard.tsx      # Score Overview
│   │   ├── StudentHistory.tsx      # Student Submission History
│   │   ├── Profile.tsx             # User Profile
│   │   ├── ForgotPassword.tsx      # Password Recovery
│   │   ├── ResetPassword.tsx       # Reset Password
│   │   ├── VerifyEmail.tsx         # Email Verification
│   │   └── NotFound.tsx            # 404 Page
│   │
│   ├── components/                  # Reusable Components
│   │   ├── ui/                     # Radix UI Components (49 items)
│   │   ├── Navbar.tsx              # Navigation Bar
│   │   └── GoogleSignInButton.tsx # Google Auth Button
│   │
│   ├── contexts/                    # React Contexts
│   │   └── AuthContext.tsx         # Authentication State + Socket
│   │
│   ├── hooks/                       # Custom Hooks
│   │   ├── use-toast.ts            # Toast Notifications
│   │   └── use-mobile.tsx          # Mobile Detection
│   │
│   ├── lib/                         # Utilities
│   │   ├── utils.ts                # Helper Functions (cn)
│   │   ├── firebase.ts             # Firebase Config
│   │   └── utils.spec.ts           # Tests
│   │
│   ├── App.tsx                      # Main App with Routes
│   ├── main.tsx                     # Entry Point
│   ├── global.css                   # Tailwind + Theme
│   └── index.html                   # HTML Template
│
├── server/                          # FastAPI Backend
│   ├── main.py                      # Main Application (2473 lines)
│   ├── database.py                  # SQLite Schema & Connection
│   ├── auth.py                      # JWT & Password Hashing
│   └── requirements.txt             # Python Dependencies
│
├── server-node/                     # Node.js Socket Server
│   ├── index.js                     # Socket.io Server
│   └── package.json                 # Node Dependencies
│
├── prisma/                          # Prisma Schema (SQLite)
│   └── schema.prisma                # Database Schema
│
├── uploads/                         # File Storage
│   ├── questions/                   # Question Images
│   └── avatars/                     # User Avatars
│
├── shared/                          # Shared Types (if any)
├── public/                          # Static Assets
├── .env                             # Environment Variables
├── .env.example                     # Example Environment
├── package.json                     # Frontend Dependencies
├── vite.config.ts                   # Vite Configuration
├── tailwind.config.ts               # Tailwind Configuration
├── tsconfig.json                    # TypeScript Config
└── project_struc.md                 # This File
```

---

## 8. ฟีเจอร์เสริมและเทคนิคพิเศษ (Additional Features)

### 8.1 Real-time Features
- **Socket.io WebSocket**: การแจ้งเตือนแบบ Real-time
- **Auto-join Room**: เข้าห้องแจ้งเตือนอัตโนมัติตาม user_id
- **Notification Types**:
  - ข้อสอบใหม่ (new_exam)
  - ใกล้หมดเวลา (deadline_soon)
  - หมดเวลาส่ง (deadline_passed)
  - AI ตรวจเสร็จ (ai_graded)
  - ประกาศผล (result_published)

### 8.2 Security Features
- **Rate Limiting**: จำกัดจำนวน request ต่อ IP
  - Register: 5 ครั้ง/ชั่วโมง
  - Login: 10 ครั้ง/นาที
- **JWT Token**: อายุ 7 วัน, HS256
- **PBKDF2 Password Hash**: 100,000 rounds + salt
- **Email Verification**: บังคับยืนยันอีเมลก่อนใช้งาน
- **CORS**: Cross-origin protection

### 8.3 Data Export Features
- **CSV Export**: UTF-8 with BOM สำหรับ Excel
- **XLSX Export**: Excel format พร้อม styling
- **Summary Export**: สรุปคะแนนทั้งห้องเรียน

### 8.4 Analytics Features
- **Score Distribution**: การกระจายคะแนน (buckets)
- **Mean/Median**: ค่าเฉลี่ยและมัธยฐาน
- **Question Difficulty**: วิเคราะห์ความยากของแต่ละข้อ
- **Submission Rate**: อัตราการส่งงาน

### 8.5 Image Handling
- **Base64 Upload**: รูปภาพแปลงเป็น base64 ก่อนส่ง
- **Multiple Images**: รองรับหลายรูปต่อข้อ
- **UUID Filename**: ป้องกันการซ้ำของชื่อไฟล์
- **Static File Serving**: /uploads path

### 8.6 Error Handling
- **Graceful Degradation**: ระบบทำงานต่อได้แม้ AI ล่ม
- **Fallback Scoring**: ให้คะแนนด้วย heuristic กรณี Gemini ไม่พร้อม
- **Validation**: Zod schema validation ทั้ง client และ server

---

## 9. Environment Variables

```env
# Database & JWT
JWT_SECRET_KEY=your-secret-key

# Email SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Firebase
FIREBASE_CREDENTIALS_PATH=firebase-adminsdk.json
VITE_FIREBASE_API_KEY=xxx
VITE_FIREBASE_AUTH_DOMAIN=xxx
VITE_FIREBASE_PROJECT_ID=xxx

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key

# Socket Server
SOCKET_PORT=3001

# Server
PORT=8001
```

---

## 10. คำสั่งที่ใช้ในการพัฒนา (Development Commands)

```bash
# Install dependencies
pnpm install
cd server-node && npm install

# Development (run all servers)
pnpm dev          # Vite dev server (port 8080)
pnpm dev:backend  # FastAPI server (port 8001)
node server-node/index.js  # Socket server (port 3001)

# Build
pnpm build        # Production build
pnpm typecheck    # TypeScript validation
pnpm test         # Run Vitest tests

# Python
pip install -r server/requirements.txt
uvicorn server.main:app --reload --port 8001
```

---

## 11. ข้อควรระวังและข้อจำกัด (Limitations & Notes)

1. **AI Model**: ใช้ Gemini 1.5 Flash (อาจมี cost ในอนาคต)
2. **Image Limit**: สูงสุด 5 รูปต่อคำตอบ (ป้องกัน token overload)
3. **Text Limit**: 300 คำต่อคำตอบ
4. **Database**: SQLite (เหมาะสำหรับ development, ควรเปลี่ยนเป็น PostgreSQL สำหรับ production)
5. **File Storage**: Local filesystem (ควรใช้ Cloud Storage สำหรับ production)
6. **Email**: ต้องตั้งค่า SMTP หรือใช้ Dev Mode

---

## 12. ฟีเจอร์ที่กำลังจะปรับปรุงหรือเพิ่มเติม (Features to Consider)

### 12.1 ระบบ Authentication & Security
- **[ ] Session Management** - จัดการ session แบบ revoke token เมื่อเปลี่ยนรหัสผ่าน
- **[ ] Audit Log** - บันทึกการกระทำสำคัญทั้งหมด (login, delete, grade changes)

### 12.2 AI Grading System
- **[ ] Confidence Threshold** - Auto-flag คำตอบที่ AI มั่นใจต่ำกว่า threshold
- **[ ] Batch Grading Queue** - ระบบ queue สำหรับประมวลผลจำนวนมากแบบ async

### 12.3 Exam & Question Management
- **[ ] Question Bank** - คลังข้อสอบที่ใช้ซ้ำได้ข้ามห้องเรียน
- **[ ] Question Categories** - แบ่งหมวดหมู่ข้อสอบตามหัวข้อ (LO, Bloom's Taxonomy)
- **[ ] Randomized Questions** - สุ่มคำถาม/ตัวเลือกสำหรับแต่ละนักเรียน
- **[ ] Time Extension** - ฟีเจอร์ขยายเวลาสอบสำหรับนักเรียนพิเศษ
- **[ ] Auto-save Draft** - บันทึกคำตอบอัตโนมัติระหว่างทำข้อสอบ

### 12.4 Analytics & Reporting
- **[ ] Learning Analytics Dashboard** - วิเคราะห์จุดอ่อนจุดแข็งของนักเรียน
- **[ ] Comparative Analysis** - เปรียบเทียบผลสอบระหว่างห้องเรียน/เทอม


### 12.5 User Experience
- **[ ] Dark Mode** - โหมดมืดสำหรับการใช้งานกลางคืน
- **[ ] Mobile App** - Native iOS/Android app หรือ PWA
- **[ ] Offline Mode** - ทำข้อสอบได้แม้ไม่มี internet แล้ว sync ภายหลัง
- **[ ] Rich Text Editor** - แก้ไขคำตอบพร้อม formatting (bold, code block)

### 12.6 Infrastructure
- **[ ] PostgreSQL Migration** - ย้ายจาก SQLite 
- **[ ] Cloud Storage** - ใช้ AWS S3/Google Cloud Storage แทน local storage 
- **[ ] CDN Integration** - เพิ่มความเร็วในการโหลดรูปภาพ
- **[ ] Redis Caching** - Cache ผลการตรวจและข้อมูลที่เข้าถึงบ่อย
- **[ ] Docker Compose** - Containerization สำหรับ deployment ที่ง่ายขึ้น
- **[ ] CI/CD Pipeline** - Automated testing และ deployment

### 12.7 Collaboration
- **[ ] Peer Review** - นักเรียนตรวจคำตอบซึ่งกันและกัน (peer grading)
- **[ ] Group Assignments** - รองรับการส่งงานกลุ่ม
- **[ ] Discussion Forum** - กระดานถาม-ตอบสำหรับแต่ละห้องเรียน
- **[ ] Announcement System** - ระบบประกาศจากอาจารย์พร้อม read receipt

### 12.8 AI Enhancements
- **[ ] Auto-rubric Generation** - AI สร้างเกณฑ์คะแนนอัตโนมัติจากคำถาม
- **[ ] Smart Rescoring** - ปรับคะแนนอัตโนมัติเมื่อมีการเปลี่ยน rubric
- **[ ] Essay Quality Metrics** - วิเคราะห์ความยาว, ความซับซ้อน, readability

---

**สร้างเมื่อ**: April 2026  
**อัปเดตล่าสุด**: April 2026  
**เวอร์ชัน**: 1.0.0
