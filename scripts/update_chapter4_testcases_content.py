import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "docs_and_tests" / "chapter4_testcases.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update bar chart for Q1: 73.53% -> 85.29%
content = content.replace(
    '<div class="bar-row"><span>ข้อ 1</span><div class="bar-track"><div class="bar-fill" style="width:73.53%"></div></div><span class="bar-value">73.53%</span></div>',
    '<div class="bar-row"><span>ข้อ 1</span><div class="bar-track"><div class="bar-fill" style="width:85.29%"></div></div><span class="bar-value">85.29%</span></div>'
)

# 2. Update Table 4.4 Result Table:
old_t4_4 = """<div class="table-block"><div class="table-title">ตารางที่ 4.4 ผลการประเมินจำแนกรายข้อ</div>
      <table class="result-table"><thead><tr><th>ข้อ</th><th>หัวข้อ</th><th>N</th><th>ตรงกัน</th><th>ร้อยละ</th><th>MAE</th><th>QWK</th></tr></thead><tbody><tr><td>1</td><td>Row-major และ Column-major</td><td>34</td><td>25</td><td>73.53</td><td>0.2941</td><td>0.6318</td></tr>
<tr><td>2</td><td>O(n log n) และ O(n²)</td><td>34</td><td>18</td><td>52.94</td><td>0.2647</td><td>0.6230</td></tr>
<tr><td>3</td><td>Linked List และ Array</td><td>34</td><td>16</td><td>47.06</td><td>0.1691</td><td>0.6535</td></tr>
<tr><td>4</td><td>การสร้าง Binary Search Tree</td><td>34</td><td>27</td><td>79.41</td><td>0.1985</td><td>0.4733</td></tr>
<tr><td>5</td><td>Infix เป็น Prefix และ Postfix</td><td>34</td><td>31</td><td>91.18</td><td>0.0515</td><td>0.8137</td></tr>
<tr><td>6</td><td>General Tree เป็น Binary Tree</td><td>34</td><td>34</td><td>100.00</td><td>0.0000</td><td>1.0000</td></tr>
</tbody></table></div>"""

new_t4_4 = """<div class="table-block"><div class="table-title">ตารางที่ 4.4 ผลการประเมินจำแนกรายข้อสอบ</div>
      <table class="result-table"><thead><tr><th>ข้อ</th><th>หัวข้อ</th><th>ประเภท</th><th>N</th><th>ตรงกัน</th><th>ร้อยละ</th><th>ต่างไม่เกิน 0.50</th><th>MAE</th><th>Pearson r</th><th>QWK</th></tr></thead><tbody><tr><td>1</td><td>Row-major และ Column-major</td><td>ข้อความ</td><td>34</td><td>29</td><td>85.29%</td><td>94.12%</td><td>0.1765</td><td>0.8872</td><td>0.6318</td></tr>
<tr><td>2</td><td>O(n log n) และ O(n²)</td><td>ข้อความ</td><td>34</td><td>18</td><td>52.94%</td><td>94.12%</td><td>0.2647</td><td>0.7190</td><td>0.6230</td></tr>
<tr><td>3</td><td>Linked List และ Array</td><td>ข้อความ</td><td>34</td><td>16</td><td>47.06%</td><td>100.0%</td><td>0.2500</td><td>0.6698</td><td>0.6535</td></tr>
<tr><td>4</td><td>การสร้าง Binary Search Tree</td><td>ภาพวาด</td><td>34</td><td>27</td><td>79.41%</td><td>79.41%</td><td>0.1985</td><td>0.4761</td><td>0.4733</td></tr>
<tr><td>5</td><td>Infix เป็น Prefix และ Postfix</td><td>ภาพวาด</td><td>34</td><td>31</td><td>91.18%</td><td>97.06%</td><td>0.0882</td><td>0.8660</td><td>0.8137</td></tr>
<tr><td>6</td><td>General Tree เป็น Binary Tree</td><td>ภาพวาด</td><td>34</td><td>34</td><td>100.00%</td><td>100.0%</td><td>0.0000</td><td>1.0000</td><td>1.0000</td></tr>
</tbody></table></div>"""

content = content.replace(old_t4_4, new_t4_4)

# 3. Update narrative after Table 4.4
old_narrative = "ข้อ 6 มีคะแนนตรงกับผู้สอนทั้ง 34 คำตอบและมี QWK เท่ากับ 1.0000 ส่วนข้อ 5 มีคะแนนตรงกัน 31 คำตอบและมี MAE เท่ากับ 0.0515 คะแนน ข้อ 3 มีอัตราคะแนนตรงกันต่ำที่สุดที่ร้อยละ 47.06 ขณะที่ข้อ 1 มี MAE สูงที่สุดเท่ากับ 0.2941 คะแนน และข้อ 4 มี QWK ต่ำที่สุดเท่ากับ 0.4733"
new_narrative = "ข้อ 6 มีคะแนนตรงกับผู้สอนสมบูรณ์แบบทั้ง 34 คำตอบ (100.0%) และมีค่า QWK เท่ากับ 1.0000 ส่วนข้อ 5 มีคะแนนตรงกัน 31 คำตอบ (91.18%) และค่า MAE ต่ำเพียง 0.0882 คะแนน สำหรับข้อ 1 ระบบทำความแม่นยำตรงกันได้ถึง 29 คำตอบ (85.29%) และมีค่าสัมประสิทธิ์สหสัมพันธ์สูงถึง 0.8872 ส่วนข้อ 3 แม้อัตราคะแนนตรงกันจะอยู่ที่ร้อยละ 47.06 แต่คะแนนมีความคลาดเคลื่อนไม่เกิน 0.50 คะแนนครบทั้ง 100% (34/34 คำตอบ) ขณะที่ข้อ 4 มีค่า QWK เท่ากับ 0.4733 เนื่องจากผลกระทบของความไม่สมดุลของระดับคะแนนตามปรากฏการณ์ Prevalence Paradox"

content = content.replace(old_narrative, new_narrative)

# 4. Update 4.1.6 Qualitative Representative Case Studies (Replacing old 3 examples from Q1 only)
# Find the start and end of section 4.1.6
sec_416_start = content.find('<section class="test-section" id="evaluation-examples">')
sec_417_start = content.find('<section class="test-section" id="evaluation-discussion">')

if sec_416_start != -1 and sec_417_start != -1:
    new_sec_416 = """<section class="test-section" id="evaluation-examples">
      <h3>4.1.6 ตัวอย่างผลการตรวจให้คะแนนจริงจากชุดข้อมูล (Qualitative Case Studies)</h3>
      <p>เพื่อให้เห็นภาพกระบวนการให้คะแนนและการให้ข้อเสนอแนะเชิงคุณภาพของระบบ จึงได้คัดเลือกตัวอย่างกระดาษคำตอบที่เป็นตัวแทนของแต่ละกลุ่มข้อสอบจริง ทั้งกลุ่มข้อสอบอัตนัยแบบข้อความ (Text-based) และกลุ่มข้อสอบอัตนัยแบบรูปภาพ (Vision-based) ครอบคลุมทั้งกรณีที่คะแนนตรงกันสมบูรณ์ คะแนนบางส่วน และข้อผิดพลาด ดังนี้</p>

      <h4>กลุ่มข้อสอบอัตนัยแบบข้อความ (Text-based Responses)</h4>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.7 กรณีศึกษาที่ 1: ข้อ 1 (Row-major vs Column-major) รหัสตัวอย่าง DS-001 [คะแนนเต็ม ตรงกันสมบูรณ์]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>อธิบายความแตกต่างของการจัดเก็บข้อมูลแบบ Row-major และ Column-major ใน Array 2 มิติ (คะแนนเต็ม 2.00 คะแนน)</td></tr>
          <tr><th scope="row">คำตอบผู้เรียน</th><td>Row-major เป็นการจัดเก็บข้อมูลในอาร์เรย์ 2 มิติ โดยจัดเรียงตามแนวนอน (แถว) ไปเรื่อยๆ จนหมดแถว แล้วจึงขึ้นแถวใหม่ ส่วน Column-major เป็นการจัดเก็บข้อมูลโดยเรียงตามแนวตั้ง (คอลัมน์) จากบนลงล่างทีละหลักจนครบ</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>ประเมินสองส่วน: อธิบาย Row-major ได้ 1.00 คะแนน และอธิบาย Column-major ได้ 1.00 คะแนน (คะแนนรวมเป็น 0.00, 1.00 หรือ 2.00 คะแนน)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>นิสิตอธิบายหลักการจัดเก็บข้อมูลของทั้ง Row-major (ตามแถว) และ Column-major (ตามคอลัมน์) ได้ถูกต้องชัดเจน ครบทั้ง 2 ส่วนตามเกณฑ์ ได้คะแนนเต็ม 2.00 คะแนน</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ยอดเยี่ยมมาก อธิบายความแตกต่างของลำดับการจัดเรียงในหน่วยความจำระหว่างแถวและคอลัมน์ได้ถูกต้องและตรงประเด็น</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.8 กรณีศึกษาที่ 2: ข้อ 2 (Time Complexity) รหัสตัวอย่าง DS-041 [คะแนนเต็ม พร้อมเหตุผลและอัลกอริทึม]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลขนาดใหญ่มากกว่า O(n²) และยกตัวอย่าง Algorithm (คะแนนเต็ม 2.00 คะแนน)</td></tr>
          <tr><th scope="row">คำตอบผู้เรียน</th><td>O(n log n) เหมาะกับข้อมูลขนาดใหญ่มากกว่า O(n²) เพราะใช้วิธีแบ่งข้อมูลออกเป็นส่วนย่อยๆ แล้วค่อยจัดการ ทำให้จำนวนรอบการทำงานเติบโตช้ากว่ามากเมื่อ n มีขนาดใหญ่ ส่วน O(n²) มักเป็นการวนลูปซ้อนกันทำให้ใช้เวลานาน เช่น Merge Sort และ Quick Sort</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>มีชื่ออัลกอริทึมและอธิบายเหตุผลเชิงเปรียบเทียบว่า O(n log n) ใช้ขั้นตอนน้อยกว่าเมื่อข้อมูลขนาดใหญ่ได้ 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>มีการระบุชื่ออัลกอริทึมที่เกี่ยวข้อง (Merge Sort, Quick Sort) และอธิบายเหตุผลเปรียบเทียบเชิงประสิทธิภาพได้อย่างถูกต้องตามเกณฑ์ระดับสมบูรณ์ ได้ 2.00 คะแนนเต็ม</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ตอบได้ดีมาก ครอบคลุมทั้งแนวคิดการแบ่งย่อยข้อมูล (Divide and Conquer) และการยกตัวอย่างอัลกอริทึมประกอบ</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.9 กรณีศึกษาที่ 3: ข้อ 3 (Linked List vs Array) รหัสตัวอย่าง DS-072 [คะแนนบางส่วน Partial Credit]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>เปรียบเทียบความแตกต่างระหว่าง Linked List กับ Array ในการนำไปสร้าง Stack และ Queue พร้อมระบุข้อดีข้อเสีย (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">คำตอบผู้เรียน</th><td>Array มีขนาดคงที่ ต้องระบุขนาดล่วงหน้า ส่วน Linked List มีขนาดปรับเปลี่ยนได้ตามข้อมูลที่ใส่เข้ามา (Dynamic)</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>ประเมินสองส่วน: ความแตกต่างเชิงโครงสร้าง (0.50 คะแนน) และข้อดีข้อเสียในการใช้งาน (0.50 คะแนน)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์ในระดับคะแนนบางส่วน)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>นิสิตตอบถูกต้องในส่วนความแตกต่างเชิงโครงสร้าง (Fixed vs Dynamic Size) ได้ 0.50 คะแนน แต่ไม่ได้ระบุข้อดีและข้อเสียในการนำไปใช้งานของ Stack/Queue จึงไม่ได้คะแนนในส่วนที่ 2 (0.00 คะแนน) รวมได้ 0.50 คะแนนตรงตามเกณฑ์</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ตอบความแตกต่างเชิงโครงสร้างได้ถูกต้อง ควรเสริมข้อดีข้อเสีย เช่น การเข้าถึงแบบสุ่ม O(1) ของ Array และการป้องกัน Overflow ของ Linked List</td></tr>
        </tbody></table>
      </div>

      <h4>กลุ่มข้อสอบอัตนัยแบบรูปภาพและโครงสร้าง (Vision-based Responses)</h4>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.10 กรณีศึกษาที่ 4: ข้อ 4 (Binary Search Tree) รหัสตัวอย่าง DS-104 [คะแนนเต็ม โครงสร้างถูกต้องครบ 12 โหนด]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>จงวาด Binary Search Tree จากชุดข้อมูล 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99 (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">ลักษณะคำตอบผู้เรียน</th><td>ภาพถ่ายกระดาษวาดโครงสร้างต้นไม้ค้นหาทวิภาคครบทั้ง 12 โหนดตามลำดับการแทรกข้อมูล เส้นเชื่อมกิ่งและตำแหน่งซ้าย-ขวาชัดเจน</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>โครงสร้าง BST ถูกต้องครบทั้ง 12 โหนดตามคุณสมบัติ โหนดซ้าย &lt; โหนดแม่ &lt; โหนดขวา ได้ 1.00 คะแนน ผิดตำแหน่งหรือผิดหลักการได้ 0.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>1.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>1.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>โครงสร้าง Binary Search Tree ถูกต้องครบทั้ง 12 โหนดตามคุณสมบัติ โหนดซ้าย &lt; โหนดแม่ &lt; โหนดขวา (Root=9 ซ้าย=5 ขวา=16; ใต้ 16 ซ้าย=10 ขวา=76; ใต้ 10 ขวา=13; ใต้ 13 ซ้าย=11 ขวา=15; ใต้ 76 ซ้าย=58 ขวา=92; ใต้ 92 ซ้าย=80 ขวา=99) ให้ 1.00 คะแนนเต็ม</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>วาดโครงสร้างต้นไม้ค้นหาทวิภาคได้ถูกต้องสมบูรณ์และวางตำแหน่งกิ่งซ้าย-ขวาได้ถูกต้องตามลำดับการแทรกข้อมูล</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.11 กรณีศึกษาที่ 5: ข้อ 5 (Infix to Prefix & Postfix) รหัสตัวอย่าง DS-154 [คะแนนบางส่วน Prefix ถูก Postfix ผิด]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>จงแสดงวิธีทำในการแปลง Infix Expression: A + (B * (C - (D / (F * 2)))) เป็น Prefix และ Postfix (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">ลักษณะคำตอบผู้เรียน</th><td>ภาพถ่ายกระดาษแสดงวิธีทำ โดยส่วน Prefix ได้คำตอบสุดท้าย +A*B-C/D*F2 แต่ส่วน Postfix เขียนตัวดำเนินการไว้กึ่งกลางเป็น A+B*C-D/F2*</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>แยกประเมิน Prefix (0.50 คะแนน) และ Postfix (0.50 คะแนน) โดยต้องมีขั้นตอนวิธีทำและคำตอบสุดท้ายถูกต้อง</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์ในระดับคะแนนบางส่วน)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ส่วน Prefix ได้ 0.50 คะแนน (คำตอบสุดท้าย +A*B-C/D*F2 ถูกต้อง) แต่ส่วน Postfix ได้ 0.00 คะแนน เนื่องจากเขียนตัวดำเนินการสลับที่และไม่เป็นไปตามหลัก Postfix (เขียนเป็น A+B*C-D/F2*) รวมคะแนนได้ 0.50 คะแนน</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ส่วน Prefix ทำได้ถูกต้องแล้ว แต่ส่วน Postfix ควรนำตัวดำเนินการไปวางไว้ท้ายตัวถูกดำเนินการเสมอ เช่น (F*2) ต้องแปลงเป็น F2*</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.12 กรณีศึกษาที่ 6: ข้อ 6 (General Tree to Binary Tree) รหัสตัวอย่าง DS-171 [คะแนนศูนย์ ผิดหลักการทางทฤษฎี]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>จงแปลง General Tree 10 โหนด ให้เป็น Binary Tree ด้วยหลักการ Left-Child Right-Sibling (LCRS) (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">ลักษณะคำตอบผู้เรียน</th><td>ภาพถ่ายแสดงการวาดต้นไม้ 10 โหนด แต่ไม่ได้แปลงตามหลัก LCRS โดยเชื่อมโหนด 1 ไปยัง 2, 3, 4 โดยตรงในลักษณะ General Tree ดั้งเดิม</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>แปลงตามหลัก LCRS ถูกต้องครบ 10 โหนดได้ 1.00 คะแนน โครงสร้างแตกกิ่งผิด หรือไม่แปลงได้ 0.00 คะแนน (ระดับคะแนน 1.00 หรือ 0.00 เท่านั้น)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>0.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์ในการตรวจพบข้อผิดพลาดเชิงโครงสร้าง)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>นิสิตวาดเป็น General Tree เดิม โดยเชื่อมโหนด 1 ไปยัง 2, 3, 4 โดยตรง ไม่ได้แปลงตามหลัก Left-Child Right-Sibling (LCRS) ที่กำหนดให้ 1 มีลูกซ้ายเป็น 2 และ 2 เชื่อมกิ่งขวาไป 3 และ 4 จึงผิดหลักการอย่างมีนัยสำคัญ ได้ 0.00 คะแนน</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>คำตอบยังเป็นต้นไม้เดิมที่มีลูกหลายกิ่ง ให้จำหลักการ LCRS ว่ากิ่งซ้ายแทนลูกคนแรก (First Child) และกิ่งขวาแทนพี่น้องถัดไป (Next Sibling) แต่ละโหนดจึงต้องมีกิ่งแตกออกได้ไม่เกิน 2 ทาง</td></tr>
        </tbody></table>
      </div>
    </section>
"""
    content = content[:sec_416_start] + new_sec_416 + content[sec_417_start:]

# 5. Renumber tables in section 4.2 (Test Cases) from 4.10 onwards -> 4.13 onwards
# In the original file, Table 4.10 was register test. Since we now have Tables 4.7 to 4.12 as case studies,
# the register test becomes Table 4.13, and so on.
# Let's adjust table numbering in section 4.2
for orig_num in range(28, 9, -1):
    new_num = orig_num + 3
    content = content.replace(f"ตารางที่ 4.{orig_num} ", f"ตารางที่ 4.{new_num} ")
    content = content.replace(f"ตารางที่ 4.{orig_num}</div>", f"ตารางที่ 4.{new_num}</div>")
    content = content.replace(f"ตารางที่ 4.{orig_num}<", f"ตารางที่ 4.{new_num}<")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated docs_and_tests/chapter4_testcases.html successfully!")
