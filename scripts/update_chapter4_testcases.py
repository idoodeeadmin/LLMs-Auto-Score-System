import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / 'docs_and_tests' / 'chapter4_testcases.html'

def update_chapter4():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # Define the 3 new sections to be inserted between test-2 and test-3 (which becomes test-6)
    new_sections = '''
    <section class="test-section" id="test-google-login">
    <h3>4.1.3 การทดสอบเข้าสู่ระบบด้วยบัญชี Google</h3>
    <p class="scope">อ้างอิงการออกแบบระบบบทที่ 3 หัวข้อ 3.7.3</p>
    <p>ทดสอบการเข้าใช้งานระบบอย่างสะดวกรวดเร็วผ่านบัญชี Google โดยผู้ใช้สามารถกดเลือกเข้าสู่ระบบด้วยบัญชี Google เดิมที่เคยใช้งาน หรือกรณีเป็นผู้ใช้ใหม่ที่เข้าสู่ระบบครั้งแรก ระบบจะทำการสร้างบัญชีให้อัตโนมัติและนำทางไปยังหน้าเลือกบทบาทผู้เรียนหรือผู้สอนอย่างถูกต้อง รายละเอียดกรณีทดสอบแสดงในตารางที่ 4.3</p>
    <div class="table-block"><div class="table-title">ตารางที่ 4.3 การทดสอบเข้าสู่ระบบด้วยบัญชี Google</div>
    <table><thead><tr><th>ข้อมูลนำเข้า</th><th class="case">Test Case 1</th><th class="case">Test Case 2</th><th class="case">Test Case 3</th></tr></thead><tbody>
      <tr><td>การดำเนินการ</td><td>เข้าสู่ระบบด้วยบัญชี Google เดิม</td><td>เข้าสู่ระบบด้วยบัญชี Google ครั้งแรก</td><td>ยกเลิกการเข้าสู่ระบบผ่าน Google</td></tr>
      <tr><td>บัญชี Google ที่ใช้</td><td>student01@gmail.com (เคยใช้งานแล้ว)</td><td>newuser@gmail.com (เข้าใช้งานครั้งแรก)</td><td>ไม่เลือกบัญชี</td></tr>
      <tr><td>การยืนยันตัวตน</td><td>เลือกบัญชีผ่านหน้าต่างของ Google</td><td>เลือกบัญชีผ่านหน้าต่างของ Google</td><td>ปิดหน้าต่างของ Google หรือกดยกเลิก</td></tr>
      <tr><td>ผลลัพธ์ที่คาดหวัง</td><td>เข้าสู่ระบบสำเร็จและนำทางไปยังหน้าหลัก</td><td>สร้างบัญชีใหม่อัตโนมัติและไปหน้าเลือกบทบาท</td><td>หน้าต่างปิดลงและยังคงอยู่ที่หน้าเข้าสู่ระบบเดิม</td></tr>
      <tr><td>ผลลัพธ์ที่ได้</td><td>................................</td><td>................................</td><td>................................</td></tr>
      <tr><td>ผลการทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td></tr>
    </tbody></table></div>
    </section>

    <section class="test-section" id="test-forgot-password">
    <h3>4.1.4 การทดสอบลืมรหัสผ่านและขอตั้งรหัสผ่านใหม่</h3>
    <p class="scope">อ้างอิงการออกแบบระบบบทที่ 3 ข้อ 3.4.4.3 (กระบวนการ 1.3) และตารางที่ 3.11</p>
    <p>ทดสอบกระบวนการขอความช่วยเหลือเมื่อผู้ใช้จำรหัสผ่านไม่ได้ โดยสามารถกรอกอีเมลที่ลงทะเบียนไว้เพื่อขอรับลิงก์สำหรับตั้งรหัสผ่านใหม่ทางกล่องข้อความอีเมล หรือเลือกยืนยันตัวตนด้วยข้อมูลรหัสนิสิตหรือชื่อผู้ใช้งานเพื่อขอตั้งรหัสผ่านใหม่ได้ทันที รายละเอียดกรณีทดสอบแสดงในตารางที่ 4.4</p>
    <div class="figure"><img src="../public/screenshots/forgot-password.png?v=20260925-scope" alt="หน้าลืมรหัสผ่าน"><div class="caption">ภาพประกอบที่ 4.3 หน้าลืมรหัสผ่านและขอตั้งรหัสผ่านใหม่</div></div>
    <div class="table-block"><div class="table-title">ตารางที่ 4.4 การทดสอบลืมรหัสผ่านและขอตั้งรหัสผ่านใหม่</div>
    <table><thead><tr><th>ข้อมูลนำเข้า</th><th class="case">Test Case 1</th><th class="case">Test Case 2</th><th class="case">Test Case 3</th></tr></thead><tbody>
      <tr><td>ช่องทางการขอความช่วยเหลือ</td><td>ขอรับลิงก์ทางอีเมล</td><td>ขอรับลิงก์ทางอีเมล</td><td>ยืนยันตัวตนด้วยตนเอง</td></tr>
      <tr><td>ข้อมูลที่ใช้ระบุตัวตน</td><td>student01@example.com (มีในระบบ)</td><td>unknown@example.com (ไม่มีในระบบ)</td><td>อีเมลและรหัสนิสิตที่ถูกต้องตรงกัน</td></tr>
      <tr><td>การดำเนินการ</td><td>กดปุ่ม "ส่งลิงก์รีเซ็ตรหัสผ่าน"</td><td>กดปุ่ม "ส่งลิงก์รีเซ็ตรหัสผ่าน"</td><td>กรอกข้อมูลครบถ้วนแล้วกดยืนยันตัวตน</td></tr>
      <tr><td>ผลลัพธ์ที่คาดหวัง</td><td>ระบบส่งลิงก์ไปยังอีเมลและแจ้งเตือนส่งเรียบร้อย</td><td>ระบบแจ้งเตือนว่าไม่พบข้อมูลบัญชีผู้ใช้งานนี้</td><td>ตรวจสอบข้อมูลถูกต้องและนำทางไปหน้าตั้งรหัสใหม่ทันที</td></tr>
      <tr><td>ผลลัพธ์ที่ได้</td><td>................................</td><td>................................</td><td>................................</td></tr>
      <tr><td>ผลการทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td></tr>
    </tbody></table></div>
    </section>

    <section class="test-section" id="test-reset-and-verify">
    <h3>4.1.5 การทดสอบตั้งรหัสผ่านใหม่และการยืนยันอีเมล</h3>
    <p class="scope">อ้างอิงการออกแบบระบบบทที่ 3 ข้อ 3.4.4.3 (กระบวนการ 1.3) และตารางที่ 3.12</p>
    <p>ทดสอบการกำหนดรหัสผ่านใหม่ผ่านลิงก์ที่ได้รับ ตลอดจนการตรวจสอบสถานะการยืนยันอีเมลของผู้ใช้งาน เพื่อสร้างความมั่นใจในความถูกต้องและความปลอดภัยของบัญชีก่อนเข้าใช้งานระบบ รายละเอียดกรณีทดสอบแสดงในตารางที่ 4.5</p>
    <div class="table-block"><div class="table-title">ตารางที่ 4.5 การทดสอบตั้งรหัสผ่านใหม่และการยืนยันอีเมล</div>
    <table><thead><tr><th>ข้อมูลนำเข้า</th><th class="case">Test Case 1</th><th class="case">Test Case 2</th><th class="case">Test Case 3</th></tr></thead><tbody>
      <tr><td>การดำเนินการ</td><td>ตั้งรหัสผ่านใหม่ผ่านลิงก์ที่ได้รับ</td><td>ตั้งรหัสผ่านใหม่โดยรหัสผ่านไม่ตรงกัน</td><td>เข้าสู่ระบบด้วยบัญชีที่ยังไม่ยืนยันอีเมล</td></tr>
      <tr><td>ข้อมูลที่กรอก</td><td>รหัสผ่านใหม่และยืนยันรหัสผ่านตรงกัน</td><td>รหัสผ่านใหม่และการยืนยันไม่ตรงกัน</td><td>อีเมลและรหัสผ่านถูกต้องแต่ยังไม่ยืนยันอีเมล</td></tr>
      <tr><td>เงื่อนไขการทดสอบ</td><td>ลิงก์ยังไม่หมดอายุและยังไม่เคยใช้งาน</td><td>ลิงก์ยังไม่หมดอายุ</td><td>กดปุ่ม "ส่งลิงก์ยืนยันใหม่" บนหน้าจอ</td></tr>
      <tr><td>ผลลัพธ์ที่คาดหวัง</td><td>บันทึกรหัสผ่านใหม่สำเร็จและไปหน้าเข้าสู่ระบบ</td><td>ระบบแจ้งเตือนว่ารหัสผ่านไม่ตรงกันและไม่บันทึก</td><td>ระบบแจ้งเตือนให้ยืนยันอีเมลและส่งลิงก์ซ้ำได้สำเร็จ</td></tr>
      <tr><td>ผลลัพธ์ที่ได้</td><td>................................</td><td>................................</td><td>................................</td></tr>
      <tr><td>ผลการทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td><td>☐ ผ่าน ☐ ไม่ผ่าน<br>☐ ยังไม่ทดสอบ</td></tr>
    </tbody></table></div>
    </section>
'''

    # Split html into parts: before test-3 and from test-3 onwards
    marker = '<section class="test-section" id="test-3">'
    if marker not in html:
        print("Error: Marker not found!")
        return

    part1, part2 = html.split(marker, 1)

    # In part2, we need to:
    # 1. Renumber sections 4.1.3 to 4.1.16 -> 4.1.6 to 4.1.19
    # We do this backwards to avoid collision
    for old_sec in range(16, 2, -1):
        new_sec = old_sec + 3
        part2 = part2.replace(f'<h3>4.1.{old_sec} ', f'<h3>4.1.{new_sec} ')
        part2 = part2.replace(f'id="test-{old_sec}"', f'id="test-{new_sec}"')

    # 2. Renumber figures in part2:
    # In original:
    # ภาพประกอบที่ 4.3 -> 4.4
    # ภาพประกอบที่ 4.4 -> 4.5
    # ...
    # ภาพประกอบที่ 4.12 -> 4.13
    for old_fig in range(12, 2, -1):
        new_fig = old_fig + 1
        part2 = part2.replace(f'ภาพประกอบที่ 4.{old_fig} ', f'ภาพประกอบที่ 4.{new_fig} ')

    # 3. Renumber tables in part2:
    # In original:
    # ตารางที่ 4.3 -> 4.6
    # ตารางที่ 4.4 -> 4.7
    # ...
    # ตารางที่ 4.21 -> 4.24
    for old_tbl in range(21, 2, -1):
        new_tbl = old_tbl + 3
        # Match table titles and text references: "ตารางที่ 4.{old_tbl}"
        # Careful with substrings: match with word boundary or non-digit lookahead
        pattern = rf'ตารางที่ 4\.{old_tbl}(?!\d)'
        replacement = f'ตารางที่ 4.{new_tbl}'
        part2 = re.sub(pattern, replacement, part2)

    # Also update section test-3 marker id
    part2 = '<section class="test-section" id="test-6">' + part2

    # Assemble full updated HTML
    updated_html = part1 + new_sections + '\n    ' + part2

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"Successfully updated {HTML_FILE.name}!")

if __name__ == '__main__':
    update_chapter4()
