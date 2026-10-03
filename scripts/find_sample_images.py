import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"

df = pd.read_excel(EXCEL_PATH, sheet_name="ชุดข้อสอบ_dataset", header=3)

print("Columns:", df.columns.tolist())

# Check how images are referenced in rows for Q4, Q5, Q6
for qno in [4, 5, 6]:
    sub = df[df["question_no"] == qno]
    first = sub.iloc[0]
    print(f"\nQuestion {qno} first row:")
    for col in df.columns:
        print(f"  {col}: {first[col]}")
