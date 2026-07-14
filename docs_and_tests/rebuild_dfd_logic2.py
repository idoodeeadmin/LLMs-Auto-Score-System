import json
import io

# 1. Load the existing script to extract flow_definitions and schemas
with io.open('c:/Users/idood/.gemini/antigravity-ide/brain/aae78b39-01be-4d59-ae1a-dffe42ae6b0d/scratch/rebuild_final_dict.py', 'r', encoding='utf-8') as f:
    code = f.read()

env = {}
exec(code.split('with io.open')[0], env)
flow_definitions = env.get('flow_definitions', {})
schemas = env.get('schemas', {})

# 2. Add the missing Data Store flows
flow_definitions['ข้อมูลบัญชีผู้ใช้และโปรไฟล์'] = ('ข้อมูลส่วนตัวและการตั้งค่าของผู้ใช้งาน', schemas['D1'], True)
flow_definitions['ข้อมูลบัญชีผู้ใช้เพื่อตรวจสอบ'] = ('ข้อมูลสำหรับตรวจสอบสิทธิ์เข้าใช้งาน', schemas['D1'], True)
flow_definitions['ข้อมูลยืนยันตัวตน'] = ('ข้อมูล Token สำหรับยืนยันตัวตนผ่านอีเมล', schemas['D9'], True)
flow_definitions['ข้อมูลรายละเอียดห้องเรียน'] = ('ข้อมูลรายละเอียดของห้องเรียนแต่ละห้อง', schemas['D2'], True)
flow_definitions['ข้อมูลสมาชิกห้องเรียน'] = ('รายชื่อนักเรียนและข้อมูลการเข้าร่วมห้องเรียน', schemas['D3'], True)
flow_definitions['ข้อมูลประกาศข่าวสาร'] = ('ประกาศและเนื้อหาที่ครูโพสต์ในห้องเรียน', schemas['D10'], True)
flow_definitions['ข้อมูลรายละเอียดข้อสอบ'] = ('รายละเอียดหลักของข้อสอบและการตั้งค่า', schemas['D4'], True)
flow_definitions['ข้อมูลโจทย์และเกณฑ์'] = ('ข้อคำถาม เฉลย และเกณฑ์รูบริค (Rubric)', schemas['D5'], True)
flow_definitions['ข้อมูลสถานะการส่ง'] = ('สถานะการเริ่มทำข้อสอบและการส่งคำตอบ', schemas['D6'], True)
flow_definitions['ข้อมูลคำตอบรายข้อ'] = ('คำตอบที่นักเรียนบันทึกในแต่ละข้อ', schemas['D7'], True)
flow_definitions['ข้อมูลผลคะแนนรวม'] = ('คะแนนรวมที่ได้จากการตรวจข้อสอบทุกข้อ', schemas['D6'], True)
flow_definitions['ข้อมูลผลคะแนนรายข้อและคอมเมนต์'] = ('คะแนนและข้อเสนอแนะรายข้อที่ตรวจแล้ว', schemas['D7'], True)
flow_definitions['ข้อมูลผลการประเมินจาก AI'] = ('ผลการประเมินที่ AI ตรวจและวิเคราะห์', schemas['D7'], True)


flow_definitions['ข้อมูลคะแนนและคอมเมนต์ที่เพิ่มและแก้ไข'] = ('คะแนนและคำติชมที่ผู้สอนแก้ไขเอง', schemas['D7'], True)
flow_definitions['ข้อมูลสถานะการอนุมัติผลคะแนน'] = ('สถานะยืนยันอนุมัติคะแนนเพื่อให้ผู้เรียนดูได้', schemas['D6'], True)
flow_definitions['ข้อมูลผลการประเมินและข้อเสนอแนะจาก AI'] = ('ผลการตรวจและคอมเมนต์จากระบบ AI ที่ส่งให้ผู้สอน', schemas['D7'], True)
flow_definitions['ข้อมูลคำขอออกรายงานสถิติ'] = ('คำสั่งร้องขอสร้างรายงานสรุปคะแนน', schemas['D6'], False)
flow_definitions['ข้อมูลรายงานสรุปคะแนน'] = ('รายงานสถิติและคะแนนรวมทั้งหมด', schemas['D6'], False)
flow_definitions['ข้อมูลประวัติการทำข้อสอบ'] = ('ประวัติและคะแนนที่ผ่านมาของผู้เรียน', schemas['D6'], False)
flow_definitions['ข้อมูลการแจ้งเตือน'] = ('ข้อความแจ้งเตือนสถานะต่างๆ ภายในระบบ', schemas['D12'], True)
flow_definitions['ข้อมูลสถานะการอ่านแจ้งเตือน'] = ('สถานะการเปิดอ่านข้อความแจ้งเตือน', schemas['D12'], True)

# 3. Load the correct Level 2 flows
with io.open('level2_extracted_flows.json', 'r', encoding='utf-8') as f:
    level2_flows = json.load(f)

# Group flows
flows_data = {}
for text, src, dst in level2_flows:
    if text not in flows_data:
        flows_data[text] = []
    if (src, dst) not in flows_data[text]:
        flows_data[text].append((src, dst))


# 3.5 ADD PROCESS 6 AND 7 FLOWS
p6 = 'Process 6.0 จัดการผลคะแนนและรายงาน'
p7 = 'Process 7.0 จัดการแจ้งเตือนและการสื่อสาร'
d4 = 'D4 แฟ้มข้อมูลข้อสอบ'
d6 = 'D6 แฟ้มข้อมูลการส่งข้อสอบ'
d7 = 'D7 แฟ้มข้อมูลคำตอบ'
d12 = 'D12 แฟ้มข้อมูลการแจ้งเตือน'

extra_flows = [
    # Process 6.0 User Inputs/Outputs
    ('ข้อมูลคะแนนและคอมเมนต์ที่เพิ่มและแก้ไข', 'ผู้สอน', p6),
    ('ข้อมูลสถานะการอนุมัติผลคะแนน', 'ผู้สอน', p6),
    ('ข้อมูลผลการประเมินและข้อเสนอแนะจาก AI', p6, 'ผู้สอน'),
    ('ข้อมูลผลคะแนนรวม', p6, 'ผู้เรียน'),
    ('ข้อมูลผลคะแนนรายข้อและคอมเมนต์', p6, 'ผู้เรียน'),
    # Process 6.0 Datastore interactions
    ('ข้อมูลผลคะแนนรวม', p6, d6),
    ('ข้อมูลผลคะแนนรายข้อและคอมเมนต์', p6, d7),
    ('ข้อมูลสถานะการส่ง', d6, p6),
    ('ข้อมูลคำตอบรายข้อ', d7, p6),
    
    # Process 7.0 User Inputs/Outputs
    ('ข้อมูลคำขอออกรายงานสถิติ', 'ผู้สอน', p7),
    ('ข้อมูลรายงานสรุปคะแนน', p7, 'ผู้สอน'),
    ('ข้อมูลประวัติการทำข้อสอบ', p7, 'ผู้เรียน'),
    ('ข้อมูลการแจ้งเตือน', p7, 'ผู้สอน'),
    ('ข้อมูลการแจ้งเตือน', p7, 'ผู้เรียน'),
    ('ข้อมูลสถานะการอ่านแจ้งเตือน', 'ผู้สอน', p7),
    ('ข้อมูลสถานะการอ่านแจ้งเตือน', 'ผู้เรียน', p7),
    # Process 7.0 Datastore interactions
    ('ข้อมูลการแจ้งเตือน', p7, d12),
    ('ข้อมูลการแจ้งเตือน', d12, p7),
    ('ข้อมูลสถานะการส่ง', d6, p7),
    ('ข้อมูลคำตอบรายข้อ', d7, p7),
    ('ข้อมูลรายละเอียดข้อสอบ', d4, p7)
]

for text, src, dst in extra_flows:
    if text not in flows_data:
        flows_data[text] = []
    if (src, dst) not in flows_data[text]:
        flows_data[text].append((src, dst))


# 4. Generate the HTML
rows_html = ''
for name, connections in sorted(flows_data.items()):
    if name not in flow_definitions:
        print(f'Missing definition for: {name}')
        continue
    desc, struct, in_db = flow_definitions[name]
        
    inner_table = '<table class="inner-table">'
    for src, dst in connections:
        inner_table += f'<tr><td>{src}</td><td>{dst}</td></tr>'
    inner_table += '</table>'
    
    display_struct = struct if in_db else f'{struct} <br><small style="color:red;">*(ไม่มีในแฟ้มข้อมูล)*</small>'
    
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
print('Done writing HTML')
