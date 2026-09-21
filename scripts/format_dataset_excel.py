import os
import sys
import math
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = os.path.join("ชุดข้อสอบใหม่", "ชุดข้อสอบ_dataset.xlsx")

def format_dataset_excel(file_path: str = FILE_PATH):
    print(f"Opening {file_path} for formatting...")
    wb = openpyxl.load_workbook(file_path)
    
    # Target sheet: 'ชุดข้อสอบ_dataset' (and 'Template_Example' if present)
    target_sheets = [s for s in wb.sheetnames if s in ['ชุดข้อสอบ_dataset', 'Dataset_QWK_204', 'Dataset_QWK']]
    if not target_sheets:
        target_sheets = [wb.active.title]

    for sheet_name in target_sheets:
        ws = wb[sheet_name]
        print(f"Formatting sheet: {sheet_name} (rows: {ws.max_row}, cols: {ws.max_column})")

        # 1. Set generous column widths
        col_widths = {
            1: 14,   # A: sample_id
            2: 12,   # B: question_no
            3: 16,   # C: question_type
            4: 55,   # D: question_content
            5: 16,   # E: answer_type
            6: 70,   # F: student_answer
            7: 16,   # G: human_score
            8: 14,   # H: ai_score
            9: 16,   # I: ai_confidence
            10: 85   # J: ai_feedback
        }

        for col_idx, width in col_widths.items():
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

        # Find header rows (usually rows 4 and 5, or 1 and 2)
        start_row = 1
        for r in range(1, 10):
            val = str(ws.cell(row=r, column=1).value or "").strip().lower()
            if "sample_id" in val or "รหัสตัวอย่าง" in val:
                start_row = r
                break

        print(f"Detected header starts at row {start_row}")

        # Header 1 (e.g. row 4)
        ws.row_dimensions[start_row].height = 30.0
        # Header 2 (e.g. row 5) if exists
        data_start_row = start_row + 1
        val_next = str(ws.cell(row=start_row + 1, column=1).value or "").strip()
        if "(" in val_next or "รหัส" in val_next:
            ws.row_dimensions[start_row + 1].height = 26.0
            data_start_row = start_row + 2

        # 2. Iterate data rows and dynamically compute row height + set top vertical alignment
        for r in range(data_start_row, ws.max_row + 1):
            max_lines = 1
            
            # Check text-heavy columns (D=4, F=6, J=10)
            text_cols = [
                (4, col_widths[4]),
                (6, col_widths[6]),
                (10, col_widths[10])
            ]
            
            for c_idx, width in text_cols:
                cell_val = str(ws.cell(row=r, column=c_idx).value or "")
                if not cell_val:
                    continue
                
                # Approximate characters per line for Thai text
                char_limit_per_line = max(20, int(width * 0.85))
                lines_in_cell = 0
                for para in cell_val.split("\n"):
                    para_len = len(para)
                    if para_len == 0:
                        lines_in_cell += 1
                    else:
                        lines_in_cell += max(1, math.ceil(para_len / char_limit_per_line))
                
                max_lines = max(max_lines, lines_in_cell)

            # Extra buffer for Thai upper/lower vowels and line breathing room
            # 1 line = 28pt, 2 lines = 52pt, 3 lines = 74pt, etc.
            calc_height = max(28.0, max_lines * 22.0 + 8.0)
            ws.row_dimensions[r].height = round(calc_height, 1)

            # 3. Apply clean alignments
            for c in range(1, 11):
                cell = ws.cell(row=r, column=c)
                if c in [1, 2, 3, 5, 7, 8, 9]:
                    # ID, numbers, type -> Center Top
                    cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
                else:
                    # Content, answer, feedback -> Left Top with wrap
                    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    wb.save(file_path)
    print(f"Successfully formatted and saved: {file_path}")

if __name__ == "__main__":
    format_dataset_excel()
