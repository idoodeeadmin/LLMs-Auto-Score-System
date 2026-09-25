import sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
EXCEL_DATASET = ROOT / 'ชุดข้อสอบใหม่' / 'ชุดข้อสอบ_dataset.xlsx'
EXCEL_AI_RUBRICS = ROOT / 'ชุดข้อสอบใหม่' / 'เกณฑ์ตรวจสำหรับAI.xlsx'

Q2_RUBRIC_TEXT = (
    "ข้อ 2 (2 คะแนน):\n"
    "- 2.0 คะแนน: อธิบายได้ว่าทำไม O(n log n) ดีกว่าเมื่อข้อมูลใหญ่ เช่น เร็วกว่า, จำนวนรอบ/การทำงานโตช้ากว่า, n² โตเร็วมาก และ มีตัวอย่าง Algorithm หรืออธิบายละเอียดพอ\n"
    "- 1.5 คะแนน: เข้าใจแก่นว่า O(n log n) มีประสิทธิภาพกว่า แต่คำอธิบายยังไม่ครบ/มีส่วนคลาดเคลื่อน/ไม่ยกตัวอย่าง หรือมีตัวอย่างแต่เหตุผลไม่แข็งมาก\n"
    "- 1.0 คะแนน: รู้เพียงว่า O(n log n) “เร็วกว่า/ดีกว่า/ซ้ำซ้อนน้อยกว่า” แต่ไม่ได้อธิบายว่าทำไมอย่างชัดเจน หรือคำอธิบายคลุมเครือ\n"
    "- 0.0 คะแนน: ไม่สามารถอธิบายความสัมพันธ์ของ O(n log n) กับ O(n²) ได้อย่างมีสาระ หรือตอบผิดหลักการ\n"
    "(ระดับคะแนนที่ให้ได้คือ 2.0, 1.5, 1.0, 0.5 หรือ 0.0 คะแนนเท่านั้น)"
)

def update_ai_rubric_file():
    if not EXCEL_AI_RUBRICS.exists():
        print(f"File not found: {EXCEL_AI_RUBRICS}")
        return
    
    wb = openpyxl.load_workbook(EXCEL_AI_RUBRICS)
    ws = wb['ข้อมูลสำหรับ API']
    
    updated = 0
    for r in range(2, ws.max_row + 1):
        q_val = str(ws.cell(row=r, column=1).value or '')
        if 'O(n log n)' in q_val:
            ws.cell(row=r, column=2, value=Q2_RUBRIC_TEXT)
            updated += 1
            
    wb.save(EXCEL_AI_RUBRICS)
    print(f"1. Updated {updated} rows in '{EXCEL_AI_RUBRICS.name}' (Sheet: ข้อมูลสำหรับ API)")

def update_dataset_exam_rubrics_sheet():
    if not EXCEL_DATASET.exists():
        print(f"File not found: {EXCEL_DATASET}")
        return
        
    wb = openpyxl.load_workbook(EXCEL_DATASET)
    
    # Create or replace Exam_Rubrics sheet
    sheet_name = 'Exam_Rubrics'
    if sheet_name in wb.sheetnames:
        del wb[sheet_name]
    ws = wb.create_sheet(title=sheet_name)
    
    # Styles
    font_title = Font(name='Aptos', size=14, bold=True, color='1F497D')
    font_subtitle = Font(name='Aptos', size=10, italic=True, color='595959')
    font_header = Font(name='Aptos', size=11, bold=True, color='FFFFFF')
    font_cell = Font(name='Aptos', size=10)
    font_bold_cell = Font(name='Aptos', size=10, bold=True)
    
    fill_header = PatternFill(start_color='1F497D', end_color='1F497D', fill_type='solid')
    fill_zebra = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    # Title
    ws.merge_cells('A1:F1')
    ws['A1'] = "เกณฑ์การให้คะแนนสำหรับการตรวจข้อสอบอัตโนมัติด้วย AI (Exam Rubrics)"
    ws['A1'].font = font_title
    
    ws.merge_cells('A2:F2')
    ws['A2'] = "วิชาโครงสร้างข้อมูลและขั้นตอนวิธี (Data Structures and Algorithms) | ฉบับปรับปรุงตามพฤติกรรมการตรวจจริง"
    ws['A2'].font = font_subtitle
    
    headers = ["ข้อที่", "หัวข้อโจทย์", "คะแนนเต็ม", "ชื่อเกณฑ์ประเมิน", "คะแนนเกณฑ์", "คำอธิบายเกณฑ์และระดับขั้นคะแนน"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    
    rubric_rows = [
        # ข้อ 1
        (1, "Row-major vs Column-major", 2.0, "Row-major", 1.0, 
         "อธิบาย Row-major ว่าเป็นการจัดเก็บข้อมูล ลำดับการเรียง หรือการหาตำแหน่ง address ตามแนวแถว (Row/แนวนอน/แกน X) ให้ 1.0 คะแนน (แนวคิดเบื้องต้นได้ 0.5 คะแนน)"),
        (1, "Row-major vs Column-major", 2.0, "Column-major", 1.0, 
         "อธิบาย Column-major ว่าเป็นการจัดเก็บข้อมูล ลำดับการเรียง หรือการหาตำแหน่ง address ตามแนวคอลัมน์ (Column/แนวตั้ง/แกน Y) ให้ 1.0 คะแนน (แนวคิดเบื้องต้นได้ 0.5 คะแนน)"),
        
        # ข้อ 2 (เกณฑ์ 4 ระดับใหม่ล่าสุด)
        (2, "O(n log n) vs O(n^2) Complexity", 2.0, "การเปรียบเทียบความซับซ้อนและตัวอย่าง", 2.0,
         "ประเมินตามระดับคะแนนดังนี้อย่างเคร่งครัด:\n"
         "• 2.0 คะแนน: อธิบายได้ว่าทำไม O(n log n) ดีกว่าเมื่อข้อมูลใหญ่ เช่น เร็วกว่า, จำนวนรอบ/การทำงานโตช้ากว่า, n² โตเร็วมาก และ มีตัวอย่าง Algorithm หรืออธิบายละเอียดพอ\n"
         "• 1.5 คะแนน: เข้าใจแก่นว่า O(n log n) มีประสิทธิภาพกว่า แต่คำอธิบายยังไม่ครบ/มีส่วนคลาดเคลื่อน/ไม่ยกตัวอย่าง หรือมีตัวอย่างแต่เหตุผลไม่แข็งมาก\n"
         "• 1.0 คะแนน: รู้เพียงว่า O(n log n) “เร็วกว่า/ดีกว่า/ซ้ำซ้อนน้อยกว่า” แต่ไม่ได้อธิบายว่าทำไมอย่างชัดเจน หรือคำอธิบายคลุมเครือ\n"
         "• 0.0 คะแนน: ไม่สามารถอธิบายความสัมพันธ์ของ O(n log n) กับ O(n²) ได้อย่างมีสาระ หรือตอบผิดหลักการ\n"
         "(ระดับคะแนนที่ให้ได้คือ 2.0, 1.5, 1.0, 0.5 หรือ 0.0 คะแนนเท่านั้น ห้ามให้เศษทศนิยมอื่น)"),
         
        # ข้อ 3
        (3, "Linked List vs Array (Stack & Queue)", 1.0, "ความแตกต่างเชิงโครงสร้าง", 0.5,
         "อธิบายความต่างเรื่อง Fixed size (Array) vs Dynamic size (Linked List) และการจองพื้นที่ต่อเนื่อง vs Pointer (ระดับคะแนน: 0.5, 0.25, 0.0)"),
        (3, "Linked List vs Array (Stack & Queue)", 1.0, "ข้อดีข้อเสียในการใช้งาน", 0.5,
         "ระบุข้อดีข้อเสีย เช่น การเกิด Overflow, ความเร็วในการเข้าถึง O(1), การใช้หน่วยความจำเพิ่มสำหรับ Pointer (ระดับคะแนน: 0.5, 0.25, 0.0)"),
         
        # ข้อ 4
        (4, "Binary Search Tree Construction", 1.0, "ความถูกต้องของโครงสร้าง BST", 1.0,
         "สร้าง Binary Search Tree จากข้อมูล 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99 ได้ถูกต้องตามคุณสมบัติ โหนดซ้าย < โหนดแม่ < โหนดขวา ครบถ้วน (หักคะแนนหากโหนดผิดหรือเชื่อมกิ่งผิด)"),
         
        # ข้อ 5
        (5, "1D Array Representation of BST", 1.0, "การแทนค่าข้อมูลใน Array 1 มิติ", 1.0,
         "แสดงค่าตัวเลขลงในช่อง Array 1 มิติ ได้ถูกต้องตามตำแหน่งโหนดของ Tree ข้อ 4 ตามสูตร root=1, left=2i, right=2i+1"),
         
        # ข้อ 6
        (6, "General Tree to Binary Tree", 1.0, "การแปลง General Tree เป็น Binary Tree", 1.0,
         "แปลงโครงสร้างตามหลักการ Left-Child Right-Sibling (ลูกคนแรกเป็นกิ่งซ้าย พี่น้องลำดับถัดไปเป็นกิ่งขวา) ได้ถูกต้องสมบูรณ์"),
    ]
    
    current_row = 5
    for r_data in rubric_rows:
        q_no, topic, max_s, r_name, r_score, desc = r_data
        
        c1 = ws.cell(row=current_row, column=1, value=q_no)
        c2 = ws.cell(row=current_row, column=2, value=topic)
        c3 = ws.cell(row=current_row, column=3, value=max_s)
        c4 = ws.cell(row=current_row, column=4, value=r_name)
        c5 = ws.cell(row=current_row, column=5, value=r_score)
        c6 = ws.cell(row=current_row, column=6, value=desc)
        
        for c in [c1, c2, c3, c4, c5, c6]:
            c.font = font_cell
            c.border = thin_border
            if current_row % 2 == 1:
                c.fill = fill_zebra
                
        c1.alignment = Alignment(horizontal='center', vertical='top')
        c2.alignment = Alignment(horizontal='left', vertical='top')
        c3.alignment = Alignment(horizontal='center', vertical='top')
        c4.alignment = Alignment(horizontal='left', vertical='top')
        c5.alignment = Alignment(horizontal='center', vertical='top')
        c6.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
        
        current_row += 1
        
    # Column widths
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 14
    ws.column_dimensions['D'].width = 30
    ws.column_dimensions['E'].width = 14
    ws.column_dimensions['F'].width = 85
    
    wb.save(EXCEL_DATASET)
    print(f"2. Created and formatted sheet '{sheet_name}' in '{EXCEL_DATASET.name}'")

if __name__ == '__main__':
    update_ai_rubric_file()
    update_dataset_exam_rubrics_sheet()
