import os
import re
from bs4 import BeautifulSoup
import codecs

def get_dfd_flows_with_endpoints():
    flows = {}
    for f in ['dfd_level0_evaly.html', 'dfd_level1_evaly.html', 'dfd_level2_all_evaly.html']:
        if not os.path.exists(f): continue
        with open(f, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            # Extract connections. Looking at previous extraction, maybe we can just parse the visual layout.
            # Usually flow-text is inside a .flow-item which has arrows indicating direction.
            # Or we can just read parsed_flows_correct.json or all_flows.json
            pass
    return flows

def get_connections_from_json():
    # If all_flows.json or extracted_connections.json exists, we can use it.
    connections = {}
    try:
        with open('extracted_connections.json', 'r', encoding='utf-8') as file:
            data = __import__('json').load(file)
            for item in data:
                # "From", "To", "Data Flow"
                name = item.get('Data Flow', '').strip()
                if name:
                    if name not in connections:
                        connections[name] = []
                    connections[name].append((item.get('From', '').strip(), item.get('To', '').strip()))
    except Exception as e:
        print(f"Could not load extracted_connections.json: {e}")
    return connections

def main():
    dict_file = 'data_flow_dict_evaly.html'
    with open(dict_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    tbody = table.find('tbody')
    if not tbody:
        print("No tbody found in dict.")
        return
        
    ds_map = {
        'D1': 'ข้อมูลผู้ใช้', 'D2': 'ข้อมูลห้องเรียน', 'D3': 'ข้อมูลสมาชิกห้องเรียน',
        'D4': 'ข้อมูลข้อสอบ', 'D5': 'ข้อมูลข้อคำถามและเกณฑ์', 'D6': 'ข้อมูลการส่งข้อสอบ',
        'D7': 'ข้อมูลคำตอบรายข้อ', 'D8': 'ข้อมูลประกาศข่าวสาร', 'D9': 'ข้อมูลการแจ้งเตือน'
    }
    
    tr_list = tbody.find_all('tr', recursive=False)
    existing_flows = set()
    
    # 1. Update existing structures
    for tr in tr_list:
        tds = tr.find_all('td', recursive=False)
        if len(tds) >= 4:
            name_td = tds[0]
            name = name_td.get_text(strip=True)
            existing_flows.add(name)
            
            src_dest_td = tds[2]
            struct_td = tds[-1]
            struct_text = struct_td.get_text(strip=True)
            
            # extract sources and dests
            inner = src_dest_td.find('table')
            endpoints = []
            if inner:
                for itr in inner.find_all('tr'):
                    itds = itr.find_all('td')
                    if len(itds) == 2:
                        endpoints.append(itds[0].get_text(strip=True))
                        endpoints.append(itds[1].get_text(strip=True))
            
            touches_ds = False
            for ep in endpoints:
                # check if D1, D2 etc or contains ds name
                if re.match(r'^D\d+', ep):
                    touches_ds = True
                    break
                for ds_name in ds_map.values():
                    if ds_name in ep:
                        touches_ds = True
                        break
                        
            if not touches_ds and 'ไม่มีในแฟ้มข้อมูล' not in struct_text:
                # Append to struct
                if struct_td.string:
                    struct_td.string.replace_with(struct_text + " *(ไม่มีในแฟ้มข้อมูล)*")
                else:
                    struct_td.clear()
                    struct_td.append(struct_text + " *(ไม่มีในแฟ้มข้อมูล)*")
    
    # 2. Add missing flows
    missing_flows = [
        "ข้อมูลการแจ้งเตือนใหม่", "ข้อมูลคะแนนทางการ", "ข้อมูลคำตอบรายข้อ",
        "ข้อมูลบัญชีผู้ใช้เพื่อตรวจสอบ", "ข้อมูลบัญชีผู้ใช้และโปรไฟล์", "ข้อมูลประกาศข่าวสาร",
        "ข้อมูลประวัติการแจ้งเตือน", "ข้อมูลผลการประเมินจาก AI", "ข้อมูลผลการประเมินที่จัดรูปแบบแล้ว",
        "ข้อมูลผลคะแนนที่อนุมัติ", "ข้อมูลผลคะแนนที่แก้ไข", "ข้อมูลผลคะแนนรวม",
        "ข้อมูลผลคะแนนรายข้อ", "ข้อมูลผลคะแนนรายข้อและคอมเมนต์", "ข้อมูลพร้อมตรวจ",
        "ข้อมูลยืนยันตัวตน", "ข้อมูลรายละเอียดข้อสอบ", "ข้อมูลรายละเอียดห้องเรียน",
        "ข้อมูลสถานะการส่ง", "ข้อมูลสถานะการอ่านประกาศ", "ข้อมูลสถานะการอ่านล่าสุด",
        "ข้อมูลสถานะอนุมัติ", "ข้อมูลสมาชิกห้องเรียน", "ข้อมูลโจทย์และเกณฑ์", "ผลการประเมินดิบ"
    ]
    
    connections = get_connections_from_json()
    
    for flow in missing_flows:
        if flow in existing_flows:
            continue
            
        desc = f"ข้อมูลที่เกี่ยวข้องกับ {flow}"
        
        flow_conns = connections.get(flow, [])
        if not flow_conns:
            flow_conns = [('ไม่ระบุ', 'ไม่ระบุ')]
            
        # Determine if it touches DS
        touches_ds = False
        for src, dest in flow_conns:
            if re.match(r'^D\d+', src) or re.match(r'^D\d+', dest): touches_ds = True
            for ds_name in ds_map.values():
                if ds_name in src or ds_name in dest: touches_ds = True
                
        struct = "(รอระบุโครงสร้างข้อมูล)"
        if not touches_ds:
            struct += " *(ไม่มีในแฟ้มข้อมูล)*"
            
        # Create new tr
        new_tr = soup.new_tag('tr')
        
        # Name
        td_name = soup.new_tag('td', style="text-align: left;")
        td_name.string = flow
        new_tr.append(td_name)
        
        # Description
        td_desc = soup.new_tag('td', **{'class': 'text-left'})
        td_desc.string = desc
        new_tr.append(td_desc)
        
        # Source / Destination
        td_src_dst = soup.new_tag('td', colspan="2", style="padding: 0;")
        inner_table = soup.new_tag('table', **{'class': 'inner-table'})
        
        for src, dest in flow_conns:
            itr = soup.new_tag('tr')
            itd_src = soup.new_tag('td')
            itd_src.string = src
            itr.append(itd_src)
            itd_dst = soup.new_tag('td')
            itd_dst.string = dest
            itr.append(itd_dst)
            inner_table.append(itr)
            
        td_src_dst.append(inner_table)
        new_tr.append(td_src_dst)
        
        # Structure
        td_struct = soup.new_tag('td')
        td_struct.string = struct
        new_tr.append(td_struct)
        
        tbody.append(new_tr)
        
    # Write back
    with open('data_flow_dict_evaly_fixed.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("Done. Created data_flow_dict_evaly_fixed.html")

if __name__ == '__main__':
    main()
