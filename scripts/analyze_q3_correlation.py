import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('artifacts/q3_all34_calibrated_results.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"{'ID':<8} | {'Human':<5} | {'OldAI':<5} | {'NewAI':<5} | {'Mentions SQ/LIFO/FIFO?':<22} | {'Has Pro/Con keywords?'}")
print('-'*75)
for x in data:
    txt = x['student_ans'].lower()
    has_sq = any(k in txt for k in ['สแตก', 'คิว', 'stack', 'queue', 'lifo', 'fifo', 'push', 'pop'])
    has_pc = any(k in txt for k in ['ข้อดี', 'ข้อเสีย'])
    print(f"{x['sample_id']:<8} | {x['human_score']:<5.2f} | {x['old_ai_score']:<5.2f} | {x['new_ai_score']:<5.2f} | {str(has_sq):<22} | {str(has_pc)}")
