import json
import io
from bs4 import BeautifulSoup

def extract_flows(filename, is_level2=False):
    soup = BeautifulSoup(open(filename, encoding='utf-8'), 'html.parser')
    flows = []
    
    for row in soup.find_all('div', class_='dfd-row'):
        p_id = row.find('div', class_='p-id')
        p_name = row.find('div', class_='p-name')
        if not p_id or not p_name: continue
        
        process = f'Process {p_id.text.strip()} {p_name.text.strip()}'
        
        # col_left (entities/processes)
        col_left = row.find('div', class_='col-left')
        if col_left:
            for entity_conn in col_left.find_all('div', class_='entity-conn'):
                entity = entity_conn.find('div', class_='entity-box') or entity_conn.find('div', class_='internal-link')
                if not entity: continue
                entity_name = entity.text.strip().replace('\n', ' ')
                
                # Replace <br> with space in internal-link if needed, though get_text handles it
                # Actually, BS4 get_text already strips it.
                
                for flow in entity_conn.find_all('div', class_='flow-item'):
                    text = flow.find('div', class_='flow-text').text.strip()
                    arrow = str(flow.find('div', class_='flow-line'))
                    if 'arrow-r' in arrow:
                        flows.append((text, entity_name, process))
                    else:
                        flows.append((text, process, entity_name))
                        
        # col_right (datastores/processes)
        col_right = row.find('div', class_='col-right')
        if col_right:
            for ds_conn in col_right.find_all('div', class_='datastore-conn') + col_right.find_all('div', class_='entity-conn'):
                ds = ds_conn.find('div', class_='datastore-box') or ds_conn.find('div', class_='entity-box') or ds_conn.find('div', class_='internal-link')
                if not ds: continue
                
                d_id = ds.find('div', class_='d-id')
                d_name = ds.find('div', class_='d-name')
                
                if d_id and d_name:
                    ds_full_name = f"{d_id.text.strip()} {d_name.text.strip()}"
                else:
                    ds_full_name = ds.text.strip().replace('\n', ' ')
                    
                for flow in ds_conn.find_all('div', class_='flow-item'):
                    text = flow.find('div', class_='flow-text').text.strip()
                    arrow = str(flow.find('div', class_='flow-line'))
                    if 'arrow-r' in arrow:
                        flows.append((text, process, ds_full_name))
                    else:
                        flows.append((text, ds_full_name, process))
    return flows

# 1. Extract all flows
all_flows = extract_flows('dfd_level1_evaly.html') + extract_flows('dfd_level2_all_evaly.html', is_level2=True)

# 2. Group them by flow text
flows_data = {}
for text, src, dst in all_flows:
    # Cleanup internal links
    src = src.replace('โพรเซส ', 'Process ')
    dst = dst.replace('โพรเซส ', 'Process ')
    
    if text not in flows_data:
        flows_data[text] = []
    if (src, dst) not in flows_data[text]:
        flows_data[text].append((src, dst))

# 3. Load base schemas and definitions
with io.open('c:/Users/idood/.gemini/antigravity-ide/brain/aae78b39-01be-4d59-ae1a-dffe42ae6b0d/scratch/rebuild_final_dict.py', 'r', encoding='utf-8') as f:
    code = f.read()

env = {}
exec(code.split('with io.open')[0], env)
flow_definitions = env.get('flow_definitions', {})
schemas = env.get('schemas', {})

# Ensure Datastores have { }
for k in schemas:
    if k.startswith('D') and k[1:].isdigit():
        schemas[k] = '{' + schemas[k] + '}'

# 4. Add missing definitions explicitly
missing_defs = {
    'ข้อมูลผลคะแนนที่แก้ไข': ('คะแนนที่ผู้สอนแก้ไข', schemas['D7'], True),
    'ข้อมูลสถานะการอ่านประกาศ': ('สถานะการรับรู้ข่าวสารของนักเรียน', schemas['D11'], True),
    'ข้อมูลพร้อมตรวจ': ('ข้อมูลข้อสอบและคำตอบที่จัดเตรียมเพื่อส่งให้ AI ตรวจ', '{รหัสข้อคำถาม + ข้อความโจทย์ + เฉลยแนวทางคำตอบ + ข้อความคำตอบ + {เกณฑ์การประเมินรูบริค}}', False),
    'ข้อมูลประวัติการแจ้งเตือน': ('รายการแจ้งเตือนที่ผ่านมา', schemas['D12'], True),
    'ข้อมูลผลคะแนนรายข้อ': ('คะแนนที่ได้จากแต่ละข้อ', schemas['D7'], True),
    'ข้อมูลผลการประเมินที่จัดรูปแบบแล้ว': ('คะแนนที่แปลงให้อยู่ในรูปแบบที่ระบบเข้าใจ', '{รหัสคำตอบ + รหัสข้อคำถาม + (คะแนนจาก AI) + (ข้อเสนอแนะจาก AI)}', False),
    'รหัสห้องเรียนและรหัสข้อสอบ': ('รหัสสำหรับระบุห้องเรียนและชุดข้อสอบ', 'รหัสห้องเรียน + รหัสข้อสอบ', False),
    'ข้อมูลสถานะการอ่านล่าสุด': ('ข้อมูลการอัปเดตสถานะการอ่าน', schemas['D11'], True),
    'ข้อมูลการแจ้งเตือนใหม่': ('รายการแจ้งเตือนล่าสุดที่ยังไม่ได้อ่าน', schemas['D12'], True),
    'ข้อมูลผลคะแนนที่อนุมัติ': ('คะแนนที่ผู้สอนยืนยันความถูกต้องแล้ว', schemas['D6'], True),
    'ข้อมูลผลการประเมินและข้อเสนอแนะ': ('ผลตรวจให้คะแนนพร้อมคอมเมนต์', '{คะแนนรวมที่ได้ + (ข้อเสนอแนะจาก AI) + (ข้อเสนอแนะจากผู้สอน)}', False),
    'ผลการประเมินดิบ': ('ข้อมูลผลตรวจดิบจาก AI API', 'คะแนนจาก AI + ข้อเสนอแนะจาก AI', False),
    'ข้อมูลผลคะแนน': ('สรุปคะแนนรวมทั้งหมด', schemas['D6'], True),
    'ข้อมูลสถานะอนุมัติ': ('สถานะยืนยันการอนุมัติคะแนน', schemas['D6'], True),
    'ข้อมูลผลคะแนนของนักเรียน': ('รายการคะแนนของผู้เรียนแต่ละคน', schemas['D6'], True),
    'ข้อมูลคะแนนทางการ': ('คะแนนสุทธิหลังการอนุมัติ', schemas['D6'], True),
    
    # Process 6 and 7 related from earlier
    'ข้อมูลคะแนนและคอมเมนต์ที่เพิ่มและแก้ไข': ('คะแนนและคำติชมที่ผู้สอนแก้ไขเอง', schemas['D7'], True),
    'ข้อมูลสถานะการอนุมัติผลคะแนน': ('สถานะยืนยันอนุมัติคะแนนเพื่อให้ผู้เรียนดูได้', schemas['D6'], True),
    'ข้อมูลผลการประเมินและข้อเสนอแนะจาก AI': ('ผลการตรวจและคอมเมนต์จากระบบ AI ที่ส่งให้ผู้สอน', schemas['D7'], True),
    'ข้อมูลคำขอออกรายงานสถิติ': ('คำสั่งร้องขอสร้างรายงานสรุปคะแนน', 'รหัสห้องเรียน + รหัสข้อสอบ', False),
    'ข้อมูลรายงานสรุปคะแนน': ('รายงานสถิติและคะแนนรวมทั้งหมด', '(จำนวนนักเรียนที่สอบผ่าน) + (จำนวนนักเรียนที่สอบตก) + (คะแนนเฉลี่ย) + (คะแนนสูงสุด) + (คะแนนต่ำสุด)', False),
    'ข้อมูลประวัติการทำข้อสอบ': ('ประวัติและคะแนนที่ผ่านมาของผู้เรียน', '{รหัสการส่งข้อสอบ + รหัสข้อสอบ + วันเวลาที่ส่ง + คะแนนรวมที่ได้}', False),
    'ข้อมูลการแจ้งเตือน': ('ข้อความแจ้งเตือนสถานะต่างๆ ภายในระบบ', schemas['D12'], True),
    'ข้อมูลสถานะการอ่านแจ้งเตือน': ('สถานะการเปิดอ่านข้อความแจ้งเตือน', schemas['D12'], True),
    
    # Missing definitions from previous step
    'ข้อมูลบัญชีผู้ใช้และโปรไฟล์': ('ข้อมูลส่วนตัวและการตั้งค่าของผู้ใช้งาน', schemas['D1'], True),
    'ข้อมูลบัญชีผู้ใช้เพื่อตรวจสอบ': ('ข้อมูลสำหรับตรวจสอบสิทธิ์เข้าใช้งาน', schemas['D1'], True),
    'ข้อมูลยืนยันตัวตน': ('ข้อมูล Token สำหรับยืนยันตัวตนผ่านอีเมล', schemas['D9'], True),
    'ข้อมูลรายละเอียดห้องเรียน': ('ข้อมูลรายละเอียดของห้องเรียนแต่ละห้อง', schemas['D2'], True),
    'ข้อมูลสมาชิกห้องเรียน': ('รายชื่อนักเรียนและข้อมูลการเข้าร่วมห้องเรียน', schemas['D3'], True),
    'ข้อมูลประกาศข่าวสาร': ('ประกาศและเนื้อหาที่ครูโพสต์ในห้องเรียน', schemas['D10'], True),
    'ข้อมูลรายละเอียดข้อสอบ': ('รายละเอียดหลักของข้อสอบและการตั้งค่า', schemas['D4'], True),
    'ข้อมูลโจทย์และเกณฑ์': ('ข้อคำถาม เฉลย และเกณฑ์รูบริค (Rubric)', schemas['D5'], True),
    'ข้อมูลสถานะการส่ง': ('สถานะการเริ่มทำข้อสอบและการส่งคำตอบ', schemas['D6'], True),
    'ข้อมูลคำตอบรายข้อ': ('คำตอบที่นักเรียนบันทึกในแต่ละข้อ', schemas['D7'], True),
    'ข้อมูลผลคะแนนรวม': ('คะแนนรวมที่ได้จากการตรวจข้อสอบทุกข้อ', schemas['D6'], True),
    'ข้อมูลผลคะแนนรายข้อและคอมเมนต์': ('คะแนนและข้อเสนอแนะรายข้อที่ตรวจแล้ว', schemas['D7'], True),
    'ข้อมูลผลการประเมินจาก AI': ('ผลการประเมินที่ AI ตรวจและวิเคราะห์', schemas['D7'], True)
}

flow_definitions.update(missing_defs)

# Wrap flow_definitions that represent lists!
list_flows = [
    'ข้อมูลสมาชิกในห้องเรียนและสถานะการส่งงาน',
    'ข้อมูลประกาศข่าวสารห้องเรียน',
    'ข้อมูลข้อสอบ',
    'ข้อมูลโจทย์ข้อสอบและเกณฑ์การให้คะแนน',
    'ข้อมูลคำตอบข้อสอบ',
    'ข้อมูลคำตอบของนักเรียน',
    'ข้อมูลห้องเรียน',
]
for k in flow_definitions:
    if k in list_flows and not flow_definitions[k][1].startswith('{'):
        flow_definitions[k] = (flow_definitions[k][0], '{' + flow_definitions[k][1] + '}', flow_definitions[k][2])


# 5. Build HTML
rows_html = ''
for name, connections in sorted(flows_data.items()):
    if name not in flow_definitions:
        print(f'Missing definition for: {name}')
        desc, struct, in_db = ('-', '-', False)
    else:
        desc, struct, in_db = flow_definitions[name]
        
    inner_table = '<table class="inner-table">'
    for src, dst in connections:
        inner_table += f'<tr><td>{src}</td><td>{dst}</td></tr>'
    inner_table += '</table>'
    
    display_struct = struct
    
    rows_html += f'''
            <tr>
                <td style="text-align: left;">{name}</td>
                <td class="text-left">{desc}</td>
                <td colspan="2" style="padding: 0;">{inner_table}</td>
                <td>{display_struct}</td>
            </tr>
'''

html_template = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Data Flow Dictionary</title>
    <style>
        body {{ font-family: 'Sarabun', Tahoma, sans-serif; padding: 20px; background-color: #f8f9fa; color: #000; }}
        h2 {{ text-align: left; font-size: 18px; margin-bottom: 10px; font-weight: normal; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; background: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: center; vertical-align: middle; }}
        th {{ background-color: #9e9e9e; color: white; font-weight: bold; }}
        td.text-left {{ text-align: left; line-height: 1.4; }}
        .inner-table {{ width: 100%; border-collapse: collapse; height: 100%; margin: 0; padding: 0; }}
        .inner-table td {{ border: none; border-bottom: 1px solid #ccc; padding: 6px; width: 50%; }}
        .inner-table tr:last-child td {{ border-bottom: none; }}
        .inner-table td:first-child {{ border-right: 1px solid #ccc; }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <h2>ตารางพจนานุกรมข้อมูล 3.3 Data Flow Description and Data Structure</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 20%;">Name</th>
                <th style="width: 25%;">Description</th>
                <th style="width: 12%;">Source</th>
                <th style="width: 12%;">Destination</th>
                <th style="width: 31%;">Data Structure</th>
            </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
    </table>
</body>
</html>'''

with io.open('data_flow_dict_evaly.html', 'w', encoding='utf-8') as f:
    f.write(html_template)
print(f'Done writing HTML, total unique flows included: {len(flows_data)}')

# --- Generate Data Store Description ---
ds_names = {
    'D1': 'แฟ้มข้อมูลผู้ใช้',
    'D2': 'แฟ้มข้อมูลห้องเรียน',
    'D3': 'แฟ้มข้อมูลสมาชิกห้องเรียน',
    'D4': 'แฟ้มข้อมูลข้อสอบ',
    'D5': 'แฟ้มข้อมูลโจทย์และเกณฑ์',
    'D6': 'แฟ้มข้อมูลการส่งข้อสอบ',
    'D7': 'แฟ้มข้อมูลคำตอบ',
    'D8': 'แฟ้มข้อมูลรีเซ็ตรหัสผ่าน',
    'D9': 'แฟ้มข้อมูลยืนยันอีเมล',
    'D10': 'แฟ้มข้อมูลประกาศข่าวสาร',
    'D11': 'แฟ้มข้อมูลการอ่านประกาศ',
    'D12': 'แฟ้มข้อมูลแจ้งเตือน'
}

ds_rows_html = ""
for ds_id in sorted(ds_names.keys(), key=lambda x: int(x[1:])):
    ds_name = ds_names[ds_id]
    ds_struct = schemas.get(ds_id, '').strip('{}')
    ds_rows_html += f'''            <tr>
                <td>{ds_id}</td>
                <td>{ds_name}</td>
                <td>{ds_struct}</td>
            </tr>\n'''

ds_html_template = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Data Store Description</title>
    <style>
        body {{ font-family: 'Sarabun', Tahoma, sans-serif; padding: 20px; background-color: #ffffff; color: #000; }}
        h2 {{ text-align: left; font-size: 18px; margin-bottom: 10px; font-weight: normal; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
        th, td {{ border: 1px solid #000; padding: 10px 15px; text-align: left; vertical-align: middle; }}
        th {{ background-color: #e2e2e2; font-weight: bold; text-align: center; }}
        td:nth-child(1) {{ width: 10%; text-align: center; }}
        td:nth-child(2) {{ width: 25%; }}
        td:nth-child(3) {{ width: 65%; line-height: 1.6; }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <h2>Data Store Description (Auto-generated from single source of truth)</h2>
    <table>
        <thead>
            <tr>
                <th>Id</th>
                <th>Data store</th>
                <th>Structure</th>
            </tr>
        </thead>
        <tbody>
{ds_rows_html}        </tbody>
    </table>
</body>
</html>'''

with io.open('datastore_description_evaly.html', 'w', encoding='utf-8') as f:
    f.write(ds_html_template)
print('Done writing Data Store HTML.')
