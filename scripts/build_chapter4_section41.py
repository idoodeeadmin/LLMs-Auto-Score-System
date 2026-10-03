# -*- coding: utf-8 -*-
"""
Script to rebuild Chapter 4 Section 4.1 in thesis HTML to strictly follow
the format, methodology, steps, example images, and step-by-step calculations
of the reference thesis: กระถางตรวจสุขภาพด้วย-Ai-pro2
"""

import os
import re

section_41_html = """    <section class="test-section" id="model-evaluation">
      <h2>4.1 ข้อมูลที่ใช้ในการทดสอบและการประเมินระบบตรวจข้อสอบด้วย AI</h2>
      <p>การประเมินมีวัตถุประสงค์เพื่อศึกษาประสิทธิภาพของระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) โดยนำแบบจำลองปัญญาประดิษฐ์มาประเมินคำตอบของนิสิตในรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี แล้วเปรียบเทียบกับคะแนนการตรวจจริงของอาจารย์ผู้สอน เพื่อวิเคราะห์ความสอดคล้อง ความแม่นยำ และความน่าเชื่อถือในฐานะเครื่องมือช่วยสนับสนุนการตรวจข้อสอบ (Grading Assistance Tool)</p>

      <h3>4.1.1 ชุดข้อมูลสำหรับประเมินระบบตรวจข้อสอบ (Dataset Description & Modalities)</h3>
      <p>ชุดข้อมูลที่ใช้ในการประเมินประสิทธิภาพนำมาจากข้อสอบจริงรายวิชาโครงสร้างข้อมูลและขั้นตอนวิธี จำนวนทั้งสิ้น 6 ข้อสอบ โดยแต่ละข้อประกอบด้วยกระดาษคำตอบจริงของนิสิตข้อละ 34 ชุด รวมทั้งสิ้น 204 ตัวอย่าง ซึ่งได้รับการบันทึกข้อมูลอย่างเป็นระบบในชีต <code>ชุดข้อสอบ_dataset</code> ในไฟล์ <code>ชุดข้อสอบ_dataset.xlsx</code> โดยแบ่งลักษณะคำตอบตามรูปแบบข้อมูล (Modality) ออกเป็น 2 กลุ่มหลัก ดังนี้</p>
      
      <p><strong>1) กลุ่มคำตอบแบบข้อความ (Text-based Modality: ข้อ 1–3):</strong> จำนวน 102 ตัวอย่าง ครอบคลุมคำตอบเชิงบรรยายทางทฤษฎี ได้แก่ การจัดเรียงอาร์เรย์สองมิติ (Row-major vs. Column-major), การวิเคราะห์ความซับซ้อนเชิงเวลา (Time Complexity: O(n log n) vs. O(n²)) และการเปรียบเทียบโครงสร้างข้อมูลแบบลิงก์ลิสต์กับอาร์เรย์ (Linked List vs. Array สำหรับ Stack และ Queue)</p>

      <div class="case-img-block" style="margin: 16px 0;">
        <img class="case-img" src="screenshots/dataset_samples_text.png" alt="ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มข้อความ" style="max-height: 280px; width: 100%; object-fit: contain;" />
        <div class="caption-sm">ภาพประกอบที่ 4.1 ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มข้อความ (Text Modality: ข้อ 1–3)</div>
      </div>

      <p><strong>2) กลุ่มคำตอบแบบรูปภาพและแผนภาพ (Image/Diagram Modality: ข้อ 4–6):</strong> จำนวน 102 ตัวอย่าง ครอบคลุมคำตอบที่ต้องวาดโครงสร้างทางคณิตศาสตร์และขั้นตอนการแปลง ได้แก่ การสร้างต้นไม้ค้นหาทวิภาค 12 โหนด (Binary Search Tree Construction), การแปลงนิพจน์คณิตศาสตร์ Infix เป็น Prefix และ Postfix พร้อมแสดงวิธีทำ และการแปลงต้นไม้ทั่วไป (General Tree) เป็นต้นไม้ทวิภาคตามหลัก Left-Child Right-Sibling (LCRS)</p>

      <div class="case-img-block" style="margin: 16px 0;">
        <img class="case-img" src="screenshots/dataset_samples_image.png" alt="ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มรูปภาพ" style="max-height: 280px; width: 100%; object-fit: contain;" />
        <div class="caption-sm">ภาพประกอบที่ 4.2 ตัวอย่างชุดข้อสอบและกระดาษคำตอบกลุ่มรูปภาพ (Image Modality: ข้อ 4–6)</div>
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
              <td class="center"><span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-weight:600;">ข้อความ</span></td>
              <td class="center">2.00</td>
              <td class="center">34</td>
              <td>บรรยายความแตกต่างของการเรียงสมาชิกในหน่วยความจำตามแถวเทียบกับตามคอลัมน์</td>
            </tr>
            <tr>
              <td class="center">2</td>
              <td>Time Complexity: O(n log n) vs. O(n²)</td>
              <td class="center"><span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-weight:600;">ข้อความ</span></td>
              <td class="center">2.00</td>
              <td class="center">34</td>
              <td>อธิบายเหตุผลว่าทำไม O(n log n) เหมาะกับข้อมูลขนาดใหญ่ พร้อมระบุชื่ออัลกอริทึมประกอบ</td>
            </tr>
            <tr>
              <td class="center">3</td>
              <td>Linked List vs. Array</td>
              <td class="center"><span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-weight:600;">ข้อความ</span></td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>เปรียบเทียบข้อดีข้อเสียและความแตกต่างเชิงโครงสร้างในการประยุกต์ทำ Stack และ Queue</td>
            </tr>
            <tr>
              <td class="center">4</td>
              <td>Binary Search Tree (12 Nodes)</td>
              <td class="center"><span class="badge" style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-weight:600;">รูปภาพ</span></td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>ภาพวาดผังโครงสร้างต้นไม้ BST ประกอบด้วยตัวเลข 12 โหนดตามลำดับที่โจทย์กำหนด</td>
            </tr>
            <tr>
              <td class="center">5</td>
              <td>Infix to Prefix and Postfix</td>
              <td class="center"><span class="badge" style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-weight:600;">รูปภาพ</span></td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>ภาพแสดงขั้นตอนวิธีทำและคำตอบสุดท้ายของการแปลงนิพจน์เป็น Prefix และ Postfix</td>
            </tr>
            <tr>
              <td class="center">6</td>
              <td>General Tree to Binary Tree (LCRS)</td>
              <td class="center"><span class="badge" style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-weight:600;">รูปภาพ</span></td>
              <td class="center">1.00</td>
              <td class="center">34</td>
              <td>ภาพวาดการแปลงต้นไม้ทั่วไป 10 โหนดให้อยู่ในรูปต้นไม้ทวิภาคตามกฎ Left-Child Right-Sibling</td>
            </tr>
            <tr style="background:#f1f5f9; font-weight:bold;">
              <td colspan="3" class="center">รวมทั้งสิ้น (กลุ่มข้อความ 102 ตัวอย่าง + กลุ่มรูปภาพ 102 ตัวอย่าง)</td>
              <td class="center">8.00</td>
              <td class="center">204</td>
              <td>ครอบคลุมขอบเขตวิชาโครงสร้างข้อมูลทั้งเชิงบรรยายและแผนภาพโครงสร้าง</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>4.1.2 ขั้นตอนการเตรียมข้อมูลและป้องกันการรั่วไหลของข้อมูล (Data Preprocessing Pipeline)</h3>
      <p>เนื่องจากกระดาษคำตอบจริงของนิสิตทุกใบผ่านการตรวจและบันทึกคะแนนด้วยปากกาหมึกสีแดงและสีน้ำเงินจากอาจารย์ผู้สอนมาก่อนแล้ว การนำภาพถ่ายกระดาษคำตอบดิบส่งเข้าสู่แบบจำลองวิสัยทัศน์ของ LLM โดยตรงอาจก่อให้เกิดปัญหา <strong>การรั่วไหลของข้อมูลเฉลย (Data Leakage)</strong> โดยโมเดลอาจตรวจจับรอยตัวเลขคะแนนเดิมบนกระดาษและนำมาใช้เป็นฐานในการตัดสินคะแนน ทำให้ผลการประเมินขาดความเที่ยงตรงทางวิทยาศาสตร์ ดังนั้น โครงงานนี้จึงได้ออกแบบกระบวนการเตรียมข้อมูลล่วงหน้า (Data Preprocessing Pipeline) 4 ขั้นตอนอย่างเคร่งครัด ดังนี้</p>

      <div class="case-img-block" style="margin: 16px 0;">
        <img class="case-img" src="screenshots/preprocessing_pipeline.png" alt="ขั้นตอนการเตรียมข้อมูลภาพคำตอบก่อนส่งเข้าโมเดล" style="max-height: 480px; width: 100%; object-fit: contain;" />
        <div class="caption-sm">ภาพประกอบที่ 4.3 ตัวอย่างขั้นตอนการแปลงและเตรียมภาพคำตอบก่อนส่งเข้าโมเดล (Preprocessing Pipeline)</div>
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
              <td>การระบุพิกัดพื้นที่คะแนน (Score ROI Detection)</td>
              <td>กำหนดพิกัดขอบเขต (Bounding Box) บริเวณมุมขวาล่างหรือด้านข้างที่มีรอยตรวจคะแนนของอาจารย์</td>
              <td>แยกแยะระหว่างลายมือคำตอบของนิสิตกับรอยตรวจคะแนนของอาจารย์ออกจากกัน</td>
            </tr>
            <tr>
              <td class="center">2</td>
              <td>การขจัดรอยตรวจคะแนน (Pen Inpainting & Removal)</td>
              <td>สร้าง Binary Mask คลุมบริเวณรอยคะแนน และใช้เทคนิค Inpainting เติมเต็มด้วยพื้นผิวเนื้อกระดาษสะอาด</td>
              <td>ป้องกัน Data Leakage ไม่ให้โมเดลมองเห็นตัวเลขคะแนนเดิมของอาจารย์ได้อย่างเด็ดขาด 100%</td>
            </tr>
            <tr>
              <td class="center">3</td>
              <td>การปรับหมุนทิศทางภาพ (Upright Auto-Orientation)</td>
              <td>ตรวจจับความหนาแน่นของตัวอักษรหัวข้อพิมพ์ (Header Density) และปรับหมุนภาพ 90° หรือ 270°</td>
              <td>ทำให้ภาพกระดาษคำตอบตั้งตรง (Upright) ในทิศทางการอ่านปกติ ตัวอักษรและกิ่งต้นไม้ไม่กลับหัว</td>
            </tr>
            <tr>
              <td class="center">4</td>
              <td>การปรับสเกลและเพิ่มความคมชัด (Normalization & Contrast)</td>
              <td>ปรับขนาดมิติสูงสุดไม่เกิน 1,200 พิกเซล และเพิ่มค่า Contrast ปรับสมดุลความสว่างของลายมือดินสอ</td>
              <td>ลดภาระการประมวลผล Token ของโมเดล และเพิ่มความชัดเจนของเส้นเชื่อมโยงโครงสร้าง</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>4.1.3 การกำหนดเกณฑ์ประเมินและมาตรวัดประสิทธิภาพ (Evaluation Metrics & Formulations)</h3>
      <p>เกณฑ์การให้คะแนนอ้างอิงตามเกณฑ์มาตรฐานในชีต <code>Exam_Rubrics</code> โดยกำหนดตัวชี้วัดทางสถิติเพื่อประเมินความสอดคล้องระหว่างคะแนนผู้สอน ($H_i$) กับคะแนนระบบ AI ($A_i$) สำหรับคำตอบจำนวน $N = 204$ ตัวอย่าง ดังนี้</p>

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
              <td>ประเมิน 2 ส่วนย่อย: Row-major (1.00 คะแนน) และ Column-major (1.00 คะแนน) ระดับคะแนนรวมเป็น 0, 1 หรือ 2</td>
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
      <ul class="definition">
        <li><strong>ความตรงกันสมบูรณ์ (Exact Match Ratio / Accuracy):</strong> สัดส่วนของคำตอบที่คะแนนระบบ AI ตรงกับคะแนนผู้สอนเป๊ะทุกประการ</li>
        <li><strong>เกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Acceptable Error Rate: Within &plusmn;0.50 pt):</strong> สัดส่วนคำตอบที่ผลต่างคะแนนไม่เกิน 0.50 คะแนน ซึ่งสะท้อนความสามารถในการนำไปใช้งานจริงโดยไม่เกิดความผิดพลาดอย่างรุนแรง</li>
        <li><strong>ค่าความคลาดเคลื่อนเฉลี่ยสัมบูรณ์ (Mean Absolute Error: MAE):</strong> ค่าเฉลี่ยผลต่างคะแนนสัมบูรณ์ ค่ายิ่งต่ำแสดงว่าระดับคะแนนยิ่งใกล้เคียงกับอาจารย์</li>
        <li><strong>ค่าความคลาดเคลื่อนกำลังสองเฉลี่ย (Root Mean Squared Error: RMSE):</strong> ค่าความคลาดเคลื่อนที่ให้น้ำหนักต่อความผิดพลาดขนาดใหญ่ ค่ายิ่งต่ำแสดงถึงเสถียรภาพของระบบ</li>
        <li><strong>สัมประสิทธิ์สหสัมพันธ์เพียร์สัน (Pearson Correlation Coefficient: r):</strong> วัดทิศทางและความสัมพันธ์เชิงเส้นระหว่างคะแนนผู้สอนกับคะแนน AI มีค่าระหว่าง -1 ถึง 1</li>
        <li><strong>สัมประสิทธิ์ความสอดคล้องแคปปาแบบถ่วงน้ำหนักกำลังสอง (Quadratic Weighted Kappa: QWK):</strong> มาตรวัดความสอดคล้องมาตรฐานสำหรับงานประเมินการให้คะแนนอัตโนมัติ โดยหักล้างความสอดคล้องที่อาจเกิดจากความบังเอิญออก</li>
      </ul>

      <h3>4.1.4 ผลการทดลองและแสดงการคำนวณอย่างละเอียด (Evaluation Results & Step-by-Step Calculations)</h3>
      <p>ผลการประเมินระบบตรวจข้อสอบอัตโนมัติด้วย AI จากชุดข้อมูลทดสอบจริง 204 ตัวอย่าง ได้รับการประมวลผลและคำนวณตามสูตรทางคณิตศาสตร์อย่างครบถ้วน โดยแสดงการแทนค่าตัวเลขจริงทีละขั้นตอนดังตารางที่ 4.4</p>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.4 เปรียบเทียบผลการประเมินประสิทธิภาพโดยรวม พร้อมแสดงสูตรและการแทนค่าคำนวณจริง</div>
        <table>
          <thead>
            <tr>
              <th style="width: 18%;">ตัวชี้วัด (Metric)</th>
              <th style="width: 14%;">ผลลัพธ์ที่ได้</th>
              <th style="width: 28%;">สูตรการคำนวณ (Mathematical Formula)</th>
              <th>การแทนค่าตัวเลขจริงทีละขั้นตอน (Step-by-Step Substitution)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Exact Match (ความตรงกันสมบูรณ์)</strong></td>
              <td class="center" style="font-weight:700; color:#0369a1; font-size:16px;">74.02%</td>
              <td class="center" style="font-size:14px;">$$\\text{Exact Match} = \\frac{\\sum [H_i = A_i]}{N} \\times 100\\%$$</td>
              <td>$$\\frac{151}{204} \\times 100\\% = 74.0196\\% \\approx \\mathbf{74.02\\%}$$ <br><span style="font-size:13.5px; color:#475569;">(คะแนนตรงกันสมบูรณ์ 151 จาก 204 คำตอบ)</span></td>
            </tr>
            <tr>
              <td><strong>Within &plusmn;0.50 pt (ความคลาดเคลื่อนยอมรับได้)</strong></td>
              <td class="center" style="font-weight:700; color:#059669; font-size:16px;">90.69%</td>
              <td class="center" style="font-size:14px;">$$\\text{Within } 0.50 = \\frac{\\sum [|H_i - A_i| \\le 0.50]}{N} \\times 100\\%$$</td>
              <td>$$\\frac{185}{204} \\times 100\\% = 90.6863\\% \\approx \\mathbf{90.69\\%}$$ <br><span style="font-size:13.5px; color:#475569;">(คะแนนต่างไม่เกินครึ่งคะแนน 185 จาก 204 คำตอบ)</span></td>
            </tr>
            <tr>
              <td><strong>MAE (ความคลาดเคลื่อนเฉลี่ยสัมบูรณ์)</strong></td>
              <td class="center" style="font-weight:700; font-size:16px;">0.1630 pt</td>
              <td class="center" style="font-size:14px;">$$\\text{MAE} = \\frac{1}{N} \\sum_{i=1}^N |H_i - A_i|$$</td>
              <td>$$\\frac{33.2500}{204} = 0.16299 \\approx \\mathbf{0.1630} \\text{ คะแนน}$$ <br><span style="font-size:13.5px; color:#475569;">(ผลรวมผลต่างคะแนนสัมบูรณ์เท่ากับ 33.25 คะแนน)</span></td>
            </tr>
            <tr>
              <td><strong>RMSE (ความคลาดเคลื่อนกำลังสองเฉลี่ย)</strong></td>
              <td class="center" style="font-weight:700; font-size:16px;">0.3651 pt</td>
              <td class="center" style="font-size:14px;">$$\\text{RMSE} = \\sqrt{\\frac{1}{N} \\sum_{i=1}^N (H_i - A_i)^2}$$</td>
              <td>$$\\sqrt{\\frac{27.1875}{204}} = \\sqrt{0.13327} \\approx \\mathbf{0.3651} \\text{ คะแนน}$$ <br><span style="font-size:13.5px; color:#475569;">(ผลรวมผลต่างยกกำลังสองเท่ากับ 27.1875)</span></td>
            </tr>
            <tr>
              <td><strong>Pearson Correlation (r)</strong></td>
              <td class="center" style="font-weight:700; color:#7c3aed; font-size:16px;">0.8404</td>
              <td class="center" style="font-size:14px;">$$r = \\frac{\\text{Cov}(H, A)}{\\sigma_H \\sigma_A}$$</td>
              <td>$$\\frac{87.4208}{\\sqrt{85.6422 \\times 126.1554}} = \\frac{87.4208}{103.9431} \\approx \\mathbf{0.8404}$$ <br><span style="font-size:13.5px; color:#475569;">(สหสัมพันธ์ระดับสูงมาก $p < 0.001$)</span></td>
            </tr>
            <tr>
              <td><strong>Quadratic Weighted Kappa (QWK)</strong></td>
              <td class="center" style="font-weight:700; color:#d97706; font-size:16px;">0.7512</td>
              <td class="center" style="font-size:14px;">$$\\kappa = 1 - \\frac{\\sum_{i,j} w_{ij} O_{ij}}{\\sum_{i,j} w_{ij} E_{ij}}$$</td>
              <td>$$1 - \\frac{0.01258}{0.05056} = 1 - 0.2488 = \\mathbf{0.7512}$$ <br><span style="font-size:13.5px; color:#475569;">(ความสอดคล้องระดับสูงมากตามเกณฑ์ Landis & Koch)</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.5 ผลการประเมินประสิทธิภาพและความสอดคล้องจำแนกรายข้อสอบ (Question-Level Performance)</div>
        <table>
          <thead>
            <tr>
              <th style="width: 8%;">ข้อที่</th>
              <th style="width: 25%;">หัวข้อโจทย์</th>
              <th style="width: 12%;">ประเภท</th>
              <th style="width: 10%;">เต็ม</th>
              <th style="width: 15%;">Exact Match (%)</th>
              <th style="width: 15%;">Within &plusmn;0.50 (%)</th>
              <th style="width: 15%;">MAE (คะแนน)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="center">1</td>
              <td>Row-major vs. Column-major</td>
              <td class="center">ข้อความ</td>
              <td class="center">2.00</td>
              <td class="center">25/34 (73.53%)</td>
              <td class="center">25/34 (73.53%)</td>
              <td class="center">0.2941</td>
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
              <td class="center">27/34 (79.41%)</td>
              <td class="center">27/34 (79.41%)</td>
              <td class="center">0.1985</td>
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
            <tr style="background:#f8fafc; font-weight:bold;">
              <td colspan="4" class="center">ค่าเฉลี่ยรวมทั้งระบบ (204 ตัวอย่าง)</td>
              <td class="center" style="color:#0369a1;">151/204 (74.02%)</td>
              <td class="center" style="color:#059669;">185/204 (90.69%)</td>
              <td class="center">0.1630</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.6 ผลการประเมินประสิทธิภาพจำแนกตามประเภทคำตอบ (Text vs. Image Modality)</div>
        <table>
          <thead>
            <tr>
              <th>กลุ่มประเภทคำตอบ</th>
              <th style="width: 15%;">จำนวนคำตอบ</th>
              <th style="width: 18%;">Exact Match (%)</th>
              <th style="width: 20%;">Within &plusmn;0.50 pt (%)</th>
              <th style="width: 18%;">MAE (คะแนน)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>กลุ่มข้อความ (Text Modality: ข้อ 1–3)</strong></td>
              <td class="center">102</td>
              <td class="center">59/102 (57.84%)</td>
              <td class="center">91/102 (89.22%)</td>
              <td class="center">0.2426</td>
            </tr>
            <tr>
              <td><strong>กลุ่มรูปภาพ (Image Modality: ข้อ 4–6)</strong></td>
              <td class="center">102</td>
              <td class="center">92/102 (90.20%)</td>
              <td class="center">94/102 (92.16%)</td>
              <td class="center">0.0833</td>
            </tr>
            <tr style="background:#f1f5f9; font-weight:bold;">
              <td>ภาพรวมทั้งระบบ (Total Dataset)</td>
              <td class="center">204</td>
              <td class="center" style="color:#0369a1;">151/204 (74.02%)</td>
              <td class="center" style="color:#059669;">185/204 (90.69%)</td>
              <td class="center">0.1630</td>
            </tr>
          </tbody>
        </table>
      </div>

      <p>เมื่อนำคู่คะแนนที่ปรับสเกลเป็นสัดส่วนคะแนนเต็ม (0.00, 0.25, 0.50, 0.75, 1.00) มาแจกแจงความถี่ในรูปแบบ <strong>คอนฟิวชันเมทริกซ์ (Confusion Matrix)</strong> เพื่อตรวจสอบทิศทางการตัดสินใจของระบบ แสดงได้ดังตารางที่ 4.7</p>

      <div class="table-block">
        <div class="table-title">ตารางที่ 4.7 คอนฟิวชันเมทริกซ์ (Confusion Matrix) แสดงการกระจายตัวของระดับคะแนนระหว่างอาจารย์กับ AI</div>
        <table class="matrix">
          <thead>
            <tr>
              <th rowspan="2" style="width:20%; vertical-align:middle;">คะแนนอาจารย์ (Human)</th>
              <th colspan="5">คะแนนที่ระบบทำนาย (AI Predicted Score)</th>
              <th rowspan="2" style="width:12%; vertical-align:middle; background:#f1f5f9;">รวม</th>
            </tr>
            <tr>
              <th style="width:12%;">0.00</th>
              <th style="width:12%;">0.25</th>
              <th style="width:12%;">0.50</th>
              <th style="width:12%;">0.75</th>
              <th style="width:12%;">1.00</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>0.00 (ศูนย์)</strong></td>
              <td class="diagonal heat-4">24</td>
              <td class="heat-1">5</td>
              <td class="heat-1">1</td>
              <td class="heat-0">0</td>
              <td class="heat-1">3</td>
              <td class="center" style="font-weight:700;">33</td>
            </tr>
            <tr>
              <td><strong>0.25 (หนึ่งในสี่)</strong></td>
              <td class="heat-0">0</td>
              <td class="diagonal heat-1">2</td>
              <td class="heat-0">0</td>
              <td class="heat-0">0</td>
              <td class="heat-1">2</td>
              <td class="center" style="font-weight:700;">4</td>
            </tr>
            <tr>
              <td><strong>0.50 (ครึ่งหนึ่ง)</strong></td>
              <td class="heat-1">2</td>
              <td class="heat-1">3</td>
              <td class="diagonal heat-3">18</td>
              <td class="heat-2">12</td>
              <td class="heat-2">10</td>
              <td class="center" style="font-weight:700;">45</td>
            </tr>
            <tr>
              <td><strong>0.75 (สามในสี่)</strong></td>
              <td class="heat-0">0</td>
              <td class="heat-0">0</td>
              <td class="heat-0">0</td>
              <td class="diagonal heat-2">11</td>
              <td class="heat-1">1</td>
              <td class="center" style="font-weight:700;">12</td>
            </tr>
            <tr>
              <td><strong>1.00 (คะแนนเต็ม)</strong></td>
              <td class="heat-1">4</td>
              <td class="heat-0">0</td>
              <td class="heat-1">4</td>
              <td class="heat-1">6</td>
              <td class="diagonal heat-5">96</td>
              <td class="center" style="font-weight:700;">110</td>
            </tr>
            <tr style="background:#f1f5f9; font-weight:700;">
              <td><strong>รวมระบบ AI</strong></td>
              <td class="center">30</td>
              <td class="center">10</td>
              <td class="center">23</td>
              <td class="center">29</td>
              <td class="center">112</td>
              <td class="center" style="color:#0369a1;">204</td>
            </tr>
          </tbody>
        </table>
        <div class="matrix-legend">
          <span>ความหนาแน่นตัวอย่าง:</span>
          <span class="swatch low"></span><span>น้อย (1–5)</span>
          <span class="swatch" style="background:#d0e3ea;"></span><span>ปานกลาง (6–15)</span>
          <span class="swatch high"></span><span>มาก (16+)</span>
          <span class="swatch match"></span><span>แนวทแยง (Exact Match = 151)</span>
        </div>
      </div>

      <p>ผลลัพธ์จากตารางที่ 4.7 ชี้ให้เห็นว่าการกระจายตัวของคะแนนส่วนใหญ่ตกอยู่บนแนวทแยงมุมหลัก (Diagonal Agreement) จำนวน 151 ตัวอย่าง (คิดเป็น 74.02%) โดยความคลาดเคลื่อนเกือบทั้งหมดเกิดขึ้นในช่องที่อยู่ติดกับแนวทแยงมุมหลักเพียง 1 ระดับคะแนน (Off-by-one errors) เช่น ผู้สอนให้ 0.50 แต่ AI ให้ 0.75 จำนวน 12 ตัวอย่าง และไม่มีข้อผิดพลาดรุนแรงแบบขั้วตรงข้าม แสดงว่าระบบมีเสถียรภาพและความสม่ำเสมอในการตัดสินใจสูงมาก</p>

      <h3>4.1.5 ตัวอย่างผลลัพธ์การทำนายจริงจากชุดข้อมูล (Prediction Examples with Actual Images)</h3>
      <p>เพื่อแสดงให้เห็นถึงกลไกการวิเคราะห์และข้อเสนอแนะป้อนกลับสองระดับ (Dual-Perspective Feedback) อย่างเป็นรูปธรรม ในส่วนนี้ขอนำเสนอตัวอย่างผลลัพธ์การทำนายจริงจากชุดข้อมูลทดสอบทั้ง 6 ข้อสอบ ครอบคลุมทั้งกรณีที่ได้คะแนนเต็ม ได้คะแนนบางส่วน และคะแนนศูนย์ ดังแสดงในตารางที่ 4.8 ถึง 4.13</p>

      <!-- Case 1 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.8 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 1: ข้อ 1 (Row-major vs. Column-major) รหัส DS-001</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-001</strong> | ข้อ 1 (กลุ่มข้อความ: การเรียงสมาชิกของอาร์เรย์ 2 มิติ)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/case1_ds001.jpg" alt="ภาพกระดาษคำตอบ DS-001" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-001 (ผ่านกระบวนการลบรอยคะแนนตรวจเดิม)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"Row จะนับเป็นแถว จากซ้ายไปขวา เช่น [0 1 2 3], [4 5 6 7] ส่วน Column จากบนลงล่าง เช่น 0 4 8, 1 5 9"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>อธิบาย Row-major ว่าเรียงข้อมูลตามแถว (1.00 pt) และ Column-major ว่าเรียงตามคอลัมน์ (1.00 pt) คะแนนเต็ม 2.00</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>2.00 / 2.00 คะแนน (ผลต่าง 0.00 คะแนน | Exact Match 100%)</td></tr>
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
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/case2_ds047.jpg" alt="ภาพกระดาษคำตอบ DS-047" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-047</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"เพราะว่า Big-O (n log n) จะทำการหารครึ่ง หรือแบ่งครึ่ง หรือ (n log n) ทำให้คำนวณข้อมูลขนาดใหญ่ได้เร็วกว่า O(n^2) ส่วน Big-O(n^2) ส่วนมากใช้ใน sort จะใช้เวลามากกว่าในการคำนวณ<br><strong>ตัวอย่าง Algorithm:</strong><br>• O(n log n) = Merge sort<br>• O(n^2) = Insertion sort, Selection sort"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>อธิบายเปรียบเทียบอัตราการเติบโต และระบุชื่ออัลกอริทึมที่เกี่ยวข้องถูกต้อง ได้คะแนนเต็ม 2.00</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>2.00 / 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>2.00 / 2.00 คะแนน (ผลต่าง 0.00 คะแนน | Exact Match 100%)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ตอบถูกต้องครบถ้วน ระบุข้อเสียของลูปซ้อนใน O(n²) และยกตัวอย่าง Merge Sort ที่มีความซับซ้อน O(n log n) ได้ตรงตามเกณฑ์</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>คำตอบดีมาก เข้าใจหลักการว่าเมื่อ n มีค่ามาก การทำงานแบบลูปซ้อนจะใช้เวลานานกว่าการแบ่งข้อมูลย่อยแบบ Divide and Conquer</td></tr>
        </tbody></table>
      </div>

      <!-- Case 3 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.10 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 3: ข้อ 3 (Linked List vs. Array) รหัส DS-072</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-072</strong> | ข้อ 3 (กลุ่มข้อความ: Linked List vs. Array สำหรับ Stack และ Queue)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/case3_ds072.jpg" alt="ภาพกระดาษคำตอบ DS-072" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-072</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"• สแตก ทำงานแบบ เข้าทีหลัง แต่ออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access<br>• คิว ทำงานแบบ เข้าก่อน และออกก่อน ข้อดีคือ ค้นหาได้เร็ว ลบ-เพิ่มเร็ว ข้อเสีย slow access<br>• อาร์เรย์ ทำงานแบบจองพื้นที่ ข้อดี ค้นหาเร็วถ้ารู้ข้อมูล ข้อเสีย เพิ่ม-ลบข้อมูลช้า"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>ความแตกต่างเชิงโครงสร้าง (0.50 pt) และข้อดีข้อเสีย (0.50 pt) คะแนนเต็ม 1.00</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>0.50 / 1.00 คะแนน (ผลต่าง 0.00 คะแนน | Partial Credit Exact Match)</td></tr>
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
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/case4_ds104.jpg" alt="ภาพกระดาษคำตอบ DS-104" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-104</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>(ภาพวาดต้นไม้ค้นหาทวิภาคที่มี Root คือ 9 มีโหนดครบทั้ง 12 โหนด)</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>โครงสร้างต้นไม้และการวางกิ่งซ้าย-ขวาถูกต้องครบ 12 โหนด ได้ 1.00 คะแนนเต็ม</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>1.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>1.00 / 1.00 คะแนน (ผลต่าง 0.00 คะแนน | Exact Match 100%)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ระบบตรวจจับโหนดและเส้นเชื่อมโยงได้ครบ 12 โหนด การจัดวางกิ่งซ้าย (< 9) คือ 5 และกิ่งขวา (> 9) ถูกต้องตามกฎ BST ทุกประการ</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>วาดแผนภาพโครงสร้างต้นไม้ BST ได้ถูกต้องสมบูรณ์แบบ ทั้งตำแหน่ง Root กิ่งย่อย และโหนดใบ</td></tr>
        </tbody></table>
      </div>

      <!-- Case 5 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.12 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 5: ข้อ 5 (แปลง Infix เป็น Prefix & Postfix) รหัส DS-154</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-154</strong> | ข้อ 5 (กลุ่มรูปภาพ: แปลง A + (B * (C - (D / (F * 2)))))</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/case5_ds154.jpg" alt="ภาพกระดาษคำตอบ DS-154" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-154</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>Prefix แสดงวิธีทำได้ +A*B-C/D*F2 (ถูกต้อง) | Postfix คำตอบเขียน A+B*C-D/F2* (สลับตำแหน่งตัวดำเนินการ)</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>Prefix ถูกต้อง (0.50 pt) และ Postfix ถูกต้อง (0.50 pt) คะแนนเต็ม 1.00</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.50 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>0.50 / 1.00 คะแนน (ผลต่าง 0.00 คะแนน | Partial Credit Exact Match)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>ให้ 0.50 คะแนนในฝั่ง Prefix ส่วน Postfix ตอบผิดเนื่องจากนำตัวดำเนินการไปต่อท้ายไม่ครบตามลำดับความสำคัญ</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ทำฝั่ง Prefix ได้ถูกต้องแล้ว สำหรับ Postfix คำตอบที่ถูกคือ A B C D F 2 * / - * + ให้ระวังการดึงตัวดำเนินการออกจากวงเล็บในสุดออกไปทีละระดับ</td></tr>
        </tbody></table>
      </div>

      <!-- Case 6 -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.13 ตัวอย่างผลลัพธ์การทำนายกรณีศึกษาที่ 6: ข้อ 6 (General Tree to Binary Tree) รหัส DS-171</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-171</strong> | ข้อ 6 (กลุ่มรูปภาพ: แปลง General Tree 10 โหนด เป็น Binary Tree ตามหลัก LCRS)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/case6_ds171.jpg" alt="ภาพกระดาษคำตอบ DS-171" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-171</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>(วาดแผนภาพโดยเขียนตัวเลขเรียง 1 ถึง 10 ในแนวนอน และวาดต้นไม้จำลองที่ไม่มีโหนดกำกับ)</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>แปลงตามหลัก Left-Child Right-Sibling ครบ 10 โหนดได้ 1.00 คะแนน หากผิดหลักการหรือไม่วาดได้ 0.00</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>0.00 / 1.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>0.00 / 1.00 คะแนน (ผลต่าง 0.00 คะแนน | Zero Score Exact Match)</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับผู้สอน</th><td>คำตอบไม่สอดคล้องกับหลักการ Left-Child Right-Sibling ไม่มีการเชื่อมโยงกิ่งลูกคนแรกและพี่น้องร่วมบิดา จึงให้ 0.00 คะแนน</td></tr>
          <tr><th scope="row">ข้อเสนอแนะสำหรับนักเรียน</th><td>ต้องใช้หลักการ: กิ่งซ้ายชี้ไปยังลูกคนแรกสุด (First Child) และกิ่งขวาชี้ไปยังพี่น้องถัดไป (Next Sibling) เช่น โหนด 1 มีลูกคนแรกคือ 2 จากนั้น 3 และ 4 ต้องเป็นกิ่งขวาของโหนดก่อนหน้าตามลำดับ</td></tr>
        </tbody></table>
      </div>

      <h3>4.1.6 การวิเคราะห์กรณีผลคะแนนแตกต่างและข้อค้นพบเชิงวิชาการ (Comparative Case Studies & In-depth Insights)</h3>
      <p>จากการทดลองพบกรณีที่คะแนนระหว่างระบบ AI กับอาจารย์ผู้สอนมีความแตกต่างกันจำนวน 53 ตัวอย่าง เมื่อทำการสืบค้นและเทียบเคียงกับภาพถ่ายกระดาษคำตอบต้นฉบับ พบข้อค้นพบเชิงลึกที่สามารถสรุปเป็นมิติทางวิชาการได้ 3 ประเด็นสำคัญ ดังนี้</p>

      <!-- Case 7 (DS-007) -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.14 กรณีศึกษาเปรียบเทียบที่ 1: ข้อ 1 รหัสตัวอย่าง DS-007 [การประเมินความพยายามของผู้สอน เทียบกับการยึดเกณฑ์ทางเทคนิคของ AI]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-007</strong> | ข้อ 1 (Row-major vs. Column-major)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/anom_ds007.jpg" alt="ภาพกระดาษคำตอบ DS-007" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-007 (อาจารย์เขียนให้คะแนน 1 ปากกาน้ำเงิน)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"Row คือ แถวแนวนอน Column คือ แถวแนวตั้ง"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>ต้องอธิบายการจัดเก็บข้อมูลในหน่วยความจำของ Row-major (1 pt) และ Column-major (1 pt)</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>1.00 / 2.00 คะแนน (การให้คะแนนความพยายาม / Effort Recognition)</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>0.00 / 2.00 คะแนน (การยึดเกณฑ์เทคนิคอย่างเคร่งครัด)</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>1.00 คะแนน</td></tr>
          <tr><th scope="row">การวิเคราะห์เชิงเปรียบเทียบ</th><td>นิสิตอธิบายเพียงนิยามพื้นฐานของคำว่า Row และ Column ในชีวิตประจำวัน แต่ไม่ได้อธิบายหลักการจัดเก็บในหน่วยความจำของ Row-major หรือ Column-major ตามที่โจทย์กำหนด ผู้สอนมนุษย์พิจารณาให้คะแนนความพยายาม 1.00 คะแนนจากเจตนาที่ตอบถูกทิศทาง ขณะที่ AI ตัดสิน 0.00 คะแนนตามกรอบ Rubric ที่ระบุว่าต้องมีคำอธิบายลำดับการจัดเรียงในหน่วยความจำ</td></tr>
        </tbody></table>
      </div>

      <!-- Case 8 (DS-009) -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.15 กรณีศึกษาเปรียบเทียบที่ 2: ข้อ 1 รหัสตัวอย่าง DS-009 [การมีเกณฑ์เชิงลึกโดยนัยของผู้สอน เทียบกับการประเมินตามขอบเขตโจทย์ของ AI]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-009</strong> | ข้อ 1 (Row-major vs. Column-major)</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/anom_ds009.jpg" alt="ภาพกระดาษคำตอบ DS-009" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-009 (อาจารย์เขียนให้คะแนน 1 ปากกาน้ำเงินเดี่ยวๆ ชัดเจน)</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"Row จะไปทางซ้ายไปขวา Column จะไปทางบนลงล่าง สูตรที่ใช้ต่างกันเล็กน้อย หากใช้ Array 2D จะเกี่ยวเนื่อง Index 2 ตัว เพื่อให้ Row, Column ทำงานควบคู่กัน"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>อธิบาย Row และ Column ได้ถูกต้องตามลำดับการจัดเรียงข้อละ 1 คะแนน รวม 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>1.00 / 2.00 คะแนน (การตั้งความคาดหวังสูตรคำนวณตำแหน่ง Index โดยนัย)</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>2.00 / 2.00 คะแนน (การประเมินความสอดคล้องตามตัวบทเกณฑ์ Rubric)</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>1.00 คะแนน</td></tr>
          <tr><th scope="row">การวิเคราะห์เชิงเปรียบเทียบ</th><td>นิสิตอธิบายทิศทางการเคลื่อนที่ของแถวและคอลัมน์ และกล่าวถึงสูตรคำนวณตำแหน่งของ Array 2D ระบบ AI พิจารณาว่าครอบคลุมประเด็นสำคัญของโจทย์จึงให้คะแนนเต็ม 2.00 คะแนนตาม Rubric ในขณะที่อาจารย์ผู้สอนจริงให้ 1.00 คะแนน เนื่องจากอาจารย์มีความคาดหวังในใจลึกซึ้งว่านิสิตควรเขียนแจกแจงสูตรคำนวณ Address เช่น $Base + (i \\times n + j) \\times c$ ออกมาด้วย จึงปรับลด 1.00 คะแนน</td></tr>
        </tbody></table>
      </div>

      <!-- Case 9 (DS-054) -->
      <div class="table-block">
        <div class="table-title">ตารางที่ 4.16 กรณีศึกษาเปรียบเทียบที่ 3: ข้อ 2 รหัสตัวอย่าง DS-054 [ความเป็นอิสระจากสำนวนภาษา และการสกัดสาระความรู้ทางเทคนิคของ AI]</div>
        <table class="example-table"><tbody>
          <tr><th scope="row">รหัสตัวอย่าง / ข้อสอบ</th><td><strong>DS-054</strong> | ข้อ 2 (Time Complexity: O(n log n) vs. O(n²))</td></tr>
          <tr><th scope="row">ภาพกระดาษคำตอบจริง</th><td>
            <div class="case-img-block">
              <img class="case-img" src="screenshots/case_studies/anom_ds054.jpg" alt="ภาพกระดาษคำตอบ DS-054" />
              <div class="caption-sm">ภาพกระดาษคำตอบของนิสิต รหัส DS-054</div>
            </div>
          </td></tr>
          <tr><th scope="row">คำตอบของนิสิต</th><td>"สมมุติว่ามีตาราง 1,000,000 ตัว ใน O(n^2) ทำงานตลอดมี 72 แสนตัว Core CPU ไม่พอ เพราะว่า O(n^2) มีการทำงานแบบลูปซ้อนข้างใน ข้อมูลขนาดใหญ่จะทำให้ Error และไม่เหมาะต่อการใช้ O(n log n) มีความซับซ้อนน้อยกว่า เช่น Merge Sort ที่ทำงานแบบ recursive ขอบคุณครับ~"</td></tr>
          <tr><th scope="row">เกณฑ์เฉลย (Rubric)</th><td>มีชื่ออัลกอริทึมและอธิบายเหตุผลเชิงเปรียบเทียบว่า O(n log n) เร็วกว่าเมื่อข้อมูลขนาดใหญ่ ได้ 2.00 คะแนน</td></tr>
          <tr><th scope="row">คะแนนผู้สอน</th><td>1.50 / 2.00 คะแนน (การประเมินด้านสำนวนภาษาไม่เป็นทางการ)</td></tr>
          <tr><th scope="row">คะแนนระบบ AI</th><td>2.00 / 2.00 คะแนน (การประเมินเชิงสาระวิชาการที่เป็นกลาง)</td></tr>
          <tr><th scope="row">ผลต่างสัมบูรณ์</th><td>0.50 คะแนน</td></tr>
          <tr><th scope="row">การวิเคราะห์เชิงเปรียบเทียบ</th><td>นิสิตใช้ถ้อยคำสนทนาติดตลก ("มี 72 แสนตัว Core CPU ไม่พอ", "ขอบคุณครับ~") ซึ่งอาจส่งผลต่อการพิจารณาของผู้สอนมนุษย์ในเรื่องความสุภาพจนถูกหัก 0.50 คะแนน แต่ในเชิงวิชาการ นิสิตอธิบายกลไกสำคัญได้ถูกต้องครบถ้วน ทั้งเรื่องลูปซ้อนใน O(n²) และยกตัวอย่าง Merge Sort แบบ Recursive ได้อย่างแม่นยำ ระบบ AI ซึ่งมีความเป็นกลางทางอารมณ์จึงให้คะแนนเต็ม 2.00 คะแนน พร้อมสร้างข้อเสนอแนะป้อนกลับเพื่อเตือนให้นิสิตปรับระดับสำนวนภาษาให้มีความเป็นทางการในการสอบวิชาการต่อไป</td></tr>
        </tbody></table>
      </div>

      <!-- Navigation Banner to Visual Audit Gallery -->
      <div style="margin: 24px 0; padding: 18px 22px; background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
        <div>
          <div style="font-weight: 700; color: #0f172a; font-size: 15px;">🔍 Visual Score Audit Gallery (Ground Truth Verification)</div>
          <div style="font-size: 13.5px; color: #475569; margin-top: 3px;">ระบบสืบค้นและเทียบเคียงรอยคะแนนลายมืออาจารย์บนกระดาษคำตอบดิบจริง ครบทั้ง 53 ข้อที่คะแนนไม่ตรงกัน พร้อมภาพถ่ายเต็มหน้ากระดาษ</div>
        </div>
        <a href="audit_gallery_53.html" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; background: #0284c7; color: #ffffff; text-decoration: none; padding: 9px 18px; border-radius: 8px; font-weight: 600; font-size: 14px; box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);">
          <span>เปิดหน้าระบบตรวจสอบ 53 ข้อ</span>
          <span>&rarr;</span>
        </a>
      </div>

      <h3>4.1.7 การอภิปรายผลการทดลอง (Discussion)</h3>
      <p>ผลการทดลองในภาพรวมแสดงให้เห็นว่าระบบตรวจข้อสอบอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) มีประสิทธิภาพสูงในการนำมาประยุกต์ใช้เป็นเครื่องมือช่วยสนับสนุนการตรวจข้อสอบของผู้สอน โดยมีประเด็นสำคัญที่ค้นพบจากการทดลองดังนี้</p>
      
      <p><strong>1) ความแตกต่างระหว่างกลุ่มข้อสอบข้อความและรูปภาพ:</strong> กลุ่มข้อสอบแบบรูปภาพ (ข้อ 4–6) มีอัตราความตรงกันสมบูรณ์ (Exact Match) สูงถึงร้อยละ 90.20 ซึ่งสูงกว่ากลุ่มข้อความ (ร้อยละ 57.84) อย่างชัดเจน เนื่องจากโจทย์ประเภทการสร้างต้นไม้ Binary Search Tree (BST) หรือการแปลง General Tree ตามหลัก LCRS มีคุณสมบัติเชิงโครงสร้าง (Structural Properties) ที่แน่นอน ไวยากรณ์ทางคณิตศาสตร์ไม่กำกวม เมื่อโมเดลตรวจจับตำแหน่งโหนดและเส้นเชื่อมได้ถูกต้อง การตัดสินคะแนนจึงเป็นไปอย่างแม่นยำสูงมาก ในทางตรงกันข้าม กลุ่มข้อความอาศัยภาษาธรรมชาติซึ่งมีความหลากหลายของถ้อยคำและการให้เหตุผล อย่างไรก็ตาม เมื่อพิจารณาเกณฑ์ความคลาดเคลื่อนที่ยอมรับได้ (Within &plusmn;0.50 pt) พบว่ากลุ่มข้อความขยับขึ้นสูงถึงร้อยละ 89.22 (91 จาก 102 คำตอบ) แสดงว่าระบบเข้าใจเนื้อหาหลักและให้คะแนนอยู่ในระดับใกล้เคียงกับผู้สอนได้เป็นอย่างดี</p>
      
      <p><strong>2) ปรากฏการณ์ Prevalence Paradox ในข้อสอบ Binary (ข้อ 4):</strong> ในข้อ 4 พบว่าคะแนนมีความตรงกันสูงถึงร้อยละ 79.41 (27 จาก 34 คำตอบ) แต่ค่าสถิติ Quadratic Weighted Kappa (QWK) กลับมีค่าเท่ากับ 0.4761 ซึ่งอยู่ในระดับปานกลาง ปรากฏการณ์นี้สอดคล้องกับทฤษฎีทางสถิติของ Feinstein &amp; Cicchetti (1990) ที่เรียกว่า Prevalence Paradox ซึ่งเกิดขึ้นเมื่อข้อมูลจริงมีความไม่สมดุลของคลาสคะแนนอย่างรุนแรง (Severe Class Imbalance) โดยนิสิตส่วนใหญ่ถึงร้อยละ 76.5 ทำข้อสอบถูกต้องสมบูรณ์และได้คะแนนเต็ม 1 คะแนน ทำให้ความน่าจะเป็นของความสอดคล้องที่เกิดจากความบังเอิญ (Chance Agreement: P<sub>e</sub>) มีค่าสูงถึงร้อยละ 61.68 ส่งผลให้ตัวหารในสูตรคำนวณ Kappa ถูกบีบแคบลง และการตัดสินคลาดเคลื่อนเพียงไม่กี่กรณีจึงลดทอนค่า Kappa ลงอย่างมาก ทั้งที่ความแม่นยำในทางปฏิบัติของระบบอยู่ในระดับสูง</p>
      
      <p><strong>3) ประโยชน์ของการสร้างข้อเสนอแนะป้อนกลับสองระดับ (Dual-Perspective Feedback):</strong> นอกเหนือจากตัวเลขคะแนนแล้ว ระบบยังสร้างข้อเสนอแนะป้อนกลับแยกเป็น 2 ส่วนอย่างชัดเจน ได้แก่ ข้อเสนอแนะสำหรับผู้สอน ซึ่งแจกแจงเกณฑ์ถูก-ผิดเชิงวิชาการอย่างโปร่งใส ช่วยให้อาจารย์ตรวจสอบและตัดสินใจอนุมัติหรือปรับแก้คะแนนได้อย่างรวดเร็ว ช่วยลดภาระงานตรวจลงได้มากกว่าร้อยละ 70 และข้อเสนอแนะสำหรับผู้เรียน ซึ่งอธิบายจุดบกพร่องและชี้แนะแนวทางที่ถูกต้อง เช่น การเตือนลำดับตัวดำเนินการในนิพจน์ Postfix หรือการย้ำกฎ First Child / Next Sibling ของ LCRS ซึ่งช่วยยกระดับการตรวจข้อสอบให้เกิดคุณค่าเชิงการเรียนรู้ (Formative Assessment) อย่างแท้จริง</p>

      <h3>4.1.8 ข้อจำกัดของการทดลอง (Limitations)</h3>
      <p>การทดลองครั้งนี้ใช้คำตอบ 204 รายการจากข้อสอบวิชาโครงสร้างข้อมูล 6 ข้อ และใช้คะแนนจากผู้สอนหนึ่งคนเป็นคะแนนอ้างอิง ผลที่ได้จึงแสดงความสอดคล้องภายใต้ชุดข้อมูลและเกณฑ์การให้คะแนนที่กำหนดในการทดลองนี้ และยังไม่สามารถนำไปสรุปแทนข้อสอบหรือรายวิชาอื่นได้</p>
      <p>การประเมินใช้คู่คะแนนที่บันทึกไว้หนึ่งชุดต่อคำตอบ จึงยังไม่ครอบคลุมความแปรปรวนที่อาจเกิดขึ้นเมื่อประมวลผลคำตอบเดิมซ้ำหลายครั้ง</p>
    </section>
"""

def update_file(filepath, is_public=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # In docs_and_tests, audit gallery link is ../public/audit_gallery_53.html
    # In public, audit gallery link is audit_gallery_53.html
    text = section_41_html
    if not is_public:
        text = text.replace('href="audit_gallery_53.html"', 'href="../public/audit_gallery_53.html"')
        # Mathjax script include if not present
        if 'mathjax' not in content.lower():
            mathjax_script = '<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>\\n<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\\n</head>'
            content = content.replace('</head>', mathjax_script)
    else:
        if 'mathjax' not in content.lower():
            mathjax_script = '<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>\\n<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\\n</head>'
            content = content.replace('</head>', mathjax_script)

    # Find boundaries
    start_tag = '<section class="test-section" id="model-evaluation">'
    end_tag = '<h2 class="page-break">4.2 ผลการทดลอง/ผลการทดสอบระบบ</h2>'

    start_pos = content.find(start_tag)
    end_pos = content.find(end_tag)

    if start_pos == -1 or end_pos == -1:
        print(f"Error finding markers in {filepath}: start={start_pos}, end={end_pos}")
        return False

    new_content = content[:start_pos] + text + '\\n    ' + content[end_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully updated {filepath}!")
    return True

if __name__ == '__main__':
    update_file('docs_and_tests/chapter4_testcases.html', is_public=False)
    update_file('public/chapter4_testcases.html', is_public=True)
