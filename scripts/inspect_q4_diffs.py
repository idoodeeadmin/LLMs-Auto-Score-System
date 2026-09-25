import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')

with open(ROOT / 'artifacts' / 'q4_all34_evaluation_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

diffs = [x for x in data if not x['match']]
print(f"Total diffs: {len(diffs)}")
for d in diffs:
    print("=" * 80)
    print(f"Sample: {d['sample_id']} (idx={d['student_idx']}) | Human={d['human_score']} | AI={d['ai_score']}")
    print(f"Teacher Feedback:\n{d['teacher_feedback']}\n")
    print(f"Student Feedback:\n{d['student_feedback']}\n")
