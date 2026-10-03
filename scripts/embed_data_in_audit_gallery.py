import json

with open('public/audit_53_mismatches.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False)

with open('public/audit_gallery_53.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = '    let allRecords = [];'
replacement = f'''    const EMBEDDED_RECORDS = {json_str};
    let allRecords = EMBEDDED_RECORDS;'''

html = html.replace(target, replacement)

# In loadData, if fetch fails or protocol is file, just use EMBEDDED_RECORDS
old_load = '''    async function loadData() {
      try {
        const res = await fetch('audit_53_mismatches.json');
        allRecords = await res.json();
        renderGallery(allRecords);
      } catch (err) {
        console.error('Failed to load audit dataset:', err);
        document.getElementById('gallery-grid').innerHTML = '<div style="color:#f87171; text-align:center; padding:40px;">ไม่สามารถโหลดไฟล์ audit_53_mismatches.json ได้ กรุณาเปิดผ่าน Web Server หรือตรวจสอบตำแหน่งไฟล์</div>';
      }
    }'''

new_load = '''    async function loadData() {
      if (window.location.protocol.startsWith('http')) {
        try {
          const res = await fetch('audit_53_mismatches.json');
          if (res.ok) {
            allRecords = await res.json();
          }
        } catch (e) {
          console.log('Using embedded records fallback');
        }
      }
      renderGallery(allRecords);
    }'''

html = html.replace(old_load, new_load)

with open('public/audit_gallery_53.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Embedded data into public/audit_gallery_53.html successfully!")
