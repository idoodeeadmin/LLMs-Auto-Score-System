# -*- coding: utf-8 -*-
import json
import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

# Load original dataset to map filenames to existing teacher scores where available
wb = openpyxl.load_workbook('ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx', data_only=True)
ws = wb['ชุดข้อสอบ_dataset']

# Current 34 mapping in dataset:
# Row 6 to 39: IMG_2791 to IMG_2828 (some were skipped)
# Let's check scripts/prepare_53_audit_dataset.py q1_files list
import os
q1_clean_files = sorted(os.listdir('ชุดข้อสอบใหม่/photo_clean_text1'))

file_to_hscore = {}
file_to_ans = {}
for r in range(6, 40):
    idx = r - 6
    if idx < len(q1_clean_files):
        fn = q1_clean_files[idx].replace('.jpg', '.HEIC')
        h = ws.cell(row=r, column=7).value
        ans = ws.cell(row=r, column=6).value
        file_to_hscore[fn] = float(h) if h is not None else 0.0
        file_to_ans[fn] = ans

data = json.load(open('artifacts/q1_all_42_scan.json', encoding='utf-8'))

bad_files = {
    'IMG_2791.HEIC', 'IMG_2797.HEIC', 'IMG_2802.HEIC', 'IMG_2810.HEIC',
    'IMG_2815.HEIC', 'IMG_2822.HEIC', 'IMG_2825.HEIC', 'IMG_2839.HEIC',
}

candidates = [d for d in data if d['filename'] not in bad_files]

print(f"Total clean candidates: {len(candidates)}")
print("="*80)
for i, c in enumerate(candidates):
    fn = c['filename']
    # Use existing teacher score if already in dataset, else use scan score (clamped to 2.0 max)
    if fn in file_to_hscore:
        score = file_to_hscore[fn]
        ans = file_to_ans[fn]
    else:
        raw_s = c.get('teacher_score')
        score = 2.0 if (raw_s is None or raw_s > 2.0) else float(raw_s)
        ans = c.get('answer_text')

    print(f"[{i+1:02d}] {fn} | Score: {score} | Ans: {repr(str(ans)[:65])}")
