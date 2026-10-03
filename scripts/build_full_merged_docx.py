# -*- coding: utf-8 -*-
"""
Full Merger Script for LLM-AutoScore Thesis Document:
1. Copies base template: docs_and_tests/LLMs_Auto_Score_Systems_Pro1_1-3.docx -> LLMs_Auto_Score_Systems_Pro2_1-5.docx
2. Removes preliminary 'เอกสารอ้างอิง' and trailing blank paragraphs from end of Chapter 3.
3. Appends Chapter 4: ผลการทดสอบและการประเมินระบบ
   - Preserves exact Heading 1, 2, 3 hierarchy and formatting matching base template and MSU CS thesis standards
   - Automatically maintains Word multi-level list numbering (บทที่ 4, 4.1, 4.1.1... 4.2, 4.2.1...)
   - Implements native Word SEQ fields for Table of Tables & Table of Figures integration
   - Fixed-layout table builder (add_table_robust_fixed) with explicit tblGrid, tcW, cantSplit, tblHeader, and #D9D9D9 shading
   - Section 4.1 contains all 10 tables (Tables 4.1 to 4.10) and Figures 4.1 to 4.3 from HTML
   - Section 4.2 contains all 19 functional test cases (Tables 4.11 to 4.29) and Figures 4.4 to 4.13
   - Unified narrative paragraphs per test case with standard 1.27 cm indent and single line spacing
   - Perfect 1-to-1 match between text table references (ตารางที่ 4.xx) and table caption numbers
4. Appends Chapter 5: สรุปผลและข้อเสนอแนะ
   - Sections 5.1 (สรุปผลและอภิปรายผล), 5.2 (ปัญหาและอุปสรรค), 5.3 (ข้อเสนอแนะ)
5. Appends เอกสารอ้างอิง (References) using Header 1 No Chaper with 1.0 cm hanging indent
6. Appends ภาคผนวก (Appendices):
   - Appendix Divider (ภาคผนวก)
   - ภาคผนวก ก: คู่มือการใช้งานระบบ (ก.1–ก.10) with complete screenshots
   - ภาคผนวก ข: ข้อมูลประกอบการประเมินระบบ with dataset structure and full official rubrics (Q1–Q6)
7. Appends บทความวิจัย (Research Article in official MSU CS Department format)
8. Automates Microsoft Word COM to update all TOCs, TOFs, TOTs, save DOCX, and export PDF.
"""

import sys
import re
import shutil
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
INPUT_DOCX = ROOT / "docs_and_tests" / "LLMs_Auto_Score_Systems_Pro1_1-3.docx"
OUTPUT_DOCX = ROOT / "docs_and_tests" / "LLMs_Auto_Score_Systems_Pro2_1-5.docx"
OUTPUT_PDF = ROOT / "docs_and_tests" / "LLMs_Auto_Score_Systems_Pro2_1-5.pdf"
HTML_FILE = ROOT / "docs_and_tests" / "chapter4_testcases.html"

def add_table_robust_fixed(doc, headers, body_rows, col_widths_cm, col0_is_header=True):
    """
    Creates a rock-solid Word table with fixed layout, explicit w:tblGrid,
    per-cell w:tcW, w:cantSplit on every row, and w:tblHeader on the header row.
    Prevents Word from auto-squishing columns.
    """
    num_cols = len(col_widths_cm)
    num_rows = len(body_rows) + (1 if headers else 0)
    
    t = doc.add_table(rows=num_rows, cols=num_cols)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    t.allow_autofit = False
    
    tblPr = t._tbl.tblPr
    tblLayout = parse_xml(r'<w:tblLayout xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="fixed"/>')
    tblPr.append(tblLayout)
    
    tblGrid = OxmlElement('w:tblGrid')
    for w_cm in col_widths_cm:
        w_dxa = int(w_cm * 567.0)
        gridCol = parse_xml(f'<w:gridCol xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:w="{w_dxa}"/>')
        tblGrid.append(gridCol)
    t._tbl.append(tblGrid)
    
    row_offset = 0
    if headers:
        trPr0 = t.rows[0]._tr.get_or_add_trPr()
        trPr0.append(OxmlElement('w:tblHeader'))
        trPr0.append(OxmlElement('w:cantSplit'))
        for c_idx, h_text in enumerate(headers):
            cell = t.cell(0, c_idx)
            w_dxa = int(col_widths_cm[c_idx] * 567.0)
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:tcW xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:w="{w_dxa}" w:type="dxa"/>'))
            tcPr.append(parse_xml(f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="clear" w:color="auto" w:fill="D9D9D9"/>'))
            
            tcMar = parse_xml(r'<w:tcMar xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>')
            tcPr.append(tcMar)
            
            p = cell.paragraphs[0]
            p.text = h_text
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            for r in p.runs:
                r.font.name = 'TH Sarabun New'
                r.font.size = Pt(14)
                r.font.color.rgb = RGBColor(0, 0, 0)
                r.bold = True
        row_offset = 1
        
    for r_idx, r_data in enumerate(body_rows):
        row = t.rows[r_idx + row_offset]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        for c_idx, val in enumerate(r_data):
            if c_idx >= num_cols:
                continue
            cell = row.cells[c_idx]
            w_dxa = int(col_widths_cm[c_idx] * 567.0)
            tcPr = cell._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:tcW xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:w="{w_dxa}" w:type="dxa"/>'))
            
            # Col 0 shading if requested
            if c_idx == 0 and col0_is_header:
                tcPr.append(parse_xml(f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="clear" w:color="auto" w:fill="D9D9D9"/>'))
            
            tcMar = parse_xml(r'<w:tcMar xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>')
            tcPr.append(tcMar)
            
            p = cell.paragraphs[0]
            p.text = val
            is_pass = val in ["ผ่าน", "ไม่ผ่าน"]
            is_col0 = (c_idx == 0 and col0_is_header)
            
            if is_pass:
                align = WD_ALIGN_PARAGRAPH.CENTER
            elif is_col0 and len(val) <= 10:
                align = WD_ALIGN_PARAGRAPH.CENTER
            else:
                align = WD_ALIGN_PARAGRAPH.LEFT
                
            p.alignment = align
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            for r in p.runs:
                r.font.name = 'TH Sarabun New'
                r.font.size = Pt(14)
                r.font.color.rgb = RGBColor(0, 0, 0)
                r.bold = False
    return t

def add_body_p(doc, text="", bold=False, first_indent=Cm(1.27), space_before=Pt(0), space_after=Pt(4), align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.style = 'Normal'
    p.alignment = align
    if first_indent:
        p.paragraph_format.first_line_indent = first_indent
    p.paragraph_format.space_before = space_before
    p.paragraph_format.space_after = space_after
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    run.font.name = 'TH Sarabun New'
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.bold = bold
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph(text, style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(14)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = 'TH Sarabun New'
        r.font.size = Pt(18)
        r.font.color.rgb = RGBColor(0, 0, 0)
        r.bold = True
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph(text, style='Heading 2')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = 'TH Sarabun New'
        r.font.size = Pt(16)
        r.font.color.rgb = RGBColor(0, 0, 0)
        r.bold = True
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph(text, style='Heading 3')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = 'TH Sarabun New'
        r.font.size = Pt(16)
        r.font.color.rgb = RGBColor(0, 0, 0)
        r.bold = False
    return p

def add_heading_unchaptered(doc, text, font_size=Pt(20), align=WD_ALIGN_PARAGRAPH.CENTER):
    p = doc.add_paragraph(text, style='Header 1 No Chaper')
    p.alignment = align
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(14)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = 'TH Sarabun New'
        r.font.size = font_size
        r.font.color.rgb = RGBColor(0, 0, 0)
        r.bold = True
    return p

def add_table_caption(doc, text):
    p = doc.add_paragraph(style='CaptionTable')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    m = re.match(r'^(ตารางที่\s*[\w\.\(\)]+)\s*(.*)$', text)
    if m:
        prefix, desc = m.group(1), m.group(2)
        r1 = p.add_run(prefix)
        r1.font.name = 'TH Sarabun New'
        r1.font.size = Pt(16)
        r1.font.color.rgb = RGBColor(0, 0, 0)
        r1.bold = True
        if desc:
            r2 = p.add_run(" " + desc)
            r2.font.name = 'TH Sarabun New'
            r2.font.size = Pt(16)
            r2.font.color.rgb = RGBColor(0, 0, 0)
            r2.bold = False
    else:
        r = p.add_run(text)
        r.font.name = 'TH Sarabun New'
        r.font.size = Pt(16)
        r.font.color.rgb = RGBColor(0, 0, 0)
        r.bold = False
    return p

def add_table_caption_with_seq(doc, desc_text, table_num=""):
    """
    Creates a native Word caption linked to the 'ตารางที่' sequence so Word's
    Table of Tables automatically updates it with page numbers.
    Only 'ตารางที่ 4.X' is BOLD. The description text is NOT BOLD.
    """
    p = doc.add_paragraph(style='CaptionTable')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    
    r1 = parse_xml(r'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t xml:space="preserve">ตารางที่ </w:t></w:r>')
    fld1 = parse_xml(r'<w:fldSimple xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:instr=" STYLEREF 1 \s "><w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/><w:noProof/></w:rPr><w:t>4</w:t></w:r></w:fldSimple>')
    r2 = parse_xml(r'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t>.</w:t></w:r>')
    fld2 = parse_xml(f'<w:fldSimple xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:instr=" SEQ ตารางที่ \\* ARABIC \\s 1 "><w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/><w:noProof/></w:rPr><w:t>{table_num}</w:t></w:r></w:fldSimple>')
    r3 = parse_xml(f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b w:val="0"/><w:bCs w:val="0"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t xml:space="preserve"> {desc_text}</w:t></w:r>')
    
    p._p.append(r1)
    p._p.append(fld1)
    p._p.append(r2)
    p._p.append(fld2)
    p._p.append(r3)
    return p

def add_subtable_caption_with_seq(doc, sub_letter, desc_text, table_num="", is_first=False):
    """
    Creates a caption for sub-tables e.g. 'ตารางที่ 4.7 (ก) กรณีศึกษาที่ 1: ...'
    Only 'ตารางที่ 4.7 (ก)' is BOLD. The description is NOT BOLD.
    If is_first=True, advances SEQ 'ตารางที่'. If False, uses SEQ \\c so table numbering does not jump.
    """
    p = doc.add_paragraph(style='CaptionTable')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    
    r1 = parse_xml(r'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t xml:space="preserve">ตารางที่ </w:t></w:r>')
    fld1 = parse_xml(r'<w:fldSimple xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:instr=" STYLEREF 1 \s "><w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/><w:noProof/></w:rPr><w:t>4</w:t></w:r></w:fldSimple>')
    r2 = parse_xml(r'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t>.</w:t></w:r>')
    
    seq_instr = r' SEQ ตารางที่ \* ARABIC \s 1 ' if is_first else r' SEQ ตารางที่ \c '
    fld2 = parse_xml(f'<w:fldSimple xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:instr="{seq_instr}"><w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/><w:noProof/></w:rPr><w:t>{table_num}</w:t></w:r></w:fldSimple>')
    
    r_sub = parse_xml(f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t xml:space="preserve"> ({sub_letter})</w:t></w:r>')
    
    r_desc = parse_xml(f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b w:val="0"/><w:bCs w:val="0"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr><w:t xml:space="preserve"> {desc_text}</w:t></w:r>')
    
    p._p.append(r1)
    p._p.append(fld1)
    p._p.append(r2)
    p._p.append(fld2)
    p._p.append(r_sub)
    p._p.append(r_desc)
    return p

def add_table_continuation_caption(doc, table_num_str, title_text):
    """
    Creates a continuation caption e.g. 'ตารางที่ 4.16 การทดสอบแก้ไขข้อมูลโปรไฟล์ (ต่อ)'
    Only 'ตารางที่ 4.16' is BOLD. 'การทดสอบ... (ต่อ)' is NOT BOLD.
    """
    p = doc.add_paragraph(style='CaptionTable')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r_prefix = p.add_run(f"ตารางที่ {table_num_str} ")
    r_prefix.font.name = 'TH Sarabun New'
    r_prefix.font.size = Pt(16)
    r_prefix.font.color.rgb = RGBColor(0, 0, 0)
    r_prefix.bold = True
    r_title = p.add_run(f"{title_text} (ต่อ)")
    r_title.font.name = 'TH Sarabun New'
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = RGBColor(0, 0, 0)
    r_title.bold = False
    return p

def add_case_study_table_clean(doc, rows_data, image_path=None, image_caption=None):
    """
    Renders a 2-column case study table:
    Column 0: Label (width 4.0 cm) - regular font, no gray background
    Column 1: Value (width 11.8 cm) - regular font, left aligned
    If image_path is provided, inserts image in the corresponding row.
    """
    tbl = doc.add_table(rows=0, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    col_widths = [Cm(4.0), Cm(11.8)]
    
    for row_item in rows_data:
        label = row_item[0]
        val = row_item[1]
        row = tbl.add_row()
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(r'<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
        
        # Col 0: Label
        c0 = row.cells[0]
        c0.width = col_widths[0]
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p0.paragraph_format.first_indent = 0
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        r0.font.name = 'TH Sarabun New'
        r0.font.size = Pt(16)
        r0.font.color.rgb = RGBColor(0, 0, 0)
        r0.bold = False
        
        # Col 1: Value
        c1 = row.cells[1]
        c1.width = col_widths[1]
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.first_indent = 0
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        
        if ("ภาพ" in label or "รูป" in label) and image_path and Path(image_path).exists():
            r_img = p1.add_run()
            r_img.add_picture(str(image_path), width=Cm(10.5))
            if image_caption:
                p_cap = c1.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.first_indent = 0
                p_cap.paragraph_format.space_before = Pt(2)
                p_cap.paragraph_format.space_after = Pt(2)
                r_cap = p_cap.add_run(image_caption)
                r_cap.font.name = 'TH Sarabun New'
                r_cap.font.size = Pt(14)
                r_cap.font.color.rgb = RGBColor(80, 80, 80)
        else:
            r1 = p1.add_run(val)
            r1.font.name = 'TH Sarabun New'
            r1.font.size = Pt(16)
            r1.font.color.rgb = RGBColor(0, 0, 0)
            r1.bold = False
        
        # Clean borders
        for cell in (c0, c1):
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                r'<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                r'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
                r'<w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
                r'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
                r'<w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
                r'</w:tcBorders>'
            )
            tcPr.append(tcBorders)
    
    # Spacing paragraph after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)
    p_after.paragraph_format.first_indent = 0
    return tbl

def add_figure_caption_with_seq(doc, desc_text, fig_num=""):
    """
    Creates a native Word caption linked to the 'รูปที่' sequence so Word's
    Table of Figures automatically updates it with page numbers.
    Figure caption is NOT bold as per thesis guidelines.
    """
    p = doc.add_paragraph(style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    
    r1 = parse_xml(r'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b w:val="0"/><w:bCs w:val="0"/><w:sz w:val="30"/><w:szCs w:val="30"/></w:rPr><w:t xml:space="preserve">รูปที่ </w:t></w:r>')
    fld1 = parse_xml(r'<w:fldSimple xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:instr=" STYLEREF 1 \s "><w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b w:val="0"/><w:bCs w:val="0"/><w:sz w:val="30"/><w:szCs w:val="30"/><w:noProof/></w:rPr><w:t>4</w:t></w:r></w:fldSimple>')
    r2 = parse_xml(r'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b w:val="0"/><w:bCs w:val="0"/><w:sz w:val="30"/><w:szCs w:val="30"/></w:rPr><w:t>.</w:t></w:r>')
    fld2 = parse_xml(f'<w:fldSimple xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:instr=" SEQ รูปที่ \\* ARABIC \\s 1 "><w:r><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b w:val="0"/><w:bCs w:val="0"/><w:sz w:val="30"/><w:szCs w:val="30"/><w:noProof/></w:rPr><w:t>{fig_num}</w:t></w:r></w:fldSimple>')
    r3 = parse_xml(f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/><w:b w:val="0"/><w:bCs w:val="0"/><w:sz w:val="30"/><w:szCs w:val="30"/></w:rPr><w:t xml:space="preserve"> {desc_text}</w:t></w:r>')
    
    p._p.append(r1)
    p._p.append(fld1)
    p._p.append(r2)
    p._p.append(fld2)
    p._p.append(r3)
    return p

def add_figure_caption_simple(doc, text):
    p = doc.add_paragraph(text, style='Caption')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    for r in p.runs:
        r.font.name = 'TH Sarabun New'
        r.font.size = Pt(15)
        r.font.color.rgb = RGBColor(0, 0, 0)
        r.bold = False
    return p

def add_image_centered(doc, img_path, width_cm=12.0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(img_path), width=Cm(min(15.2, width_cm)))
    return p

def build_merged_document():
    print(f"Step 1: Copying {INPUT_DOCX.name} -> {OUTPUT_DOCX.name}")
    shutil.copy2(INPUT_DOCX, OUTPUT_DOCX)

    doc = docx.Document(OUTPUT_DOCX)
    print(f"Loaded template copy: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")

    # Step 2: Remove trailing 'เอกสารอ้างอิง' and its references from end of chapter 3
    ref_idx = None
    for idx, p in enumerate(doc.paragraphs):
        if p.style and p.style.name == 'Header 1 No Chaper' and 'เอกสารอ้างอิง' in p.text:
            ref_idx = idx
            break
    
    if ref_idx is not None:
        print(f"Found 'เอกสารอ้างอิง' at paragraph {ref_idx}. Removing trailing references from end of chapter 3...")
        paras_to_remove = doc.paragraphs[ref_idx:]
        for p in paras_to_remove:
            p._p.getparent().remove(p._p)
        
        while len(doc.paragraphs) > 0 and not doc.paragraphs[-1].text.strip():
            p_last = doc.paragraphs[-1]
            p_last._p.getparent().remove(p_last._p)
        print(f"Cleaned end of Chapter 3. Current paragraph count: {len(doc.paragraphs)}")

    # Parse HTML for Chapter 4 & 5 content
    soup = BeautifulSoup(HTML_FILE.read_text(encoding="utf-8"), 'html.parser')

    # ==========================================
    # CHAPTER 4: ผลการทดสอบและการประเมินระบบ
    # ==========================================
    print("Step 3: Appending Chapter 4...")
    doc.add_page_break()
    add_heading_1(doc, "\nผลการทดสอบและการประเมินระบบ")

    add_body_p(doc, "บทนี้นำเสนอผลการทดสอบและการประเมินระบบให้คะแนนข้อสอบอัตนัยอัตโนมัติด้วยแบบจำลองภาษาขนาดใหญ่ (LLM-AutoScore System) ที่พัฒนาขึ้น โดยแบ่งการประเมินออกเป็น 2 ส่วนหลัก ได้แก่ หัวข้อ 4.1 การประเมินประสิทธิภาพของแบบจำลองในการตรวจข้อสอบอัตนัย และหัวข้อ 4.2 การทดสอบการทำงานของระบบ (Functional Testing) ครอบคลุมการทำงานทุกโมดูลตามขอบเขตของโครงงาน")

    # ------------------------------------------
    # Section 4.1: การประเมินประสิทธิภาพของแบบจำลองในการตรวจข้อสอบ
    # ------------------------------------------
    add_heading_2(doc, "การประเมินประสิทธิภาพของแบบจำลองในการตรวจข้อสอบ")
    add_body_p(doc, "การประเมินส่วนนี้มุ่งศึกษาความแม่นยำและความสอดคล้องระหว่างคะแนนที่ประเมินโดยแบบจำลอง Gemini 3.8 Flash กับคะแนนอ้างอิงจากผู้สอนประจำรายวิชา (Ground Truth) ในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี โดยใช้คำตอบจริงของผู้เรียนจำนวนทั้งสิ้น 204 ตัวอย่าง (34 คน × 6 ข้อ) และไม่เปิดเผยคะแนนอ้างอิงแก่แบบจำลอง")

    # 4.1.1 ข้อมูลที่ใช้ในการประเมิน
    add_heading_3(doc, "ข้อมูลที่ใช้ในการประเมิน")
    add_body_p(doc, "ชุดข้อมูลที่ใช้ในการประเมินประกอบด้วยข้อสอบ 6 ข้อ แบ่งตามรูปแบบคำตอบออกเป็น 2 กลุ่ม ได้แก่ คำตอบแบบข้อความ (ข้อที่ 1–3) จำนวน 102 ตัวอย่าง และคำตอบแบบภาพลายมือเชิงโครงสร้างและสัญลักษณ์ (ข้อที่ 4–6) จำนวน 102 ตัวอย่าง ข้อมูลทั้งหมดนำมาจากกระดาษคำตอบจริงของผู้เรียนในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี รายละเอียดของข้อสอบแสดงในตารางที่ 4.1")

    # Table 4.1
    add_table_caption_with_seq(doc, "ข้อมูลข้อสอบที่ใช้ในการประเมิน", table_num="1")
    t41_headers = ["ข้อที่", "หัวข้อโจทย์", "รูปแบบคำตอบ", "คะแนนเต็ม", "จำนวนคำตอบ"]
    t41_rows = [
        ["1", "Row-major และ Column-major", "ข้อความ", "2", "34"],
        ["2", "ความซับซ้อน O(n log n) และ O(n²)", "ข้อความ", "2", "34"],
        ["3", "Linked List และ Array สำหรับ Stack และ Queue", "ข้อความ", "1", "34"],
        ["4", "การสร้าง Binary Search Tree", "ภาพลายมือเชิงโครงสร้างและสัญลักษณ์", "1", "34"],
        ["5", "การแปลง Infix Expression เป็น Prefix และ Postfix", "ภาพลายมือเชิงโครงสร้างและสัญลักษณ์", "1", "34"],
        ["6", "การแปลง General Tree เป็น Binary Tree", "ภาพลายมือเชิงโครงสร้างและสัญลักษณ์", "1", "34"],
        ["รวม", "ครอบคลุมเนื้อหาโครงสร้างข้อมูลทั้งทฤษฎีและแผนภาพ", "ข้อความ 102 / ภาพลายมือ 102", "8", "204"]
    ]
    add_table_robust_fixed(doc, t41_headers, t41_rows, [1.5, 6.3, 3.2, 2.2, 2.6], col0_is_header=False)

    add_body_p(doc, "สำหรับคำตอบแบบข้อความ ได้ถอดเนื้อหาจากกระดาษคำตอบของผู้เรียนเป็นข้อความโดยคงเนื้อหาเดิม และไม่นำคะแนนหรือรอยตรวจของผู้สอนมาใช้เป็นข้อมูลนำเข้าสำหรับแบบจำลอง ตัวอย่างกระดาษคำตอบต้นฉบับแสดงในรูปที่ 4.1 และข้อมูลหลังถอดเป็นข้อความแสดงในตารางที่ 4.2", space_before=Pt(6))

    # Figure 4.1
    img41_path = ROOT / "docs_and_tests" / "screenshots" / "evaluation_ds084_original_with_score.jpg"
    if img41_path.exists():
        add_image_centered(doc, img41_path, width_cm=10.0)
        add_figure_caption_with_seq(doc, "ตัวอย่างคำตอบต้นฉบับของผู้เรียนที่มีคะแนนผู้สอนก่อนถอดเป็นข้อความ", fig_num="1")

    # Table 4.2
    add_table_caption_with_seq(doc, "ตัวอย่างข้อมูลคำตอบ", table_num="2")
    t42_headers = ["รหัส", "ข้อที่", "คำตอบที่ถอดเป็นข้อความ", "คะแนนผู้สอน"]
    t42_rows = [
        ["DS-084", "3", "การใช้ Link List แทน Array นั้น ข้อดี คือ สามารถเพิ่มและลบได้เรื่อย ๆ เพราะขนาดของ Link List ไม่จำกัดเหมือน Array และเพิ่มหรือลบได้รวดเร็วกว่า Array ข้อเสีย คือ การเข้าถึงและค้นหาข้อมูลทำได้ยากกว่า Array", "0.50"]
    ]
    add_table_robust_fixed(doc, t42_headers, t42_rows, [2.2, 1.6, 9.8, 2.2], col0_is_header=False)

    # Figure 4.2 and Data leakage prevention
    add_body_p(doc, "ก่อนนำกระดาษคำตอบส่งเข้าแบบจำลอง ได้มีการเตรียมข้อมูลโดยลบคะแนนและรอยตรวจเดิมของผู้สอนออกจากภาพคำตอบ เพื่อป้องกันปัญหาการรั่วไหลของข้อมูลเฉลย (Data Leakage) และให้แบบจำลองประเมินจากเนื้อหาคำตอบของผู้เรียนอย่างแท้จริง ดังแสดงในรูปที่ 4.2", space_before=Pt(6))

    img42_path = ROOT / "docs_and_tests" / "screenshots" / "case_studies" / "case4_ds104.jpg"
    if img42_path.exists():
        add_image_centered(doc, img42_path, width_cm=11.0)
        add_figure_caption_with_seq(doc, "ภาพกระดาษคำตอบหลังลบคะแนนเดิมเพื่อใช้ในการทดสอบแบบปิดตา", fig_num="2")

    # 4.1.2 เกณฑ์การให้คะแนนและคะแนนอ้างอิง
    add_heading_3(doc, "เกณฑ์การให้คะแนนและคะแนนอ้างอิง")
    add_body_p(doc, "เกณฑ์การให้คะแนนรายข้อจัดทำขึ้นจากแนวทางการตรวจที่ได้รับจากผู้สอนประจำรายวิชา โดยจำแนกระดับคะแนนและกำหนดประเด็นที่ต้องมีในคำตอบอย่างชัดเจน เพื่อใช้เป็นข้อมูลนำเข้าประกอบคำสั่ง (Prompt) ในการประเมินของแบบจำลอง ดังแสดงในตารางที่ 4.3")

    # Table 4.3
    add_table_caption_with_seq(doc, "สรุปเกณฑ์และระดับคะแนนที่ใช้ตรวจคำตอบแต่ละข้อ", table_num="3")
    t43_headers = ["ข้อที่", "คะแนนเต็ม", "ระดับคะแนนที่กำหนด", "องค์ประกอบที่พิจารณา"]
    t43_rows = [
        ["1", "2", "0, 1 และ 2", "พิจารณาการอธิบาย Row-major และ Column-major แยกส่วนละ 1 คะแนน"],
        ["2", "2", "0, 0.5, 1, 1.5 และ 2", "พิจารณาการเปรียบเทียบความเร็วและการระบุตัวอย่างอัลกอริทึมที่ถูกต้อง"],
        ["3", "1", "0, 0.25, 0.5, 0.75 และ 1", "พิจารณาการระบุความแตกต่างเชิงโครงสร้างและข้อดีข้อเสียอย่างละ 0.5 คะแนน"],
        ["4", "1", "0 และ 1", "ตรวจความถูกต้องของโครงสร้างต้นไม้ค้นหาทวิภาคครบทั้ง 12 โหนด"],
        ["5", "1", "0, 0.5 และ 1", "ตรวจขั้นตอนและผลลัพธ์การแปลง Prefix และ Postfix อย่างละ 0.5 คะแนน"],
        ["6", "1", "0 และ 1", "ตรวจความถูกต้องของการแปลงต้นไม้ทั่วไปเป็นต้นไม้ทวิภาคตามหลัก LCRS ครบ 10 โหนด"]
    ]
    add_table_robust_fixed(doc, t43_headers, t43_rows, [1.5, 2.3, 3.2, 8.8], col0_is_header=False)

    # 4.1.3 วิธีการให้คะแนนด้วย Gemini 3.8 Flash
    add_heading_3(doc, "วิธีการให้คะแนนด้วย Gemini 3.8 Flash")
    add_body_p(doc, "การให้คะแนนใช้ฟังก์ชันตรวจคำตอบแม่แบบเดียวกับที่ระบบใช้ตรวจจริง โดยส่งคำถาม คำตอบ เกณฑ์การให้คะแนน และคำสั่งควบคุมไปยัง Gemini 3.8 Flash ผ่าน Gemini API และกำหนดผลลัพธ์เป็นโครงสร้าง JSON ประกอบด้วยคะแนน (ai_score), เหตุผล (reasoning), ระดับความมั่นใจ (ai_confidence), ข้อเสนอแนะสำหรับผู้สอน (teacher_feedback) และข้อเสนอแนะสำหรับผู้เรียน (student_feedback) ขั้นตอนแสดงในตารางที่ 4.4")

    # Table 4.4
    add_table_caption_with_seq(doc, "ขั้นตอนการให้คะแนนคำตอบด้วย Gemini 3.8 Flash", table_num="4")
    t44_headers = ["ขั้นตอน", "การดำเนินการ"]
    t44_rows = [
        ["1", "เตรียมโจทย์ คำตอบของผู้เรียน คะแนนเต็ม แนวคำตอบ และเกณฑ์การให้คะแนนของข้อนั้น"],
        ["2", "แนบข้อความหรือภาพคำตอบตามรูปแบบข้อมูล และใช้คำสั่งแม่แบบเดียวกันกับคำตอบทั้งหมดภายในข้อเดียวกัน"],
        ["3", "ส่งข้อมูลให้ Gemini 3.8 Flash วิเคราะห์ความถูกต้องตามแนวคำตอบและเกณฑ์ที่กำหนด"],
        ["4", "รับผลลัพธ์ในรูปแบบที่กำหนด ประกอบด้วยคะแนน ระดับความมั่นใจ เหตุผลสำหรับผู้สอน คำแนะนำสำหรับผู้เรียน และข้อความที่แบบจำลองอ่านได้จากภาพ"],
        ["5", "ตรวจสอบความถูกต้องของคะแนนให้อยู่ในช่วง 0 ถึงคะแนนเต็ม และบันทึกผลการประเมินลงในระบบ"]
    ]
    add_table_robust_fixed(doc, t44_headers, t44_rows, [2.0, 13.8], col0_is_header=False)

    # 4.1.4 ตัวชี้วัดที่ใช้ในการประเมิน
    add_heading_3(doc, "ตัวชี้วัดที่ใช้ในการประเมิน")
    add_body_p(doc, "การประเมินประสิทธิภาพการให้คะแนนของแบบจำลองใช้ตัวชี้วัด 3 ค่า ได้แก่ อัตราคะแนนตรงกันสมบูรณ์ (Exact Match) ค่าความคลาดเคลื่อนสัมบูรณ์เฉลี่ย (Mean Absolute Error: MAE) และค่าสัมประสิทธิ์ความสอดคล้องแบบถ่วงน้ำหนักกำลังสอง (Quadratic Weighted Kappa: QWK) โดยเปรียบเทียบคะแนนที่แบบจำลองประเมินกับคะแนนอ้างอิงจากผู้สอนของคำตอบรายการเดียวกัน")

    # Table 4.5
    add_table_caption_with_seq(doc, "ตัวชี้วัดที่ใช้ในการประเมินประสิทธิภาพการให้คะแนน", table_num="5")
    t45_headers = ["ตัวชี้วัด", "วิธีคำนวณ", "ความหมาย"]
    t45_rows = [
        ["Exact Match", "จำนวนคำตอบที่คะแนนจากแบบจำลองเท่ากับคะแนนผู้สอน หารด้วยจำนวนคำตอบทั้งหมด แล้วคูณด้วย 100", "แสดงร้อยละของคำตอบที่ได้คะแนนตรงกันทุกประการ ค่ายิ่งสูงแสดงว่าคะแนนตรงกันมาก"],
        ["MAE", "ผลรวมของค่าสัมบูรณ์ของผลต่างระหว่างคะแนนทั้งสองแหล่ง หารด้วยจำนวนคำตอบทั้งหมด", "แสดงขนาดความคลาดเคลื่อนเฉลี่ยในหน่วยคะแนน ค่าใกล้ 0 แสดงว่าคะแนนแตกต่างกันน้อย"],
        ["QWK", "เปรียบเทียบความไม่สอดคล้องที่สังเกตได้กับความไม่สอดคล้องที่คาดว่าจะเกิดจากความบังเอิญ โดยให้น้ำหนักกำลังสองตามระยะห่างของระดับคะแนน", "แสดงความสอดคล้องของระดับคะแนนโดยคำนึงถึงโอกาสเกิดความตรงกันโดยบังเอิญ และลงโทษกรณีที่คะแนนต่างกันมากหนักกว่ากรณีที่ต่างกันเล็กน้อย"]
    ]
    add_table_robust_fixed(doc, t45_headers, t45_rows, [3.2, 6.6, 6.0], col0_is_header=False)

    # Formula Box
    add_body_p(doc, "สูตรที่ใช้ในการคำนวณ", bold=True, space_before=Pt(6), space_after=Pt(2))
    add_body_p(doc, "Exact Match = (1 ÷ N) × Σᴺᵢ₌₁ I(Hᵢ = Aᵢ) × 100", first_indent=Cm(1.27), space_after=Pt(1))
    add_body_p(doc, "MAE = (1 ÷ N) × Σᴺᵢ₌₁ |Hᵢ − Aᵢ|", first_indent=Cm(1.27), space_after=Pt(1))
    add_body_p(doc, "QWK = 1 − [Σᵢ,ⱼ wᵢⱼOᵢⱼ ÷ Σᵢ,ⱼ wᵢⱼEᵢⱼ]", first_indent=Cm(1.27), space_after=Pt(1))
    add_body_p(doc, "wᵢⱼ = (i − j)² ÷ (K − 1)²", first_indent=Cm(1.27), space_after=Pt(4))

    add_body_p(doc, "กำหนดให้ Hᵢ คือคะแนนอ้างอิงจากผู้สอน Aᵢ คือคะแนนที่แบบจำลองประเมิน และ N คือจำนวนคำตอบที่นำมาประเมิน โดย I(Hᵢ = Aᵢ) มีค่าเท่ากับ 1 เมื่อคะแนนทั้งสองแหล่งตรงกัน และมีค่าเท่ากับ 0 เมื่อคะแนนไม่ตรงกัน สำหรับ QWK กำหนดให้ Oᵢⱼ คือความถี่ที่สังเกตได้เมื่อคะแนนผู้สอนอยู่ในระดับ i และคะแนนแบบจำลองอยู่ในระดับ j ส่วน Eᵢⱼ คือความถี่ที่คาดหมายจากการแจกแจงคะแนนของทั้งสองแหล่ง และ wᵢⱼ คือน้ำหนักความคลาดเคลื่อนแบบกำลังสอง ในการศึกษานี้กำหนด K = 5 ตามจำนวนระดับของสเกลร่วม 0–4 สำหรับทุกข้อ แม้ว่าบางข้อจะมีระดับคะแนนที่ใช้งานจริงเพียงบางระดับ เพื่อรักษาระยะห่างของสัดส่วนคะแนนให้เป็นมาตรฐานเดียวกัน")

    add_body_p(doc, "เนื่องจากข้อสอบแต่ละข้อมีคะแนนเต็มและระดับคะแนนแตกต่างกัน การคำนวณ QWK รายข้อจึงปรับคะแนนด้วยคะแนนเต็มของข้อนั้นให้อยู่ในช่วง 0–1 จากนั้นแปลงเป็นสเกลลำดับร่วม 5 ระดับ ได้แก่ 0, 1, 2, 3 และ 4 ซึ่งสอดคล้องกับสัดส่วนคะแนน 0, 0.25, 0.50, 0.75 และ 1.00 ตามลำดับ โดยกำหนด K = 5 สำหรับทุกข้อ ระดับที่ไม่ปรากฏตามเกณฑ์ของข้อใดจะมีความถี่เป็นศูนย์ แต่ยังคงอยู่ในสเกลร่วมเมื่อคำนวณ QWK ส่วนค่า QWK ภาพรวมคำนวณโดยนำคะแนนทั้ง 204 คำตอบที่แปลงเข้าสเกลเดียวกันมาพิจารณาร่วมกัน วิธีดังกล่าวช่วยรักษาระยะห่างระหว่างระดับคะแนนให้เป็นมาตรฐานเดียวกัน ส่วน Exact Match และ MAE คำนวณจากคะแนนดิบตามคะแนนเต็มของแต่ละข้อ ค่า MAE ในการประเมินรายข้อจึงแสดงในหน่วยคะแนนดิบของข้อนั้นและใช้พิจารณาความคลาดเคลื่อนภายในแต่ละข้อเป็นหลัก ส่วนการเปรียบเทียบข้ามข้อที่มีคะแนนเต็มแตกต่างกันจะพิจารณาค่าที่ปรับตามคะแนนเต็มเพิ่มเติม")

    # 4.1.5 ผลการประเมินรายข้อ
    add_heading_3(doc, "ผลการประเมินรายข้อ")
    add_body_p(doc, "ผลการประเมินรายข้อคำนวณจากคำตอบของผู้เรียนข้อละ 34 คำตอบ โดยเปรียบเทียบคะแนนที่แบบจำลองประเมินกับคะแนนอ้างอิงจากผู้สอนของคำตอบรายการเดียวกัน ตารางที่ 4.6 แสดงจำนวนและร้อยละของคะแนนที่ตรงกัน ค่า MAE, ค่า Normalized MAE (NMAE) และค่า QWK")

    # Table 4.6
    add_table_caption_with_seq(doc, "ผลการประเมินประสิทธิภาพการให้คะแนนจำแนกรายข้อ", table_num="6")
    t46_headers = ["ข้อ", "รูปแบบคำตอบ", "คะแนนเต็ม", "คะแนนตรงกัน", "Exact Match (%)", "MAE", "Normalized MAE (NMAE)", "QWK"]
    t46_rows = [
        ["1", "ข้อความ", "2", "27/34", "79.41", "0.2353", "0.1176", "0.6288"],
        ["2", "ข้อความ", "2", "19/34", "55.88", "0.3088", "0.1544", "0.5783"],
        ["3", "ข้อความ", "1", "12/34", "35.29", "0.2426", "0.2426", "0.5330"],
        ["4", "ภาพลายมือ", "1", "34/34", "100.00", "0.0000", "0.0000", "1.0000"],
        ["5", "ภาพลายมือ", "1", "34/34", "100.00", "0.0000", "0.0000", "1.0000"],
        ["6", "ภาพลายมือ", "1", "34/34", "100.00", "0.0000", "0.0000", "1.0000"],
        ["รวม", "2 รูปแบบ", "8", "160/204", "78.43", "0.1311", "0.0983", "0.8546"]
    ]
    add_table_robust_fixed(doc, t46_headers, t46_rows, [1.2, 2.2, 1.6, 2.2, 2.6, 1.7, 2.3, 2.0], col0_is_header=False)

    add_body_p(doc, "จากตารางที่ 4.6 ข้อสอบประเภทภาพลายมือเชิงโครงสร้างและสัญลักษณ์ในข้อที่ 4–6 ได้แก่ การสร้าง Binary Search Tree, การแปลงนิพจน์ Infix เป็น Prefix/Postfix และการแปลง General Tree เป็น Binary Tree ตามหลัก LCRS มีคะแนนตรงกับผู้สอนสมบูรณ์ครบทั้ง 102 รายการ (คิดเป็นร้อยละ 100.00) ค่า MAE เท่ากับ 0.0000 และ QWK เท่ากับ 1.0000 เนื่องจากคำตอบกลุ่มนี้มีโครงสร้างทางคณิตศาสตร์และขั้นตอนวิธีที่ชัดเจน", space_before=Pt(6))
    add_body_p(doc, "สำหรับคำตอบแบบข้อความ ข้อที่ 1 มีอัตราคะแนนตรงกันสูงที่สุดที่ร้อยละ 79.41 รองลงมาคือข้อที่ 2 ร้อยละ 55.88 และข้อที่ 3 ร้อยละ 35.29 อย่างไรก็ตาม หากพิจารณาเกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (ต่างไม่เกิน ±0.50 คะแนน) พบว่ากลุ่มข้อความมีความสอดคล้องสูงถึงร้อยละ 87.25 เมทริกซ์ความคลาดเคลื่อนในการให้คะแนนรายข้อแสดงในรูปที่ 4.3")

    # Figure 4.3: Confusion Matrix
    img43_path = ROOT / "docs_and_tests" / "screenshots" / "confusion_matrix.png"
    if img43_path.exists():
        add_image_centered(doc, img43_path, width_cm=12.0)
        add_figure_caption_with_seq(doc, "เมทริกซ์ความสับสนของคะแนนผู้สอนและแบบจำลอง แยกรายข้อ", fig_num="3")

    # 4.1.6 การวิเคราะห์ความคลาดเคลื่อนในการให้คะแนน
    add_heading_3(doc, "การวิเคราะห์ความคลาดเคลื่อนในการให้คะแนน")
    add_body_p(doc, "จากการนำคำตอบที่มีคะแนนต่างกันมาวิเคราะห์ร่วมกับเกณฑ์การให้คะแนน พบประเด็นสำคัญที่ส่งผลต่อความคลาดเคลื่อน ได้แก่ การตีความความครบถ้วนของคำตอบ และการให้น้ำหนักคะแนนส่วนย่อย ซึ่งแบบจำลองยึดตามข้อความของเกณฑ์อย่างเคร่งครัด ขณะที่ผู้สอนอาจผ่อนปรนให้คะแนนความพยายามหรืออนุมานความเข้าใจของผู้เรียนจากคำสำคัญ กรณีศึกษาแสดงในตารางที่ 4.7")

    # Table 4.7
    add_table_caption_with_seq(doc, "กรณีศึกษาเปรียบเทียบความคลาดเคลื่อนในการให้คะแนนระหว่างผู้สอนและแบบจำลอง AI (คำตอบประเภทข้อความ)", table_num="7")
    cases_47 = [
        ("กรณีศึกษาที่ 1: การพิจารณาความพยายามของผู้เรียนเทียบกับความถูกต้องทางเทคนิค", [
            ["รหัสตัวอย่าง / โจทย์", "DS-025 | ข้อ 1 (Row-major vs. Column-major) [คะแนนเต็ม 2.00]"],
            ["ข้อความคำตอบของผู้เรียน", '"Row-major จะนับจากบนลงล่าง เช่น [0][0], [1][0], [0][1], [1][1], [0][2], [1][2] Column-major จะนับจากซ้ายไปขวา เช่น [0][0], [0][1], [0][2], [1][0], [1][1], [1][2]"'],
            ["การเปรียบเทียบคะแนน", "คะแนนผู้สอน: 2.00 / 2.00 คะแนน (ให้เต็ม) | คะแนนแบบจำลอง AI: 0.00 / 2.00 คะแนน (ผลต่าง -2.00)"],
            ["คำอธิบาย / การวิเคราะห์", "ผู้เรียนสลับนิยามความหมายระหว่าง Row-major และ Column-major ทำให้แบบจำลองตัดสินว่าคำตอบผิดหลักวิชาการจึงให้ 0.00 คะแนน ขณะที่ผู้สอนให้ 2.00 คะแนนเต็มเนื่องจากมองเห็นความพยายามในการยกตัวอย่างดัชนี (Index)"]
        ]),
        ("กรณีศึกษาที่ 2: ความเคร่งครัดตามเกณฑ์การประเมินเทียบกับความยืดหยุ่นในการให้คะแนน", [
            ["รหัสตัวอย่าง / โจทย์", "DS-056 | ข้อ 2 (Time Complexity) [คะแนนเต็ม 2.00]"],
            ["ข้อความคำตอบของผู้เรียน", '"O(n log n) มีความเร็วมากกว่า O(n^2) เพราะ O(n^2) จะทำการเปรียบเทียบข้อมูลทุกตัว ซึ่งจะช้ากว่า เช่น Bubble sort O(n log n) จะใช้วิธี Divide and Conquer เช่น Merge sort"'],
            ["การเปรียบเทียบคะแนน", "คะแนนผู้สอน: 1.00 / 2.00 คะแนน | คะแนนแบบจำลอง AI: 2.00 / 2.00 คะแนน (ผลต่าง +1.00)"],
            ["คำอธิบาย / การวิเคราะห์", "คำตอบของผู้เรียนระบุชื่ออัลกอริทึมทั้งสองกลุ่มถูกต้อง และระบุหลักการ Divide and Conquer ตรงตามเกณฑ์คะแนนเต็ม 2.00 คะแนนทุกประการ แต่ผู้สอนให้เพียง 1.00 คะแนน"]
        ]),
        ("กรณีศึกษาที่ 3: การประเมินตามองค์ประกอบย่อยเทียบกับความครบถ้วนของคำตอบ", [
            ["รหัสตัวอย่าง / โจทย์", "DS-099 | ข้อ 2 (Time Complexity) [คะแนนเต็ม 2.00]"],
            ["ข้อความคำตอบของผู้เรียน", '"O(n log n) เช่น merge sort เร็วกว่า O(n^2) เช่น bubble sort"'],
            ["การเปรียบเทียบคะแนน", "คะแนนผู้สอน: 1.00 / 2.00 คะแนน | คะแนนแบบจำลอง AI: 1.50 / 2.00 คะแนน (ผลต่าง +0.50)"],
            ["คำอธิบาย / การวิเคราะห์", "ผู้เรียนตอบสั้นโดยระบุชื่ออัลกอริทึมถูกต้องทั้งสองกลุ่มและบอกว่าเร็วกว่า แต่ไม่ได้อธิบายเหตุผลประกอบ"]
        ]),
        ("กรณีศึกษาที่ 4: การอนุมานและตีความความหมายแทนผู้เรียนของแบบจำลอง AI", [
            ["รหัสตัวอย่าง / โจทย์", "DS-005 | ข้อ 3 (Linked List vs Array ใน Stack และ Queue) [คะแนนเต็ม 1.00]"],
            ["ข้อความคำตอบของผู้เรียน", '"Linked List เข้าถึงข้อมูลช้ากว่า Array แต่เพิ่มลบข้อมูลได้เร็วกว่าและปรับขนาดได้ง่ายกว่า Array ขนาดคงที่ เข้าถึงข้อมูลได้เร็ว แต่เพิ่มลบข้อมูลช้า"'],
            ["การเปรียบเทียบคะแนน", "คะแนนผู้สอน: 0.50 / 1.00 คะแนน | คะแนนแบบจำลอง AI: 1.00 / 1.00 คะแนน (ผลต่าง +0.50)"],
            ["คำอธิบาย / การวิเคราะห์", "ผู้เรียนเปรียบเทียบข้อดีข้อเสียระหว่าง Linked List กับ Array ทั่วไป แต่ไม่ได้เชื่อมโยงกับพฤติกรรมของ Stack (LIFO) และ Queue (FIFO) โดยตรง แบบจำลองได้อนุมานเชื่อมโยงความรู้ให้อัตโนมัติ"]
        ])
    ]
    for case_title, case_rows in cases_47:
        add_body_p(doc, case_title, bold=False, first_indent=0, space_before=Pt(6), space_after=Pt(2))
        add_table_robust_fixed(doc, None, case_rows, [3.8, 12.0], col0_is_header=True)

    # 4.1.7 การประเมินความสามารถในการอ่านข้อความลายมือและระบุกรณีที่ควรทบทวน
    add_heading_3(doc, "การประเมินความสามารถของโมเดลในการอ่านข้อความลายมือและระบุกรณีที่ควรทบทวน")
    add_body_p(doc, "การทดลองเพิ่มเติมนี้ประเมินความสามารถของแบบจำลองในการอ่านข้อความลายมือจากภาพคำตอบข้อที่ 3 จำนวน 34 ภาพ ซึ่งประกอบด้วยภาษาไทยและภาษาอังกฤษปะปนกัน เกณฑ์การพิจารณาความเพียงพอของการอ่านแสดงในตารางที่ 4.8")

    # Table 4.8
    add_table_caption_with_seq(doc, "เกณฑ์พิจารณาความเพียงพอของการอ่านข้อความลายมือข้อที่ 3", table_num="8")
    t48_headers = ["ระดับผลการอ่าน", "ความหมาย", "จำนวนภาพ"]
    t48_rows = [
        ["ถูกต้อง", "อ่านสาระที่เกี่ยวข้องครบ โดยไม่มีความผิดพลาดที่เปลี่ยนความหมาย", "16"],
        ["คลาดเคลื่อนเล็กน้อย", "มีคำผิดหรือตกหล่น แต่ไม่เปลี่ยนสาระที่ใช้ให้คะแนน", "15"],
        ["ผิดสาระสำคัญ", "อ่านผิดหรือตกหล่นจนความหมายที่ใช้ให้คะแนนเปลี่ยน", "2"],
        ["ภาพกำกวม", "ผู้ตรวจยังไม่สามารถยืนยันข้อความอ้างอิงจากภาพได้", "1"],
        ["รวม", "ภาพคำตอบลายมือทั้งหมดที่นำมาประเมิน", "34"]
    ]
    add_table_robust_fixed(doc, t48_headers, t48_rows, [3.5, 9.5, 2.8], col0_is_header=False)

    add_body_p(doc, "เมื่อตัดภาพกำกวม 1 ภาพออก แบบจำลองอ่านข้อความได้เพียงพอต่อการตรวจ 31 จาก 33 ภาพ คิดเป็นร้อยละ 93.94 นอกจากนี้ ระบบแจ้งเตือนให้ผู้สอนทบทวน (Review Flags) เมื่อแบบจำลองรายงานความมั่นใจระดับปานกลางหรือต่ำ ผลการประเมินแสดงในตารางที่ 4.9", space_before=Pt(6))

    # Table 4.9
    add_table_caption_with_seq(doc, "ผลการประเมินการระบุกรณีที่ควรทบทวนของผู้สอน (Review Flagging Evaluation)", table_num="9")
    t49_headers = ["รายการตัวชี้วัด", "ผลการประเมิน", "การแปลผล"]
    t49_rows = [
        ["ภาพที่ควรทบทวนตามการจัดกลุ่มเบื้องต้น", "3 / 34 ภาพ (8.82%)", "ภาพที่อ่านผิดสาระสำคัญ (2 ภาพ) และภาพกำกวม (1 ภาพ)"],
        ["ภาพที่ระบบติดธงแจ้งเตือนให้ทบทวน", "8 / 34 ภาพ (23.53%)", "ภาพที่แบบจำลองรายงานความมั่นใจระดับปานกลาง"],
        ["กรณีที่ตรวจจับได้ถูกต้อง (True Positives)", "3 / 3 ภาพ", "ระบบแจ้งเตือนครบทั้ง 3 ภาพที่จัดว่าควรทบทวน"],
        ["อัตราการตรวจจับกรณีผิดพลาด (Review Recall)", "3 / 3 = 100.00%", "ภาพที่จัดว่าควรทบทวนทั้ง 3 ภาพได้รับการแจ้งเตือน"],
        ["อัตราการแจ้งเตือนถูกต้อง (Precision)", "3 / 8 = 37.50%", "ภาพที่แจ้งเตือน 8 ภาพ มี 3 ภาพที่ต้องทบทวนจริง อีก 5 ภาพตรวจได้ปกติ"],
        ["อัตราการหลุดรอด (False Negative Rate)", "0 / 3 = 0.00%", "ไม่มีภาพที่ควรทบทวนหลุดรอดจากการแจ้งเตือน"]
    ]
    add_table_robust_fixed(doc, t49_headers, t49_rows, [5.0, 4.2, 6.6], col0_is_header=False)

    add_body_p(doc, "ตัวอย่างการอ่านข้อความลายมือและการระบุกรณีที่ควรทบทวนในระดับต่างๆ แสดงในตารางที่ 4.10", space_before=Pt(6))

    # Table 4.10
    add_table_caption_with_seq(doc, "ตัวอย่างการอ่านข้อความลายมือและการระบุกรณีที่ควรทบทวน (DS-082, DS-079 และ DS-095)", table_num="10")
    cases_410 = [
        ("กรณีศึกษาที่ 1: การตรวจจับข้อผิดพลาดในสาระสำคัญจากลายมือหวัด (รหัสตัวอย่าง DS-082)", [
            ["รหัสตัวอย่าง / โจทย์", "DS-082 | ข้อ 3 (ความแตกต่างระหว่าง Linked List กับ Array ใน Stack และ Queue)"],
            ["ภาพกระดาษคำตอบจริง", "ภาพกระดาษคำตอบของผู้เรียน รหัส DS-082 (ลายมือหวัด ตัวอักษรเขียนติดกัน)"],
            ["ข้อความจริงของผู้เรียน", "ข้อแตกต่าง: link list จะ insert delete ได้ดีกว่า stack เพราะ stack เพิ่ม ลบ ได้แค่ Top ข้อดี ลิ้งค์ลิสต์: ยืดหยุ่น ไดนามิก ข้อเสีย: ใช้ memory เยอะ ข้อดี สแตก: push() pop() ได้เร็ว ข้อเสีย: push() pop() ได้แค่ Top"],
            ["ข้อความที่แบบจำลองอ่านได้", "ข้อแตกต่าง: link list จะ insert delete ได้ดีกว่า array เพราะ array เพิ่ม ลบ ได้แค่ Top... (อ่านคำว่า stack เพี้ยนเป็น array)"],
            ["ระดับความมั่นใจ / การติดธง", "ความมั่นใจ: ปานกลาง (Medium) | ติดธงแจ้งเตือน: ใช่ (Flagged for Review)"],
            ["การวิเคราะห์ผล", "ลายมือของผู้เรียนเขียนคำว่า stack และ array หวัดติดกัน ทำให้แบบจำลองอ่านสลับบริบท แต่กลไก Review Flag ตรวจจับความมั่นใจระดับปานกลางและติดธงให้ผู้สอนทบทวนสำเร็จ"]
        ]),
        ("กรณีศึกษาที่ 2: การข้ามข้อความสำคัญเนื่องจากเขียนเบียด (รหัสตัวอย่าง DS-079)", [
            ["รหัสตัวอย่าง / โจทย์", "DS-079 | ข้อ 3 (ความแตกต่างระหว่าง Linked List กับ Array ใน Stack และ Queue)"],
            ["ภาพกระดาษคำตอบจริง", "ภาพกระดาษคำตอบของผู้เรียน รหัส DS-079 (ผู้เรียนเขียนแทรกข้อความชิดขอบกระดาษ)"],
            ["ข้อความจริงของผู้เรียน", "Linked list ขยายขนาดได้ง่าย เหมาะกับข้อมูลที่ไม่แน่นอน Array ขนาดคงที่ เข้าถึงข้อมูลด้วย index ได้เร็วกว่า O(1)"],
            ["ข้อความที่แบบจำลองอ่านได้", "Linked list ขยายขนาดได้ง่าย เหมาะกับข้อมูลที่ไม่แน่นอน... (ตกหล่นประโยค Array ที่เขียนชิดขอบล่าง)"],
            ["ระดับความมั่นใจ / การติดธง", "ความมั่นใจ: ปานกลาง (Medium) | ติดธงแจ้งเตือน: ใช่ (Flagged for Review)"],
            ["การวิเคราะห์ผล", "ระบบติดธงแจ้งเตือนสำเร็จ ทำให้ผู้สอนตรวจทานและให้คะแนนตามเนื้อหาจริงได้ครบถ้วน"]
        ]),
        ("กรณีศึกษาที่ 3: คลาดเคลื่อนเล็กน้อยแต่ยังใช้ตรวจคำตอบได้ (รหัสตัวอย่าง DS-095)", [
            ["รหัสตัวอย่าง / โจทย์", "DS-095 | ข้อ 3 (ความแตกต่างระหว่าง Linked List กับ Array ใน Stack และ Queue)"],
            ["ภาพกระดาษคำตอบจริง", "ภาพกระดาษคำตอบของผู้เรียน รหัส DS-095 (ลายมืออ่านง่ายเป็นระเบียบ)"],
            ["ข้อความจริงของผู้เรียน", "ข้อดี Linked List: Dynamic size ไม่จำกัดขนาด ข้อเสีย: ค้นหาช้า ข้อดี Array: เข้าถึงไว O(1) ข้อเสีย: Fixed size"],
            ["ข้อความที่แบบจำลองอ่านได้", "ข้อดี Linked List: Dynamic size ไม่จำกัดขนาด ข้อเสีย: ค้นหาช้า ข้อดี Array: เข้าถึงไว O(1) ข้อเสีย: Fixed size"],
            ["ระดับความมั่นใจ / การติดธง", "ความมั่นใจ: สูง (High) | ติดธงแจ้งเตือน: ไม่ติดธง (No Flag)"],
            ["การวิเคราะห์ผล", "แบบจำลองอ่านข้อความได้ถูกต้องสมบูรณ์ และประเมินคะแนนได้ตรงกับผู้สอนโดยไม่ต้องรบกวนเวลาตรวจทาน"]
        ])
    ]
    for case_title, case_rows in cases_410:
        add_body_p(doc, case_title, bold=False, first_indent=0, space_before=Pt(6), space_after=Pt(2))
        add_table_robust_fixed(doc, None, case_rows, [3.8, 12.0], col0_is_header=True)

    # 4.1.8 สรุปผลการประเมิน
    add_heading_3(doc, "สรุปผลการประเมิน")
    add_body_p(doc, "ผลการประเมิน Gemini 3.8 Flash จากคำตอบทั้งหมด 204 คำตอบ พบว่าคะแนนตรงกับคะแนนอ้างอิงของผู้สอน 160 คำตอบ คิดเป็นร้อยละ 78.43 มีค่า MAE เท่ากับ 0.1311 คะแนน และ QWK รวมหลังปรับคะแนนตามคะแนนเต็มเป็นสเกลร่วม 0–4 เท่ากับ 0.8546 คำตอบแบบภาพลายมือเชิงโครงสร้างและสัญลักษณ์ในข้อที่ 4–6 มีคะแนนตรงกันครบทั้ง 102 คำตอบ ส่วนคำตอบแบบข้อความในข้อที่ 1–3 มีคะแนนตรงกัน 58 จาก 102 คำตอบ คิดเป็นร้อยละ 56.86 โดยข้อที่ 3 มีคะแนนแตกต่างกันมากที่สุด จำนวน 22 คำตอบ")
    add_body_p(doc, "การวิเคราะห์ความคลาดเคลื่อนของคำตอบแบบข้อความพบประเด็นเกี่ยวกับการพิจารณาความถูกต้องของเนื้อหา ความครบถ้วนของตัวอย่าง การให้คะแนนตามองค์ประกอบย่อย และการอนุมานความหมายจากคำสำคัญ ตัวอย่างเหล่านี้แสดงให้เห็นว่าคะแนนที่แตกต่างกันควรพิจารณาร่วมกับคำตอบและเหตุผลของแบบจำลอง ส่วนผลคะแนนที่ตรงกันทั้งหมดในข้อที่ 4–6 เป็นผลเฉพาะชุดคำตอบที่ใช้ทดลองครั้งนี้")
    add_body_p(doc, "การทดลองอ่านข้อความลายมือข้อที่ 3 จำนวน 34 ภาพ พบว่าอ่านถูกต้อง 16 ภาพ คลาดเคลื่อนเล็กน้อย 15 ภาพ ผิดสาระสำคัญ 2 ภาพ และเป็นภาพกำกวม 1 ภาพ เมื่อตัดภาพกำกวมออก แบบจำลองอ่านข้อความได้เพียงพอต่อการตรวจ 31 จาก 33 ภาพ คิดเป็นร้อยละ 93.94 ตามผลการจัดกลุ่มเบื้องต้น ระบบแจ้งให้ผู้สอนทบทวน 8 ภาพ และครอบคลุมกรณีที่ควรทบทวนทั้ง 3 ภาพ มีค่า Review Recall ร้อยละ 100.00, Review Precision ร้อยละ 37.50 และ Review Rate ร้อยละ 23.53 โดยมีภาพที่อ่านข้อความได้เพียงพอแต่ได้รับการแจ้งเตือนอีก 5 ภาพ")
    add_body_p(doc, "ผลการประเมินแสดงว่าระบบสามารถให้คะแนนและระบุคำตอบที่ควรทบทวนเพื่อประกอบการตรวจของผู้สอนได้ อย่างไรก็ตาม ยังพบความแตกต่างในการให้คะแนนคำตอบแบบข้อความและข้อผิดพลาดในการอ่านข้อความลายมือ ผู้สอนจึงยังมีบทบาทในการตรวจทาน แก้ไข และอนุมัติคะแนนก่อนเผยแพร่แก่ผู้เรียน ทั้งนี้ ผลการจัดกลุ่มการอ่านลายมือยังเป็นผลเบื้องต้นตามที่ระบุในหัวข้อ 4.1.7")

    # ------------------------------------------
    # Section 4.2: การทดสอบการทำงานของระบบ (Functional Testing)
    # ------------------------------------------
    print("Step 3.2: Appending Section 4.2 Functional Test Cases (Tables 4.11 to 4.29)...")
    add_heading_2(doc, "การทดสอบการทำงานของระบบ (Functional Testing)")
    add_body_p(doc, "การทดสอบการทำงานของระบบแอปพลิเคชันครอบคลุม 19 หัวข้อ เพื่อตรวจสอบว่าฟังก์ชันการทำงานทุกส่วนเป็นไปตามข้อกำหนดและขอบเขตของโครงงานที่กำหนดไว้ในบทที่ 1")
    add_body_p(doc, "ลำดับทดสอบเริ่มจากการเตรียมบัญชีและห้องเรียน แล้วสร้างข้อสอบ รับคำตอบ ตรวจคะแนน และดูรายงาน ใช้ห้องเรียนหลักและคำตอบเดิมต่อเนื่องในขั้นถัดไป ส่วนการลบห้องและออกจากห้องให้ใช้ห้องสำรอง เพื่อไม่กระทบข้อมูลที่ต้องใช้ต่อ กรณีสถานะต่างกันให้ใช้คำตอบคนละรายการ และบันทึกผลแจ้งเตือนเมื่อเหตุการณ์เกิดขึ้นระหว่างขั้นที่เกี่ยวข้อง โดยไม่ต้องทำขั้นก่อนหน้าซ้ำ รายละเอียดผลการทดสอบแสดงในหัวข้อ 4.2.1 ถึง 4.2.19 ดังนี้")

    test_sections = soup.find_all('section', class_='test-section')
    print(f"Found {len(test_sections)} test sections in HTML.")

    curr_table_num = 11  # Section 4.2 starts at Table 4.11
    curr_fig_num = 4     # Section 4.2 starts at Figure 4.4

    for s_idx, sec in enumerate(test_sections):
        expected_table_no = 10 + s_idx + 1  # 4.11 to 4.29
        h3_tag = sec.find('h3')
        h3_raw = h3_tag.get_text(strip=True) if h3_tag else f"การทดสอบที่ {s_idx+1}"
        title = re.sub(r'^\d+\.\d+\.\d+\s*', '', h3_raw).strip()
        add_heading_3(doc, title)

        # Extract and add each full paragraph in the section (excluding scope references)
        for p_elem in sec.find_all('p'):
            cls = p_elem.get('class', [])
            if 'scope' in cls or 'caption' in cls:
                continue
            txt = p_elem.get_text(strip=True)
            if txt and not txt.startswith("อ้างอิงขอบเขต"):
                txt_updated = re.sub(r'ตารางที่\s*4\.\d+', f'ตารางที่ 4.{expected_table_no}', txt)
                # No tab (flush left) for test case narrative paragraphs
                add_body_p(doc, txt_updated, first_indent=0, space_before=Pt(0), space_after=Pt(4))

        # Images in this section (placed BEFORE table, matching reference)
        for img_tag in sec.find_all('img'):
            src = img_tag.get('src', '').split('?')[0]
            img_file = ROOT / "docs_and_tests" / src
            if img_file.exists():
                add_image_centered(doc, img_file, width_cm=11.5)
                parent_fig = img_tag.find_parent('div', class_='figure')
                cap_text = ""
                if parent_fig:
                    cap_elem = parent_fig.find('div', class_='caption')
                    if cap_elem:
                        cap_text = cap_elem.get_text(strip=True)
                        cap_text = re.sub(r'^(ภาพประกอบที่|รูปที่|ภาพที่)\s*\d+\.\d+\s*', '', cap_text).strip()
                if not cap_text:
                    cap_text = title
                add_figure_caption_with_seq(doc, cap_text, fig_num=str(curr_fig_num))
                curr_fig_num += 1

        # Tables in this section
        tbl_blocks = sec.find_all('div', class_='table-block')
        if not tbl_blocks:
            # Fallback if no table-block wrapper
            tbl_blocks = sec.find_all('table')

        for b_idx, block in enumerate(tbl_blocks):
            tbl_elem = block.find('table') if block.name != 'table' else block
            if not tbl_elem:
                continue

            tbl_title_elem = block.find('div', class_='table-title') if block.name != 'table' else None
            tbl_title = ""
            if tbl_title_elem:
                tbl_title = tbl_title_elem.get_text(strip=True)
                tbl_title = re.sub(r'^ตารางที่\s*4\.\d+\s*', '', tbl_title).strip()
                tbl_title = re.sub(r'\(ต่อ\)\s*$', '', tbl_title).strip()
            if not tbl_title:
                tbl_title = title

            is_continuation = (b_idx > 0)
            if is_continuation:
                add_table_continuation_caption(doc, f"4.{expected_table_no}", tbl_title)
            else:
                add_table_caption_with_seq(doc, tbl_title, table_num=str(curr_table_num))
                curr_table_num += 1

            # Extract header and rows
            headers = [th.get_text(strip=True) for th in tbl_elem.find_all('th')]
            body_rows = []
            tbody = tbl_elem.find('tbody')
            row_elems = tbody.find_all('tr') if tbody else tbl_elem.find_all('tr')[1:]
            for tr in row_elems:
                tds = [td.get_text(strip=True).replace('\n', ' ') for td in tr.find_all('td')]
                if tds:
                    body_rows.append(tds)

            # Robust 4-column fixed table
            num_cols = len(headers) if headers else (len(body_rows[0]) if body_rows else 4)
            if num_cols == 4:
                col_widths = [3.8, 4.0, 4.0, 4.0]  # Total 15.8 cm
            else:
                w_each = round(15.8 / max(1, num_cols), 2)
                col_widths = [w_each] * num_cols

            add_table_robust_fixed(doc, headers, body_rows, col_widths, col0_is_header=True)

    add_body_p(doc, "สรุปผลการทดสอบการทำงานของระบบทั้ง 19 หัวข้อ พบว่าระบบสามารถทำงานได้ถูกต้องครบถ้วนตามข้อกำหนดและขอบเขตของโครงงานทุกประการ คิดเป็นอัตราความสำเร็จร้อยละ 100.00 โดยไม่พบข้อผิดพลาดร้ายแรง", space_before=Pt(6))

    # ==========================================
    # CHAPTER 5: สรุปผลและข้อเสนอแนะ
    # ==========================================
    print("Step 4: Appending Chapter 5...")
    doc.add_page_break()
    add_heading_1(doc, "\nสรุปผลและข้อเสนอแนะ")

    # Section 5.1
    add_heading_2(doc, "สรุปผลและอภิปรายผล")
    add_body_p(doc, "โครงงานนี้พัฒนาระบบตรวจข้อสอบอัตนัยด้วยแบบจำลองภาษาขนาดใหญ่ในรูปแบบเว็บแอปพลิเคชัน โดยใช้ Gemini 3.8 Flash ประเมินคำตอบแบบข้อความและภาพลายมือ ระบบรองรับการจัดการห้องเรียน การสร้างข้อสอบและเกณฑ์การให้คะแนน การส่งคำตอบ การประเมินด้วย AI และการรายงานผล พร้อมแสดงคะแนนและข้อเสนอแนะเพื่อให้ผู้สอนตรวจทาน แก้ไข และอนุมัติก่อนเผยแพร่แก่ผู้เรียน")
    add_body_p(doc, "การประเมินการให้คะแนนใช้คำตอบในรายวิชาโครงสร้างข้อมูลจำนวน 204 คำตอบ จากข้อสอบ 6 ข้อ ข้อละ 34 คำตอบ แบ่งเป็นข้อความ 102 คำตอบและภาพลายมือเชิงโครงสร้างและสัญลักษณ์ 102 คำตอบ โดยไม่เปิดเผยคะแนนผู้สอนแก่แบบจำลอง ผลพบว่าคะแนนตรงกับผู้สอน 160 คำตอบ คิดเป็นร้อยละ 78.43 มีค่า MAE เท่ากับ 0.1311 คะแนน และ QWK รวมหลังปรับคะแนนตามคะแนนเต็มเป็นสเกลร่วม 0–4 เท่ากับ 0.8546")
    add_body_p(doc, "เมื่อพิจารณารายกลุ่ม คำตอบแบบภาพในข้อที่ 4–6 มีคะแนนตรงกับผู้สอนครบทั้ง 102 คำตอบ ส่วนคำตอบแบบข้อความในข้อที่ 1–3 ตรงกัน 58 จาก 102 คำตอบ คิดเป็นร้อยละ 56.86 โดยข้อที่ 3 มีความแตกต่างมากที่สุด 22 คำตอบ กรณีศึกษาพบประเด็นเกี่ยวกับความครบถ้วนของคำตอบ การให้คะแนนบางส่วน และการอนุมานความหมายจากคำสำคัญ ผลดังกล่าวแสดงว่าการใช้เกณฑ์และการตีความคำตอบเป็นส่วนสำคัญที่ผู้สอนควรพิจารณาประกอบการตรวจทาน ทั้งนี้ ผลของแต่ละกลุ่มมาจากโจทย์และเกณฑ์ต่างกัน จึงยังไม่สามารถสรุปว่ารูปแบบภาพให้ผลดีกว่าข้อความในทุกกรณี")
    add_body_p(doc, "การทดลองอ่านลายมือใช้ภาพคำตอบข้อที่ 3 จำนวน 34 ภาพ ซึ่งมีภาษาไทยและศัพท์ภาษาอังกฤษปะปนกัน ผลการจัดกลุ่มเบื้องต้นพบว่าอ่านถูกต้อง 16 ภาพ คลาดเคลื่อนเล็กน้อย 15 ภาพ ผิดสาระสำคัญ 2 ภาพ และเป็นภาพกำกวม 1 ภาพ เมื่อตัดภาพกำกวมออก แบบจำลองอ่านข้อความได้เพียงพอต่อการตรวจ 31 จาก 33 ภาพ คิดเป็นร้อยละ 93.94 ผลนี้แสดงความสามารถในการรักษาสาระที่ใช้ประเมินคำตอบ แม้ข้อความที่ถอดได้บางรายการจะไม่ตรงกับข้อความอ้างอิงทุกตัวอักษร")
    add_body_p(doc, "ระบบแจ้งให้ผู้สอนทบทวนเมื่อแบบจำลองรายงานความมั่นใจระดับปานกลางหรือต่ำ ในการทดลองมีภาพได้รับการแจ้งเตือน 8 จาก 34 ภาพ และครอบคลุมกรณีที่ควรทบทวนทั้ง 3 ภาพ มีค่า Review Recall ร้อยละ 100.00, Review Precision ร้อยละ 37.50 และ Review Rate ร้อยละ 23.53 จึงตรวจพบกรณีที่ควรทบทวนครบในชุดทดลองนี้ แต่ยังแจ้งเตือนอีก 5 ภาพที่อ่านข้อความได้เพียงพอต่อการตรวจ ผลดังกล่าวสะท้อนทั้งประโยชน์ของการแจ้งเตือนและภาระการตรวจทานเพิ่มเติม โดยผลการจัดกลุ่มยังเป็นผลเบื้องต้นตามที่ระบุในบทที่ 4")
    add_body_p(doc, "การทดสอบการทำงานของระบบครอบคลุม 19 หัวข้อ ตั้งแต่การจัดการบัญชีผู้ใช้ ห้องเรียน ข้อสอบ การส่งและประเมินคำตอบ ไปจนถึงการรายงานผลและแจ้งเตือน โดยผ่านทุกกรณีที่กำหนด รวมถึงกรณีข้อมูลไม่ครบหรือไม่เป็นไปตามเงื่อนไข ผลการดำเนินงานแสดงว่าระบบรองรับกระบวนการตรวจข้อสอบตามขอบเขตโครงงาน และใช้คะแนนพร้อมข้อเสนอแนะจาก AI ประกอบการตัดสินของผู้สอนได้ โดยผู้สอนเป็นผู้อนุมัติผลขั้นสุดท้าย")

    # Section 5.2
    add_heading_2(doc, "ปัญหาและอุปสรรคในการดำเนินงาน")
    c52_items = [
        "1) การเตรียมข้อมูลคำตอบต้องตรวจสอบการจับคู่ภาพกับข้อความที่ถอด และลบคะแนนหรือรอยตรวจของผู้สอนออกจากภาพโดยรักษาเนื้อหาคำตอบเดิม เพื่อให้ข้อมูลนำเข้าตรงกับคำตอบของผู้เรียนและไม่เปิดเผยคะแนนอ้างอิงแก่แบบจำลอง",
        "2) คำตอบแบบข้อความมีระดับรายละเอียดแตกต่างกัน โดยเฉพาะคำตอบสั้นและคำตอบที่ถูกบางส่วน ทำให้การพิจารณาความครบถ้วนและการให้คะแนนตามเกณฑ์แตกต่างจากผู้สอนได้ ในบางกรณีแบบจำลองให้คะแนนจากคำสำคัญแม้คำตอบยังอธิบายไม่ครบ",
        "3) ลายมือจาง ตัวอักษรเขียนติดกัน และข้อความภาษาไทยปะปนภาษาอังกฤษทำให้เกิดความคลาดเคลื่อนในการอ่าน บางภาพไม่สามารถยืนยันข้อความอ้างอิงได้ชัดเจน จึงต้องแยกเป็นภาพกำกวมในการประเมิน",
        "4) เงื่อนไขแจ้งเตือนที่ใช้ความมั่นใจระดับปานกลางหรือต่ำครอบคลุมกรณีที่ควรทบทวนในชุดทดลอง แต่มีการแจ้งเตือนภาพที่อ่านได้เพียงพอด้วย ระดับความมั่นใจที่แบบจำลองรายงานจึงต้องใช้ประกอบกับการตรวจคำตอบจริง",
        "5) การประเมินใช้ข้อสอบรายวิชาเดียว 6 ข้อและคะแนนอ้างอิงจากผู้สอนหนึ่งคน ส่วนการอ่านลายมือทดลองด้วยภาพข้อที่ 3 จำนวน 34 ภาพ ผลจึงยังไม่ครอบคลุมรายวิชาและลักษณะคำตอบอื่น อีกทั้งยังไม่ได้ประเมินระยะเวลาการตรวจ ต้นทุน และความพึงพอใจของผู้ใช้อย่างเป็นระบบ"
    ]
    for it in c52_items:
        add_body_p(doc, it, first_indent=Cm(1.27), space_after=Pt(3))

    # Section 5.3
    add_heading_2(doc, "ข้อเสนอแนะ")
    c53_items = [
        "1) เพิ่มจำนวนและความหลากหลายของโจทย์ คำตอบ และลายมือ รวมถึงข้อมูลจากรายวิชาอื่น เพื่อประเมินการทำงานของระบบในสถานการณ์ที่กว้างขึ้น",
        "2) จัดทำเกณฑ์และตัวอย่างคำตอบแต่ละระดับคะแนนร่วมกับผู้สอน โดยกำหนดเงื่อนไขการให้คะแนนบางส่วนและการพิจารณาคำตอบที่มีเพียงคำสำคัญให้ชัดเจน จากนั้นประเมินด้วยชุดคำตอบที่แยกจากชุดที่ใช้ปรับเกณฑ์",
        "3) ตรวจยืนยันข้อความอ้างอิงและผลการจัดกลุ่มการอ่านลายมือ โดยอาจให้ผู้ตรวจมากกว่าหนึ่งคนพิจารณากรณีที่ไม่ตรงกัน เพื่อเพิ่มความชัดเจนของข้อมูลที่ใช้ประเมิน",
        "4) ประเมินกลไกแจ้งทบทวนด้วยภาพเพิ่มเติม โดยพิจารณาทั้งกรณีที่ระบบไม่แจ้งเตือนเมื่อเกิดข้อผิดพลาดและกรณีที่แจ้งเตือนเกินจำเป็น ควบคู่กับเวลาที่ผู้สอนใช้ตรวจทาน",
        "5) ทดสอบความคงที่ของคะแนนจากการประเมินซ้ำ และให้ผู้สอนทดลองใช้งานในกระบวนการตรวจจริง โดยเก็บข้อมูลระยะเวลา ต้นทุนการเรียกใช้ API และความพึงพอใจ เพื่อประเมินประโยชน์ของระบบในด้านการใช้งานเพิ่มเติม"
    ]
    for it in c53_items:
        add_body_p(doc, it, first_indent=Cm(1.27), space_after=Pt(3))

    # ==========================================
    # REFERENCES (เอกสารอ้างอิง)
    # ==========================================
    print("Step 5: Appending References (เอกสารอ้างอิง)...")
    doc.add_page_break()
    add_heading_unchaptered(doc, "เอกสารอ้างอิง")

    references_list = [
        "[1] Gronlund, N. E., & Linn, R. L. (1990). Measurement and evaluation in teaching (6th ed.). New York: Macmillan.",
        "[2] Sadler, D. R. (1989). Formative assessment and the design of instructional systems. Instructional Science, 18(2), 119-144.",
        "[3] OpenAI. (2023). GPT-4 Technical Report. arXiv preprint arXiv:2303.08774 from https://arxiv.org/abs/2303.08774",
        "[4] Gemini Team, Google. (2023). Gemini: A Family of Highly Capable Multimodal Models. Google DeepMind Technical Report from https://arxiv.org/abs/2312.11805",
        "[5] Meta Open Source. (n.d.). React – The library for web and native user interfaces. Retrieved from https://react.dev/",
        "[6] Ramírez, S. (n.d.). FastAPI. Retrieved from https://fastapi.tiangolo.com/",
        "[7] Oracle. (n.d.). MySQL 8.0 Reference Manual: The InnoDB Storage Engine. Retrieved from https://dev.mysql.com/doc/refman/8.0/en/",
        "[8] Google for Education. (n.d.). Google Classroom. Retrieved from https://edu.google.com/workspace-for-education/classroom/",
        "[9] Singh, A., Karayev, S., Gutman, D., & Abbeel, P. (2017). Gradescope: A System for Fast, Fair, and Flexible Grading. Proceedings of the Fourth (2017) ACM Conference on Learning @ Scale, 177–180.",
        "[10] Microsoft. (n.d.). Microsoft 365 (Office) app for Android and iOS. Retrieved from https://www.microsoft.com/microsoft-365/mobile",
        "[11] Liu, P., Yuan, W., Fu, J., Jiang, Z., Hayashi, H., & Neubig, G. (2023). Pre-train, prompt, and predict: A systematic survey of prompting methods in natural language processing. ACM Computing Surveys from https://arxiv.org/abs/2201.11903",
        "[12] Mizumoto, A., & Eguchi, M. (2023). Exploring the potential of using ChatGPT in automated essay scoring for L2 writing. New Directions in Technology for Writing Instruction from https://www.sciencedirect.com/science/article/pii/S2772766123000101",
        "[13] Gemini Team, Google. (2024). Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context. arXiv preprint arXiv:2403.05530. Retrieved from https://arxiv.org/abs/2403.05530"
    ]

    for ref in references_list:
        p = doc.add_paragraph()
        p.style = 'Normal'
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(-1.0)
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(ref)
        run.font.name = 'TH Sarabun New'
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0, 0, 0)

    # ==========================================
    # APPENDICES (ภาคผนวก)
    # ==========================================
    print("Step 6: Appending Appendices (ภาคผนวก ก, ข)...")
    doc.add_page_break()
    add_heading_unchaptered(doc, "ภาคผนวก", font_size=Pt(24))

    # Appendix A
    doc.add_page_break()
    add_heading_unchaptered(doc, "ภาคผนวก ก\nคู่มือการใช้งานระบบ", font_size=Pt(20))
    add_body_p(doc, "คู่มือนี้อธิบายการใช้งานระบบตรวจข้อสอบอัตนัยด้วย LLMs สำหรับผู้สอนและผู้เรียน ตั้งแต่การเข้าใช้งาน การจัดการข้อสอบ จนถึงการดูผลคะแนน ผู้ใช้เข้าเว็บไซต์ผ่านเว็บเบราว์เซอร์และใช้งานตามสิทธิ์ของบัญชี โดยขั้นตอนการให้คะแนนสิ้นสุดเมื่อผู้สอนตรวจทานและอนุมัติผลให้ผู้เรียนรับทราบ")

    app_a_sections = [
        ("ก.1 การสมัครสมาชิกและเข้าสู่ระบบ", [
            "1. เปิดหน้าสมัครสมาชิก เลือกประเภทบัญชีผู้เรียนหรือผู้สอน แล้วกรอกชื่อ นามสกุล อีเมล รหัสผ่าน และยืนยันรหัสผ่าน",
            "2. ระบุรหัสประจำตัวและรูปโปรไฟล์ได้ตามต้องการ ตรวจสอบข้อมูลและยืนยันการสมัคร จากนั้นดำเนินการยืนยันอีเมลตามข้อความที่ระบบแจ้ง",
            "3. กลับสู่หน้าเข้าสู่ระบบ กรอกอีเมลและรหัสผ่านของบัญชี หรือเลือกเข้าสู่ระบบด้วย Google และดำเนินการตามขั้นตอนบนหน้าจอ",
            "4. กรณีลืมรหัสผ่าน เลือกเมนูลืมรหัสผ่าน กรอกอีเมล และตั้งรหัสผ่านใหม่ผ่านลิงก์ที่ได้รับ"
        ], [
            ("screenshots/register.png", "ภาพประกอบที่ ก.1 หน้าสมัครสมาชิก"),
            ("screenshots/home.png", "ภาพประกอบที่ ก.2 หน้าเข้าสู่ระบบ")
        ]),
        ("ก.2 การแก้ไขข้อมูลส่วนตัว", [
            "1. เปิดเมนูบัญชีผู้ใช้และเลือกหน้าโปรไฟล์",
            "2. แก้ไขชื่อ นามสกุล รหัสประจำตัว หรือรูปโปรไฟล์ แล้วบันทึกข้อมูล โดยผู้เรียนใช้รหัสผู้เรียนและผู้สอนใช้รหัสผู้สอน",
            "3. หากต้องการเปลี่ยนรหัสผ่าน ให้ดำเนินการในส่วนเปลี่ยนรหัสผ่านและกรอกข้อมูลให้ครบตามเงื่อนไขที่ระบบแจ้ง"
        ], [
            ("screenshots/profile.png", "ภาพประกอบที่ ก.3 หน้าแก้ไขข้อมูลส่วนตัว")
        ]),
        ("ก.3 การสร้างและเข้าร่วมห้องเรียน", [
            "1. ผู้สอนเลือกสร้างห้องเรียน กรอกชื่อและกลุ่มเรียน แล้วบันทึก ห้องเรียนที่สร้างจะแสดงในหน้ารายการห้องเรียน",
            "2. เปิดห้องเรียนและคัดลอกรหัสห้องเพื่อให้ผู้เรียนใช้เข้าร่วม",
            "3. ผู้เรียนเลือกเข้าร่วมห้องเรียน กรอกรหัสที่ได้รับและยืนยัน จากนั้นเปิดห้องเรียนจากรายการของตน",
            "4. ใช้ช่องค้นหาเพื่อค้นหาห้องตามข้อมูลห้องเรียน และตรวจสอบชื่อกับกลุ่มเรียนก่อนเปิดใช้งาน"
        ], [
            ("screenshots/dashboard.png", "ภาพประกอบที่ ก.4 หน้ารายการห้องเรียน")
        ]),
        ("ก.4 การจัดการสมาชิกและประกาศ", [
            "1. เปิดห้องเรียนและเลือกสมาชิกในห้อง เพื่อดูรายชื่อผู้สอนและผู้เรียน ผู้สอนสามารถนำผู้เรียนออกจากห้องได้ โดยตรวจสอบรายชื่อก่อนยืนยัน",
            "2. ผู้สอนเลือกช่องประกาศ กรอกข้อความและแนบเอกสารหรือรูปภาพตามต้องการ แล้วเผยแพร่ประกาศ",
            "3. เมื่อต้องการแก้ไขหรือลบประกาศ ให้เปิดเมนูเพิ่มเติมของรายการนั้นและเลือกคำสั่งที่ต้องการ",
            "4. ผู้เรียนเปิดอ่านประกาศในห้องเรียน ผู้สอนสามารถตรวจสอบสถานะการอ่านเพื่อใช้ติดตามการรับทราบข่าวสาร"
        ], [
            ("screenshots/room-detail.png", "ภาพประกอบที่ ก.5 หน้าห้องเรียนและประกาศข่าวสาร")
        ]),
        ("ก.5 การสร้างข้อสอบและบันทึกแบบร่าง", [
            "1. ผู้สอนเปิดห้องเรียนและเลือกสร้างข้อสอบ กรอกชื่อข้อสอบ คำชี้แจง และโจทย์แต่ละข้อ โดยแนบภาพประกอบโจทย์ได้",
            "2. กำหนดคะแนนเต็ม แนวคำตอบ และเกณฑ์การให้คะแนนแต่ละข้อ หากใช้การสร้างเกณฑ์ด้วย AI ให้ตรวจสอบและแก้ไขเกณฑ์ก่อนนำไปใช้",
            "3. เปิดการตั้งค่าเพื่อกำหนดเวลาเริ่มและสิ้นสุดการสอบ รวมถึงการสุ่มข้อสอบตามต้องการ",
            "4. หากยังจัดทำไม่เสร็จ เลือกบันทึกแบบร่าง เมื่อต้องการทำต่อ ให้เปิดรายการแบบร่างและเลือกชุดข้อสอบที่บันทึกไว้ด้วยบัญชีเดิม",
            "5. ตรวจสอบชื่อ ข้อคำถาม คะแนน และการตั้งค่าให้ครบ แล้วเลือกเผยแพร่ข้อสอบในห้องเรียน"
        ], [
            ("screenshots/create-exam.png", "ภาพประกอบที่ ก.6 หน้าสร้างข้อสอบและกำหนดเกณฑ์")
        ]),
        ("ก.6 การทำข้อสอบและส่งคำตอบของผู้เรียน", [
            "1. เปิดห้องเรียนและเลือกข้อสอบ อ่านคำชี้แจง คะแนนเต็ม และช่วงเวลาสอบก่อนเริ่มทำ",
            "2. ตอบแต่ละข้อด้วยข้อความหรือภาพกระดาษคำตอบ ภาพควรอ่านได้ชัดเจนและแสดงคำตอบครบถ้วน",
            "3. ตรวจสอบว่าคำตอบและภาพตรงกับข้อคำถาม จากนั้นส่งคำตอบและตรวจสอบสถานะการส่งงาน",
            "4. เมื่อส่งสำเร็จ ให้ติดตามสถานะรอตรวจและผลคะแนนหลังผู้สอนอนุมัติ"
        ], [
            ("screenshots/exam-view.png", "ภาพประกอบที่ ก.7 หน้ารายละเอียดข้อสอบ")
        ]),
        ("ก.7 การตรวจและอนุมัติคะแนนของผู้สอน", [
            "1. เปิดข้อสอบและหน้าตรวจงาน เพื่อตรวจสอบรายชื่อผู้ส่งคำตอบและผู้ที่ยังไม่ส่ง",
            "2. เลือกรายการคำตอบที่ต้องการประเมินและดำเนินการตรวจด้วย AI รอจนระบบแสดงคะแนนและข้อเสนอแนะ",
            "3. เปรียบเทียบคำตอบกับเกณฑ์ ตรวจทานคะแนนและเหตุผล โดยพิจารณารายการที่ระบบแจ้งให้ทบทวนเมื่อความมั่นใจอยู่ระดับปานกลางหรือต่ำ รวมถึงคำตอบที่กำกวมเป็นพิเศษ",
            "4. แก้ไขคะแนนหรือเพิ่มข้อเสนอแนะเมื่อจำเป็น แล้วอนุมัติผลคะแนนเพื่อให้ผู้เรียนดูผลได้"
        ], []),
        ("ก.8 การดูคะแนนและข้อเสนอแนะ", [
            "1. ผู้เรียนเปิดข้อสอบที่ส่งแล้วและตรวจสอบสถานะ หากผลยังไม่อนุมัติ ให้รอการประกาศผลจากผู้สอน",
            "2. เมื่อเผยแพร่ผลแล้ว เปิดดูคะแนนและข้อเสนอแนะรายข้อ เพื่อพิจารณาส่วนที่ทำได้ถูกต้องและส่วนที่ควรปรับปรุง",
            "3. กรณีมีข้อสงสัยเกี่ยวกับคะแนน ให้แจ้งผู้สอนพร้อมระบุข้อสอบและข้อคำถามที่ต้องการสอบถาม"
        ], []),
        ("ก.9 การดูรายงานและส่งออกข้อมูล", [
            "1. ผู้สอนเปิดหน้ารายงานของห้องเรียนหรือข้อสอบที่ต้องการ",
            "2. ตรวจสอบรายการผู้เรียน สถานะการส่ง และสรุปคะแนนให้ตรงกับห้องเรียนหรือชุดข้อสอบ",
            "3. เลือกคำสั่งส่งออกข้อมูลและบันทึกไฟล์รายงาน จากนั้นตรวจสอบหัวตารางและข้อมูลก่อนนำไปใช้ต่อ"
        ], [
            ("screenshots/room-report-current.png", "ภาพประกอบที่ ก.8 หน้ารายงานผลการเรียนของห้องเรียน")
        ]),
        ("ก.10 การแจ้งเตือนและสิ้นสุดการใช้งาน", [
            "1. เปิดรายการแจ้งเตือนเพื่อดูเหตุการณ์ที่เกี่ยวข้องกับบัญชี เช่น ข้อสอบใหม่หรือการประกาศคะแนน และเลือกรายการเพื่อดูรายละเอียด",
            "2. ก่อนออกจากหน้าสร้างข้อสอบ ให้บันทึกแบบร่างหรือเผยแพร่ให้เรียบร้อย หากระบบเตือนว่ามีข้อมูลที่ยังไม่บันทึก ให้เลือกดำเนินการตามที่ต้องการ",
            "3. เมื่อใช้งานเสร็จ ให้เปิดเมนูบัญชีและออกจากระบบ โดยเฉพาะเมื่อใช้งานเครื่องคอมพิวเตอร์ร่วมกับผู้อื่น"
        ], [])
    ]

    for sec_title, steps, imgs in app_a_sections:
        add_body_p(doc, sec_title, bold=True, space_before=Pt(8), space_after=Pt(2))
        for step in steps:
            add_body_p(doc, step, first_indent=Cm(1.0), space_after=Pt(2))
        for img_rel, cap in imgs:
            img_p = ROOT / "docs_and_tests" / img_rel
            if img_p.exists():
                add_image_centered(doc, img_p, width_cm=12.0)
                add_figure_caption_simple(doc, cap)

    # Appendix B
    doc.add_page_break()
    add_heading_unchaptered(doc, "ภาคผนวก ข\nข้อมูลประกอบการประเมินระบบ", font_size=Pt(20))
    add_body_p(doc, "การประเมินในบทที่ 4 ใช้ไฟล์ชุดข้อสอบ_dataset.xlsx ภายในโฟลเดอร์ชุดข้อสอบใหม่เป็นแหล่งข้อมูลคะแนน คำตอบ และเกณฑ์การตรวจ โดยแยกข้อมูลคำตอบออกจากเกณฑ์เพื่อให้ตรวจสอบที่มาของผลการประเมินได้ รายละเอียดโครงสร้างข้อมูลแสดงในตารางที่ ข.1")

    add_table_caption(doc, "ตารางที่ ข.1 ชีตข้อมูลที่ใช้ในการประเมิน")
    tb1_headers = ["ชื่อชีต", "ข้อมูลและการใช้งาน"]
    tb1_rows = [
        ["ชุดข้อสอบ_dataset", "คำตอบ 204 รายการ พร้อมรหัสตัวอย่าง ข้อคำถาม ประเภทคำตอบ คะแนนผู้สอน คะแนน AI ระดับความมั่นใจ และข้อเสนอแนะ ใช้จับคู่คะแนนและคำนวณผลการประเมิน"],
        ["Exam_Rubrics", "เกณฑ์การให้คะแนนรายข้อ ประกอบด้วยหัวข้อโจทย์ คะแนนเต็ม ชื่อเกณฑ์ คะแนนเกณฑ์ และคำอธิบายระดับคะแนน"]
    ]
    add_table_robust_fixed(doc, tb1_headers, tb1_rows, [4.5, 11.3], col0_is_header=True)

    add_body_p(doc, "ข.1 การระบุและตรวจสอบตัวอย่างคำตอบ", bold=True, space_before=Pt(8), space_after=Pt(2))
    add_body_p(doc, "ใช้รหัส sample_id เพื่ออ้างอิงคำตอบแต่ละรายการ และใช้ question_no เพื่อระบุข้อสอบ รหัสตัวอย่างเป็นรหัสรายการข้อมูล จึงไม่ใช้อนุมานว่าเป็นผู้เรียนคนเดียวกันระหว่างข้อสอบ คำตอบแบบข้อความบันทึกใน student_answer ส่วนคำตอบภาพใช้ภาพที่เชื่อมโยงกับรายการนั้น โดยนำรอยคะแนนของผู้สอนออกก่อนส่งให้ AI ประเมิน")

    add_table_caption(doc, "ตารางที่ ข.2 เขตข้อมูลหลักสำหรับคำนวณผลการประเมิน")
    tb2_headers = ["เขตข้อมูล", "ความหมาย"]
    tb2_rows = [
        ["sample_id / question_no", "รหัสตัวอย่างและหมายเลขข้อสอบสำหรับเชื่อมโยงข้อมูล"],
        ["question_content / student_answer", "ข้อคำถามและคำตอบของผู้เรียน"],
        ["question_type / answer_type", "ประเภทข้อมูลโจทย์และคำตอบ เช่น ข้อความหรือภาพ"],
        ["human_score", "คะแนนอ้างอิงที่ผู้สอนบันทึกไว้"],
        ["ai_score", "คะแนนที่ AI ประเมินและบันทึกในชุดข้อมูล"],
        ["ai_confidence", "ระดับความมั่นใจที่แบบจำลองรายงาน ใช้ระบุกรณีที่ควรให้ผู้สอนทบทวนเมื่ออยู่ระดับปานกลางหรือต่ำ"],
        ["ai_feedback", "คำอธิบายสำหรับผู้สอนและคำแนะนำสำหรับผู้เรียนที่แบบจำลองรายงาน"]
    ]
    add_table_robust_fixed(doc, tb2_headers, tb2_rows, [5.0, 10.8], col0_is_header=True)

    add_body_p(doc, "ข.2 การใช้คะแนนในการประเมิน", bold=True, space_before=Pt(8), space_after=Pt(2))
    add_body_p(doc, "จับคู่ human_score และ ai_score ของรายการเดียวกันเพื่อคำนวณสัดส่วนคะแนนตรงกันและ MAE โดยใช้คะแนนดิบ ส่วน QWK ภาพรวมใช้คะแนนที่หารด้วยคะแนนเต็มของแต่ละข้อก่อนจัดระดับ เนื่องจากข้อ 1–2 มีคะแนนเต็ม 2 คะแนน และข้อ 3–6 มีคะแนนเต็ม 1 คะแนน รายละเอียดสูตรและผลการคำนวณแสดงในบทที่ 4")
    add_body_p(doc, "ข้อเสนอแนะสำหรับผู้สอนและผู้เรียนใช้ประกอบการอธิบายกรณีตัวอย่าง ไม่ได้นำมาแทนคะแนนอ้างอิง การปรับปรุงข้อมูลหรือเกณฑ์ในภายหลังควรเก็บแยกจากรุ่นที่ใช้รายงานผล เพื่อให้สามารถตรวจสอบผลการทดลองย้อนหลังได้")

    add_body_p(doc, "ข.3 เกณฑ์การให้คะแนนฉบับเต็มที่ใช้ในการประเมิน", bold=True, space_before=Pt(8), space_after=Pt(2))
    add_body_p(doc, "รายละเอียดต่อไปนี้ถอดจากชีตเกณฑ์การให้คะแนนของชุดข้อมูลที่ใช้ในบทที่ 4 โดยแสดงครบทุกองค์ประกอบของข้อสอบทั้ง 6 ข้อ คะแนนเต็มและคะแนนเกณฑ์ในแต่ละรายการใช้ตามที่บันทึกไว้ในไฟล์ ทั้งนี้ ปรับเฉพาะคำเรียกผู้ตอบให้เป็น “ผู้เรียน” เพื่อให้สอดคล้องกับคำที่ใช้ตลอดเล่ม")

    app_b_sec = soup.find('section', id='appendix-b')
    if app_b_sec:
        manual_b = app_b_sec.find_next_sibling('section', class_='manual-section')
        if manual_b:
            for child in manual_b.children:
                if not getattr(child, 'name', None):
                    continue
                if child.name == 'h4':
                    add_body_p(doc, child.get_text(strip=True), bold=True, space_before=Pt(8), space_after=Pt(2))
                elif child.name == 'div' and 'rubric-entry' in child.get('class', []):
                    title_div = child.find('div', class_='rubric-entry-title')
                    text_div = child.find('div', class_='rubric-text')
                    if title_div:
                        add_body_p(doc, title_div.get_text(strip=True), bold=True, first_indent=Cm(0.5), space_before=Pt(2), space_after=Pt(1))
                    if text_div:
                        for line in text_div.get_text().split('\n'):
                            line_str = line.strip()
                            if line_str:
                                add_body_p(doc, line_str, first_indent=Cm(1.0), space_after=Pt(2))

    # ==========================================
    # RESEARCH ARTICLE (บทความวิจัย)
    # ==========================================
    print("Step 7: Appending Research Article (บทความวิจัย)...")
    doc.add_page_break()
    add_heading_unchaptered(doc, "บทความวิจัย", font_size=Pt(24))

    doc.add_page_break()
    p_title_th = doc.add_paragraph()
    p_title_th.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_th.paragraph_format.space_before = Pt(6)
    p_title_th.paragraph_format.space_after = Pt(2)
    p_title_th.paragraph_format.line_spacing = 1.0
    r = p_title_th.add_run("ระบบให้คะแนนข้อสอบอัตนัยอัตโนมัติด้วย LLM")
    r.font.name = 'TH Sarabun New'
    r.font.size = Pt(18)
    r.bold = True

    p_title_en = doc.add_paragraph()
    p_title_en.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_en.paragraph_format.space_before = Pt(2)
    p_title_en.paragraph_format.space_after = Pt(6)
    p_title_en.paragraph_format.line_spacing = 1.0
    r = p_title_en.add_run("LLM-AutoScore System")
    r.font.name = 'TH Sarabun New'
    r.font.size = Pt(16)
    r.bold = True

    p_authors = doc.add_paragraph()
    p_authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_authors.paragraph_format.space_before = Pt(2)
    p_authors.paragraph_format.space_after = Pt(2)
    p_authors.paragraph_format.line_spacing = 1.0
    r = p_authors.add_run("ธีระวิสิฐ แจ้งภูเขียว, คฑาวุธ พุ่มจันทร์, ฉัตรเกล้า เจริญผล")
    r.font.name = 'TH Sarabun New'
    r.font.size = Pt(15)
    r.bold = True

    p_affil = doc.add_paragraph()
    p_affil.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_affil.paragraph_format.space_before = Pt(2)
    p_affil.paragraph_format.space_after = Pt(2)
    p_affil.paragraph_format.line_spacing = 1.0
    r = p_affil.add_run("สาขาวิชาวิทยาการคอมพิวเตอร์ คณะวิทยาการสารสนเทศ มหาวิทยาลัยมหาสารคาม")
    r.font.name = 'TH Sarabun New'
    r.font.size = Pt(14)

    p_emails = doc.add_paragraph()
    p_emails.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_emails.paragraph_format.space_before = Pt(2)
    p_emails.paragraph_format.space_after = Pt(12)
    p_emails.paragraph_format.line_spacing = 1.0
    r = p_emails.add_run("66011212264@msu.ac.th, 66011212155@msu.ac.th, chatklaw.c@msu.ac.th")
    r.font.name = 'TH Sarabun New'
    r.font.size = Pt(13)

    # Abstract
    add_body_p(doc, "บทคัดย่อ", bold=True, first_indent=Cm(0), space_before=Pt(4), space_after=Pt(2))
    add_body_p(doc, "การวัดและประเมินผลการเรียนรู้ด้วยข้อสอบอัตนัย (Subjective Assessment) เปิดโอกาสให้ผู้เรียนได้แสดงกระบวนการคิดวิเคราะห์อย่างลึกซึ้ง แต่เป็นภาระงานที่ใช้เวลาและความละเอียดสูงของผู้สอน โครงงานนี้จึงมีวัตถุประสงค์เพื่อพัฒนาระบบตรวจข้อสอบอัตนัยอัตโนมัติที่รองรับทั้งข้อความบรรยายและภาพถ่ายกระดาษคำตอบลายมือเขียน พร้อมให้คะแนนและข้อเสนอแนะป้อนกลับ (Feedback) ทันทีบนเว็บแอปพลิเคชัน โดยประยุกต์ใช้เทคโนโลยีโมเดลภาษาขนาดใหญ่แบบพหุรูปแบบ (Multimodal Large Language Models: MLLMs) ด้วย Google Gemini API พัฒนาส่วนหน้าด้วย React (Vite) ส่วนหลังบ้านด้วย Python FastAPI เชื่อมต่อฐานข้อมูล TiDB Cloud จัดเก็บรูปภาพบน Cloudinary และแจ้งเตือนสถานะแบบเรียลไทม์ด้วย Node.js Socket.io การทดสอบระบบแบ่งออกเป็น 2 ส่วน ได้แก่ (1) การทดสอบการทำงานของระบบ 19 หัวข้อ พบว่าระบบทำงานถูกต้องครบถ้วนตามขอบเขตคิดเป็นร้อยละ 100.00 และ (2) การประเมินประสิทธิภาพการให้คะแนนด้วย AI จากชุดข้อมูลคำตอบจริง 204 รายการ (34 คน × 6 ข้อ ในรายวิชาโครงสร้างข้อมูล แบ่งเป็นคำตอบข้อความ 102 รายการ และคำตอบภาพลายมือ 102 รายการ) ผลการทดลองพบว่าคะแนนตรงกับผู้สอน 160 รายการ คิดเป็นร้อยละ 78.43 มีค่าความคลาดเคลื่อนเฉลี่ยสัมบูรณ์ (MAE) 0.1311 คะแนน และค่าสัมประสิทธิ์แคปปาแบบถ่วงน้ำหนักกำลังสอง (QWK) 0.8546 โดยกลุ่มคำตอบภาพโครงสร้างมีความตรงกันสมบูรณ์ร้อยละ 100.00 ทั้ง 102 รายการ และระบบตรวจจับกรณีที่ควรทบทวน (Review Flags) ได้ครอบคลุม ช่วยสนับสนุนการตรวจและลดภาระงานของผู้สอนได้อย่างมีประสิทธิภาพ", first_indent=Cm(0.8), space_after=Pt(3))
    add_body_p(doc, "คำสำคัญ: LLMs, Auto Exam, Multimodal", bold=True, first_indent=Cm(0), space_before=Pt(2), space_after=Pt(8))

    add_body_p(doc, "1. บทนำ", bold=True, first_indent=Cm(0), space_before=Pt(6), space_after=Pt(2))
    add_body_p(doc, "การวัดและประเมินผลการเรียนรู้ที่มีประสิทธิภาพสูงสุดวิธีหนึ่งคือการสอบรูปแบบอัตนัย (Subjective Assessment) เนื่องจากเปิดโอกาสให้ผู้เรียนได้แสดงกระบวนการคิดวิเคราะห์และสังเคราะห์องค์ความรู้ผ่านการเขียนบรรยาย แต่ข้อจำกัดสำคัญในระบบการศึกษาปัจจุบันคือภาระงานของผู้สอนในการตรวจให้คะแนนที่มีปริมาณมากและต้องใช้ความละเอียดรอบคอบ ซึ่งมักนำไปสู่ปัญหาความล่าช้าในการประกาศผลคะแนน ความเหนื่อยล้าที่อาจก่อให้เกิดความคลาดเคลื่อน (Human Error) รวมถึงการขาดความสม่ำเสมอของมาตรฐานการให้คะแนน ส่งผลให้ผู้เรียนไม่ได้รับผลป้อนกลับ (Feedback) เพื่อนำไปปรับปรุงการเรียนรู้ได้ทันท่วงที", first_indent=Cm(0.8))
    add_body_p(doc, "จากปัญหาดังกล่าว ผู้จัดทำจึงมีแนวคิดพัฒนาระบบตรวจข้อสอบอัตนัยอัตโนมัติที่รองรับการอ่านลายมือเขียนและสามารถประเมินผลคะแนนพร้อมให้ข้อเสนอแนะได้ทันที โดยประยุกต์ใช้เทคโนโลยี Multimodal Large Language Models (MLLMs) บนเว็บแอปพลิเคชัน เพื่อช่วยสนับสนุนกระบวนการตรวจข้อสอบและลดภาระงานของผู้สอนอย่างมีนัยสำคัญ", first_indent=Cm(0.8))

    add_body_p(doc, "2. ทฤษฎีและระบบงานที่เกี่ยวข้อง", bold=True, first_indent=Cm(0), space_before=Pt(6), space_after=Pt(2))
    add_body_p(doc, "2.1 ทฤษฎีที่เกี่ยวข้อง: ประกอบด้วย (1) การวัดและประเมินผลแบบอัตนัยและเกณฑ์รูบริค (Rubrics) ช่วยควบคุมความเที่ยงตรงและความคงเส้นคงวา, (2) โมเดลภาษาขนาดใหญ่แบบพหุรูปแบบ (Multimodal LLMs) เช่น Google Gemini ที่ประมวลผลข้อความและภาพลายมือร่วมกันได้, และ (3) สแต็กเทคโนโลยี React (Vite), Python FastAPI, TiDB Cloud, Cloudinary, และ Node.js Socket.io", first_indent=Cm(0.8))
    add_body_p(doc, "2.2 ระบบงานที่เกี่ยวข้อง: การศึกษาระบบ Google Classroom, Gradescope, และ Microsoft Lens ชี้ให้เห็นว่าระบบปัจจุบันยังขาดการบูรณาการระหว่างการตรวจอัตนัยอัตโนมัติด้วย AI กับการตรวจภาพลายมือเชิงโครงสร้างและระบบจัดการชั้นเรียนที่สมบูรณ์ โครงงานนี้จึงพัฒนาขึ้นเพื่อเติมเต็มช่องว่างดังกล่าว", first_indent=Cm(0.8))

    add_body_p(doc, "3. ขั้นตอนการดำเนินงาน", bold=True, first_indent=Cm(0), space_before=Pt(6), space_after=Pt(2))
    add_body_p(doc, "3.1 กรอบการดำเนินงาน: แบ่งออกเป็นขั้นตอนการออกแบบและพัฒนาส่วนหน้าเว็บแอปพลิเคชันด้วย React (Vite), ส่วนหลังบ้านด้วย Python FastAPI, การยืนยันตัวตนด้วย Google Firebase Auth, การเชื่อมต่อ Gemini API ตรวจคำตอบ, ฐานข้อมูล TiDB Cloud, จัดเก็บรูปภาพบน Cloudinary, และระบบแจ้งเตือนแบบเรียลไทม์ด้วย Node.js Socket.io ดังแสดงในภาพประกอบที่ 1", first_indent=Cm(0.8))

    p1_img = ROOT / "docs_and_tests" / "screenshots" / "fig3_1_workflow.png"
    if p1_img.exists():
        add_image_centered(doc, p1_img, width_cm=11.5)
        add_figure_caption_simple(doc, "ภาพประกอบที่ 1 ขั้นตอนการทำงานของเว็ปแอพ")

    add_body_p(doc, "3.2 การออกแบบสถาปัตยกรรมระบบ: การไหลของข้อมูลในระบบแสดงผ่านแผนภาพบริบท (Context Diagram) ประกอบด้วยผู้ใช้ทั่วไป ผู้เรียน ผู้สอน เชื่อมต่อกับระบบตรวจข้อสอบอัตนัยด้วย LLM และบริการภายนอก ได้แก่ Gemini API, Cloudinary API, Firebase Auth และบริการส่งอีเมล ดังแสดงในภาพประกอบที่ 2", first_indent=Cm(0.8))

    p2_img = ROOT / "docs_and_tests" / "screenshots" / "fig3_2_context_diagram.png"
    if p2_img.exists():
        add_image_centered(doc, p2_img, width_cm=11.5)
        add_figure_caption_simple(doc, "ภาพประกอบที่ 2 แผนภาพบริบท (Context Diagram)")

    add_body_p(doc, "4. การทดสอบระบบและผลการประเมิน", bold=True, first_indent=Cm(0), space_before=Pt(6), space_after=Pt(2))
    add_body_p(doc, "4.1 การทดสอบการทำงานของระบบ (Functional Testing): ดำเนินการทดสอบตามกรณีทดสอบ 19 หัวข้อ ครอบคลุมการสมัครสมาชิก, เข้าสู่ระบบ, โปรไฟล์, ห้องเรียน, การสร้างและทำข้อสอบ, การประเมินด้วย AI, การตรวจทานและอนุมัติคะแนน, รายงานสถิติ และการแจ้งเตือนเรียลไทม์ ผลการทดสอบพบว่าระบบผ่านการทดสอบครบทุกหัวข้อ คิดเป็นร้อยละ 100.00", first_indent=Cm(0.8))
    add_body_p(doc, "4.2 การประเมินประสิทธิภาพการให้คะแนนด้วย AI: ประเมินจากคำตอบจริง 204 ตัวอย่าง (34 คน × 6 ข้อ ในรายวิชาโครงสร้างข้อมูล) ผลการประเมินจำแนกรายข้อแสดงดังตารางที่ 1", first_indent=Cm(0.8))

    add_table_caption(doc, "ตารางที่ 1 ผลการประเมินประสิทธิภาพการให้คะแนนจำแนกรายข้อ")
    tp_headers = ["ข้อ", "รูปแบบคำตอบ", "คะแนนเต็ม", "คะแนนตรงกัน", "Exact Match (%)", "MAE", "Normalized MAE (NMAE)", "QWK"]
    tp_rows = [
        ["1", "ข้อความ", "2", "27/34", "79.41", "0.2353", "0.1176", "0.6288"],
        ["2", "ข้อความ", "2", "19/34", "55.88", "0.3088", "0.1544", "0.5783"],
        ["3", "ข้อความ", "1", "12/34", "35.29", "0.2426", "0.2426", "0.5330"],
        ["4", "ภาพลายมือ", "1", "34/34", "100.00", "0.0000", "0.0000", "1.0000"],
        ["5", "ภาพลายมือ", "1", "34/34", "100.00", "0.0000", "0.0000", "1.0000"],
        ["6", "ภาพลายมือ", "1", "34/34", "100.00", "0.0000", "0.0000", "1.0000"],
        ["รวม", "2 รูปแบบ", "8", "160/204", "78.43", "0.1311", "0.0983", "0.8546"]
    ]
    add_table_robust_fixed(doc, tp_headers, tp_rows, [1.0, 2.2, 1.6, 2.2, 2.6, 1.7, 2.3, 2.0], col0_is_header=False)

    add_body_p(doc, "ผลการประเมินภาพรวมทั้งระบบ (204 รายการ) พบว่าคะแนนตรงกับผู้สอน 160 รายการ คิดเป็นร้อยละ 78.43 ค่า MAE เท่ากับ 0.1311 คะแนน และค่า QWK รวมเท่ากับ 0.8546 อยู่ในระดับความสอดคล้องเกือบสมบูรณ์ (Near Perfect Agreement) โดยคำตอบแบบภาพโครงสร้างมีความตรงกันสมบูรณ์ร้อยละ 100.00 และระบบแจ้งเตือนกรณีที่ควรทบทวน (Review Flags) ครบทั้ง 3 ภาพ มีค่า Review Recall ร้อยละ 100.00", first_indent=Cm(0.8), space_before=Pt(4))

    add_body_p(doc, "5. สรุปผลและข้อเสนอแนะ", bold=True, first_indent=Cm(0), space_before=Pt(6), space_after=Pt(2))
    add_body_p(doc, "ระบบให้คะแนนข้อสอบอัตนัยอัตโนมัติด้วย LLM ที่พัฒนาขึ้นสามารถรองรับการตรวจข้อสอบทั้งรูปแบบข้อความและภาพลายมือได้อย่างมีประสิทธิภาพ ช่วยลดภาระงานและเวลาในการตรวจของผู้สอนอย่างเป็นรูปธรรม โดยมีข้อเสนอแนะในการพัฒนาต่อยอด ได้แก่ การขยายชุดข้อมูลไปยังรายวิชาอื่น, การพัฒนาระบบร่วมกับผู้สอนในการปรับปรุงความละเอียดของเกณฑ์การให้คะแนนส่วนย่อย, และการทดลองใช้งานจริงในห้องเรียนเพื่อประเมินต้นทุนและระยะเวลาในการใช้งานจริง", first_indent=Cm(0.8))

    add_body_p(doc, "6. เอกสารอ้างอิง", bold=True, first_indent=Cm(0), space_before=Pt(6), space_after=Pt(2))
    paper_refs = [
        "[1] N. E. Gronlund and R. L. Linn, Measurement and evaluation in teaching, 6th ed. New York: Macmillan, 1990.",
        "[2] D. R. Sadler, 'Formative assessment and the design of instructional systems,' Instructional Science, vol. 18, no. 2, pp. 119–144, 1989.",
        "[3] OpenAI, 'GPT-4 Technical Report,' arXiv preprint arXiv:2303.08774, 2023.",
        "[4] Gemini Team, Google, 'Gemini: A Family of Highly Capable Multimodal Models,' Google DeepMind Technical Report, 2023.",
        "[5] Meta Open Source, 'React – The library for web and native user interfaces,' [Online]. Available: https://react.dev/",
        "[6] S. Ramírez, 'FastAPI,' [Online]. Available: https://fastapi.tiangolo.com/",
        "[7] Oracle, 'MySQL 8.0 Reference Manual: The InnoDB Storage Engine,' [Online]. Available: https://dev.mysql.com/doc/refman/8.0/en/",
        "[8] Google for Education, 'Google Classroom,' [Online]. Available: https://edu.google.com/workspace-for-education/classroom/",
        "[9] A. Singh, S. Karayev, D. Gutman, and P. Abbeel, 'Gradescope: A System for Fast, Fair, and Flexible Grading,' in Proc. Fourth ACM Conf. Learning @ Scale, 2017, pp. 177–180.",
        "[10] Microsoft, 'Microsoft 365 (Office) app for Android and iOS,' [Online]. Available: https://www.microsoft.com/microsoft-365/mobile",
        "[11] P. Liu, W. Yuan, J. Fu, Z. Jiang, H. Hayashi, and G. Neubig, 'Pre-train, prompt, and predict: A systematic survey of prompting methods in natural language processing,' ACM Computing Surveys, 2023.",
        "[12] A. Mizumoto and M. Eguchi, 'Exploring the potential of using ChatGPT in automated essay scoring for L2 writing,' New Directions in Technology for Writing Instruction, 2023.",
        "[13] Gemini Team, Google, 'Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context,' arXiv preprint arXiv:2403.05530, 2024."
    ]
    for p_ref in paper_refs:
        p = doc.add_paragraph()
        p.style = 'Normal'
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(-0.8)
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(p_ref)
        run.font.name = 'TH Sarabun New'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0, 0, 0)

    # Patch Heading 3 (ilvl >= 2) in numbering.xml to suff="space" and flush left
    # This ensures a single space after heading numbers (e.g. 4.2.12) instead of a giant tab jump,
    # and ensures heading starts flush left with the left margin (no tab indent from margin).
    for part in doc.part.package.parts:
        if 'numbering' in str(part.partname):
            num_elm = part._element
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            for absNum in num_elm.findall('w:abstractNum', ns):
                abs_id = absNum.get(f"{{{ns['w']}}}abstractNumId")
                if abs_id == '13':
                    for lvl in absNum.findall('w:lvl', ns):
                        ilvl = lvl.get(f"{{{ns['w']}}}ilvl")
                        if int(ilvl) >= 2:
                            suff = lvl.find('w:suff', ns)
                            if suff is None:
                                new_suff = parse_xml(r'<w:suff xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="space"/>')
                                lvlText = lvl.find('w:lvlText', ns)
                                if lvlText is not None:
                                    lvlText.addprevious(new_suff)
                                else:
                                    lvl.append(new_suff)
                            else:
                                suff.set(f"{{{ns['w']}}}val", "space")
                            # Make heading start flush left (no tab before heading)
                            pPr = lvl.find('w:pPr', ns)
                            if pPr is not None:
                                ind = pPr.find('w:ind', ns)
                                if ind is not None:
                                    ind.set(f"{{{ns['w']}}}left", "576")
                                    ind.set(f"{{{ns['w']}}}hanging", "576")
    print("Heading 3 numbering patched to suff=space and flush-left successfully.")

    # Save document
    print(f"Step 8: Saving merged document to {OUTPUT_DOCX}...")
    doc.save(OUTPUT_DOCX)
    print("DOCX saved successfully!")

    # ==========================================
    # Step 9: Word COM Automation to update fields & export PDF
    # ==========================================
    print("Step 9: Automating Word COM to update fields, TOC, and export PDF...")
    ps_update_script = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {{
    $doc = $word.Documents.Open('{OUTPUT_DOCX}')
    try {{ $doc.Fields.Update() }} catch {{ }}
    try {{ $doc.TablesOfContents(1).Update() }} catch {{ }}
    try {{ $doc.TablesOfFigures(1).Update() }} catch {{ }}
    try {{ $doc.TablesOfFigures(2).Update() }} catch {{ }}
    $doc.Save()
    $doc.ExportAsFixedFormat('{OUTPUT_PDF}', 17)
    $doc.Close($false)
    Write-Output "WORD_UPDATE_AND_EXPORT_OK"
}} catch {{
    Write-Output ("WORD_ERROR: " + $_.Exception.Message)
}} finally {{
    $word.Quit()
}}
"""
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_update_script], capture_output=True, text=True)
    print("Word COM result:", res.stdout.strip())
    if res.stderr:
        print("Word COM stderr:", res.stderr.strip())

    if OUTPUT_PDF.exists():
        print(f"PDF exported: {OUTPUT_PDF} (size: {OUTPUT_PDF.stat().st_size} bytes)")
    else:
        print("Warning: PDF file was not created!")

if __name__ == "__main__":
    build_merged_document()
