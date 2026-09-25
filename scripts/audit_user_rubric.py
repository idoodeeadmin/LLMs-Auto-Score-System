import json
from pathlib import Path

def main():
    user_files = list(Path('artifacts/q3-user-rubric-eval-20260922-162302').glob('*.json'))
    data = json.load(open(user_files[0], encoding='utf-8'))['results']
    
    lines = []
    lines.append("=== USER 5-LEVEL RUBRIC MISMATCH ANALYSIS (22 MISMATCHES) ===")
    
    diff_groups = {}
    for r in data:
        diff = round(r['ai_score'] - r['human_score'], 2)
        if diff != 0:
            diff_groups.setdefault(diff, []).append(r)
            
    for d, items in sorted(diff_groups.items()):
        lines.append(f"\n--- Diff {d:+0.2f} (count={len(items)}) ---")
        for it in items:
            ans = it['answer'].replace('\n', ' ')
            lines.append(f"  [{it['sample_id']}] Human={it['human_score']:.2f} | AI={it['ai_score']:.2f}")
            lines.append(f"    Ans: {ans}")
            
    Path('scripts/user_rubric_analysis.txt').write_text('\n'.join(lines), encoding='utf-8')
    print("User rubric analysis written.")

if __name__ == '__main__':
    main()
