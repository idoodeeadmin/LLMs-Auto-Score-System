# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('artifacts/q1_all_42_scan.json', encoding='utf-8'))

pure_text = [d for d in data if not d.get('has_drawing')]
drawing = [d for d in data if d.get('has_drawing')]

print(f"=== {len(pure_text)} PURE TEXT FILES ===")
for d in pure_text:
    score = d.get('teacher_score')
    ans = d.get('answer_text', '').replace('\n', ' ')
    print(f"  {d['filename']} | Score: {score} | {ans[:70]}")

print(f"\n=== {len(drawing)} DRAWING / TABLE FILES ===")
for d in drawing:
    score = d.get('teacher_score')
    reason = d.get('brief_reason', '')
    ans = d.get('answer_text', '').replace('\n', ' ')
    print(f"  {d['filename']} | Score: {score} | Reason: {reason[:40]} | Ans: {ans[:40]}")
