import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('artifacts/q3_all34_calibrated_results.json', encoding='utf-8') as f:
    data = json.load(f)

for sid in ['DS-090', 'DS-091', 'DS-092', 'DS-093', 'DS-094', 'DS-095', 'DS-096', 'DS-097', 'DS-098', 'DS-100']:
    item = next(x for x in data if x['sample_id'] == sid)
    print(f"=== {item['sample_id']} (Human: {item['human_score']}) ===")
    print(item['student_ans'])
    print()
