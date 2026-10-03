import re, sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = 'scripts/build_full_chapter4_documents.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add add_case_study function after add_callout_box
helper_func = """def add_case_study(doc, title, img_path, img_caption, details_list):
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    run_t = p_title.add_run(title)
    run_t.bold = True
    run_t.font.name = "TH Sarabun New"
    run_t.font.size = Pt(16)
    
    if img_path and os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_path), width=Inches(3.6))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(6)
        run_cap = p_cap.add_run(img_caption)
        run_cap.font.name = "TH Sarabun New"
        run_cap.font.size = Pt(13)
        run_cap.italic = True
        
    add_callout_box(doc, "รายละเอียดและผลการประเมิน:", details_list)
"""

content = content.replace("def add_callout_box(doc, title, items):", helper_func + "\ndef add_callout_box(doc, title, items):")

# 2. Replace Cases 1-6 block
cases_pattern = re.compile(
    r'# Case 1\s*add_callout_box\(doc, "กรณีศึกษาที่ 1:.*?'
    r'add_callout_box\(doc, "กรณีศึกษาที่ 6:.*?\n    \]\)\n',
    re.DOTALL
)

new_cases_code = """    # Case 1
    add_case_study(doc, "ตารางที่ 4.7 กรณีศึกษาที่ 1: กลุ่มข้อความ - ข้อ 1 (Row-major vs Column-major) รหัสตัวอย่าง DS-001 [Exact Match: 2.00 เต็ม]", 
        ROOT / "public/screenshots/case_studies/case1_ds001.jpg", 
        "ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-001 (ข้อ 1)", [
        "• คำตอบของนิสิต (ถอดความจากลายมือ):",
        "  \"Row จะนับเป็นแถวจากซ้ายไปขวา ส่วน Column จากบนลงล่าง เช่น 0 1 2 3, 4 5 6 7, 8 9 10 11\"",
        "• คะแนนที่ได้: อาจารย์ผู้สอน = 2.00 คะแนน | ระบบ AI = 2.00 คะแนน (ตรงกันสมบูรณ์ 100%)",
        "• ข้อเสนอแนะจากระบบ (AI Feedback):",
        "  - สำหรับผู้สอน: คำตอบได้คะแนนเต็ม 2.00 คะแนน เนื่องจากอธิบายองค์ประกอบสำคัญได้ครบทั้งสองส่วน: Row-major คือการเรียงข้อมูลตามแถวจากซ้ายไปขวา และ Column-major คือการเรียงข้อมูลตามคอลัมน์จากบนลงล่าง ซึ่งตรงตามเกณฑ์ Row-major 1.00 คะแนน และ Column-major 1.00 คะแนน ตัวอย่างข้อมูลที่จัดเป็นแถวยังสอดคล้องกับแนวคิดการเรียงแบบ Row-major",
        "  - สำหรับนักเรียน: ตอบได้ถูกต้องและได้คะแนนเต็ม โดยแยกความแตกต่างของ Row-major และ Column-major ได้ชัดเจนแล้ว หากต้องการให้สมบูรณ์ยิ่งขึ้น อาจระบุว่า Row-major เก็บข้อมูลในหน่วยความจำทีละแถว ส่วน Column-major เก็บทีละคอลัมน์"
    ])
    
    # Case 2
    add_case_study(doc, "ตารางที่ 4.8 กรณีศึกษาที่ 2: กลุ่มข้อความ - ข้อ 2 (Time Complexity) รหัสตัวอย่าง DS-047 [Exact Match: 2.00 เต็ม]", 
        ROOT / "public/screenshots/case_studies/case2_ds047.jpg", 
        "ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-047 (ข้อ 2)", [
        "• คำตอบของนิสิต (ถอดความจากลายมือ):",
        "  \"เพราะว่า Big-O (n log n) จะทำการหารครึ่ง หรือแบ่งครึ่ง หรือ (n log n) ทำให้คำนวณข้อมูลขนาดใหญ่ได้เร็วกว่า O(n^2)",
        "   ส่วน Big-O(n^2) ส่วนมากใช้ใน sort จะใช้เวลามากกว่าในการคำนวณ ตัวอย่าง Algorithm: O(n log n) = Merge sort, O(n^2) = Insertion sort, Selection sort\"",
        "• คะแนนที่ได้: อาจารย์ผู้สอน = 2.00 คะแนน | ระบบ AI = 2.00 คะแนน (ตรงกันสมบูรณ์ 100%)",
        "• ข้อเสนอแนะจากระบบ (AI Feedback):",
        "  - สำหรับผู้สอน: คำตอบได้คะแนนเต็ม 2.00 คะแนน เพราะระบุเหตุผลได้ถูกต้องว่า O(n log n) มีการแบ่งข้อมูล/หารครึ่ง และใช้เวลาน้อยกว่าหรือเร็วกว่า O(n^2) เมื่อข้อมูลมีขนาดใหญ่ อีกทั้งยกตัวอย่างอัลกอริทึมได้ถูกต้อง ได้แก่ Merge Sort สำหรับ O(n log n) และ Insertion Sort, Selection Sort สำหรับ O(n^2)",
        "  - สำหรับนักเรียน: ตอบได้ถูกต้องและครบทั้งสองส่วน อธิบายว่า O(n log n) เติบโตช้ากว่าและมักใช้แนวคิดแบ่งข้อมูลเป็นส่วนย่อย รวมถึงยกตัวอย่างอัลกอริทึมได้ถูกต้องตรงตามทฤษฎี"
    ])
    
    # Case 3
    add_case_study(doc, "ตารางที่ 4.9 กรณีศึกษาที่ 3: กลุ่มข้อความ - ข้อ 3 (Linked List vs Array) รหัสตัวอย่าง DS-072 [Partial Credit: 0.50 คะแนน]", 
        ROOT / "public/screenshots/case_studies/case3_ds072.jpg", 
        "ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-072 (ข้อ 3)", [
        "• คำตอบของนิสิต (ถอดความจากลายมือ):",
        "  \"สแตก ทำงานแบบ เข้าทีหลัง แต่ออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access",
        "   คิว ทำงานแบบ เข้าก่อน และออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access",
        "   อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า\"",
        "• คะแนนที่ได้: อาจารย์ผู้สอน = 0.50 คะแนน | ระบบ AI = 0.50 คะแนน (ตรงกันสมบูรณ์ในระดับคะแนนบางส่วน)",
        "• ข้อเสนอแนะจากระบบ (AI Feedback):",
        "  - สำหรับผู้สอน: ได้ 0.50 คะแนนตามเกณฑ์ระดับมาตรฐาน เนื่องจากผู้เรียนระบุพฤติกรรม LIFO และ FIFO ได้ถูกต้อง และกล่าวถึงข้อดีข้อเสียของ Array บางส่วน แต่ไม่ได้เปรียบเทียบการใช้ Linked List กับ Array สำหรับ Stack/Queue โดยตรง และไม่ได้กล่าวถึงลักษณะ Dynamic จึงไม่ได้คะแนนในส่วนที่ 2 (0.00 คะแนน)",
        "  - สำหรับนักเรียน: เข้าใจพฤติกรรม Stack/Queue และ Array เบื้องต้น แต่ขาดประเด็นหลักคือการเปรียบเทียบ Linked List กับ Array ควรระบุว่า Array ขนาดคงที่ ส่วน Linked List ปรับขนาดได้ยืดหยุ่นด้วย Pointer"
    ])
    
    # Case 4
    add_case_study(doc, "ตารางที่ 4.10 กรณีศึกษาที่ 4: กลุ่มรูปภาพ - ข้อ 4 (วาด Binary Search Tree 12 โหนด) รหัสตัวอย่าง DS-104 [Exact Match: 1.00 เต็ม]", 
        ROOT / "public/screenshots/case_studies/case4_ds104.jpg", 
        "ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-104 (ข้อ 4)", [
        "• ลักษณะคำตอบ: ภาพถ่ายกระดาษวาดโครงสร้างต้นไม้ค้นหาทวิภาค (BST) ครบทั้ง 12 โหนดตามลำดับข้อมูล 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99",
        "• คะแนนที่ได้: อาจารย์ผู้สอน = 1.00 คะแนน | ระบบ AI = 1.00 คะแนน (ตรงกันสมบูรณ์ 100%)",
        "• ข้อเสนอแนะจากระบบ (AI Feedback):",
        "  - สำหรับผู้สอน: โครงสร้าง Binary Search Tree ถูกต้องครบทั้ง 12 โหนดตามคุณสมบัติ โหนดซ้าย < โหนดแม่ < โหนดขวา (Root=9 ซ้าย=5 ขวา=16; ใต้ 16 ซ้าย=10 ขวา=76; ใต้ 10 ขวา=13; ใต้ 13 ซ้าย=11 ขวา=15; ใต้ 76 ซ้าย=58 ขวา=92; ใต้ 92 ซ้าย=80 ขวา=99) ให้ 1.00 คะแนนเต็ม",
        "  - สำหรับนักเรียน: วาดโครงสร้างต้นไม้ค้นหาทวิภาคได้ถูกต้องสมบูรณ์และวางตำแหน่งกิ่งซ้าย-ขวาได้ถูกต้องตามลำดับการแทรกข้อมูล"
    ])
    
    # Case 5
    add_case_study(doc, "ตารางที่ 4.11 กรณีศึกษาที่ 5: กลุ่มรูปภาพ - ข้อ 5 (แปลง Infix เป็น Prefix & Postfix) รหัสตัวอย่าง DS-154 [Partial Credit: 0.50 คะแนน]", 
        ROOT / "public/screenshots/case_studies/case5_ds154.jpg", 
        "ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-154 (ข้อ 5)", [
        "• ลักษณะคำตอบ: ภาพถ่ายแสดงขั้นตอนวิธีทำแปลงนิพจน์ Infix A + (B * (C - (D / (F * 2))))",
        "• คะแนนที่ได้: อาจารย์ผู้สอน = 0.50 คะแนน | ระบบ AI = 0.50 คะแนน (ตรวจแยกส่วน Prefix และ Postfix อย่างเป็นธรรม)",
        "• ข้อเสนอแนะจากระบบ (AI Feedback):",
        "  - สำหรับผู้สอน: ส่วน Prefix ได้ 0.50 คะแนน (คำตอบสุดท้าย +A*B-C/D*F2 ถูกต้อง) แต่ส่วน Postfix ได้ 0.00 คะแนน เนื่องจากเขียนตัวดำเนินการสลับที่และไม่เป็นไปตามหลัก Postfix (เขียนเป็น A+B*C-D/F2*) รวมคะแนนได้ 0.50 คะแนน",
        "  - สำหรับนักเรียน: ส่วน Prefix ทำได้ถูกต้องแล้ว แต่ส่วน Postfix ควรนำตัวดำเนินการไปวางไว้ท้ายตัวถูกดำเนินการเสมอ เช่น (F*2) ต้องแปลงเป็น F2* อย่าเขียนเครื่องหมาย +, *, -, / ไว้ระหว่างตัวแปรเหมือน Infix"
    ])
    
    # Case 6
    add_case_study(doc, "ตารางที่ 4.12 กรณีศึกษาที่ 6: กลุ่มรูปภาพ - ข้อ 6 (General Tree เป็น Binary Tree / LCRS) รหัสตัวอย่าง DS-171 [Zero Score: 0.00 ผิดหลักการ]", 
        ROOT / "public/screenshots/case_studies/case6_ds171.jpg", 
        "ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-171 (ข้อ 6)", [
        "• ลักษณะคำตอบ: ภาพถ่ายแสดงการวาดโครงสร้างต้นไม้ 10 โหนด แต่ไม่ได้แปลงตามหลัก LCRS",
        "• คะแนนที่ได้: อาจารย์ผู้สอน = 0.00 คะแนน | ระบบ AI = 0.00 คะแนน (ตรงกันสมบูรณ์ในการตรวจพบข้อผิดพลาดเชิงโครงสร้าง)",
        "• ข้อเสนอแนะจากระบบ (AI Feedback):",
        "  - สำหรับผู้สอน: นิสิตวาดเป็น General Tree เดิม โดยเชื่อมโหนด 1 ไปยัง 2, 3, 4 โดยตรง ไม่ได้แปลงตามหลัก Left-Child Right-Sibling (LCRS) ที่กำหนดให้ 1 มีลูกซ้ายเป็น 2 และ 2 เชื่อมกิ่งขวาไป 3 และ 4 จึงผิดหลักการอย่างมีนัยสำคัญ ได้ 0.00 คะแนน",
        "  - สำหรับนักเรียน: คำตอบยังเป็นต้นไม้เดิมที่มีลูกหลายตัว จึงยังไม่ใช่ Binary Tree แบบ LCRS ให้จำหลักว่า กิ่งซ้ายแทนลูกคนแรก (First Child) และกิ่งขวาแทนพี่น้องถัดไป (Next Sibling): แต่ละโหนดมีลูกซ้ายและขวาได้ไม่เกินอย่างละหนึ่งกิ่ง"
    ])
"""

content, count = cases_pattern.subn(new_cases_code, content)
print(f"Replaced cases in Word builder: {count} occurrence(s)")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully updated {file_path}")
