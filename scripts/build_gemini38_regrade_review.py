"""Render the completed Gemini regrade as a local review page."""

import html
import json
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs_and_tests/gemini38_regrade"
report = json.loads((FOLDER / "all_204_results.json").read_text(encoding="utf-8"))
assert len(report["results"]) == 204 and all(x["success"] for x in report["results"])
book = openpyxl.load_workbook(ROOT / "ชุดข้อสอบใหม่/ชุดข้อสอบ_dataset.xlsx", read_only=True, data_only=True)
source = book["ชุดข้อสอบ_dataset"]


def esc(value):
    return html.escape(str(value if value is not None else ""))


summaries = []
for q in range(1, 7):
    s = report["summary"][str(q)]
    summaries.append(f"<tr><td>{q}</td><td>{s['exact']}/34</td><td>{s['exact']/34*100:.2f}%</td>"
                     f"<td>{s['mae']:.4f}</td><td>{s['changed_from_previous_ai']}</td></tr>")

rows = []
for item in report["results"]:
    result = item["result"]
    differs = item["human_score"] != result["score"]
    images = []
    for label, entry in item["image_inputs"].items():
        src = "../../" + entry["path"].replace("\\", "/")
        images.append(f'<figure><figcaption>{esc(label)}</figcaption><img loading="lazy" src="{esc(src)}"></figure>')
    answer_text = source.cell(item["row"], 6).value if item["answer_type"] == "text" else ""
    answer = "" if item["answer_type"] == "img" else f'<p><b>คำตอบใน Excel</b></p><pre>{esc(answer_text)}</pre>'
    rows.append(f'''<tr data-q="{item['question_no']}" data-diff="{int(differs)}"><td>{esc(item['sample_id'])}</td>
      <td>{item['question_no']}</td><td>{item['human_score']:.2f}</td><td>{result['score']:.2f}</td>
      <td>{item['previous_ai_score']:.2f}</td><td>{esc(result['confidence'])}</td>
      <td><details><summary>ดูคำตอบและ feedback</summary><div class="detail">{answer}
      <div class="images">{''.join(images)}</div>
      <p><b>เหตุผลสำหรับผู้สอน</b></p><pre>{esc(result['teacher_feedback'])}</pre>
      <p><b>คำแนะนำสำหรับนักเรียน</b></p><pre>{esc(result['student_feedback'])}</pre>
      </div></details></td></tr>''')

page = f'''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ผลตรวจใหม่ด้วย Gemini 3.8 Flash — 204 คำตอบ</title>
<style>body{{font-family:system-ui,'Segoe UI',sans-serif;background:#f4f7f6;color:#18362d;margin:0}}
header{{background:#fff;padding:24px;border-bottom:1px solid #d7e3dd}}h1{{font-size:25px;margin:0 0 8px}}p{{line-height:1.55}}
main{{max-width:1400px;margin:auto;padding:18px}}.card{{background:#fff;border:1px solid #d7e3dd;border-radius:12px;padding:16px;margin-bottom:18px;overflow:auto}}
table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #e2eae6;padding:10px;text-align:left;vertical-align:top}}th{{background:#eaf2ee;white-space:nowrap}}
pre{{white-space:pre-wrap;font:14px/1.55 system-ui,'Segoe UI',sans-serif}}select,label{{font:inherit}}select{{padding:6px;margin:0 16px 10px 5px}}
summary{{cursor:pointer;color:#086247}}.detail{{min-width:350px;max-width:650px;padding:10px;background:#f8faf9}}.images{{display:flex;gap:12px;overflow:auto}}
figure{{margin:0;min-width:230px}}figcaption{{font-size:12px;color:#63776c}}img{{max-width:300px;max-height:350px;object-fit:contain}}</style>
<header><h1>ผลตรวจใหม่ด้วย Gemini 3.8 Flash</h1><p>ตรวจครบ 204 คำตอบด้วยเกณฑ์จาก Excel และแม่แบบระบบจริง · ข้อ 1–3 ใช้ข้อความ · ข้อ 4–6 ใช้ภาพคำตอบสะอาด · คะแนนผู้สอนไม่ถูกส่งให้โมเดล</p>
<p><b>ข้อ 4:</b> ส่งภาพคำตอบพร้อม <a href="../../public/answer-keys/q4_bst_ground_truth.png" target="_blank">ภาพแนวคำตอบ BST</a> ให้ Gemini ครบทั้ง 34 รายการแล้ว แต่โมเดลยังอ่านตำแหน่งกิ่งผิดในหลายภาพ จึงควรตรวจผลรายภาพ</p>
<p><b>หมายเหตุ:</b> ผลนี้เป็นการทดลองแยกต่างหาก ยังไม่ได้เขียนทับคะแนนเดิมใน Excel</p></header>
<main><section class="card"><h2>สรุปรายข้อ</h2><table><tr><th>ข้อ</th><th>ตรงกับผู้สอน</th><th>Exact Match</th><th>MAE</th><th>เปลี่ยนจากคะแนน AI เดิม</th></tr>{''.join(summaries)}</table></section>
<section class="card"><h2>ผลรายคำตอบ</h2><label>ข้อ <select id="q"><option value="all">ทั้งหมด</option>{''.join(f'<option value="{q}">{q}</option>' for q in range(1,7))}</select></label>
<label>คะแนน <select id="diff"><option value="all">ทั้งหมด</option><option value="1">ต่างจากผู้สอน</option><option value="0">ตรงกับผู้สอน</option></select></label>
<table id="items"><tr><th>รหัส</th><th>ข้อ</th><th>ผู้สอน</th><th>Gemini</th><th>AI เดิม</th><th>ความมั่นใจ</th><th>รายละเอียด</th></tr>{''.join(rows)}</table></section></main>
<script>const q=document.getElementById('q'),d=document.getElementById('diff');function filter(){{for(const row of document.querySelectorAll('#items tr[data-q]'))row.hidden=(q.value!=='all'&&row.dataset.q!==q.value)||(d.value!=='all'&&row.dataset.diff!==d.value)}}q.onchange=filter;d.onchange=filter;</script></html>'''
out = FOLDER / "all_204_review.html"
out.write_text(page, encoding="utf-8")
book.close()
print(out)
