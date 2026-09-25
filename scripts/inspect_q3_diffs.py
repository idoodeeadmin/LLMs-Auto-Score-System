import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('artifacts/q3_all34_calibrated_results.json', encoding='utf-8') as f:
    data = json.load(f)

for x in data:
    if x['human_score'] == 1.0:
        print(f"{x['sample_id']} | Human: {x['human_score']} | AI: {x['new_ai_score']} | diff: {x['diff']}")
        print(f"  ANS: {x['student_ans']}")
        print('-'*70)

