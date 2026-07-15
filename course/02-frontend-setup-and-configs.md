# บทที่ 2: หน้าบ้าน (Frontend Setup & Configs) 🛠

หลังจากเข้าใจภาพรวมในบทแรกไปแล้ว ในบทนี้เราจะมาเจาะลึกที่โฟลเดอร์ฝั่งหน้าบ้าน (Client) กันครับ ว่าโปรเจกต์นี้เซ็ตอัปขึ้นมาได้ยังไง และไฟล์ Config ยึกยือๆ มากมายที่อยู่ในโฟลเดอร์ Root (`vite.config.ts`, `tailwind.config.ts`, `tsconfig.json`) มีหน้าที่อะไรกันแน่

---

## 📁 โครงสร้างโปรเจกต์

โดยปกติแล้วเมื่อใช้คำสั่งสร้างโปรเจกต์ Vite (เช่น `pnpm create vite client --template react-swc-ts`) เราจะได้โครงสร้างโฟลเดอร์ประมาณนี้:

```text
/client
  ├── /components    (ส่วนประกอบย่อยๆ เช่น ปุ่ม, กรอบข้อความ)
  ├── /contexts      (ตัวจัดการสถานะส่วนกลาง เช่น AuthContext)
  ├── /pages         (หน้าเว็บหลัก เช่น Home, Profile, Login)
  ├── /lib           (ฟังก์ชันตัวช่วย หรือการตั้งค่า Firebase)
  ├── App.tsx        (จุดเริ่มต้นของการแบ่งหน้าเว็บ Routing)
  └── global.css     (ไฟล์ CSS หลักที่มี Tailwind)
```

---

## ⚙️ ทำความเข้าใจ Config Files

สิ่งสำคัญที่ทำให้โปรเจกต์นี้ทำงานได้อย่างราบรื่นคือไฟล์ Configuration เหล่านี้ครับ:

### 1. `package.json`
ไฟล์นี้คือ "ทะเบียนบ้าน" ของโปรเจกต์ 
- ใช้บอกว่าโปรเจกต์นี้ติดตั้งแพ็กเกจอะไรไปบ้าง (ในหมวด `dependencies` และ `devDependencies`)
- ใช้สร้าง "คำสั่งย่อ" ในหมวด `scripts` เช่น ตอนที่คุณพิมพ์ `pnpm dev` มันก็จะไปเรียกคำสั่ง `vite` ให้ทำงาน

### 2. `vite.config.ts`
ไฟล์ตั้งค่าสำหรับ **Vite** (ตัวจัดการการ Build หน้าเว็บ)
ในโปรเจกต์เรามีการตั้งค่าที่สำคัญคือ:
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./client"),
      "@shared": path.resolve(__dirname, "./shared"),
    },
  },
  // ...
});
```
**ทำไมต้องแก้:** 
สังเกตตรง `alias` นะครับ การตั้งค่าตรงนี้ทำให้เราสามารถ Import ไฟล์โดยใช้ตัว `@` ได้เลย เช่น `import { Button } from "@/components/ui/button"` ไม่ต้องมานั่งเขียน `../../../components` ให้ปวดหัวครับ!

### 3. `tailwind.config.ts`
ไฟล์นี้คือกฎหมายหลักของการตกแต่งเว็บ (Styling)
```typescript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./client/**/*.{js,jsx,ts,tsx}"],
  theme: {
    // กำหนดสีและฟอนต์เฉพาะตัวของโปรเจกต์
  }
}
```
**ทำไมต้องแก้:** 
- `content`: เป็นการบอก Tailwind ว่า "ช่วยไปสแกนหาโค้ดในโฟลเดอร์ `/client` หน่อยนะ แล้วเอาเฉพาะคลาสที่ถูกใช้งานจริงๆ มาสร้างเป็น CSS" 
- `theme`: ใช้กำหนด "ระบบสี" ของแบรนด์ เช่น สี primary, secondary ทำให้เวลาเขียนหน้าเว็บ สีจะคุมโทนไปในทิศทางเดียวกันทั้งหมด

### 4. `tsconfig.json`
ไฟล์ตั้งค่าของ **TypeScript**
บอก TypeScript ว่าจะยอมให้โค้ดหลวมได้แค่ไหน การเปิด `strict: true` จะทำให้ TypeScript เข้มงวดมาก ถ้าเขียนโค้ดผิด Type แม้แต่นิดเดียว มันจะแสดงเส้นสีแดงเตือนทันที

---

## 🛣 การทำ Routing (แบ่งหน้าเว็บ)

พอเราตั้งค่าทุกอย่างเสร็จ จุดเริ่มต้นของการแสดงผลหน้าเว็บจะอยู่ที่ไฟล์ `client/App.tsx`
ในนี้เราใช้ไลบรารี `react-router-dom` เพื่อกำหนดว่า ถ้าผู้ใช้พิมพ์ URL ไหน ให้ไปแสดง Component หน้าไหนครับ

```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Profile from "./pages/Profile";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </BrowserRouter>
  );
}
```

ในบทต่อไป เราจะไปดูข้างในไฟล์ `Index` หรือ `Profile` กันครับ ว่าเวลาเราสร้างหน้าเว็บขึ้นมา 1 หน้าด้วย React เราต้องประกอบมันขึ้นมายังไง!
