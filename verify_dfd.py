import json
import os
from bs4 import BeautifulSoup

def parse_html_table(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    if not table:
        return []
    
    headers = []
    thead = table.find('thead')
    if thead:
        headers = [th.get_text(strip=True) for th in thead.find_all('th')]
    
    rows = []
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr') if tbody else table.find_all('tr')[1:]
    
    for tr in tr_list:
        tds = tr.find_all('td', recursive=False)
        if not tds:
            tds = [td for td in tr.find_all('td') if td.find_parent('table') == table or td.find_parent('table') is None]
        
        row_dict = {}
        col_index = 0
        for td in tds:
            inner_tbl = td.find('table', class_='inner-table')
            colspan = int(td.get('colspan', 1))
            
            if inner_tbl:
                pairs = []
                for itr in inner_tbl.find_all('tr'):
                    itds = itr.find_all('td')
                    if len(itds) == 2:
                        pairs.append((itds[0].get_text(strip=True), itds[1].get_text(strip=True)))
                
                # If colspan is 2, it probably covers Source and Destination
                if colspan == 2 and col_index < len(headers):
                    sources = [p[0] for p in pairs]
                    dests = [p[1] for p in pairs]
                    row_dict[headers[col_index]] = sources
                    if col_index + 1 < len(headers):
                        row_dict[headers[col_index+1]] = dests
                    col_index += 2
            else:
                if col_index < len(headers):
                    row_dict[headers[col_index]] = td.get_text(separator=' ', strip=True)
                col_index += colspan
                
        rows.append(row_dict)
    return rows

def parse_dfd_flows(filepath):
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    flows = set()
    for el in soup.find_all('div', class_='flow-text'):
        text = el.get_text(strip=True)
        if text:
            flows.add(text)
    return flows

def main():
    dfd_dict = parse_html_table('data_flow_dict_evaly.html')
    ds_desc = parse_html_table('datastore_description_evaly.html')

    flows_0 = parse_dfd_flows('dfd_level0_evaly.html')
    flows_1 = parse_dfd_flows('dfd_level1_evaly.html')
    flows_2 = parse_dfd_flows('dfd_level2_all_evaly.html')
    
    all_dfd_flows = flows_0.union(flows_1).union(flows_2)
        
    ds_structures = {}
    for row in ds_desc:
        if 'Data Store Name' in row and 'Data Structure' in row:
            ds_name = row['Data Store Name'].strip()
            ds_structures[ds_name] = row['Data Structure'].strip()

    with open("verify_output.txt", "w", encoding="utf-8") as out:
        out.write("=== DFD Dictionary check ===\n")
        
        dict_flows = set()
        missing_in_dfd = []
        
        for row in dfd_dict:
            name = row.get('Name', '')
            if isinstance(name, str):
                name = name.strip()
                if name:
                    dict_flows.add(name)
                    if name not in all_dfd_flows:
                        missing_in_dfd.append(name)
                    
        out.write(f"Total unique flows in DFD levels 0-2 (visual): {len(all_dfd_flows)}\n")
        out.write(f"Total unique flows in Data Flow Dictionary: {len(dict_flows)}\n")
        
        out.write("\n--- Flows in Dictionary but not found in any DFD Level 0-2 ---\n")
        if not missing_in_dfd:
            out.write("None. All dictionary flows exist in DFD levels.\n")
        for m in missing_in_dfd:
            out.write(f" - {m}\n")
            
        out.write("\n--- Flows in DFD Levels but not in Dictionary ---\n")
        missing_in_dict = [f for f in all_dfd_flows if f not in dict_flows]
        if not missing_in_dict:
            out.write("None. All DFD flows are documented in dictionary.\n")
        for m in missing_in_dict:
            out.write(f" - {m}\n")

        out.write("\n=== Data Structure Check ===\n")
        for row in dfd_dict:
            name = row.get('Name', '')
            if not isinstance(name, str) or not name: continue
            name = name.strip()
            struct = row.get('Data Structure', '')
            if not isinstance(struct, str): struct = str(struct)
            struct = struct.strip()
            
            srcs = row.get('Source', [])
            dests = row.get('Destination', [])
            
            if isinstance(srcs, str): srcs = [srcs]
            if isinstance(dests, str): dests = [dests]
            
            store_names = set()
            for src in srcs:
                if isinstance(src, str):
                    if src.startswith('D') and src.strip(): store_names.add(src)
                    for ds in ds_structures.keys():
                        if ds in src: store_names.add(ds)
            for dest in dests:
                if isinstance(dest, str):
                    if dest.startswith('D') and dest.strip(): store_names.add(dest)
                    for ds in ds_structures.keys():
                        if ds in dest: store_names.add(ds)

            if not store_names:
                out.write(f"\nFlow '{name}' is not connected to any Data Store.\n")
                out.write(f"  Note: Its structure is -> {struct}\n")
            else:
                for ds in store_names:
                    ds_clean = ds.split(' - ')[-1] if ' - ' in ds else ds
                    matched_ds = None
                    for k in ds_structures.keys():
                        if k.lower() in ds_clean.lower() or ds_clean.lower() in k.lower():
                            matched_ds = k
                            break
                    
                    if matched_ds:
                        ds_struct = ds_structures[matched_ds].replace(' ', '').lower()
                        flow_struct = struct.replace(' ', '').lower()
                        
                        if flow_struct and flow_struct in ds_struct or ds_struct in flow_struct:
                            out.write(f"\nFlow '{name}' -> DS '{matched_ds}': Structure MATCHES or is SUBSET.\n")
                        else:
                            out.write(f"\nFlow '{name}' -> DS '{matched_ds}': Structure MISMATCH or DIFFERENT format.\n")
                            out.write(f"  Flow Struct: {struct}\n")
                            out.write(f"  DS Struct  : {ds_structures[matched_ds]}\n")
                    else:
                        out.write(f"\nFlow '{name}' is connected to Data Store '{ds_clean}' but not found in Data Store description!\n")

if __name__ == '__main__':
    main()
