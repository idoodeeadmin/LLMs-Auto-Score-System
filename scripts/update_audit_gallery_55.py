import json
import re

with open('public/audit_53_mismatches.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False)

with open('public/audit_gallery_53.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace embedded records
html = re.sub(r'const EMBEDDED_RECORDS = \[.*?\];\s*let allRecords', f'const EMBEDDED_RECORDS = {json_str};\n    let allRecords', html, flags=re.DOTALL)

# Update stat cards
html = html.replace('<span class="stat-value">53 <span style="font-size:14px; color:var(--text-muted);">/ 204</span></span>',
                    '<span class="stat-value">55 <span style="font-size:14px; color:var(--text-muted);">/ 204</span></span>')
html = html.replace('<span class="stat-desc">คิดเป็น 25.98% ของข้อสอบทั้งหมด</span>',
                    '<span class="stat-desc">คิดเป็น 26.96% ของข้อสอบทั้งหมด</span>')
html = html.replace('<span class="stat-value" style="color:#38bdf8;" id="cnt-ai-higher">34 ข้อ</span>',
                    '<span class="stat-value" style="color:#38bdf8;" id="cnt-ai-higher">35 ข้อ</span>')
html = html.replace('<span class="stat-value" style="color:#fbbf24;" id="cnt-ai-lower">19 ข้อ</span>',
                    '<span class="stat-value" style="color:#fbbf24;" id="cnt-ai-lower">20 ข้อ</span>')

# Update pills
html = html.replace('<button class="pill active" data-q="all">ทั้งหมด (53)</button>',
                    '<button class="pill active" data-q="all">ทั้งหมด (55)</button>')
html = html.replace('<button class="pill" data-q="1">ข้อ 1 (9)</button>',
                    '<button class="pill" data-q="1">ข้อ 1 (11)</button>')

with open('public/audit_gallery_53.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated public/audit_gallery_53.html with 55 mismatches successfully!")
