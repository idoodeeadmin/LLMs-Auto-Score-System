import sys
sys.stdout.reconfigure(encoding="utf-8")

with open('docs_and_tests/chapter4_testcases.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if any(k in line for k in ['<h2', 'id="test-1"', '4.1.6', '4.1.7', '4.1.8', '4.2 ']):
            print(f'Line {idx+1}: {line.strip()[:70]}')
