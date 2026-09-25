import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

f_old = 'artifacts/q1-confidence-eval-20260922-151705/q1_results.json'
f_new = 'artifacts/q1-confidence-eval-20260924-192340/q1_results.json'

with open(f_old, encoding='utf-8') as f:
    d_old = json.load(f)
with open(f_new, encoding='utf-8') as f:
    d_new = json.load(f)

old_map = {r['sample_id']: r for r in d_old['results']}
new_map = {r['sample_id']: r for r in d_new['results']}

changed = []
same = []

for sid in sorted(old_map.keys()):
    ro = old_map[sid]
    rn = new_map[sid]
    h = ro['human_score']
    so = ro['ai_score']
    sn = rn['ai_score']
    if so != sn:
        changed.append({
            'sid': sid,
            'human': h,
            'run1_score': so,
            'run2_score': sn,
            'run1_diff': round(so - h, 2),
            'run2_diff': round(sn - h, 2),
            'ans': ro['answer'],
            'fb_old': ro.get('feedback', ''),
            'fb_new': rn.get('feedback', '')
        })
    else:
        same.append(sid)

print('========================================================================')
print('Q1 REPRODUCIBILITY TEST: EXACT SAME RUBRIC (RUN 1 vs RUN 2)')
print('========================================================================')
print(f"Run 1 (Original Baseline): Exact = {d_old['summary']['exact_count']}/34 ({d_old['summary']['exact_pct']}%), Tol<=0.5 = {d_old['summary']['tolerance_0_5_count']}/34 ({d_old['summary']['tolerance_0_5_pct']}%), MAE = {d_old['summary']['mae']}, QWK = {d_old['summary']['qwk']}")
print(f"Run 2 (New Live Re-test) : Exact = {d_new['summary']['exact_count']}/34 ({d_new['summary']['exact_pct']}%), Tol<=0.5 = {d_new['summary']['tolerance_0_5_count']}/34 ({d_new['summary']['tolerance_0_5_pct']}%), MAE = {d_new['summary']['mae']}, QWK = {d_new['summary']['qwk']}")
print('------------------------------------------------------------------------')
print(f"Total students: 34")
print(f"Scores completely UNCHANGED: {len(same)}/34 ({len(same)/34*100:.1f}%)")
print(f"Scores CHANGED:             {len(changed)}/34 ({len(changed)/34*100:.1f}%)")
print('========================================================================\n')

print('LIST OF STUDENTS WHOSE SCORES CHANGED:')
print(f"{'ID':<7} | {'Human':<5} | {'Run 1':<6} -> {'Run 2':<6} | {'Delta':<7} | Answer Snippet")
print('-'*80)
for c in changed:
    snippet = c['ans'].replace('\n', ' ')[:45]
    delta = f"{c['run2_score'] - c['run1_score']:+.1f}"
    print(f"{c['sid']:<7} | {c['human']:<5.1f} | {c['run1_score']:<6.1f} -> {c['run2_score']:<6.1f} | {delta:<7} | {snippet}")

print('\n========================================================================')
print('DETAILED FEEDBACK FOR CHANGED STUDENTS:')
print('========================================================================')
for c in changed:
    print(f"\n[{c['sid']}] Human={c['human']} | Run 1={c['run1_score']} -> Run 2={c['run2_score']}")
    print(f"Answer: {c['ans']}")
    print(f"Run 1 FB: {c['fb_old'][:150]}...")
    print(f"Run 2 FB: {c['fb_new'][:150]}...")
