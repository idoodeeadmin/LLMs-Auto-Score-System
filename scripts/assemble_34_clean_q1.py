# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('artifacts/q1_all_42_scan.json', encoding='utf-8'))

# We want 34 best items that:
# 1. Do NOT have pure number grids (no "0 1 2 3 4 5 6 7", no "1 2 3 4 5 6")
# 2. Have actual explanatory text describing Row-major and Column-major
# 3. Exclude the 8 files that have severe number dump / pure table

bad_files = {
    'IMG_2791.HEIC', # pure 0 1 2 3 4 5 6 7 8 9 10 11
    'IMG_2797.HEIC', # pure 1 4 2 3 / 1 3 2 4
    'IMG_2802.HEIC', # 1 2 3 4 5 (R1) C1 C2 C3
    'IMG_2810.HEIC', # 6623 ซ้ายไปขวา
    'IMG_2815.HEIC', # 1 2 3 4 5 6 7 8 9 10 11 12
    'IMG_2822.HEIC', # ac(2,1)=9
    'IMG_2825.HEIC', # [0][1][2]
    'IMG_2839.HEIC', # 0 1 2 3 4 5 6 7
}

candidates = [d for d in data if d['filename'] not in bad_files]
print(f"Total candidate files without number-grids: {len(candidates)} (out of 42)")

# Exactly 34! 42 - 8 = 34!
print(f"\nExact 34 selected files for Question 1:")
for i, c in enumerate(candidates):
    sid = f"DS-{i+1:03d}"
    fn = c['filename']
    score = c.get('teacher_score')
    ans = c.get('answer_text', '').replace('\n', ' ')
    print(f"  {sid} ({fn}) | Teacher: {score} | {ans[:70]}")
