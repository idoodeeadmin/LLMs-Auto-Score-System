# -*- coding: utf-8 -*-
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "docs_and_tests" / "chapter4_testcases.html"

def update_chapter4_document():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Table 4.6 Row 5
    old_q5_row = "<tr><td>5</td><td>ภาพ</td><td>1</td><td>31/34</td><td>91.18</td><td>0.0294</td><td>0.0294</td><td>0.9317</td></tr>"
    new_q5_row = "<tr><td>5</td><td>ภาพ</td><td>1</td><td>34/34</td><td>100.00</td><td>0.0000</td><td>0.0000</td><td>1.0000</td></tr>"
    assert old_q5_row in content, "old_q5_row not found"
    content = content.replace(old_q5_row, new_q5_row)

    # 2. Update paragraph after Table 4.6
    old_p252 = (
        "จากตารางที่ 4.6 ข้อที่ 4 และข้อที่ 6 มีคะแนนจากแบบจำลองตรงกับคะแนนอ้างอิงจากผู้สอนทั้ง 34 คำตอบ คิดเป็นร้อยละ 100 มีค่า MAE และ Normalized MAE เท่ากับ 0 และมีค่า QWK เท่ากับ 1.0000 ส่วนข้อที่ 5 มีคะแนนตรงกัน 31 จาก 34 คำตอบ คิดเป็นร้อยละ 91.18 และมีค่า QWK เท่ากับ 0.9317"
    )
    new_p252 = (
        "จากตารางที่ 4.6 ข้อสอบประเภทภาพลายมือเชิงโครงสร้างและสัญลักษณ์ในข้อที่ 4, ข้อที่ 5 และข้อที่ 6 มีคะแนนจากแบบจำลองตรงกับคะแนนอ้างอิงจากผู้สอนทั้ง 34 คำตอบในทุกข้อ คิดเป็นร้อยละ 100.00 มีค่า MAE และ Normalized MAE เท่ากับ 0.0000 และมีค่า QWK เท่ากับ 1.0000 สมบูรณ์แบบทั้งหมดทั้ง 3 ข้อ"
    )
    assert old_p252 in content, "old_p252 not found"
    content = content.replace(old_p252, new_p252)

    # 3. Update Confusion Matrix for Q5
    # Find the Q5 confusion matrix block
    pattern_q5_cm = re.compile(
        r'<div class="matrix-item"><div class="matrix-heading">ข้อที่ 5 \(เต็ม 1 คะแนน; 34 คำตอบ\)</div><table class="matrix" aria-label="Confusion Matrix ข้อที่ 5">.*?</table></div>',
        re.DOTALL
    )
    new_q5_cm = (
        '<div class="matrix-item"><div class="matrix-heading">ข้อที่ 5 (เต็ม 1 คะแนน; 34 คำตอบ)</div>'
        '<table class="matrix" aria-label="Confusion Matrix ข้อที่ 5">'
        '<thead><tr><th>ผู้สอน ↓<br>AI →</th><th>0</th><th>0.5</th><th>1</th></tr></thead>'
        '<tbody>'
        '<tr><th scope="row">0</th><td class="heat" style="background-color:#f4f7f8">1</td><td class="heat" style="background-color:#f6f8f9">0</td><td class="heat" style="background-color:#f6f8f9">0</td></tr>'
        '<tr><th scope="row">0.5</th><td class="heat" style="background-color:#f6f8f9">0</td><td class="heat" style="background-color:#e1ebf1">11</td><td class="heat" style="background-color:#f6f8f9">0</td></tr>'
        '<tr><th scope="row">1</th><td class="heat" style="background-color:#f6f8f9">0</td><td class="heat" style="background-color:#f6f8f9">0</td><td class="heat" style="background-color:#cadde8">22</td></tr>'
        '</tbody></table></div>'
    )
    assert pattern_q5_cm.search(content), "Q5 confusion matrix pattern not found"
    content = pattern_q5_cm.sub(new_q5_cm, content)

    # 4. Update grand total paragraph
    old_grand_p = (
        "เมื่อพิจารณาผลรวมทั้ง 204 คำตอบ พบว่าคะแนนตรงกัน 157 คำตอบ คิดเป็น Exact Agreement (Exact Match) ร้อยละ 76.96 มีค่า MAE เท่ากับ 0.1360 คะแนน และ QWK เท่ากับ 0.8488"
    )
    new_grand_p = (
        "เมื่อพิจารณาผลรวมทั้ง 204 คำตอบ พบว่าคะแนนตรงกัน 160 คำตอบ คิดเป็น Exact Agreement (Exact Match) ร้อยละ 78.43 มีค่า MAE เท่ากับ 0.1311 คะแนน และ QWK เท่ากับ 0.8685"
    )
    assert old_grand_p in content, "old_grand_p not found"
    content = content.replace(old_grand_p, new_grand_p)

    # 5. Update Section 4.1.6 introductory paragraphs
    old_p271 = (
        "จากการทดลองประเมินคำตอบทั้งหมด 204 รายการ แบบจำลองให้คะแนนตรงกับคะแนนอ้างอิงของผู้สอนจำนวน 157 รายการ (ร้อยละ 76.96) และมีคะแนนแตกต่างกันจำนวน 47 รายการ (ร้อยละ 23.04) โดยพบในข้อที่ 1 จำนวน 7 รายการ, ข้อที่ 2 จำนวน 15 รายการ, ข้อที่ 3 จำนวน 22 รายการ และข้อที่ 5 จำนวน 3 รายการ ส่วนข้อที่ 4 และข้อที่ 6 ซึ่งเป็นโจทย์การวาดโครงสร้างต้นไม้ มีคะแนนตรงกันทุกรายการ (ร้อยละ 100)"
    )
    new_p271 = (
        "จากการทดลองประเมินคำตอบทั้งหมด 204 รายการ แบบจำลองให้คะแนนตรงกับคะแนนอ้างอิงของผู้สอนจำนวน 160 รายการ (ร้อยละ 78.43) และมีคะแนนแตกต่างกันจำนวน 44 รายการ (ร้อยละ 21.57) โดยพบเฉพาะในกลุ่มข้อสอบแบบข้อความ ได้แก่ ข้อที่ 1 จำนวน 7 รายการ, ข้อที่ 2 จำนวน 15 รายการ และข้อที่ 3 จำนวน 22 รายการ ส่วนข้อสอบประเภทภาพเขียนมือเชิงโครงสร้างและสัญลักษณ์ (ข้อที่ 4, ข้อที่ 5 และข้อที่ 6) แบบจำลองให้คะแนนตรงกับผู้สอนทุกรายการครบทั้ง 102 คำตอบ (ร้อยละ 100.00)"
    )
    assert old_p271 in content, "old_p271 not found"
    content = content.replace(old_p271, new_p271)

    old_p272 = (
        "เมื่อนำคำตอบที่มีคะแนนต่างกันมาเปรียบเทียบกับเกณฑ์และคำอธิบายของแบบจำลอง พบตัวอย่างที่น่าสนใจ 5 กรณี แบ่งเป็นคำตอบประเภทข้อความ 4 กรณี ในตารางที่ 4.7 และคำตอบประเภทภาพเขียนมือ 1 กรณี ในตารางที่ 4.8 โดยการวิเคราะห์พิจารณาจากข้อมูลที่บันทึกไว้"
    )
    new_p272 = (
        "เมื่อนำคำตอบที่มีคะแนนต่างกันมาเปรียบเทียบกับเกณฑ์และคำอธิบายของแบบจำลอง พบตัวอย่างกรณีศึกษาที่น่าสนใจ 4 กรณีในกลุ่มคำตอบประเภทข้อความ ดังแสดงในตารางที่ 4.7 โดยการวิเคราะห์พิจารณาจากข้อมูลที่บันทึกไว้"
    )
    assert old_p272 in content, "old_p272 not found"
    content = content.replace(old_p272, new_p272)

    # 6. Remove Table 4.8 (Case Study 5: DS-159)
    pattern_table48 = re.compile(
        r'<div class="table-block">\s*<div class="table-title">ตารางที่ 4\.8 กรณีศึกษาเปรียบเทียบความคลาดเคลื่อนในการให้คะแนนข้อสอบประเภทภาพเขียนมือ \(รหัสตัวอย่าง DS-159\)</div>.*?</table>\s*</div>',
        re.DOTALL
    )
    assert pattern_table48.search(content), "Table 4.8 block not found"
    content = pattern_table48.sub("", content)

    # 7. Update conclusion paragraph of 4.1.6
    old_p357 = (
        "<p>จากทั้ง 5 กรณีศึกษา พบว่าความแตกต่างของคะแนนเกิดขึ้นได้จากหลายมิติ ทั้งกรณีที่ผู้สอนยืดหยุ่นหรือพิจารณาภาพรวม (กรณีศึกษาที่ 1 และ 2) กรณีที่ AI ช่วยให้คะแนนส่วนย่อยได้อย่างเป็นธรรม (กรณีศึกษาที่ 3) กรณีที่ AI อนุมานความหมายจากคำสำคัญเข้าข้างผู้เรียนเกินจริง (กรณีศึกษาที่ 4) และกรณีที่ AI เกิดความผิดพลาดในการอ่านสัญลักษณ์ลายมือ (กรณีศึกษาที่ 5) การนำระบบ AI มาช่วยประเมินร่วมกับการเปิดโอกาสให้ผู้สอนตรวจทานและแก้ไขคะแนน (Human-in-the-Loop) จึงเป็นแนวทางที่เหมาะสมและรัดกุมที่สุดในการรักษามาตรฐานความถูกต้องและความเป็นธรรมในการวัดผล</p>"
    )
    new_p357 = (
        "<p>จากกรณีศึกษาทั้ง 4 กรณี ซึ่งพบเฉพาะในข้อสอบประเภทข้อความ พบว่าความแตกต่างของคะแนนเกิดขึ้นได้จากหลายมิติ ทั้งกรณีที่ผู้สอนยืดหยุ่นหรือพิจารณาภาพรวม (กรณีศึกษาที่ 1 และ 2) กรณีที่ AI ช่วยให้คะแนนส่วนย่อยได้อย่างเป็นธรรม (กรณีศึกษาที่ 3) และกรณีที่ AI อนุมานความหมายจากคำสำคัญเข้าข้างผู้เรียนเกินจริง (กรณีศึกษาที่ 4) ส่วนข้อสอบประเภทภาพลายมือเชิงโครงสร้างและสัญลักษณ์ แบบจำลองสามารถตรวจจับโครงสร้าง ลำดับขั้นตอน และสัญลักษณ์ได้อย่างแม่นยำตรงกับผู้สอนสมบูรณ์แบบร้อยละ 100.00 อย่างไรก็ดี การนำระบบ AI มาช่วยประเมินร่วมกับการเปิดโอกาสให้ผู้สอนตรวจทานและแก้ไขคะแนน (Human-in-the-Loop) ยังคงเป็นแนวทางที่เหมาะสมและรัดกุมที่สุดในการรักษามาตรฐานความถูกต้องและความเป็นธรรมในการวัดผล</p>"
    )
    assert old_p357 in content, "old_p357 not found"
    content = content.replace(old_p357, new_p357)

    # 8. Renumber Table 4.9 -> Table 4.8, 4.10 -> 4.9, ..., 4.30 -> 4.29
    # We must do this from 4.9 up to 4.30 in sequential or regex replacement
    # To prevent double replacement (e.g. 4.9 -> 4.8 then 4.8 -> 4.7), replace with tokens first or use a replacement function
    def renumber_match(m):
        num = int(m.group(1))
        if num >= 9:
            return f"ตารางที่ 4.{num - 1}"
        return m.group(0)

    content = re.sub(r"ตารางที่ 4\.(\d+)", renumber_match, content)

    # Write back to docs_and_tests/chapter4_testcases.html
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully updated: {HTML_FILE}")

    # Sync to public/chapter4_testcases.html
    public_file = ROOT / "public" / "chapter4_testcases.html"
    shutil.copy2(HTML_FILE, public_file)
    print(f"Successfully synced: {public_file}")

    # Sync to client/public/chapter4_testcases.html if different
    client_public_file = ROOT / "client" / "public" / "chapter4_testcases.html"
    try:
        shutil.copy2(HTML_FILE, client_public_file)
        print(f"Successfully synced: {client_public_file}")
    except shutil.SameFileError:
        pass

if __name__ == "__main__":
    update_chapter4_document()
