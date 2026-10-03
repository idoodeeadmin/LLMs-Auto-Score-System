"""Create a visual audit of corrected Q2/Q3 answer transcriptions."""

import html
import json
from pathlib import Path

import openpyxl

root = Path(__file__).resolve().parents[1]
out_dir = root / "docs_and_tests/q2_q3_review"
updates = json.loads((out_dir / "corrections.json").read_text(encoding="utf-8"))
before = openpyxl.load_workbook(root / "ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset_before_q2_q3_text_fixes.xlsx", read_only=True, data_only=True)
sheet = before["ชุดข้อสอบ_dataset"]
images = {51: "IMG_2859.jpg", 55: "IMG_2863.jpg", 57: "IMG_2866.jpg", 89: "IMG_2914.jpg", 101: "IMG_2926.jpg"}
parts = ['''<!doctype html><html lang="th"><meta charset="utf-8"><title>ตรวจคำตอบข้อ 2–3</title>
<style>body{font:16px Tahoma,sans-serif;max-width:1250px;margin:auto;background:#f4f7f6;color:#142824}h1{margin:30px 0}article{background:white;margin:20px 0;padding:20px;border-radius:12px}section{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{max-width:100%;max-height:750px;object-fit:contain}pre{white-space:pre-wrap;font:15px Tahoma,sans-serif;background:#f8faf9;padding:12px}</style>
<h1>คำตอบข้อ 2–3 ที่แก้ให้ตรงกับภาพ</h1><p>ตรวจภาพครบ 68 คู่ พบ 5 แถวที่ข้อความเดิมคลาดเคลื่อนจากภาพชัดเจน คะแนน AI เดิมยังไม่ได้ตรวจซ้ำ</p>''']
for number, filename in images.items():
    question = 2 if number < 69 else 3
    image = f"../../ชุดข้อสอบใหม่/photo_clean_text{question}/{filename}"
    old = html.escape(str(sheet.cell(number + 5, 6).value))
    new = html.escape(updates[str(number)])
    parts.append(f'<article><h2>DS-{number:03d} · ข้อ {question}</h2><section><div><img src="{image}"></div><div><h3>ข้อความเดิม</h3><pre>{old}</pre><h3>ข้อความที่แก้</h3><pre>{new}</pre></div></section></article>')
parts.append("</html>")
(out_dir / "correction_review.html").write_text("".join(parts), encoding="utf-8")
before.close()
