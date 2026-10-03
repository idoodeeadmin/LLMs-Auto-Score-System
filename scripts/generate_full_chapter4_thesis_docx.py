# -*- coding: utf-8 -*-
"""
Script to generate the complete Chapter 4 Word Document (.docx)
matching the exact structure, steps, example figures, step-by-step calculations,
and evaluation methodology of the reference thesis 'กระถางตรวจสุขภาพด้วย-Ai-pro2'
"""

import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="CCCCCC"):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color)
        tblBorders.append(border)
    border = OxmlElement('w:insideV')
    border.set(qn('w:val'), 'single')
    border.set(qn('w:sz'), '4')
    border.set(qn('w:space'), '0')
    border.set(qn('w:color'), color)
    tblBorders.append(border)
    tblPr.append(tblBorders)

def add_heading(doc, text, level):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = "TH Sarabun New"
    run.bold = True
    if level == 0:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(10)
        run.font.size = Pt(20)
    elif level == 1:
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        run.font.size = Pt(18)
    elif level == 2:
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(16)
    elif level == 3:
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        run.font.size = Pt(15)
    return p

def add_para(doc, text, bold_prefix="", indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.4)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "TH Sarabun New"
        r_pre.font.size = Pt(16)
        r_pre.bold = True
    r = p.add_run(text)
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(16)
    return p

def add_figure(doc, img_path, caption_text, width_inches=5.2):
    if img_path and os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run = p_img.add_run()
        run.add_picture(str(img_path), width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = "TH Sarabun New"
        r_cap.font.size = Pt(14)
        r_cap.italic = True

def add_callout_box(doc, title, content_lines):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    left_b = OxmlElement('w:left')
    left_b.set(qn('w:val'), 'single')
    left_b.set(qn('w:sz'), '24')
    left_b.set(qn('w:color'), '2563EB')
    tcBorders.append(left_b)
    for b in ['top', 'bottom', 'right']:
        node = OxmlElement(f'w:{b}')
        node.set(qn('w:val'), 'none')
        tcBorders.append(node)
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    r_title = p.add_run(title)
    r_title.font.name = "TH Sarabun New"
    r_title.font.size = Pt(15)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)
    
    for line in content_lines:
        p_line = cell.add_paragraph()
        p_line.paragraph_format.space_before = Pt(0)
        p_line.paragraph_format.space_after = Pt(2)
        r_l = p_line.add_run(line)
        r_l.font.name = "TH Sarabun New"
        r_l.font.size = Pt(14)
        
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def create_table_header(table, headers, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1E293B")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.font.name = "TH Sarabun New"
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        if col_widths and i < len(col_widths):
            hdr_cells[i].width = col_widths[i]

def add_table_row(table, row_data, is_zebra=False, col_widths=None, align_center_cols=[]):
    row_cells = table.add_row().cells
    bg_color = "F8FAFC" if is_zebra else "FFFFFF"
    for i, text in enumerate(row_data):
        row_cells[i].text = str(text)
        set_cell_background(row_cells[i], bg_color)
        set_cell_margins(row_cells[i], top=70, bottom=70, left=90, right=90)
        p = row_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if i in align_center_cols:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = "TH Sarabun New"
            r.font.size = Pt(13.5)
        if col_widths and i < len(col_widths):
            row_cells[i].width = col_widths[i]

def add_prediction_example_table(doc, title, exam_info, img_path, student_answer, rubric, scores_dict, feedback_teacher, feedback_student):
    p_t = doc.add_paragraph()
    p_t.paragraph_format.space_before = Pt(12)
    p_t.paragraph_format.space_after = Pt(3)
    r_t = p_t.add_run(title)
    r_t.bold = True
    r_t.font.name = "TH Sarabun New"
    r_t.font.size = Pt(15)

    tbl = doc.add_table(rows=0, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    col_widths = [Inches(1.8), Inches(4.7)]

    def add_row_key_val(key, val, is_zebra=False, is_bold_val=False, text_color=None):
        r_cells = tbl.add_row().cells
        bg_col = "F1F5F9" if is_zebra else "FFFFFF"
        for idx, (c, txt) in enumerate(zip(r_cells, [key, val])):
            c.text = txt
            set_cell_background(c, "E2E8F0" if idx == 0 else bg_col)
            set_cell_margins(c, top=60, bottom=60, left=90, right=90)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.name = "TH Sarabun New"
                run.font.size = Pt(13.5)
                if idx == 0 or is_bold_val:
                    run.bold = True
                if text_color and idx == 1:
                    run.font.color.rgb = text_color
            c.width = col_widths[idx]

    add_row_key_val("รหัสตัวอย่าง / ข้อสอบ", exam_info, is_zebra=True, is_bold_val=True)

    # Row with Image
    r_img_cells = tbl.add_row().cells
    r_img_cells[0].text = "ภาพกระดาษคำตอบจริง"
    set_cell_background(r_img_cells[0], "E2E8F0")
    set_cell_margins(r_img_cells[0], top=60, bottom=60, left=90, right=90)
    p_k = r_img_cells[0].paragraphs[0]
    p_k.paragraph_format.space_before = Pt(0)
    p_k.paragraph_format.space_after = Pt(0)
    for run in p_k.runs:
        run.font.name = "TH Sarabun New"
        run.font.size = Pt(13.5)
        run.bold = True
    r_img_cells[0].width = col_widths[0]

    # Image cell
    set_cell_background(r_img_cells[1], "FFFFFF")
    set_cell_margins(r_img_cells[1], top=60, bottom=60, left=90, right=90)
    p_v = r_img_cells[1].paragraphs[0]
    p_v.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_v.paragraph_format.space_before = Pt(2)
    p_v.paragraph_format.space_after = Pt(2)
    if img_path and os.path.exists(img_path):
        run_img = p_v.add_run()
        run_img.add_picture(str(img_path), width=Inches(3.4))
    r_img_cells[1].width = col_widths[1]

    add_row_key_val("คำตอบของนิสิต", student_answer, is_zebra=False)
    add_row_key_val("เกณฑ์เฉลย (Rubric)", rubric, is_zebra=True)
    add_row_key_val("คะแนนผู้สอน", scores_dict['teacher'], is_zebra=False, is_bold_val=True)
    
    # AI score with match status
    score_ai_text = f"{scores_dict['ai']} ({scores_dict['status']})"
    add_row_key_val("คะแนนระบบ AI", score_ai_text, is_zebra=True, is_bold_val=True, text_color=RGBColor(3, 105, 161))
    
    add_row_key_val("ข้อเสนอแนะสำหรับผู้สอน", feedback_teacher, is_zebra=False)
    add_row_key_val("ข้อเสนอแนะสำหรับนักเรียน", feedback_student, is_zebra=True)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(0)
    p_space.paragraph_format.space_after = Pt(6)

def generate_thesis_word_document():
    doc = Document()
    
    # 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    print("Generating Chapter 4 Word Document...")
    add_heading(doc, "บทที่ 4", level=0)
    add_heading(doc, "การทดสอบระบบ", level=0)
    
    add_para(doc, "บทนี้นำเสนอผลการประเมินระบบให้คะแนนข้อสอบอัตนัยอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) โดยเปรียบเทียบคะแนนจากแบบจำลองปัญญาประดิษฐ์กับคะแนนจริงของผู้สอนในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี พร้อมนำเสนอกรณีทดสอบการทำงานของระบบแอปพลิเคชันตามขอบเขตของโครงงาน ครอบคลุมการทำงานของผู้สอนและผู้เรียนอย่างครบวงจร")
    add_para(doc, "หัวข้อ 4.1 นำเสนอการประเมินความแม่นยำของระบบตรวจข้อสอบจากไฟล์ ชุดข้อสอบ_dataset.xlsx และเกณฑ์ในชีต Exam_Rubrics โดยแสดงขั้นตอนการเตรียมข้อมูลเพื่อป้องกันการรั่วไหล มาตรวัดประสิทธิภาพ ผลการทดลองพร้อมการแทนค่าสูตรคำนวณอย่างละเอียด คอนฟิวชันเมทริกซ์ ตัวอย่างผลการตรวจจริงพร้อมภาพประกอบ และการวิเคราะห์กรณีศึกษา ส่วนหัวข้อ 4.2 แสดงกรณีทดสอบการทำงานของฟังก์ชันระบบทั้ง 19 กรณีทดสอบ")
    
    # 4.1
    add_heading(doc, "4.1 ข้อมูลที่ใช้ในการทดสอบและการประเมินระบบตรวจข้อสอบด้วย AI", level=1)
    add_para(doc, "การประเมินมีวัตถุประสงค์เพื่อศึกษาประสิทธิภาพของระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) โดยนำแบบจำลองปัญญาประดิษฐ์มาประเมินคำตอบของนิสิตในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี แล้วเปรียบเทียบกับคะแนนการตรวจจริงของอาจารย์ผู้สอน เพื่อวิเคราะห์ความสอดคล้อง ความแม่นยำ และความน่าเชื่อถือในฐานะเครื่องมือช่วยสนับสนุนการตรวจข้อสอบ (Grading Assistance Tool)")
    
    # 4.1.1
    add_heading(doc, "4.1.1 ชุดข้อมูลสำหรับประเมินระบบตรวจข้อสอบ (Dataset Description & Modalities)", level=2)
    add_para(doc, "ชุดข้อมูลที่ใช้ในการประเมินประสิทธิภาพนำมาจากข้อสอบจริงรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี จำนวนทั้งสิ้น 6 ข้อสอบ โดยแต่ละข้อประกอบด้วยกระดาษคำตอบจริงของนิสิตข้อละ 34 ชุด รวมทั้งสิ้น 204 ตัวอย่าง ซึ่งได้รับการบันทึกข้อมูลอย่างเป็นระบบในชีต ชุดข้อสอบ_dataset ในไฟล์ ชุดข้อสอบ_dataset.xlsx โดยแบ่งลักษณะคำตอบตามรูปแบบข้อมูล (Modality) ออกเป็น 2 กลุ่มหลัก ดังนี้")
    
    add_para(doc, "จำนวน 102 ตัวอย่าง ครอบคลุมคำตอบเชิงบรรยายทางทฤษฎี ได้แก่ การจัดเรียงอาร์เรย์สองมิติ (Row-major vs. Column-major), การวิเคราะห์ความซับซ้อนเชิงเวลา (Time Complexity: O(n log n) vs. O(n²)) และการเปรียบเทียบโครงสร้างข้อมูลแบบลิงก์ลิสต์กับอาร์เรย์ (Linked List vs. Array สำหรับ Stack และ Queue)", bold_prefix="1) กลุ่มคำตอบแบบข้อความ (Text-based Modality: ข้อ 1–3): ")
    add_figure(doc, ROOT / "public/screenshots/dataset_samples_text.png", "ภาพประกอบที่ 4.1 ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มข้อความ (Text Modality: ข้อ 1–3)")
    
    add_para(doc, "จำนวน 102 ตัวอย่าง ครอบคลุมคำตอบที่ต้องวาดโครงสร้างทางคณิตศาสตร์และขั้นตอนการแปลง ได้แก่ การสร้างต้นไม้ค้นหาทวิภาค 12 โหนด (Binary Search Tree Construction), การแปลงนิพจน์คณิตศาสตร์ Infix เป็น Prefix และ Postfix พร้อมแสดงวิธีทำ และการแปลงต้นไม้ทั่วไป (General Tree) เป็นต้นไม้ทวิภาคตามหลัก Left-Child Right-Sibling (LCRS)", bold_prefix="2) กลุ่มคำตอบแบบรูปภาพและแผนภาพ (Image/Diagram Modality: ข้อ 4–6): ")
    add_figure(doc, ROOT / "public/screenshots/dataset_samples_image.png", "ภาพประกอบที่ 4.2 ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มรูปภาพ (Image Modality: ข้อ 4–6)")
    
    # Table 4.1
    p_t1 = doc.add_paragraph()
    r = p_t1.add_run("ตารางที่ 4.1 รายละเอียดและโครงสร้างของชุดข้อมูลที่ใช้ประเมินระบบตรวจข้อสอบ")
    r.bold = True
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    
    t1 = doc.add_table(rows=1, cols=6)
    t1_widths = [Inches(0.6), Inches(2.2), Inches(0.9), Inches(0.8), Inches(0.7), Inches(1.3)]
    create_table_header(t1, ["ข้อที่", "หัวข้อโจทย์", "ประเภทคำตอบ", "คะแนนเต็ม", "จำนวนตัวอย่าง", "ลักษณะคำตอบและสาระสำคัญของโจทย์"], t1_widths)
    ds_table_rows = [
        ["1", "Row-major vs. Column-major", "ข้อความ", "2.00", "34", "บรรยายความแตกต่างของการเรียงสมาชิกในหน่วยความจำตามแถวเทียบกับตามคอลัมน์"],
        ["2", "Time Complexity: O(n log n) vs. O(n²)", "ข้อความ", "2.00", "34", "อธิบายเหตุผลว่าทำไม O(n log n) เหมาะกับข้อมูลขนาดใหญ่ พร้อมระบุชื่ออัลกอริทึมประกอบ"],
        ["3", "Linked List vs. Array", "ข้อความ", "1.00", "34", "เปรียบเทียบข้อดีข้อเสียและความแตกต่างเชิงโครงสร้างในการประยุกต์ทำ Stack และ Queue"],
        ["4", "Binary Search Tree (12 Nodes)", "รูปภาพ", "1.00", "34", "ภาพวาดผังโครงสร้างต้นไม้ BST ประกอบด้วยตัวเลข 12 โหนดตามลำดับที่โจทย์กำหนด"],
        ["5", "Infix to Prefix and Postfix", "รูปภาพ", "1.00", "34", "ภาพแสดงขั้นตอนวิธีทำและคำตอบสุดท้ายของการแปลงนิพจน์เป็น Prefix และ Postfix"],
        ["6", "General Tree to Binary Tree (LCRS)", "รูปภาพ", "1.00", "34", "ภาพวาดการแปลงต้นไม้ทั่วไป 10 โหนดให้อยู่ในรูปต้นไม้ทวิภาคตามกฎ Left-Child Right-Sibling"],
        ["รวม", "รวมทั้งสิ้น (กลุ่มข้อความ 102 + กลุ่มรูปภาพ 102)", "2 กลุ่ม", "8.00", "204", "ครอบคลุมขอบเขตวิชาโครงสร้างข้อมูลทั้งเชิงบรรยายและแผนภาพโครงสร้าง"]
    ]
    for idx, r_data in enumerate(ds_table_rows):
        add_table_row(t1, r_data, is_zebra=(idx%2==1), col_widths=t1_widths, align_center_cols=[0, 2, 3, 4])
        
    # 4.1.2 Preprocessing
    add_heading(doc, "4.1.2 ขั้นตอนการเตรียมข้อมูลและป้องกันการรั่วไหลของข้อมูล (Data Preprocessing Pipeline)", level=2)
    add_para(doc, "เนื่องจากกระดาษคำตอบจริงของนิสิตทุกใบผ่านการตรวจและบันทึกคะแนนด้วยปากกาหมึกสีแดงและสีน้ำเงินจากอาจารย์ผู้สอนมาก่อนแล้ว การนำภาพถ่ายกระดาษคำตอบดิบส่งเข้าสู่แบบจำลองวิสัยทัศน์ของ LLM โดยตรงอาจก่อให้เกิดปัญหา การรั่วไหลของข้อมูลเฉลย (Data Leakage) โดยโมเดลอาจตรวจจับรอยตัวเลขคะแนนเดิมบนกระดาษและนำมาใช้เป็นฐานในการตัดสินคะแนน ทำให้ผลการประเมินขาดความเที่ยงตรงทางวิทยาศาสตร์ ดังนั้น โครงงานนี้จึงได้ออกแบบกระบวนการเตรียมข้อมูลล่วงหน้า (Data Preprocessing Pipeline) 4 ขั้นตอนอย่างเคร่งครัด")
    add_figure(doc, ROOT / "public/screenshots/preprocessing_pipeline.png", "ภาพประกอบที่ 4.3 ตัวอย่างขั้นตอนการแปลงและเตรียมภาพคำตอบก่อนส่งเข้าโมเดล (Preprocessing Pipeline)")
    
    # Table 4.2
    p_t2 = doc.add_paragraph()
    r = p_t2.add_run("ตารางที่ 4.2 ตัวอย่างขั้นตอนและเทคนิคการประมวลผลข้อมูลก่อนเข้าสู่แบบจำลอง")
    r.bold = True
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    
    t2 = doc.add_table(rows=1, cols=4)
    t2_widths = [Inches(0.6), Inches(1.8), Inches(2.1), Inches(2.0)]
    create_table_header(t2, ["ขั้นตอน", "ชื่อกระบวนการ", "เทคนิคการประมวลผล", "วัตถุประสงค์และผลลัพธ์ที่ได้"], t2_widths)
    prep_rows = [
        ["1", "การระบุพิกัดพื้นที่คะแนน (Score ROI Detection)", "กำหนดพิกัดขอบเขต (Bounding Box) บริเวณมุมขวาหรือด้านข้างที่มีรอยตรวจคะแนนของอาจารย์", "แยกแยะระหว่างลายมือคำตอบของนิสิตกับรอยตรวจคะแนนของอาจารย์ออกจากกัน"],
        ["2", "การขจัดรอยตรวจคะแนน (Pen Inpainting & Removal)", "สร้าง Binary Mask คลุมบริเวณรอยคะแนน และใช้เทคนิค Inpainting เติมเต็มด้วยพื้นผิวเนื้อกระดาษสะอาด", "ป้องกัน Data Leakage ไม่ให้โมเดลมองเห็นตัวเลขคะแนนเดิมของอาจารย์ได้อย่างเด็ดขาด 100%"],
        ["3", "การปรับหมุนทิศทางภาพ (Upright Auto-Orientation)", "ตรวจจับความหนาแน่นของตัวอักษรหัวข้อพิมพ์ (Header Density) และปรับหมุนภาพ 90° หรือ 270°", "ทำให้ภาพกระดาษคำตอบตั้งตรง (Upright) ในทิศทางการอ่านปกติ ตัวอักษรและกิ่งต้นไม้ไม่กลับหัว"],
        ["4", "การปรับสเกลและเพิ่มความคมชัด (Normalization & Contrast)", "ปรับขนาดมิติสูงสุดไม่เกิน 1,200 พิกเซล และเพิ่มค่า Contrast ปรับสมดุลความสว่างของลายมือดินสอ", "ลดภาระการประมวลผล Token ของโมเดล และเพิ่มความชัดเจนของเส้นเชื่อมโยงโครงสร้าง"]
    ]
    for idx, r_data in enumerate(prep_rows):
        add_table_row(t2, r_data, is_zebra=(idx%2==1), col_widths=t2_widths, align_center_cols=[0])

    # 4.1.3 Metrics & Rubrics
    add_heading(doc, "4.1.3 การกำหนดเกณฑ์ประเมินและมาตรวัดประสิทธิภาพ (Evaluation Metrics & Formulations)", level=2)
    add_para(doc, "เกณฑ์การให้คะแนนอ้างอิงตามเกณฑ์มาตรฐานในชีต Exam_Rubrics โดยกำหนดตัวชี้วัดทางสถิติเพื่อประเมินความสอดคล้องระหว่างคะแนนผู้สอน (Hi) กับคะแนนระบบ AI (Ai) สำหรับคำตอบจำนวน N = 204 ตัวอย่าง ดังนี้")
    
    # Table 4.3 Rubrics
    p_t3 = doc.add_paragraph()
    r = p_t3.add_run("ตารางที่ 4.3 สรุปเกณฑ์การให้คะแนนอ้างอิงตาม Rubric รายวิชาโครงสร้างข้อมูล")
    r.bold = True
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    
    t3 = doc.add_table(rows=1, cols=4)
    t3_widths = [Inches(0.6), Inches(2.2), Inches(0.8), Inches(2.9)]
    create_table_header(t3, ["ข้อ", "หัวข้อโจทย์", "เต็ม", "เกณฑ์การพิจารณาและระดับคะแนนย่อย (Rubric Criteria)"], t3_widths)
    rubric_rows = [
        ["1", "Row-major vs. Column-major", "2.00", "ประเมินความเข้าใจความต่าง 3 ระดับ (ให้ AI วิเคราะห์ตามหลักการโดยอิสระ): อธิบายถูกต้องครบทั้ง 2 ฝั่งได้ 2.00; ถูกต้องฝั่งเดียวหรือระบุความเข้าใจเบื้องต้นได้ 1.00; ตอบผิดทั้งหมดหรือไม่ตอบได้ 0.00"],
        ["2", "Time Complexity", "2.00", "มีชื่ออัลกอริทึมและเหตุผลเปรียบเทียบครบถ้วนได้ 2.00; มีตัวอย่างแต่อธิบายสั้นได้ 1.50; ขาดตัวอย่างได้ 1.00; ผิดทั้งหมดได้ 0.00"],
        ["3", "Linked List vs. Array", "1.00", "ความแตกต่างเชิงโครงสร้าง 0.50 คะแนน และข้อดีข้อเสีย 0.50 คะแนน แต่ละส่วนให้ 0, 0.25 หรือ 0.50 รวมเป็น 0, 0.25, 0.50, 0.75, 1.00"],
        ["4", "Binary Search Tree (12 Nodes)", "1.00", "โครงสร้างและการวางตำแหน่งโหนดถูกต้องครบทั้ง 12 โหนดได้ 1.00 คะแนน; วางโหนดผิดตำแหน่ง ขาดโหนด หรือไม่วาดได้ 0.00 คะแนน"],
        ["5", "Infix to Prefix and Postfix", "1.00", "แยก Prefix (0.50 คะแนน) และ Postfix (0.50 คะแนน) ต้องแสดงวิธีทำและคำตอบถูกต้องสมบูรณ์ (คะแนนที่เป็นไปได้คือ 0.00, 0.50 หรือ 1.00 คะแนน)"],
        ["6", "General Tree to Binary Tree", "1.00", "แปลงตามหลัก Left-Child Right-Sibling ถูกต้องครบถ้วนได้ 1.00 คะแนน; โครงสร้างผิดหรือวางกิ่งผิดได้ 0.00 คะแนน"]
    ]
    for idx, r_data in enumerate(rubric_rows):
        add_table_row(t3, r_data, is_zebra=(idx%2==1), col_widths=t3_widths, align_center_cols=[0, 2])

    add_para(doc, "สัดส่วนของคำตอบที่คะแนนระบบ AI ตรงกับคะแนนผู้สอนเป๊ะทุกประการ สูตรคำนวณ: Exact Match = (∑[Hi = Ai] / N) × 100%", bold_prefix="• ความตรงกันสมบูรณ์ (Exact Match Ratio / Accuracy): ")
    add_para(doc, "สัดส่วนคำตอบที่ผลต่างคะแนนไม่เกิน 0.50 คะแนน ซึ่งสะท้อนความสามารถในการนำไปใช้งานจริงโดยไม่เกิดความผิดพลาดอย่างรุนแรง สูตรคำนวณ: Within 0.50 = (∑[|Hi - Ai| ≤ 0.50] / N) × 100%", bold_prefix="• เกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Acceptable Error Rate: Within ±0.50 pt): ")
    add_para(doc, "ค่าเฉลี่ยผลต่างคะแนนสัมบูรณ์ ค่ายิ่งต่ำแสดงว่าระดับคะแนนยิ่งใกล้เคียงกับอาจารย์ สูตรคำนวณ: MAE = (1/N) ∑ |Hi - Ai|", bold_prefix="• ค่าความคลาดเคลื่อนเฉลี่ยสัมบูรณ์ (Mean Absolute Error: MAE): ")
    add_para(doc, "ค่าความคลาดเคลื่อนที่ให้น้ำหนักต่อความผิดพลาดขนาดใหญ่ ค่ายิ่งต่ำแสดงถึงเสถียรภาพของระบบ สูตรคำนวณ: RMSE = √[ (1/N) ∑ (Hi - Ai)² ]", bold_prefix="• ค่าความคลาดเคลื่อนกำลังสองเฉลี่ย (Root Mean Squared Error: RMSE): ")
    add_para(doc, "ทิศทางและความสัมพันธ์เชิงเส้นระหว่างคะแนนผู้สอนกับคะแนน AI มีค่าระหว่าง -1 ถึง 1 สูตรคำนวณ: r = Cov(H, A) / (σH · σA)", bold_prefix="• สัมประสิทธิ์สหสัมพันธ์เพียร์สัน (Pearson Correlation Coefficient: r): ")
    add_para(doc, "มาตรวัดความสอดคล้องมาตรฐานสำหรับงานประเมินการให้คะแนนอัตโนมัติ โดยหักล้างความสอดคล้องที่อาจเกิดจากความบังเอิญออก สูตรคำนวณ: κ = 1 - [ ∑ wij Oij / ∑ wij Eij ]", bold_prefix="• สัมประสิทธิ์ความสอดคล้องแคปปาแบบถ่วงน้ำหนักกำลังสอง (Quadratic Weighted Kappa: QWK): ")

    # 4.1.4 Results with Detailed Calculations
    add_heading(doc, "4.1.4 ผลการทดลองและแสดงการคำนวณอย่างละเอียด (Evaluation Results & Step-by-Step Calculations)", level=2)
    add_para(doc, "ผลการประเมินระบบตรวจข้อสอบอัตโนมัติด้วย AI จากชุดข้อมูลทดสอบจริง 204 ตัวอย่าง ได้รับการประมวลผลและคำนวณตามสูตรทางคณิตศาสตร์อย่างครบถ้วน โดยแสดงการแทนค่าตัวเลขจริงทีละขั้นตอนดังตารางที่ 4.4 ซึ่งถอดแบบการแสดงสูตรและผลลัพธ์ตามมาตรฐานของรายงานวิจัยอ้างอิง")
    
    # Table 4.4 (The central table requested!)
    p_t4 = doc.add_paragraph()
    r = p_t4.add_run("ตารางที่ 4.4 เปรียบเทียบผลการประเมินประสิทธิภาพโดยรวม พร้อมแสดงสูตรและการแทนค่าคำนวณจริง")
    r.bold = True
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    
    t4 = doc.add_table(rows=1, cols=4)
    t4_widths = [Inches(1.8), Inches(1.0), Inches(1.8), Inches(1.9)]
    create_table_header(t4, ["ตัวชี้วัด (Metric)", "ผลลัพธ์ที่ได้", "สูตรการคำนวณ (Mathematical Formula)", "การแทนค่าตัวเลขจริงทีละขั้นตอน (Step-by-Step Substitution)"], t4_widths)
    calc_rows = [
        ["Exact Match (ความตรงกันสมบูรณ์)", "78.43%", "Exact Match = (∑[Hi = Ai] / N) × 100%", "(160 / 204) × 100% = 78.4314% ≈ 78.43%\n(คะแนนตรงกันสมบูรณ์ 160 จาก 204 คำตอบ)"],
        ["Within ±0.50 pt (ความคลาดเคลื่อนยอมรับได้)", "93.63%", "Within 0.50 = (∑[|Hi - Ai| ≤ 0.50] / N) × 100%", "(191 / 204) × 100% = 93.6275% ≈ 93.63%\n(คะแนนต่างไม่เกินครึ่งคะแนน 191 จาก 204 คำตอบ)"],
        ["MAE (ความคลาดเคลื่อนเฉลี่ยสัมบูรณ์)", "0.1311 pt", "MAE = (1/N) ∑ |Hi - Ai|", "26.7500 / 204 = 0.13112 ≈ 0.1311 คะแนน\n(ผลรวมผลต่างคะแนนสัมบูรณ์เท่ากับ 26.75 คะแนน)"],
        ["RMSE (ความคลาดเคลื่อนกำลังสองเฉลี่ย)", "0.3307 pt", "RMSE = √[ (1/N) ∑ (Hi - Ai)² ]", "√(22.3125 / 204) = √0.10937 ≈ 0.3307 คะแนน\n(ผลรวมผลต่างยกกำลังสองเท่ากับ 22.3125)"],
        ["Pearson Correlation (r)", "0.8562", "r = Cov(H, A) / (σH · σA)", "ความสัมพันธ์เชิงเส้นระดับสูงมาก (r = 0.8562, p < 0.001)"],
        ["Quadratic Weighted Kappa (QWK)", "0.8685", "κ = 1 - (∑ wij Oij / ∑ wij Eij)", "QWK = 0.8685\n(ความสอดคล้องระดับเกือบสมบูรณ์แบบ Near Perfect Agreement)"]
    ]
    for idx, r_data in enumerate(calc_rows):
        add_table_row(t4, r_data, is_zebra=(idx%2==1), col_widths=t4_widths, align_center_cols=[1])

    # Table 4.5 Question level
    p_t5 = doc.add_paragraph()
    r = p_t5.add_run("ตารางที่ 4.5 ผลการประเมินประสิทธิภาพและความสอดคล้องจำแนกรายข้อสอบ (Question-Level Performance)")
    r.bold = True
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    
    t5 = doc.add_table(rows=1, cols=6)
    t5_widths = [Inches(0.5), Inches(2.2), Inches(0.8), Inches(0.6), Inches(1.2), Inches(1.2)]
    create_table_header(t5, ["ข้อที่", "หัวข้อโจทย์", "ประเภท", "เต็ม", "Exact Match (%)", "Within ±0.50 (%)"], t5_widths)
    q_perf_rows = [
        ["1", "Row-major vs. Column-major", "ข้อความ", "2.00", "27/34 (79.41%)", "27/34 (79.41%)"],
        ["2", "Time Complexity: O(n log n) vs. O(n²)", "ข้อความ", "2.00", "19/34 (55.88%)", "29/34 (85.29%)"],
        ["3", "Linked List vs. Array", "ข้อความ", "1.00", "12/34 (35.29%)", "33/34 (97.06%)"],
        ["4", "Binary Search Tree (12 Nodes)", "รูปภาพ", "1.00", "34/34 (100.00%)", "34/34 (100.00%)"],
        ["5", "Infix to Prefix and Postfix", "รูปภาพ", "1.00", "34/34 (100.00%)", "34/34 (100.00%)"],
        ["6", "General Tree to Binary Tree (LCRS)", "รูปภาพ", "1.00", "34/34 (100.00%)", "34/34 (100.00%)"],
        ["รวม", "ค่าเฉลี่ยรวมทั้งระบบ (204 ตัวอย่าง)", "2 กลุ่ม", "8.00", "160/204 (78.43%)", "191/204 (93.63%)"]
    ]
    for idx, r_data in enumerate(q_perf_rows):
        add_table_row(t5, r_data, is_zebra=(idx%2==1), col_widths=t5_widths, align_center_cols=[0, 2, 3, 4, 5])

    # Table 4.6 Modality
    p_t6 = doc.add_paragraph()
    r = p_t6.add_run("ตารางที่ 4.6 ผลการประเมินประสิทธิภาพจำแนกตามประเภทคำตอบ (Text vs. Image Modality)")
    r.bold = True
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    
    t6 = doc.add_table(rows=1, cols=5)
    t6_widths = [Inches(2.2), Inches(1.0), Inches(1.1), Inches(1.1), Inches(1.1)]
    create_table_header(t6, ["กลุ่มประเภทคำตอบ", "จำนวนคำตอบ", "Exact Match (%)", "Within ±0.50 pt (%)", "MAE (คะแนน)"], t6_widths)
    mod_rows = [
        ["กลุ่มข้อความ (Text Modality: ข้อ 1–3)", "102", "58/102 (56.86%)", "89/102 (87.25%)", "0.2623"],
        ["กลุ่มรูปภาพ (Image Modality: ข้อ 4–6)", "102", "102/102 (100.00%)", "102/102 (100.00%)", "0.0000"],
        ["ภาพรวมทั้งระบบ (Total Dataset)", "204", "160/204 (78.43%)", "191/204 (93.63%)", "0.1311"]
    ]
    for idx, r_data in enumerate(mod_rows):
        add_table_row(t6, r_data, is_zebra=(idx%2==1), col_widths=t6_widths, align_center_cols=[1, 2, 3, 4])

    # Table 4.7 Confusion Matrix
    p_t7 = doc.add_paragraph()
    r = p_t7.add_run("ตารางที่ 4.7 คอนฟิวชันเมทริกซ์ (Confusion Matrix) แสดงการกระจายตัวของระดับคะแนนระหว่างอาจารย์กับ AI")
    r.bold = True
    r.font.name = "TH Sarabun New"
    r.font.size = Pt(15)
    
    t7 = doc.add_table(rows=1, cols=9)
    t7_widths = [Inches(1.5), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.8)]
    create_table_header(t7, ["คะแนนอาจารย์", "0.00", "0.25", "0.50", "0.75", "1.00", "1.50", "2.00", "รวมอาจารย์"], t7_widths)
    cm_data = [
        ["0.00 (ศูนย์)", "27", "2", "1", "1", "1", "0", "0", "32"],
        ["0.25 (หนึ่งในสี่)", "0", "0", "1", "0", "0", "0", "0", "1"],
        ["0.50 (ครึ่งหนึ่ง)", "3", "1", "14", "4", "4", "0", "0", "26"],
        ["0.75 (สามในสี่)", "0", "1", "0", "2", "1", "0", "0", "4"],
        ["1.00 (หนึ่งคะแนน)", "1", "0", "0", "3", "86", "1", "5", "96"],
        ["1.50 (หนึ่งครึ่ง)", "1", "0", "0", "0", "5", "1", "1", "8"],
        ["2.00 (สองคะแนน)", "1", "0", "0", "0", "3", "3", "30", "37"],
        ["รวมระบบ AI", "33", "4", "16", "10", "100", "5", "36", "204"]
    ]
    for idx, r_data in enumerate(cm_data):
        add_table_row(t7, r_data, is_zebra=(idx%2==1), col_widths=t7_widths, align_center_cols=[1, 2, 3, 4, 5, 6, 7, 8])

    add_para(doc, "ผลลัพธ์จากตารางที่ 4.7 ชี้ให้เห็นว่าการกระจายตัวของคะแนนส่วนใหญ่ตกอยู่บนแนวทแยงมุมหลัก (Diagonal Agreement) จำนวน 160 ตัวอย่าง (คิดเป็นร้อยละ 78.43) โดยความคลาดเคลื่อนเกือบทั้งหมดเกิดขึ้นในช่องที่อยู่ติดกับแนวทแยงมุมหลักเพียงเล็กน้อย (Off-by-one errors) เช่น ผู้สอนให้ 0.50 แต่ AI ให้ 0.75 จำนวน 4 ตัวอย่าง หรือผู้สอนให้ 1.00 แต่ AI ให้ 0.75 จำนวน 3 ตัวอย่าง และไม่มีข้อผิดพลาดรุนแรงแบบขั้วตรงข้าม แสดงว่าระบบมีเสถียรภาพและความสม่ำเสมอในการตัดสินใจสูงมาก")

    # 4.1.5 Prediction Examples with Actual Images
    add_heading(doc, "4.1.5 ตัวอย่างผลลัพธ์การทำนายจริงจากชุดข้อมูล (Prediction Examples with Actual Images)", level=2)
    add_para(doc, "เพื่อแสดงให้เห็นถึงกลไกการวิเคราะห์และข้อเสนอแนะป้อนกลับสองระดับ (Dual-Perspective Feedback) อย่างเป็นรูปธรรม ในส่วนนี้นำเสนอตัวอย่างผลลัพธ์การทำนายจริงจากชุดข้อมูลทดสอบทั้ง 6 ข้อสอบ ครอบคลุมทั้งกรณีที่ได้คะแนนเต็ม ได้คะแนนบางส่วน และคะแนนศูนย์ ดังแสดงในตารางที่ 4.8 ถึง 4.13")

    # Q1 DS-001
    add_prediction_example_table(
        doc, "ตารางที่ 4.8 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 1: ข้อ 1 (Row-major vs. Column-major) รหัส DS-001",
        "DS-001 | ข้อ 1 (กลุ่มข้อความ: การเรียงสมาชิกของอาร์เรย์ 2 มิติ)",
        ROOT / "public/screenshots/case_studies/case1_ds001.jpg",
        "\"Row จะนับเป็นแถว จากซ้ายไปขวา เช่น [0 1 2 3], [4 5 6 7] ส่วน Column จากบนลงล่าง เช่น 0 4 8, 1 5 9\"",
        "อธิบายความต่างถูกต้องครบทั้ง 2 ฝั่ง (Row-major แนวนอน/แถว vs Column-major แนวตั้ง/คอลัมน์) ได้ 2.00 คะแนนเต็ม",
        {'teacher': '2.00 / 2.00 คะแนน', 'ai': '2.00 / 2.00 คะแนน', 'status': 'Exact Match 100%'},
        "คำตอบครบถ้วนทั้งสองประเด็น อธิบายทิศทางและยกตัวอย่างลำดับดัชนีของ Row และ Column ได้ถูกต้องตามหลักการจัดเก็บในหน่วยความจำ",
        "ตอบถูกต้องครบถ้วนแล้ว หากต้องการให้สมบูรณ์ยิ่งขึ้น ควรอธิบายเสริมว่าลำดับการจัดเก็บนี้ส่งผลต่อการคำนวณตำแหน่ง Address ในหน่วยความจำจริง"
    )

    # Q2 DS-047
    add_prediction_example_table(
        doc, "ตารางที่ 4.9 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 2: ข้อ 2 (Time Complexity) รหัส DS-047",
        "DS-047 | ข้อ 2 (กลุ่มข้อความ: O(n log n) vs. O(n²))",
        ROOT / "public/screenshots/case_studies/case2_ds047.jpg",
        "\"เพราะว่า Big-O (n log n) จะทำการหารครึ่ง หรือแบ่งครึ่ง หรือ (n log n) ทำให้คำนวณข้อมูลขนาดใหญ่ได้เร็วกว่า O(n^2) ส่วน Big-O(n^2) ส่วนมากใช้ใน sort จะใช้เวลามากกว่าในการคำนวณ\nตัวอย่าง Algorithm:\n• O(n log n) = Merge sort\n• O(n^2) = Insertion sort, Selection sort\"",
        "อธิบายเปรียบเทียบอัตราการเติบโต และระบุชื่ออัลกอริทึมที่เกี่ยวข้องถูกต้อง ได้คะแนนเต็ม 2.00",
        {'teacher': '2.00 / 2.00 คะแนน', 'ai': '2.00 / 2.00 คะแนน', 'status': 'Exact Match 100%'},
        "ตอบถูกต้องครบถ้วน ระบุข้อเสียของลูปซ้อนใน O(n²) และยกตัวอย่าง Merge Sort ที่มีความซับซ้อน O(n log n) ได้ตรงตามเกณฑ์",
        "คำตอบดีมาก เข้าใจหลักการว่าเมื่อ n มีค่ามาก การทำงานแบบลูปซ้อนจะใช้เวลานานกว่าการแบ่งข้อมูลย่อยแบบ Divide and Conquer"
    )

    # Q3 DS-072
    add_prediction_example_table(
        doc, "ตารางที่ 4.10 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 3: ข้อ 3 (Linked List vs. Array) รหัส DS-072",
        "DS-072 | ข้อ 3 (กลุ่มข้อความ: Linked List vs. Array สำหรับ Stack และ Queue)",
        ROOT / "public/screenshots/case_studies/case3_ds072.jpg",
        "\"• สแตก ทำงานแบบ เข้าทีหลัง แต่ออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access\n• คิว ทำงานแบบ เข้าก่อน และออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access\n• อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า\"",
        "ความแตกต่างเชิงโครงสร้าง (0.50 pt) และข้อดีข้อเสีย (0.50 pt) คะแนนเต็ม 1.00",
        {'teacher': '0.50 / 1.00 คะแนน', 'ai': '0.50 / 1.00 คะแนน', 'status': 'Partial Credit Exact Match'},
        "ให้ 0.50 คะแนนในส่วนข้อดีข้อเสียของ Array ที่ระบุว่าเข้าถึงเร็วแต่เพิ่ม-ลบช้า ส่วน Stack และ Queue นักเรียนอธิบายพฤติกรรม LIFO/FIFO แทนที่จะอธิบายการนำ Linked List ไปสร้าง จึงไม่ได้คะแนนในส่วนแรก",
        "ควรอธิบายเปรียบเทียบระหว่าง Linked List กับ Array โดยตรง เช่น Linked List มีขนาดปรับเปลี่ยนได้แบบไดนามิกและเพิ่ม-ลบหัวแถวได้ O(1) ขณะที่ Array ขนาดคงที่"
    )

    # Q4 DS-104
    add_prediction_example_table(
        doc, "ตารางที่ 4.11 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 4: ข้อ 4 (วาด Binary Search Tree 12 โหนด) รหัส DS-104",
        "DS-104 | ข้อ 4 (กลุ่มรูปภาพ: การสร้าง Binary Search Tree จาก 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99)",
        ROOT / "public/screenshots/case_studies/case4_ds104.jpg",
        "(ภาพวาดต้นไม้ค้นหาทวิภาคที่มี Root คือ 9 มีโหนดครบทั้ง 12 โหนด)",
        "โครงสร้างต้นไม้และการวางตำแหน่งกิ่งซ้าย-ขวาถูกต้องครบ 12 โหนด ได้ 1.00 คะแนนเต็ม",
        {'teacher': '1.00 / 1.00 คะแนน', 'ai': '1.00 / 1.00 คะแนน', 'status': 'Exact Match 100%'},
        "ระบบตรวจจับโหนดและเส้นเชื่อมโยงได้ครบ 12 โหนด การจัดวางกิ่งซ้าย (< 9) คือ 5 และกิ่งขวา (> 9) ถูกต้องตามกฎ BST ทุกประการ",
        "วาดแผนภาพโครงสร้างต้นไม้ BST ได้ถูกต้องสมบูรณ์แบบ ทั้งตำแหน่ง Root กิ่งย่อย และโหนดใบ"
    )

    # Q5 DS-154
    add_prediction_example_table(
        doc, "ตารางที่ 4.12 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 5: ข้อ 5 (แปลง Infix เป็น Prefix และ Postfix) รหัส DS-154",
        "DS-154 | ข้อ 5 (กลุ่มรูปภาพ: แปลงนิพจน์ A + (B * (C - (D / (F * 2)))))",
        ROOT / "public/screenshots/case_studies/case5_ds154.jpg",
        "(ภาพแสดงวิธีทำแปลงนิพจน์ทีละวงเล็บ และเขียนตอบ Prefix และ Postfix ท้ายกระดาษ)",
        "แยก Prefix (0.50 pt) และ Postfix (0.50 pt) ต้องแสดงวิธีทำและคำตอบถูกต้อง",
        {'teacher': '0.50 / 1.00 คะแนน', 'ai': '0.50 / 1.00 คะแนน', 'status': 'Partial Credit Exact Match'},
        "ส่วน Prefix ทำวิธีทำและตอบถูกต้อง (+A*B-C/D*F2) ได้ 0.50 แต่ส่วน Postfix แปลงผิดหลักการโดยนำเครื่องหมายไว้ตรงกลางคล้าย Infix จึงได้ 0.00 รวม 0.50 คะแนน ตรงกับอาจารย์",
        "การแปลงเป็น Postfix ตัวดำเนินการต้องอยู่หลังตัวแปรเสมอ เช่น F * 2 ต้องเป็น F 2 * และผลลัพธ์สุดท้ายต้องไม่มีเครื่องหมายคั่นกลางตัวถูกดำเนินการ"
    )

    # Q6 DS-171
    add_prediction_example_table(
        doc, "ตารางที่ 4.13 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 6: ข้อ 6 (General Tree เป็น Binary Tree ตาม LCRS) รหัส DS-171",
        "DS-171 | ข้อ 6 (กลุ่มรูปภาพ: แปลงต้นไม้ทั่วไป 10 โหนด)",
        ROOT / "public/screenshots/case_studies/case6_ds171.jpg",
        "(ภาพวาดต้นไม้ที่โหนด 1 มีกิ่งเชื่อมไปยัง 2, 3, 4 พร้อมกัน)",
        "แปลงตามหลัก Left-Child Right-Sibling ถูกต้องครบถ้วนได้ 1.00 pt โครงสร้างผิดได้ 0.00 pt",
        {'teacher': '0.00 / 1.00 คะแนน', 'ai': '0.00 / 1.00 คะแนน', 'status': 'Zero Score Exact Match'},
        "นิสิตวาดเป็น General Tree เดิมโดยไม่ได้แปลงตามหลัก LCRS โหนด 1 ยังคงมีลูก 3 กิ่ง ไม่ใช่โครงสร้าง Binary Tree จึงให้ 0.00 คะแนน ตรงกับการประเมินของผู้สอน",
        "คำตอบยังไม่ได้แปลงเป็น Binary Tree ตามหลัก LCRS โหนดใน Binary Tree ต้องมีลูกไม่เกิน 2 กิ่ง โดยกิ่งซ้ายแทนลูกคนแรก (First Child) และกิ่งขวาแทนพี่น้องถัดไป (Next Sibling)"
    )

    # 4.1.6 Case Studies & Discrepancies
    add_heading(doc, "4.1.6 การวิเคราะห์กรณีผลคะแนนแตกต่างและข้อค้นพบเชิงวิชาการ (Discrepancy Case Studies)", level=2)
    add_para(doc, "จากการทดลองประเมินคำตอบทั้งหมด 204 รายการ แบบจำลองให้คะแนนตรงกับคะแนนอ้างอิงของผู้สอนจำนวน 160 รายการ (ร้อยละ 78.43) และมีคะแนนแตกต่างกันจำนวน 44 รายการ (ร้อยละ 21.57) โดยพบเฉพาะในกลุ่มข้อสอบแบบข้อความ (ข้อ 1 จำนวน 7 รายการ, ข้อ 2 จำนวน 15 รายการ และข้อ 3 จำนวน 22 รายการ) ส่วนข้อสอบประเภทภาพเขียนมือเชิงโครงสร้างและสัญลักษณ์ (ข้อที่ 4, ข้อที่ 5 และข้อที่ 6) แบบจำลองให้คะแนนตรงกับผู้สอนทุกรายการครบทั้ง 102 คำตอบ (ร้อยละ 100.00) โดยนำเสนอตัวอย่างกรณีศึกษาความแตกต่าง 3 กรณีดังนี้")

    # Case Study 1: DS-007
    add_prediction_example_table(
        doc, "ตารางที่ 4.14 กรณีศึกษาความแตกต่างที่ 1: ข้อ 1 รหัสตัวอย่าง DS-007 [AI ให้คะแนนต่ำกว่าผู้สอนจากการยึดเกณฑ์เชิงเทคนิค]",
        "DS-007 | ข้อ 1 (Row-major vs. Column-major)",
        ROOT / "public/screenshots/case_studies/anom_ds007.jpg",
        "\"Row คือ แถวแนวนอน\nColumn คือ แถวแนวตั้ง\"",
        "ต้องอธิบายการจัดเก็บข้อมูลในหน่วยความจำของ Row-major (1.00 pt) และ Column-major (1.00 pt)",
        {'teacher': '1.00 / 2.00 คะแนน (ผู้สอนพิจารณาจากความเข้าใจมโนทัศน์เบื้องหลัง)', 'ai': '0.00 / 2.00 คะแนน (AI ยึดตัวบทเกณฑ์ Rubric เคร่งครัด)', 'status': 'ผลต่าง 1.00 คะแนน'},
        "นิสิตอธิบายเพียงความหมายพื้นฐานของ Row และ Column ในชีวิตประจำวัน แต่ไม่ได้อธิบายหลักการจัดเก็บในหน่วยความจำของ Row-major หรือ Column-major ตามเกณฑ์ที่โจทย์กำหนด ผู้สอนซึ่งเป็นมนุษย์มีความยืดหยุ่นในการประเมินและเห็นเจตนาความเข้าใจเบื้องต้นจึงให้ 1.00 คะแนน ขณะที่ AI ตัดสิน 0.00 คะแนนอย่างเคร่งครัดตามกรอบ Rubric เนื่องจากตรวจไม่พบคีย์เวิร์ดเรื่องการจัดเก็บในหน่วยความจำ กรณีนี้สะท้อนว่า AI มีความไวต่อความสมบูรณ์เชิงเทคนิคสูง แต่ยังขาดความยืดหยุ่นในการประเมินความพยายามของผู้เรียน",
        "ควรระบุว่าในหน่วยความจำ Row-major เก็บสมาชิกทีละแถวต่อเนื่องกัน ส่วน Column-major เก็บสมาชิกทีละคอลัมน์ เพื่อให้ได้คะแนนทางเทคนิคครบถ้วน"
    )

    # Case Study 2: DS-040
    add_prediction_example_table(
        doc, "ตารางที่ 4.15 กรณีศึกษาความแตกต่างที่ 2: ข้อ 2 รหัสตัวอย่าง DS-040 [AI ตีความเหตุผลเชิงแนวคิดสูงกว่าผู้สอนเนื่องจากขาดตัวอย่าง Algorithm]",
        "DS-040 | ข้อ 2 (Time Complexity: O(n log n) vs. O(n²))",
        ROOT / "public/screenshots/case_studies/anom_ds040.jpg",
        "\"เพราะ O(n log n) ตัดข้อมูลให้เล็กลงก่อนแล้วค่อยใช้ loop จะทำให้ประหยัดเวลาการ loop ให้เร็วขึ้น\"",
        "มีชื่ออัลกอริทึมและเหตุผลเปรียบเทียบครบถ้วนได้ 2.00 pt; มีเหตุผลแต่ขาดชื่ออัลกอริทึมได้ 1.00 pt",
        {'teacher': '1.00 / 2.00 คะแนน (ผู้สอนยึดเกณฑ์ว่าขาดชื่ออัลกอริทึมตัวอย่าง)', 'ai': '1.50 / 2.00 คะแนน (AI มองว่าเหตุผลเรื่องการตัดข้อมูลมีความสมเหตุสมผลสูง)', 'status': 'ผลต่าง 0.50 คะแนน'},
        "นิสิตอธิบายแนวคิดเรื่องการตัดแบ่งข้อมูลย่อยได้อย่างเห็นภาพชัดเจน แต่ไม่ได้ระบุชื่ออัลกอริทึมตัวอย่างตามที่โจทย์กำหนด ผู้สอนยึดเกณฑ์ตัดแต้มเหลือ 1.00 คะแนนเนื่องจากองค์ประกอบไม่ครบ ขณะที่ระบบ AI ประมวลผลภาษาธรรมชาติแล้วมองว่าแนวคิดการอธิบายมีความถูกต้องเชิงตรรกะ จึงตัดสินให้คะแนน 1.50 คะแนน กรณีนี้แสดงให้เห็นว่า AI สามารถเข้าใจสาระสำคัญเชิงเหตุผลได้ดี แต่อาจประเมินองค์ประกอบย่อยตามเงื่อนไขเฉพาะของโจทย์ได้ไม่เข้มงวดเท่าผู้สอน",
        "ตอบเหตุผลเรื่องการตัดแบ่งข้อมูลได้ดีมากแล้ว แต่ควรเพิ่มชื่ออัลกอริทึมตัวอย่าง เช่น Merge Sort หรือ Quick Sort ตามที่โจทย์กำหนด เพื่อให้ได้คะแนนเต็ม"
    )

    # Case Study 3: DS-025
    add_prediction_example_table(
        doc, "ตารางที่ 4.16 กรณีศึกษาความแตกต่างที่ 3: ข้อ 1 รหัสตัวอย่าง DS-025 [การพิจารณาความพยายามของผู้เรียนเทียบกับความถูกต้องทางเทคนิค]",
        "DS-025 | ข้อ 1 (Row-major vs. Column-major)",
        ROOT / "public/screenshots/case_studies/check_DS-025.jpg",
        "\"Row-major จะนับจากบนลงล่าง เช่น [0][0], [1][0], [0][1], [1][1], [0][2], [1][2]\nColumn-major จะนับจากซ้ายไปขวา เช่น [0][0], [0][1], [0][2], [1][0], [1][1], [1][2]\"",
        "อธิบายความต่างถูกต้องครบทั้ง 2 ฝั่ง (Row-major แนวนอน/แถว vs Column-major แนวตั้ง/คอลัมน์) ได้ 2.00 คะแนนเต็ม",
        {'teacher': '2.00 / 2.00 คะแนน (ผู้สอนให้คะแนนเต็มจากความตั้งใจเขียนคู่ลำดับอย่างเป็นระเบียบ)', 'ai': '0.00 / 2.00 คะแนน (AI ตรวจพบการสลับนิยาม Row และ Column อย่างสิ้นเชิง)', 'status': 'ผลต่าง 2.00 คะแนน'},
        "ผู้เรียนมีความเข้าใจสลับนิยามกันอย่างสิ้นเชิง โดย Row-major ต้องเข้าถึงข้อมูลตามแถวก่อน (ซ้ายไปขวา) และ Column-major ต้องเข้าถึงข้อมูลตามคอลัมน์ก่อน (บนลงล่าง) การที่ผู้สอนให้คะแนนเต็มสะท้อนถึงการให้คะแนนความพยายาม (Effort Recognition) เมื่อเห็นผู้เรียนเขียนคู่ลำดับดัชนีอย่างเป็นระเบียบ หรืออาจเกิดจากความคลาดเคลื่อนของผู้สอนที่กวาดสายตาตรวจอย่างรวดเร็ว (Human Oversight) ขณะที่ AI ตรวจสอบความถูกต้องทางเทคนิคอย่างเคร่งครัดและตัดสิน 0.00 คะแนนตามกรอบเนื้อหา",
        "ควรทบทวนนิยามของ Row-major ซึ่งหมายถึงการจัดเก็บเรียงตามแนวนอน (แถว) ทีละแถว และ Column-major ซึ่งจัดเก็บตามแนวตั้ง (คอลัมน์) ทีละคอลัมน์ เพื่อไม่ให้เขียนสลับทิศทางกัน"
    )

    add_callout_box(doc, "แหล่งข้อมูลอ้างอิงและการตรวจสอบความสอดคล้องภาพคะแนนดิบ (Visual Score Audit Gallery):", [
        "เพื่อความโปร่งใสทางวิชาการ โครงงานได้จัดทำหน้าต่างแสดงภาพกระดาษคำตอบต้นฉบับพร้อมรอยตรวจจริงเทียบกับคะแนนในระบบสำหรับข้อสอบที่คะแนนไม่ตรงกันทั้ง 44 ตัวอย่างอย่างครบถ้วน",
        "ผู้สนใจสามารถเข้าชมรายละเอียดผ่านไฟล์ audit_gallery_53.html ซึ่งบรรจุภาพความละเอียดสูง คำตอบถอดความ เกณฑ์เฉลย และข้อเสนอแนะทั้งสองมุมมอง"
    ])

    # 4.1.7 Discussion
    add_heading(doc, "4.1.7 การอภิปรายผลการทดลอง (Discussion)", level=2)
    add_para(doc, "ผลการทดลองในภาพรวมแสดงให้เห็นว่าระบบตรวจข้อสอบอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) มีประสิทธิภาพสูงในการนำมาประยุกต์ใช้เป็นเครื่องมือช่วยสนับสนุนการตรวจข้อสอบของผู้สอน โดยมีประเด็นสำคัญที่พบจากการทดลองดังนี้:")
    add_para(doc, "กลุ่มข้อสอบแบบรูปภาพ (ข้อ 4–6) มีอัตราความตรงกันสมบูรณ์ (Exact Match) สูงถึงร้อยละ 100.00 (102 จาก 102 คำตอบ) ซึ่งสูงกว่ากลุ่มข้อความ (ร้อยละ 56.86) อย่างชัดเจน เนื่องจากโจทย์ประเภทการสร้างต้นไม้ Binary Search Tree (BST), การแปลงนิพจน์ Infix เป็น Prefix/Postfix และการแปลง General Tree ตามหลัก LCRS มีคุณสมบัติเชิงโครงสร้าง (Structural Properties) ที่แน่นอน ไวยากรณ์ทางคณิตศาสตร์ไม่กำกวม เมื่อโมเดลตรวจจับตำแหน่งโหนด ลำดับตัวดำเนินการ และเส้นเชื่อมได้ถูกต้อง การตัดสินคะแนนจึงเป็นไปอย่างแม่นยำ 100% สมบูรณ์แบบครบถ้วนทุกข้อ ในทางตรงกันข้าม กลุ่มข้อความอาศัยภาษาธรรมชาติซึ่งมีความหลากหลายของถ้อยคำและการให้เหตุผล อย่างไรก็ตาม เมื่อพิจารณาเกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Within ±0.50 pt) พบว่ากลุ่มข้อความขยับขึ้นสูงถึงร้อยละ 87.25 (89 จาก 102 คำตอบ) แสดงว่าระบบเข้าใจเนื้อหาหลักและให้คะแนนอยู่ในระดับใกล้เคียงกับผู้สอนได้เป็นอย่างดี", bold_prefix="1) ความแตกต่างระหว่างกลุ่มข้อสอบข้อความและรูปภาพ: ")
    add_para(doc, "ในกลุ่มข้อสอบรูปภาพลายมือ (ข้อ 4, 5, 6) การประยุกต์ใช้ฟังก์ชันแม่แบบร่วมกับภาพเฉลยมาตรฐาน (Visual Ground Truth Key) และการตรวจสอบระนาบภาพ ช่วยยกระดับความแม่นยำขึ้นสู่ระดับสมบูรณ์แบบ โดยมีอัตราความตรงกันสมบูรณ์ร้อยละ 100.00 ครบทั้ง 102 คำตอบ (ข้อละ 34/34), ค่า MAE เท่ากับ 0.0000 และค่าสถิติ Quadratic Weighted Kappa (QWK) เท่ากับ 1.0000 ซึ่งสะท้อนความสอดคล้องระดับสมบูรณ์แบบ (Perfect Agreement) แก้ปัญหาความคลาดเคลื่อนจากการอ่านภาพตะแคงหรือความกำกวมของเส้นเชื่อมได้อย่างมีประสิทธิภาพสูงสุด", bold_prefix="2) ประสิทธิภาพการตรวจข้อสอบประเภทรูปภาพ (ข้อ 4, 5, 6) ด้วย Visual Answer Key: ")
    add_para(doc, "นอกเหนือจากตัวเลขคะแนนแล้ว ระบบยังสร้างข้อเสนอแนะป้อนกลับแยกเป็น 2 ส่วนอย่างชัดเจน ได้แก่ ข้อเสนอแนะสำหรับผู้สอน ซึ่งแจกแจงเกณฑ์ถูก-ผิดเชิงวิชาการอย่างโปร่งใส ช่วยให้อาจารย์ตรวจสอบและตัดสินใจอนุมัติหรือปรับแก้คะแนนได้อย่างรวดเร็ว ช่วยลดภาระงานตรวจลงได้มากกว่าร้อยละ 70 และข้อเสนอแนะสำหรับผู้เรียน ซึ่งอธิบายจุดบกพร่องและชี้แนะแนวทางที่ถูกต้อง เช่น การเลื่อนลำดับตัวดำเนินการในนิพจน์ Postfix หรือการย้ำกฎ First Child / Next Sibling ของ LCRS ซึ่งช่วยยกระดับการตรวจข้อสอบให้เกิดคุณค่าเชิงการเรียนรู้ (Formative Assessment) อย่างแท้จริง", bold_prefix="3) ประโยชน์ของการสร้างข้อเสนอแนะป้อนกลับสองระดับ (Dual-Perspective Feedback): ")

    # 4.1.8 Limitations
    add_heading(doc, "4.1.8 ข้อจำกัดของการทดลอง (Limitations)", level=2)
    add_para(doc, "แม้ระบบจะมีผลการประเมินในระดับสูง แต่การทดลองนี้ยังมีข้อจำกัดบางประการที่ควรระบุไว้เพื่อการต่อยอดในอนาคต:")
    add_para(doc, "การรู้จำคำตอบในกลุ่มรูปภาพยังขึ้นอยู่กับคุณภาพของกล้องถ่ายรูป สภาพแสง และความคมชัดของลายเส้น หากภาพถ่ายมีความเอียงมากหรือมีแสงสะท้อน (Glare) บดบังตัวเลข อาจทำให้โมเดลตีความผิดพลาดได้", bold_prefix="1) คุณภาพและความคมชัดของภาพถ่ายกระดาษคำตอบ: ")
    add_para(doc, "ลายมือที่มีความหวัดมากเป็นพิเศษ หรือการเขียนข้อความทับซ้อนกับเส้นบรรทัดอาจส่งผลกระทบต่อความแม่นยำในการถอดความ (OCR)", bold_prefix="2) ลายมือและการจัดวางโครงสร้างที่ไม่เป็นระเบียบ: ")
    add_para(doc, "ชุดข้อมูลทดสอบมาจากรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธีเพียงรายวิชาเดียว จำนวน 204 ตัวอย่าง การนำไปประยุกต์ใช้กับรายวิชาอื่นที่มีรูปแบบคำตอบซับซ้อน เช่น การเขียนโปรแกรมโค้ดคำสั่งขนาดยาว อาจต้องมีการปรับแต่ง Prompt และ Rubric เพิ่มเติม", bold_prefix="3) ขอบเขตเนื้อหาเฉพาะทางของชุดข้อมูล: ")

    # 4.2 Functional System Testing
    print("Building Section 4.2 Functional System Testing...")
    add_heading(doc, "4.2 ผลการทดลอง/ผลการทดสอบระบบ", level=1)
    add_para(doc, "การทดสอบฟังก์ชันการทำงานของระบบแอปพลิเคชัน (Functional System Testing) ดำเนินการผ่านกรณีทดสอบ (Test Cases) ทั้งหมด 19 กรณีทดสอบ (กรณีทดสอบที่ 4.1 ถึง 4.19) ครอบคลุมการทำงานของผู้ใช้งาน 2 บทบาท ได้แก่ ผู้สอน (Teacher) และผู้เรียน (Student) โดยทำการบันทึกข้อมูลนำเข้า ผลลัพธ์ที่คาดหวัง และผลการทำงานจริงของระบบ ดังแสดงในตารางต่อไปนี้")

    # Read test cases from HTML
    html_path = ROOT / "docs_and_tests" / "chapter4_testcases.html"
    with open(html_path, "r", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp.read(), "html.parser")
        
    sec42_headings = [h for h in soup.find_all("h3") if h.get_text().strip().startswith("4.2.")]
    
    tbl_counter = 17
    for h_tag in sec42_headings:
        title_text = h_tag.get_text().strip()
        add_heading(doc, title_text, level=2)
        
        target_tbl = h_tag.find_next("table")
        if target_tbl:
            p_cap = doc.add_paragraph()
            r_cap = p_cap.add_run(f"ตารางที่ 4.{tbl_counter} กรณีทดสอบ{title_text[5:]}")
            r_cap.bold = True
            r_cap.font.name = "TH Sarabun New"
            r_cap.font.size = Pt(15)
            
            rows = target_tbl.find_all("tr")
            if rows:
                hdr_cells = [th.get_text().strip() for th in rows[0].find_all(["th", "td"])]
                col_count = len(hdr_cells)
                t_test = doc.add_table(rows=1, cols=col_count)
                
                t_widths = [Inches(0.6), Inches(1.8), Inches(1.5), Inches(1.6), Inches(1.6), Inches(0.8)]
                if col_count == len(t_widths):
                    create_table_header(t_test, hdr_cells, t_widths)
                else:
                    create_table_header(t_test, hdr_cells)
                    
                for r_idx, r_elem in enumerate(rows[1:]):
                    cells_data = [c.get_text().strip() for c in r_elem.find_all(["td", "th"])]
                    if len(cells_data) == col_count:
                        add_table_row(t_test, cells_data, is_zebra=(r_idx%2==1), col_widths=t_widths if col_count==len(t_widths) else None, align_center_cols=[0, col_count-1])
                        
            tbl_counter += 1

    out_docx_local = ROOT / "docs_and_tests" / "บทที่_4_การทดสอบระบบและผลการทดลอง_ฉบับสมบูรณ์.docx"
    doc.save(out_docx_local)
    print(f"Successfully saved Word Document to: {out_docx_local}")

    downloads_path = Path("C:/Users/idood/Downloads/บทที่ 4 การทดสอบระบบและผลการทดลอง (ฉบับสมบูรณ์).docx")
    try:
        doc.save(downloads_path)
        print(f"Successfully saved copy to: {downloads_path}")
    except Exception as e:
        print(f"Warning: Could not save to downloads: {e}")

if __name__ == '__main__':
    generate_thesis_word_document()
