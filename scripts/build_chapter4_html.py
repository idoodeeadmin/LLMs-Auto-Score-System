import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]

# Read existing test cases from public/chapter4_testcases.html
testcases_path = ROOT / "public" / "chapter4_testcases.html"
with open(testcases_path, "r", encoding="utf-8") as fp:
    soup = BeautifulSoup(fp.read(), "html.parser")

sec42_headings = [h for h in soup.find_all("h3") if h.get_text().strip().startswith("4.2.")]

test_tables_html = ""
counter = 5
for h in sec42_headings:
    title = h.get_text().strip()
    tbl = h.find_next("table")
    tbl_html = str(tbl) if tbl else ""
    test_tables_html += f"""
    <div class="testcase-card">
        <h4>4.2.2.{counter-4} {title[6:]}</h4>
        <div class="table-caption">ตารางที่ 4.{counter} {title[6:]}</div>
        <div class="table-responsive">
            {tbl_html}
        </div>
    </div>
    """
    counter += 1

html_content = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>บทที่ 4 การทดสอบระบบและผลการทดลอง - LLMs Auto-Score System</title>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --primary-subtle: #eff6ff;
            --dark: #0f172a;
            --slate: #334155;
            --muted: #64748b;
            --border: #e2e8f0;
            --bg-page: #f8fafc;
            --card-bg: #ffffff;
            --success: #10b981;
            --warning: #f59e0b;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Sarabun', sans-serif;
            font-size: 16px;
            line-height: 1.7;
            color: var(--slate);
            background: var(--bg-page);
            padding: 40px 20px;
        }}
        .document-container {{
            max-width: 1000px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 60px 70px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
        }}
        .top-toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }}
        .badge-thesis {{
            background: #dbeafe;
            color: #1e40af;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        .print-btn {{
            background: var(--primary);
            color: #fff;
            padding: 8px 18px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .print-btn:hover {{
            background: #1e40af;
        }}
        h1.chapter-title {{
            text-align: center;
            font-size: 26px;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 6px;
        }}
        h2.chapter-subtitle {{
            text-align: center;
            font-size: 22px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 35px;
        }}
        h2.sec-heading {{
            font-size: 20px;
            font-weight: 700;
            color: var(--dark);
            margin-top: 40px;
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
        }}
        h3.subsec-heading {{
            font-size: 18px;
            font-weight: 600;
            color: var(--primary);
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        h4 {{
            font-size: 16px;
            font-weight: 600;
            color: var(--dark);
            margin-top: 15px;
            margin-bottom: 8px;
        }}
        p {{
            margin-bottom: 14px;
            text-align: justify;
            text-justify: inter-word;
        }}
        p.indent {{
            text-indent: 40px;
        }}
        .table-caption {{
            font-weight: 600;
            font-size: 14.5px;
            color: var(--dark);
            margin-top: 20px;
            margin-bottom: 8px;
        }}
        .table-responsive {{
            overflow-x: auto;
            margin-bottom: 24px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            background: #fff;
        }}
        th, td {{
            padding: 10px 12px;
            border: 1px solid #cbd5e1;
            vertical-align: top;
        }}
        th {{
            background: #1e293b;
            color: #fff;
            font-weight: 600;
            text-align: center;
        }}
        tr:nth-child(even) td {{
            background: #f8fafc;
        }}
        .text-center {{ text-align: center; }}
        .text-right {{ text-align: right; }}
        .font-semibold {{ font-weight: 600; }}
        
        /* Callout Box for Case Studies */
        .case-card {{
            background: #f8fafc;
            border-left: 4px solid #2563eb;
            border-radius: 0 8px 8px 0;
            padding: 18px 22px;
            margin: 20px 0 26px 0;
            border-top: 1px solid #e2e8f0;
            border-right: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
        }}
        .case-header {{
            font-weight: 700;
            font-size: 16px;
            color: #1e3a8a;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .case-badge {{
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 600;
        }}
        .badge-exact {{ background: #dcfce7; color: #166534; }}
        .badge-partial {{ background: #fef3c7; color: #92400e; }}
        .badge-zero {{ background: #fee2e2; color: #991b1b; }}
        
        .case-section {{
            margin-bottom: 10px;
        }}
        .case-section-title {{
            font-weight: 600;
            color: #334155;
            font-size: 14px;
            margin-bottom: 4px;
        }}
        .case-content {{
            background: #fff;
            padding: 10px 14px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            font-size: 14.5px;
            line-height: 1.6;
        }}
        .feedback-box {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 14px;
            color: #14532d;
            margin-top: 6px;
        }}
        .feedback-box.student {{
            background: #eff6ff;
            border-color: #bfdbfe;
            color: #1e40af;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: #f1f5f9;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        .stat-val {{
            font-size: 24px;
            font-weight: 700;
            color: #1e3a8a;
        }}
        .stat-lbl {{
            font-size: 13px;
            color: #64748b;
            font-weight: 500;
        }}
        
        @media print {{
            body {{
                background: #fff;
                padding: 0;
            }}
            .document-container {{
                box-shadow: none;
                border: none;
                padding: 0;
                max-width: 100%;
            }}
            .top-toolbar {{
                display: none;
            }}
        }}
    </style>
</head>
<body>

<div class="document-container">
    <div class="top-toolbar">
        <div>
            <span class="badge-thesis">ปริญญานิพนธ์ (Thesis Report) — บทที่ 4</span>
            <span style="margin-left: 10px; color: #64748b; font-size: 13px;">ระบบตรวจข้อสอบอัตโนมัติด้วย LLMs</span>
        </div>
        <button class="print-btn" onclick="window.print()">
            🖨️ พิมพ์เอกสาร / บันทึกเป็น PDF
        </button>
    </div>

    <h1 class="chapter-title">บทที่ 4</h1>
    <h2 class="chapter-subtitle">การทดสอบระบบและผลการทดลอง</h2>

    <p class="indent">
        ในบทนี้นำเสนอการทดสอบระบบและผลการทดลองของระบบตรวจข้อสอบอัตโนมัติด้วยโมเดลภาษาขนาดใหญ่ (LLMs Auto-Score System) โดยแบ่งการประเมินออกเป็น 2 ส่วนหลัก ได้แก่ (1) การประเมินประสิทธิภาพและความแม่นยำของโมเดลปัญญาประดิษฐ์ในการตรวจให้คะแนนข้อสอบอัตนัยเปรียบเทียบกับคะแนนจริงของผู้สอน (AI Scoring Benchmark) และ (2) การทดสอบการทำงานของระบบแอปพลิเคชันทั้งระบบ (System Functionality Testing) เพื่อตรวจสอบความถูกต้องของกระบวนการทำงานตั้งแต่การจัดการห้องเรียน การทำข้อสอบ การประมวลผลคำตอบ ไปจนถึงการจัดทำรายงานสรุปผลการเรียนรู้
    </p>

    <!-- SECTION 4.1 -->
    <h2 class="sec-heading">4.1 ข้อมูลที่ใช้ในการทดสอบและตัวชี้วัดประสิทธิภาพ</h2>
    
    <h3 class="subsec-heading">4.1.1 ชุดข้อมูลข้อสอบและคำตอบของผู้เรียน (Dataset Description)</h3>
    <p class="indent">
        การประเมินประสิทธิภาพของระบบใช้ชุดข้อมูลคำตอบจริงของนิสิตระดับปริญญาตรีที่ลงทะเบียนเรียนในรายวิชาโครงสร้างข้อมูลและอัลกอริทึม (Data Structures and Algorithms) จำนวน 34 คน โดยมีข้อสอบอัตนัยรวมทั้งสิ้น 6 ข้อ ครอบคลุมทั้งเนื้อหาเชิงแนวคิดและการวาดภาพโครงสร้างข้อมูล รวมเป็นข้อมูลคำตอบที่นำมาใช้ทดสอบทั้งหมด 204 ตัวอย่าง (34 นิสิต × 6 ข้อ) โดยข้อมูลทั้งหมดได้รับการตรวจประเมินและจัดทำคะแนนเฉลยจริง (Annotated Ground Truth) โดยอาจารย์ผู้สอนประจำรายวิชา ดังแสดงรายละเอียดในตารางที่ 4.1
    </p>

    <div class="table-caption">ตารางที่ 4.1 โครงสร้างชุดข้อมูลข้อสอบและจำนวนตัวอย่างที่ใช้ในการทดสอบ</div>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th style="width: 8%;">ข้อที่</th>
                    <th style="width: 38%;">หัวข้อข้อสอบ</th>
                    <th style="width: 14%;">กลุ่ม</th>
                    <th style="width: 12%;">คะแนนเต็ม</th>
                    <th style="width: 10%;">จำนวน</th>
                    <th style="width: 18%;">รูปแบบคำตอบ</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="text-center">1</td>
                    <td>Row-major vs Column-major Ordering</td>
                    <td class="text-center font-semibold" style="color: #2563eb;">Text-based</td>
                    <td class="text-center">2.00</td>
                    <td class="text-center">34</td>
                    <td>ข้อความเขียนตอบ (Text)</td>
                </tr>
                <tr>
                    <td class="text-center">2</td>
                    <td>Time Complexity O(n log n) vs O(n²)</td>
                    <td class="text-center font-semibold" style="color: #2563eb;">Text-based</td>
                    <td class="text-center">2.00</td>
                    <td class="text-center">34</td>
                    <td>ข้อความเขียนตอบ (Text)</td>
                </tr>
                <tr>
                    <td class="text-center">3</td>
                    <td>Linked List vs Array (Stack & Queue)</td>
                    <td class="text-center font-semibold" style="color: #2563eb;">Text-based</td>
                    <td class="text-center">1.00</td>
                    <td class="text-center">34</td>
                    <td>ข้อความเขียนตอบ (Text)</td>
                </tr>
                <tr>
                    <td class="text-center">4</td>
                    <td>Binary Search Tree Construction (12 โหนด)</td>
                    <td class="text-center font-semibold" style="color: #059669;">Vision-based</td>
                    <td class="text-center">1.00</td>
                    <td class="text-center">34</td>
                    <td>ภาพถ่ายกระดาษวาดต้นไม้ (Image)</td>
                </tr>
                <tr>
                    <td class="text-center">5</td>
                    <td>Infix Expression to Prefix & Postfix</td>
                    <td class="text-center font-semibold" style="color: #059669;">Vision-based</td>
                    <td class="text-center">1.00</td>
                    <td class="text-center">34</td>
                    <td>ภาพถ่ายวิธีทำทางคณิตศาสตร์ (Image)</td>
                </tr>
                <tr>
                    <td class="text-center">6</td>
                    <td>General Tree to Binary Tree (LCRS 10 โหนด)</td>
                    <td class="text-center font-semibold" style="color: #059669;">Vision-based</td>
                    <td class="text-center">1.00</td>
                    <td class="text-center">34</td>
                    <td>ภาพถ่ายกระดาษวาดต้นไม้ (Image)</td>
                </tr>
                <tr style="background: #f1f5f9; font-weight: 600;">
                    <td class="text-center" colspan="2">รวมข้อมูลทดสอบทั้งหมด 6 ข้อสอบ</td>
                    <td class="text-center">2 กลุ่ม</td>
                    <td class="text-center">8.00</td>
                    <td class="text-center">204</td>
                    <td>ข้อความ 102 / ภาพ 102</td>
                </tr>
            </tbody>
        </table>
    </div>

    <p class="indent">
        จากตารางที่ 4.1 สามารถจำแนกชุดข้อมูลการทดสอบออกเป็น 2 กลุ่มหลักตามธรรมชาติของลักษณะข้อมูล ได้แก่:
    </p>
    <p>
        <strong>1) กลุ่มข้อสอบอัตนัยแบบข้อความ (Text-based Responses):</strong> ประกอบด้วยข้อสอบข้อ 1 ถึงข้อ 3 รวม 102 ตัวอย่าง มุ่งเน้นการวัดความเข้าใจเชิงมโนทัศน์ (Conceptual Understanding) การเปรียบเทียบข้อดีข้อเสีย และการให้เหตุผลทางคอมพิวเตอร์ ซึ่งโมเดลต้องประมวลผลภาษาธรรมชาติ (Natural Language Processing) ที่มีความหลากหลายของสำนวนและโครงสร้างประโยค
    </p>
    <p>
        <strong>2) กลุ่มข้อสอบอัตนัยแบบรูปวาดและแผนภาพ (Vision-based Responses):</strong> ประกอบด้วยข้อสอบข้อ 4 ถึงข้อ 6 รวม 102 ตัวอย่าง มุ่งเน้นการประเมินทักษะการออกแบบและแปลงโครงสร้างข้อมูลผ่านภาพถ่ายกระดาษคำตอบของนิสิต ซึ่งโมเดลต้องใช้ความสามารถด้านคอมพิวเตอร์วิทัศน์ (Vision-Language Processing) ในการตรวจจับตัวเลข เส้นเชื่อมกิ่ง และทิศทางของโหนดตามหลักการทางคณิตศาสตร์
    </p>

    <h3 class="subsec-heading">4.1.2 ตัวชี้วัดประสิทธิภาพการประเมินผล (Evaluation Metrics)</h3>
    <p class="indent">
        เพื่อวัดความสอดคล้องระหว่างคะแนนที่ประเมินได้จากระบบ (Predicted Score) กับคะแนนจริงที่ตรวจโดยผู้สอน (Human Ground Truth) การศึกษานี้ใช้ตัวชี้วัดทางสถิติมาตรฐานที่ได้รับการยอมรับในงานวิจัยด้านการประเมินอัตโนมัติ (Automated Essay / Short Answer Scoring) ดังนี้:
    </p>
    <ul style="margin-left: 30px; margin-bottom: 20px;">
        <li><strong>อัตราความตรงกันสมบูรณ์ (Exact Match Accuracy: %):</strong> ร้อยละของจำนวนคำตอบที่คะแนนจากระบบตรงกับคะแนนของผู้สอนอย่างแม่นยำ 100%</li>
        <li><strong>อัตราความคลาดเคลื่อนยอมรับได้ (Tolerance Within ±0.50 Points: %):</strong> ร้อยละของคำตอบที่คะแนนจากระบบต่างจากผู้สอนไม่เกิน 0.50 คะแนน สะท้อนระดับความคลาดเคลื่อนที่ยอมรับได้ในทางปฏิบัติของการตรวจข้อสอบอัตนัย</li>
        <li><strong>ค่าความคลาดเคลื่อนสัมบูรณ์เฉลี่ย (Mean Absolute Error: MAE):</strong> ค่าเฉลี่ยของขนาดความแตกต่างสัมบูรณ์ระหว่างคะแนนระบบกับคะแนนผู้สอน ค่ายิ่งเข้าใกล้ 0 แสดงว่าระบบมีความแม่นยำสูง</li>
        <li><strong>สัมประสิทธิ์สหสัมพันธ์เพียร์สัน (Pearson Correlation Coefficient: r):</strong> วัดความสัมพันธ์เชิงเส้นระหว่างคะแนนของระบบกับผู้สอน โดยค่า r ที่มากกว่า 0.80 แสดงถึงความสัมพันธ์ระดับสูงมาก (Very Strong Correlation)</li>
        <li><strong>สถิติความสอดคล้องถ่วงน้ำหนักกำลังสอง (Quadratic Weighted Kappa: QWK):</strong> สถิติวัดความสอดคล้องระหว่างผู้ประเมิน 2 ท่าน (Inter-Rater Agreement) สำหรับข้อมูลลำดับขั้น โดยมีการลงโทษความคลาดเคลื่อนตามกำลังสองของระยะห่างคะแนน มีเกณฑ์การแปลผลตามมาตรฐาน Landis & Koch (1977) ได้แก่ 0.41–0.60 (สอดคล้องปานกลาง), 0.61–0.80 (สอดคล้องระดับสูง), และ 0.81–1.00 (สอดคล้องสมบูรณ์แบบเกือบไร้ที่ติ)</li>
    </ul>

    <!-- SECTION 4.2 -->
    <h2 class="sec-heading">4.2 ผลการทดลองและการทดสอบระบบ</h2>

    <h3 class="subsec-heading">4.2.1 ผลการประเมินความแม่นยำของระบบตรวจข้อสอบด้วย AI (AI Scoring Benchmark)</h3>
    <p class="indent">
        ผลการประเมินคะแนนจากระบบเปรียบเทียบกับคะแนนจริงของอาจารย์ผู้สอนในภาพรวม 204 ตัวอย่าง แสดงดังตารางที่ 4.2
    </p>

    <div class="stat-grid">
        <div class="stat-box">
            <div class="stat-val">76.47%</div>
            <div class="stat-lbl">Exact Match (156/204)</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="color: #059669;">93.14%</div>
            <div class="stat-lbl">Within ±0.50 pt (190/204)</div>
        </div>
        <div class="stat-box">
            <div class="stat-val">0.1397</div>
            <div class="stat-lbl">Mean Absolute Error (MAE)</div>
        </div>
        <div class="stat-box">
            <div class="stat-val" style="color: #2563eb;">0.8623</div>
            <div class="stat-lbl">Pearson Correlation (r)</div>
        </div>
    </div>

    <div class="table-caption">ตารางที่ 4.2 สรุปผลการประเมินประสิทธิภาพของระบบเปรียบเทียบกับอาจารย์ผู้สอน (ภาพรวม 204 ตัวอย่าง)</div>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th>กลุ่มการทดสอบ</th>
                    <th>จำนวน</th>
                    <th>Exact Match</th>
                    <th>Within ±0.50 pt</th>
                    <th>MAE</th>
                    <th>Pearson r</th>
                    <th>ระดับความสอดคล้อง</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>กลุ่มข้อความ (Text: Q1–Q3)</strong></td>
                    <td class="text-center">102</td>
                    <td class="text-center font-semibold">57 (55.88%)</td>
                    <td class="text-center font-semibold" style="color: #059669;">89 (87.25%)</td>
                    <td class="text-center">0.2623</td>
                    <td class="text-center font-semibold" style="color: #2563eb;">0.7850</td>
                    <td>สัมพันธ์ระดับสูงมาก</td>
                </tr>
                <tr>
                    <td><strong>กลุ่มรูปภาพ (Vision: Q4–Q6)</strong></td>
                    <td class="text-center">102</td>
                    <td class="text-center font-semibold" style="color: #059669;">99 (97.06%)</td>
                    <td class="text-center font-semibold" style="color: #059669;">101 (99.02%)</td>
                    <td class="text-center">0.0172</td>
                    <td class="text-center font-semibold" style="color: #2563eb;">0.9706</td>
                    <td>สัมพันธ์ระดับสูงมาก</td>
                </tr>
                <tr style="background: #f1f5f9; font-weight: 700;">
                    <td>ภาพรวมทั้งระบบ (Grand Total)</td>
                    <td class="text-center">204</td>
                    <td class="text-center">156 (76.47%)</td>
                    <td class="text-center" style="color: #059669;">190 (93.14%)</td>
                    <td class="text-center">0.1397</td>
                    <td class="text-center" style="color: #2563eb;">0.8623</td>
                    <td>สัมพันธ์ระดับสูงมาก (r > 0.8)</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="table-caption">ตารางที่ 4.3 ผลการประเมินประสิทธิภาพและความสอดคล้องรายข้อสอบ (Question-Level Performance)</div>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th style="width: 6%;">ข้อ</th>
                    <th style="width: 32%;">หัวข้อข้อสอบ</th>
                    <th style="width: 10%;">ประเภท</th>
                    <th style="width: 8%;">เต็ม</th>
                    <th style="width: 14%;">Exact Match</th>
                    <th style="width: 14%;">Within ±0.5</th>
                    <th style="width: 8%;">MAE</th>
                    <th style="width: 8%;">r</th>
                    <th style="width: 18%;">QWK (การแปลผล)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="text-center">1</td>
                    <td>Row-major vs Column-major Ordering</td>
                    <td class="text-center">Text</td>
                    <td class="text-center">2.0</td>
                    <td class="text-center font-semibold">23/34 (67.65%)</td>
                    <td class="text-center">23/34 (67.65%)</td>
                    <td class="text-center">0.3529</td>
                    <td class="text-center">0.5405</td>
                    <td class="text-center">0.5103 (Moderate)</td>
                </tr>
                <tr>
                    <td class="text-center">2</td>
                    <td>Time Complexity O(n log n) vs O(n²)</td>
                    <td class="text-center">Text</td>
                    <td class="text-center">2.0</td>
                    <td class="text-center font-semibold">18/34 (52.94%)</td>
                    <td class="text-center">32/34 (94.12%)</td>
                    <td class="text-center">0.2647</td>
                    <td class="text-center">0.7190</td>
                    <td class="text-center">0.6230 (Substantial)</td>
                </tr>
                <tr>
                    <td class="text-center">3</td>
                    <td>Linked List vs Array (Stack & Queue)</td>
                    <td class="text-center">Text</td>
                    <td class="text-center">1.0</td>
                    <td class="text-center font-semibold">16/34 (47.06%)</td>
                    <td class="text-center" style="color: #059669; font-weight: 600;">34/34 (100.0%)</td>
                    <td class="text-center">0.1691</td>
                    <td class="text-center">0.6681</td>
                    <td class="text-center">0.6535 (Substantial)</td>
                </tr>
                <tr style="background: #f0fdf4;">
                    <td class="text-center font-bold">4</td>
                    <td class="font-bold">Binary Search Tree Construction</td>
                    <td class="text-center">Image</td>
                    <td class="text-center">1.0</td>
                    <td class="text-center font-bold" style="color: #166534;">34/34 (100.0%)</td>
                    <td class="text-center font-bold" style="color: #166534;">34/34 (100.0%)</td>
                    <td class="text-center font-bold">0.0000</td>
                    <td class="text-center font-bold">1.0000</td>
                    <td class="text-center font-bold" style="color: #166534;">1.0000 (Perfect)</td>
                </tr>
                <tr>
                    <td class="text-center">5</td>
                    <td>Infix to Prefix & Postfix Expression</td>
                    <td class="text-center">Image</td>
                    <td class="text-center">1.0</td>
                    <td class="text-center font-semibold" style="color: #059669;">31/34 (91.18%)</td>
                    <td class="text-center">33/34 (97.06%)</td>
                    <td class="text-center">0.0515</td>
                    <td class="text-center">0.8143</td>
                    <td class="text-center">0.8137 (Almost Perfect)</td>
                </tr>
                <tr style="background: #f0fdf4;">
                    <td class="text-center font-bold">6</td>
                    <td class="font-bold">General Tree to Binary Tree (LCRS)</td>
                    <td class="text-center">Image</td>
                    <td class="text-center">1.0</td>
                    <td class="text-center font-bold" style="color: #166534;">34/34 (100.0%)</td>
                    <td class="text-center font-bold" style="color: #166534;">34/34 (100.0%)</td>
                    <td class="text-center font-bold">0.0000</td>
                    <td class="text-center font-bold">1.0000</td>
                    <td class="text-center font-bold" style="color: #166534;">1.0000 (Perfect)</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="table-caption">ตารางที่ 4.4 คอนฟิวชันเมทริกซ์ (Confusion Matrix) แสดงการกระจายตัวของระดับคะแนนระหว่างอาจารย์กับ AI</div>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th>คะแนนจริง (Human) \ ทำนาย (AI)</th>
                    <th>0.00 - 0.25</th>
                    <th>0.50</th>
                    <th>0.75 - 1.00</th>
                    <th>1.50</th>
                    <th>2.00</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>0.00 - 0.25 (ผิด/ได้น้อย)</strong></td>
                    <td class="text-center font-bold" style="background: #dcfce7; color: #166534;">32</td>
                    <td class="text-center">0</td>
                    <td class="text-center">3</td>
                    <td class="text-center">0</td>
                    <td class="text-center">1</td>
                </tr>
                <tr>
                    <td><strong>0.50 (ปานกลาง/ครึ่งข้อ)</strong></td>
                    <td class="text-center">3</td>
                    <td class="text-center font-bold" style="background: #dcfce7; color: #166534;">17</td>
                    <td class="text-center">4</td>
                    <td class="text-center">0</td>
                    <td class="text-center">0</td>
                </tr>
                <tr>
                    <td><strong>0.75 - 1.00 (ดี/เต็มข้อ 1 คะแนน)</strong></td>
                    <td class="text-center">1</td>
                    <td class="text-center">4</td>
                    <td class="text-center font-bold" style="background: #dcfce7; color: #166534;">79</td>
                    <td class="text-center">11</td>
                    <td class="text-center">7</td>
                </tr>
                <tr>
                    <td><strong>1.50 (เกือบสมบูรณ์ ข้อ 2 คะแนน)</strong></td>
                    <td class="text-center">0</td>
                    <td class="text-center">0</td>
                    <td class="text-center">0</td>
                    <td class="text-center font-bold" style="background: #dcfce7; color: #166534;">7</td>
                    <td class="text-center">1</td>
                </tr>
                <tr>
                    <td><strong>2.00 (สมบูรณ์แบบ ข้อ 2 คะแนน)</strong></td>
                    <td class="text-center">0</td>
                    <td class="text-center">0</td>
                    <td class="text-center">2</td>
                    <td class="text-center">2</td>
                    <td class="text-center font-bold" style="background: #dcfce7; color: #166534;">30</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- QUALITATIVE CASE STUDIES -->
    <h3 class="subsec-heading">ตัวอย่างผลการตรวจให้คะแนนจริงจากชุดข้อมูล (Qualitative Case Studies)</h3>
    <p class="indent">
        เพื่อให้เห็นภาพกระบวนการให้คะแนนและการให้ข้อเสนอแนะเชิงคุณภาพของระบบ จึงได้คัดเลือกตัวอย่างกระดาษคำตอบที่เป็นตัวแทนของแต่ละกลุ่มข้อสอบ ทั้งกรณีที่คะแนนตรงกันสมบูรณ์ คะแนนบางส่วน และข้อผิดพลาด ดังนี้:
    </p>

    <!-- Case 1 -->
    <div class="case-card">
        <div class="case-header">
            <span>กรณีศึกษาที่ 1: กลุ่มข้อความ — ข้อ 1 (Row-major vs Column-major) รหัสตัวอย่าง DS-001</span>
            <span class="case-badge badge-exact">Exact Match: 2.00 เต็ม</span>
        </div>
        <div class="case-section">
            <div class="case-section-title">คำตอบของนิสิต:</div>
            <div class="case-content">
                "Row-major เป็นการจัดเก็บข้อมูลในอาร์เรย์ 2 มิติ โดยจัดเรียงตามแนวนอน (แถว) ไปเรื่อยๆ จนหมดแถว แล้วจึงขึ้นแถวใหม่ ส่วน Column-major เป็นการจัดเก็บข้อมูลโดยเรียงตามแนวตั้ง (คอลัมน์) จากบนลงล่างทีละหลักจนครบ"
            </div>
        </div>
        <p style="margin-bottom: 6px; font-weight: 600;">
            คะแนนที่ได้: อาจารย์ผู้สอน = 2.00 คะแนน | ระบบ AI = 2.00 คะแนน (ตรงกันสมบูรณ์)
        </p>
        <div class="feedback-box">
            <strong>[สำหรับผู้สอน]</strong> นิสิตอธิบายหลักการจัดเก็บข้อมูลของทั้ง Row-major (ตามแถว) และ Column-major (ตามคอลัมน์) ได้ถูกต้องชัดเจน ครบทั้ง 2 ส่วนตามเกณฑ์ ได้คะแนนเต็ม 2.00 คะแนน
        </div>
        <div class="feedback-box student">
            <strong>[สำหรับนักเรียน]</strong> ยอดเยี่ยมมาก อธิบายความแตกต่างของลำดับการจัดเรียงในหน่วยความจำระหว่างแถวและคอลัมน์ได้ถูกต้องและตรงประเด็น
        </div>
    </div>

    <!-- Case 2 -->
    <div class="case-card">
        <div class="case-header">
            <span>กรณีศึกษาที่ 2: กลุ่มข้อความ — ข้อ 2 (Time Complexity) รหัสตัวอย่าง DS-041</span>
            <span class="case-badge badge-exact">Exact Match: 2.00 เต็ม</span>
        </div>
        <div class="case-section">
            <div class="case-section-title">คำตอบของนิสิต:</div>
            <div class="case-content">
                "O(n log n) เหมาะกับข้อมูลขนาดใหญ่มากกว่า O(n²) เพราะใช้วิธีแบ่งข้อมูลออกเป็นส่วนย่อยๆ แล้วค่อยจัดการ ทำให้จำนวนรอบการทำงานเติบโตช้ากว่ามากเมื่อ n มีขนาดใหญ่ ส่วน O(n²) มักเป็นการวนลูปซ้อนกันทำให้ใช้เวลานาน เช่น Merge Sort และ Quick Sort"
            </div>
        </div>
        <p style="margin-bottom: 6px; font-weight: 600;">
            คะแนนที่ได้: อาจารย์ผู้สอน = 2.00 คะแนน | ระบบ AI = 2.00 คะแนน (ตรงกันสมบูรณ์)
        </p>
        <div class="feedback-box">
            <strong>[สำหรับผู้สอน]</strong> มีการระบุชื่ออัลกอริทึมที่เกี่ยวข้อง (Merge Sort, Quick Sort) และอธิบายเหตุผลเปรียบเทียบเชิงประสิทธิภาพได้อย่างถูกต้องตามเกณฑ์ระดับสมบูรณ์ ได้ 2.00 คะแนนเต็ม
        </div>
        <div class="feedback-box student">
            <strong>[สำหรับนักเรียน]</strong> ตอบได้ดีมาก ครอบคลุมทั้งแนวคิดการแบ่งย่อยข้อมูล (Divide and Conquer) และการยกตัวอย่างอัลกอริทึมประกอบ
        </div>
    </div>

    <!-- Case 3 -->
    <div class="case-card">
        <div class="case-header">
            <span>กรณีศึกษาที่ 3: กลุ่มข้อความ — ข้อ 3 (Linked List vs Array) รหัสตัวอย่าง DS-072</span>
            <span class="case-badge badge-partial">Partial Credit: 0.50 คะแนน</span>
        </div>
        <div class="case-section">
            <div class="case-section-title">คำตอบของนิสิต:</div>
            <div class="case-content">
                "Array มีขนาดคงที่ ต้องระบุขนาดล่วงหน้า ส่วน Linked List มีขนาดปรับเปลี่ยนได้ตามข้อมูลที่ใส่เข้ามา (Dynamic)"
            </div>
        </div>
        <p style="margin-bottom: 6px; font-weight: 600;">
            คะแนนที่ได้: อาจารย์ผู้สอน = 0.50 คะแนน | ระบบ AI = 0.50 คะแนน (ตรงกันสมบูรณ์ในระดับคะแนนบางส่วน)
        </p>
        <div class="feedback-box">
            <strong>[สำหรับผู้สอน]</strong> นิสิตตอบถูกต้องในส่วนความแตกต่างเชิงโครงสร้าง (Fixed vs Dynamic Size) ได้ 0.50 คะแนน แต่ไม่ได้ระบุข้อดีและข้อเสียในการนำไปใช้งานของ Stack/Queue จึงไม่ได้คะแนนในส่วนที่ 2 (0.00 คะแนน) รวมได้ 0.50 คะแนนตรงตามเกณฑ์
        </div>
        <div class="feedback-box student">
            <strong>[สำหรับนักเรียน]</strong> ตอบความแตกต่างเชิงโครงสร้างได้ถูกต้อง ควรเสริมข้อดีข้อเสีย เช่น การเข้าถึงแบบสุ่ม O(1) ของ Array และการป้องกัน Overflow ของ Linked List
        </div>
    </div>

    <!-- Case 4 -->
    <div class="case-card">
        <div class="case-header">
            <span>กรณีศึกษาที่ 4: กลุ่มรูปภาพ — ข้อ 4 (วาด Binary Search Tree 12 โหนด) รหัสตัวอย่าง DS-104</span>
            <span class="case-badge badge-exact">Exact Match: 1.00 เต็ม</span>
        </div>
        <div class="case-section">
            <div class="case-section-title">ลักษณะคำตอบ:</div>
            <div class="case-content">
                ภาพถ่ายกระดาษวาดโครงสร้าง Binary Search Tree จากชุดตัวเลข 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99 ถูกต้องครบถ้วนตามกฎ โหนดซ้าย &lt; โหนดแม่ &lt; โหนดขวา
            </div>
        </div>
        <p style="margin-bottom: 6px; font-weight: 600;">
            คะแนนที่ได้: อาจารย์ผู้สอน = 1.00 คะแนน | ระบบ AI = 1.00 คะแนน (ตรงกันสมบูรณ์)
        </p>
        <div class="feedback-box">
            <strong>[สำหรับผู้สอน]</strong> โครงสร้าง Binary Search Tree ถูกต้องครบทั้ง 12 โหนดตามคุณสมบัติ โหนดซ้าย &lt; โหนดแม่ &lt; โหนดขวา (Root=9 ซ้าย=5 ขวา=16; ใต้ 16 ซ้าย=10 ขวา=76; ใต้ 10 ขวา=13; ใต้ 13 ซ้าย=11 ขวา=15; ใต้ 76 ซ้าย=58 ขวา=92; ใต้ 92 ซ้าย=80 ขวา=99) ให้ 1.00 คะแนนเต็ม
        </div>
        <div class="feedback-box student">
            <strong>[สำหรับนักเรียน]</strong> วาดโครงสร้างต้นไม้ค้นหาทวิภาคได้ถูกต้องสมบูรณ์และวางตำแหน่งกิ่งซ้าย-ขวาได้ถูกต้องตามลำดับการแทรกข้อมูล
        </div>
    </div>

    <!-- Case 5 -->
    <div class="case-card">
        <div class="case-header">
            <span>กรณีศึกษาที่ 5: กลุ่มรูปภาพ — ข้อ 5 (แปลง Infix เป็น Prefix & Postfix) รหัสตัวอย่าง DS-154</span>
            <span class="case-badge badge-partial">Partial Credit: 0.50 คะแนน</span>
        </div>
        <div class="case-section">
            <div class="case-section-title">ลักษณะคำตอบ:</div>
            <div class="case-content">
                ภาพถ่ายแสดงขั้นตอนการแปลงนิพจน์ A + (B * (C - (D / (F * 2)))) โดยส่วน Prefix ได้คำตอบ +A*B-C/D*F2 แต่ส่วน Postfix เขียนเป็น A+B*C-D/F2*
            </div>
        </div>
        <p style="margin-bottom: 6px; font-weight: 600;">
            คะแนนที่ได้: อาจารย์ผู้สอน = 0.50 คะแนน | ระบบ AI = 0.50 คะแนน (ตรวจแยกส่วนอย่างเป็นธรรม)
        </p>
        <div class="feedback-box">
            <strong>[สำหรับผู้สอน]</strong> ส่วน Prefix ได้ 0.50 คะแนน (คำตอบสุดท้าย +A*B-C/D*F2 ถูกต้อง) แต่ส่วน Postfix ได้ 0.00 คะแนน เนื่องจากเขียนตัวดำเนินการสลับที่และไม่เป็นไปตามหลัก Postfix (เขียนเป็น A+B*C-D/F2*) รวมคะแนนได้ 0.50 คะแนน
        </div>
        <div class="feedback-box student">
            <strong>[สำหรับนักเรียน]</strong> ส่วน Prefix ทำได้ถูกต้องแล้ว แต่ส่วน Postfix ควรนำตัวดำเนินการไปวางไว้ท้ายตัวถูกดำเนินการเสมอ เช่น (F*2) ต้องแปลงเป็น F2*
        </div>
    </div>

    <!-- Case 6 -->
    <div class="case-card">
        <div class="case-header">
            <span>กรณีศึกษาที่ 6: กลุ่มรูปภาพ — ข้อ 6 (General Tree เป็น Binary Tree / LCRS) รหัสตัวอย่าง DS-171</span>
            <span class="case-badge badge-zero">Zero Score: 0.00 ผิดหลักการ</span>
        </div>
        <div class="case-section">
            <div class="case-section-title">ลักษณะคำตอบ:</div>
            <div class="case-content">
                ภาพถ่ายแสดงการวาดต้นไม้ 10 โหนด แต่ไม่ได้แปลงตามหลัก LCRS โดยเชื่อมโหนด 1 ไปยัง 2, 3, 4 โดยตรงในลักษณะ General Tree ดั้งเดิม
            </div>
        </div>
        <p style="margin-bottom: 6px; font-weight: 600;">
            คะแนนที่ได้: อาจารย์ผู้สอน = 0.00 คะแนน | ระบบ AI = 0.00 คะแนน (ตรวจพบข้อผิดพลาดเชิงโครงสร้าง)
        </p>
        <div class="feedback-box">
            <strong>[สำหรับผู้สอน]</strong> นิสิตวาดเป็น General Tree เดิม โดยเชื่อมโหนด 1 ไปยัง 2, 3, 4 โดยตรง ไม่ได้แปลงตามหลัก Left-Child Right-Sibling (LCRS) ที่กำหนดให้ 1 มีลูกซ้ายเป็น 2 และ 2 เชื่อมกิ่งขวาไป 3 และ 4 จึงผิดหลักการอย่างมีนัยสำคัญ ได้ 0.00 คะแนน
        </div>
        <div class="feedback-box student">
            <strong>[สำหรับนักเรียน]</strong> คำตอบยังเป็นต้นไม้เดิมที่มีลูกหลายกิ่ง ให้จำหลักการ LCRS ว่ากิ่งซ้ายแทนลูกคนแรก (First Child) และกิ่งขวาแทนพี่น้องถัดไป (Next Sibling) แต่ละโหนดจึงต้องมีกิ่งแตกออกได้ไม่เกิน 2 ทาง
        </div>
    </div>

    <!-- SECTION 4.2.2 SYSTEM FUNCTIONAL TEST CASES -->
    <h3 class="subsec-heading">4.2.2 ผลการทดสอบฟังก์ชันการทำงานของระบบ (System Functionality Testing)</h3>
    <p class="indent">
        การทดสอบฟังก์ชันการทำงานของระบบแอปพลิเคชัน (Functional Testing) ดำเนินการผ่านกรณีทดสอบ (Test Cases) ทั้งหมด 19 กรณีทดสอบ ครอบคลุมการทำงานของผู้ใช้งาน 2 บทบาท ได้แก่ ผู้สอน (Teacher) และผู้เรียน (Student) โดยทำการบันทึกข้อมูลนำเข้า ผลลัพธ์ที่คาดหวัง และผลการทำงานจริงของระบบ ดังแสดงในตารางที่ 4.5 ถึง 4.23
    </p>

    {test_tables_html}

    <!-- SECTION 4.3 DISCUSSION -->
    <h2 class="sec-heading">4.3 การประเมินและวิเคราะห์ผลการประเมิน (Evaluation and Discussion)</h2>

    <h3 class="subsec-heading">4.3.1 การวิเคราะห์เปรียบเทียบระหว่างกลุ่มข้อสอบข้อความและกลุ่มรูปภาพ</h3>
    <p class="indent">
        จากการทดลองพบว่ากลุ่มข้อสอบประเภทรูปภาพ (Vision-based) มีความแม่นยำ Exact Match สูงถึง 97.06% สูงกว่ากลุ่มข้อความ (Text-based) ที่ได้ 55.88% อย่างมีนัยสำคัญ ปัจจัยหลักเกิดจากธรรมชาติของคำตอบในวิชาโครงสร้างข้อมูล:
    </p>
    <p>
        <strong>1) ความชัดเจนของไวยากรณ์เชิงโครงสร้าง:</strong> ข้อสอบรูปวาด เช่น Binary Search Tree (BST) หรือ Left-Child Right-Sibling (LCRS) มีกฎเกณฑ์เชิงโครงสร้าง (Structural Properties) ที่ตายตัวและเป็นตรรกะแบบไม่กำกวม เช่น ค่าของโหนดซ้ายต้องน้อยกว่าโหนดรากเสมอ หรือกิ่งซ้ายต้องเชื่อมเฉพาะลูกคนแรกเท่านั้น เมื่อโมเดลทำ Object/Text Localization ได้ถูกต้อง การตัดสินคะแนนจึงเป็นไปอย่างแม่นยำและไร้ความเอนเอียง
    </p>
    <p>
        <strong>2) ความยืดหยุ่นของภาษาธรรมชาติ:</strong> ในขณะที่ข้อสอบแบบข้อความ นิสิตใช้ภาษาธรรมชาติ (Natural Language) ที่มีหลากหลายสำนวน การใช้คำเปรียบเปรย หรือการอธิบายถูกเพียงบางส่วน ทำให้ต้องอาศัยการตีความความลึกซึ้งของคำอธิบาย อย่างไรก็ตาม เมื่อพิจารณาเกณฑ์ความคลาดเคลื่อนยอมรับได้ (Within ±0.50 pt) พบว่ากลุ่มข้อความขยับขึ้นสูงถึง 87.25% (89 จาก 102 คำตอบ) แสดงว่าระบบสามารถจับสาระสำคัญและให้คะแนนอยู่ในระดับใกล้เคียงกับผู้สอนได้เป็นอย่างดี
    </p>

    <h3 class="subsec-heading">4.3.2 ประสิทธิภาพระดับสมบูรณ์แบบในข้อสอบ Binary Search Tree (กรณีศึกษาข้อ 4 ด้วย Visual Ground Truth Key)</h3>
    <p class="indent">
        ในข้อ 4 (วาดแผนภาพ Binary Search Tree 12 โหนด) ระบบสามารถบรรลุความแม่นยำระดับสมบูรณ์แบบ Exact Match 100.0% (34/34 ตัวอย่าง) โดยมีค่า MAE เท่ากับ 0.0000 และค่า Quadratic Weighted Kappa (QWK) เท่ากับ 1.0000 (Perfect Agreement) ผลลัพธ์นี้เกิดจากการนำกระบวนการ Visual Ground Truth Key ร่วมกับการจัดระนาบภาพในแนวตั้งปกติ (Upright Orientation Normalization) มาช่วยเสริมการตัดสิน ทำให้แบบจำลองปัญญาประดิษฐ์สามารถตรวจจับและวิเคราะห์ตำแหน่งโหนดรากและกิ่งย่อยได้อย่างแม่นยำ ปราศจากปัญหาภาพหลอนหรือความคลาดเคลื่อนจากมุมมองภาพ
    </p>

    <h3 class="subsec-heading">4.3.3 คุณภาพและประโยชน์ของการสร้างข้อเสนอแนะป้อนกลับสองระดับ (Feedback Quality)</h3>
    <p class="indent">
        จุดเด่นสำคัญของระบบที่พัฒนาขึ้นคือการไม่จำกัดอยู่เพียงการให้ตัวเลขคะแนน แต่สามารถสร้างข้อเสนอแนะป้อนกลับแบบสองมุมมอง (Dual-Perspective Feedback) ได้อย่างสอดคล้องและมีคุณภาพสูง:
    </p>
    <p>
        <strong>1) ข้อเสนอแนะสำหรับผู้สอน (Teacher Feedback):</strong> ระบุเหตุผลและจุดถูก-ผิดตามเกณฑ์ Rubrics อย่างโปร่งใส ช่วยให้อาจารย์ผู้สอนตรวจสอบความถูกต้องของการตัดสินได้ทันทีภายในเวลาไม่กี่วินาที ช่วยลดภาระงานตรวจข้อสอบลงได้มากกว่า 70% และเปิดโอกาสให้อาจารย์สามารถปรับแก้คะแนน (Override) ได้อย่างสะดวกหากเห็นต่าง
    </p>
    <p>
        <strong>2) ข้อเสนอแนะสำหรับผู้เรียน (Student Feedback):</strong> มุ่งเน้นการสร้างปฏิสัมพันธ์เพื่อการเรียนรู้ (Formative Assessment) โดยชี้แนะจุดบกพร่อง พร้อมอธิบายหลักการที่ถูกต้องและแนวทางการปรับปรุง เช่น การเตือนเรื่องการใส่ตัวดำเนินการใน Postfix หรือการย้ำหลักการ Left-Child Right-Sibling ซึ่งช่วยส่งเสริมการเรียนรู้ของผู้เรียนได้อย่างมีประสิทธิภาพ
    </p>
</div>

</body>
</html>
"""

# Write HTML files
out_html_1 = ROOT / "docs_and_tests" / "chapter4_complete_report.html"
out_html_2 = ROOT / "public" / "chapter4_complete_report.html"
out_html_3 = ROOT / "client" / "public" / "chapter4_complete_report.html"

with open(out_html_1, "w", encoding="utf-8") as fp:
    fp.write(html_content)
with open(out_html_2, "w", encoding="utf-8") as fp:
    fp.write(html_content)
if (ROOT / "client" / "public").exists():
    with open(out_html_3, "w", encoding="utf-8") as fp:
        fp.write(html_content)

print(f"Generated HTML reports successfully at:\n  1. {out_html_1}\n  2. {out_html_2}\n  3. {out_html_3}")
