import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('docs_and_tests/chapter4_testcases.html', 'r', encoding='utf-8') as f:
    html = f.read()

sections = re.split(r'<h3[^>]*>(4\.1\.\d+[^<]+)</h3>', html)

for i in range(1, len(sections), 2):
    title = sections[i].strip()
    body = sections[i+1]
    tables = re.findall(r'<table[^>]*>.*?</table>', body, re.DOTALL)
    captions = re.findall(r'<caption[^>]*>(.*?)</caption>', body, re.DOTALL)
    clean_caps = [re.sub(r'<[^>]+>', '', c).strip() for c in captions]
    
    # check images
    imgs = re.findall(r'src=["\']([^"\']+)["\']', body)
    
    # check test cases inside tables
    test_cases = re.findall(r'Test Case \d+', body)
    
    print(f"{title} | Tables: {len(tables)} | Captions: {clean_caps} | TestCases: {set(test_cases)} | Imgs: {len(imgs)}")
