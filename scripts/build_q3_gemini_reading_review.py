"""Build a local, read-only comparison of Q3 handwriting transcriptions."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs_and_tests/q3_transcription_review"
gemini = json.loads((FOLDER / "q3_gemini_handwriting_reading_results.json").read_text(encoding="utf-8"))
gpt = json.loads((FOLDER / "q3_handwriting_reading_results.json").read_text(encoding="utf-8"))
old = {x["sample_id"]: x for x in gpt["results"]}

# Human semantic review against the image as well as the reviewed transcription.
# These are provisional research labels, not user-confirmed ground truth.
MINOR = {
    "DS-069": "การจัดคอลัมน์ข้อดี/ข้อเสียเปลี่ยน แต่รายการคำตอบยังอยู่",
    "DS-071": "คำสั้น ๆ ในประโยคที่อ้างอิงเองอ่านไม่ชัดคลาดเคลื่อน แต่ LIFO/FIFO ยังครบ",
    "DS-072": "สะกด slow access ผิดเล็กน้อย สาระอื่นครบ",
    "DS-074": "มีคำเกินและรูปพหูพจน์ต่างกัน สาระไม่เปลี่ยน",
    "DS-077": "ข้อความอ้างอิงตกหล่นบางส่วนจากผังสองคอลัมน์; Gemini ถอดส่วนที่เห็นในภาพเพิ่ม",
    "DS-085": "ถอดคำ stack ที่ถูกขีดฆ่าติดมาด้วย แต่ยังระบุ Queue และ FIFO",
    "DS-086": "สะกด variable ผิดและเปลี่ยนคำเรียก Front/Rear แต่หลัก LIFO/FIFO ยังครบ",
    "DS-087": "คำท้ายประโยคคลาดเล็กน้อย ความหมายเดิม",
    "DS-088": "คำบางคำขาดตัวอักษร แต่ใจความเรื่องขนาดและเพิ่ม/ลบยังอยู่",
    "DS-091": "แทรก [อ่านไม่ชัด] ในคำว่า Fix Size แต่สาระยังอ่านได้",
    "DS-093": "เพิ่มคำว่า 'ลด' ในเรื่องขนาด แต่ใจความ Dynamic ยังอยู่",
    "DS-094": "คำว่า 'การท่อง' คลาดเคลื่อน แต่การเริ่มจาก head และข้อดีข้อเสียยังครบ",
    "DS-095": "การเว้นวรรคและคำสะกดคลาดเล็กน้อย",
    "DS-097": "'ใช้ข้อมูล' เป็น 'ใส่ข้อมูล' แต่ประเด็นเรื่องพื้นที่ยังอยู่",
    "DS-101": "สะกดลิ้งลิสต์คลาดเล็กน้อย",
}
SIGNIFICANT = {
    "DS-082": "อ่าน Double linked list และ Dynamic ผิดจนส่วนข้อดีสำคัญสูญไป",
    "DS-102": "'ได้เห็นภาพ' เปลี่ยนเป็น 'ได้ปริมาณ' และข้อดีเปลี่ยนเป็น 'ประหยัดที่เก็บ'",
}
AMBIGUOUS = {
    "DS-079": "ลายมือช่วงท้ายกำกวม และข้อความอ้างอิงที่ตรวจไว้ก็มีคำที่ควรยืนยันจากภาพอีกครั้ง",
}
GPT_CORRECT = {"DS-069", "DS-075", "DS-084", "DS-091", "DS-094", "DS-096", "DS-099"}
GPT_MINOR = {"DS-072", "DS-080", "DS-085", "DS-093", "DS-095", "DS-101"}


def gpt_assessment(sample_id):
    if sample_id in AMBIGUOUS:
        return "ภาพกำกวม"
    if sample_id in GPT_CORRECT:
        return "ถูกต้อง"
    if sample_id in GPT_MINOR:
        return "คลาดเคลื่อนเล็กน้อย"
    return "ผิดสาระสำคัญ"


def assessment(sample_id):
    if sample_id in MINOR:
        return "คลาดเคลื่อนเล็กน้อย", MINOR[sample_id]
    if sample_id in SIGNIFICANT:
        return "ผิดสาระสำคัญ", SIGNIFICANT[sample_id]
    if sample_id in AMBIGUOUS:
        return "ภาพกำกวม", AMBIGUOUS[sample_id]
    return "ถูกต้อง", "สาระสำคัญตรงกับข้อความอ้างอิงและภาพ"


def esc(value):
    return html.escape(str(value or ""))


cards = []
labels = []
for row in gemini["results"]:
    sample_id = row["sample_id"]
    prior = old.get(sample_id, {})
    current = row.get("result") or {}
    previous = prior.get("result") or {}
    image = "../../ชุดข้อสอบใหม่/photo_clean_text3/" + row["image"]
    category, note = assessment(sample_id)
    gpt_category = gpt_assessment(sample_id)
    labels.append({"sample_id": sample_id, "category": category, "note": note,
                   "confidence": current.get("confidence"),
                   "manual_review_required_by_production_rule": current.get("confidence") == "low",
                   "gpt_category": gpt_category, "gpt_confidence": previous.get("confidence")})
    cards.append(f"""<article id="{esc(sample_id)}" class="card">
      <h2>{esc(sample_id)} <small>{esc(row['image'])}</small> <span class="badge">{esc(category)}</span></h2>
      <p class="note">{esc(note)}</p>
      <div class="grid">
        <div><h3>ภาพคำตอบที่ส่งจริง</h3><img loading="lazy" src="{esc(image)}" alt="ภาพคำตอบ {esc(sample_id)}"></div>
        <div><h3>ข้อความอ้างอิงที่ตรวจโดยมนุษย์</h3><pre>{esc(row['human_reference'])}</pre></div>
        <div><h3>Gemini 3.8 Flash · {esc(current.get('confidence'))}</h3><pre>{esc(current.get('transcription'))}</pre><p>{esc(current.get('teacher_feedback'))}</p></div>
        <div><h3>GPT รอบเดิม · {esc(previous.get('confidence'))} · {esc(gpt_category)}</h3><pre>{esc(previous.get('transcription'))}</pre><p>{esc(previous.get('teacher_feedback'))}</p></div>
      </div>
    </article>""")

page = f"""<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>เปรียบเทียบการอ่านลายมือข้อ 3</title>
<style>
body{{font-family:system-ui,'Segoe UI',sans-serif;background:#f4f7f6;color:#143129;margin:0}}
header{{position:sticky;top:0;background:#fff;padding:16px 24px;border-bottom:1px solid #ccd9d3;z-index:2}}
h1{{font-size:24px;margin:0 0 6px}}header p{{margin:0;color:#51675e}}
nav{{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}}nav a{{padding:4px 8px;background:#e9f1ee;border-radius:6px;color:#135644;text-decoration:none}}
main{{max-width:1500px;margin:20px auto;padding:0 16px}}.card{{background:#fff;border:1px solid #d6e1dc;border-radius:12px;margin-bottom:24px;padding:18px}}
h2{{margin:0 0 12px;font-size:20px}}small{{font-size:13px;color:#6b7d76;margin-left:8px}}h3{{font-size:15px;margin:0 0 10px}}
.badge{{font-size:13px;background:#dcece6;color:#164836;border-radius:12px;padding:4px 9px;margin-left:8px}}.note{{color:#405c52;margin:0 0 12px}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.grid>div{{min-width:0;background:#f8faf9;padding:12px;border-radius:8px}}
img{{width:100%;height:auto;max-height:600px;object-fit:contain}}pre{{white-space:pre-wrap;font:15px/1.6 system-ui,'Segoe UI',sans-serif;margin:0}}p{{line-height:1.5}}
@media(max-width:1100px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}
</style><header><h1>เปรียบเทียบการอ่านลายมือข้อ 3</h1><p>ภาพคำตอบ 34 ภาพ · Gemini 3.8 Flash · GPT รอบเดิม · ผลจัดกลุ่มนี้เป็นการประเมินเบื้องต้นจากภาพและข้อความอ้างอิง ควรให้ผู้วิจัยตรวจยืนยันอีกครั้ง</p>
<p>Gemini: ถูกต้อง 16 · คลาดเล็กน้อย 15 · ผิดสาระ 2 · กำกวม 1 · อ่านเพียงพอ 31/33 (93.94%)<br>GPT: ถูกต้อง 7 · คลาดเล็กน้อย 6 · ผิดสาระ 20 · กำกวม 1 · อ่านเพียงพอ 13/33 (39.39%)</p>
<nav>{''.join(f'<a href="#{esc(x["sample_id"])}">{esc(x["sample_id"])}</a>' for x in gemini['results'])}</nav></header>
<main>{''.join(cards)}</main></html>"""
out = FOLDER / "q3_gemini_reading_comparison.html"
out.write_text(page, encoding="utf-8")
labels_out = FOLDER / "q3_gemini_reading_assessment_provisional.json"
labels_out.write_text(json.dumps({"model": gemini["model"], "status": "provisional_human_review",
                                  "labels": labels}, ensure_ascii=False, indent=2), encoding="utf-8")
print(out)
