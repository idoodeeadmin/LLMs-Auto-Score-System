# -*- coding: utf-8 -*-
import os

with open('scripts/build_chapter4_section41.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_ds047 = '<tr><th scope="row">คำตอบของนิสิต</th><td>"เพราะว่า ข้อมูลขนาดใหญ่มีจำนวนมาก การที่จะมาลูปซ้อนลูปจะเสียเวลามากเกินไป ดังนั้น O(n log n) จึงเป็นวิธีที่ทำให้เร็วกว่า ตัวอย่างเช่น Merge Sort"</td></tr>'

new_ds047 = '''<tr><th scope="row">คำตอบของนิสิต</th><td>"เพราะว่า Big-O (n log n) จะทำการหารครึ่ง หรือแบ่งครึ่ง หรือ (n log n) ทำให้คำนวณข้อมูลขนาดใหญ่ได้เร็วกว่า O(n^2) ส่วน Big-O(n^2) ส่วนมากใช้ใน sort จะใช้เวลามากกว่าในการคำนวณ<br><strong>ตัวอย่าง Algorithm:</strong><br>• O(n log n) = Merge sort<br>• O(n^2) = Insertion sort, Selection sort"</td></tr>'''

old_ds072 = '<tr><th scope="row">คำตอบของนิสิต</th><td>"สแตก ทำงานแบบเข้าทีหลังออกก่อน ข้อดี ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access, คิว ทำงานแบบเข้าก่อนออกก่อน ข้อดี ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access, อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า"</td></tr>'

new_ds072 = '''<tr><th scope="row">คำตอบของนิสิต</th><td>"• สแตก ทำงานแบบ เข้าทีหลัง แต่ออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access<br>• คิว ทำงานแบบ เข้าก่อน และออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access<br>• อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า"</td></tr>'''

if old_ds047 in text:
    text = text.replace(old_ds047, new_ds047)
    print("Replaced DS-047 in build_chapter4_section41.py")
else:
    print("old_ds047 not found in build_chapter4_section41.py")

if old_ds072 in text:
    text = text.replace(old_ds072, new_ds072)
    print("Replaced DS-072 in build_chapter4_section41.py")
else:
    print("old_ds072 not found in build_chapter4_section41.py")

with open('scripts/build_chapter4_section41.py', 'w', encoding='utf-8') as f:
    f.write(text)

# Also update scripts/generate_full_chapter4_thesis_docx.py
with open('scripts/generate_full_chapter4_thesis_docx.py', 'r', encoding='utf-8') as f:
    docx_script = f.read()

old_docx_ds047 = '"\\"เพราะว่า ข้อมูลขนาดใหญ่มีจำนวนมาก การที่จะมาลูปซ้อนลูปจะเสียเวลามากเกินไป ดังนั้น O(n log n) จึงเป็นวิธีที่ทำให้เร็วกว่า ตัวอย่างเช่น Merge Sort\\"",'

new_docx_ds047 = '''"\\"เพราะว่า Big-O (n log n) จะทำการหารครึ่ง หรือแบ่งครึ่ง หรือ (n log n) ทำให้คำนวณข้อมูลขนาดใหญ่ได้เร็วกว่า O(n^2) ส่วน Big-O(n^2) ส่วนมากใช้ใน sort จะใช้เวลามากกว่าในการคำนวณ\\nตัวอย่าง Algorithm:\\n• O(n log n) = Merge sort\\n• O(n^2) = Insertion sort, Selection sort\\"",'''

old_docx_ds072 = '"\\"สแตก ทำงานแบบเข้าทีหลังออกก่อน ข้อดี ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access, คิว ทำงานแบบเข้าก่อนออกก่อน ข้อดี ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access, อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า\\"",'

new_docx_ds072 = '''"\\"• สแตก ทำงานแบบ เข้าทีหลัง แต่ออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access\\n• คิว ทำงานแบบ เข้าก่อน และออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access\\n• อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า\\"",'''

if old_docx_ds047 in docx_script:
    docx_script = docx_script.replace(old_docx_ds047, new_docx_ds047)
    print("Replaced DS-047 in generate_full_chapter4_thesis_docx.py")
else:
    print("old_docx_ds047 not found in generate_full_chapter4_thesis_docx.py")

if old_docx_ds072 in docx_script:
    docx_script = docx_script.replace(old_docx_ds072, new_docx_ds072)
    print("Replaced DS-072 in generate_full_chapter4_thesis_docx.py")
else:
    print("old_docx_ds072 not found in generate_full_chapter4_thesis_docx.py")

with open('scripts/generate_full_chapter4_thesis_docx.py', 'w', encoding='utf-8') as f:
    f.write(docx_script)

print("Patch complete.")
