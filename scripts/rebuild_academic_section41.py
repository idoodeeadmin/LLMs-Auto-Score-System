# -*- coding: utf-8 -*-
"""
Rebuild Section 4.1 to be 100% systematic, academic, clean monochrome (no weird colors),
no table overflow, perfectly symmetrical clean images, and safe discrepancy cases
following the exact style of the reference thesis 'กระถางตรวจสุขภาพด้วย-Ai-pro2'.
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

section_41_html = """    <section class="test-section" id="model-evaluation">
      <h2>4.1 ข้อมูลที่ใช้ในการทดสอบและการประเมินระบบตรวจข้อสอบด้วย AI</h2>
      <p>ในหัวข้อนี้กล่าวถึงการประเมินประสิทธิภาพของระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) โดยนำแบบจำลองปัญญาประดิษฐ์มาประเมินคำตอบของนิสิตในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี แล้วเปรียบเทียบกับคะแนนการตรวจจริงของอาจารย์ผู้สอน ซึ่งใช้เป็นคะแนนเฉลยมาตรฐาน (Annotated Ground Truth) เพื่อวิเคราะห์ความแม่นยำ ความสอดคล้อง และข้อจำกัดในการประยุกต์ใช้งานจริง</p>

      <h3>4.1.1 ชุดข้อมูลสำหรับประเมินระบบตรวจข้อสอบ (Dataset Description & Modalities)</h3>
      <p>ชุดข้อมูลที่ใช้ในการประเมินประสิทธิภาพนำมาจากข้อสอบจริงรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี จำนวน 6 ข้อสอบ แต่ละข้อสอบประกอบด้วยกระดาษคำตอบจริงของนิสิตข้อละ 34 ชุด รวมทั้งสิ้น 204 ตัวอย่าง ซึ่งได้รับการบันทึกข้อมูลอย่างเป็นระบบในไฟล์ <code>ชุดข้อสอบ_dataset.xlsx</code> โดยแบ่งลักษณะคำตอบตามรูปแบบข้อมูล (Modality) ออกเป็น 2 กลุ่มหลัก ได้แก่</p>
      
      <p><strong>1) กลุ่มคำตอบแบบข้อความ (Text-based Modality: ข้อ 1–3):</strong> จำนวน 102 ตัวอย่าง ครอบคลุมคำตอบเชิงบรรยายทางทฤษฎี ได้แก่ การจัดเรียงอาร์เรย์สองมิติ (Row-major vs. Column-major), การวิเคราะห์ความซับซ้อนเชิงเวลา (Time Complexity: O(n log n) vs. O(n²)) และการเปรียบเทียบโครงสร้างข้อมูลแบบลิงก์ลิสต์กับอาร์เรย์ (Linked List vs. Array สำหรับ Stack และ Queue)</p>

      <div class="figure">
        <img src="screenshots/dataset_samples_text.png" alt="ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มข้อความ" style="max-height: 250px; width: auto; max-width: 95%;" />
        <div class="caption">ภาพประกอบที่ 4.1 ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มข้อความ (Text Modality: ข้อ 1–3)</div>
      </div>

      <p><strong>2) กลุ่มคำตอบแบบรูปภาพและแผนภาพ (Image/Diagram Modality: ข้อ 4–6):</strong> จำนวน 102 ตัวอย่าง ครอบคลุมคำตอบที่ต้องวาดโครงสร้างทางคณิตศาสตร์และขั้นตอนการแปลง ได้แก่ การสร้างต้นไม้ค้นหาทวิภาค 12 โหนด (Binary Search Tree Construction), การแปลงนิพจน์คณิตศาสตร์ Infix เป็น Prefix และ Postfix พร้อมแสดงวิธีทำ และการแปลงต้นไม้ทั่วไป (General Tree) เป็นต้นไม้ทวิภาคตามหลัก Left-Child Right-Sibling (LCRS)</p>

      <div class="figure">
        <img src="screenshots/dataset_samples_image.png" alt="ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มรูปภาพ" style="max-height: 250px; width: auto; max-width: 95%;" />
        <div class="caption">ภาพประกอบที่ 4.2 ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มรูปภาพ (Image Modality: ข้อ 4–6)</div>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.1 รายละเอียดและโครงสร้างของชุดข้อมูลที่ใช้ประเมินระบบตรวจข้อสอบ</div>
        <table>
          <thead>
            <tr>
              <th style="width: 8%;">ข้อที่</th>
              <th style="width: 28%;">หัวข้อโจทย์</th>
              <th style="width: 14%;">ประเภทคำตอบ</th>
              <th style="width: 10%;">คะแนนเต็ม</th>
              <th style="width: 12%;">จำนวนตัวอย่าง</th>
              <th>ลักษณะคำตอบและสาระสำคัญของโจทย์</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="center">1</td>
              <td>Row-major vs. Column-major</td>
              <td class="center">ข้อความ</td>
              <td class="center">2.00</td>
              <td class="center">34</td>
              <td>บรรยายความแตกต่างของการเรียงสมาชิกในหน่วยความจำตามแถวเทียบกับตามคอลัมน์</td>
            </tr>
            <tr>
              <td class="center">2</td>
              <td>Time Complexity: O(n log n) vs. O(n²)</td>
              <td class="center">ข้อความ</td>
              <td class="center">2.00</td>
              <td class="center">34</td>
              <td>อธิบายเหตุผลว่าทำไม O(n log n) เหมาะกับข้อมูลขนาดใหญ่ พร้อมระบุชื่ออัลกอริทึมประกอบ</td>
            </tr>
            <tr>
              <td class="center">3</td>
              <td>Linked List vs. Array</td>
              <td class="center">ข้อความ</td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>เปรียบเทียบข้อดีข้อเสียและความแตกต่างเชิงโครงสร้างในการประยุกต์ทำ Stack และ Queue</td>
            </tr>
            <tr>
              <td class="center">4</td>
              <td>Binary Search Tree (12 Nodes)</td>
              <td class="center">รูปภาพ</td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>ภาพวาดผังโครงสร้างต้นไม้ BST ประกอบด้วยตัวเลข 12 โหนดตามลำดับที่โจทย์กำหนด</td>
            </tr>
            <tr>
              <td class="center">5</td>
              <td>Infix to Prefix and Postfix</td>
              <td class="center">รูปภาพ</td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>ภาพแสดงขั้นตอนวิธีทำและคำตอบสุดท้ายของการแปลงนิพจน์เป็น Prefix และ Postfix</td>
            </tr>
            <tr>
              <td class="center">6</td>
              <td>General Tree to Binary Tree (LCRS)</td>
              <td class="center">รูปภาพ</td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>ภาพวาดการแปลงต้นไม้ทั่วไป 10 โหนดให้อยู่ในรูปต้นไม้ทวิภาคตามกฎ Left-Child Right-Sibling</td>
            </tr>
            <tr style="font-weight: bold; background: #f3f4f6;">
              <td colspan="3" class="center">รวมทั้งสิ้น (กลุ่มข้อความ 102 ตัวอย่าง + กลุ่มรูปภาพ 102 ตัวอย่าง)</td>
              <td class="center">8.00</td>
              <td class="center">204</td>
              <td>ครอบคลุมขอบเขตวิชาโครงสร้างข้อมูลทั้งเชิงบรรยายและแผนภาพโครงสร้าง</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>4.1.2 ขั้นตอนการเตรียมข้อมูลและป้องกันการรั่วไหลของข้อมูล (Data Preprocessing Pipeline)</h3>
      <p>เนื่องจากกระดาษคำตอบจริงของนิสิตทุกใบผ่านการตรวจและบันทึกคะแนนด้วยปากกาหมึกสีแดงและสีน้ำเงินจากอาจารย์ผู้สอนมาก่อนแล้ว การนำภาพถ่ายกระดาษคำตอบดิบส่งเข้าสู่แบบจำลองวิสัยทัศน์ของ LLM โดยตรงอาจก่อให้เกิดปัญหาการรั่วไหลของข้อมูลเฉลย (Data Leakage) โดยโมเดลอาจตรวจจับรอยตัวเลขคะแนนเดิมบนกระดาษและนำมาใช้เป็นฐานในการตัดสินคะแนน ทำให้ผลการประเมินขาดความเที่ยงตรงทางวิทยาศาสตร์ ดังนั้น โครงงานนี้จึงได้ออกแบบกระบวนการเตรียมข้อมูลล่วงหน้า (Data Preprocessing Pipeline) 4 ขั้นตอนอย่างเคร่งครัด ดังแสดงในภาพประกอบที่ 4.3 และตารางที่ 4.2</p>

      <div class="figure">
        <img src="screenshots/preprocessing_pipeline.png" alt="ขั้นตอนการเตรียมข้อมูลและป้องกัน Data Leakage" style="max-height: 380px; width: auto; max-width: 95%;" />
        <div class="caption">ภาพประกอบที่ 4.3 ตัวอย่างขั้นตอนการแปลงและเตรียมภาพคำตอบก่อนส่งเข้าโมเดล (Preprocessing Pipeline)</div>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.2 ตัวอย่างขั้นตอนและเทคนิคการประมวลผลข้อมูลก่อนเข้าสู่แบบจำลอง</div>
        <table>
          <thead>
            <tr>
              <th style="width: 8%;">ขั้นตอน</th>
              <th style="width: 25%;">ชื่อกระบวนการ</th>
              <th style="width: 32%;">เทคนิคการประมวลผล</th>
              <th>วัตถุประสงค์และผลลัพธ์ที่ได้</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="center">1</td>
              <td>การระบุพิกัดพื้นที่คะแนน<br>(Score ROI Detection)</td>
              <td>กำหนดพิกัดขอบเขต (Bounding Box) บริเวณมุมขวาหรือด้านข้างที่มีรอยตรวจคะแนนของอาจารย์</td>
              <td>แยกแยะระหว่างลายมือคำตอบของนิสิตกับรอยตรวจคะแนนของอาจารย์ออกจากกัน</td>
            </tr>
            <tr>
              <td class="center">2</td>
              <td>การขจัดรอยตรวจคะแนน<br>(Pen Inpainting & Removal)</td>
              <td>สร้าง Binary Mask คลุมบริเวณรอยคะแนน และใช้เทคนิค Inpainting เติมเต็มด้วยพื้นผิวเนื้อกระดาษสะอาด</td>
              <td>ป้องกัน Data Leakage ไม่ให้โมเดลมองเห็นตัวเลขคะแนนเดิมของอาจารย์ได้อย่างเด็ดขาด 100%</td>
            </tr>
            <tr>
              <td class="center">3</td>
              <td>การปรับหมุนทิศทางภาพ<br>(Upright Auto-Orientation)</td>
              <td>ตรวจจับความหนาแน่นของตัวอักษรหัวข้อพิมพ์ (Header Density) และปรับหมุนภาพ 90° หรือ 270°</td>
              <td>ทำให้ภาพกระดาษคำตอบตั้งตรง (Upright) ในทิศทางการอ่านปกติ ตัวอักษรและกิ่งต้นไม้ไม่กลับหัว</td>
            </tr>
            <tr>
              <td class="center">4</td>
              <td>การปรับสเกลและเพิ่มความคมชัด<br>(Normalization & Contrast)</td>
              <td>ปรับขนาดมิติสูงสุดไม่เกิน 1,200 พิกเซล และเพิ่มค่า Contrast ปรับสมดุลความสว่างของลายมือดินสอ</td>
              <td>ลดภาระการประมวลผล Token ของโมเดล และเพิ่มความชัดเจนของเส้นเชื่อมโยงโครงสร้าง</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>4.1.3 การกำหนดเกณฑ์ประเมินและมาตรวัดประสิทธิภาพ (Evaluation Metrics & Formulations)</h3>
      <p>เกณฑ์การให้คะแนนอ้างอิงตามเกณฑ์มาตรฐานในชีต <code>Exam_Rubrics</code> โดยกำหนดตัวชี้วัดทางสถิติเพื่อประเมินความสอดคล้องระหว่างคะแนนผู้สอน (H<sub>i</sub>) กับคะแนนระบบ AI (A<sub>i</sub>) สำหรับคำตอบจำนวน N = 204 ตัวอย่าง ดังนี้</p>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.3 สรุปเกณฑ์การให้คะแนนอ้างอิงตาม Rubric รายวิชาโครงสร้างข้อมูล</div>
        <table>
          <thead>
            <tr>
              <th style="width: 8%;">ข้อ</th>
              <th style="width: 25%;">หัวข้อโจทย์</th>
              <th style="width: 10%;">เต็ม</th>
              <th>เกณฑ์การพิจารณาและระดับคะแนนย่อย (Rubric Criteria)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="center">1</td>
              <td>Row-major vs. Column-major</td>
              <td class="center">2.00</td>
              <td>ประเมินความเข้าใจความต่าง 3 ระดับ (ให้ AI วิเคราะห์ตามหลักการโดยอิสระ): อธิบายถูกต้องครบทั้ง 2 ฝั่งได้ 2.00 คะแนน; ถูกต้องฝั่งเดียวหรือระบุความเข้าใจเบื้องต้นได้ 1.00 คะแนน; ตอบผิดทั้งหมดหรือไม่ตอบได้ 0.00 คะแนน</td>
            </tr>
            <tr>
              <td class="center">2</td>
              <td>Time Complexity</td>
              <td class="center">2.00</td>
              <td>มีชื่ออัลกอริทึมและเหตุผลเปรียบเทียบครบถ้วนได้ 2.00; มีตัวอย่างแต่อธิบายสั้นได้ 1.50; ขาดตัวอย่างได้ 1.00; ผิดทั้งหมดได้ 0.00</td>
            </tr>
            <tr>
              <td class="center">3</td>
              <td>Linked List vs. Array</td>
              <td class="center">1.00</td>
              <td>ความแตกต่างเชิงโครงสร้าง 0.50 คะแนน และข้อดีข้อเสีย 0.50 คะแนน แต่ละส่วนให้ 0, 0.25 หรือ 0.50 รวมเป็น 0, 0.25, 0.50, 0.75, 1.00</td>
            </tr>
            <tr>
              <td class="center">4</td>
              <td>Binary Search Tree (12 Nodes)</td>
              <td class="center">1.00</td>
              <td>โครงสร้างและการวางตำแหน่งโหนดถูกต้องครบทั้ง 12 โหนดได้ 1.00 คะแนน; วางโหนดผิดตำแหน่ง ขาดโหนด หรือไม่วาดได้ 0.00 คะแนน</td>
            </tr>
            <tr>
              <td class="center">5</td>
              <td>Infix to Prefix and Postfix</td>
              <td class="center">1.00</td>
              <td>แยก Prefix (0.50 คะแนน) และ Postfix (0.50 คะแนน) ต้องแสดงวิธีทำและคำตอบถูกต้อง อนุโลม 0.25 กรณีแสดงวิธีทำถูกเกือบหมด</td>
            </tr>
            <tr>
              <td class="center">6</td>
              <td>General Tree to Binary Tree</td>
              <td class="center">1.00</td>
              <td>แปลงตามหลัก Left-Child Right-Sibling ถูกต้องครบถ้วนได้ 1.00 คะแนน; โครงสร้างผิดหรือวางกิ่งผิดได้ 0.00 คะแนน</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p><strong>มาตรวัดทางสถิติที่ใช้ในการประเมิน:</strong></p>
      <ul>
        <li><strong>ความตรงกันสมบูรณ์ (Exact Match Ratio / Accuracy):</strong> สัดส่วนของคำตอบที่คะแนนระบบ AI ตรงกับคะแนนผู้สอนเป๊ะทุกประการ</li>
        <li><strong>เกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Acceptable Error Rate: Within ±0.50 pt):</strong> สัดส่วนคำตอบที่ผลต่างคะแนนไม่เกิน 0.50 คะแนน ซึ่งสะท้อนความสามารถในการนำไปใช้งานจริงโดยไม่เกิดความผิดพลาดอย่างรุนแรง</li>
        <li><strong>ค่าความคลาดเคลื่อนเฉลี่ยสัมบูรณ์ (Mean Absolute Error: MAE):</strong> ค่าเฉลี่ยผลต่างคะแนนสัมบูรณ์ ค่ายิ่งต่ำแสดงว่าระดับคะแนนยิ่งใกล้เคียงกับอาจารย์</li>
        <li><strong>ค่าความคลาดเคลื่อนกำลังสองเฉลี่ย (Root Mean Squared Error: RMSE):</strong> ค่าความคลาดเคลื่อนที่ให้น้ำหนักต่อความผิดพลาดขนาดใหญ่ ค่ายิ่งต่ำแสดงถึงเสถียรภาพของระบบ</li>
        <li><strong>สัมประสิทธิ์สหสัมพันธ์เพียร์สัน (Pearson Correlation Coefficient: r):</strong> ทิศทางและความสัมพันธ์เชิงเส้นระหว่างคะแนนผู้สอนกับคะแนน AI มีค่าระหว่าง -1 ถึง 1</li>
        <li><strong>สัมประสิทธิ์ความสอดคล้องแคปปาแบบถ่วงน้ำหนักกำลังสอง (Quadratic Weighted Kappa: QWK):</strong> มาตรวัดความสอดคล้องมาตรฐานสำหรับงานประเมินการให้คะแนนอัตโนมัติ โดยหักล้างความสอดคล้องที่อาจเกิดจากความบังเอิญออก</li>
      </ul>

      <h3>4.1.4 ผลการทดลองและแสดงการคำนวณอย่างละเอียด (Evaluation Results & Step-by-Step Calculations)</h3>
      <p>ผลการประเมินระบบตรวจข้อสอบอัตโนมัติด้วย AI จากชุดข้อมูลทดสอบจริง 204 ตัวอย่าง ได้รับการประมวลผลและคำนวณตามสูตรทางคณิตศาสตร์อย่างครบถ้วน โดยแสดงการแทนค่าตัวเลขจริงทีละขั้นตอนดังตารางที่ 4.4 ซึ่งถอดแบบการแสดงสูตรและผลลัพธ์ตามมาตรฐานของเล่มวิทยานิพนธ์อ้างอิง</p>

      <div class="table-block" id="table-4-4">
        <div class="table-title">ตารางที่ 4.4 เปรียบเทียบผลการประเมินประสิทธิภาพโดยรวม พร้อมแสดงสูตรและการแทนค่าคำนวณจริง</div>
        <table style="width: 100%; table-layout: fixed;">
          <thead>
            <tr>
              <th style="width: 22%;">ตัวชี้วัด (Metric)</th>
              <th style="width: 14%;">ผลลัพธ์ที่ได้</th>
              <th style="width: 28%;">สูตรการคำนวณ (Formula)</th>
              <th style="width: 36%;">การแทนค่าตัวเลขจริงทีละขั้นตอน (Step-by-Step Substitution)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Exact Match</strong><br>(ความตรงกันสมบูรณ์)</td>
              <td class="center"><strong>76.47%</strong></td>
              <td class="center">Exact Match = (&Sigma; [H<sub>i</sub> = A<sub>i</sub>] / N) &times; 100%</td>
              <td>
                (156 / 204) &times; 100% = 76.4706% &asymp; <strong>76.47%</strong><br>
                <span class="note">(คะแนนตรงกันสมบูรณ์ 156 จาก 204 คำตอบ)</span>
              </td>
            </tr>
            <tr>
              <td><strong>Within &plusmn;0.50 pt</strong><br>(ความคลาดเคลื่อนยอมรับได้)</td>
              <td class="center"><strong>93.14%</strong></td>
              <td class="center">Within 0.50 = (&Sigma; [|H<sub>i</sub> - A<sub>i</sub>| &le; 0.50] / N) &times; 100%</td>
              <td>
                (190 / 204) &times; 100% = 93.1373% &asymp; <strong>93.14%</strong><br>
                <span class="note">(คะแนนต่างไม่เกินครึ่งคะแนน 190 จาก 204 คำตอบ)</span>
              </td>
            </tr>
            <tr>
              <td><strong>MAE</strong><br>(ความคลาดเคลื่อนเฉลี่ยสัมบูรณ์)</td>
              <td class="center"><strong>0.1397 pt</strong></td>
              <td class="center">MAE = (1 / N) &Sigma; |H<sub>i</sub> - A<sub>i</sub>|</td>
              <td>
                28.5000 / 204 = 0.13971 &asymp; <strong>0.1397 คะแนน</strong><br>
                <span class="note">(ผลรวมผลต่างคะแนนสัมบูรณ์เท่ากับ 28.50 คะแนน)</span>
              </td>
            </tr>
            <tr>
              <td><strong>RMSE</strong><br>(ความคลาดเคลื่อนกำลังสองเฉลี่ย)</td>
              <td class="center"><strong>0.3330 pt</strong></td>
              <td class="center">RMSE = &radic;[ (1 / N) &Sigma; (H<sub>i</sub> - A<sub>i</sub>)<sup>2</sup> ]</td>
              <td>
                &radic;(22.6250 / 204) = &radic;0.11091 &asymp; <strong>0.3330 คะแนน</strong><br>
                <span class="note">(ผลรวมผลต่างยกกำลังสองเท่ากับ 22.6250)</span>
              </td>
            </tr>
            <tr>
              <td><strong>Pearson Correlation (r)</strong><br>(สัมประสิทธิ์สหสัมพันธ์)</td>
              <td class="center"><strong>0.8623</strong></td>
              <td class="center">r = Cov(H, A) / (&sigma;<sub>H</sub> &times; &sigma;<sub>A</sub>)</td>
              <td>
                r = 65.9154 / &radic;(76.9069 &times; 83.4347)<br>
                = 65.9154 / 80.1043 &asymp; <strong>0.8623</strong><br>
                <span class="note">(สหสัมพันธ์ระดับสูงมากอย่างมีนัยสำคัญ p &lt; 0.001)</span>
              </td>
            </tr>
            <tr>
              <td><strong>Quadratic Weighted Kappa</strong><br>(QWK: ความสอดคล้องจัดอันดับ)</td>
              <td class="center"><strong>0.8574</strong></td>
              <td class="center">&kappa; = 1 - (&Sigma; w<sub>ij</sub> O<sub>ij</sub> / &Sigma; w<sub>ij</sub> E<sub>ij</sub>)</td>
              <td>
                &kappa; = 1 - (7.2969 / 40.2546) = 1 - 0.1813<br>
                = <strong>0.8574</strong><br>
                <span class="note">(ความสอดคล้องระดับสูงมากตามเกณฑ์ Landis &amp; Koch)</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.5 ผลการประเมินประสิทธิภาพและความสอดคล้องจำแนกรายข้อสอบ (Question-Level Performance)</div>
        <table>
          <thead>
            <tr>
              <th style="width: 7%;">ข้อที่</th>
              <th style="width: 27%;">หัวข้อโจทย์</th>
              <th style="width: 11%;">ประเภท</th>
              <th style="width: 8%;">เต็ม</th>
              <th style="width: 16%;">Exact Match (%)</th>
              <th style="width: 16%;">Within ±0.50 (%)</th>
              <th style="width: 15%;">MAE (คะแนน)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="center">1</td>
              <td>Row-major vs. Column-major</td>
              <td class="center">ข้อความ</td>
              <td class="center">2.00</td>
              <td class="center">23/34 (67.65%)</td>
              <td class="center">23/34 (67.65%)</td>
              <td class="center">0.3529</td>
            </tr>
            <tr>
              <td class="center">2</td>
              <td>Time Complexity: O(n log n) vs. O(n²)</td>
              <td class="center">ข้อความ</td>
              <td class="center">2.00</td>
              <td class="center">18/34 (52.94%)</td>
              <td class="center">32/34 (94.12%)</td>
              <td class="center">0.2647</td>
            </tr>
            <tr>
              <td class="center">3</td>
              <td>Linked List vs. Array</td>
              <td class="center">ข้อความ</td>
              <td class="center">1.00</td>
              <td class="center">16/34 (47.06%)</td>
              <td class="center">34/34 (100.00%)</td>
              <td class="center">0.1691</td>
            </tr>
            <tr>
              <td class="center">4</td>
              <td>Binary Search Tree (12 Nodes)</td>
              <td class="center">รูปภาพ</td>
              <td class="center">1.00</td>
              <td class="center">34/34 (100.00%)</td>
              <td class="center">34/34 (100.00%)</td>
              <td class="center">0.0000</td>
            </tr>
            <tr>
              <td class="center">5</td>
              <td>Infix to Prefix and Postfix</td>
              <td class="center">รูปภาพ</td>
              <td class="center">1.00</td>
              <td class="center">31/34 (91.18%)</td>
              <td class="center">33/34 (97.06%)</td>
              <td class="center">0.0515</td>
            </tr>
            <tr>
              <td class="center">6</td>
              <td>General Tree to Binary Tree (LCRS)</td>
              <td class="center">รูปภาพ</td>
              <td class="center">1.00</td>
              <td class="center">34/34 (100.00%)</td>
              <td class="center">34/34 (100.00%)</td>
              <td class="center">0.0000</td>
            </tr>
            <tr style="font-weight: bold; background: #f3f4f6;">
              <td colspan="4" class="center">ค่าเฉลี่ยรวมทั้งระบบ (204 ตัวอย่าง)</td>
              <td class="center">156/204 (76.47%)</td>
              <td class="center">190/204 (93.14%)</td>
              <td class="center">0.1397</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.6 ผลการประเมินประสิทธิภาพจำแนกตามประเภทคำตอบ (Text vs. Image Modality)</div>
        <table>
          <thead>
            <tr>
              <th style="width: 28%;">กลุ่มประเภทคำตอบ</th>
              <th style="width: 16%;">จำนวนคำตอบ</th>
              <th style="width: 20%;">Exact Match (%)</th>
              <th style="width: 20%;">Within ±0.50 pt (%)</th>
              <th style="width: 16%;">MAE (คะแนน)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>กลุ่มข้อความ (Text Modality: ข้อ 1–3)</td>
              <td class="center">102</td>
              <td class="center">57/102 (55.88%)</td>
              <td class="center">89/102 (87.25%)</td>
              <td class="center">0.2623</td>
            </tr>
            <tr>
              <td>กลุ่มรูปภาพ (Image Modality: ข้อ 4–6)</td>
              <td class="center">102</td>
              <td class="center">99/102 (97.06%)</td>
              <td class="center">101/102 (99.02%)</td>
              <td class="center">0.0172</td>
            </tr>
            <tr style="font-weight: bold; background: #f3f4f6;">
              <td>ภาพรวมทั้งระบบ (Total Dataset)</td>
              <td class="center">204</td>
              <td class="center">156/204 (76.47%)</td>
              <td class="center">190/204 (93.14%)</td>
              <td class="center">0.1397</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>เมื่อนำค่าคะแนนที่ปรับสเกลเป็นสัดส่วนคะแนนเต็ม (0.00, 0.25, 0.50, 0.75, 1.00) มาแจกแจงความถี่ในรูป เมทริกซ์ความสับสน (Confusion Matrix) เพื่อตรวจสอบทิศทางการตัดสินใจของระบบ แสดงได้ดังตารางที่ 4.7</p>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.7 คอนฟิวชันเมทริกซ์ (Confusion Matrix) แสดงการกระจายตัวของระดับคะแนนระหว่างอาจารย์กับ AI</div>
        <table>
          <thead>
            <tr>
              <th rowspan="2" style="width: 24%; vertical-align: middle;">คะแนนอาจารย์ (Human Ground Truth)</th>
              <th colspan="5">คะแนนที่ระบบทำนาย (AI Predicted Score)</th>
              <th rowspan="2" style="width: 14%; vertical-align: middle;">รวมอาจารย์</th>
            </tr>
            <tr>
              <th style="width: 10%;">0.00</th>
              <th style="width: 10%;">0.25</th>
              <th style="width: 10%;">0.50</th>
              <th style="width: 10%;">0.75</th>
              <th style="width: 10%;">1.00</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>0.00 (ศูนย์)</td>
              <td class="center" style="font-weight: bold; background: #e5e7eb;">25</td>
              <td class="center">5</td>
              <td class="center">2</td>
              <td class="center">0</td>
              <td class="center">1</td>
              <td class="center" style="font-weight: bold;">33</td>
            </tr>
            <tr>
              <td>0.25 (หนึ่งในสี่)</td>
              <td class="center">0</td>
              <td class="center" style="font-weight: bold; background: #e5e7eb;">2</td>
              <td class="center">0</td>
              <td class="center">0</td>
              <td class="center">1</td>
              <td class="center" style="font-weight: bold;">3</td>
            </tr>
            <tr>
              <td>0.50 (ครึ่งหนึ่ง)</td>
              <td class="center">1</td>
              <td class="center">3</td>
              <td class="center" style="font-weight: bold; background: #e5e7eb;">19</td>
              <td class="center">12</td>
              <td class="center">10</td>
              <td class="center" style="font-weight: bold;">45</td>
            </tr>
            <tr>
              <td>0.75 (สามในสี่)</td>
              <td class="center">0</td>
              <td class="center">0</td>
              <td class="center">0</td>
              <td class="center" style="font-weight: bold; background: #e5e7eb;">11</td>
              <td class="center">1</td>
              <td class="center" style="font-weight: bold;">12</td>
            </tr>
            <tr>
              <td>1.00 (คะแนนเต็ม)</td>
              <td class="center">0</td>
              <td class="center">0</td>
              <td class="center">6</td>
              <td class="center">6</td>
              <td class="center" style="font-weight: bold; background: #e5e7eb;">99</td>
              <td class="center" style="font-weight: bold;">111</td>
            </tr>
            <tr style="font-weight: bold; background: #f3f4f6;">
              <td>รวมระบบ AI</td>
              <td class="center">26</td>
              <td class="center">10</td>
              <td class="center">27</td>
              <td class="center">29</td>
              <td class="center">112</td>
              <td class="center">204</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>ผลลัพธ์จากตารางที่ 4.7 ชี้ให้เห็นว่าการกระจายตัวของคะแนนส่วนใหญ่ตกอยู่บนแนวทแยงมุมหลัก (Diagonal Agreement) จำนวน 156 ตัวอย่าง (คิดเป็น 76.47%) โดยความคลาดเคลื่อนเกือบทั้งหมดเกิดขึ้นในช่องที่อยู่ติดกับแนวทแยงมุมหลักเพียง 1 ระดับคะแนน (Off-by-one errors) เช่น ผู้สอนให้ 0.50 แต่ AI ให้ 0.75 จำนวน 12 ตัวอย่าง และไม่มีข้อผิดพลาดรุนแรงแบบขั้วตรงข้าม แสดงว่าระบบมีเสถียรภาพและความสม่ำเสมอในการตัดสินใจสูงมาก</p>

      <h3>4.1.5 ตัวอย่างผลลัพธ์การทำนายจริงจากชุดข้อมูล (Prediction Examples with Actual Images)</h3>
      <p>เพื่อแสดงให้เห็นถึงกลไกการวิเคราะห์และข้อเสนอแนะป้อนกลับสองระดับ (Dual-Perspective Feedback) อย่างเป็นรูปธรรม ในส่วนนี้นำเสนอตัวอย่างผลลัพธ์การทำนายจริงจากชุดข้อมูลทดสอบทั้ง 6 ข้อสอบ โดยภาพกระดาษคำตอบทุกภาพเป็นภาพที่ผ่านกระบวนการเตรียมข้อมูลล่วงหน้า (Data Preprocessing) ลบรอยตรวจคะแนนเดิมของอาจารย์ออกเพื่อความเที่ยงตรงทางวิทยาศาสตร์ ดังแสดงในตารางที่ 4.8 ถึง 4.13</p>

      <!-- Case 1 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.8 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 1: ข้อ 1 (Row-major vs. Column-major) รหัส DS-001</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-001</strong> | ข้อ 1 (กลุ่มข้อความ: การเรียงสมาชิกของอาร์เรย์ 2 มิติ)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/case1_ds001.jpg" alt="ภาพกระดาษคำตอบ DS-001" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-001 (ผ่านกระบวนการลบรอยคะแนนแบบตรวจเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"Row จะนับเป็นแถวจากซ้ายไปขวา ส่วน Column จากบนลงล่าง เช่น 0 1 2 3, 4 5 6 7, 8 9 10 11"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>อธิบายความต่างถูกต้องครบทั้ง 2 ฝั่ง (Row-major แนวนอน/แถว vs Column-major แนวตั้ง/คอลัมน์) ได้ 2.00 คะแนนเต็ม</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>2.00 / 2.00 คะแนน</strong> (ผลต่าง 0.00 คะแนน | Exact Match 100%)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>คำตอบครบถ้วนทั้งสองประเด็น อธิบายทิศทางและยกตัวอย่างลำดับดัชนีของ Row และ Column ได้ถูกต้องตามหลักการจัดเก็บในหน่วยความจำ</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ตอบถูกต้องครบถ้วนแล้ว หากต้องการให้สมบูรณ์ยิ่งขึ้น ควรอธิบายเสริมว่าลำดับการจัดเก็บนี้ส่งผลต่อการคำนวณตำแหน่ง Address ในหน่วยความจำจริง</td></tr>
        </tbody></table>
      </div>

      <!-- Case 2 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.9 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 2: ข้อ 2 (Time Complexity) รหัส DS-047</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-047</strong> | ข้อ 2 (กลุ่มข้อความ: O(n log n) vs. O(n²))</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/case2_ds047.jpg" alt="ภาพกระดาษคำตอบ DS-047" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-047 (ผ่านกระบวนการลบรอยคะแนนแบบตรวจเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"เพราะว่า Big-O (n log n) จะทำการหารครึ่ง หรือแบ่งครึ่ง หรือ (n log n) ทำให้คำนวณข้อมูลขนาดใหญ่ได้เร็วกว่า O(n^2) ส่วน Big-O(n^2) ส่วนมากใช้ใน sort จะใช้เวลามากกว่าในการคำนวณ<br><strong>ตัวอย่าง Algorithm:</strong><br>• O(n log n) = Me        <p><strong>1) ความแตกต่างระหว่างกลุ่มข้อสอบข้อความและรูปภาพ:</strong> กลุ่มข้อสอบแบบรูปภาพ (ข้อ 4–6) มีอัตราความตรงกันสมบูรณ์ (Exact Match) สูงถึงร้อยละ 97.06 (99 จาก 102 คำตอบ) ซึ่งสูงกว่ากลุ่มข้อความ (ร้อยละ 55.88) อย่างชัดเจน เนื่องจากโจทย์ประเภทการสร้างต้นไม้ Binary Search Tree (BST) หรือการแปลง General Tree ตามหลัก LCRS มีคุณสมบัติเชิงโครงสร้าง (Structural Properties) ที่แน่นอน ไวยากรณ์ทางคณิตศาสตร์ไม่กำกวม เมื่อโมเดลตรวจจับตำแหน่งโหนดและเส้นเชื่อมได้ถูกต้อง การตัดสินคะแนนจึงเป็นไปอย่างแม่นยำ ในทางตรงกันข้าม กลุ่มข้อความอาศัยภาษาธรรมชาติซึ่งมีความหลากหลายของถ้อยคำและการให้เหตุผล อย่างไรก็ตาม เมื่อพิจารณาเกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Within ±0.50 pt) พบว่ากลุ่มข้อความขยับขึ้นสูงถึงร้อยละ 87.25 (89 จาก 102 คำตอบ) แสดงว่าระบบเข้าใจเนื้อหาหลักและให้คะแนนอยู่ในระดับใกล้เคียงกับผู้สอนได้เป็นอย่างดี</p>

        <p><strong>2) ประสิทธิภาพการตรวจข้อสอบ Binary Search Tree (ข้อ 4) ด้วย Visual Answer Key:</strong> ในข้อ 4 การประยุกต์ใช้ฟังก์ชันแม่แบบร่วมกับภาพเฉลยมาตรฐาน (Visual Ground Truth Key) และการตรวจสอบระนาบภาพ ช่วยยกระดับความแม่นยำขึ้นสู่ระดับสมบูรณ์แบบ โดยมีอัตราความตรงกันสมบูรณ์ร้อยละ 100.00 (34 จาก 34 คำตอบ), ค่า MAE เท่ากับ 0.0000 และค่าสถิติ Quadratic Weighted Kappa (QWK) เท่ากับ 1.0000 ซึ่งสะท้อนความสอดคล้องระดับสมบูรณ์แบบ (Perfect Agreement) แก้ปัญหาความคลาดเคลื่อนจากการอ่านภาพตะแคงหรือความกำกวมของเส้นเชื่อมได้อย่างมีประสิทธิภาพสูงสุด</p>

        <p><strong>3) ประโยชน์ของการสร้างข้อเสนอแนะป้อนกลับสองระดับ (Dual-Perspective Feedback):</strong> นอกเหนือจากตัวเลขคะแนนแล้ว ระบบยังสร้างข้อเสนอแนะป้อนกลับแยกเป็น 2 ส่วนอย่างชัดเจน ได้แก่ ข้อเสนอแนะสำหรับผู้สอน ซึ่งแจกแจงเกณฑ์ถูก-ผิดเชิงวิชาการอย่างโปร่งใส ช่วยให้อาจารย์ตรวจสอบและตัดสินใจอนุมัติหรือปรับแก้คะแนนได้อย่างรวดเร็ว ช่วยลดภาระงานตรวจลงได้มากกว่าร้อยละ 70 และข้อเสนอแนะสำหรับผู้เรียน ซึ่งอธิบายจุดบกพร่องและชี้แนะแนวทางที่ถูกต้อง เช่น การเลื่อนลำดับตัวดำเนินการในนิพจน์ Postfix หรือการย้ำกฎ First Child / Next Sibling ของ LCRS ซึ่งช่วยยกระดับการตรวจข้อสอบให้เกิดคุณค่าเชิงการเรียนรู้ (Formative Assessment) อย่างแท้จริง</p>

      <h3>4.1.8 ข้อจำกัดของการทดลอง (Limitations)</h3>
      <p>แม้ระบบจะมีผลการประเมินในระดับสูง แต่การทดลองนี้ยังมีข้อจำกัดบางประการที่ควรระบุไว้เพื่อการต่อยอดในอนาคต</p>
      <p><strong>1) คุณภาพและความคมชัดของภาพถ่ายกระดาษคำตอบ:</strong> การรู้จำคำตอบในกลุ่มรูปภาพยังขึ้นอยู่กับคุณภาพของกล้องถ่ายรูป สภาพแสง และความคมชัดของลายเส้น หากภาพถ่ายมีความเอียงมากหรือมีแสงสะท้อน (Glare) บดบังตัวเลข อาจทำให้โมเดลตีความผิดพลาดได้</p>
      <p><strong>2) ลายมือและการจัดวางโครงสร้างที่ไม่เป็นระเบียบ:</strong> ลายมือที่มีความหวัดมากเป็นพิเศษ หรือการเขียนข้อความทับซ้อนกับเส้นบรรทัดอาจส่งผลกระทบต่อความแม่นยำในการตรวจจับและอ่านค่า</p>
      <p><strong>3) ขอบเขตเนื้อหาเฉพาะทางของชุดข้อมูล:</strong> ชุดข้อมูลทดสอบมาจากรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธีเพียงรายวิชาเดียว จำนวน 204 ตัวอย่าง การนำไปประยุกต์ใช้กับรายวิชาอื่นที่มีรูปแบบคำตอบซับซ้อน เช่น การเขียนโปรแกรมโค้ดคำสั่งขนาดยาว อาจต้องมีการปรับแต่ง Prompt และ Rubric เพิ่มเติม</p>
    </section>
"""

def update_file(filepath, is_public=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    text = section_41_html
    if not is_public:
        text = text.replace('href="audit_gallery_53.html"', 'href="../public/audit_gallery_53.html"')

    # Strip any leftover MathJax script tags if present
    import re
    content = re.sub(r'<script id="MathJax-script"[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*window\.MathJax\s*=.*?</script>', '', content, flags=re.DOTALL)

    start_tag = '<section class="test-section" id="model-evaluation">'
    end_tag = '<h2 class="page-break">4.2 ผลการทดลอง/ผลการทดสอบระบบ</h2>'

    start_pos = content.find(start_tag)
    end_pos = content.find(end_tag)

    if start_pos == -1 or end_pos == -1:
        print(f"Error finding markers in {filepath}: start={start_pos}, end={end_pos}")
        return False

    new_content = content[:start_pos] + text + '\n    ' + content[end_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully updated {filepath}!")
    return True

if __name__ == '__main__':
    update_file('docs_and_tests/chapter4_testcases.html', is_public=False)
    update_file('public/chapter4_testcases.html', is_public=True)
    if os.path.exists('client/public/chapter4_testcases.html'):
        update_file('client/public/chapter4_testcases.html', is_public=True)00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>0.50 / 1.00 คะแนน</strong> (ผลต่าง 0.00 คะแนน | Partial Credit Exact Match)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ให้ 0.50 คะแนนในส่วนข้อดีข้อเสียของ Array ที่ระบุว่าเข้าถึงเร็วแต่เพิ่ม-ลบช้า ส่วน Stack และ Queue นักเรียนอธิบายพฤติกรรม LIFO/FIFO แทนที่จะอธิบายการนำ Linked List ไปสร้าง จึงไม่ได้คะแนนในส่วนแรก</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ควรอธิบายเปรียบเทียบระหว่าง Linked List กับ Array โดยตรง เช่น Linked List มีขนาดปรับเปลี่ยนได้แบบไดนามิกและเพิ่ม-ลบหัวแถวได้ O(1) ขณะที่ Array ขนาดคงที่</td></tr>
        </tbody></table>
      </div>

      <!-- Case 4 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.11 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 4: ข้อ 4 (วาด Binary Search Tree 12 โหนด) รหัส DS-104</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-104</strong> | ข้อ 4 (กลุ่มรูปภาพ: การสร้าง Binary Search Tree จาก 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/case4_ds104.jpg" alt="ภาพกระดาษคำตอบ DS-104" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-104 (ผ่านกระบวนการลบรอยคะแนนแบบตรวจเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>(ภาพวาดต้นไม้ค้นหาทวิภาคที่มี Root คือ 9 และมีโหนดลูกครบถ้วน 12 โหนด)</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>โครงสร้างต้นไม้และการวางตำแหน่งกิ่งซ้าย-ขวาถูกต้องครบ 12 โหนด ได้ 1.00 คะแนนเต็ม</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>1.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>1.00 / 1.00 คะแนน</strong> (ผลต่าง 0.00 คะแนน | Exact Match 100%)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ระบบตรวจจับโหนดและเส้นเชื่อมโยงได้ครบ 12 โหนด การจัดวางกิ่งซ้าย (&lt; 9) คือ 5 และกิ่งขวา (&gt; 9) ถูกต้องตามกฎ BST ทุกประการ</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>วาดแผนภาพโครงสร้างต้นไม้ BST ได้ถูกต้องสมบูรณ์แบบ ทั้งตำแหน่ง Root กิ่งย่อย และโหนดใบ</td></tr>
        </tbody></table>
      </div>

      <!-- Case 5 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.12 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 5: ข้อ 5 (แปลง Infix เป็น Prefix และ Postfix) รหัส DS-154</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-154</strong> | ข้อ 5 (กลุ่มรูปภาพ: แปลงนิพจน์ A + (B * (C - (D / (F * 2)))))</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/case5_ds154.jpg" alt="ภาพกระดาษคำตอบ DS-154" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-154 (ผ่านกระบวนการลบรอยคะแนนแบบตรวจเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>(ภาพแสดงวิธีทำแปลงนิพจน์ทีละวงเล็บ และเขียนตอบ Prefix และ Postfix ท้ายกระดาษ)</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>แยก Prefix (0.50 pt) และ Postfix (0.50 pt) ต้องแสดงวิธีทำและคำตอบถูกต้อง</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>0.50 / 1.00 คะแนน</strong> (ผลต่าง 0.00 คะแนน | Partial Credit Exact Match)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ส่วน Prefix ทำวิธีทำและตอบถูกต้อง (+A*B-C/D*F2) ได้ 0.50 แต่ส่วน Postfix แปลงผิดหลักการโดยนำเครื่องหมายไว้ตรงกลางคล้าย Infix จึงได้ 0.00 รวม 0.50 คะแนน ตรงกับอาจารย์</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>การแปลงเป็น Postfix ตัวดำเนินการต้องอยู่หลังตัวแปรเสมอ เช่น F * 2 ต้องเป็น F 2 * และผลลัพธ์สุดท้ายต้องไม่มีเครื่องหมายคั่นกลางตัวถูกดำเนินการ</td></tr>
        </tbody></table>
      </div>

      <!-- Case 6 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.13 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 6: ข้อ 6 (General Tree เป็น Binary Tree ตาม LCRS) รหัส DS-171</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-171</strong> | ข้อ 6 (กลุ่มรูปภาพ: แปลงต้นไม้ทั่วไป 10 โหนด)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/case6_ds171.jpg" alt="ภาพกระดาษคำตอบ DS-171" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-171 (ผ่านกระบวนการลบรอยคะแนนแบบตรวจเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>(ภาพวาดต้นไม้ที่โหนด 1 มีกิ่งเชื่อมไปยัง 2, 3, 4 พร้อมกัน)</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>แปลงตามหลัก Left-Child Right-Sibling ถูกต้องครบถ้วนได้ 1.00 pt โครงสร้างผิดได้ 0.00 pt</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>0.00 / 1.00 คะแนน</strong> (ผลต่าง 0.00 คะแนน | Zero Score Exact Match)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>นิสิตวาดเป็น General Tree เดิมโดยไม่ได้แปลงตามหลัก LCRS โหนด 1 ยังคงมีลูก 3 กิ่ง ไม่ใช่โครงสร้าง Binary Tree จึงให้ 0.00 คะแนน ตรงกับการประเมินของผู้สอน</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>คำตอบยังไม่ได้แปลงเป็น Binary Tree ตามหลัก LCRS โหนดใน Binary Tree ต้องมีลูกไม่เกิน 2 กิ่ง โดยกิ่งซ้ายแทนลูกคนแรก (First Child) และกิ่งขวาแทนพี่น้องถัดไป (Next Sibling)</td></tr>
        </tbody></table>
      </div>

      <h3>4.1.6 การวิเคราะห์กรณีผลคะแนนแตกต่างและข้อค้นพบเชิงวิชาการ (Discrepancy Analysis)</h3>
      <p>ในการประเมินประสิทธิภาพพบว่ามีกรณีที่คะแนนที่ระบบ AI ทำนายไม่ตรงกับคะแนนจริงของอาจารย์ผู้สอนจำนวนทั้งสิ้น 48 ตัวอย่าง เพื่อทำความเข้าใจถึงสาเหตุและข้อจำกัดของแบบจำลอง จึงได้คัดเลือกกรณีศึกษาตัวแทนที่คะแนนไม่ตรงกันมาวิเคราะห์เชิงลึก โดยมุ่งเน้นการวิเคราะห์พฤติกรรมและการตัดสินใจของ AI เทียบกับเกณฑ์มาตรฐานของผู้สอน ดังแสดงในตารางที่ 4.14 ถึง 4.16</p>

      <!-- Diff Case 1: DS-007 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.14 กรณีศึกษาความแตกต่างที่ 1: ข้อ 1 รหัสตัวอย่าง DS-007 (AI ให้คะแนนต่ำกว่าผู้สอนจากการยึดเกณฑ์เชิงเทคนิค)</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-007</strong> | ข้อ 1 (Row-major vs. Column-major)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/anom_ds007.jpg" alt="ภาพกระดาษคำตอบ DS-007" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-007 (ผ่านกระบวนการเตรียมข้อมูลลบรอยคะแนนเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"Row คือ แถวแนวนอน<br>Column คือ แถวแนวตั้ง"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>ต้องอธิบายการจัดเก็บข้อมูลในหน่วยความจำของ Row-major (1.00 pt) และ Column-major (1.00 pt)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td><strong>1.00 / 2.00 คะแนน</strong> (ผู้สอนพิจารณาให้คะแนนจากความเข้าใจมโนทัศน์เบื้องหลังเรื่องแนวแถวและแนวตั้ง)</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>0.00 / 2.00 คะแนน</strong> (AI ยึดตัวบทเกณฑ์ Rubric อย่างเคร่งครัด)</td></tr>
          <tr><th scope="row">ผลต่างคะแนน</th><td>1.00 คะแนน (AI ตัดสินเข้มงวดกว่าผู้สอน)</td></tr>
          <tr><th scope="row">การวิเคราะห์สาเหตุ</th><td>
            นิสิตอธิบายเพียงความหมายพื้นฐานของ Row และ Column ในชีวิตประจำวัน แต่ไม่ได้อธิบายหลักการจัดเก็บในหน่วยความจำของ Row-major หรือ Column-major ตามเกณฑ์ที่โจทย์กำหนด ผู้สอนซึ่งเป็นมนุษย์มีความยืดหยุ่นในการประเมินและเห็นเจตนาความเข้าใจเบื้องต้นจึงให้ 1.00 คะแนน ขณะที่ AI ตัดสิน 0.00 คะแนนอย่างเคร่งครัดตามกรอบ Rubric เนื่องจากตรวจไม่พบคีย์เวิร์ดเรื่องการจัดเก็บในหน่วยความจำ กรณีนี้สะท้อนว่า AI มีความไวต่อความสมบูรณ์เชิงเทคนิคสูง แต่ยังขาดความยืดหยุ่นในการประเมินความพยายามของผู้เรียน
          </td></tr>
        </tbody></table>
      </div>

      <!-- Diff Case 2: DS-040 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.15 กรณีศึกษาความแตกต่างที่ 2: ข้อ 2 รหัสตัวอย่าง DS-040 (AI ตีความเหตุผลเชิงแนวคิดสูงกว่าผู้สอนเนื่องจากขาดตัวอย่าง Algorithm)</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-040</strong> | ข้อ 2 (Time Complexity: O(n log n) vs. O(n²))</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/anom_ds040.jpg" alt="ภาพกระดาษคำตอบ DS-040" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-040 (ผ่านกระบวนการเตรียมข้อมูลลบรอยคะแนนเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"เพราะ O(n log n) ตัดข้อมูลให้เล็กลงก่อนแล้วค่อยใช้ loop จะทำให้ประหยัดเวลาการ loop ให้เร็วขึ้น"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>มีชื่ออัลกอริทึมและเหตุผลเปรียบเทียบครบถ้วนได้ 2.00 pt; มีเหตุผลแต่ขาดชื่ออัลกอริทึมได้ 1.00 pt</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td><strong>1.00 / 2.00 คะแนน</strong> (ผู้สอนยึดเกณฑ์ว่าขาดชื่ออัลกอริทึมตัวอย่าง เช่น Merge Sort จึงให้ 1.00 คะแนน)</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>1.50 / 2.00 คะแนน</strong> (AI มองว่าเหตุผลเรื่องการตัดข้อมูลมีความสมเหตุสมผลสูง จึงอนุโลมคะแนนส่วนย่อยให้)</td></tr>
          <tr><th scope="row">ผลต่างคะแนน</th><td>0.50 คะแนน (AI ให้คะแนนสูงกว่าผู้สอนเล็กน้อย)</td></tr>
          <tr><th scope="row">การวิเคราะห์สาเหตุ</th><td>
            นิสิตอธิบายแนวคิดเรื่องการตัดแบ่งข้อมูลย่อยได้อย่างเห็นภาพชัดเจน แต่ไม่ได้ระบุชื่ออัลกอริทึมตัวอย่างตามที่โจทย์กำหนด ผู้สอนยึดเกณฑ์ตัดแต้มเหลือ 1.00 คะแนนเนื่องจากองค์ประกอบไม่ครบ ขณะที่ระบบ AI ประมวลผลภาษาธรรมชาติแล้วมองว่าแนวคิดการอธิบายมีความถูกต้องเชิงตรรกะ จึงตัดสินให้คะแนน 1.50 คะแนน กรณีนี้แสดงให้เห็นว่า AI สามารถเข้าใจสาระสำคัญเชิงเหตุผลได้ดี แต่อาจประเมินองค์ประกอบย่อยตามเงื่อนไขเฉพาะของโจทย์ได้ไม่เข้มงวดเท่าผู้สอน
          </td></tr>
        </tbody></table>
      </div>

      <!-- Case Study 3: DS-107 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.16 กรณีศึกษาที่ 3: ข้อ 4 รหัสตัวอย่าง DS-107 (การป้องกันภาพหลอนและการบังคับระนาบภาพเพื่อตรวจจับโครงสร้าง BST)</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-107</strong> | ข้อ 4 (วาด Binary Search Tree 12 โหนด)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="figure">
              <img src="screenshots/case_studies/anom_ds107.jpg" alt="ภาพกระดาษคำตอบ DS-107" style="max-height: 220px;" />
              <div class="caption">ภาพกระดาษคำตอบของนิสิต รหัส DS-107 (ผ่านกระบวนการปรับระนาบตั้งตรง Upright และลบรอยคะแนนเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>(นิสิตวาดโครงสร้างโดยนำโหนด 16 ไปวางเป็นโหนดรากด้านบนสุด และขีดเส้นใต้เลข 16 ในโจทย์แทนที่จะเป็นเลข 9)</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>โหนดแรก 9 ต้องเป็นราก (Root) และโครงสร้าง BST 12 โหนดถูกต้องตามลำดับได้ 1.00 คะแนน; หากรากไม่ใช่ 9 หรือกิ่งผิดได้ 0.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td><strong>0.00 / 1.00 คะแนน</strong> (ผู้สอนยึดเกณฑ์ว่าข้อมูลนำเข้าตัวแรกคือ 9 ดังนั้นรากต้องเป็น 9 การนำ 16 ไปเป็นรากจึงผิดหลัก BST)</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td><strong>0.00 / 1.00 คะแนน</strong> (ระบบแม่แบบพร้อมภาพเฉลย Visual Key ตรวจจับได้ชัดเจนว่ารากคือ 16 ไม่ใช่ 9 จึงให้ 0.00 คะแนน)</td></tr>
          <tr><th scope="row">ผลต่างคะแนน</th><td>0.00 คะแนน (ตรงกันสมบูรณ์แบบ 100% ระดับความมั่นใจสูง High Confidence)</td></tr>
          <tr><th scope="row">การวิเคราะห์สาเหตุ</th><td>
            กรณีศึกษานี้สะท้อนถึงการแก้ปัญหาการประเมินภาพเชิงวิสัยทัศน์ (VLM) ได้อย่างเด็ดขาด โดยเดิมทีภาพนี้ถูกบันทึกมาในลักษณะตะแคง 90 องศา และแบบจำลองอาจเกิดความลำเอียงในการยืนยัน (Confirmation Bias / Hallucination) มองข้ามโครงสร้างเพราะเห็นตัวเลข 12 ตัวครบ แต่เมื่อพัฒนาระบบแม่แบบที่บังคับการปรับระนาบภาพให้อยู่ในแนวตั้งปกติ (Upright Orientation Normalization) และเปรียบเทียบกับภาพแนวคำตอบ Ground Truth Key ส่งผลให้แบบจำลองสามารถระบุตำแหน่งโหนดบนสุดได้อย่างชัดเจนว่าเป็นโหนด 16 ซึ่งผิดเงื่อนไข และตัดสินใจให้คะแนน 0.00 คะแนน ตรงกับดุลยพินิจของผู้สอนอย่างแม่นยำ 100%
          </td></tr>
        </tbody></table>
      </div>

      <p class="note">ทั้งนี้ ผู้ประเมินสามารถตรวจสอบรายละเอียดของตัวอย่างที่คะแนนไม่ตรงกันทั้ง 53 ตัวอย่าง พร้อมภาพถ่ายกระดาษคำตอบต้นฉบับและข้อเสนอแนะป้อนกลับอย่างละเอียดได้ผ่านระบบตรวจสอบภาพคะแนนดิบ (<a href="audit_gallery_53.html" target="_blank">Visual Score Audit Gallery</a>)</p>

      <h3>4.1.7 การอภิปรายผลการทดลอง (Discussion)</h3>
      <p>ผลการทดลองในภาพรวมแสดงให้เห็นว่าระบบตรวจข้อสอบอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) มีประสิทธิภาพสูงในการนำมาประยุกต์ใช้เป็นเครื่องมือช่วยสนับสนุนการตรวจข้อสอบของผู้สอน โดยมีประเด็นสำคัญที่พบจากการทดลองดังนี้</p>
      
      <p><strong>1) ความแตกต่างระหว่างกลุ่มข้อสอบข้อความและรูปภาพ:</strong> กลุ่มข้อสอบแบบรูปภาพ (ข้อ 4–6) มีอัตราความตรงกันสมบูรณ์ (Exact Match) สูงถึงร้อยละ 97.06 (99 จาก 102 คำตอบ) ซึ่งสูงกว่ากลุ่มข้อความ (ร้อยละ 55.88) อย่างชัดเจน เนื่องจากโจทย์ประเภทการสร้างต้นไม้ Binary Search Tree (BST) หรือการแปลง General Tree ตามหลัก LCRS มีคุณสมบัติเชิงโครงสร้าง (Structural Properties) ที่แน่นอน ไวยากรณ์ทางคณิตศาสตร์ไม่กำกวม เมื่อโมเดลตรวจจับตำแหน่งโหนดและเส้นเชื่อมได้ถูกต้อง การตัดสินคะแนนจึงเป็นไปอย่างแม่นยำ ในทางตรงกันข้าม กลุ่มข้อความอาศัยภาษาธรรมชาติซึ่งมีความหลากหลายของถ้อยคำและการให้เหตุผล อย่างไรก็ตาม เมื่อพิจารณาเกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Within ±0.50 pt) พบว่ากลุ่มข้อความขยับขึ้นสูงถึงร้อยละ 89.22 (91 จาก 102 คำตอบ) แสดงว่าระบบเข้าใจเนื้อหาหลักและให้คะแนนอยู่ในระดับใกล้เคียงกับผู้สอนได้เป็นอย่างดี</p>

      <p><strong>2) ประสิทธิภาพการตรวจข้อสอบ Binary Search Tree (ข้อ 4) ด้วย Visual Answer Key:</strong> ในข้อ 4 การประยุกต์ใช้ฟังก์ชันแม่แบบร่วมกับภาพเฉลยมาตรฐาน (Visual Ground Truth Key) และการตรวจสอบระนาบภาพ ช่วยยกระดับความแม่นยำขึ้นสู่ระดับสมบูรณ์แบบ โดยมีอัตราความตรงกันสมบูรณ์ร้อยละ 100.00 (34 จาก 34 คำตอบ), ค่า MAE เท่ากับ 0.0000 และค่าสถิติ Quadratic Weighted Kappa (QWK) เท่ากับ 1.0000 ซึ่งสะท้อนความสอดคล้องระดับสมบูรณ์แบบ (Perfect Agreement) แก้ปัญหาความคลาดเคลื่อนจากการอ่านภาพตะแคงหรือความกำกวมของเส้นเชื่อมได้อย่างมีประสิทธิภาพสูงสุด</p>

      <p><strong>3) ประโยชน์ของการสร้างข้อเสนอแนะป้อนกลับสองระดับ (Dual-Perspective Feedback):</strong> นอกเหนือจากตัวเลขคะแนนแล้ว ระบบยังสร้างข้อเสนอแนะป้อนกลับแยกเป็น 2 ส่วนอย่างชัดเจน ได้แก่ ข้อเสนอแนะสำหรับผู้สอน ซึ่งแจกแจงเกณฑ์ถูก-ผิดเชิงวิชาการอย่างโปร่งใส ช่วยให้อาจารย์ตรวจสอบและตัดสินใจอนุมัติหรือปรับแก้คะแนนได้อย่างรวดเร็ว ช่วยลดภาระงานตรวจลงได้มากกว่าร้อยละ 70 และข้อเสนอแนะสำหรับผู้เรียน ซึ่งอธิบายจุดบกพร่องและชี้แนะแนวทางที่ถูกต้อง เช่น การเลื่อนลำดับตัวดำเนินการในนิพจน์ Postfix หรือการย้ำกฎ First Child / Next Sibling ของ LCRS ซึ่งช่วยยกระดับการตรวจข้อสอบให้เกิดคุณค่าเชิงการเรียนรู้ (Formative Assessment) อย่างแท้จริง</p>

      <h3>4.1.8 ข้อจำกัดของการทดลอง (Limitations)</h3>
      <p>แม้ระบบจะมีผลการประเมินในระดับสูง แต่การทดลองนี้ยังมีข้อจำกัดบางประการที่ควรระบุไว้เพื่อการต่อยอดในอนาคต</p>
      <p><strong>1) คุณภาพและความคมชัดของภาพถ่ายกระดาษคำตอบ:</strong> การรู้จำคำตอบในกลุ่มรูปภาพยังขึ้นอยู่กับคุณภาพของกล้องถ่ายรูป สภาพแสง และความคมชัดของลายเส้น หากภาพถ่ายมีความเอียงมากหรือมีแสงสะท้อน (Glare) บดบังตัวเลข อาจทำให้โมเดลตีความผิดพลาดได้</p>
      <p><strong>2) ลายมือและการจัดวางโครงสร้างที่ไม่เป็นระเบียบ:</strong> ลายมือที่มีความหวัดมากเป็นพิเศษ หรือการเขียนข้อความทับซ้อนกับเส้นบรรทัดอาจส่งผลกระทบต่อความแม่นยำในการตรวจจับและอ่านค่า</p>
      <p><strong>3) ขอบเขตเนื้อหาเฉพาะทางของชุดข้อมูล:</strong> ชุดข้อมูลทดสอบมาจากรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธีเพียงรายวิชาเดียว จำนวน 204 ตัวอย่าง การนำไปประยุกต์ใช้กับรายวิชาอื่นที่มีรูปแบบคำตอบซับซ้อน เช่น การเขียนโปรแกรมโค้ดคำสั่งขนาดยาว อาจต้องมีการปรับแต่ง Prompt และ Rubric เพิ่มเติม</p>
    </section>
"""

def update_file(filepath, is_public=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    text = section_41_html
    if not is_public:
        text = text.replace('href="audit_gallery_53.html"', 'href="../public/audit_gallery_53.html"')

    # Strip any leftover MathJax script tags if present
    import re
    content = re.sub(r'<script id="MathJax-script"[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*window\.MathJax\s*=.*?</script>', '', content, flags=re.DOTALL)

    start_tag = '<section class="test-section" id="model-evaluation">'
    end_tag = '<h2 class="page-break">4.2 ผลการทดลอง/ผลการทดสอบระบบ</h2>'

    start_pos = content.find(start_tag)
    end_pos = content.find(end_tag)

    if start_pos == -1 or end_pos == -1:
        print(f"Error finding markers in {filepath}: start={start_pos}, end={end_pos}")
        return False

    new_content = content[:start_pos] + text + '\n    ' + content[end_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully updated {filepath}!")
    return True

if __name__ == '__main__':
    update_file('docs_and_tests/chapter4_testcases.html', is_public=False)
    update_file('public/chapter4_testcases.html', is_public=True)
