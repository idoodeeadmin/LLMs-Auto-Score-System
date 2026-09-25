import sys
import json
from pathlib import Path

def main():
    analytical_files = list(Path('artifacts/q3-analytical-rubric-eval-20260922-173634').glob('*.json'))
    user_files = list(Path('artifacts/q3-user-rubric-eval-20260922-162302').glob('*.json'))
    
    an_data = json.load(open(analytical_files[0], encoding='utf-8'))['results']
    us_data = json.load(open(user_files[0], encoding='utf-8'))['results']
    
    lines = []
    lines.append("=" * 100)
    lines.append("ALL 34 CASES IN QUESTION 3 COMPARISON")
    lines.append(f"{'ID':7s} | {'Human':5s} | {'UserRub':7s} | {'Analytical':10s} | {'Diff(An)':8s} | {'Student Answer'}")
    lines.append("=" * 100)
    
    diff_reasons = []
    
    for an, us in zip(an_data, us_data):
        h = an['human_score']
        u_ai = us['ai_score']
        a_ai = an['ai_score']
        diff = round(a_ai - h, 2)
        diff_str = "MATCH" if diff == 0 else f"{diff:+0.2f}"
        ans = an['answer'].replace('\n', ' ')
        lines.append(f"{an['sample_id']:7s} | {h:5.2f} | {u_ai:7.2f} | {a_ai:10.2f} | {diff_str:8s} | {ans[:70]}")
        
        if diff != 0:
            diff_reasons.append({
                'id': an['sample_id'],
                'human': h,
                'user_rub': u_ai,
                'analytical': a_ai,
                'diff': diff,
                'answer': ans,
                'feedback': an.get('feedback', '')
            })
            
    lines.append("\n" + "=" * 100)
    lines.append(f"TOTAL MISMATCHES IN ANALYTICAL: {len(diff_reasons)} / 34")
    lines.append("=" * 100)
    
    by_diff = {}
    for d in diff_reasons:
        by_diff.setdefault(d['diff'], []).append(d)
        
    for k, v in sorted(by_diff.items()):
        lines.append(f"\n--- Group Diff {k:+0.2f} (count={len(v)}) ---")
        for item in v:
            lines.append(f"  [{item['id']}] Human={item['human']:.2f} | AI={item['analytical']:.2f}")
            lines.append(f"    Answer: {item['answer']}")

    Path('scripts/scratch_audit_report.txt').write_text('\n'.join(lines), encoding='utf-8')
    print("Report written successfully.")

if __name__ == '__main__':
    main()
