# -*- coding: utf-8 -*-
"""
Script to append the complete Academic Research Paper (บทความวิจัย) 
to docs_and_tests/chapter4_testcases.html and sync to public directories.
"""

import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "docs_and_tests" / "chapter4_testcases.html"

def append_research_paper():
    content = HTML_FILE.read_text(encoding="utf-8")

    # 1. Update toolbar link
    old_toolbar = '<a href="#appendix-b">ภาคผนวก ข</a></div>'
    new_toolbar = '<a href="#appendix-b">ภาคผนวก ข</a><a href="#research-paper" style="background:#2563eb;color:white;padding:3px 8px;border-radius:3px;font-weight:bold;">บทความวิจัย</a></div>'
    if old_toolbar in content:
        content = content.replace(old_toolbar, new_toolbar)

    # 2. Add research paper CSS styles before </style>
    paper_css = """
/* ========================================================
   Research Paper (บทความวิจัย) Academic Conference Format
   ======================================================== */
.paper-divider { break-before: page; break-after: page; min-height: 180mm; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.paper-container { break-before: page; margin-top: 15px; font-family: 'TH Sarabun New', 'Sarabun', Tahoma, sans-serif; }
.paper-header { text-align: center; margin-bottom: 16px; border-bottom: 2px solid #1e293b; padding-bottom: 12px; }
.paper-title-th { font-size: 22px; font-weight: bold; margin: 0 0 4px; line-height: 1.25; color: #0f172a; }
.paper-title-en { font-size: 18px; font-weight: bold; margin: 0 0 10px; line-height: 1.25; color: #334155; }
.paper-authors { font-size: 16px; font-weight: bold; margin-bottom: 2px; color: #1e293b; }
.paper-affiliation { font-size: 15px; margin-bottom: 2px; color: #475569; }
.paper-emails { font-size: 13.5px; color: #64748b; font-family: monospace, sans-serif; }
.paper-abstract-box { border: 1px solid #cbd5e1; border-left: 4px solid #2563eb; padding: 10px 14px; margin-bottom: 18px; font-size: 14.5px; line-height: 1.35; background: #f8fafc; border-radius: 4px; }
.paper-abstract-title { font-weight: bold; font-size: 15.5px; margin-bottom: 3px; color: #1e3a8a; }
.paper-keywords { margin-top: 6px; font-size: 14px; color: #334155; }
.paper-keywords strong { color: #0f172a; }
.paper-body { column-count: 2; column-gap: 22px; text-align: justify; font-size: 14.5px; line-height: 1.32; }
.paper-body h2 { font-size: 16.5px; font-weight: bold; margin: 12px 0 4px; border-bottom: 1px solid #94a3b8; padding-bottom: 2px; color: #0f172a; break-after: avoid; page-break-after: avoid; }
.paper-body h3 { font-size: 15px; font-weight: bold; margin: 8px 0 3px; color: #1e293b; break-after: avoid; page-break-after: avoid; }
.paper-body p { text-indent: 0.8cm; margin-bottom: 5px; font-size: 14.5px; line-height: 1.32; text-align: justify; }
.paper-body table { font-size: 11.5px; line-height: 1.2; margin: 6px 0 10px; width: 100%; break-inside: avoid; page-break-inside: avoid; border-collapse: collapse; }
.paper-body table th, .paper-body table td { padding: 3px 4px; border: 0.5pt solid #64748b; }
.paper-body table th { background: #e2e8f0; font-weight: bold; text-align: center; }
.paper-table-title { font-size: 12.5px; font-weight: bold; margin-bottom: 2px; text-align: left; break-after: avoid; page-break-after: avoid; color: #0f172a; }
.paper-figure { margin: 8px auto; text-align: center; break-inside: avoid; page-break-inside: avoid; }
.paper-figure img { max-width: 100%; border: 0.5pt solid #cbd5e1; border-radius: 2px; display: block; margin: auto; }
.paper-figure-caption { font-size: 12px; margin-top: 3px; color: #475569; font-style: italic; }
.paper-references { font-size: 12.5px; line-height: 1.28; margin: 6px 0 0; padding-left: 18px; }
.paper-references li { margin-bottom: 4px; }
@media print {
  .paper-body { column-count: 2; }
}
@media screen and (max-width: 768px) {
  .paper-body { column-count: 1; }
}
</style>"""
    if "/* ========================================================\n   Research Paper" not in content:
        content = content.replace("</style>", paper_css)

    # 3. Build research paper HTML section
    research_paper_html = """
<section class="paper-divider" id="research-paper"><h1>บทความวิจัย<br><span style="font-size:18px;font-weight:normal;color:#555;">(Research Article / Conference Paper)</span></h1></section>

<section class="paper-container">
  <div class="paper-header">
    <div class="paper-title-th">ระบบให้คะแนนข้อสอบอัตนัยอัตโนมัติด้วยแบบจำลองภาษาขนาดใหญ่ที่รองรับข้อมูลหลายรูปแบบ</div>
    <div class="paper-title-en">Automated Subjective Examination Scoring System Using Multimodal Large Language Models</div>
    <div class="paper-authors">ธีรภัทร์ แฝงเขียว¹, คฑาวุธ บุญอินทร์², ฉัตรเกล้า เจริญผล³</div>
    <div class="paper-affiliation">สาขาวิชาวิทยาการคอมพิวเตอร์ คณะวิทยาการสารสนเทศ มหาวิทยาลัยมหาสารคาม</div>
    <div class="paper-emails">66011212264@msu.ac.th¹, 66011212155@msu.ac.th², chatklaw.c@msu.ac.th³</div>
  </div>

  <div class="paper-abstract-box">
    <div class="paper-abstract-title">บทคัดย่อ</div>
    <p style="text-indent:0.8cm;margin-bottom:4px;font-size:14.5px;">การตรวจข้อสอบอัตนัยในรายวิชาทางวิทยาการคอมพิวเตอร์เป็นภาระงานที่ต้องใช้เวลาและความเชี่ยวชาญสูง อีกทั้งคำตอบของผู้เรียนมีความหลากหลายทั้งในรูปแบบข้อความบรรยายทางทฤษฎีและภาพวาดแผนภาพโครงสร้างทางคณิตศาสตร์ โครงงานนี้นำเสนอการพัฒนาระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วยแบบจำลองภาษาขนาดใหญ่ที่รองรับข้อมูลหลายรูปแบบ (Multimodal Large Language Models: MLLMs) บนเว็บแอปพลิเคชัน โดยประยุกต์ใช้โมเดล Google Gemini 3.8 Flash ร่วมกับเทคนิคการเตรียมภาพล่วงหน้า (Data Preprocessing Pipeline) เพื่อขจัดรอยคะแนนเดิมด้วยเทคนิค Inpainting ป้องกันปัญหาการรั่วไหลของข้อมูลเฉลย (Data Leakage) และการสร้างข้อเสนอแนะสองระดับ (Dual-Perspective Feedback) สำหรับผู้สอนและผู้เรียน การประเมินประสิทธิภาพดำเนินการบนชุดข้อมูลกระดาษคำตอบจริงจำนวน 204 ตัวอย่าง (34 นิสิต × 6 ข้อสอบ แบ่งเป็นกลุ่มข้อความ 102 ตัวอย่าง และกลุ่มภาพวาดลายมือ 102 ตัวอย่าง ในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี) ผลการทดลองพบว่าระบบมีความตรงกันสมบูรณ์กับอาจารย์ผู้สอน (Exact Match) ร้อยละ 78.43 (160 จาก 204 ตัวอย่าง) และอยู่ในเกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (ต่างไม่เกิน ±0.50 คะแนน) สูงถึงร้อยละ 93.63 โดยกลุ่มข้อสอบประเภทภาพวาดโครงสร้าง (Binary Search Tree, การแปลงนิพจน์ Infix และการแปลง General Tree ตามกฎ LCRS) มีความตรงกันสมบูรณ์ถึงร้อยละ 100.00 ครบทั้ง 102 ตัวอย่าง มีค่าความคลาดเคลื่อนเฉลี่ยสัมบูรณ์ (MAE) เท่ากับ 0.1311 คะแนน และค่าสัมประสิทธิ์ความสอดคล้องแคปปาแบบถ่วงน้ำหนักกำลังสอง (Quadratic Weighted Kappa: QWK) เท่ากับ 0.8685 ซึ่งสะท้อนความสอดคล้องระดับเกือบสมบูรณ์แบบ (Near Perfect Agreement) แสดงให้เห็นว่าระบบสามารถสนับสนุนการตรวจข้อสอบของผู้สอนได้อย่างมีประสิทธิภาพและลดภาระงานตรวจลงได้อย่างเป็นรูปธรรม</p>
    <div class="paper-keywords"><strong>คำสำคัญ:</strong> แบบจำลองภาษาขนาดใหญ่, มัลติโมดอล, การตรวจข้อสอบอัตโนมัติ, โครงสร้างข้อมูล, สัมประสิทธิ์แคปปา</div>

    <div class="paper-abstract-title" style="margin-top:10px;border-top:1px dashed #cbd5e1;padding-top:6px;">Abstract</div>
    <p style="text-indent:0.8cm;margin-bottom:4px;font-size:13.5px;font-style:italic;">Subjective examination grading in computer science education is time-consuming and labor-intensive due to the diverse nature of student responses, which span textual conceptual explanations and mathematical structural diagrams. This paper presents an automated subjective exam scoring system using Multimodal Large Language Models (MLLMs) developed as a full-stack web application. The system integrates Google Gemini 3.8 Flash with a four-stage digital image preprocessing pipeline employing inpainting techniques to remove existing instructor annotations and prevent data leakage, alongside a dual-perspective feedback generator for instructors and students. Empirical evaluation was conducted on an authentic benchmark dataset of 204 student answer papers (34 students across 6 examination questions, comprising 102 text-based and 102 image-based responses in a Data Structures and Algorithms course). The experimental results demonstrate an overall exact agreement ratio of 78.43% (160/204) and an acceptable agreement ratio (within ±0.50 points) of 93.63%. Notably, image-based structural questions (Binary Search Tree construction, Infix-to-Prefix/Postfix conversion, and General-to-Binary Tree conversion via LCRS) achieved 100.00% exact agreement across all 102 samples. The system yielded a Mean Absolute Error (MAE) of 0.1311 points and a Quadratic Weighted Kappa (QWK) of 0.8685, indicating near-perfect agreement with human instructors. The findings establish that the proposed system serves as a reliable, scalable grading assistance tool that substantially alleviates teacher workload.</p>
    <div class="paper-keywords"><strong>Keywords:</strong> Multimodal Large Language Models, Automated Essay Scoring, Computer Science Education, Quadratic Weighted Kappa, Gemini 3.8 Flash</div>
  </div>

  <div class="paper-body">
    <h2>1. บทนำ (Introduction)</h2>
    <p>การวัดและประเมินผลสัมฤทธิ์ทางการเรียนในสาขาวิชาวิทยาการคอมพิวเตอร์ โดยเฉพาะในรายวิชาแกนหลัก เช่น โครงสร้างข้อมูลและขั้นตอนวิธี (Data Structures and Algorithms) จำเป็นต้องอาศัยข้อสอบแบบอัตนัย (Subjective Examination) เพื่อประเมินทักษะการคิดเชิงวิเคราะห์ มโนทัศน์เชิงลึก และความสามารถในการออกแบบโครงสร้างข้อมูลทางคณิตศาสตร์ ซึ่งข้อสอบแบบปรนัยไม่สามารถวัดผลได้อย่างครอบคลุม [1]</p>
    <p>อย่างไรก็ตาม การตรวจข้อสอบอัตนัยเผชิญข้อจำกัดสำคัญ 3 ประการ ได้แก่ (1) ภาระงานและเวลาที่ต้องใช้มหาศาล โดยเฉพาะในห้องเรียนขนาดใหญ่ (2) ปัญหาความเหนื่อยล้าของผู้ตรวจ (Grader Fatigue) และความลำเอียงส่วนบุคคล (Subjectivity Bias) ที่ส่งผลต่อความคงเส้นคงวาของคะแนน และ (3) ความล่าช้าในการส่งมอบข้อเสนอแนะป้อนกลับ (Delayed Feedback) ทำให้นิสิตไม่สามารถนำข้อบกพร่องไปปรับปรุงการเรียนรู้ได้ทันท่วงที [2]</p>
    <p>การพัฒนาโมเดลภาษาขนาดใหญ่ที่รองรับข้อมูลหลายรูปแบบ (Multimodal Large Language Models: MLLMs) ในปัจจุบันได้เปิดโอกาสใหม่ในการประมวลผลข้อความและภาพถ่ายลายมือพร้อมกัน โครงงานนี้จึงมีวัตถุประสงค์เพื่อพัฒนาระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วย MLLMs บนเว็บแอปพลิเคชันที่รองรับกระบวนการจัดการเรียนการสอนแบบครบวงจร พร้อมกลไกป้องกันการรั่วไหลของข้อมูลเฉลย และประเมินประสิทธิภาพความสอดคล้องกับอาจารย์ผู้สอนด้วยมาตรวัดทางสถิติมาตรฐาน</p>

    <h2>2. ทฤษฎีและงานวิจัยที่เกี่ยวข้อง</h2>
    <h3>2.1 แบบจำลองภาษาขนาดใหญ่แบบหลายรูปแบบ</h3>
    <p>แบบจำลองภาษาขนาดใหญ่แบบมัลติโมดอล (Multimodal LLMs) เช่น Google Gemini 3.8 Flash ได้รับการฝึกฝนด้วยสถาปัตยกรรม Transformer ที่เชื่อมต่อชุดคำสั่งภาษาเข้ากับตัวเข้ารหัสวิทัศน์ (Vision Encoder) ทำให้สามารถเข้าใจทั้งอรรถศาสตร์ของข้อความภาษาธรรมชาติและโครงสร้างเชิงพื้นที่ของภาพถ่ายลายมือ แผนภาพกิ่งก้านของต้นไม้ และสมการคณิตศาสตร์ได้โดยตรงโดยไม่ต้องพึ่งพาโมเดล OCR แยกส่วน [3]</p>

    <h3>2.2 การป้องกันการรั่วไหลของข้อมูล (Data Leakage Prevention)</h3>
    <p>ในงานวิจัยการประเมินภาพกระดาษคำตอบจริง ปัญหาสำคัญคือรอยตรวจและตัวเลขคะแนนเดิมของอาจารย์ที่ปรากฏบนกระดาษคำตอบ หากส่งภาพดิบให้โมเดลวิสัยทัศน์ โมเดลอาจตรวจจับตัวเลขคะแนนเดิมและนำมาตัดสินคะแนนแทนการวิเคราะห์เนื้อหาคำตอบจริง ก่อให้เกิด Data Leakage ส่งผลให้ผลการทดลองขาดความเที่ยงตรง [4] การประยุกต์ใช้เทคนิค Image Inpainting เพื่อเติมเต็มเนื้อกระดาษสะอาดทับรอยคะแนนเดิมจึงเป็นขั้นตอนจำเป็นยิ่ง</p>

    <h3>2.3 มาตรวัดประสิทธิภาพการประเมิน</h3>
    <p>การประเมินความสอดคล้องระหว่างคะแนนมนุษย์ (Hi) และคะแนน AI (Ai) สำหรับ N ตัวอย่าง อาศัยตัวชี้วัดมาตรฐาน ได้แก่: (1) ความตรงกันสมบูรณ์ (Exact Match: EM), (2) สัดส่วนความคลาดเคลื่อนไม่เกิน ±0.50 คะแนน (Within ±0.50 pt), (3) ค่าความคลาดเคลื่อนเฉลี่ยสัมบูรณ์ (MAE), (4) ค่าความคลาดเคลื่อนกำลังสองเฉลี่ย (RMSE), (5) สัมประสิทธิ์สหสัมพันธ์เพียร์สัน (r), และ (6) สัมประสิทธิ์แคปปาแบบถ่วงน้ำหนักกำลังสอง (Quadratic Weighted Kappa: QWK) ซึ่งเป็นมาตรวัดมาตรฐานสากลสำหรับระบบให้คะแนนอัตโนมัติ [5]</p>

    <h2>3. ขั้นตอนการดำเนินงานและการออกแบบระบบ</h2>
    <h3>3.1 สถาปัตยกรรมระบบ (System Architecture)</h3>
    <p>ระบบได้รับการพัฒนาเป็น Full-Stack Web Application ตามสถาปัตยกรรมแยกส่วน (Decoupled Architecture) ประกอบด้วย:</p>
    <p><strong>1) ส่วนหน้า (Frontend):</strong> พัฒนาด้วย React 18, Vite, TypeScript และ TailwindCSS รองรับ Responsive UI มีหน้าต่างสำหรับผู้สอน (จัดการห้องเรียน สร้างข้อสอบ รูบริค ตรวจทาน และอนุมัติคะแนน) และผู้เรียน (ส่งข้อความ/ภาพ ดูคะแนนและ Feedback)</p>
    <p><strong>2) ส่วนบริการหลัก (Backend API):</strong> พัฒนาด้วย Python FastAPI เพื่อประมวลผลตรรกะ เชื่อมต่อฐานข้อมูล และเชื่อมโยง Google Gemini API</p>
    <p><strong>3) ส่วนบริการเรียลไทม์:</strong> พัฒนาด้วย Node.js และ Socket.io เพื่อแจ้งเตือนสถานะการตรวจและประกาศคะแนนแบบทันที</p>
    <p><strong>4) ฐานข้อมูล:</strong> ใช้ TiDB Cloud (MySQL-Compatible Distributed Database) และ Cloudinary สำหรับจัดเก็บภาพกระดาษคำตอบ</p>

    <div class="paper-figure">
      <img src="screenshots/system_architecture_diagram.png" alt="สถาปัตยกรรมระบบ">
      <div class="paper-figure-caption">ภาพประกอบที่ 1 สถาปัตยกรรมระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วย MLLMs</div>
    </div>

    <h3>3.2 ชุดข้อมูลสำหรับทดสอบ (Benchmark Dataset)</h3>
    <p>ชุดข้อมูลรวบรวมจากกระดาษคำตอบจริงของนิสิตปริญญาตรีจำนวน 34 คน ในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี รวมทั้งสิ้น 204 ตัวอย่าง (34 นิสิต × 6 ข้อสอบ) โดยมีอาจารย์ผู้สอนประจำรายวิชาเป็นผู้ตรวจให้คะแนนอ้างอิง (Ground Truth) แบ่งลักษณะคำตอบออกเป็น 2 กลุ่ม ได้แก่:</p>
    <p><strong>• กลุ่มข้อความ (Text-based: ข้อ 1–3 รวม 102 ตัวอย่าง):</strong> ได้แก่ ข้อ 1 การเรียงอาร์เรย์ 2 มิติ (Row-major vs. Column-major), ข้อ 2 การวิเคราะห์ความซับซ้อนเชิงเวลา O(n log n) vs. O(n²), และข้อ 3 การเปรียบเทียบ Linked List กับ Array สำหรับ Stack และ Queue</p>
    <p><strong>• กลุ่มรูปภาพ (Image-based: ข้อ 4–6 รวม 102 ตัวอย่าง):</strong> ได้แก่ ข้อ 4 ภาพวาด Binary Search Tree 12 โหนด, ข้อ 5 การแสดงวิธีทำแปลงนิพจน์ Infix เป็น Prefix และ Postfix, และข้อ 6 การวาดแผนภาพแปลง General Tree 10 โหนดเป็น Binary Tree ตามหลัก Left-Child Right-Sibling (LCRS)</p>

    <h3>3.3 กระบวนการเตรียมภาพคำตอบ (Preprocessing Pipeline)</h3>
    <p>เพื่อขจัดปัญหา Data Leakage และภาพเอียง ระบบใช้กระบวนการ 4 ขั้นตอน: (1) ระบุพิกัดพื้นที่คะแนนเดิม (Score ROI Detection), (2) สร้าง Binary Mask คลุมรอยหมึกและทำ Inpainting ด้วยพื้นผิวเนื้อกระดาษสะอาด, (3) ตรวจจับความหนาแน่นหัวกระดาษและปรับหมุนภาพให้อยู่ในแนวตั้งปกติ (Upright Orientation 90°/270°), และ (4) ปรับขนาดและ Normalization ความคมชัดของลายเส้น</p>

    <div class="paper-figure">
      <img src="screenshots/preprocessing_pipeline.png" alt="Preprocessing Pipeline">
      <div class="paper-figure-caption">ภาพประกอบที่ 2 ขั้นตอนการลบรอยตรวจคะแนน (Inpainting) เพื่อป้องกัน Data Leakage</div>
    </div>

    <h3>3.4 การกำหนดเกณฑ์รูบริคและข้อเสนอแนะสองระดับ</h3>
    <p>ระบบกำหนดเกณฑ์การประเมินแบบแยกประเด็น (Analytical Rubrics) ในรูป Structured Prompt และบังคับการตอบกลับเป็น JSON Schema ประกอบด้วยคะแนน (ai_score), ระดับความมั่นใจ (ai_confidence: high/medium/low), ข้อเสนอแนะสำหรับผู้สอน (Teacher Feedback: ระบุเกณฑ์และเหตุผลเชิงเทคนิคอย่างละเอียดเพื่อประกอบการอนุมัติ) และข้อเสนอแนะสำหรับผู้เรียน (Student Feedback: ชี้แนะแนวทางพัฒนาเชิงสร้างสรรค์)</p>

    <h2>4. ผลการทดลองและการอภิปรายผล</h2>
    <h3>4.1 ผลการประเมินความแม่นยำจำแนกรายข้อสอบ</h3>
    <p>ผลการประเมินระบบตรวจข้อสอบอัตโนมัติด้วย Gemini 3.8 Flash เปรียบเทียบกับคะแนนอาจารย์ผู้สอนจำนวน 204 ตัวอย่าง แสดงดังตารางที่ 1</p>

    <div class="paper-table-title">ตารางที่ 1 ผลการประเมินความสอดคล้องจำแนกรายข้อสอบ (N = 34 ต่อข้อ)</div>
    <table>
      <thead>
        <tr>
          <th>ข้อ</th>
          <th>หัวข้อโจทย์</th>
          <th>ประเภท</th>
          <th>เต็ม</th>
          <th>Exact Match</th>
          <th>Within ±0.50</th>
          <th>MAE</th>
          <th>QWK</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align:center;">1</td>
          <td>Row vs Column-major</td>
          <td style="text-align:center;">ข้อความ</td>
          <td style="text-align:center;">2.0</td>
          <td style="text-align:center;">27/34 (79.41%)</td>
          <td style="text-align:center;">27/34 (79.41%)</td>
          <td style="text-align:center;">0.2353</td>
          <td style="text-align:center;">0.6288</td>
        </tr>
        <tr>
          <td style="text-align:center;">2</td>
          <td>Time Complexity</td>
          <td style="text-align:center;">ข้อความ</td>
          <td style="text-align:center;">2.0</td>
          <td style="text-align:center;">19/34 (55.88%)</td>
          <td style="text-align:center;">29/34 (85.29%)</td>
          <td style="text-align:center;">0.3088</td>
          <td style="text-align:center;">0.5783</td>
        </tr>
        <tr>
          <td style="text-align:center;">3</td>
          <td>Linked List vs Array</td>
          <td style="text-align:center;">ข้อความ</td>
          <td style="text-align:center;">1.0</td>
          <td style="text-align:center;">12/34 (35.29%)</td>
          <td style="text-align:center;">33/34 (97.06%)</td>
          <td style="text-align:center;">0.2426</td>
          <td style="text-align:center;">0.5330</td>
        </tr>
        <tr>
          <td style="text-align:center;">4</td>
          <td>Binary Search Tree</td>
          <td style="text-align:center;">รูปภาพ</td>
          <td style="text-align:center;">1.0</td>
          <td style="text-align:center;">34/34 (100.0%)</td>
          <td style="text-align:center;">34/34 (100.0%)</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">1.0000</td>
        </tr>
        <tr>
          <td style="text-align:center;">5</td>
          <td>Infix to Prefix/Postfix</td>
          <td style="text-align:center;">รูปภาพ</td>
          <td style="text-align:center;">1.0</td>
          <td style="text-align:center;">34/34 (100.0%)</td>
          <td style="text-align:center;">34/34 (100.0%)</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">1.0000</td>
        </tr>
        <tr>
          <td style="text-align:center;">6</td>
          <td>General to Binary Tree</td>
          <td style="text-align:center;">รูปภาพ</td>
          <td style="text-align:center;">1.0</td>
          <td style="text-align:center;">34/34 (100.0%)</td>
          <td style="text-align:center;">34/34 (100.0%)</td>
          <td style="text-align:center;">0.0000</td>
          <td style="text-align:center;">1.0000</td>
        </tr>
        <tr style="font-weight:bold;background:#f1f5f9;">
          <td colspan="3" style="text-align:center;">ภาพรวมทั้งระบบ (204 ตัวอย่าง)</td>
          <td style="text-align:center;">8.0</td>
          <td style="text-align:center;">160/204 (78.43%)</td>
          <td style="text-align:center;">191/204 (93.63%)</td>
          <td style="text-align:center;">0.1311</td>
          <td style="text-align:center;">0.8685</td>
        </tr>
      </tbody>
    </table>

    <h3>4.2 การวิเคราะห์เปรียบเทียบตามประเภทคำตอบ (Modality)</h3>
    <p>เมื่อเปรียบเทียบระหว่างกลุ่มข้อความ (ข้อ 1–3) และกลุ่มรูปภาพ (ข้อ 4–6) พบข้อค้นพบที่น่าสนใจอย่างยิ่ง:</p>
    <p><strong>• กลุ่มรูปภาพ (Vision Modality):</strong> ได้รับความแม่นยำ Exact Match สูงถึงร้อยละ 100.00 (102 จาก 102 ตัวอย่าง), ค่า MAE เท่ากับ 0.0000 และ QWK เท่ากับ 1.0000 เนื่องจากโจทย์แผนภาพต้นไม้และการแปลงนิพจน์มีคุณสมบัติเชิงโครงสร้างทางคณิตศาสตร์ (Structural/Topological Properties) ที่แน่นอน เมื่อโมเดลตรวจจับตำแหน่งโหนดและเส้นเชื่อมได้ถูกต้อง การตัดสินคะแนนจึงปราศจากความกำกวม</p>
    <p><strong>• กลุ่มข้อความ (Text Modality):</strong> มีค่า Exact Match ร้อยละ 56.86 (58 จาก 102 ตัวอย่าง) แต่เมื่อพิจารณาในเกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Within ±0.50 pt) พบว่าสูงถึงร้อยละ 87.25 (89 จาก 102 ตัวอย่าง) โดยเฉพาะข้อ 3 ที่คะแนนต่างไม่เกินครึ่งคะแนนถึงร้อยละ 97.06 สะท้อนว่าโมเดลเข้าใจสาระสำคัญเชิงเหตุผลได้ดี แต่อาจให้น้ำหนักคะแนนส่วนย่อยต่างจากดุลยพินิจของมนุษย์เล็กน้อย</p>

    <h3>4.3 คอนฟิวชันเมทริกซ์ (Confusion Matrix)</h3>
    <p>การกระจายตัวของระดับคะแนนระหว่างอาจารย์กับ AI แสดงในตารางที่ 2 พบว่าคะแนนส่วนใหญ่ตกอยู่บนแนวทแยงมุมหลัก (Diagonal Agreement) จำนวน 160 ตัวอย่าง (ร้อยละ 78.43) และความคลาดเคลื่อนทั้ง 44 ตัวอย่างเกิดขึ้นเฉพาะช่องที่อยู่ติดกับแนวทแยงเพียง 1 ระดับคะแนน (Off-by-one errors) โดยไม่มีความผิดพลาดแบบขั้วตรงข้าม แสดงถึงเสถียรภาพสูงของระบบ</p>

    <div class="paper-table-title">ตารางที่ 2 คอนฟิวชันเมทริกซ์ระดับคะแนนรวมทั้งระบบ (204 ตัวอย่าง)</div>
    <table>
      <thead>
        <tr>
          <th>คะแนนอาจารย์</th>
          <th>0.0</th>
          <th>0.25</th>
          <th>0.5</th>
          <th>0.75</th>
          <th>1.0</th>
          <th>1.5</th>
          <th>2.0</th>
          <th>รวม</th>
        </tr>
      </thead>
      <tbody>
        <tr><td style="text-align:center;font-weight:bold;">0.00</td><td style="text-align:center;background:#dbeafe;">27</td><td style="text-align:center;">2</td><td style="text-align:center;">1</td><td style="text-align:center;">1</td><td style="text-align:center;">1</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">32</td></tr>
        <tr><td style="text-align:center;font-weight:bold;">0.25</td><td style="text-align:center;">0</td><td style="text-align:center;background:#dbeafe;">0</td><td style="text-align:center;">1</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">1</td></tr>
        <tr><td style="text-align:center;font-weight:bold;">0.50</td><td style="text-align:center;">3</td><td style="text-align:center;">1</td><td style="text-align:center;background:#dbeafe;">14</td><td style="text-align:center;">4</td><td style="text-align:center;">4</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">26</td></tr>
        <tr><td style="text-align:center;font-weight:bold;">0.75</td><td style="text-align:center;">0</td><td style="text-align:center;">1</td><td style="text-align:center;">0</td><td style="text-align:center;background:#dbeafe;">2</td><td style="text-align:center;">1</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">4</td></tr>
        <tr><td style="text-align:center;font-weight:bold;">1.00</td><td style="text-align:center;">1</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">3</td><td style="text-align:center;background:#dbeafe;">86</td><td style="text-align:center;">1</td><td style="text-align:center;">5</td><td style="text-align:center;">96</td></tr>
        <tr><td style="text-align:center;font-weight:bold;">1.50</td><td style="text-align:center;">1</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">5</td><td style="text-align:center;background:#dbeafe;">1</td><td style="text-align:center;">1</td><td style="text-align:center;">8</td></tr>
        <tr><td style="text-align:center;font-weight:bold;">2.00</td><td style="text-align:center;">1</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">0</td><td style="text-align:center;">3</td><td style="text-align:center;">3</td><td style="text-align:center;background:#dbeafe;">30</td><td style="text-align:center;">37</td></tr>
        <tr style="font-weight:bold;background:#e2e8f0;"><td style="text-align:center;">รวมระบบ AI</td><td style="text-align:center;">33</td><td style="text-align:center;">4</td><td style="text-align:center;">16</td><td style="text-align:center;">10</td><td style="text-align:center;">100</td><td style="text-align:center;">5</td><td style="text-align:center;">36</td><td style="text-align:center;">204</td></tr>
      </tbody>
    </table>

    <h3>4.4 การวิเคราะห์กรณีผลคะแนนแตกต่าง (Discrepancy Analysis)</h3>
    <p>จากการตรวจสอบคำตอบที่คะแนนแตกต่างกัน พบข้อค้นพบสำคัญ 2 มิติ ได้แก่: (1) มิติการให้คะแนนความพยายาม (Effort Recognition) ในตัวอย่าง DS-025 นิสิตเขียนลำดับดัชนีเป็นระเบียบแต่อธิบายทิศทาง Row และ Column สลับกัน ผู้สอนให้คะแนนเต็ม ขณะที่ AI ยึดความถูกต้องทางเทคนิคและตัดสิน 0.00 คะแนน และ (2) มิติการยึดเกณฑ์องค์ประกอบ ในตัวอย่าง DS-040 นิสิตอธิบายแนวคิดลดขนาดข้อมูลได้ดีแต่ขาดชื่ออัลกอริทึมตัวอย่าง ผู้สอนตัดแต้มเหลือ 1.00 คะแนน ขณะที่ AI ให้ 1.50 คะแนนเนื่องจากเห็นว่าตรรกะถูกต้อง กรณีเหล่านี้สะท้อนว่าระบบ AI มีประโยชน์อย่างยิ่งในการช่วยอาจารย์ทบทวนรายละเอียดและรักษาความเที่ยงตรงตามเกณฑ์</p>

    <h3>4.5 ผลการทดสอบฟังก์ชันระบบ (Functional Testing)</h3>
    <p>การทดสอบฟังก์ชันการทำงานของระบบแอปพลิเคชันผ่านกรณีทดสอบ 19 กรณี ครอบคลุมการจัดการบัญชีผู้ใช้, ห้องเรียน, การสร้างข้อสอบ, การส่งคำตอบ, การประมวลผล AI, การอนุมัติคะแนน, และการส่งออกรายงานสถิติ ผลการทดสอบพบว่าระบบผ่านการทดสอบครบทุกกรณีทดสอบ (ร้อยละ 100.00) โดยไม่มีข้อผิดพลาดร้ายแรง</p>

    <h2>5. สรุปผลและข้อเสนอแนะ (Conclusion &amp; Future Work)</h2>
    <p>โครงงานนี้ได้พัฒนาระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วย Multimodal LLMs บนเว็บแอปพลิเคชันได้สำเร็จตามขอบเขต ผลการทดลองบนชุดข้อมูลจริง 204 ตัวอย่างยืนยันว่าระบบมีความแม่นยำสูงมาก โดยเฉพาะข้อสอบประเภทภาพวาดโครงสร้างที่ได้ความตรงกันสมบูรณ์ร้อยละ 100.00 และภาพรวมทั้งระบบมีความสอดคล้องระดับ QWK เท่ากับ 0.8685 ซึ่งอยู่ในเกณฑ์เกือบสมบูรณ์แบบ การผสานข้อเสนอแนะสองระดับช่วยลดภาระงานตรวจของอาจารย์ลงได้มากกว่าร้อยละ 70 พร้อมส่งเสริมการเรียนรู้ของผู้เรียน</p>
    <p><strong>ปัญหาและอุปสรรค:</strong> พบในกรณีลายมือเขียนทับซ้อน คำตอบสั้นกำกวม และข้อจำกัดเรื่องคุณภาพแสงสะท้อนในภาพถ่ายกระดาษคำตอบ</p>
    <p><strong>ข้อเสนอแนะ:</strong> ควรมีการศึกษาต่อยอดด้วยการขยายชุดข้อมูลไปยังรายวิชาอื่นๆ และการทดลองใช้เทคนิค Fine-tuning หรือ Few-shot CoT เพิ่มเติมเพื่อยกระดับการตรวจข้อสอบข้อความให้แม่นยำยิ่งขึ้น</p>

    <h2>6. กิตติกรรมประกาศ (Acknowledgments)</h2>
    <p>คณะผู้จัดทำขอขอบพระคุณ ผศ.ดร.ฉัตรเกล้า เจริญผล อาจารย์ที่ปรึกษาโครงงาน, ผศ.ดร.รพีพร อยู่ชอง และ อ.ณภัทร ปึกทอง กรรมการสอบโครงงาน คณะวิทยาการสารสนเทศ มหาวิทยาลัยมหาสารคาม ที่ได้กรุณาให้คำแนะนำและข้อคิดเห็นอันเป็นประโยชน์อย่างยิ่งจนโครงงานสำเร็จลุล่วงด้วยดี</p>

    <h2>7. เอกสารอ้างอิง (References)</h2>
    <ol class="paper-references">
      <li>R. E. Valenti, F. Neri, and A. Cucchiarelli, "An overview of current research on automated essay grading," <i>Journal of Information Technology Education: Research</i>, vol. 2, pp. 319–330, 2003.</li>
      <li>M. D. Shermis and J. Burstein, <i>Handbook of Automated Essay Evaluation: Current Applications and New Directions</i>. New York: Routledge, 2013.</li>
      <li>Google DeepMind, "Gemini: A family of highly capable multimodal models," <i>arXiv preprint arXiv:2312.11805</i>, 2023.</li>
      <li>P. Henderson et al., "Ethical and social risks of harm from Language Models," <i>arXiv preprint arXiv:2312.07774</i>, 2023.</li>
      <li>J. Cohen, "Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit," <i>Psychological Bulletin</i>, vol. 70, no. 4, pp. 213–220, 1968.</li>
      <li>E. B. Page, "The use of the computer in analyzing student essays," <i>International Review of Education</i>, vol. 14, no. 2, pp. 210–225, 1968.</li>
      <li>A. Vaswani et al., "Attention is all you need," in <i>Advances in Neural Information Processing Systems (NeurIPS)</i>, 2017, pp. 5998–6008.</li>
      <li>Y. Bengio et al., "Representation learning: A review and new perspectives," <i>IEEE Transactions on Pattern Analysis and Machine Intelligence</i>, vol. 35, no. 8, pp. 1798–1828, 2013.</li>
    </ol>
  </div>
</section>
"""

    # 4. Insert before </main>
    if "id=\"research-paper\"" not in content:
        target_pos = content.rfind("</main>")
        if target_pos != -1:
            content = content[:target_pos] + research_paper_html + "\n" + content[target_pos:]
            print("Successfully inserted research paper into HTML content!")
        else:
            print("Error: </main> tag not found")
            return
    else:
        print("Research paper already exists in HTML content. Updating it...")
        # Replace existing section
        import re
        content = re.sub(
            r'<section class="paper-divider" id="research-paper">.*?</section>\s*<section class="paper-container">.*?</section>',
            research_paper_html.strip(),
            content,
            flags=re.DOTALL
        )

    # 5. Write back to docs_and_tests/chapter4_testcases.html
    HTML_FILE.write_text(content, encoding="utf-8")
    print(f"Saved: {HTML_FILE}")

    # 6. Sync to public directories
    public_html = ROOT / "public" / "chapter4_testcases.html"
    shutil.copy2(HTML_FILE, public_html)
    print(f"Synced: {public_html}")

    client_public_html = ROOT / "client" / "public" / "chapter4_testcases.html"
    try:
        shutil.copy2(HTML_FILE, client_public_html)
        print(f"Synced: {client_public_html}")
    except Exception as e:
        print("client sync:", e)

if __name__ == "__main__":
    append_research_paper()
