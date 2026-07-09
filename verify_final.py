import os
from bs4 import BeautifulSoup
import codecs

def parse_html_table(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    if not table: return []
    
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr', recursive=False) if tbody else table.find_all('tr', recursive=False)[1:]
    
    rows = []
    for tr in tr_list:
        tds = tr.find_all('td', recursive=False)
        if len(tds) >= 4:
            name = tds[0].get_text(strip=True)
            desc = tds[1].get_text(strip=True)
            struct = tds[-1].get_text(strip=True)
            
            # Extract source/dest from inner table
            src_dest_td = tds[2]
            inner = src_dest_td.find('table')
            sources = []
            dests = []
            if inner:
                for itr in inner.find_all('tr'):
                    itds = itr.find_all('td')
                    if len(itds) == 2:
                        sources.append(itds[0].get_text(strip=True))
                        dests.append(itds[1].get_text(strip=True))
            
            rows.append({
                'Name': name,
                'Structure': struct,
                'Sources': sources,
                'Destinations': dests
            })
    return rows

def parse_dfd_flows():
    flows = set()
    for f in ['dfd_level0_evaly.html', 'dfd_level1_evaly.html', 'dfd_level2_all_evaly.html']:
        with open(f, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            for el in soup.find_all('div', class_='flow-text'):
                text = el.get_text(strip=True)
                if text: flows.add(text)
    return flows

def parse_ds():
    with open('datastore_description_evaly.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    table = soup.find('table')
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr', recursive=False)
    ds_map = {}
    for tr in tr_list:
        tds = tr.find_all('td', recursive=False)
        if len(tds) >= 3:
            name = tds[1].get_text(strip=True)
            struct = tds[-1].get_text(strip=True)
            ds_map[name] = struct
    return ds_map

def main():
    dict_rows = parse_html_table('data_flow_dict_evaly.html')
    dfd_flows = parse_dfd_flows()
    ds_map = parse_ds()
    
    dict_flow_names = {r['Name'] for r in dict_rows if r['Name']}
    
    with codecs.open('verify_final.txt', 'w', 'utf-8') as out:
        out.write("=== 1. ตรวจสอบ Data Flow Lines ===\n\n")
        
        missing_in_dfd = sorted(list(dict_flow_names - dfd_flows))
        out.write("เส้นที่มีใน Data Flow Dictionary แต่ *ไม่มี* ในรูป DFD Level 0-2 (เส้นขาดหาย หรือชื่อไม่ตรง):\n")
        for m in missing_in_dfd: out.write(f" - {m}\n")
        if not missing_in_dfd: out.write(" - ไม่มี (ครบถ้วน)\n")
        
        missing_in_dict = sorted(list(dfd_flows - dict_flow_names))
        out.write("\nเส้นที่มีในรูป DFD Level 0-2 แต่ *ไม่มี* ใน Data Flow Dictionary (เส้นงอกขึ้นมา หรือชื่อไม่ตรง):\n")
        for m in missing_in_dict: out.write(f" - {m}\n")
        if not missing_in_dict: out.write(" - ไม่มี (ครบถ้วน)\n")
        
        out.write("\n\n=== 2. ตรวจสอบ Data Structure และ Data Store ===\n\n")
        for r in dict_rows:
            name = r['Name']
            if not name: continue
            struct = r['Structure']
            srcs = r['Sources']
            dsts = r['Destinations']
            
            out.write(f"Flow: {name}\n")
            
            # Find if this flow touches any data store in the dictionary definition
            ds_touched = set()
            for s in srcs + dsts:
                if s.startswith('D') and len(s) > 1 and s[1].isdigit():
                    ds_touched.add(s)
                # also fuzzy check if ds name is in the source/dest
                for d_name in ds_map.keys():
                    if d_name in s: ds_touched.add(d_name)
                    
            if not ds_touched:
                if 'ไม่มีในแฟ้มข้อมูล' in struct:
                    out.write(" => ถูกต้อง: ไม่ได้เก็บใน Data Store (และระบุไว้ใน Dictionary ชัดเจน)\n")
                else:
                    out.write(" => ข้อสังเกต: ไม่ได้เชื่อมต่อกับ Data Store (แต่ไม่ได้ระบุ '*(ไม่มีในแฟ้มข้อมูล)*')\n")
            else:
                out.write(f" => เชื่อมต่อกับ Data Store: {', '.join(ds_touched)}\n")
                # Structure check
                for dt in ds_touched:
                    clean_dt = dt.split(' - ')[-1] if ' - ' in dt else dt
                    matched_ds = None
                    for k in ds_map.keys():
                        if k.lower() in clean_dt.lower() or clean_dt.lower() in k.lower():
                            matched_ds = k; break
                    if matched_ds:
                        ds_struct = ds_map[matched_ds]
                        if struct.replace(' ', '') in ds_struct.replace(' ', '') or ds_struct.replace(' ', '') in struct.replace(' ', ''):
                            out.write(f"    - โครงสร้างตรงกับ {matched_ds}\n")
                        else:
                            out.write(f"    - โครงสร้าง *ไม่ตรง* กับ {matched_ds}\n")
                            out.write(f"      [Flow]: {struct}\n")
                            out.write(f"      [DS]  : {ds_struct}\n")
                    else:
                        out.write(f"    - ไม่พบคำอธิบาย Data Store ชื่อ {dt} ใน Data Store Dictionary\n")
            out.write("\n")

if __name__ == '__main__':
    main()
