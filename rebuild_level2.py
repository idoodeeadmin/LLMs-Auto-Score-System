import json
from bs4 import BeautifulSoup

def make_entity_conn(entity_name, flows):
    html = f'<div class="entity-conn">\\n<div class="entity-box"><div class="duplicated-mark"></div>{entity_name}</div>\\n<div class="flows">\\n'
    for direction, text in flows:
        if direction == "in":
            arrow = '<div class="arrow-r"></div>'
        else:
            arrow = '<div class="arrow-l"></div>'
        html += f'<div class="flow-item"><div class="flow-line">{arrow}</div><div class="flow-text">{text}</div></div>\\n'
    html += '</div>\\n</div>'
    return html

mappings = {
    "1.1": [
        ("ผู้ใช้งานทั่วไป", [("in", "ข้อมูลการสมัครสมาชิก"), ("out", "ข้อมูลบัญชีผู้ใช้")])
    ],
    "1.2": [
        ("ผู้ใช้งานทั่วไป", [("in", "ข้อมูลการเข้าสู่ระบบ"), ("out", "ข้อมูลสถานะการเข้าสู่ระบบ")]),
        ("Firebase Auth", [("in", "Authentication Token"), ("in", "ข้อมูลโปรไฟล์ผู้ใช้"), ("out", "ข้อมูลคำขอตรวจสอบสิทธิ์การเข้าถึง"), ("out", "ข้อมูลคำขอเข้าสู่ระบบด้วยบัญชี Google")])
    ],
    "1.3": [
        ("ผู้เรียน", [("in", "ข้อมูลโปรไฟล์ที่เพิ่มและแก้ไข"), ("out", "ข้อมูลบัญชีผู้ใช้")]),
        ("ผู้สอน", [("in", "ข้อมูลโปรไฟล์และรูปภาพที่เพิ่มและแก้ไข"), ("out", "ข้อมูลบัญชีผู้ใช้")]),
        ("Cloudinary API", [("in", "ข้อมูล URL และสถานะการจัดเก็บรูปภาพ"), ("out", "ข้อมูลไฟล์รูปภาพโปรไฟล์")])
    ],
    "1.4": [
        ("ผู้ใช้งานทั่วไป", [("in", "ข้อมูลคำขอรีเซ็ตรหัสผ่าน"), ("in", "ข้อมูลการยืนยันตัวตนทางอีเมล")]),
        ("SMTP", [("in", "ข้อมูลสถานะการส่งอีเมล"), ("out", "ข้อมูลอีเมลและลิงก์รีเซ็ตรหัสผ่าน"), ("out", "ข้อมูลอีเมลและลิงก์ยืนยันตัวตน")])
    ],
    "2.1": [
        ("ผู้สอน", [("in", "ข้อมูลห้องเรียนที่เพิ่มและแก้ไข"), ("in", "ข้อมูลห้องเรียนที่ลบ"), ("out", "ข้อมูลห้องเรียน")]),
        ("ผู้เรียน", [("out", "ข้อมูลห้องเรียน")])
    ],
    "2.2": [
        ("ผู้เรียน", [("in", "ข้อมูลคำขอเข้าร่วมห้องเรียนพร้อมรหัสคลาส")]),
        ("ผู้สอน", [("out", "ข้อมูลสมาชิกในห้องเรียนและสถานะการส่งงาน")])
    ],
    "2.3": [
        ("ผู้สอน", [("in", "ข้อมูลประกาศข่าวสารห้องเรียนที่เพิ่มและแก้ไข"), ("in", "ข้อมูลประกาศข่าวสารห้องเรียนที่ลบ"), ("out", "ข้อมูลประกาศข่าวสารห้องเรียน")]),
        ("ผู้เรียน", [("out", "ข้อมูลประกาศข่าวสารห้องเรียน")])
    ],
    "3.1": [
        ("ผู้สอน", [("in", "ข้อมูลข้อสอบที่เพิ่มและแก้ไข"), ("in", "ข้อมูลข้อสอบที่ลบ"), ("out", "ข้อมูลข้อสอบ")])
    ],
    "3.2": [
        ("Cloudinary API", [("in", "ข้อมูล URL และสถานะการจัดเก็บรูปภาพ"), ("out", "ข้อมูลไฟล์รูปภาพโจทย์ข้อสอบ"), ("out", "ข้อมูลคำขอปรับแต่งรูปภาพ")])
    ],
    "3.3": [
        ("ผู้สอน", [("in", "ข้อมูลเกณฑ์การประเมินที่เพิ่มและแก้ไข"), ("in", "ข้อมูลเกณฑ์การประเมินที่ลบ"), ("out", "ข้อมูลร่างเกณฑ์การให้คะแนนจาก AI")]),
        ("Gemini API", [("in", "ข้อมูลเกณฑ์รูบริคอัตโนมัติ"), ("out", "ข้อมูลคำสั่งสร้างเกณฑ์ประเมิน")])
    ],
    "4.1": [
        ("ผู้เรียน", [("out", "ข้อมูลเวลาคงเหลือในการสอบ"), ("out", "ข้อมูลข้อสอบ")])
    ],
    "4.2": [
        ("ผู้เรียน", [("in", "ข้อมูลคำตอบข้อสอบ")])
    ],
    "4.3": [
        ("ผู้เรียน", [("in", "ข้อมูลการส่งข้อสอบ"), ("out", "ข้อมูลสถานะการส่งข้อสอบ")]),
        ("ผู้สอน", [("out", "ข้อมูลรายการส่งข้อสอบ")]),
        ("Cloudinary API", [("in", "ข้อมูล URL และสถานะการจัดเก็บรูปภาพ"), ("out", "ข้อมูลไฟล์รูปภาพคำตอบลายมือเขียน")])
    ],
    "5.1": [],
    "5.2": [
        ("Gemini API", [("in", "ข้อมูลผลการประเมิน"), ("in", "ข้อมูลข้อเสนอแนะการประเมิน"), ("in", "ข้อมูลระดับความมั่นใจของคำตอบ"), ("out", "ข้อมูลโจทย์ข้อสอบและเกณฑ์การให้คะแนน"), ("out", "ข้อมูลคำตอบของนักเรียน"), ("out", "ข้อมูลคำสั่งและเงื่อนไขการตรวจประเมิน")])
    ],
    "5.3": [],
    "6.1": [
        ("ผู้สอน", [("out", "ข้อมูลคำตอบของนักเรียน"), ("out", "ข้อมูลผลการประเมินและข้อเสนอแนะอัจฉริยะ")])
    ],
    "6.2": [
        ("ผู้สอน", [("in", "ข้อมูลคะแนนและคอมเมนต์ที่เพิ่มและแก้ไข"), ("in", "ข้อมูลการอนุมัติผลคะแนน")])
    ],
    "6.3": [
        ("ผู้เรียน", [("out", "ข้อมูลผลคะแนน"), ("out", "ข้อมูลผลการประเมินและข้อเสนอแนะ")])
    ],
    "7.1": [
        ("ผู้เรียน", [("out", "ข้อมูลการแจ้งเตือน")]),
        ("ผู้สอน", [("out", "ข้อมูลการแจ้งเตือน")])
    ],
    "7.2": [
        ("ผู้สอน", [("in", "ข้อมูลคำขอออกรายงานสถิติ"), ("out", "ข้อมูลรายงานสรุปคะแนน"), ("out", "ข้อมูลประวัติการแก้ไขคะแนน")]),
        ("ผู้เรียน", [("out", "ข้อมูลประวัติการทำข้อสอบ")])
    ]
}

def rebuild():
    with open('dfd_level2_all_evaly.html', 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    for row in soup.find_all('div', class_='dfd-row'):
        pid_div = row.find('div', class_='p-id')
        if not pid_div: continue
        pid = pid_div.get_text(strip=True)
        
        if pid in mappings:
            col_left = row.find('div', class_='col-left')
            if col_left:
                # Remove all existing external entity blocks
                for entity_conn in col_left.find_all('div', class_='entity-conn'):
                    entity_conn.decompose()
                
                # We need to prepend the new entity blocks. 
                # Let's create a temporary soup to parse the new HTML
                new_html = ""
                for entity_name, flows in mappings[pid]:
                    new_html += make_entity_conn(entity_name, flows)
                
                new_soup = BeautifulSoup(new_html, 'html.parser')
                # Insert at the beginning of col_left
                col_left.insert(0, new_soup)

    with open('dfd_level2_all_evaly.html', 'w', encoding='utf-8') as f:
        # Use str(soup) to keep it formatted, then we can run a prettier if needed
        f.write(str(soup))

if __name__ == '__main__':
    rebuild()
