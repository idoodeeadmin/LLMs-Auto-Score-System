# บทที่ 4: การตั้งค่า Backend ด้วย FastAPI (Python) 🐍

หลังจากที่เราทำหน้าบ้าน (Frontend) เสร็จแล้ว ตอนนี้หน้าเว็บของเราก็เหมือนห้างสรรพสินค้าที่ตกแต่งสวยงาม แต่ยังไม่มีพนักงานคอยบริการ ในบทนี้เราจะมาสร้างพนักงานหลังบ้าน (Backend) ด้วย **FastAPI** ในภาษา Python กันครับ

---

## 🤔 ทำไมถึงเลือกใช้ FastAPI?

ในฝั่งของภาษา Python มี Framework สำหรับทำเว็บชื่อดังอย่าง Django และ Flask อยู่แล้ว ทำไมเราถึงเลือกใช้ FastAPI แทน?

1. **เร็วมาก (High Performance):** ชื่อ FastAPI ไม่ได้ตั้งมาเท่ๆ แต่มันทำงานได้เร็วเทียบเท่ากับ NodeJS หรือ Go เพราะมันรองรับการทำงานแบบ Asynchronous (ทำหลายงานพร้อมกันได้)
2. **สร้าง Document ให้ฟรี (Swagger):** พอเราเขียน API เสร็จ FastAPI จะสร้างหน้าคู่มือ API (ที่ `http://localhost:8000/docs`) ให้แบบอัตโนมัติ ทำให้คนทำหน้าบ้านรู้ว่าจะต้องต่อ API ยังไง
3. **การตรวจสอบ Type (Type Hinting):** คล้ายๆ กับ TypeScript FastAPI บังคับให้เราใส่ชนิดตัวแปร ซึ่งช่วยลดบัคได้เยอะมาก

---

## 📁 โครงสร้างโปรเจกต์ฝั่ง Backend (`/server`)

โฟลเดอร์ `/server` ในโปรเจกต์ Evaly มีโครงสร้างที่ควรรู้จักดังนี้:

- `main.py`: จุดเริ่มต้นของเซิร์ฟเวอร์
- `database.py`: ตัวตั้งค่าการเชื่อมต่อกับฐานข้อมูล (TiDB/MySQL)
- `models.py`: สร้างโมเดลของข้อมูล (เทียบเท่ากับ Interface/Struct)
- `routes/`: แยกย่อย API ตามหมวดหมู่ เช่น ระบบล็อกอิน, ระบบห้องเรียน
- `requirements.txt`: สมุดจดรายชื่อ Library (แพ็กเกจ) ของ Python ที่ต้องติดตั้ง

**วิธีติดตั้งแพ็กเกจที่จำเป็น:**
```bash
pip install -r server/requirements.txt
```

---

## 🚦 การสร้าง API Endpoint (จุดรับส่งข้อมูล)

ลองมาดูตัวอย่างการสร้าง API ง่ายๆ ใน `main.py` กันครับ

```python
from fastapi import FastAPI

# 1. สร้างตัวเซิร์ฟเวอร์
app = FastAPI()

# 2. สร้าง Endpoint แบบ GET
@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "Pong!"}
```

ถ้าเราใช้คำสั่งรันเซิร์ฟเวอร์ (`uvicorn server.main:app --reload --port 8001`) แล้วเอาเบราว์เซอร์เข้าไปที่ `http://localhost:8001/api/ping` เราก็จะได้ข้อมูล JSON ส่งกลับมาว่า `{"status": "ok", "message": "Pong!"}` ครับ

### การทำงานแบบ Asynchronous (คีย์เวิร์ด `async` / `await`)

เวลาเซิร์ฟเวอร์ต้องไปดึงข้อมูลจากฐานข้อมูล หรือเรียก AI (Gemini) มันต้อง "รอ" ครับ
ถ้าเขียนแบบปกติ เซิร์ฟเวอร์จะค้างและไม่รับแขกคนอื่นเลยจนกว่าจะทำเสร็จ แต่ถ้าเราใส่ `async` และ `await` เซิร์ฟเวอร์จะรับงานไว้ รอให้ข้อมูลมา แล้วแวะไปรับแขกคนอื่นพลางๆ ก่อนได้

```python
@app.get("/api/rooms")
async def get_rooms():
    # การไปดึงฐานข้อมูลต้องใช้เวลา เลยต้องใส่ await ให้เซิร์ฟเวอร์ไปทำอย่างอื่นรอ
    rooms = await fetch_rooms_from_db()
    return rooms
```

---

## 🛡️ การทำระบบ Authentication (Login/Register)

ระบบ Evaly มีการจัดการระบบ Auth ด้วย **JWT (JSON Web Token)**
หลักการคือ:
1. ผู้ใช้ส่ง Username/Password หรือ Google Firebase Token มาหา Backend
2. Backend ตรวจสอบความถูกต้อง
3. ถ้าผ่าน Backend จะ "ออกบัตรประจำตัว" (JWT Token) ที่มีลายเซ็นดิจิทัลส่งกลับไป
4. ในครั้งถัดไปที่ Frontend จะขอดูข้อมูล (เช่น ขอดูรายชื่อห้องเรียน) ก็แค่แนบบัตรประจำตัวนี้มาพร้อมกับ Request
5. Backend แค่เช็คว่าบัตรหมดอายุหรือยัง และลายเซ็นถูกไหม โดยไม่ต้องไปดึงข้อมูลผู้ใช้ซ้ำทุกครั้ง

ตัวอย่างการป้องกัน API:
```python
@app.get("/api/protected-data")
async def get_secret_data(current_user = Depends(get_current_user)):
    # โค้ดในบรรทัดนี้จะทำงานก็ต่อเมื่อ get_current_user ยืนยัน Token ได้สำเร็จแล้วเท่านั้น
    return {"message": f"Hello {current_user.name}"}
```

ในบทต่อไป เราจะไปดูหัวใจสำคัญในการเก็บข้อมูล นั่นก็คือ **Database และ ORM** ครับ!
