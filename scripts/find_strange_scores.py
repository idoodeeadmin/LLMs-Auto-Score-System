import sys
import io
import openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb = openpyxl.load_workbook('ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx', data_only=True)
ws = wb['ชุดข้อสอบ_dataset']
rows = list(ws.iter_rows(values_only=True))

items = []
for r in rows[5:]:
    if r[0] and str(r[0]).startswith('DS-'):
        sid = str(r[0])
        qno = r[1]
        q_type = r[2]
        q_content = r[3]
        ans = str(r[5]) if r[5] is not None else ''
        h_score = float(r[6]) if r[6] is not None else None
        ai_score = float(r[7]) if r[7] is not None else None
        diff = abs(h_score - ai_score) if (h_score is not None and ai_score is not None) else None
        items.append({
            'sid': sid,
            'qno': qno,
            'ans': ans,
            'h_score': h_score,
            'ai_score': ai_score,
            'diff': diff,
            'feedback': str(r[9]) if len(r)>9 and r[9] is not None else ''
        })

print(f"Parsed {len(items)} items\n")

print("--- 1. Unique Human Scores & AI Scores per Question ---")
for q in range(1, 7):
    q_items = [it for it in items if it['qno'] == q]
    h_scores = sorted(list(set(it['h_score'] for it in q_items if it['h_score'] is not None)))
    ai_scores = sorted(list(set(it['ai_score'] for it in q_items if it['ai_score'] is not None)))
    print(f"Q{q} (N={len(q_items)}): Human scores = {h_scores} | AI scores = {ai_scores}")

print("\n--- 2. Items with Fractional or Unusual Human Scores ---")
for it in items:
    h = it['h_score']
    # Check if score has fractions not just integer or half (e.g. 0.25, 0.75, 1.25, 1.5, 1.75 etc.)
    # Or in 1-point questions where score is > 1 or strange
    if h is not None:
        rem_half = (h * 2) % 1
        rem_quarter = (h * 4) % 1
        if rem_half != 0 or h == 1.5:
            print(f"Unusual Human Score: {it['sid']} (Q{it['qno']}) -> Human={h}, AI={it['ai_score']} | Ans: {it['ans'][:50]}")

print("\n--- 3. Top 20 Largest Discrepancies (|Human - AI|) ---")
diff_items = sorted([it for it in items if it['diff'] is not None], key=lambda x: x['diff'], reverse=True)
for it in diff_items[:20]:
    ans_snippet = it['ans'].replace('\n', ' ')[:70]
    print(f"{it['sid']} (Q{it['qno']}): Human={it['h_score']} vs AI={it['ai_score']} (Diff={it['diff']:.2f}) | Ans: {ans_snippet}")

print("\n--- 4. Checking Blank or Extremely Short Answers with Human Score > 0 ---")
for it in items:
    if it['h_score'] is not None and it['h_score'] > 0:
        ans_clean = it['ans'].strip()
        if len(ans_clean) < 15 and not ans_clean.endswith(('.jpg', '.png', '.jpeg')):
            print(f"Short Ans but Human > 0: {it['sid']} (Q{it['qno']}) -> Human={it['h_score']}, AI={it['ai_score']} | Ans: '{ans_clean}'")

