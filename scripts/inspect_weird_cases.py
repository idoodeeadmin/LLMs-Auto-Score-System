import sys
import io
import openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb = openpyxl.load_workbook('ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx', data_only=True)
ws = wb['ชุดข้อสอบ_dataset']
rows = list(ws.iter_rows(values_only=True))

items = []
for r in rows[5:]:
    if r[0] and str(r[0]).startswith('DS-'):
        items.append({
            'sid': str(r[0]),
            'qno': r[1],
            'ans': str(r[5]) if r[5] is not None else '',
            'h': float(r[6]) if r[6] is not None else None,
            'ai': float(r[7]) if r[7] is not None else None,
            'fb': str(r[9]) if len(r)>9 and r[9] is not None else ''
        })

print("================================================================================")
print("1. กลุ่มคะแนนเศษที่ไม่มีในเกณฑ์มาตรฐาน (0.25, 0.75, 1.50)")
print("================================================================================")

print("\n--- [ข้อ 4 วาด BST (เต็ม 1.00)] แต่ครูให้ 0.25 ---")
for it in items:
    if it['sid'] == 'DS-121':
        print(f"รหัส: {it['sid']} | คะแนนครู: {it['h']} | AI: {it['ai']}")
        print(f"คำตอบ: {it['ans']}")
        print(f"AI Feedback: {it['fb']}")

print("\n--- [ข้อ 5 แปลง Infix (เต็ม 1.00, ปกติหาร 2 คือ 0.50/0.50)] แต่ครูให้ 0.25 ---")
for it in items:
    if it['sid'] in ['DS-165', 'DS-166']:
        print(f"รหัส: {it['sid']} | คะแนนครู: {it['h']} | AI: {it['ai']}")
        print(f"คำตอบ: {it['ans']}")
        print(f"AI Feedback: {it['fb']}\n")

print("\n--- [ข้อ 2 Time Complexity (เต็ม 2.00, เกณฑ์ปกติคือ 0, 1, 2)] แต่ครูให้ 1.50 ---")
for it in items:
    if it['qno'] == 2 and it['h'] == 1.5:
        print(f"รหัส: {it['sid']} | คะแนนครู: {it['h']} | AI: {it['ai']}")
        print(f"คำตอบ: {it['ans']}")
        print(f"AI Feedback: {it['fb']}\n")

print("\n--- [ข้อ 3 Linked list vs Array (เต็ม 1.00)] ครูให้ 0.25 หรือ 0.75 ---")
for it in items:
    if it['qno'] == 3 and it['h'] in [0.25, 0.75]:
        print(f"รหัส: {it['sid']} | คะแนนครู: {it['h']} | AI: {it['ai']}")
        print(f"คำตอบ: {it['ans']}")
        print(f"AI Feedback: {it['fb']}\n")

print("================================================================================")
print("2. กลุ่มที่คำตอบแปลก/ตอบนิดเดียว/หลงประเด็น แต่อาจารย์ให้คะแนน (Teacher Leniency)")
print("================================================================================")
for it in items:
    if it['sid'] in ['DS-007', 'DS-015']:
        print(f"รหัส: {it['sid']} (ข้อ {it['qno']}) | คะแนนครู: {it['h']} | AI: {it['ai']}")
        print(f"คำตอบ: {it['ans']}")
        print(f"AI Feedback: {it['fb']}\n")

print("================================================================================")
print("3. กลุ่มที่ตอบถูกดีมาก แต่ถูกอาจารย์หักเหลือ 1 คะแนน (Harsh Penalty / Discrepancy)")
print("================================================================================")
for it in items:
    if it['sid'] in ['DS-008', 'DS-009', 'DS-025', 'DS-031']:
        print(f"รหัส: {it['sid']} (ข้อ {it['qno']}) | คะแนนครู: {it['h']} | AI: {it['ai']}")
        print(f"คำตอบ: {it['ans']}")
        print(f"AI Feedback: {it['fb']}\n")

print("================================================================================")
print("4. กลุ่มที่ตอบมีประเด็น แต่อาจารย์กดให้ 0 คะแนน")
print("================================================================================")
for it in items:
    if it['sid'] in ['DS-030']:
        print(f"รหัส: {it['sid']} (ข้อ {it['qno']}) | คะแนนครู: {it['h']} | AI: {it['ai']}")
        print(f"คำตอบ: {it['ans']}")
        print(f"AI Feedback: {it['fb']}\n")
