"""Build an auditable Q3 handwriting-reading experiment review page."""
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs_and_tests/q3_transcription_review"
SOURCE = DIR / "q3_handwriting_reading_results.json"
LABELS = DIR / "q3_handwriting_reading_labels.json"
PAGE = DIR / "q3_handwriting_reading_review.html"

# Provisional human comparison of the two transcriptions. Image and reference
# should be reviewed together before using these labels in a thesis table.
labels = {
    "DS-069": ("correct", "สาระครบ ต่างเพียงการสะกด linked list และรูปแบบตาราง"),
    "DS-070": ("material", "ช่วงข้อเสียท้ายคำตอบอ่านต่างจากข้อความอ้างอิง จึงอาจกระทบคะแนนด้านข้อดีข้อเสีย"),
    "DS-071": ("ambiguous", "ข้อความอ้างอิงยังมี [ไม่ชัดเจน] จึงไม่ใช้ตัดสินความถูกต้องของทั้งภาพ"),
    "DS-072": ("minor", "ชื่อ Stack ตอนต้นผิด แต่สาระคำตอบที่ใช้พิจารณาคะแนนยังอยู่"),
    "DS-073": ("material", "คำเกี่ยวกับข้อมูลเต็มและการกำหนดช่องคลาดเคลื่อน ซึ่งเป็นสาระของการเปรียบเทียบโครงสร้าง"),
    "DS-074": ("wrong", "มีคำที่ AI สร้างขึ้นและใจความหลายจุดเปลี่ยน"),
    "DS-075": ("correct", "ใจความสำคัญครบ ความต่างเป็นถ้อยคำเล็กน้อย"),
    "DS-076": ("wrong", "ข้อความหลักเรื่องใช้พื้นที่คุ้มค่าและจัดการข้อมูลถูกอ่านเปลี่ยน"),
    "DS-077": ("wrong", "อ่าน Array Fix ขนาดเป็น FIFO และข้อเสียท้ายคำตอบเปลี่ยน"),
    "DS-078": ("wrong", "ตกหล่นใจความหลักเรื่อง Linked List เพิ่มและลบข้อมูล"),
    "DS-079": ("wrong", "ข้อความหลักถูกอ่านเป็นคำอื่นจำนวนมาก"),
    "DS-080": ("minor", "ความสัมพันธ์ LinkList เป็น Stack อ่านเป็นแทน Stack แต่สาระข้อดีข้อเสียที่ใช้ตรวจยังครบ"),
    "DS-081": ("wrong", "อ่านนำข้อมูลเข้าและลบข้อมูลเป็นคำอื่น ทำให้ความหมายข้อดีข้อเสียเปลี่ยน"),
    "DS-082": ("material", "รายละเอียดการเปรียบเทียบและข้อดีข้อเสียบางส่วนผิดหรือตก"),
    "DS-083": ("wrong", "ข้อความเรื่อง push/pop และข้อดีข้อเสียอ่านได้ผิดเป็นส่วนใหญ่"),
    "DS-084": ("minor", "ทำได้ยากกว่าถูกอ่านเป็นทำได้ช้ากว่า แต่ยังสื่อข้อเสียด้านการเข้าถึงข้อมูล"),
    "DS-085": ("material", "ส่วนที่กล่าวถึง Array หลายคำผิดหรือตก อาจกระทบการประเมินการเปรียบเทียบ"),
    "DS-086": ("material", "คำอธิบายข้อเสียเปลี่ยนจากความซับซ้อนเป็นต้นทุนข้อมูล"),
    "DS-087": ("wrong", "ใจความคำตอบเกือบทั้งหมดถูกอ่านเป็นข้อความอื่น"),
    "DS-088": ("material", "ข้อเสียที่เปรียบเทียบกับ Array และส่วนต้นอ่านผิด"),
    "DS-089": ("wrong", "ข้อเสียไม่มีการ sort ถูกอ่านเป็นจะมีการ sort ซึ่งกลับความหมาย"),
    "DS-090": ("material", "ข้อดีของ Linked List ตกหล่น ซึ่งเป็นองค์ประกอบที่ใช้ให้คะแนน"),
    "DS-091": ("correct", "ใจความเรื่อง static/dynamic และข้อดีข้อเสียครบ"),
    "DS-092": ("wrong", "ใจความเรื่อง Array เต็มและค้นหาช้าถูกอ่านผิด"),
    "DS-093": ("material", "ข้อดี insert/delete ไวกว่าอ่านเป็นไม่จำกัด ซึ่งเปลี่ยนสาระที่ใช้ให้คะแนน"),
    "DS-094": ("correct", "สาระเรื่อง dynamic/static การเข้าถึงและข้อดีข้อเสียครบ"),
    "DS-095": ("material", "ข้อดีเร็วถูกอ่านเป็นเรื่อง ทำให้ข้อดีที่ผู้เรียนเขียนหายไป"),
    "DS-096": ("correct", "ใจความ Stack/Queue และ dynamic size ครบ"),
    "DS-097": ("material", "คำและหัวข้อหลายส่วนผิด รวมถึงสาระที่ใช้พิจารณาข้อดีข้อเสีย"),
    "DS-098": ("material", "ข้อเสียทำงานตามลำดับอ่านเป็นทำงานค่อนข้างช้า"),
    "DS-099": ("correct", "สาระเรื่องขนาด Array และ Linked List ตรงกัน"),
    "DS-100": ("wrong", "ไม่แตกต่างถูกอ่านเป็นได้แตกต่าง และรายละเอียดสำคัญตกหล่น"),
    "DS-101": ("material", "ข้อดีใช้พื้นที่เท่าที่จำเป็นอ่านไม่ครบ ซึ่งเป็นองค์ประกอบที่ใช้ให้คะแนน"),
    "DS-102": ("wrong", "ข้อความหลักเกือบทั้งหมดอ่านไม่ได้หรือถูกสร้างเป็นข้อความอื่น"),
}

source = json.loads(SOURCE.read_text(encoding="utf-8"))
assert len(source["results"]) == 34 and all(x["success"] for x in source["results"])
assert set(labels) == {x["sample_id"] for x in source["results"]}
assert all(len(re.findall(r"[\u0E00-\u0E7F]+|[a-zA-Z0-9_]+", x["result"]["transcription"])) < 300
           for x in source["results"]), "A transcription may exceed the production word limit"
records = []
for x in source["results"]:
    label, rationale = labels[x["sample_id"]]
    if label in ("material", "wrong"):
        label = "significant"
    records.append({"sample_id": x["sample_id"], "image": x["image"],
                    "human_reference": x["human_reference"], "human_note": x["human_note"],
                    "ai_transcription": x["result"]["transcription"],
                    "confidence": x["result"]["confidence"],
                    "manual_review_required": x["result"]["confidence"] == "low",
                    "teacher_feedback": x["result"]["teacher_feedback"],
                    "label": label, "rationale": rationale})
usable = [r for r in records if r["label"] != "ambiguous"]
counts = Counter(r["label"] for r in records)
review_needed = [r for r in records if r["label"] in ("significant", "ambiguous")]
tagged = [r for r in records if r["manual_review_required"]]
true_positive = sum(r["manual_review_required"] for r in review_needed)
safe_count = counts["correct"] + counts["minor"]
summary = (f"RQ1 อ่านเพียงพอต่อการตรวจ {safe_count}/{len(usable)} ({safe_count/len(usable):.2%}) · "
           f"ถูกต้อง {counts['correct']} · คลาดเคลื่อนเล็กน้อย {counts['minor']} · "
           f"ผิดสาระสำคัญ {counts['significant']} · ภาพกำกวม {counts['ambiguous']} | "
           f"RQ2 Review Recall {true_positive}/{len(review_needed)} ({true_positive/len(review_needed):.2%}) · "
           f"Review Precision {true_positive}/{len(tagged)} ({true_positive/len(tagged):.2%}) · "
           f"Review Rate {len(tagged)}/{len(records)} ({len(tagged)/len(records):.2%})")
LABELS.write_text(json.dumps({
    "status": "provisional_human_comparison", "source": SOURCE.name,
    "production_confidence_rule": source["production_confidence_rule"],
    "manual_review_rule": "word_limit_exceeded or confidence == low, as in server/services/openai_grading.py; no transcription in this set reaches the 300-word limit",
    "manual_review_required_source": "derived from the production rule; the transcription-only API response contains confidence but not this flag",
    "summary": {"total_images": len(records), "clear_ground_truth": len(usable),
                "correct": counts["correct"], "minor": counts["minor"],
                "significant": counts["significant"], "ambiguous": counts["ambiguous"],
                "sufficient_to_grade": safe_count, "sufficient_to_grade_rate": safe_count / len(usable),
                "review_true_positive": true_positive, "review_needed": len(review_needed),
                "review_tagged": len(tagged), "review_recall": true_positive / len(review_needed),
                "review_precision": true_positive / len(tagged), "review_rate": len(tagged) / len(records)},
    "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")

cards = []
for r in records:
    rid = html.escape(r["sample_id"])
    options = "".join(f'<option value="{v}" {"selected" if v == r["label"] else ""}>{label}</option>'
                      for v, label in (("correct", "ถูกต้อง: ใช้ตรวจได้"),
                                       ("minor", "คลาดเคลื่อนเล็กน้อย: ใช้ตรวจได้"),
                                       ("significant", "ผิดสาระสำคัญ: ต้องทบทวน"),
                                       ("ambiguous", "ภาพกำกวม: ไม่คิด RQ1 / ต้องทบทวน RQ2")))
    cards.append(f'''<article class="card" data-id="{rid}" data-confidence="{r['confidence']}">
<header><strong>{rid}</strong><span>{html.escape(r["image"])} · confidence: <b>{r["confidence"]}</b></span>
<label>ผลประเมิน <select>{options}</select></label></header>
<div class="cols"><img src="../../ชุดข้อสอบใหม่/photo_clean_text3/{html.escape(r["image"])}" alt="ภาพคำตอบ {rid}">
<section><h3>ข้อความอ้างอิงที่มนุษย์ตรวจ</h3><pre>{html.escape(r["human_reference"])}</pre></section>
<section><h3>AI ถอดจากภาพ</h3><pre>{html.escape(r["ai_transcription"])}</pre></section></div>
<div class="notes"><b>เหตุผลจัดระดับ:</b> {html.escape(r["rationale"])}<br>
<b>หมายเหตุข้อความอ้างอิง:</b> {html.escape(r["human_note"])}<br>
<b>คำอธิบายความมั่นใจของ AI:</b> {html.escape(r["teacher_feedback"])}</div></article>''')

PAGE.write_text(f'''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ประเมินการอ่านลายมือข้อ 3</title><style>
body{{font:16px/1.6 system-ui,sans-serif;background:#f4f7f6;color:#18342f;margin:0}}main{{max-width:1500px;margin:auto;padding:24px}}
h1{{margin:0}}.intro{{background:white;padding:18px;border:1px solid #cdded8;border-radius:12px;margin:14px 0 24px}}
.card{{background:white;border:1px solid #cdded8;border-radius:12px;margin:16px 0;overflow:hidden}}
.card header{{display:flex;gap:20px;align-items:center;flex-wrap:wrap;background:#e9f3ef;padding:10px 16px}}
select,button{{font:inherit;padding:6px 10px;border:1px solid #adc5bc;border-radius:7px;background:white}}
.cols{{display:grid;grid-template-columns:1.1fr 1fr 1fr;gap:14px;padding:14px}}
.cols img{{width:100%;max-height:500px;object-fit:contain;background:#e8eeeb}}
.cols section{{min-width:0}}h3{{margin:0 0 8px;font-size:15px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.65 system-ui,sans-serif;margin:0}}
.notes{{padding:10px 16px;border-top:1px solid #e2ebe7;font-size:14px}}.small{{font-size:14px;color:#536d64}}
@media(max-width:900px){{.cols{{grid-template-columns:1fr}}}}
</style><main><h1>การอ่านลายมือจากภาพคำตอบ ข้อ 3</h1>
<div class="intro"><p><b>ผลจัดระดับเบื้องต้น:</b> <span id="summary">{html.escape(summary)}</span></p>
<p><b>RQ1:</b> เปรียบเทียบคำถอดจากภาพกับข้อความที่ผู้ใช้ตรวจแล้ว โดยตัดสินว่าข้อความยังเพียงพอสำหรับนำไปให้คะแนนตามเกณฑ์ข้อ 3 หรือไม่ คำผิดที่ไม่เปลี่ยนองค์ประกอบการให้คะแนนถือว่ายังใช้ตรวจได้ ภาพกำกวมไม่นับในตัวหาร RQ1</p>
<p><b>RQ2:</b> กรณีผิดสาระสำคัญหรือภาพกำกวมถือว่าควรทบทวน เปรียบเทียบกับป้าย <code>manual_review_required</code> ของระบบ ซึ่งเกิดเมื่อ <code>confidence=low</code> (ชุดนี้ไม่มีคำตอบเกินขีดจำกัดจำนวนคำ) การจัดระดับนี้เป็นการตรวจเบื้องต้นและสามารถแก้ไขก่อนนำไปอ้างในรายงานได้</p>
<p><b>เกณฑ์ป้ายความมั่นใจจากแม่แบบจริง:</b> {html.escape(source['production_confidence_rule'])}</p>
<p class="small">ระดับความมั่นใจเป็นสิ่งที่โมเดลรายงานเอง ไม่ใช่ค่าความน่าจะเป็นที่ปรับเทียบแล้ว ผลหลักใช้ป้ายตามพฤติกรรมระบบจริง ไม่ได้นับ medium เป็นการส่งให้ผู้สอนทบทวน</p>
<button id="download">ส่งออกผลตรวจ JSON</button></div>{''.join(cards)}
<script>const cards=[...document.querySelectorAll('.card')];function update(){{const c={{correct:0,minor:0,significant:0,ambiguous:0}};let tp=0,tagged=0;for(const x of cards){{const label=x.querySelector('select').value,tag=x.dataset.confidence==='low';c[label]++;tagged+=tag;tp+=tag&&(label==='significant'||label==='ambiguous');}}const n=cards.length-c.ambiguous,safe=c.correct+c.minor,needs=c.significant+c.ambiguous,p=(v,d)=>d?((100*v/d).toFixed(2)+'%'):'–';document.querySelector('#summary').textContent=`RQ1 อ่านเพียงพอต่อการตรวจ ${{safe}}/${{n}} (${{p(safe,n)}}) · ถูกต้อง ${{c.correct}} · คลาดเคลื่อนเล็กน้อย ${{c.minor}} · ผิดสาระสำคัญ ${{c.significant}} · ภาพกำกวม ${{c.ambiguous}} | RQ2 Review Recall ${{tp}}/${{needs}} (${{p(tp,needs)}}) · Review Precision ${{tp}}/${{tagged}} (${{p(tp,tagged)}}) · Review Rate ${{tagged}}/${{cards.length}} (${{p(tagged,cards.length)}})`;}}
cards.forEach(x=>x.querySelector('select').addEventListener('change',update));document.querySelector('#download').onclick=()=>{{const labels=Object.fromEntries(cards.map(x=>[x.dataset.id,x.querySelector('select').value]));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(labels,null,2)],{{type:'application/json'}}));a.download='q3_handwriting_labels_reviewed.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}};</script></main></html>''', encoding="utf-8")
print(summary)
print(PAGE)
