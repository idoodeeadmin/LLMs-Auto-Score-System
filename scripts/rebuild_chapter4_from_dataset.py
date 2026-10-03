"""Build the chapter 4 HTML from the authoritative exam workbook.

The workbook is read only. Functional test results were confirmed as passed
by the project owner. Run from the repository root.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path
import re
import shutil

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"
OUTPUT = ROOT / "docs_and_tests" / "chapter4_testcases.html"
FULL_TESTCASES = ROOT / "docs_and_tests" / "partials" / "chapter4_full_testcases.html"

wb = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True)
samples = [
    row
    for row in wb["ชุดข้อสอบ_dataset"].iter_rows(min_row=6, values_only=True)
    if str(row[0]).startswith("DS-")
]
assert len(samples) == 204
assert all(isinstance(r[6], (int, float)) and isinstance(r[7], (int, float)) for r in samples)
by_id = {r[0]: r for r in samples}
rubrics = [r for r in wb["Exam_Rubrics"].values if isinstance(r[0], int)]
assert len(by_id) == len(samples) and len(rubrics) == 8


def score_stats(rows, normalized=False):
    pairs = [
        (r[6] / (2 if normalized and r[1] in (1, 2) else 1),
         r[7] / (2 if normalized and r[1] in (1, 2) else 1))
        for r in rows
    ]
    n = len(pairs)
    human = Counter(x for x, _ in pairs)
    ai = Counter(y for _, y in pairs)
    obs = sum((x - y) ** 2 for x, y in pairs) / n
    exp = sum(
        h_count * a_count * (x - y) ** 2
        for x, h_count in human.items()
        for y, a_count in ai.items()
    ) / n**2
    return {
        "n": n,
        "match": sum(x == y for x, y in pairs),
        "absolute": sum(abs(x - y) for x, y in pairs),
        "mae": sum(abs(x - y) for x, y in pairs) / n,
        "qwk": 1 - obs / exp,
        "observed": obs,
        "expected": exp,
        "within_half": sum(abs(x - y) <= 0.5 for x, y in pairs),
        "lower": sum(y < x for x, y in pairs),
        "higher": sum(y > x for x, y in pairs),
    }


overall = score_stats(samples)
overall_norm = score_stats(samples, normalized=True)
per_question = {q: score_stats([r for r in samples if r[1] == q]) for q in range(1, 7)}
per_type = {
    kind: score_stats([r for r in samples if r[4] == kind])
    for kind in ("text", "img")
}


def e(value):
    return escape(str(value)).replace("\n", "<br>")


tables = 0
figures = 0


def table(caption, headers, rows, cls=""):
    global tables
    tables += 1
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        f'<div class="table-block"><div class="table-title">ตารางที่ 4.{tables} {e(caption)}</div>'
        f'<table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    )


def figure(caption, source, alt, style=""):
    global figures
    figures += 1
    target = OUTPUT.parent / source
    assert target.is_file(), source
    return (
        f'<figure><img src="{e(source)}" alt="{e(alt)}" style="{style}">'
        f'<figcaption>ภาพประกอบที่ 4.{figures} {e(caption)}</figcaption></figure>'
    )


def score_removal_figure():
    global figures
    figures += 1
    before = "screenshots/case_studies/raw_score_case4.jpg"
    after = "screenshots/case_studies/case4_ds104.jpg"
    assert (OUTPUT.parent / before).is_file() and (OUTPUT.parent / after).is_file()
    return (
        '<figure><div class="score-comparison">'
        f'<div><div class="score-comparison-label">(ก) ก่อนลบรอยคะแนน</div><img src="{before}" alt="ภาพคำตอบของนักเรียนที่ยังมีรอยคะแนนผู้สอน"></div>'
        f'<div><div class="score-comparison-label">(ข) หลังลบรอยคะแนน</div><img src="{after}" alt="ภาพคำตอบของนักเรียนหลังลบรอยคะแนนผู้สอน"></div>'
        '</div>'
        f'<figcaption>ภาพประกอบที่ 4.{figures} ตัวอย่างการลบรอยคะแนนจากภาพคำตอบของนักเรียน</figcaption></figure>'
    )


def feedback(row):
    teacher = str(row[9] or "").split("[สำหรับนักเรียน]")[0]
    return teacher.replace("[สำหรับผู้สอน]", "").strip()


def example(sample_id, caption, image=None):
    r = by_id[sample_id]
    full = 2 if r[1] in (1, 2) else 1
    rows = [["รหัส / ข้อ", f"{sample_id} / ข้อ {r[1]}"]]
    if image:
        assert (OUTPUT.parent / image).is_file()
        rows.append(("ภาพคำตอบ", f'<img class="sample-image" src="{e(image)}" alt="ภาพคำตอบ {sample_id}">'))
    else:
        rows.append(("คำตอบผู้เรียน", e(r[5])))
    rows.extend([
        ("คะแนนผู้สอน", f"{r[6]:g} / {full} คะแนน"),
        ("คะแนนระบบ", f"{r[7]:g} / {full} คะแนน"),
        ("ผลต่าง", f"{abs(r[6] - r[7]):g} คะแนน"),
        ("คำอธิบายจาก AI", e(feedback(r))),
    ])
    return table(caption, ["รายการ", "ข้อมูลจากชุดทดสอบ"], rows, "example-table")


titles = [
    "Row-major กับ Column-major",
    "O(n log n) กับ O(n²)",
    "Linked List กับ Array",
    "การสร้าง Binary Search Tree",
    "Infix เป็น Prefix และ Postfix",
    "General Tree เป็น Binary Tree",
]

parts = [
    '<h1>บทที่ 4</h1><h1>ผลการทดลองและการทดสอบระบบ</h1>',
    '<p class="lead">บทนี้นำเสนอชุดข้อมูลและเกณฑ์ที่ใช้ประเมินระบบตรวจข้อสอบอัตนัยด้วย AI '
    'ผลการเปรียบเทียบคะแนนกับผู้สอน ตัวอย่างผลการตรวจ และกรณีทดสอบการทำงานของระบบ '
    'การรายงานผลคะแนนอ้างอิงข้อมูลที่บันทึกในไฟล์ ชุดข้อสอบ_dataset.xlsx</p>',
    '<h2>4.1 ข้อมูลที่ใช้ในการทดลอง</h2>',
    '<h3>4.1.1 ชุดคำตอบและรูปแบบข้อมูล</h3>',
    '<p>การทดลองใช้คำตอบจากข้อสอบวิชาโครงสร้างข้อมูล 6 ข้อ ข้อละ 34 คำตอบ รวม 204 คำตอบ '
    'คำตอบข้อ 1–3 เป็นข้อความ และข้อ 4–6 เป็นภาพลายมือ คะแนนอ้างอิงของผู้สอนและคะแนนจากระบบ '
    'จัดเก็บเป็นรายคำตอบในชีต ชุดข้อสอบ_dataset ส่วนเกณฑ์อยู่ในชีต Exam_Rubrics ของไฟล์เดียวกัน '
    'ตารางที่ 4.1 แสดงจำนวนและรูปแบบคำตอบ</p>',
]

parts.append(table(
    "องค์ประกอบของชุดข้อมูลที่ใช้ประเมิน",
    ["ข้อ", "เนื้อหา", "รูปแบบคำตอบ", "จำนวน", "คะแนนเต็ม"],
    [[str(q), e(titles[q - 1]), "ข้อความ" if q <= 3 else "ภาพ", "34", "2" if q <= 2 else "1"]
     for q in range(1, 7)]
    + [["รวม", "—", "ข้อความ 102 / ภาพ 102", "204", "—"]],
))
parts.append('<p>จากตารางที่ 4.1 จำนวนคำตอบของแต่ละข้อเท่ากัน จึงสามารถเปรียบเทียบอัตราคะแนนตรงกันรายข้อได้โดยตรง '
             'อย่างไรก็ตาม ข้อสอบแต่ละข้อวัดเนื้อหาและมีคะแนนเต็มต่างกัน การเปรียบเทียบขนาดความคลาดเคลื่อนจึงต้องดูคะแนนเต็มประกอบด้วย</p>')
parts.append(figure("ตัวอย่างคำตอบแบบข้อความในข้อ 1–3 หลังลบรอยคะแนนผู้ตรวจ", "screenshots/dataset_samples_text.png", "ภาพตัวอย่างคำตอบข้อความที่ลบรอยคะแนนแล้ว"))
parts.append(figure("ตัวอย่างคำตอบแบบภาพในข้อ 4–6 หลังลบรอยคะแนนผู้ตรวจ", "screenshots/dataset_samples_image.png", "ภาพตัวอย่างคำตอบภาพที่ลบรอยคะแนนแล้ว"))

parts.append('<p>การให้คะแนนใช้เกณฑ์รายข้อจากชีต Exam_Rubrics ในไฟล์ Excel ต้นฉบับ '
             'โดยใช้เกณฑ์เดียวกันกับคำตอบทุกรายการของข้อสอบแต่ละข้อ</p>')

parts.extend([
    '<h3>4.1.2 การเตรียมภาพคำตอบ</h3>',
    '<p>นำภาพคำตอบของนักเรียนมาลบรอยคะแนนที่ผู้สอนเขียนไว้ก่อนส่งให้ระบบตรวจ '
    'เพื่อให้ระบบประเมินจากคำตอบของนักเรียนโดยไม่เห็นคะแนนเดิม ตัวอย่างภาพก่อนและหลังลบรอยคะแนนแสดงในภาพประกอบที่ 4.3</p>',
])
parts.append(score_removal_figure())

parts.extend([
    '<h3>4.1.3 ขั้นตอนและตัวชี้วัดการประเมิน</h3>',
    '<p>สำหรับคำตอบแต่ละรายการ ระบบใช้โจทย์ คำตอบ คะแนนเต็ม แนวคำตอบและเกณฑ์รายข้อเพื่อสร้างคะแนน '
    'จากนั้นนำคะแนนที่บันทึกในคอลัมน์ ai_score มาเทียบกับ human_score '
    'การทดลองใช้คะแนนหนึ่งชุดต่อคำตอบ ไม่มีการนำผลทดลองเกณฑ์ฉบับอื่นมารวมในตารางผลนี้</p>',
    '<p>ใช้ตัวชี้วัดสามค่า ได้แก่ Exact Match ซึ่งนับคำตอบที่คะแนนตรงกันทุกทศนิยม, '
    'Mean Absolute Error (MAE) ซึ่งหาค่าเฉลี่ยของผลต่างคะแนนสัมบูรณ์ และ Quadratic Weighted Kappa (QWK) '
    'ซึ่งวัดความสอดคล้องโดยให้น้ำหนักมากขึ้นเมื่อคะแนนห่างกันมาก '
    'สำหรับ QWK ภาพรวม ปรับคะแนนแต่ละข้อด้วยคะแนนเต็มให้เป็นช่วง 0–1 ก่อนคำนวณ '
    'เพื่อไม่ให้ข้อที่เต็ม 2 คะแนนมีน้ำหนักของระยะห่างมากกว่าข้อที่เต็ม 1 คะแนนเพียงเพราะสเกลต่างกัน</p>',
    '<h2>4.2 ผลการทดลอง</h2>',
    '<h3>4.2.1 ผลการเปรียบเทียบคะแนนภาพรวม</h3>',
    '<p>ตารางที่ 4.2 แสดงผลการเปรียบเทียบคะแนนจากระบบกับคะแนนผู้สอนทั้งหมด 204 คำตอบ '
    'โดยคำนวณใหม่จากค่าคะแนนในชีต ชุดข้อสอบ_dataset</p>',
])
parts.append(table(
    "ผลการประเมินคะแนนภาพรวม",
    ["ตัวชี้วัด", "ผลการประเมิน"],
    [
        ["คะแนนตรงกัน", f"{overall['match']} จาก {overall['n']} คำตอบ ({overall['match']/overall['n']*100:.2f}%)"],
        ["MAE", f"{overall['mae']:.4f} คะแนน"],
        ["QWK หลังปรับคะแนนเป็นช่วง 0–1", f"{overall_norm['qwk']:.4f}"],
    ],
))
parts.append(
    f"<p>จากตารางที่ 4.2 คะแนนตรงกัน {overall['match']} คำตอบ หรือร้อยละ {overall['match']/204*100:.2f} "
    f"ค่า MAE เท่ากับ {overall['mae']:.4f} คะแนน และ QWK ภาพรวมหลังปรับสเกลเท่ากับ {overall_norm['qwk']:.4f} "
    "ผลดังกล่าวแสดงความสอดคล้องภายใต้ชุดข้อมูลที่ทดลอง แต่ยังมีรายการที่ผู้สอนควรตรวจทาน</p>"
)
parts.append(
    '<div class="formula"><strong>ตัวอย่างการคำนวณจากคะแนนจริง</strong><br>'
    f"Exact Match = {overall['match']} ÷ 204 × 100 = {overall['match']/204*100:.2f}%<br>"
    f"MAE = {overall['absolute']:.2f} ÷ 204 = {overall['mae']:.4f} คะแนน<br>"
    f"QWK = 1 − ({overall_norm['observed']:.6f} ÷ {overall_norm['expected']:.6f}) = {overall_norm['qwk']:.4f}"
    '</div>'
)

parts.extend([
    '<h3>4.2.2 ผลการประเมินรายข้อและตามรูปแบบคำตอบ</h3>',
    '<p>ตารางที่ 4.3 แสดงผลแยกตามข้อสอบเพื่อให้เห็นว่าระบบให้คะแนนสอดคล้องกับผู้สอนในโจทย์ประเภทใด '
    'ค่า MAE แสดงเป็นคะแนนดิบของแต่ละข้อ ส่วน QWK รายข้อคำนวณภายในข้อเดียวกัน</p>',
])
per_rows = []
for q in range(1, 7):
    d = per_question[q]
    per_rows.append([
        str(q), e(titles[q - 1]), "ข้อความ" if q <= 3 else "ภาพ", "34",
        f"{d['match']}/34 ({d['match']/34*100:.2f}%)",
        f"{d['mae']:.4f}", f"{d['qwk']:.4f}",
    ])
parts.append(table(
    "ผลการประเมินจำแนกรายข้อ",
    ["ข้อ", "เนื้อหา", "คำตอบ", "จำนวน", "คะแนนตรงกัน", "MAE", "QWK"],
    per_rows,
    "results",
))
perfect_questions = [str(q) for q, d in per_question.items() if d['match'] == d['n']]
lowest_match = min(d['match'] / d['n'] for d in per_question.values())
lowest_qwk = min(d['qwk'] for d in per_question.values())
lowest_match_questions = ' และ '.join(str(q) for q, d in per_question.items() if d['match'] / d['n'] == lowest_match)
lowest_qwk_questions = ' และ '.join(str(q) for q, d in per_question.items() if d['qwk'] == lowest_qwk)
parts.append(
    f"<p>จากตารางที่ 4.3 ข้อ {' และ '.join(perfect_questions)} ได้คะแนนตรงกันครบทุกคำตอบ "
    f"และข้อ 5 ตรงกัน {per_question[5]['match']} จาก {per_question[5]['n']} คำตอบ "
    f"ส่วนข้อ 1 ตรงกัน {per_question[1]['match']} จาก 34 คำตอบ ({per_question[1]['match']/34*100:.2f}%) "
    f"ข้อ {lowest_match_questions} มีอัตราคะแนนตรงกันต่ำที่สุด ขณะที่ข้อ {lowest_qwk_questions} มี QWK ต่ำที่สุด "
    "การดูทั้งสัดส่วนที่ตรงกัน MAE และ QWK ช่วยให้เห็นลักษณะความคลาดเคลื่อนที่ต่างกัน</p>"
)
type_rows = []
for kind, label in [("text", "ข้อความ (ข้อ 1–3)"), ("img", "ภาพลายมือ (ข้อ 4–6)")]:
    d = per_type[kind]
    type_rows.append([label, str(d["n"]), f"{d['match']} ({d['match']/d['n']*100:.2f}%)", f"{d['mae']:.4f}"])
parts.append(table("ผลการประเมินจำแนกตามรูปแบบคำตอบ", ["รูปแบบ", "จำนวน", "คะแนนตรงกัน", "MAE"], type_rows))
parts.append(
    "<p>กลุ่มภาพลายมือมีอัตราคะแนนตรงกันสูงกว่ากลุ่มข้อความในชุดทดสอบนี้ "
    "แต่ข้อสอบสองกลุ่มวัดเนื้อหาต่างกันและใช้เกณฑ์คนละแบบ "
    "ผลนี้จึงยังใช้สรุปไม่ได้ว่าโมเดลอ่านภาพได้ดีกว่าข้อความโดยทั่วไป</p>"
)

matrix = [[0] * 5 for _ in range(5)]
for r in samples:
    denominator = 2 if r[1] in (1, 2) else 1
    matrix[round(r[6] / denominator * 4)][round(r[7] / denominator * 4)] += 1
assert sum(sum(row) for row in matrix) == 204
parts.extend([
    '<h3>4.2.3 การกระจายของคู่คะแนน</h3>',
    '<p>ตารางที่ 4.5 แสดงจำนวนคู่คะแนนของผู้สอนและระบบในรูป Confusion Matrix '
    'โดยปรับคะแนนของแต่ละข้อด้วยคะแนนเต็มเป็นระดับ 0, 0.25, 0.50, 0.75 และ 1.00 '
    'แถวแทนคะแนนผู้สอน คอลัมน์แทนคะแนนระบบ ช่องแนวทแยงคือคะแนนที่ตรงกัน</p>',
])
matrix_rows = []
for i, row in enumerate(matrix):
    values = [f"{i/4:.2f}"]
    for j, value in enumerate(row):
        alpha = 0 if value == 0 else 0.09 + 0.58 * value / max(max(x) for x in matrix)
        css = f"background:rgba(36,95,110,{alpha:.3f});"
        if i == j:
            css += "box-shadow:inset 0 0 0 1.5px #15513f;font-weight:bold;"
        values.append(f'<span class="heat" style="{css}">{value}</span>')
    matrix_rows.append(values)
parts.append(table(
    "Confusion Matrix ของคะแนนที่ปรับเป็นช่วง 0–1",
    ["ผู้สอน \\ ระบบ", "0.00", "0.25", "0.50", "0.75", "1.00"], matrix_rows, "matrix",
))
parts.append(
    f"<p>จากตารางที่ 4.5 ค่าแนวทแยงรวม {overall['match']} คำตอบ "
    f"อีก {204-overall['match']} คำตอบมีคะแนนต่างจากผู้สอน "
    f"โดยระบบให้ต่ำกว่า {overall['lower']} คำตอบและให้สูงกว่า {overall['higher']} คำตอบ "
    "ความเข้มสีแสดงจำนวนรายการในแต่ละคู่คะแนน</p>"
)

parts.extend([
    '<h3>4.2.4 ตัวอย่างผลการตรวจคำตอบ</h3>',
    '<p>ตัวอย่างต่อไปนี้นำคำตอบและคะแนนจริงจากชุดทดสอบมาแสดงในรูปแบบเดียวกับการนำภาพ '
    'ผลเฉลย และผลทำนายมาเปรียบเทียบในเอกสารอ้างอิง โดยเลือกทั้งกรณีที่คะแนนตรงกันและต่างกัน '
    'คำอธิบายที่ยกมาคือข้อความจาก AI ใน Excel ไม่ใช่เหตุผลการให้คะแนนของผู้สอน</p>',
])
parts.append(example("DS-007", "คำตอบข้อ 1 ที่ผู้สอนและระบบให้ 1 คะแนน"))
parts.append(
    '<p>จากตารางที่ 4.6 คำตอบ DS-007 ระบุลักษณะของแถวและคอลัมน์ในระดับเบื้องต้น '
    'คะแนนจากระบบตรงกับคะแนนผู้สอนที่ 1 คะแนนตามข้อมูลล่าสุดใน Excel</p>'
)
parts.append(example("DS-025", "คำตอบข้อ 1 ที่ระบบให้สูงกว่าผู้สอน"))
parts.append(
    '<p>จากตารางที่ 4.7 DS-025 กล่าวถึงแนวนอนและแนวตั้งเช่นเดียวกัน และเพิ่มว่าทั้งสองแบบคำนวณไม่เหมือนกัน '
    'ผู้สอนให้ 1 คะแนน แต่ระบบให้ 2 คะแนน แม้เกณฑ์ภาพรวมเปิดให้ 1 คะแนนสำหรับความเข้าใจเบื้องต้น '
    'คำอธิบายของ AI ตีความคำตอบนี้ว่าอธิบายการจัดเรียงครบสองส่วน จึงเป็นกรณีที่ควรให้ผู้สอนพิจารณาคะแนนก่อนยืนยัน</p>'
)
parts.append(example("DS-154", "คำตอบภาพข้อ 5 ที่ได้คะแนนบางส่วน", "screenshots/case_studies/case5_ds154.jpg"))
parts.append(
    '<p>จากตารางที่ 4.8 ผู้สอนและระบบให้ 0.50 จาก 1 คะแนนตรงกัน โดยคำอธิบายจากระบบระบุว่า '
    'ส่วน Prefix ถูกต้อง ส่วน Postfix ยังไม่ถูกต้อง ภาพแสดงวิธีทำที่ใช้ประกอบการตัดสินคะแนนบางส่วน</p>'
)
parts.append(example("DS-171", "คำตอบภาพข้อ 6 ที่ได้ 0 คะแนน", "screenshots/case_studies/case6_ds171.jpg"))
parts.append(
    '<p>จากตารางที่ 4.9 ผู้สอนและระบบให้ 0 คะแนนตรงกัน โดยคำอธิบายของ AI ระบุว่า '
    'คำตอบยังไม่แสดงการแปลงเป็น Binary Tree ตามหลัก Left-Child Right-Sibling</p>'
)

parts.append(
    '<p>สำหรับข้อ 3 เลือกเปรียบเทียบคำตอบ DS-084 และ DS-088 ซึ่งกล่าวถึงความยืดหยุ่นด้านขนาด '
    'ความสะดวกในการเพิ่มและลบข้อมูล และข้อจำกัดด้านการเข้าถึงข้อมูลของ Linked List เมื่อเทียบกับ Array '
    'ทั้งสองคำตอบมีประเด็นหลักใกล้เคียงกัน แต่ได้รับคะแนนจากผู้สอนต่างกัน ดังตารางที่ 4.10</p>'
)
comparison_ids = ('DS-084', 'DS-088')
comparison_samples = [by_id[sample_id] for sample_id in comparison_ids]
assert comparison_samples[0][3] == comparison_samples[1][3]
comparison_feedback = []
for row in comparison_samples:
    full_feedback = feedback(row)
    if 'อย่างไรก็ตาม' in full_feedback:
        excerpt = 'อย่างไรก็ตาม ' + full_feedback.split('อย่างไรก็ตาม', 1)[1].split('นอกจากนี้', 1)[0].strip()
    else:
        excerpt = full_feedback
    comparison_feedback.append(e(excerpt))
parts.append(table(
    'ตัวอย่างคำตอบข้อ 3 ที่มีประเด็นใกล้เคียงกันแต่คะแนนผู้สอนต่างกัน',
    ['รายการ', *comparison_ids],
    [
        ['โจทย์ข้อ 3 (เต็ม 1 คะแนน)', e(comparison_samples[0][3])],
        ['คำตอบผู้เรียน', *[e(row[5]) for row in comparison_samples]],
        ['คะแนนผู้สอน (เต็ม 1)', *[f'{row[6]:.2f}' for row in comparison_samples]],
        ['คะแนนระบบ (เต็ม 1)', *[f'{row[7]:.2f}' for row in comparison_samples]],
        ['คำอธิบาย AI (ข้อความบางส่วน)', *comparison_feedback],
    ],
    'comparison-table',
))
parts[-1] = parts[-1].replace(
    '<td>' + e(comparison_samples[0][3]) + '</td>',
    '<td colspan="2">' + e(comparison_samples[0][3]) + '</td>',
    1,
)
parts.append(
    f'<p>จากตารางที่ 4.10 ผู้สอนให้ DS-084 เท่ากับ {comparison_samples[0][6]:.2f} คะแนน '
    f'และ DS-088 เท่ากับ {comparison_samples[1][6]:.2f} คะแนน '
    f'ขณะที่ระบบให้ {comparison_samples[0][7]:.2f} และ {comparison_samples[1][7]:.2f} คะแนนตามลำดับ '
    'คำอธิบายของ AI ในทั้งสองกรณีระบุว่ายังขาดการแจกแจงข้อดีและข้อเสียของ Array อย่างชัดเจน '
    'คู่นี้จึงแสดงตัวอย่างความแตกต่างของคะแนนอ้างอิงสำหรับคำตอบที่มีสาระใกล้เคียงกัน '
    'อย่างไรก็ตาม ชุดข้อมูลไม่มีเหตุผลการให้คะแนนรายคำตอบจากผู้สอน จึงยังระบุสาเหตุของความแตกต่างดังกล่าวไม่ได้</p>'
)

# Restore the complete 19-section functional test cases, including their original
# input, expected-result, observed-result, and test-status rows.
full_testcases = FULL_TESTCASES.read_text(encoding="utf-8")
assert full_testcases.count('<section class="test-section"') == 19
# Keep all test-case table references continuous when evaluation examples are added.
test_table_numbers = list(dict.fromkeys(re.findall(r'ตารางที่ 4\.(\d+)', full_testcases)))
test_table_map = {old: str(tables + offset) for offset, old in enumerate(test_table_numbers, 1)}
full_testcases = re.sub(r'ตารางที่ 4\.(\d+)', lambda match: 'ตารางที่ 4.' + test_table_map[match.group(1)], full_testcases)
parts.append(full_testcases)
tables += len(set(re.findall(r"ตารางที่ 4\.(\d+)", full_testcases)))
figures += len(set(re.findall(r"ภาพประกอบที่ 4\.(\d+)", full_testcases)))

parts.extend([
    '<h2>4.4 การประเมินและวิเคราะห์ผล</h2>',
    f"<p>ผลการเปรียบเทียบคะแนน {overall['n']} คำตอบพบว่าคะแนนจากระบบตรงกับผู้สอน "
    f"ร้อยละ {overall['match']/overall['n']*100:.2f} ค่า MAE เท่ากับ {overall['mae']:.4f} คะแนน "
    f"และ QWK ภาพรวมหลังปรับช่วงคะแนนเท่ากับ {overall_norm['qwk']:.4f} "
    "ตัวอย่างข้อ 5 และข้อ 6 แสดงกรณีที่ระบบให้คะแนนตรงกับผู้สอนทั้งคะแนนบางส่วนและศูนย์คะแนน "
    "ขณะที่ตัวอย่างข้อ 1 แสดงความต่างจากการตีความข้อความสั้น ผู้สอนจึงยังมีบทบาทตรวจทานคะแนน "
    "โดยเฉพาะคำตอบที่มีความกำกวมหรือคำอธิบายของระบบไม่สอดคล้องกับเกณฑ์</p>",
    '<p>การทดลองนี้ใช้ข้อสอบรายวิชาเดียว 6 ข้อและคะแนนอ้างอิงจากผู้สอนหนึ่งคน '
    'ผลจึงอธิบายความสอดคล้องของคะแนนในชุดข้อมูลนี้ การประเมินใช้ผลคะแนนหนึ่งชุดต่อคำตอบ '
    'ยังไม่ได้ตรวจความคงที่เมื่อประมวลผลซ้ำ ส่วนการทดสอบการทำงานในหัวข้อ 4.3 '
    'ผ่านทุกกรณีที่กำหนด โดยครอบคลุมทั้งข้อมูลที่ถูกต้องและการจัดการข้อมูลที่ไม่เป็นไปตามเงื่อนไข '
    'ผลดังกล่าวไม่ใช่การวัดระยะเวลาหรือต้นทุนในการตรวจข้อสอบ</p>',
])

chapter5 = (ROOT / 'docs_and_tests/partials/chapter5_appendices.html').read_text(encoding='utf-8')
chapter5 = chapter5.replace('156 รายการ คิดเป็นร้อยละ 76.47',
    f"{overall['match']} รายการ คิดเป็นร้อยละ {overall['match']/overall['n']*100:.2f}")
chapter5 = chapter5.replace('0.1397 คะแนน', f"{overall['mae']:.4f} คะแนน")
chapter5 = chapter5.replace('เท่ากับ 0.8534', f"เท่ากับ {overall_norm['qwk']:.4f}")
parts.append(chapter5)

css = """
@page { size: A4; margin: 21mm 19mm 20mm 23mm; }
* { box-sizing: border-box; }
html { background: #ddd; }
body { margin: 0; color: #111; font: 18px/1.4 'TH Sarabun New','Sarabun',Tahoma,sans-serif; }
.toolbar { background: #202124; color: white; padding: 9px; text-align: center; font: 13px Tahoma,sans-serif; }
.toolbar button { margin-right: 10px; padding: 7px 12px; }
.document { width: 210mm; margin: 14px auto 25px; padding: 21mm 19mm 20mm 23mm; background: white; box-shadow: 0 1px 9px #777; }
h1 { margin: 0; text-align: center; font-size: 24px; line-height: 1.25; }
.chapter-start { break-before: page; margin-top: 45px; }
.appendix-divider { break-before: page; break-after: page; min-height: 180mm; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.manual-section { break-before: page; }
.manual-section ol { margin-top: 6px; padding-left: 28px; }
.manual-section li { margin-bottom: 7px; }
.toolbar a { color: white; margin: 0 12px; }
@media print { .chapter-start { margin-top: 0; } }
h2 { margin: 24px 0 8px; font-size: 21px; }
h3 { margin: 20px 0 6px; font-size: 19px; }
h1,h2,h3,.table-title { break-after: avoid; page-break-after: avoid; }
p { margin: 0 0 9px; text-indent: 1.1cm; text-align: justify; }
.lead { margin-top: 22px; }
.table-block { margin: 11px 0 15px; }
.table-title { margin-bottom: 4px; }
table { width: 100%; border-collapse: collapse; font: 16px/1.28 'TH Sarabun New','Sarabun',Tahoma,sans-serif; }
th,td { border: 1px solid #333; padding: 5px 6px; vertical-align: top; overflow-wrap: anywhere; }
th { background: #dedede; text-align: center; }
thead { display: table-header-group; }
.results { font-size: 15px; }
.results td:first-child, .results td:nth-child(3) { text-align:center; }
.example-table td:first-child { width: 26%; font-weight: bold; background: #f3f3f3; }
.comparison-table { table-layout: fixed; }
.comparison-table th:first-child { width: 20%; }
.comparison-table td:first-child { font-weight: bold; background: #f3f3f3; }
.sample-image { max-width: 100%; max-height: 116mm; display:block; margin: auto; object-fit:contain; }
.matrix { table-layout: fixed; text-align: center; }
.matrix td { padding: 0; }
.heat { display: block; padding: 5px 0; }
.test-overview { font-size: 14px; }
.test-overview td:first-child { width: 7%; text-align:center; }
.test-overview td:nth-child(2) { width: 24%; }
.test-overview td:last-child { width: 13%; }
.test-section { margin-top: 20px; }
.test-section h3 { margin-bottom: 4px; }
.test-section .scope { text-indent: 0; color: #444; font-size: 16px; margin-bottom: 6px; }
.test-section table { table-layout: fixed; }
.test-section td:first-child { width: 22%; background: #dedede; font-weight: 600; }
.test-section .case { width: 26%; }
.test-section .case-4 { width: 20.5%; }
.test-section .figure { margin: 12px auto; text-align: center; break-inside: avoid; }
.test-section .figure img { display: block; max-width: 80%; max-height: 105mm; margin: auto; object-fit: contain; }
.test-section .caption { margin-top: 5px; font-size: 16px; }
.signature { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 20px; text-align: center; font-size: 16px; }
.signature div { border-top: 1px dotted #555; padding-top: 4px; }
.formula { margin: 12px 0 17px 1.1cm; padding: 6px 0 6px 12px; border-left: 2px solid #777; font-size: 16px; }
figure { margin: 14px auto 17px; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 105mm; object-fit: contain; }
.score-comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; text-align: center; }
.score-comparison-label { font-size: 14px; margin-bottom: 5px; }
.score-comparison img { width: 100%; height: 68mm; object-fit: contain; }
figcaption { font-size: 16px; margin-top: 4px; }
a { color: #164f69; }
@media print {
  html,body { background:white; }
  .toolbar { display:none; }
  .document { width:auto; margin:0; padding:0; box-shadow:none; }
  th,.heat { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  tr,figure { break-inside:avoid; }
}
@media screen and (max-width:840px) {
  .document { width:100%; padding:22px 16px; }
  table { font-size:14px; }
  body { font-size:17px; }
}
"""

html = (
    '<!doctype html><html lang="th"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>บทที่ 4–5 และภาคผนวก — ระบบตรวจข้อสอบอัตนัยด้วย LLMs</title>'
    f'<style>{css}</style></head><body>'
    '<div class="toolbar"><button onclick="window.print()">พิมพ์ / บันทึกเป็น PDF</button>'
    '<a href="#chapter5">บทที่ 5</a><a href="#appendix-a">ภาคผนวก ก</a><a href="#appendix-b">ภาคผนวก ข</a></div>'
    '<main class="document">' + "\n".join(parts) + '</main></body></html>'
)

backup = ROOT / "tmp" / f"chapter4_before_rewrite_{datetime.now():%Y%m%d_%H%M%S}.html"
backup.parent.mkdir(exist_ok=True)
shutil.copy2(OUTPUT, backup)
OUTPUT.write_text(html, encoding="utf-8")
print(
    f"Wrote {OUTPUT}, backup {backup}, tables={tables}, figures={figures}, "
    f"matches={overall['match']}/204, q1={per_question[1]['match']}/34, QWK={overall_norm['qwk']:.4f}"
)
