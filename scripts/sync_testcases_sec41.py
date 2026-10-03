# -*- coding: utf-8 -*-
"""
Sync Section 4.1 from public/chapter4_testcases.html to:
- docs_and_tests/chapter4_testcases.html
- client/public/chapter4_testcases.html
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public/chapter4_testcases.html', 'r', encoding='utf-8') as f:
    master = f.read()

start_marker = '<section class="test-section" id="model-evaluation">'
end_marker = '<h2 class="page-break">4.2 ผลการทดลอง/ผลการทดสอบระบบ</h2>'

s = master.find(start_marker)
e = master.find(end_marker)

if s == -1 or e == -1:
    print("Error: markers not found in master file!")
    sys.exit(1)

sec41_public = master[s:e]
# In docs_and_tests, relative path to audit_gallery_53.html is ../public/audit_gallery_53.html
sec41_docs = sec41_public.replace('href="audit_gallery_53.html"', 'href="../public/audit_gallery_53.html"')

def sync_target(target_path, is_docs=False):
    if not os.path.exists(target_path):
        print(f"Target not found: {target_path}")
        return
    with open(target_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ts = content.find(start_marker)
    te = content.find(end_marker)
    if ts == -1 or te == -1:
        print(f"Markers not found in {target_path} (ts={ts}, te={te})")
        return
        
    replacement = sec41_docs if is_docs else sec41_public
    new_content = content[:ts] + replacement + content[te:]
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Successfully synced {target_path}!")

sync_target('docs_and_tests/chapter4_testcases.html', is_docs=True)
sync_target('client/public/chapter4_testcases.html', is_docs=False)
