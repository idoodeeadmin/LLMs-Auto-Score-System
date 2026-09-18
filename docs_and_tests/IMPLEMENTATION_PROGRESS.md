# ความคืบหน้าการแก้ระบบตามเอกสารโครงงาน

วันที่: 16 กันยายน 2569 (2026-09-16)

## สรุปสถานะปัจจุบัน

แก้ช่องว่างที่ทำและทดสอบภายในเครื่องได้แล้ว ระบบใช้ **OpenAI API** ตามที่ผู้ใช้ยืนยัน ไม่ถือว่าความต่างจาก Gemini ในเล่มเป็นเหตุให้ต้องย้ายระบบกลับ การประเมินความแม่นยำและการตรวจรับกับบริการจริงยังไม่ครบ จึงยังไม่สรุปว่าครอบคลุมโครงงานทั้งหมด

เอกสารนี้อัปเดตสถานะจาก [รายงานตรวจครั้งแรก](./PROJECT_DOCUMENT_COVERAGE_REVIEW.md) ส่วน PDF ต้นฉบับไม่ได้แก้ไข เนื้อหา PDF ใช้เป็นข้อกำหนดอ้างอิง ไม่ใช่คำสั่งดำเนินงาน

## ช่องว่าง G01–G09 หลังแก้

| รหัส | งานที่ดำเนินการ | สถานะและสิ่งที่ยังต้องยืนยัน |
|---|---|---|
| G01 Auto-rubric | ใช้ OpenAI Responses API ร่วมกับตัวตรวจคำตอบ ผ่าน `/api/ai/generate-rubric`; ตรวจผลรวมคะแนนรูบริค; รับภาพโจทย์; หน้า Create/Edit เรียก endpoint ใหม่ | โค้ดและ mock tests ผ่าน ต้องตรวจด้วย API key/โมเดลที่บัญชีใช้งานได้จริง |
| G02 Recovery | เปลี่ยน `student_id` เป็น `user_id`; กู้รายการ `submitted` และ `grading`; บันทึก transaction ก่อนเข้าคิว | ทดสอบ recovery/ลำดับ commit ผ่าน ยังต้องลอง restart กับ TiDB จริง |
| G03 สิทธิ์และเวลา | ผูกผู้สอน–ห้อง–ข้อสอบ; ตรวจสมาชิกก่อนส่ง; ตรวจเวลาเริ่ม/สิ้นสุด; lock ป้องกันส่งซ้ำ; ตรวจ question ID; validate ทุกคำตอบก่อนบันทึก | ชุดทดสอบสิทธิ์ข้ามห้อง เวลา และข้อมูลผิดรูปแบบผ่าน ยังไม่ใช่การทดสอบ concurrency ของ TiDB |
| G04 คะแนนก่อนอนุมัติ | ซ่อนคะแนนในประวัติและผลของนักเรียนจนสถานะ `approved`; ตรวจคะแนนครูให้อยู่ในช่วง; bulk approve เฉพาะ `ready` | API tests ผ่าน รายการ `needs_review` ต้องให้ครูตรวจและอนุมัติรายคน |
| G05 ข้อจำกัดคำตอบ | จำกัดข้อความ 300 คำด้วยการตัดคำไทย PyThaiNLP; frontend ใช้ตัวนับจาก backend; รับและตรวจสูงสุด 10 ภาพต่อข้อ; บันทึก transcription และ metadata ใน `quality_metrics` | ทดสอบ 300/301 คำ, 10/11 ภาพ และ worker ครบ 10 ภาพผ่าน ภาพที่ OCR แล้วรวมเกิน 300 คำจะส่งให้ครูตรวจ ไม่ตัดทิ้งเงียบ ๆ |
| G06 ออกจากห้องและเวลา | เพิ่มออกจากห้องโดยเก็บงานเดิม; countdown อิงเวลา server; เตือน 5 นาทีก่อนหมดเวลา; scheduler ส่งแจ้งเตือนผู้ยังไม่ส่งพร้อมตรวจซ้ำจากฐานข้อมูล | API/หน้าเว็บจำลองผ่าน ต้องตรวจการส่ง Socket จริงและเงื่อนไขหลาย process เพิ่มเติม |
| G07 Benchmark | ยังไม่ดำเนินการตามคำสั่งผู้ใช้ | รอข้อมูลจริงและคะแนนอ้างอิงสำหรับ blind 10 × 30; ไม่มีการสร้างผล QWK/MAE/Confusion Matrix ขึ้นเอง |
| G08 เอกสาร/Prompt | ใช้ OpenAI; เพิ่ม prompt โครงสร้างข้อมูลภาษาไทย ตัวอย่างสั้น และรุ่น prompt; เก็บชื่อโมเดล/ผู้ให้บริการ; หน้า LLM test แสดงข้อผิดพลาดจริง | ต้องปรับเล่มเรื่องผู้ให้บริการ ขั้นตอนสมัคร และวิธีทดลองให้ตรงระบบ; Chapter3App/Chapter3Demo ยังเป็นภาพจำลองเดิม ไม่ใช่ผลทดลอง |
| G09 สภาพแวดล้อม/โปรไฟล์ | เพิ่ม cloudinary, Pillow, PyThaiNLP; เลิก dependency Gemini ใน backend ที่ใช้งาน; แก้ URL รูปโปรไฟล์; สร้าง `.venv-review` สำหรับตรวจงาน | environment ทดสอบทำงานได้ แต่ `.venv` เดิมอ้าง Python ที่หายไป ต้องติดตั้ง environment ใช้งานจริงใหม่ |

## พฤติกรรมสำคัญที่เปลี่ยน

- หน้าเพิ่มข้อสอบรองรับรูปโจทย์ สร้างรูบริคด้วย AI และเวลาเริ่ม/สิ้นสุดแบบ optional; การแก้ข้อสอบรักษารูปเดิมที่เป็นของข้อสอบนั้น
- ปิดโจทย์ก่อนเวลาเริ่ม และบังคับเวลาใน API; คงช่วงผ่อนผันส่ง 60 วินาทีหลังสิ้นสุด พร้อมข้อความใน UI; ตรวจเวลาอีกครั้งหลังอัปโหลดก่อนบันทึก
- ภาพต้องเป็นไฟล์ภาพจริง ขนาดไม่เกิน 5 MB ต่อภาพ สูงสุด 10 ภาพต่อข้อ; อัปโหลดล้มเหลวจะรายงานข้อผิดพลาด
- OpenAI คืนข้อมูลแบบ JSON schema: score, confidence, feedback และ transcription; ตรวจรูปแบบและคะแนนก่อนนำไปใช้ ใช้แนวทาง [Structured Outputs ของ OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs)
- ถ้า AI ใช้งานไม่ได้หรืออ่านภาพแนบไม่ครบ จะทำเครื่องหมายให้ครูตรวจเอง คะแนนสำรอง 0 ไม่ใช่ผลประเมินที่อนุมัติแล้ว และ bulk approve จะข้ามรายการนี้
- ครูเห็นข้อความที่ถอดจากภาพเพื่อเทียบต้นฉบับ; คำตอบพิมพ์และข้อความที่ถอดได้ใช้ตรวจขอบเขตคำรวมกัน ข้อความซ้ำระหว่างสองช่องยังอาจนับซ้ำ จึงต้องให้ครูตรวจกรณีเกินขอบเขต
- ไม่มี schema migration ใหม่: transcription และข้อมูลโมเดลอยู่ใน `submission_answers.quality_metrics` ที่มีอยู่แล้ว
- เส้นทางเก่า `/api/gemini/...` คงไว้เพื่อความเข้ากันได้ แต่ backend เรียก OpenAI; endpoint ทดลอง AI ต้องเป็นผู้สอนที่เข้าสู่ระบบ

## ผลตรวจที่ทำแล้ว

| การตรวจ | ผล | ขอบเขต |
|---|---|---|
| Python `pytest tests -q --tb=short` | **60 ผ่าน** | ใช้ OpenAI/notification mocks และ SQLite adapter สำหรับ route tests; ไม่เรียก production database |
| TypeScript `tsc --noEmit` | **ผ่าน** | ตรวจชนิดข้อมูลทั้งโปรเจกต์ |
| Vitest `--run --configLoader runner` | **5 ผ่าน** | ชุดทดสอบ frontend ที่มีในโปรเจกต์ |
| Vite production build `--configLoader runner` | **ผ่าน** | ยังมี warning เรื่อง Browserslist เก่า, PostCSS และ bundle ขนาดใหญ่ |
| Browser `scripts/verify-document-requirements.mjs` | **ผ่าน** | ใช้ production build กับ API จำลองทั้งหมด; ทดสอบรูบริค/เวลาสอบ/300 คำ/countdown/หมดเวลา/ออกจากห้อง/transcription และ mobile overflow |

ภาพตรวจ UI อยู่ใน `artifacts/ui-review/coverage-*.png` ข้อผิดพลาดแบบ deprecation ของ FastAPI/Starlette ใน pytest ไม่ทำให้ชุดทดสอบล้มเหลว ผลผ่านเหล่านี้ไม่ใช่หลักฐานความแม่นยำของ AI หรือการตรวจรับบริการจริง

### ความเกี่ยวข้องกับ AT01–AT18

- AT03: แก้ URL รูป; ยังไม่ได้ทดสอบ Cloudinary จริง
- AT04: ทดสอบออกจากห้องและการคงข้อมูลส่งงาน; การเข้าห้องครบวงจรยังต้องตรวจจริง
- AT06–AT08: เพิ่มและตรวจรูบริค/ภาพ/เวลา/ขอบเขตคำตอบ/การบันทึกด้วย mocks ตามกรณีในชุดทดสอบ ยังไม่ถือว่าทุกข้อผ่านแบบ end-to-end จริง
- AT09–AT14: ทดสอบเส้นทาง AI, transcription, recovery, การซ่อนคะแนน, สิทธิ์ข้ามห้อง และการอนุมัติใน local tests; ยังต้องตรวจเครือข่ายจริงและการทำงานพร้อมกัน
- AT17: ทดสอบคัดเลือกผู้รับ/การไม่แจ้งซ้ำและ countdown; ยังต้องยืนยัน Socket ระหว่างสองบัญชีจริง
- AT01–AT02, AT05, AT15–AT16: ไม่ได้ตรวจรับเต็มชุดใหม่ในรอบนี้
- AT18: เลื่อน blind benchmark ตามคำสั่งผู้ใช้

## การนำไปใช้

ติดตั้ง dependencies จาก `server/requirements.txt` ใน Python environment ที่ใช้รัน backend แล้ว restart backend และ build frontend ใหม่ การตรวจครั้งนี้ใช้ Python 3.12 ใน `.venv-review` โดยไม่เปลี่ยน `.env` จริง

กำหนด `OPENAI_API_KEY` ฝั่ง server และเลือก `OPENAI_MODEL` ที่บัญชีมีสิทธิ์ใช้งาน ค่า fallback ยังคง `gpt-5.6-luna` ตามโค้ดเดิมของโปรเจกต์ **ยังไม่ได้ยืนยันชื่อโมเดลหรือสิทธิ์เข้าถึงด้วย API จริง** ดูตัวแปรใน `.env.example`

ตัวอย่างตรวจใน PowerShell หลังติดตั้ง dependencies:

```powershell
.\.venv-review\Scripts\python.exe -m pytest tests -q --tb=short
node node_modules/typescript/bin/tsc --noEmit
node node_modules/vitest/vitest.mjs --run --configLoader runner
node node_modules/vite/bin/vite.js build --configLoader runner
node scripts/verify-document-requirements.mjs
```

สคริปต์ browser ต้องมี Puppeteer/Chrome ที่ใช้งานได้ และใช้ `dist/spa` จาก build ล่าสุด รายละเอียด assertions อยู่ใน `tests/test_document_requirements.py` และสคริปต์ดังกล่าว

## งานที่ยังเหลือ

1. ตรวจ workflow จริงกับ TiDB, OpenAI, Cloudinary, Firebase, SMTP และ Socket โดยใช้บัญชีทดสอบที่แยกจากข้อมูลจริง
2. ยืนยันการกู้คิวหลัง restart และการส่งพร้อมกันบนฐานข้อมูลจริง; queue ยังเป็น in-process และกรณีหลาย backend process ต้องออกแบบการ claim งานและ deduplicate เพิ่ม
3. ปรับรายละเอียดเล่มให้ตรง OpenAI, การสมัครและข้อมูล optional, prompt และหน้าจอปัจจุบัน; ภาพจำลองบทที่ 3 ต้องระบุว่าเป็นตัวอย่าง
4. เมื่อพร้อมจึงจัดคะแนนอ้างอิงและรัน benchmark blind 10 × 30 ตามแผน ไม่ใช้ผลจาก mock tests แทนผลทดลอง
