import re
from bs4 import BeautifulSoup
import sys

def get_flows(html_file, level):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    rows = soup.find_all('div', class_='dfd-row')
    process_flows = {}
    
    for row in rows:
        process_div = row.find('div', class_='process')
        if not process_div: continue
        p_id_div = process_div.find('div', class_='p-id')
        if not p_id_div: continue
        p_id = p_id_div.text.strip()
        
        main_p_id = p_id.split('.')[0] + '.0' if level == 2 else p_id
        
        if main_p_id not in process_flows:
            process_flows[main_p_id] = {'in': set(), 'out': set()}
            
        col_left = row.find('div', class_='col-left')
        if col_left:
            conns = col_left.find_all('div', class_='entity-conn')
            for conn in conns:
                if conn.find('div', class_='internal-link'):
                    continue
                flows_container = conn.find('div', class_='flows')
                if not flows_container: continue
                items = flows_container.find_all('div', class_='flow-item')
                for item in items:
                    text_div = item.find('div', class_='flow-text')
                    if not text_div: continue
                    text = text_div.text.strip()
                    if item.find('div', class_='arrow-r'):
                        process_flows[main_p_id]['in'].add(text)
                    elif item.find('div', class_='arrow-l'):
                        process_flows[main_p_id]['out'].add(text)
    
    return process_flows

l1 = get_flows('dfd_level1_evaly.html', 1)
l2 = get_flows('dfd_level2_all_evaly.html', 2)

with open('comparison.txt', 'w', encoding='utf-8') as f:
    for p_id in sorted(l1.keys()):
        f.write(f'--- Process {p_id} ---\n')
        f.write(f'IN L1 missing in L2: {l1[p_id]["in"] - l2.get(p_id, {}).get("in", set())}\n')
        f.write(f'IN L2 extra (not in L1): {l2.get(p_id, {}).get("in", set()) - l1[p_id]["in"]}\n')
        f.write(f'OUT L1 missing in L2: {l1[p_id]["out"] - l2.get(p_id, {}).get("out", set())}\n')
        f.write(f'OUT L2 extra (not in L1): {l2.get(p_id, {}).get("out", set()) - l1[p_id]["out"]}\n')
