import pandas as pd
import json
from bs4 import BeautifulSoup
import codecs
import sys

def get_dfd_flows():
    flows = set()
    for f in ['dfd_level0_evaly.html', 'dfd_level1_evaly.html', 'dfd_level2_all_evaly.html']:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                for el in soup.find_all('div', class_='flow-text'):
                    text = el.get_text(strip=True)
                    if text: flows.add(text)
        except Exception as e:
            print(f"Error reading {f}: {e}")
    return flows

def main():
    with codecs.open('verify_output_pd.txt', 'w', 'utf-8') as out:
        try:
            dict_df = pd.read_html('data_flow_dict_evaly.html')[0]
            
            # Clean up the headers which might be hierarchical due to pandas
            if isinstance(dict_df.columns, pd.MultiIndex):
                dict_df.columns = dict_df.columns.get_level_values(-1)
                
            dict_flows = set(dict_df['Name'].dropna().str.strip().tolist())
        except Exception as e:
            out.write(f"Error reading dictionary: {e}\n")
            return
            
        try:
            ds_df = pd.read_html('datastore_description_evaly.html')[0]
            if isinstance(ds_df.columns, pd.MultiIndex):
                ds_df.columns = ds_df.columns.get_level_values(-1)
                
            ds_structures = {}
            for _, row in ds_df.iterrows():
                ds_name = str(row.get('Data Store Name', '')).strip()
                ds_struct = str(row.get('Data Structure', '')).strip()
                if ds_name and ds_struct:
                    ds_structures[ds_name] = ds_struct
        except Exception as e:
            out.write(f"Error reading data stores: {e}\n")
            return
            
        dfd_flows = get_dfd_flows()
        
        out.write("=== Data Flow Lines Verification ===\n\n")
        out.write("1. เส้นที่มีใน Data Flow Dictionary แต่ไม่มีใน DFD (เส้นเกินมา หรือตั้งชื่อไม่ตรงกัน):\n")
        missing_in_dfd = sorted(list(dict_flows - dfd_flows))
        for m in missing_in_dfd:
            out.write(f" - {m}\n")
            
        out.write("\n2. เส้นที่มีใน DFD Level 0-2 แต่ไม่มีใน Data Flow Dictionary (เส้นที่ขาดไป):\n")
        missing_in_dict = sorted(list(dfd_flows - dict_flows))
        for m in missing_in_dict:
            out.write(f" - {m}\n")
            
        out.write("\n=== Data Structure Verification ===\n\n")
        out.write("ตรวจสอบโครงสร้างข้อมูลของ Data Flow เทียบกับ Data Store:\n")
        
        for idx, row in dict_df.iterrows():
            name = str(row.get('Name', '')).strip()
            struct = str(row.get('Data Structure', '')).strip()
            
            if name == 'nan' or not name: continue
            
            # We want to know if this flow connects to a datastore based on its description
            # or by checking DFD. We don't have DFD source/dest parsed perfectly for every flow,
            # but we can check if its structure matches any datastore.
            out.write(f"\nFlow: {name}\n")
            out.write(f"Structure in Dict: {struct}\n")
            
            # check if it mentions 'ไม่มีในแฟ้มข้อมูล'
            if 'ไม่มีในแฟ้มข้อมูล' in struct:
                out.write("=> ไม่ได้เก็บใน Data Store (ระบุไว้ใน Dictionary อย่างถูกต้อง)\n")
                continue
                
            # Compare with data stores
            matched = False
            for ds_name, ds_struct in ds_structures.items():
                # simple heuristics: if structure overlaps significantly
                clean_struct = struct.replace(' ', '').replace('+', '')
                clean_ds_struct = ds_struct.replace(' ', '').replace('+', '')
                
                if clean_struct in clean_ds_struct or clean_ds_struct in clean_struct:
                    out.write(f"=> สอดคล้องกับ Data Store: {ds_name}\n")
                    matched = True
                    break
            
            if not matched:
                out.write("=> โครงสร้างข้อมูลไม่สอดคล้องกับ Data Store ใดๆ อย่างชัดเจน หรืออาจจะไม่ได้เก็บใน Data Store (แต่ไม่ได้ระบุไว้)\n")

if __name__ == '__main__':
    main()
