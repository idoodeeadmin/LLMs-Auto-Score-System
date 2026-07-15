# บทที่ 5: ฐานข้อมูลและการเชื่อมต่อ (Database & SQL) 🗄️

ข้อมูลทุกอย่างของระบบ Evaly ทั้งบัญชีผู้ใช้, รายชื่อห้องเรียน, ข้อสอบ, และคะแนนสอบ จะต้องถูกจัดเก็บอย่างเป็นระเบียบและปลอดภัย ในบทนี้เราจะมาดูกันว่าเราใช้ฐานข้อมูลแบบไหน และเชื่อมต่อกับ Python อย่างไรครับ

---

## 🛢️ TiDB (MySQL-Compatible)

ในโปรเจกต์นี้ เราเลือกใช้ **TiDB** (Ti Database) หรือคุณสามารถใช้ MySQL ก็ได้ เพราะ TiDB ถูกออกแบบมาให้ทำงานได้เหมือน MySQL เป๊ะๆ แต่มีข้อดีคือ:
- **Cloud-native:** เหมาะกับการรันบนคลาวด์
- **Scalability:** ถ้าข้อมูลใหญ่ขึ้นเป็นล้านๆ เรคคอร์ด มันสามารถกระจายข้อมูลไปหลายๆ เซิร์ฟเวอร์ได้แบบเนียนๆ

เนื่องจากมันเป็น Relational Database (SQL) ข้อมูลทั้งหมดจะถูกเก็บเป็น "ตาราง" ที่มีความสัมพันธ์กัน (Relational)

### 📊 โครงสร้างตาราง (Database Schema)
ตัวอย่างตารางหลักๆ ในระบบเรา:
1. **`users`**: เก็บข้อมูลผู้ใช้งาน (อีเมล, รหัสผ่าน, รูปภาพ)
2. **`rooms`**: เก็บข้อมูลห้องเรียน (รหัสเข้าห้อง, ชื่อวิชา)
3. **`room_members`**: ตารางเชื่อม (Join Table) ว่าใครอยู่ห้องไหนบ้าง (นักเรียน -> ห้อง)
4. **`exams`**: เก็บข้อมูลข้อสอบ (ชื่อข้อสอบ, คำสั่ง)
5. **`exam_submissions`**: เก็บคำตอบของนักเรียน, ภาพถ่ายลายมือ, และคะแนนที่ AI ตรวจเสร็จแล้ว

---

## 🔌 การเชื่อมต่อ Python เข้ากับ Database

ลองเปิดไฟล์ `server/database.py` ดูครับ ไฟล์นี้คือศูนย์กลางในการติดต่อสื่อสารกับฐานข้อมูล
ปกติแล้วการสั่งฐานข้อมูล เราต้องเขียนคำสั่ง SQL เพียวๆ (เช่น `SELECT * FROM users;`) 
โปรเจกต์เราใช้การเชื่อมต่อผ่านไลบรารี `mysql-connector-python` หรือใช้ `aiomysql` (สำหรับการทำงานแบบ Asynchronous)

### การอ่านข้อมูล (SELECT)
ตัวอย่างฟังก์ชันเวลาต้องการดึงข้อมูลห้องเรียน
```python
import mysql.connector

def get_all_rooms():
    # 1. เชื่อมต่อ (Connect)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="evaly_db"
    )
    cursor = conn.cursor(dictionary=True) # ให้ผลลัพธ์เป็น Dictionary
    
    # 2. ยิงคำสั่ง SQL
    cursor.execute("SELECT * FROM rooms")
    
    # 3. รับข้อมูลกลับมา
    rooms = cursor.fetchall()
    
    # 4. ปิดการเชื่อมต่อ
    cursor.close()
    conn.close()
    
    return rooms
```

### การเขียนข้อมูล (INSERT / UPDATE)
เวลาเขียนข้อมูล หรือลบข้อมูล สิ่งสำคัญคือต้องมีการ **Commit** เพื่อย้ำให้ฐานข้อมูลบันทึกจริงๆ
```python
def create_room(name, code, owner_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ป้องกัน SQL Injection โดยใช้การแทนที่ด้วย %s
    sql = "INSERT INTO rooms (name, class_code, owner_id) VALUES (%s, %s, %s)"
    val = (name, code, owner_id)
    
    cursor.execute(sql, val)
    
    # ต้อง Commit! ไม่งั้นข้อมูลจะไม่เซฟ
    conn.commit()
    
    # ดึง ID ของห้องที่เพิ่งสร้างมาใช้ต่อ
    new_id = cursor.lastrowid
    conn.close()
    
    return new_id
```

> **ข้อควรระวัง (Security Warning):** เราจะไม่เอาข้อมูลที่รับจากผู้ใช้มาต่อ String ด้วยการใช้ `+` หรือ f-string ลงในคำสั่ง SQL ตรงๆ เด็ดขาด! (เช่น `f"SELECT * FROM users WHERE name = '{user_input}'"`) เพราะจะโดนแฮกเกอร์โจมตีด้วยวิธี **SQL Injection** ได้เสมอครับ เราจึงต้องใช้ `(%s, %s)` ตามที่แสดงให้ดูในโค้ดด้านบน

ตอนนี้หลังบ้านของเราสามารถรับข้อมูลจากหน้าบ้าน และบันทึกลงฐานข้อมูลได้แล้ว ในบทต่อไปเราจะมาดู "ไฮไลท์" ของโปรเจกต์กัน นั่นคือการส่งข้อมูลไปหา AI ครับ!
