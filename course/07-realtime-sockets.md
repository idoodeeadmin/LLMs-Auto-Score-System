# บทที่ 7: ระบบแจ้งเตือน Real-time ด้วย WebSockets ⚡

ในเว็บทั่วไป (HTTP Protocol) การสื่อสารจะเป็นแบบ **ถาม-ตอบ (Request-Response)** เสมอ
หมายความว่า ลูกค้า (Frontend) ต้องเป็นคนเดินไปถามร้านค้า (Backend) ว่า "ของมาหรือยัง?" "ของมาหรือยัง?" ถ้าร้านบอกยังไม่มา ลูกค้าก็ต้องกลับไป แล้วเดินมาถามใหม่ (Polling)

**ปัญหา:** การตรวจข้อสอบด้วย AI อาจใช้เวลานาน (5 - 30 วินาที) ถ้านักเรียนนั่งรอหน้าโหลด (Loading spinner) ก็จะรู้สึกว่าเว็บช้าและอาจกดปิดเว็บหนีไปก่อน

---

## 🔌 เข้าสู่โลกของ WebSockets

WebSockets เป็นโปรโตคอลที่สร้าง **"ท่อสื่อสารที่เปิดค้างไว้ตลอดเวลา"** ระหว่าง Frontend กับ Backend 
พอมีท่อนี้แล้ว Frontend ไม่จำเป็นต้องเดินไปถามพร่ำเพรื่ออีกต่อไป... เพราะเมื่อไหร่ที่ตรวจข้อสอบเสร็จ Backend จะ "ตะโกน (Push/Broadcast)" กลับมาตามท่อนี้ เพื่อให้หน้าจอ Frontend อัปเดตคะแนนทันที!

### โครงสร้างของระบบ Notification
ในโปรเจกต์ Evaly เรามี **Node.js + Socket.io** ทำหน้าที่เป็นพนักงานรับส่งข้อความแบบ Real-time แยกต่างหากจาก FastAPI ครับ

1. **Frontend (React)** ทำการต่อสาย (Connect) ไปหา Socket.io Server ทิ้งไว้
2. นักเรียนกดปุ่ม "ส่งคำตอบ" ไปให้ **FastAPI (Backend)**
3. FastAPI แอบเอาข้อสอบไปให้ AI ตรวจแบบเงียบๆ (Background Task) โดยตอบ Frontend ทันทีว่า "ส่งเรียบร้อยแล้ว แป๊บนึงนะเดี๋ยวตรวจให้" (Frontend ก็เลิกโหลด แล้วไปทำอย่างอื่นได้เลย)
4. พอ AI ตรวจเสร็จ **FastAPI** จะยิงคำสั่งลับ (Webhook) ไปบอก **Socket.io Server** ว่า "ข้อสอบนาย A ตรวจเสร็จแล้ว ได้ 8/10"
5. **Socket.io Server** จะกระจายเสียง (Broadcast) วิ่งตามท่อไปบอก Frontend ของนาย A 
6. หน้าจอของนาย A ก็จะมี Notification เด้งขึ้นมาป๊อปอัปว่า "ตรวจข้อสอบเสร็จแล้ว!"

---

## 🛠️ ตัวอย่างโค้ดฝั่งหน้าบ้าน (React + Socket.io-client)

เราติดตั้งแพ็กเกจ `socket.io-client` ในโฟลเดอร์หน้าบ้าน แล้วไปที่ไฟล์ Context หรือไฟล์แจ้งเตือน

```tsx
import { useEffect } from 'react';
import { io } from 'socket.io-client';
import { toast } from 'sonner';

export default function NotificationListener({ userId }) {
  
  useEffect(() => {
    // 1. เชื่อมต่อไปยังเซิร์ฟเวอร์ Socket.io
    const socket = io('http://localhost:3000'); 
    
    // 2. ขอเข้าร่วมห้อง (Room) ที่เป็นรหัสส่วนตัวของเรา
    socket.emit("join_room", `user_${userId}`);

    // 3. ดักฟัง! ถ้ามีข้อความในหัวข้อ "exam_graded" ส่งมาหาห้องเรา
    socket.on("exam_graded", (data) => {
      // 4. แสดง ป๊อปอัป แจ้งเตือน!
      toast.success(`ตรวจข้อสอบวิชา ${data.exam_name} เสร็จแล้ว! ได้คะแนน ${data.score}`);
    });

    // คืนค่ากลับ (ตัดสาย) เมื่อผู้ใช้ปิดหน้าเว็บ
    return () => {
      socket.disconnect();
    };
  }, [userId]);

  return null; // Component นี้ไม่มีหน้าตา แค่ดักฟังหลังบ้านเงียบๆ
}
```

เมื่อประกอบทุกอย่างเข้าด้วยกัน เราก็จะได้เว็บแอปพลิเคชันที่สมบูรณ์แบบ ทั้งว่องไว (React) ฉลาด (Gemini AI) และโต้ตอบได้ทันที (Socket.io) 

ในบทสุดท้าย เราจะมาดูวิธีเอาเว็บเทพๆ นี้ ไปแจกให้เพื่อนใช้กันครับ (Deployment)!
