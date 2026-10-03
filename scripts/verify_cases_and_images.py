import os, sys, openpyxl
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx', data_only=True)
ws = wb.active

cases = [
    {
        'case_num': 1,
        'q': 1,
        'sid': 'DS-001',
        'row': 6,
        'img_path': 'ชุดข้อสอบใหม่/photo_clean_text1/IMG_2791.jpg'
    },
    {
        'case_num': 2,
        'q': 2,
        'sid': 'DS-041',
        'row': 46,
        'img_path': 'ชุดข้อสอบใหม่/photo_clean_text2/IMG_2847.jpg'
    },
    {
        'case_num': 3,
        'q': 3,
        'sid': 'DS-072',
        'row': 77,
        'img_path': 'ชุดข้อสอบใหม่/photo_clean_text3/IMG_2895.jpg'
    },
    {
        'case_num': 4,
        'q': 4,
        'sid': 'DS-104',
        'row': 109,
        'img_path': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่1/LINE_ALBUM_Photo1_260917_2.jpg'
    },
    {
        'case_num': 5,
        'q': 5,
        'sid': 'DS-154',
        'row': 159,
        'img_path': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่2/LINE_ALBUM_Photo2.1_260918_18.jpg'
    },
    {
        'case_num': 6,
        'q': 6,
        'sid': 'DS-171',
        'row': 176,
        'img_path': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่3/LINE_ALBUM_Photo2.2_260918_1.jpg'
    }
]

for c in cases:
    r = c['row']
    sid = ws.cell(r, 1).value
    ans_text = str(ws.cell(r, 6).value)
    h_score = ws.cell(r, 7).value
    ai_score = ws.cell(r, 8).value
    p = c['img_path']
    exists = os.path.exists(p)
    size = os.path.getsize(p) if exists else 0
    im = Image.open(p) if exists else None
    dims = im.size if im else None
    print(f"Case {c['case_num']} (Q{c['q']}): {sid} (row {r}) | Score H:{h_score} AI:{ai_score}")
    print(f"   Image: {p} (Exists: {exists}, Dims: {dims}, Size: {size//1024} KB)")
    print(f"   Answer text in Excel: {ans_text[:100]}...\n")
