# -*- coding: utf-8 -*-
"""
Script to build the authentic Academic Research Paper (บทความวิจัย) 
matching MSU thesis standard (pro2 reference pp. 191-196) and derived 100% 
from Chapters 1-5 of LLM.pdf and chapter4_testcases.html.
"""

import sys
import shutil
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "docs_and_tests" / "chapter4_testcases.html"

def update_research_paper():
    content = HTML_FILE.read_text(encoding="utf-8")

    # 1. Update CSS: Authentic Academic Proceeding Format (No boxes, no thick black lines)
    academic_css = """
/* ========================================================
   Research Paper (บทความวิจัย) Authentic MSU Conference Format
   ======================================================== */
.paper-divider { break-before: page; break-after: page; min-height: 220mm; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.paper-divider h1 { font-family: 'TH Sarabun New', 'Sarabun', Tahoma, sans-serif; font-size: 32px; font-weight: bold; color: #000000; margin: 0; }
.paper-container { break-before: page; margin-top: 10px; font-family: 'TH Sarabun New', 'Sarabun', Tahoma, sans-serif; color: #000000; }
.paper-header { text-align: center; margin-bottom: 12px; }
.paper-title-th { font-size: 20px; font-weight: bold; margin: 0 0 3px; line-height: 1.25; color: #000000; }
.paper-title-en { font-size: 17px; font-weight: bold; margin: 0 0 8px; line-height: 1.25; color: #000000; }
.paper-authors { font-size: 15.5px; font-weight: bold; margin-bottom: 2px; color: #000000; }
.paper-affiliation { font-size: 14.5px; margin-bottom: 2px; color: #000000; }
.paper-emails { font-size: 13.5px; color: #000000; margin-bottom: 12px; }
.paper-body { column-count: 2; column-gap: 20px; text-align: justify; font-size: 14.5px; line-height: 1.26; }
.paper-body h2 { font-size: 15.5px; font-weight: bold; margin: 10px 0 3px; color: #000000; break-after: avoid; page-break-after: avoid; }
.paper-body h3 { font-size: 14.5px; font-weight: bold; margin: 6px 0 2px; color: #000000; break-after: avoid; page-break-after: avoid; }
.paper-body p { text-indent: 0.8cm; margin-bottom: 4px; font-size: 14.5px; line-height: 1.26; text-align: justify; }
.paper-body table { font-size: 11px; line-height: 1.2; margin: 6px 0 8px; width: 100%; break-inside: avoid; page-break-inside: avoid; border-collapse: collapse; }
.paper-body table th, .paper-body table td { padding: 3px 4px; border: 0.5pt solid #000000; }
.paper-body table th { background: #f2f2f2; font-weight: bold; text-align: center; }
.paper-table-title { font-size: 12px; font-weight: bold; margin-bottom: 2px; text-align: left; break-after: avoid; page-break-after: avoid; color: #000000; }
.paper-figure { margin: 8px auto; text-align: center; break-inside: avoid; page-break-inside: avoid; }
.paper-figure img { max-width: 100%; border: 0.5pt solid #999999; display: block; margin: auto; }
.paper-figure-caption { font-size: 12px; margin-top: 3px; color: #000000; font-weight: normal; }
.paper-references { font-size: 12px; line-height: 1.22; margin: 4px 0 0; padding-left: 18px; }
.paper-references li { margin-bottom: 3px; }
@media print {
  .paper-body { column-count: 2; }
}
@media screen and (max-width: 768px) {
  .paper-body { column-count: 1; }
}
"""
    # Replace previous paper CSS if exists
    if "/* ========================================================\n   Research Paper" in content:
        content = re.sub(
            r'/\* ========================================================\s*Research Paper.*?\*/.*?(?=\s*</style>)',
            academic_css.strip(),
            content,
            flags=re.DOTALL
        )
    else:
        content = content.replace("</style>", academic_css + "\n</style>")

    # 2. Build Authentic Research Paper HTML
    paper_html = """
<section class="paper-divider" id="research-paper">
  <h1>บทความวิจัย</h1>
</section>

<section class="paper-container">
  <div class="paper-header">
    <div class="paper-title-th">ระบบให้คะแนนข้อสอบอัตนัยอัตโนมัติด้วย LLM</div>
    <div class="paper-title-en">LLM-AutoScore System</div>
    <div class="paper-authors">ธีระวิสิฐ แจ้งภูเขียว, คฑาวุธ พุ่มจันทร์, ฉัตรเกล้า เจริญผล</div>
    <div class="paper-affiliation">สาขาวิชาวิทยาการคอมพิวเตอร์ คณะวิทยาการสารสนเทศ มหาวิทยาลัยมหาสารคาม</div>
    <div class="paper-emails">66011212264@msu.ac.th, 66011212155@msu.ac.th, chatklaw.c@msu.ac.th</div>
  </div>

  <div class="paper-body">
    <h2>บทคัดย่อ</h2>
    <p>การวัดและประเมินผลการเรียนรู้ด้วยข้อสอบอัตนัย (Subjective Assessment) เปิดโอกาสให้ผู้เรียนได้แสดงกระบวนการคิดวิเคราะห์อย่างลึกซึ้ง แต่เป็นภาระงานที่ใช้เวลาและความละเอียดสูงของผู้สอน โครงงานนี้จึงมีวัตถุประสงค์เพื่อพัฒนาระบบตรวจข้อสอบอัตนัยอัตโนมัติที่รองรับทั้งข้อความบรรยายและภาพถ่ายกระดาษคำตอบลายมือเขียน พร้อมให้คะแนนและข้อเสนอแนะป้อนกลับ (Feedback) ทันทีบนเว็บแอปพลิเคชัน โดยประยุกต์ใช้เทคโนโลยีโมเดลภาษาขนาดใหญ่แบบพหุรูปแบบ (Multimodal Large Language Models: MLLMs) ด้วย Google Gemini API พัฒนาส่วนหน้าด้วย React (Vite) ส่วนหลังบ้านด้วย Python FastAPI เชื่อมต่อฐานข้อมูล TiDB Cloud จัดเก็บรูปภาพบน Cloudinary และแจ้งเตือนสถานะแบบเรียลไทม์ด้วย Node.js Socket.io การทดสอบระบบแบ่งออกเป็น 2 ส่วน ได้แก่ (1) การทดสอบการทำงานของระบบ 19 หัวข้อ พบว่าระบบทำงานถูกต้องครบถ้วนตามขอบเขตคิดเป็นร้อยละ 100.00 และ (2) การประเมินประสิทธิภาพการให้คะแนนด้วย AI จากชุดข้อมูลคำตอบจริง 204 รายการ (34 คน × 6 ข้อ ในรายวิชาโครงสร้างข้อมูล แบ่งเป็นคำตอบข้อความ 102 รายการ และคำตอบภาพลายมือ 102 รายการ) ผลการทดลองพบว่าคะแนนตรงกับผู้สอน 160 รายการ คิดเป็นร้อยละ 78.43 มีค่าความคลาดเคลื่อนเฉลี่ยสัมบูรณ์ (MAE) 0.1311 คะแนน และค่าสัมประสิทธิ์แคปปาแบบถ่วงน้ำหนักกำลังสอง (QWK) 0.8546 โดยกลุ่มคำตอบภาพโครงสร้างมีความตรงกันสมบูรณ์ร้อยละ 100.00 ทั้ง 102 รายการ และระบบตรวจจับกรณีที่ควรทบทวน (Review Flags) ได้ครอบคลุม ช่วยสนับสนุนการตรวจและลดภาระงานของผู้สอนได้อย่างมีประสิทธิภาพ</p>
    <p style="text-indent:0;margin-top:4px;"><strong>คำสำคัญ:</strong> LLMs, Auto Exam, Multimodal</p>

    <h2>1. บทนำ</h2>
    <p>การวัดและประเมินผลการเรียนรู้ที่มีประสิทธิภาพสูงสุดวิธีหนึ่งคือการสอบรูปแบบอัตนัย (Subjective Assessment) เนื่องจากเปิดโอกาสให้ผู้เรียนได้แสดงกระบวนการคิดวิเคราะห์และสังเคราะห์องค์ความรู้ผ่านการเขียนบรรยาย แต่ข้อจำกัดสำคัญในระบบการศึกษาปัจจุบันคือภาระงานของผู้สอนในการตรวจให้คะแนนที่มีปริมาณมากและต้องใช้ความละเอียดรอบคอบ ซึ่งมักนำไปสู่ปัญหาความล่าช้าในการประกาศผลคะแนน ความเหนื่อยล้าที่อาจก่อให้เกิดความคลาดเคลื่อน (Human Error) รวมถึงการขาดความสม่ำเสมอของมาตรฐานการให้คะแนน ส่งผลให้ผู้เรียนไม่ได้รับผลป้อนกลับ (Feedback) เพื่อนำไปปรับปรุงการเรียนรู้ได้ทันท่วงที</p>
    <p>จากปัญหาดังกล่าว ผู้จัดทำจึงมีแนวคิดพัฒนาระบบตรวจข้อสอบอัตนัยอัตโนมัติที่รองรับการอ่านลายมือเขียนและสามารถประเมินผลคะแนนพร้อมให้ข้อเสนอแนะได้ทันที โดยประยุกต์ใช้เทคโนโลยี Multimodal Large Language Models (MLLMs) บนเว็บแอปพลิเคชัน</p>
    <p>ขอบเขตของโครงงานครอบคลุมผู้ใช้งาน 2 กลุ่มหลัก ได้แก่ (1) ผู้เรียน สามารถสมัครสมาชิก เข้าสู่ระบบ ทำข้อสอบทั้งรูปแบบข้อความและแนบภาพถ่ายลายมือ ตรวจสอบสถานะการส่งคำตอบ และดูคะแนนพร้อมข้อเสนอแนะหลังจากผู้สอนอนุมัติผล และ (2) ผู้สอน สามารถจัดการห้องเรียน เพิ่มและแก้ไขโจทย์ข้อสอบ กำหนดธงคำตอบและรูบริคเกณฑ์การให้คะแนน ตรวจสอบความถูกต้องของคะแนนที่ AI ประเมิน แก้ไขคะแนน และอนุมัติผล โดยระบบรองรับการตรวจข้อสอบในรายวิชาโครงสร้างข้อมูล (Data Structures) ที่มีรูปแบบคำตอบทั้งข้อความและภาพวาดลายมือเชิงโครงสร้าง</p>

    <h2>2. ทฤษฎีและระบบงานที่เกี่ยวข้อง</h2>
    <h3>2.1 ทฤษฎีที่เกี่ยวข้อง</h3>
    <p><strong>1) การวัดและประเมินผลแบบอัตนัย:</strong> เน้นการวัดทักษะพุทธิพิสัยขั้นสูง โดยใช้เกณฑ์รูบริค (Rubrics) ช่วยควบคุมความเที่ยงตรงและความคงเส้นคงวาในการให้คะแนน</p>
    <p><strong>2) โมเดลภาษาขนาดใหญ่แบบพหุรูปแบบ (Multimodal LLMs):</strong> สถาปัตยกรรมแบบจำลอง เช่น Google Gemini ที่ได้รับการฝึกฝนให้สามารถประมวลผลและเข้าใจความสัมพันธ์ระหว่างข้อความและรูปภาพลายมือได้พร้อมกัน</p>
    <p><strong>3) สแต็กเทคโนโลยีการพัฒนาเว็บแอปพลิเคชัน:</strong> ส่วนหน้า (Frontend) พัฒนาด้วย React และ Vite ร่วมกับ TailwindCSS สำหรับจัดทำ User Interface ที่ตอบสนองการใช้งาน, ส่วนหลังบ้าน (Backend) ใช้ Python และ FastAPI ในการสร้าง RESTful API ประมวลผลตรรกะและส่งคำขอไปยังโมเดล AI, จัดเก็บข้อมูลในฐานข้อมูลเชิงสัมพันธ์ TiDB Cloud (MySQL-Compatible Distributed Database), จัดเก็บไฟล์รูปภาพกระดาษคำตอบบน Cloudinary และใช้ Node.js ร่วมกับ Socket.io สำหรับระบบแจ้งเตือนแบบเรียลไทม์</p>
    <h3>2.2 ระบบงานที่เกี่ยวข้อง</h3>
    <p>จากการศึกษาระบบงานที่เกี่ยวข้อง ได้แก่ Google Classroom ซึ่งโดดเด่นด้านการจัดการชั้นเรียนแต่ขาดระบบตรวจอัตนัยอัตโนมัติ, Gradescope ซึ่งรองรับการตรวจข้อสอบและจัดการรูบริคแต่จำกัดเฉพาะคำตอบแบบสั้นหรือต้องอาศัยผู้สอนตรวจทานเป็นหลัก, และ Microsoft Lens ที่ช่วยแปลงภาพถ่ายเอกสารแต่ไม่สามารถให้คะแนนเชิงวิชาการได้ ผู้จัดทำจึงนำจุดเด่นของแต่ละระบบมาบูรณาการเป็นระบบตรวจข้อสอบอัตนัยที่สมบูรณ์</p>

    <h2>3. ขั้นตอนการดำเนินงาน</h2>
    <h3>3.1 กรอบดำเนินงาน</h3>
    <p>การดำเนินงานแบ่งออกเป็นขั้นตอนการออกแบบและพัฒนาส่วนหน้าเว็บแอปพลิเคชันด้วย React (Vite), ส่วนหลังบ้านด้วย Python FastAPI, การยืนยันตัวตนด้วย Google Firebase Authentication, การเชื่อมต่อ Google Gemini API สำหรับวิเคราะห์คำตอบและให้คะแนน, การจัดการฐานข้อมูลหลัก TiDB Cloud, การจัดเก็บภาพบน Cloudinary, และการแจ้งเตือนสถานะแบบเรียลไทม์ด้วย Node.js Socket.io ดังแสดงในภาพประกอบที่ 1</p>

    <div class="paper-figure">
      <img src="screenshots/fig3_1_workflow.png" alt="ขั้นตอนการทำงานของเว็ปแอพ">
      <div class="paper-figure-caption">ภาพประกอบที่ 1 ขั้นตอนการทำงานของเว็ปแอพ</div>
    </div>

    <h3>3.2 การออกแบบระบบ</h3>
    <p>การไหลของข้อมูลในระบบแสดงผ่านแผนภาพบริบท (Context Diagram) ประกอบด้วยผู้ใช้ทั่วไป ผู้เรียน ผู้สอน เชื่อมต่อกับระบบตรวจข้อสอบอัตนัยด้วย LLM และบริการภายนอก ได้แก่ Gemini API, Cloudinary API, Firebase Auth และบริการส่งอีเมล ดังแสดงในภาพประกอบที่ 2</p>

    <div class="paper-figure">
      <img src="screenshots/fig3_2_context_diagram.png" alt="แผนภาพบริบท (Context Diagram)">
      <div class="paper-figure-caption">ภาพประกอบที่ 2 แผนภาพบริบท (Context Diagram)</div>
    </div>

    <h2>4. การทดสอบระบบ</h2>
    <h3>4.1 การทดสอบการทำงานของระบบ (Functional Testing)</h3>
    <p>การทดสอบฟังก์ชันการทำงานของระบบดำเนินการผ่านการทดสอบตามกรณีทดสอบ 19 หัวข้อ ครอบคลุมการสมัครสมาชิก (4.3.1), ลืมรหัสผ่าน (4.3.2), ตั้งรหัสผ่านใหม่และยืนยันอีเมล (4.3.3), เข้าสู่ระบบ (4.3.4), เข้าสู่ระบบด้วย Google (4.3.5), แก้ไขโปรไฟล์ (4.3.6), จัดการห้องเรียน (4.3.7), เข้าร่วมและออกจากห้องเรียน (4.3.8), ประกาศข่าวสาร (4.3.9), เพิ่มและแก้ไขข้อสอบ (4.3.10), สร้างเกณฑ์ให้คะแนน (4.3.11), ทำข้อสอบและส่งคำตอบ (4.3.12), ติดตามการส่งข้อสอบ (4.3.13), ประเมินคำตอบด้วย LLM (4.3.14), ตรวจสอบแก้ไขและอนุมัติคะแนน (4.3.15), ดูสถานะการส่งคำตอบ (4.3.16), ดูคะแนนและข้อเสนอแนะ (4.3.17), รายงานสถิติและส่งออก (4.3.18), และการแจ้งเตือนเรียลไทม์ (4.3.19) ผลการทดสอบพบว่าระบบผ่านการทดสอบครบทุกหัวข้อ คิดเป็นร้อยละ 100.00</p>

    <h3>4.2 การประเมินประสิทธิภาพการให้คะแนนด้วย AI</h3>
    <p>การประเมินประสิทธิภาพดำเนินการบนชุดข้อมูลกระดาษคำตอบจริงจำนวน 204 รายการ จากนิสิต 34 คน ใน 6 ข้อสอบรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี โดยเปรียบเทียบคะแนนที่แบบจำลองประเมินกับคะแนนอ้างอิงของผู้สอน ผลการประเมินจำแนกรายข้อแสดงดังตารางที่ 1</p>

    <div class="paper-table-title">ตารางที่ 1 ผลการประเมินประสิทธิภาพการให้คะแนนจำแนกรายข้อ</div>
    <table>
      <thead>
        <tr>
          <th>ข้อ</th>
          <th>รูปแบบคำตอบ</th>
          <th>คะแนนเต็ม</th>
          <th>คะแนนตรงกัน</th>
          <th>Exact Match (%)</th>
          <th>MAE</th>
          <th>NMAE</th>
          <th>QWK</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align:center;">1</td>
          <td style="text-align:center;">ข้อความ</td>
          <td style="text-align:center;">2</td>
          <td style="text-align:center;">27/34</td>
          <td style="text-align:center;">79.41</td>
          <td style="text-align:center;">0.2353</td>
          <td style="text-align:center;">0.1176</td>
          <td style="text-align:center;">0.6288</td>
        </tr>
        <tr>
          <td style="text-align:center;">2</td>
          <td style="text-align:center;">ข้อความ</td>
          <td style="text-align:center;">2</td>
          <td style="text-align:center;">19/34</td>
          <td style="text-align:center;">55.88</td>
          <td style="text-align:center;">0.3088</td>
          <td style="text-align:center;">0.1544</td>
          <td style="text-align:center;">0.5783</td>
        </tr>
        <tr>
          <td style="text-align:center;">3</td>
          <td style="text-align:center;">ข้อความ</td>
          <td style="text-align:center;">1</td>
          <td style="text-align:center;">12/34</td>
          <td style="text-align:center;">35.29</td>
          <td style="text-align:center;">0.2426</td>
          <td style="text-align:center;">0.2426</td>
          <td style="text-align:center;">0.5330</td>
        </tr>
        <tr>
          <td style="text-align:center;">4</td>
          <td style="text-align:center;">ภาพ</td>
          <td style="text-align:center;">1</td>
          <td style="text-align:center;">34/34</td>
          <td style="text-align:center;">100.00</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">1.0000</td>
        </tr>
        <tr>
          <td style="text-align:center;">5</td>
          <td style="text-align:center;">ภาพ</td>
          <td style="text-align:center;">1</td>
          <td style="text-align:center;">34/34</td>
          <td style="text-align:center;">100.00</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">1.0000</td>
        </tr>
        <tr>
          <td style="text-align:center;">6</td>
          <td style="text-align:center;">ภาพ</td>
          <td style="text-align:center;">1</td>
          <td style="text-align:center;">34/34</td>
          <td style="text-align:center;">100.00</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">1.0000</td>
        </tr>
      </tbody>
    </table>

    <p>จากตารางที่ 1 ผลการประเมินภาพรวมทั้งระบบ (204 รายการ) พบว่าคะแนนตรงกับผู้สอน 160 รายการ คิดเป็นร้อยละ 78.43 มีค่า MAE เท่ากับ 0.1311 คะแนน และค่า QWK รวมหลังปรับเป็นสเกลร่วม 0–4 เท่ากับ 0.8546 โดยคำตอบแบบภาพในข้อที่ 4–6 มีคะแนนตรงกับผู้สอนครบทั้ง 102 รายการ (ร้อยละ 100.00) ส่วนคำตอบแบบข้อความในข้อที่ 1–3 ตรงกัน 58 จาก 102 รายการ (ร้อยละ 56.86)</p>
    <p>สำหรับการทดลองอ่านลายมือในภาพคำตอบข้อที่ 3 จำนวน 34 ภาพ แบบจำลองอ่านข้อความได้เพียงพอต่อการตรวจ 31 จาก 33 ภาพ (ตัดภาพกำกวม 1 ภาพ) คิดเป็นร้อยละ 93.94 และระบบแจ้งเตือนให้ผู้สอนทบทวน (Review Flags) เมื่อแบบจำลองมีความมั่นใจปานกลางหรือต่ำ โดยครอบคลุมกรณีที่ควรทบทวนครบทั้ง 3 ภาพ มีค่า Review Recall ร้อยละ 100.00</p>

    <h2>5. สรุปผลและข้อเสนอแนะ</h2>
    <h3>5.1 สรุปและอภิปรายผล</h3>
    <p>โครงงานนี้พัฒนาระบบตรวจข้อสอบอัตนัยด้วยแบบจำลองภาษาขนาดใหญ่ในรูปแบบเว็บแอปพลิเคชัน โดยใช้ Gemini 3.8 Flash เป็นแบบจำลองหลักในการประเมินคำตอบและสร้างข้อเสนอแนะร่วมกับเกณฑ์การให้คะแนน ผลการประเมินกับชุดข้อมูลคำตอบจริง 204 รายการ พบว่าคะแนนตรงกับผู้สอนร้อยละ 78.43 มีค่า MAE 0.1311 คะแนน และ QWK 0.8546 คำตอบแบบภาพมีความตรงกันสมบูรณ์ร้อยละ 100.00 ส่วนคำตอบแบบข้อความตรงกันร้อยละ 56.86 การทดสอบการทำงานของระบบ 19 หัวข้อผ่านการทดสอบทุกกรณี แสดงให้เห็นว่าระบบรองรับกระบวนการตรวจข้อสอบตามขอบเขตโครงงานและสามารถใช้ช่วยสนับสนุนผู้สอนได้อย่างมีประสิทธิภาพ โดยผู้สอนยังคงเป็นผู้อนุมัติผลขั้นสุดท้าย</p>

    <h3>5.2 ปัญหาและอุปสรรคในการดำเนินงาน</h3>
    <p>1) การเตรียมข้อมูลคำตอบต้องตรวจสอบการจับคู่ภาพกับข้อความ และลบคะแนนหรือรอยตรวจของผู้สอนออกจากภาพโดยรักษาเนื้อหาเดิม เพื่อให้ข้อมูลนำเข้าตรงกับคำตอบของผู้เรียนและไม่เปิดเผยคะแนนอ้างอิงแก่แบบจำลอง</p>
    <p>2) คำตอบแบบข้อความมีระดับรายละเอียดต่างกัน โดยเฉพาะคำตอบสั้นและคำตอบที่ถูกบางส่วน ทำให้การพิจารณาความครบถ้วนและการให้คะแนนตามเกณฑ์แตกต่างจากผู้สอนได้</p>
    <p>3) ลายมือจาง ตัวอักษรเขียนติดกัน และข้อความลบหรือเขียนทับ ส่งผลต่อความชัดเจนในการถอดข้อความในบางคำตอบ</p>

    <h3>5.3 ข้อเสนอแนะ</h3>
    <p>1) ควรเพิ่มจำนวนและความหลากหลายของโจทย์ คำตอบ และลายมือ รวมถึงข้อมูลจากรายวิชาอื่น เพื่อประเมินการทำงานในสถานการณ์ที่กว้างขึ้น</p>
    <p>2) จัดทำเกณฑ์และตัวอย่างคำตอบแต่ละระดับคะแนนร่วมกับผู้สอน โดยกำหนดเงื่อนไขการให้คะแนนบางส่วนและการพิจารณาคำตอบที่มีเพียงคำสำคัญให้ชัดเจน</p>
    <p>3) ประเมินกลไกแจ้งทบทวนด้วยภาพเพิ่มเติม ทั้งกรณีที่ระบบไม่แจ้งเตือนและกรณีที่แจ้งเตือนเกินจำเป็น ควบคู่กับเวลาที่ผู้สอนใช้ตรวจทาน</p>
    <p>4) ทดสอบความคงที่ของคะแนนจากการประเมินซ้ำ และทดลองใช้งานในกระบวนการตรวจจริงเพื่อเก็บข้อมูลระยะเวลา ต้นทุน API และความพึงพอใจของผู้ใช้</p>

    <h2>6. เอกสารอ้างอิง</h2>
    <ol class="paper-references">
      <li>N. E. Gronlund and R. L. Linn, <i>Measurement and evaluation in teaching</i>, 6th ed. New York: Macmillan, 1990.</li>
      <li>D. R. Sadler, "Formative assessment and the design of instructional systems," <i>Instructional Science</i>, vol. 18, no. 2, pp. 119–144, 1989.</li>
      <li>OpenAI, "GPT-4 Technical Report," <i>arXiv preprint arXiv:2303.08774</i>, 2023.</li>
      <li>Gemini Team, Google, "Gemini: A Family of Highly Capable Multimodal Models," <i>Google DeepMind Technical Report</i>, 2023. [Online]. Available: https://arxiv.org/abs/2312.11805</li>
      <li>Meta Open Source, "React – The library for web and native user interfaces," [Online]. Available: https://react.dev/</li>
      <li>S. Ramírez, "FastAPI," [Online]. Available: https://fastapi.tiangolo.com/</li>
      <li>Oracle, "MySQL 8.0 Reference Manual: The InnoDB Storage Engine," [Online]. Available: https://dev.mysql.com/doc/refman/8.0/en/</li>
      <li>Google for Education, "Google Classroom," [Online]. Available: https://edu.google.com/workspace-for-education/classroom/</li>
      <li>A. Singh, S. Karayev, D. Gutman, and P. Abbeel, "Gradescope: A System for Fast, Fair, and Flexible Grading," in <i>Proc. Fourth ACM Conf. Learning @ Scale</i>, 2017, pp. 177–180.</li>
      <li>Microsoft, "Microsoft 365 (Office) app for Android and iOS," [Online]. Available: https://www.microsoft.com/microsoft-365/mobile</li>
      <li>P. Liu, W. Yuan, J. Fu, Z. Jiang, H. Hayashi, and G. Neubig, "Pre-train, prompt, and predict: A systematic survey of prompting methods in natural language processing," <i>ACM Computing Surveys</i>, 2023.</li>
      <li>A. Mizumoto and M. Eguchi, "Exploring the potential of using ChatGPT in automated essay scoring for L2 writing," <i>New Directions in Technology for Writing Instruction</i>, 2023.</li>
      <li>Gemini Team, Google, "Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context," <i>arXiv preprint arXiv:2403.05530</i>, 2024.</li>
    </ol>
  </div>
</section>
"""

    # 3. Replace research-paper in content
    pattern = r'<section class="paper-divider" id="research-paper">.*?</section>\s*<section class="paper-container">.*?</section>'
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, paper_html.strip(), content, flags=re.DOTALL)
        print("Updated existing research paper section!")
    else:
        target_pos = content.rfind("</main>")
        if target_pos != -1:
            content = content[:target_pos] + paper_html + "\n" + content[target_pos:]
            print("Appended research paper before </main>")
        else:
            print("Error: </main> not found")
            return

    # 4. Save to docs_and_tests/chapter4_testcases.html
    HTML_FILE.write_text(content, encoding="utf-8")
    print(f"Saved: {HTML_FILE}")

    # 5. Sync to public directories
    public_html = ROOT / "public" / "chapter4_testcases.html"
    shutil.copy2(HTML_FILE, public_html)
    print(f"Synced: {public_html}")

    client_public_html = ROOT / "client" / "public" / "chapter4_testcases.html"
    shutil.copy2(HTML_FILE, client_public_html)
    print(f"Synced: {client_public_html}")

if __name__ == "__main__":
    update_research_paper()
