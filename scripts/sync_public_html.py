import re, sys, shutil

sys.stdout.reconfigure(encoding='utf-8')

src_html = 'docs_and_tests/chapter4_testcases.html'
dst_html = 'public/chapter4_testcases.html'

with open(src_html, 'r', encoding='utf-8') as f:
    text = f.read()

# In public/chapter4_testcases.html, replace ../public/screenshots/ with screenshots/
# so that both HTTP / Vite server and direct file viewing in public work seamlessly
public_text = text.replace('../public/screenshots/', 'screenshots/')

with open(dst_html, 'w', encoding='utf-8') as f:
    f.write(public_text)

print(f"Synced {src_html} -> {dst_html} successfully!")
