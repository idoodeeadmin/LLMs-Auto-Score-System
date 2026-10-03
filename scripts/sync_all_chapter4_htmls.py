# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read master public/chapter4_testcases.html
with open('public/chapter4_testcases.html', 'r', encoding='utf-8') as f:
    master_testcases = f.read()

# Write to docs_and_tests/chapter4_testcases.html
with open('docs_and_tests/chapter4_testcases.html', 'w', encoding='utf-8') as f:
    f.write(master_testcases.replace('href="audit_gallery_53.html"', 'href="../public/audit_gallery_53.html"'))

# Write to client/public/chapter4_testcases.html if dir exists
if os.path.exists('client/public'):
    with open('client/public/chapter4_testcases.html', 'w', encoding='utf-8') as f:
        f.write(master_testcases)

print("Synchronized all chapter4_testcases.html files!")

# Verify all files
check_files = [
    'public/chapter4_testcases.html',
    'public/chapter4_complete_report.html',
    'docs_and_tests/chapter4_testcases.html',
    'docs_and_tests/chapter4_complete_report.html',
    'client/public/chapter4_testcases.html',
    'client/public/chapter4_complete_report.html',
]

print("\n--- Integrity Check ---")
for p in check_files:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            txt = f.read()
        has_old_pct = '73.04%' in txt
        has_old_count = '149/204' in txt or '149 (73.04%)' in txt
        has_new_pct = '76.47%' in txt
        has_new_count = '156/204' in txt or '156 (76.47%)' in txt
        print(f"{p:<45} | Old (73.04%): {has_old_pct} | Old (149): {has_old_count} | New (76.47%): {has_new_pct} | New (156): {has_new_count}")
    else:
        print(f"{p:<45} | NOT FOUND")
