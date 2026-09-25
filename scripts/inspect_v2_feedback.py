import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('artifacts/q3_all34_calibrated_v2_results.json', encoding='utf-8') as f:
    data = json.load(f)

for sid in ['DS-088', 'DS-099', 'DS-101']:
    item = next(x for x in data if x['sample_id'] == sid)
    print(f"=== {item['sample_id']} (Human: {item['human_score']}, AI: {item['new_ai_score']}) ===")
    print(f"ANS: {item['student_ans']}")
    print(f"TF:  {item['teacher_feedback']}")
    print('-'*60)
