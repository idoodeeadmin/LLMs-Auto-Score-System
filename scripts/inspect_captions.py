import re, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('docs_and_tests/chapter4_testcases.html', 'r', encoding='utf-8') as f:
    content = f.read()

tables = re.findall(r'<div class=["\']table-title["\']>(.*?)</div>', content)
print(f'Total tables: {len(tables)}')
for idx, t in enumerate(tables, 1):
    print(f'{idx:2d}. {t}')
