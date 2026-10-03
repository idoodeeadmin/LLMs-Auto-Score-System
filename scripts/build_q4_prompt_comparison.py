"""Render Q4 scores before and after the clearer image-reading prompt."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs_and_tests/gemini38_regrade"
before = json.loads((FOLDER / "all_204_results.json").read_text(encoding="utf-8"))
after = json.loads((FOLDER / "q4_new_prompt_results.json").read_text(encoding="utf-8"))
old = {r["sample_id"]: r for r in before["results"] if r["question_no"] == 4}
assert len(old) == len(after["results"]) == 34


def esc(value):
    return html.escape(str(value or ""))


cards = []
for new in after["results"]:
    previous = old[new["sample_id"]]
    old_score = previous["result"]["score"]
    new_score = new["result"]["score"]
    changed = old_score != new_score
    image = "../../" + new["image_inputs"]["answer_image"]["path"].replace("\\", "/")
    cards.append(f'''<article data-changed="{int(changed)}" data-mismatch="{int(new_score != new['human_score'])}">
    <h2>{esc(new['sample_id'])} <small>ผู้สอน {new['human_score']:.0f} · Gemini ก่อน {old_score:.0f} → หลัง {new_score:.0f}</small></h2>
    <div class="grid"><div><h3>ภาพคำตอบผู้เรียน</h3><img loading="lazy" src="{esc(image)}"></div>
    <div><h3>Feedback ก่อนแก้แม่แบบ</h3><pre>{esc(previous['result']['teacher_feedback'])}</pre></div>
    <div><h3>Feedback หลังแก้แม่แบบ</h3><pre>{esc(new['result']['teacher_feedback'])}</pre></div></div></article>''')

page = f'''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ข้อ 4: เทียบก่อน–หลังแก้แม่แบบ Gemini</title><style>
body{{font-family:system-ui,'Segoe UI',sans-serif;background:#f4f7f6;color:#18362d;margin:0}}header{{background:#fff;padding:20px;border-bottom:1px solid #dce5df}}
h1{{font-size:24px;margin:0 0 8px}}p{{line-height:1.5}}main{{max-width:1500px;margin:20px auto;padding:0 16px}}
article{{background:white;border:1px solid #dce5df;border-radius:12px;padding:16px;margin:0 0 20px}}h2{{margin:0 0 12px}}small{{font-size:15px;font-weight:400;margin-left:10px}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}.grid>div{{background:#f8faf9;padding:12px;min-width:0}}img{{width:100%;max-height:650px;object-fit:contain}}
pre{{white-space:pre-wrap;font:14px/1.55 system-ui,'Segoe UI',sans-serif}}label{{margin-right:20px}}@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style><header><h1>ข้อ 4: ก่อน–หลังแก้แม่แบบ Gemini</h1><p>ใช้ภาพคำตอบ 34 ภาพ เกณฑ์และภาพแนวคำตอบเดียวกันทั้งสองรอบ · ตรงผู้สอน 19/34 เท่ากัน · คะแนนเปลี่ยน 8 ภาพ (ดีขึ้น 4, แย่ลง 4) · ทุกรายการรายงานความมั่นใจ high</p>
<p><a href="../../public/answer-keys/q4_bst_ground_truth.png" target="_blank">เปิดภาพแนวคำตอบที่ส่งทั้งสองรอบ</a></p>
<label><input id="changed" type="checkbox"> เฉพาะคะแนนที่เปลี่ยน</label><label><input id="mismatch" type="checkbox"> เฉพาะคะแนนรอบใหม่ที่ต่างจากผู้สอน</label></header>
<main>{''.join(cards)}</main><script>function apply(){{for(const x of document.querySelectorAll('article'))x.hidden=(changed.checked&&x.dataset.changed!=='1')||(mismatch.checked&&x.dataset.mismatch!=='1')}}changed.onchange=apply;mismatch.onchange=apply;</script></html>'''
out = FOLDER / "q4_new_prompt_comparison.html"
out.write_text(page, encoding="utf-8")
print(out)
