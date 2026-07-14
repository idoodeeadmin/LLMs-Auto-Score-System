import io
from complete_dfd_builder import flows_data

# The subset of processes we want to document (Level 2 + Unsplit Level 1)
target_processes = {
    'Process 1.1 สมัครสมาชิก': {
        'id': '1.1', 'name': 'สมัครสมาชิก', 'desc': 'ลงทะเบียนเข้าใช้งานระบบ',
        'logic': ['เริ่มต้น', '1. รับข้อมูลการลงทะเบียนของผู้ใช้ใหม่', '2. ตรวจสอบรายละเอียดของข้อมูล เพื่อบันทึกข้อมูล', '&nbsp;&nbsp;&nbsp;&nbsp;2.1 ถ้า (ข้อมูลถูกต้องครบถ้วน)', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1.1 ตรวจสอบอีเมล', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ถ้า (อีเมลซ้ำกับในฐานข้อมูล) แสดงข้อความแจ้งเตือนว่ามีอีเมลนี้แล้ว กลับไป 1.', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ถ้า (อีเมลไม่ซ้ำในฐานข้อมูล) บันทึกข้อมูลลงฐานข้อมูล', '&nbsp;&nbsp;&nbsp;&nbsp;2.2 ถ้า (ข้อมูลไม่ถูกต้องและไม่ครบถ้วน)', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;แสดงข้อความว่าข้อมูลไม่ถูกต้องหรือไม่ครบถ้วน กลับไป 1.', 'จบการทำงาน']
    },
    'Process 1.2 เข้าสู่ระบบ': {
        'id': '1.2', 'name': 'เข้าสู่ระบบ', 'desc': 'ตรวจสอบสิทธิ์การเข้าใช้งานระบบ',
        'logic': ['เริ่มต้น', '1. รับข้อมูลการเข้าสู่ระบบ (อีเมลและรหัสผ่าน)', '2. ตรวจสอบข้อมูลในฐานข้อมูล', '&nbsp;&nbsp;&nbsp;&nbsp;2.1 ถ้าข้อมูลถูกต้องและยืนยันอีเมลแล้ว', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;อนุญาตให้เข้าสู่ระบบและสร้างเซสชันการใช้งาน', '&nbsp;&nbsp;&nbsp;&nbsp;2.2 ถ้าข้อมูลไม่ถูกต้อง', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;แสดงข้อความเตือนอีเมลหรือรหัสผ่านผิด', 'จบการทำงาน']
    },
    'Process 1.3 ยืนยันตัวตนและรีเซ็ตรหัสผ่าน': {
        'id': '1.3', 'name': 'ยืนยันตัวตนและรีเซ็ตรหัสผ่าน', 'desc': 'ตรวจสอบโทเคนยืนยันอีเมลหรือรีเซ็ตรหัสผ่านใหม่',
        'logic': ['เริ่มต้น', '1. รับโทเคนหรือข้อมูลการขอรีเซ็ตรหัสผ่าน', '2. ตรวจสอบโทเคนในฐานข้อมูล', '&nbsp;&nbsp;&nbsp;&nbsp;2.1 ถ้าโทเคนถูกต้องและยังไม่หมดอายุ', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;อัปเดตสถานะการยืนยันตัวตน หรือเปลี่ยนรหัสผ่านใหม่', '&nbsp;&nbsp;&nbsp;&nbsp;2.2 ถ้าโทเคนหมดอายุหรือไม่ถูกต้อง', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;แสดงข้อผิดพลาดให้ผู้ใช้ทราบ', 'จบการทำงาน']
    },
    'Process 1.4 แก้ไขโปรไฟล์ผู้ใช้': {
        'id': '1.4', 'name': 'แก้ไขโปรไฟล์ผู้ใช้', 'desc': 'ปรับปรุงข้อมูลส่วนตัวของผู้ใช้งาน',
        'logic': ['เริ่มต้น', '1. รับข้อมูลโปรไฟล์ใหม่จากผู้ใช้', '2. ตรวจสอบความถูกต้องของข้อมูล', '&nbsp;&nbsp;&nbsp;&nbsp;2.1 ถ้าข้อมูลถูกต้อง อัปเดตแฟ้มข้อมูลผู้ใช้', '&nbsp;&nbsp;&nbsp;&nbsp;2.2 ถ้าข้อมูลไม่ถูกต้อง แจ้งเตือนข้อผิดพลาด', 'จบการทำงาน']
    },
    'Process 2.1 จัดการข้อมูลห้องเรียน': {
        'id': '2.1', 'name': 'จัดการข้อมูลห้องเรียน', 'desc': 'สร้างหรือแก้ไขข้อมูลรายละเอียดของห้องเรียน',
        'logic': ['เริ่มต้น', '1. รับคำสั่งและข้อมูลห้องเรียนจากผู้สอน', '2. ตรวจสอบสิทธิ์และข้อมูลที่ส่งมา', '&nbsp;&nbsp;&nbsp;&nbsp;2.1 ถ้าเป็นการสร้างใหม่ ให้สร้างรหัสเข้าห้องเรียนและบันทึก', '&nbsp;&nbsp;&nbsp;&nbsp;2.2 ถ้าเป็นการแก้ไข ให้อัปเดตข้อมูลที่มีอยู่', 'จบการทำงาน']
    },
    'Process 2.2 เข้าร่วมและดูสมาชิกห้องเรียน': {
        'id': '2.2', 'name': 'เข้าร่วมและดูสมาชิกห้องเรียน', 'desc': 'ตรวจสอบรหัสห้องเรียนและเพิ่มสมาชิกใหม่',
        'logic': ['เริ่มต้น', '1. รับรหัสห้องเรียนจากผู้เรียน', '2. ค้นหารหัสห้องเรียนในระบบ', '&nbsp;&nbsp;&nbsp;&nbsp;2.1 ถ้ารหัสถูกต้องและยังเปิดรับสมาชิก', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;เพิ่มผู้เรียนเข้าสู่แฟ้มข้อมูลสมาชิกห้องเรียน', '&nbsp;&nbsp;&nbsp;&nbsp;2.2 ถ้ารหัสผิด แจ้งเตือนผู้เรียน', 'จบการทำงาน']
    },
    'Process 2.3 จัดการประกาศห้องเรียน': {
        'id': '2.3', 'name': 'จัดการประกาศห้องเรียน', 'desc': 'สร้างข่าวสารหรือประกาศให้สมาชิกในห้อง',
        'logic': ['เริ่มต้น', '1. รับข้อมูลประกาศจากผู้สอน', '2. บันทึกข้อมูลลงในแฟ้มข้อมูลประกาศ', '3. แจ้งเตือนไปยังระบบส่งแจ้งเตือน', 'จบการทำงาน']
    },
    'Process 3.1 สร้างและแก้ไขข้อสอบ': {
        'id': '3.1', 'name': 'สร้างและแก้ไขข้อสอบ', 'desc': 'จัดการคำถามและกำหนดเกณฑ์การประเมิน',
        'logic': ['เริ่มต้น', '1. รับข้อมูลข้อสอบและคำถามจากผู้สอน', '2. ตรวจสอบความสมบูรณ์ของข้อมูล', '3. บันทึกรายละเอียดข้อสอบลงฐานข้อมูล', 'จบการทำงาน']
    },
    'Process 3.2 สร้างเกณฑ์ด้วย AI': {
        'id': '3.2', 'name': 'สร้างเกณฑ์ด้วย AI', 'desc': 'ใช้ AI ช่วยแยกแยะและสร้างเกณฑ์รูบริค',
        'logic': ['เริ่มต้น', '1. รับข้อความและเงื่อนไขการให้คะแนนจากผู้สอน', '2. ส่งข้อมูลไปยัง AI API เพื่อวิเคราะห์เกณฑ์', '3. รับผลลัพธ์เกณฑ์การประเมินจาก AI', '4. แสดงผลให้ผู้สอนตรวจสอบและยืนยัน', 'จบการทำงาน']
    },
    'Process 4.1 เริ่มทำข้อสอบ': {
        'id': '4.1', 'name': 'เริ่มทำข้อสอบ', 'desc': 'ตรวจสอบสิทธิ์และดึงข้อมูลข้อสอบให้ผู้เรียน',
        'logic': ['เริ่มต้น', '1. รับคำร้องขอทำข้อสอบจากผู้เรียน', '2. ตรวจสอบเวลาและสิทธิ์ในการทำข้อสอบ', '&nbsp;&nbsp;&nbsp;&nbsp;2.1 ถ้าอยู่ในเวลาที่กำหนด ให้ดึงข้อมูลโจทย์ข้อสอบมาแสดง', '&nbsp;&nbsp;&nbsp;&nbsp;2.2 ถ้าหมดเวลา ไม่อนุญาตให้ทำข้อสอบ', 'จบการทำงาน']
    },
    'Process 4.2 ส่งคำตอบ': {
        'id': '4.2', 'name': 'ส่งคำตอบ', 'desc': 'บันทึกคำตอบของนักเรียนเข้าสู่ระบบ',
        'logic': ['เริ่มต้น', '1. รับข้อมูลคำตอบจากผู้เรียน', '2. จัดรูปแบบและตรวจสอบความครบถ้วน', '3. บันทึกคำตอบลงแฟ้มข้อมูลคำตอบ', '4. อัปเดตสถานะการส่งข้อสอบ', 'จบการทำงาน']
    },
    'Process 5.1 เตรียมข้อมูลตรวจ': {
        'id': '5.1', 'name': 'เตรียมข้อมูลตรวจ', 'desc': 'ดึงคำตอบและเกณฑ์ที่เกี่ยวข้องเตรียมส่งให้ AI',
        'logic': ['เริ่มต้น', '1. ตรวจสอบแฟ้มข้อมูลเพื่อค้นหาคำตอบที่เพิ่งส่ง', '2. ดึงข้อมูลคำตอบและเกณฑ์รูบริคที่เกี่ยวข้อง', '3. จัดฟอร์แมตข้อมูลให้อยู่ในรูปแบบที่ API ต้องการ', 'จบการทำงาน']
    },
    'Process 5.2 ประเมินคำตอบด้วย AI': {
        'id': '5.2', 'name': 'ประเมินคำตอบด้วย AI', 'desc': 'ส่งคำตอบและเกณฑ์ไปให้ AI ตรวจสอบ',
        'logic': ['เริ่มต้น', '1. รับข้อมูลที่ถูกจัดฟอร์แมตแล้ว', '2. เชื่อมต่อและส่งข้อมูลไปยัง Gemini API', '3. รอรับผลลัพธ์การประเมินดิบกลับมา', 'จบการทำงาน']
    },
    'Process 5.3 สรุปผลการประเมิน': {
        'id': '5.3', 'name': 'สรุปผลการประเมิน', 'desc': 'รับผลดิบจาก AI มาแปลงเป็นคะแนนที่ใช้งานได้',
        'logic': ['เริ่มต้น', '1. รับผลการประเมินดิบจาก AI', '2. ตรวจสอบโครงสร้างและแยกแยะคะแนนและคอมเมนต์', '3. จัดโครงสร้างข้อมูลให้อยู่ในรูปแบบมาตราฐาน', 'จบการทำงาน']
    },
    'Process 5.4 บันทึกคะแนนจาก AI': {
        'id': '5.4', 'name': 'บันทึกคะแนนจาก AI', 'desc': 'บันทึกผลการประเมินสำเร็จลงฐานข้อมูล',
        'logic': ['เริ่มต้น', '1. รับข้อมูลผลการประเมินที่จัดรูปแบบแล้ว', '2. อัปเดตคะแนนและคอมเมนต์ลงในแฟ้มข้อมูลคำตอบ', 'จบการทำงาน']
    },
    'Process 6.0 ตรวจสอบและประกาศผลคะแนน': {
        'id': '6.0', 'name': 'ตรวจสอบและประกาศผลคะแนน', 'desc': 'ผู้สอนตรวจสอบและอนุมัติผลคะแนน',
        'logic': ['เริ่มต้น', '1. ดึงผลคะแนนรวมและรายข้อมาแสดงให้ผู้สอนดู', '2. รับการตรวจสอบและแก้ไขจากผู้สอน', '3. รับคำสั่งยืนยันการประกาศผลคะแนน', '4. อัปเดตสถานะให้ผู้เรียนสามารถดูผลสอบได้', 'จบการทำงาน']
    },
    'Process 7.0 จัดการแจ้งเตือนและส่งออกสถิติ': {
        'id': '7.0', 'name': 'จัดการแจ้งเตือนและส่งออกสถิติ', 'desc': 'ส่งการแจ้งเตือนสถานะและทำรายงานสถิติ',
        'logic': ['เริ่มต้น', '1. ตรวจสอบเหตุการณ์ใหม่ในระบบ (เช่น คะแนนออก, มีประกาศ)', '2. สร้างข้อความแจ้งเตือนและส่งให้ผู้เรียน/ผู้สอนที่เกี่ยวข้อง', '3. หากมีคำสั่งส่งออกสถิติ ให้ประมวลผลคะแนนแล้วออกรายงาน', 'จบการทำงาน']
    }
}

html_tables = ""

# Match exact names from flows_data or partial match for 5.1, 5.2, 5.3, 5.4
def get_flows_for_process(target_proc_id):
    inputs = set()
    outputs = set()
    for f_name, connections in flows_data.items():
        for src, dst in connections:
            if target_proc_id in dst:
                inputs.add(f_name)
            if target_proc_id in src:
                outputs.add(f_name)
    return sorted(list(inputs)), sorted(list(outputs))

# Order of iteration
sorted_targets = sorted(target_processes.keys())
index = 1

for t_key in sorted_targets:
    p_info = target_processes[t_key]
    pid = p_info['id']
    pname = p_info['name']
    pdesc = p_info['desc']
    plogic = p_info['logic']
    
    in_flows, out_flows = get_flows_for_process('Process ' + pid)
    
    in_html = '<br>'.join([f'- {x}' for x in in_flows]) if in_flows else '-'
    out_html = '<br>'.join([f'- {x}' for x in out_flows]) if out_flows else '-'
    logic_html = '<br>'.join(plogic)
    
    table = f'''
    <div style="page-break-inside: avoid;">
    <h3 style="color: #000; margin-top: 30px; font-weight: normal;">3.8.{index} Process {pname}</h3>
    <table>
        <tr>
            <th style="width: 25%; text-align: left; background-color: #BFBFBF; color: #000;">Number</th>
            <td style="text-align: left;">{pid}</td>
        </tr>
        <tr>
            <th style="text-align: left; background-color: #BFBFBF; color: #000;">Name</th>
            <td style="text-align: left;">{pname}</td>
        </tr>
        <tr>
            <th style="text-align: left; background-color: #BFBFBF; color: #000;">Description</th>
            <td style="text-align: left;">{pdesc}</td>
        </tr>
        <tr>
            <th style="text-align: left; background-color: #BFBFBF; color: #000; vertical-align: top;">Input data flow</th>
            <td style="text-align: left; vertical-align: top; line-height: 1.8;">{in_html}</td>
        </tr>
        <tr>
            <th style="text-align: left; background-color: #BFBFBF; color: #000; vertical-align: top;">Output data flow</th>
            <td style="text-align: left; vertical-align: top; line-height: 1.8;">{out_html}</td>
        </tr>
        <tr>
            <th style="text-align: left; background-color: #BFBFBF; color: #000; vertical-align: top;">Process description</th>
            <td style="text-align: left; vertical-align: top; line-height: 1.8;">{logic_html}</td>
        </tr>
    </table>
    </div>
    '''
    html_tables += table
    index += 1

html_template = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>3.8 คำอธิบายการประมวลผล (Process Description)</title>
    <style>
        body {{ font-family: 'Sarabun', Tahoma, sans-serif; padding: 40px; background-color: #ffffff; color: #000; max-width: 900px; margin: 0 auto; }}
        h2 {{ text-align: left; font-size: 18px; margin-bottom: 20px; font-weight: normal; color: #000; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 15px; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #000; padding: 10px 15px; vertical-align: middle; }}
        th {{ font-weight: normal; }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <h2>3.8 คำอธิบายการประมวลผล (Process Description)</h2>
    {html_tables}
</body>
</html>'''

with io.open('process_description_evaly.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Generated new process_description_evaly.html successfully!")
