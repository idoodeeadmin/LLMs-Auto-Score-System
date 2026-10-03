import re, sys

sys.stdout.reconfigure(encoding='utf-8')

html_file = 'docs_and_tests/chapter4_testcases.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS rules in <style>
css_to_add = """  .example-table th { width:24%; text-align:left; }
  .example-table td { white-space:normal; }
  .case-img-block { text-align:center; padding:6px 0; }
  .case-img { display:block; max-width:100%; max-height:225px; margin:0 auto; border:1px solid #94a3b8; border-radius:4px; box-shadow:0 1px 4px rgba(0,0,0,0.12); object-fit:contain; background:#f8fafc; }
  .caption-sm { font-size:14.5px; color:#475569; margin-top:4px; text-align:center; font-style:italic; }
</style>"""

content = content.replace("""  .example-table th { width:25%; text-align:left; }
.example-table td { white-space:normal; }
</style>""", css_to_add)

# 2. Section 4.1.6 Replacement with Embedded Student Answer Images and Correct Table Numbers
old_section_pattern = re.compile(
    r'<section class="test-section" id="evaluation-examples">.*?</section>\s*(?=<section class="test-section" id="evaluation-discussion">)',
    re.DOTALL
)

new_section = """<section class="test-section" id="evaluation-examples">
      <h3>4.1.6 ตัวอย่างผลการตรวจให้คะแนนจริงจากชุดข้อมูล (Qualitative Case Studies)</h3>
      <p>เพื่อให้เห็นภาพกระบวนการให้คะแนนและการให้ข้อเสนอแนะเชิงคุณภาพของระบบ จึงได้คัดเลือกตัวอย่างกระดาษคำตอบที่เป็นตัวแทนของแต่ละกลุ่มข้อสอบจริง พร้อมแนบภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต ทั้งกลุ่มข้อสอบอัตนัยแบบข้อความ (Text-based) และกลุ่มข้อสอบอัตนัยแบบรูปภาพ (Vision-based) ครอบคลุมทั้งกรณีที่คะแนนตรงกันสมบูรณ์ คะแนนบางส่วน และการตรวจพบข้อผิดพลาดเชิงโครงสร้าง ดังนี้</p>

      <h4>กลุ่มข้อสอบอัตนัยแบบข้อความ (Text-based Responses)</h4>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.7 กรณีศึกษาที่ 1: ข้อ 1 (Row-major vs Column-major) รหัสตัวอย่าง DS-001 [คะแนนเต็ม ตรงกันสมบูรณ์]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>อธิบายความแตกต่างของการจัดเก็บข้อมูลแบบ Row-major และ Column-major ใน Array 2 มิติ (คะแนนเต็ม 2.00 คะแนน)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบ</th><td>
            <div class="case-img-block">
              <img src="../public/screenshots/case_studies/case1_ds001.jpg" alt="ภาพถ่ายกระดาษคำตอบ DS-001" class="case-img" />
              <div class="caption-sm">ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-001 (ข้อ 1)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบผู้เรียน (ถอดความ)</th><td>Row จะนับเป็นแถวจากซ้ายไปขวา ส่วน Column จากบนลงล่าง<br>เช่น 0 1 2 3, 4 5 6 7, 8 9 10 11</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>ประเมินสองส่วน: อธิบาย Row-major ได้ 1.00 คะแนน และอธิบาย Column-major ได้ 1.00 คะแนน (คะแนนรวมเป็น 0.00, 1.00 หรือ 2.00 คะแนน)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>คำตอบได้คะแนนเต็ม 2.00 คะแนน เนื่องจากอธิบายองค์ประกอบสำคัญได้ครบทั้งสองส่วน: Row-major คือการเรียงข้อมูลตามแถวจากซ้ายไปขวา และ Column-major คือการเรียงข้อมูลตามคอลัมน์จากบนลงล่าง ซึ่งตรงตามเกณฑ์ Row-major 1.00 คะแนน และ Column-major 1.00 คะแนน ตัวอย่างข้อมูลที่จัดเป็นแถวยังสอดคล้องกับแนวคิดการเรียงแบบ Row-major</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ตอบได้ถูกต้องและได้คะแนนเต็ม โดยแยกความแตกต่างของ Row-major และ Column-major ได้ชัดเจนแล้ว หากต้องการให้สมบูรณ์ยิ่งขึ้น อาจระบุว่า Row-major เก็บข้อมูลในหน่วยความจำทีละแถว ส่วน Column-major เก็บทีละคอลัมน์</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.8 กรณีศึกษาที่ 2: ข้อ 2 (Time Complexity) รหัสตัวอย่าง DS-047 [คะแนนเต็ม พร้อมเหตุผลและอัลกอริทึม]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>อธิบายว่าทำไม O(n log n) เหมาะกับข้อมูลขนาดใหญ่มากกว่า O(n²) และยกตัวอย่าง Algorithm (คะแนนเต็ม 2.00 คะแนน)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบ</th><td>
            <div class="case-img-block">
              <img src="../public/screenshots/case_studies/case2_ds047.jpg" alt="ภาพถ่ายกระดาษคำตอบ DS-047" class="case-img" />
              <div class="caption-sm">ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-047 (ข้อ 2)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบผู้เรียน (ถอดความ)</th><td>เพราะว่า Big-O (n log n) จะทำการหารครึ่ง หรือแบ่งครึ่ง หรือ (n log n) ทำให้คำนวณข้อมูลขนาดใหญ่ได้เร็วกว่า O(n^2) ส่วน Big-O(n^2) ส่วนมากใช้ใน sort จะใช้เวลามากกว่าในการคำนวณ<br>ตัวอย่าง Algorithm: O(n log n) = Merge sort, O(n^2) = Insertion sort, Selection sort</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>มีชื่ออัลกอริทึมและอธิบายเหตุผลเชิงเปรียบเทียบว่า O(n log n) เติบโตช้ากว่า/ใช้ขั้นตอนน้อยกว่าเมื่อข้อมูลขนาดใหญ่ได้ 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>คำตอบได้คะแนนเต็ม 2.00 คะแนน เพราะระบุเหตุผลได้ถูกต้องว่า O(n log n) มีการแบ่งข้อมูล/หารครึ่ง และใช้เวลาน้อยกว่าหรือเร็วกว่า O(n^2) เมื่อข้อมูลมีขนาดใหญ่ อีกทั้งยกตัวอย่างอัลกอริทึมได้ถูกต้อง ได้แก่ Merge Sort สำหรับ O(n log n) และ Insertion Sort, Selection Sort สำหรับ O(n^2)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ตอบได้ถูกต้องและครบทั้งสองส่วน อธิบายว่า O(n log n) เติบโตช้ากว่าและมักใช้แนวคิดแบ่งข้อมูลเป็นส่วนย่อย รวมถึงยกตัวอย่างอัลกอริทึมได้ถูกต้องตรงตามทฤษฎี</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.9 กรณีศึกษาที่ 3: ข้อ 3 (Linked List vs Array) รหัสตัวอย่าง DS-072 [คะแนนบางส่วน Partial Credit]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>เปรียบเทียบความแตกต่างระหว่าง Linked List กับ Array ในการนำไปสร้าง Stack และ Queue พร้อมระบุข้อดีข้อเสีย (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบ</th><td>
            <div class="case-img-block">
              <img src="../public/screenshots/case_studies/case3_ds072.jpg" alt="ภาพถ่ายกระดาษคำตอบ DS-072" class="case-img" />
              <div class="caption-sm">ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-072 (ข้อ 3)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบผู้เรียน (ถอดความ)</th><td>สแตก ทำงานแบบ เข้าทีหลัง แต่ออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access<br>คิว ทำงานแบบ เข้าก่อน และออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access<br>อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>ประเมินสองส่วน: ความแตกต่างเชิงโครงสร้าง (0.50 คะแนน) และข้อดีข้อเสียในการใช้งาน (0.50 คะแนน)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์ในระดับคะแนนบางส่วน)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ได้ 0.50 คะแนนตามเกณฑ์ระดับมาตรฐาน เนื่องจากผู้เรียนระบุพฤติกรรม LIFO และ FIFO ได้ถูกต้อง และกล่าวถึงข้อดีข้อเสียของ Array บางส่วน แต่ไม่ได้เปรียบเทียบการใช้ Linked List กับ Array สำหรับ Stack/Queue โดยตรง และไม่ได้กล่าวถึงลักษณะ Dynamic จึงไม่ได้คะแนนในส่วนที่ 2 (0.00 คะแนน)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>เข้าใจพฤติกรรม Stack/Queue และ Array เบื้องต้น แต่ขาดประเด็นหลักคือการเปรียบเทียบ Linked List กับ Array ควรระบุว่า Array ขนาดคงที่ ส่วน Linked List ปรับขนาดได้ยืดหยุ่นด้วย Pointer</td></tr>
        </tbody></table>
      </div>

      <h4>กลุ่มข้อสอบอัตนัยแบบรูปภาพและโครงสร้าง (Vision-based Responses)</h4>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.10 กรณีศึกษาที่ 4: ข้อ 4 (Binary Search Tree) รหัสตัวอย่าง DS-104 [คะแนนเต็ม โครงสร้างถูกต้องครบ 12 โหนด]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>จงวาด Binary Search Tree จากชุดข้อมูล 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99 (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบ</th><td>
            <div class="case-img-block">
              <img src="../public/screenshots/case_studies/case4_ds104.jpg" alt="ภาพถ่ายกระดาษคำตอบ DS-104" class="case-img" />
              <div class="caption-sm">ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-104 (ข้อ 4)</div>
            </div>
          </td></tr>
          <tr><th scope="row">ลักษณะคำตอบผู้เรียน</th><td>ภาพถ่ายกระดาษวาดโครงสร้างต้นไม้ค้นหาทวิภาคครบทั้ง 12 โหนดตามลำดับการแทรกข้อมูล เส้นเชื่อมกิ่งและตำแหน่งซ้าย-ขวาถูกต้องชัดเจน</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>โครงสร้าง BST ถูกต้องครบทั้ง 12 โหนดตามคุณสมบัติ โหนดซ้าย &lt; โหนดแม่ &lt; โหนดขวา ได้ 1.00 คะแนน ผิดตำแหน่งหรือผิดหลักการได้ 0.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>1.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>1.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ได้ 1.00 คะแนน เนื่องจากโครงสร้าง Binary Search Tree ถูกต้องครบทั้ง 12 โหนดตามลำดับข้อมูลที่กำหนด: รากคือ 9 มี 5 เป็นกิ่งซ้ายและ 16 เป็นกิ่งขวา; ใต้ 16 มี 10 ทางซ้ายและ 76 ทางขวา; ใต้ 10 มี 13 ทางขวา โดย 13 มี 11 ทางซ้ายและ 15 ทางขวา; ใต้ 76 มี 58 ทางซ้ายและ 92 ทางขวา โดย 92 มี 80 ทางซ้ายและ 99 ทางขวา ทุกโหนดเป็นไปตามเงื่อนไขค่ากิ่งซ้ายน้อยกว่าและกิ่งขวามากกว่าโหนดแม่ ภาพโดยรวมชัดเจนเพียงพอสำหรับการตรวจสอบ</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>วาด BST ได้ถูกต้องครบถ้วน ทั้งตำแหน่งของโหนดและความสัมพันธ์ของกิ่งซ้าย-ขวาเป็นไปตามหลักการ BST วางตำแหน่งกิ่งซ้าย-ขวาได้ถูกต้องตามลำดับการแทรกข้อมูล</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.11 กรณีศึกษาที่ 5: ข้อ 5 (Infix to Prefix & Postfix) รหัสตัวอย่าง DS-154 [คะแนนบางส่วน Prefix ถูก Postfix ผิด]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>จงแสดงวิธีทำในการแปลง Infix Expression: A + (B * (C - (D / (F * 2)))) เป็น Prefix และ Postfix (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบ</th><td>
            <div class="case-img-block">
              <img src="../public/screenshots/case_studies/case5_ds154.jpg" alt="ภาพถ่ายกระดาษคำตอบ DS-154" class="case-img" />
              <div class="caption-sm">ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-154 (ข้อ 5)</div>
            </div>
          </td></tr>
          <tr><th scope="row">ลักษณะคำตอบผู้เรียน</th><td>ภาพถ่ายกระดาษแสดงวิธีทำ โดยส่วน Prefix ได้คำตอบสุดท้าย +A*B-C/D*F2 แต่ส่วน Postfix เขียนตัวดำเนินการไว้กึ่งกลางเป็น A+B*C-D/F2*</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>แยกประเมิน Prefix (0.50 คะแนน) และ Postfix (0.50 คะแนน) โดยต้องมีขั้นตอนวิธีทำและคำตอบสุดท้ายถูกต้อง</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์ในระดับคะแนนบางส่วน)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ประเมินได้ 0.50 คะแนนจาก 1.00 คะแนน โดยส่วน Prefix ได้ 0.50 คะแนน: คำตอบสุดท้ายที่เขียนเป็น +A*B-C/D*F2 ตรงกับเฉลย และขั้นตอนย่อยที่แสดงสอดคล้องกับการแปลง Prefix ส่วน Postfix ได้ 0.00 คะแนน: แม้ขั้นตอนแรก F2* จะถูกต้อง แต่คำตอบสุดท้ายที่เขียนเป็น A+B*C-D/F2* ไม่ใช่ Postfix ที่ถูกต้องและลำดับตัวดำเนินการไม่เป็นไปตามหลัก Postfix</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ส่วน Prefix ทำได้ถูกต้องและได้คำตอบตรงตามเฉลยแล้ว ควรทบทวน Postfix โดยเมื่อแปลงแต่ละนิพจน์ย่อย ให้เขียนตัวถูกดำเนินการก่อน แล้วจึงวางตัวดำเนินการไว้ท้ายสุด เช่น (F*2) เป็น F2* อย่าเขียนเครื่องหมาย +, *, -, / ไว้ระหว่างตัวแปรเหมือน Infix</td></tr>
        </tbody></table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.12 กรณีศึกษาที่ 6: ข้อ 6 (General Tree to Binary Tree) รหัสตัวอย่าง DS-171 [คะแนนศูนย์ ผิดหลักการทางทฤษฎี]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">โจทย์</th><td>จงแปลง General Tree 10 โหนด ให้เป็น Binary Tree ด้วยหลักการ Left-Child Right-Sibling (LCRS) (คะแนนเต็ม 1.00 คะแนน)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบ</th><td>
            <div class="case-img-block">
              <img src="../public/screenshots/case_studies/case6_ds171.jpg" alt="ภาพถ่ายกระดาษคำตอบ DS-171" class="case-img" />
              <div class="caption-sm">ภาพประกอบ: ภาพถ่ายกระดาษคำตอบลายมือจริงของนิสิต รหัส DS-171 (ข้อ 6)</div>
            </div>
          </td></tr>
          <tr><th scope="row">ลักษณะคำตอบผู้เรียน</th><td>ภาพถ่ายแสดงการวาดต้นไม้ 10 โหนด แต่ไม่ได้แปลงตามหลัก LCRS โดยเชื่อมโหนด 1 ไปยัง 2, 3, 4 โดยตรงในลักษณะ General Tree ดั้งเดิม</td></tr>
          <tr><th scope="row">เกณฑ์โดยสรุป</th><td>แปลงตามหลัก LCRS ถูกต้องครบ 10 โหนดได้ 1.00 คะแนน โครงสร้างแตกกิ่งผิด หรือไม่แปลงได้ 0.00 คะแนน (ระดับคะแนน 1.00 หรือ 0.00 เท่านั้น)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ</th><td>0.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.00 คะแนน (ตรงกันสมบูรณ์ในการตรวจพบข้อผิดพลาดเชิงโครงสร้าง)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>นักเรียนวาดโครงสร้างแบบ General Tree เดิม ไม่ใช่ Binary Tree ตามหลัก Left-Child Right-Sibling (LCRS): โหนด 1 ถูกเชื่อมกับ 2, 3 และ 4 โดยตรง ทั้งที่ในการแปลง LCRS ต้องให้ 1 มีลูกซ้ายเป็น 2 และให้ 2 มีกิ่งขวาเป็น 3 ต่อด้วย 4 และแตกกิ่งแบบ General Tree อย่างมีนัยสำคัญ ตาม rubric ได้ 0.00 คะแนน</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>คำตอบยังเป็นต้นไม้เดิมที่มีลูกหลายตัว จึงยังไม่ใช่ Binary Tree แบบ LCRS ให้จำหลักว่า กิ่งซ้ายแทนลูกคนแรก (First Child) และกิ่งขวาแทนพี่น้องถัดไป (Next Sibling): แต่ละโหนดมีลูกซ้ายและขวาได้ไม่เกินอย่างละหนึ่งกิ่ง</td></tr>
        </tbody></table>
      </div>
    </section>"""

content, count = old_section_pattern.subn(new_section, content)
print(f"Replaced 4.1.6 section: {count} occurrence(s)")

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully updated {html_file}")
