"""Recheck all Q2 answers using the clarified current workbook rubric."""

import asyncio
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import pilot_q2_holistic_rubric as pilot
wb = openpyxl.load_workbook(ROOT / "ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx", read_only=True, data_only=True)
description = wb["Exam_Rubrics"].cell(7, 6).value
wb.close()
assert "คำอธิบายเพิ่มเติมในการแยกคะแนนบางส่วน" in description

pilot.RUBRIC = [{"name": "ความซับซ้อน O(n log n) vs O(n^2) และตัวอย่างอัลกอริทึม",
                 "score": 2.0, "allowed_scores": [0.0, 1.0, 1.5, 2.0],
                 "description": description}]
pilot.KEY = (
    "O(n log n) เติบโตช้ากว่า O(n^2) เมื่อข้อมูลมีขนาดใหญ่ "
    "เช่น Merge Sort หรือ Quick Sort (กรณีเฉลี่ย) เทียบกับ Bubble Sort หรือ Selection Sort. "
    "recursive โดยตัวมันเองไม่ยืนยันว่าเป็น O(n log n)."
)
pilot.OUT = ROOT / "docs_and_tests/q2_q3_review/q2_clarified_rubric_regrade.json"

if __name__ == "__main__":
    asyncio.run(pilot.main())
