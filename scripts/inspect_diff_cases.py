import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')
wb = openpyxl.load_workbook('ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx', data_only=True)
sheet = wb['ชุดข้อสอบ_dataset']

diffs = []
for row in sheet.iter_rows(values_only=True):
    if row[0] and str(row[0]).startswith('DS-'):
        rid = row[0]
        q_num = row[1]
        t_score = float(row[6]) if row[6] is not None else 0.0
        ai_score = float(row[7]) if row[7] is not None else 0.0
        diff = abs(t_score - ai_score)
        if diff > 0.001:
            diffs.append({
                'id': rid,
                'q': q_num,
                'teacher': t_score,
                'ai': ai_score,
                'diff': diff,
                'student': str(row[5])[:120]
            })

print(f"Total discrepancies: {len(diffs)}")
for q in range(1, 7):
    q_diffs = [d for d in diffs if d['q'] == q]
    print(f"Question {q}: {len(q_diffs)} differences")
    for d in q_diffs[:4]:
        print(f"  {d['id']}: Teacher={d['teacher']}, AI={d['ai']}, Diff={d['diff']} | Text: {d['student']}")
