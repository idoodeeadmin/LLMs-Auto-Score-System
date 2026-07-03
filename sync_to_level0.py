import re
from bs4 import BeautifulSoup

def sync_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Global replacements for specific strings
    replacements = {
        'ข้อมูลโครงสร้างเกณฑ์การประเมิน': 'โครงสร้างเกณฑ์การประเมิน',
        'ข้อมูลผลการประเมินและข้อเสนอแนะ': 'ผลการประเมินและข้อเสนอแนะอัจฉริยะ',
        'ไฟล์รายงานสรุปคะแนน (CSV/Excel)': 'ไฟล์รายงานสรุปคะแนน',
        'ข้อมูลคำอธิบายและข้อเสนอแนะโครงสร้างประเมิน': 'คำอธิบาย ข้อเสนอแนะ และข้อมูลโครงสร้างประเมินรายด้าน',
        'ข้อมูลระดับความมั่นใจของคำตอบ': 'ระดับความมั่นใจของคำตอบ',
        'ข้อมูล Authentication Token': 'Authentication Token',
        'ข้อมูลการยืนยันและประกาศผลคะแนน': 'ข้อมูลคำสั่งยืนยันและประกาศผลคะแนน',
        'ข้อมูลคำขอออกรายงานสถิติ': 'ข้อมูลคำขอออกรายงานสถิติ', # This is actually correct in L0 image "ข้อมูลคำขอออกรายงานสถิติ"
        'ข้อมูลคำสั่งสร้างโครงสร้างเกณฑ์การประเมิน': 'ข้อมูลคำสั่งสร้างโครงสร้างเกณฑ์การประเมิน',
        'ข้อมูลการดึงข้อสอบจากคลัง': 'ข้อมูลการดึงข้อสอบจากคลัง', # This is internal, so it can stay as is
    }
    
    for flow_text_div in soup.find_all('div', class_='flow-text'):
        text = flow_text_div.get_text(strip=True)
        
        # Exact string replacements
        if text in replacements:
            flow_text_div.string = replacements[text]
            
    # 2. Specific Entity Connection fixes
    for entity_conn in soup.find_all('div', class_='entity-conn'):
        entity_box = entity_conn.find('div', class_='entity-box')
        if not entity_box: continue
        entity_name = entity_box.get_text(strip=True)
        
        flows = entity_conn.find('div', class_='flows')
        if not flows: continue
        
        for flow_item in flows.find_all('div', class_='flow-item'):
            flow_text_div = flow_item.find('div', class_='flow-text')
            if not flow_text_div: continue
            
            text = flow_text_div.get_text(strip=True)
            
            # If flow goes to ผู้เรียน or ผู้สอน
            if 'ผู้เรียน' in entity_name or 'ผู้สอน' in entity_name:
                if 'แจ้งเตือน' in text and 'อ่าน' not in text: # If it's an output to user about notification
                    # Level 0 says "ข้อมูลการแจ้งเตือนแบบเรียลไทม์"
                    flow_text_div.string = 'ข้อมูลการแจ้งเตือนแบบเรียลไทม์'
                if text == 'ข้อมูลผลการประเมินจาก AI':
                    flow_text_div.string = 'ผลการประเมินและข้อเสนอแนะอัจฉริยะ'
                
                # Check for "ข้อมูลสถานะการทำรายการบัญชีและโปรไฟล์" which is correct
                # Check for "ข้อมูลสถานะการเข้าสู่ระบบและToken" which is correct
                # Wait, image says "ข้อมูลสถานะการเข้าสู่ระบบและ Token" for ผู้สอน, but without space for ผู้เรียน. Let's just use "ข้อมูลสถานะการเข้าสู่ระบบและToken".

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == '__main__':
    sync_html('dfd_level1_evaly.html')
    sync_html('dfd_level2_all_evaly.html')
