import os
import json
from bs4 import BeautifulSoup
import re

def get_connections_from_json():
    connections = {}
    try:
        with open('extracted_connections.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                name = item.get('flow', '').strip()
                if name:
                    if name not in connections:
                        connections[name] = []
                    for c in item.get('connections', []):
                        if len(c) == 2:
                            connections[name].append((c[0], c[1]))
    except Exception as e:
        print(f"Could not load extracted_connections.json: {e}")
    return connections

def main():
    dict_file = 'data_flow_dict_evaly.html'
    with open(dict_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    if not table: return
    tbody = table.find('tbody')
    if not tbody: return
        
    ds_map = {
        'D1': 'ข้อมูลผู้ใช้', 'D2': 'ข้อมูลห้องเรียน', 'D3': 'ข้อมูลสมาชิกห้องเรียน',
        'D4': 'ข้อมูลข้อสอบ', 'D5': 'ข้อมูลข้อคำถามและเกณฑ์', 'D6': 'ข้อมูลการส่งข้อสอบ',
        'D7': 'ข้อมูลคำตอบรายข้อ', 'D8': 'ข้อมูลประกาศข่าวสาร', 'D9': 'ข้อมูลการแจ้งเตือน'
    }
    
    connections = get_connections_from_json()
    
    tr_list = tbody.find_all('tr', recursive=False)
    
    for tr in tr_list:
        tds = tr.find_all('td', recursive=False)
        if len(tds) >= 4:
            name_td = tds[0]
            name = name_td.get_text(strip=True)
            
            src_dest_td = tds[2]
            inner_table = src_dest_td.find('table')
            if not inner_table: continue
            
            # check if it has "ไม่ระบุ"
            first_text = inner_table.get_text(strip=True)
            if 'ไม่ระบุ' in first_text:
                flow_conns = connections.get(name, [])
                if not flow_conns:
                    flow_conns = [('ไม่ระบุ', 'ไม่ระบุ')]
                    
                # Rebuild inner table
                inner_table.clear()
                for src, dest in flow_conns:
                    itr = soup.new_tag('tr')
                    itd_src = soup.new_tag('td')
                    itd_src.string = src
                    itr.append(itd_src)
                    itd_dst = soup.new_tag('td')
                    itd_dst.string = dest
                    itr.append(itd_dst)
                    inner_table.append(itr)
                    
                # Check touches DS and update struct if needed
                struct_td = tds[-1]
                struct_text = struct_td.get_text(strip=True)
                
                touches_ds = False
                for src, dest in flow_conns:
                    if re.match(r'^D\d+', src) or re.match(r'^D\d+', dest): touches_ds = True
                    for ds_name in ds_map.values():
                        if ds_name in src or ds_name in dest: touches_ds = True
                
                new_struct = struct_text.replace(' *(ไม่มีในแฟ้มข้อมูล)*', '')
                if not touches_ds:
                    new_struct += ' *(ไม่มีในแฟ้มข้อมูล)*'
                    
                struct_td.string = new_struct
                
    with open('data_flow_dict_evaly_fixed2.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("Fixed.")

if __name__ == '__main__':
    main()
