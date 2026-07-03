import re
from bs4 import BeautifulSoup

def clean_verbs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    replacements = {
        'คำสั่งเตรียมส่งอีเมล': 'ข้อมูลเตรียมการส่งอีเมล',
        'คำขอจัดการสมาชิกห้องเรียน': 'ข้อมูลการจัดการสมาชิกห้องเรียน',
        'คำสั่งให้ AI สร้างเกณฑ์อัตโนมัติ': 'ข้อมูลเงื่อนไขการสร้างเกณฑ์อัตโนมัติ',
        'คำสั่งดึงข้อสอบไปใช้งาน': 'ข้อมูลการดึงข้อสอบจากคลัง',
        'คำขอเริ่มทำข้อสอบ': 'ข้อมูลคำขอเริ่มทำข้อสอบ',
        'คำขอตรวจสอบประวัติการทำข้อสอบ': 'ข้อมูลคำขอตรวจสอบประวัติการทำข้อสอบ',
        'คำสั่งยืนยันและประกาศผลคะแนน': 'ข้อมูลการยืนยันและประกาศผลคะแนน',
        'คำขออัปเดตสถานะการอ่านแจ้งเตือน': 'ข้อมูลสถานะการอ่านแจ้งเตือน',
        'คำสั่งขอส่งออกข้อมูลสถิติ': 'ข้อมูลคำขอออกรายงานสถิติ',
        'ไฟล์รูปภาพลายมือคำตอบ': 'ข้อมูลไฟล์รูปภาพคำตอบลายมือเขียน',
        'ผลการประเมินคะแนนและข้อเสนอแนะจาก AI': 'ข้อมูลผลการประเมินจาก AI',
        'ผลการประเมินและข้อเสนอแนะอัจฉริยะ': 'ข้อมูลผลการประเมินและข้อเสนอแนะ',
        'คำอธิบาย ข้อเสนอแนะ และข้อมูลโครงสร้างประเมินรายด้าน': 'ข้อมูลคำอธิบายและข้อเสนอแนะโครงสร้างประเมิน',
        'ระดับความมั่นใจของคำตอบ': 'ข้อมูลระดับความมั่นใจของคำตอบ',
        'Authentication Token': 'ข้อมูล Authentication Token',
        'โครงสร้างเกณฑ์การประเมิน': 'ข้อมูลโครงสร้างเกณฑ์การประเมิน'
    }
    
    for flow_text_div in soup.find_all('div', class_='flow-text'):
        text = flow_text_div.get_text(strip=True)
        
        # Exact matches
        if text in replacements:
            flow_text_div.string = replacements[text]
        # Generic prefix fixing
        elif text.startswith('คำสั่ง'):
            flow_text_div.string = 'ข้อมูล' + text[6:]
        elif text.startswith('คำขอ'):
            flow_text_div.string = 'ข้อมูล' + text
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == '__main__':
    clean_verbs('dfd_level1_evaly.html')
    clean_verbs('dfd_level2_all_evaly.html')
