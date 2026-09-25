import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / 'docs_and_tests' / 'chapter4_testcases.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

print("=== 4.1 Sections ===")
sections = re.findall(r'<h3>(4\.1\.\d+[^<]+)</h3>', html)
for s in sections:
    print(" ", s)

print(f"\nTotal 4.1 sections: {len(sections)}")

print("\n=== Table Titles ===")
table_titles = re.findall(r'<div class="table-title">(ตารางที่ 4\.\d+[^<]*)</div>', html)
for t in table_titles:
    print(" ", t)

print(f"\nTotal table titles: {len(table_titles)}")

print("\n=== Figure Captions ===")
figures = re.findall(r'<div class="caption">(ภาพประกอบที่ 4\.\d+[^<]*)</div>', html)
for fig in figures:
    print(" ", fig)

print(f"\nTotal figures: {len(figures)}")
