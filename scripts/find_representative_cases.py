import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"

df = pd.read_excel(EXCEL_PATH, sheet_name="ชุดข้อสอบ_dataset", header=3)

print("Columns:", df.columns.tolist())

# Let's inspect each question
for qno in [1, 2, 3, 4, 5, 6]:
    sub = df[df["question_no"] == qno]
    print(f"\n==================== QUESTION {qno} ====================")
    
    # 1. Exact Match Max Score
    max_score = sub["human_score"].max()
    full_match = sub[(sub["human_score"] == max_score) & (sub["ai_score"] == max_score)]
    if not full_match.empty:
        r = full_match.iloc[0]
        print(f"--- [Exact Match Full Score: {max_score}] Sample: {r['sample_id']} ---")
        print("Student Answer:", str(r['student_answer'])[:250])
        print("AI Feedback:", str(r['ai_feedback'])[:250])
        print("-" * 50)
        
    # 2. Exact Match Partial Score
    partials = sub[(sub["human_score"] > 0) & (sub["human_score"] < max_score) & (sub["human_score"] == sub["ai_score"])]
    if not partials.empty:
        r = partials.iloc[0]
        print(f"--- [Exact Match Partial Score: {r['human_score']}] Sample: {r['sample_id']} ---")
        print("Student Answer:", str(r['student_answer'])[:250])
        print("AI Feedback:", str(r['ai_feedback'])[:250])
        print("-" * 50)
        
    # 3. Exact Match Zero Score
    zeros = sub[(sub["human_score"] == 0) & (sub["ai_score"] == 0)]
    if not zeros.empty:
        r = zeros.iloc[0]
        print(f"--- [Exact Match Zero Score: 0.0] Sample: {r['sample_id']} ---")
        print("Student Answer:", str(r['student_answer'])[:250])
        print("AI Feedback:", str(r['ai_feedback'])[:250])
        print("-" * 50)
        
    # 4. Discrepancy / Edge Case (where diff != 0)
    diffs = sub[sub["human_score"] != sub["ai_score"]]
    if not diffs.empty:
        r = diffs.iloc[0]
        print(f"--- [Discrepancy Case: Human={r['human_score']} vs AI={r['ai_score']}] Sample: {r['sample_id']} ---")
        print("Student Answer:", str(r['student_answer'])[:250])
        print("AI Feedback:", str(r['ai_feedback'])[:250])
        print("-" * 50)
