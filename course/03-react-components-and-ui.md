# บทที่ 3: การสร้าง React Components และ UI 🎨

ในบทนี้ เราจะมาเรียนรู้วิธีการ "ปั้น" หน้าเว็บแต่ละหน้าขึ้นมา โดยการใช้แนวคิดของ **Component-Based Architecture** ซึ่งเป็นหัวใจสำคัญของ React กันครับ

---

## 🧱 Component คืออะไร?

ในอดีต ถ้าเราจะสร้างหน้าเว็บยาวๆ 1 หน้า เราต้องเขียน HTML ยาวเหยียดไว้ในไฟล์เดียว แต่สำหรับ React เรามองทุกอย่างเป็น **"ชิ้นส่วนเลโก้" (Component)** ครับ

ตัวอย่างเช่น ในหน้า Dashboard แทนที่เราจะเขียนโค้ดทั้งหมดไว้ที่เดียวกัน เราจะแยกมันออกเป็นส่วนๆ:
1. `Navbar` (แถบเมนูด้านบน)
2. `Sidebar` (เมนูแถบข้าง)
3. `ExamCard` (การ์ดแสดงรายวิชา)

พอแยกแบบนี้ โค้ดจะอ่านง่ายขึ้น และชิ้นส่วนไหนใช้บ่อยๆ (เช่น ปุ่ม) เราก็เอาไปใช้ซ้ำ (Reuse) ในหน้าอื่นได้ด้วย

---

## 🎨 การแต่งหน้าเว็บด้วย TailwindCSS

อย่างที่บอกไปในบทแรกว่าเราใช้ TailwindCSS ในการแต่งเว็บ ลองมาดูความแตกต่างกันครับ

**ถ้าเขียน CSS ปกติ:**
```html
<button class="my-button">คลิกเลย</button>

<style>
.my-button {
    background-color: blue;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
}
</style>
```

**ถ้าเขียนแบบ TailwindCSS (ใน React):**
```tsx
<button className="bg-blue-500 text-white px-4 py-2 rounded-md">
  คลิกเลย
</button>
```
เห็นไหมครับ! เราไม่ต้องสลับไปเขียนไฟล์ CSS เลย แค่พิมพ์คลาสอธิบายลงไปตรงๆ (เช่น `bg-blue-500` = สีพื้นหลังสีฟ้า)

---

## 🧠 State & Props (ความจำและการสื่อสาร)

React มีแนวคิด 2 อย่างที่ทำให้เว็บ "มีชีวิต" (ตอบสนองต่อผู้ใช้ได้) คือ State และ Props

### 1. State (`useState`) - ความจำส่วนตัว
ใช้จำข้อมูลที่ "เปลี่ยนแปลงได้" ในหน้านั้นๆ เช่น การนับจำนวนการคลิก หรือสิ่งที่ผู้ใช้พิมพ์ในช่องค้นหา

```tsx
import { useState } from "react";

export default function Counter() {
  // สร้างความจำชื่อ count เริ่มต้นที่ 0
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>คุณคลิกไปแล้ว {count} ครั้ง</p>
      <button onClick={() => setCount(count + 1)}>บวกเพิ่ม</button>
    </div>
  );
}
```
*เมื่อใดก็ตามที่ State เปลี่ยนแปลง React จะทำการ "วาดหน้าจอใหม่ (Re-render)" โดยอัตโนมัติ!*

### 2. Props - การส่งของให้ฟังก์ชันอื่น
เหมือนการพาส Parameter ในภาษา C ครับ ใช้สำหรับส่งข้อมูลจาก Component ตัวแม่ ไปหาตัวลูก

```tsx
// สร้างกล่องเลโก้ที่รอรับชื่อวิชา
function ExamCard(props: { title: string }) {
  return <div className="border p-4">{props.title}</div>;
}

// นำมาใช้งาน
function Dashboard() {
  return (
    <div>
      <ExamCard title="Software Engineering 101" />
      <ExamCard title="Database Systems" />
    </div>
  );
}
```

---

## 🌐 การดึงข้อมูลจาก API (Data Fetching)

เมื่อหน้าเว็บพร้อมแล้ว เราต้องดึงข้อมูลจริงจากหลังบ้านมาแสดง เราจะใช้สิ่งที่เรียกว่า `useEffect` และฟังก์ชัน `fetch` พื้นฐานของเบราว์เซอร์ครับ

```tsx
import { useState, useEffect } from "react";

export default function RoomList() {
  const [rooms, setRooms] = useState([]); // เริ่มต้นด้วย Array ว่าง

  // useEffect ทำงานแค่ครั้งเดียวตอนเปิดหน้านี้ขึ้นมา
  useEffect(() => {
    const fetchRooms = async () => {
      // ดึงข้อมูลจาก API หลังบ้าน
      const response = await fetch("/api/rooms");
      const data = await response.json();
      
      // เอาข้อมูลที่ได้มา เก็บใส่ State
      setRooms(data);
    };

    fetchRooms();
  }, []);

  return (
    <div>
      {rooms.map((room) => (
        <p key={room.id}>{room.name}</p> // วนลูปแสดงชื่อห้องเรียน
      ))}
    </div>
  );
}
```

หลักการก็ง่ายๆ แค่นี้เลยครับ! เปิดหน้าเว็บมา -> ดึงข้อมูล -> เก็บใส่ State -> React เอา State มาวาดลงหน้าจอ 

พอจะเห็นภาพการทำงานของหน้าบ้านหรือยังครับ? ในบทหน้าเราจะข้ามไปดูฝั่งหลังบ้าน (Backend) กันบ้าง ว่าไอ้ `/api/rooms` เนี่ย มันถูกสร้างมายังไง!
