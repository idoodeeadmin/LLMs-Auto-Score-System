import re
from bs4 import BeautifulSoup

def fix_flows():
    with open('dfd_level2_all_evaly.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # We only want to replace specific flow texts inside Entity Connections, NOT Data Store Connections.
    
    # Find all entity-conn blocks
    for entity_conn in soup.find_all('div', class_='entity-conn'):
        entity_box = entity_conn.find('div', class_='entity-box')
        if not entity_box: continue
        entity_name = entity_box.get_text(strip=True)
        
        # We only care about flows connected to ผู้เรียน or ผู้สอน
        if 'ผู้เรียน' in entity_name or 'ผู้สอน' in entity_name:
            flows = entity_conn.find('div', class_='flows')
            if not flows: continue
            
            for flow_item in flows.find_all('div', class_='flow-item'):
                flow_text_div = flow_item.find('div', class_='flow-text')
                if not flow_text_div: continue
                
                text = flow_text_div.get_text(strip=True)
                
                # Input flows (arrow pointing right to system)
                if 'ข้อมูลสมัครสมาชิก' == text:
                    flow_text_div.string = 'ข้อมูลการสมัครสมาชิก'
                elif 'ข้อมูลเข้าสู่ระบบ' == text:
                    flow_text_div.string = 'ข้อมูลการเข้าสู่ระบบ'
                    
                # Output flows (arrow pointing left to entity)
                if 'ข้อมูลผู้ใช้งาน' == text:
                    # Determine context by checking siblings or process context
                    # Process 1.2 Login -> ข้อมูลสถานะการเข้าสู่ระบบและToken
                    # Process 1.1 Register & 1.4 Profile -> ข้อมูลสถานะการทำรายการบัญชีและโปรไฟล์
                    # Let's find the closest process name
                    dfd_row = flow_item.find_parent('div', class_='dfd-row')
                    process_name = ''
                    if dfd_row:
                        p_name_div = dfd_row.find('div', class_='p-name')
                        if p_name_div:
                            process_name = p_name_div.get_text(strip=True)
                            
                    if 'เข้าสู่ระบบ' in process_name and 'จัดการ' not in process_name:
                        flow_text_div.string = 'ข้อมูลสถานะการเข้าสู่ระบบและToken'
                    elif 'สมัครสมาชิก' in process_name or 'จัดการข้อมูลโปรไฟล์' in process_name:
                        flow_text_div.string = 'ข้อมูลสถานะการทำรายการบัญชีและโปรไฟล์'

    with open('dfd_level2_all_evaly.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == '__main__':
    fix_flows()
