import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"

df = pd.read_excel(EXCEL_PATH, sheet_name="ชุดข้อสอบ_dataset", header=3)

samples = ["DS-001", "DS-037", "DS-041", "DS-072", "DS-077", "DS-104", "DS-137", "DS-154", "DS-171", "DS-172"]
for sid in samples:
    r = df[df["sample_id"] == sid]
    if not r.empty:
        row = r.iloc[0]
        print(f"\n==================== {sid} (Question {row['question_no']}) ====================")
        print(f"Human Score: {row['human_score']} | AI Score: {row['ai_score']}")
        print("Student Answer:\n", row["student_answer"])
        print("\nAI Feedback:\n", row["ai_feedback"])
