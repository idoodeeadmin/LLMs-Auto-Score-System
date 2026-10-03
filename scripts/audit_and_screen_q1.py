# -*- coding: utf-8 -*-
import sys
import os
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

# Current 34 dataset items
wb = openpyxl.load_workbook('ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx', data_only=True)
ws = wb['ชุดข้อสอบ_dataset']

samples = []
for r in range(6, 40):
    sid = ws.cell(row=r, column=1).value
    ans = str(ws.cell(row=r, column=6).value or '').strip()
    score_t = float(ws.cell(row=r, column=7).value or 0.0)
    samples.append({
        'id': sid,
        'source': 'ชุดข้อสอบใหม่',
        'file': f'IMG_{2791 + (r-6)}.jpg', # approximate
        'ans': ans,
        'score': score_t
    })

# Unused 8 files from ชุดข้อสอบเก่า/Textชุดที่1
unused_transcriptions = [
    {
        'id': 'OLD-2834',
        'source': 'ชุดข้อสอบเก่า (IMG_2834)',
        'ans': 'Row-major คือการดูแถวก่อน หรือ แถวหลัก (แถว, คอลัมน์)\nColumn-major คือการดูคอลัมน์ก่อน หรือ คอลัมน์หลัก (คอลัมน์, แถว)',
        'score': 2.0,
        'has_drawing': False,
        'type': 'pure_text'
    },
    {
        'id': 'OLD-2835',
        'source': 'ชุดข้อสอบเก่า (IMG_2835)',
        'ans': 'Row-major => ข้อมูลจะถูกเก็บเรียงตามแถว (Row) รวมถึงการคำนวณดัชนีด้วย B + [ (U2-L2) * (I-L1) + (J-L2) ]\nColumn-major => ข้อมูลจะถูกเก็บเรียงตามคอลัมน์ (Column) โดยการคำนวณดัชนีจะเป็น B + [ (U1-L1) * (J-L2) + (I-L1) ]\nสิ่งที่ต่างกันระหว่างทั้งสองคือการจัดเก็บ ซึ่งจะมีผลต่อการเข้าถึงข้อมูลในหน่วยความจำ',
        'score': 2.0,
        'has_drawing': False,
        'type': 'pure_text'
    },
    {
        'id': 'OLD-2832',
        'source': 'ชุดข้อสอบเก่า (IMG_2832)',
        'ans': 'Row-major: การคำนวณ = B + NC * I + J\nColumn-major: การคำนวณ = B + NC * J + I',
        'score': 2.0,
        'has_drawing': False,
        'type': 'pure_text'
    },
    {
        'id': 'OLD-2831',
        'source': 'ชุดข้อสอบเก่า (IMG_2831)',
        'ans': 'Row-major คือ การจัดเก็บข้อมูลในรูปแบบที่เก็บข้อมูลในแถวก่อน\nColumn-major คือ การจัดเก็บข้อมูลในรูปแบบที่เก็บข้อมูลในคอลัมน์ก่อน',
        'score': 2.0,
        'has_drawing': True, # has drawing
        'type': 'drawing'
    },
    {
        'id': 'OLD-2829',
        'source': 'ชุดข้อสอบเก่า (IMG_2829)',
        'ans': 'Row-major จัดเก็บข้อมูลในรูปแบบแถวก่อน และ Column-major จัดเก็บข้อมูลในรูปแบบคอลัมน์ก่อน',
        'score': 1.0,
        'has_drawing': True,
        'type': 'drawing'
    },
    {
        'id': 'OLD-2833',
        'source': 'ชุดข้อสอบเก่า (IMG_2833)',
        'ans': 'Row-major คือ A[i][j] = A[lim][len]\nColumn-major คือ A[x][y] = A[lin][j]',
        'score': 2.0,
        'has_drawing': True,
        'type': 'drawing'
    },
    {
        'id': 'OLD-2839',
        'source': 'ชุดข้อสอบเก่า (IMG_2839)',
        'ans': 'Row: เรียงตามเลเยอร์แนว Row -> 0 1 2 3 4 5 6 7\nColumn: เรียงตามเลเยอร์แนว Column -> 0 5 6 9 1 4 7 10 2 5 8 11',
        'score': 2.0,
        'has_drawing': True,
        'type': 'drawing'
    }
]

# Known drawing cases from our image audit
DRAWING_SIDS = {'DS-001', 'DS-010', 'DS-022', 'DS-029', 'DS-031'}

# Known teacher leniency cases (answered just general definition / direction, but teacher gave 2.0)
LENIENT_SIDS = {
    'DS-002': 'บอกแค่เก็บแบบแถว vs คอลัมน์ แต่ครูให้ 2.0',
    'DS-003': 'บอกแค่เน้นชื่อแถว vs ชื่อคอลัมน์ แต่ครูให้ 2.0',
    'DS-005': 'บอกแค่ Array แนวนอน vs แนวตั้ง แต่ครูให้ 2.0',
    'DS-017': 'บอกแค่คิดแถวเป็นหลัก vs คิดคอลัมน์เป็นหลัก แต่ครูให้ 2.0',
    'DS-018': 'บอกแค่เปรียบเสมือนแกน x vs แกน y แต่ครูให้ 2.0',
    'DS-019': 'บอกแค่จัดเก็บเป็น Row vs จัดเก็บ col ใน 2D แต่ครูให้ 2.0',
    'DS-024': 'บอกแค่คำนวณจากแถว vs หลักตัวตั้ง จัดเรียงแนวนอนแนวตั้ง แต่ครูให้ 2.0',
    'DS-032': 'บอกแค่เอาแถวก่อน vs เอาคอลัมน์ก่อน สั้นมาก แต่ครูให้ 2.0'
}

print("="*80)
print("AUDIT SUMMARY OF ALL CANDIDATES FOR QUESTION 1")
print("="*80)

accepted = []
rejected_drawing = []
rejected_lenient = []

for s in samples:
    sid = s['id']
    ans = s['ans']
    score = s['score']
    
    if sid in DRAWING_SIDS:
        rejected_drawing.append((sid, score, ans, 'มีรูปวาดตาราง/เมทริกซ์ในกระดาษจริง (OCR ถอดเป็นตัวเลขคลาดเคลื่อน)'))
    elif sid in LENIENT_SIDS:
        rejected_lenient.append((sid, score, ans, LENIENT_SIDS[sid]))
    else:
        accepted.append((sid, score, ans, 'ข้อความบรรยายตรงเกณฑ์และคะแนนสมเหตุสมผล'))

print(f"\n1. กลุ่มที่ถูกคัดออกเพราะเป็น 'รูปวาด/ตารางเมทริกซ์' ({len(rejected_drawing)} ข้อ):")
for sid, score, ans, reason in rejected_drawing:
    print(f"  - [{sid}] (คะแนนครู: {score}) : {reason}")
    print(f"    ข้อความ: {repr(ans[:60])}")

print(f"\n2. กลุ่มที่ถูกคัดออกเพราะ 'อาจารย์ใจดีให้คะแนน (Teacher Leniency)' ({len(rejected_lenient)} ข้อ):")
for sid, score, ans, reason in rejected_lenient:
    print(f"  - [{sid}] (คะแนนครู: {score}) : {reason}")
    print(f"    ข้อความ: {repr(ans[:60])}")

print(f"\n3. กลุ่มที่ผ่านเกณฑ์คุณภาพสูง (Pure Text + คะแนนสมเหตุสมผล) ในชุดปัจจุบัน ({len(accepted)} ข้อ):")
for sid, score, ans, reason in accepted:
    print(f"  - [{sid}] คะแนน: {score} | {repr(ans[:65])}")

print(f"\n4. ตัวเลือกคุณภาพสูงเพิ่มเติมจาก 'ชุดข้อสอบเก่า' (ที่ไม่มีรูปวาด + มีวิธีเรียก):")
for u in unused_transcriptions:
    if not u['has_drawing']:
        print(f"  - [{u['id']}] คะแนน: {u['score']} | {repr(u['ans'][:65])}")
