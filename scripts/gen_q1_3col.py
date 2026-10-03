"""
Generate Q1 3-column comparison page:
Left: original photo (with teacher score) | Middle: clean photo | Right: transcribed text
Output: public/q1_compare.html
"""
import base64
import sys, openpyxl, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Load data
wb = openpyxl.load_workbook(ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx", data_only=True)
ws = wb["ชุดข้อสอบ_dataset"]
graded = json.load(open(ROOT / "scratch" / "optimal_34_graded.json", encoding="utf-8"))
fn_map = {f"DS-{i+1:03d}": item["filename"] for i, item in enumerate(graded)}

items = []
for r in range(6, 40):
    sid = ws.cell(r, 1).value
    if not sid:
        continue
    h = float(ws.cell(r, 7).value or 0)
    ai = float(ws.cell(r, 8).value or 0)
    ans = str(ws.cell(r, 6).value or "").replace("\r\n", "\n").strip()
    fb_raw = str(ws.cell(r, 10).value or "")
    teacher_fb = (
        fb_raw.split("[สำหรับนักเรียน]")[0].replace("[สำหรับผู้สอน]", "").strip()
        if "[สำหรับผู้สอน]" in fb_raw
        else fb_raw.strip()
    )
    orig_fn = fn_map.get(sid, "")
    img_file = f"{sid}_{orig_fn}" if orig_fn else ""
    items.append({
        "sid": sid, "img": img_file, "orig_fn": orig_fn,
        "ans": ans, "h": h, "ai": ai,
        "diff": round(ai - h, 1), "teacher_fb": teacher_fb,
    })

total = len(items)
exact = sum(1 for x in items if x["diff"] == 0.0)
diffs_pos = sum(1 for x in items if x["diff"] > 0)
items_json_raw = json.dumps(items, ensure_ascii=False)
items_json_b64 = base64.b64encode(items_json_raw.encode('utf-8')).decode('ascii')

out_path = ROOT / "public" / "q1_compare.html"

with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Q1: ภาพต้นฉบับ vs Clean vs Text — 34 ตัวอย่าง</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,"Noto Sans Thai",sans-serif;background:#0f1117;color:#e2e8f0;min-height:100vh}}
:root{{
  --border:rgba(99,102,241,.18);--accent:#6366f1;--green:#22c55e;--red:#ef4444;
  --orange:#f97316;--blue:#38bdf8;--muted:#64748b;
  --match-bg:rgba(34,197,94,.07);--diff-bg:rgba(239,68,68,.07);
  --match-border:rgba(34,197,94,.3);--diff-border:rgba(239,68,68,.3);
}}
.header{{background:linear-gradient(135deg,#1e1b4b,#1a1d2e,#0f172a);border-bottom:1px solid var(--border);padding:22px 36px;position:sticky;top:0;z-index:100}}
.header h1{{font-size:20px;font-weight:700;color:#fff}}
.header .sub{{font-size:12px;color:var(--muted);margin-top:3px}}
.stats{{display:flex;gap:16px;margin-top:12px;flex-wrap:wrap}}
.chip{{display:flex;align-items:center;gap:7px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:5px 12px;font-size:12px}}
.chip .v{{font-weight:700;font-size:14px}}
.chip.g{{border-color:var(--match-border);color:var(--green)}}
.chip.r{{border-color:var(--diff-border);color:var(--red)}}
.chip.b{{border-color:rgba(56,189,248,.3);color:var(--blue)}}
.filters{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:12px 36px;background:#141624;border-bottom:1px solid var(--border)}}
.fb{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);color:var(--muted);border-radius:16px;padding:5px 14px;font-size:12px;cursor:pointer;font-family:inherit;transition:.2s}}
.fb.active,.fb:hover{{background:rgba(99,102,241,.15);border-color:var(--accent);color:#fff}}
.lbl{{font-size:11px;color:var(--muted);font-weight:500;margin-right:4px}}
.grid{{display:grid;grid-template-columns:1fr;gap:16px;padding:20px 36px;max-width:1800px;margin:0 auto}}
.card{{background:#1a1d2e;border-radius:12px;border:1px solid var(--border);overflow:hidden;transition:transform .2s,box-shadow .2s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 10px 36px rgba(0,0,0,.4)}}
.card.match{{border-color:var(--match-border);background:var(--match-bg)}}
.card.diff{{border-color:var(--diff-border);background:var(--diff-bg)}}
.ch{{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid rgba(255,255,255,.06);background:rgba(0,0,0,.2)}}
.ch .l{{display:flex;align-items:center;gap:8px}}
.sid{{background:rgba(99,102,241,.2);border:1px solid rgba(99,102,241,.4);color:#a5b4fc;border-radius:5px;padding:2px 8px;font-family:"JetBrains Mono",monospace;font-size:11px;font-weight:600}}
.fn{{font-size:10px;color:var(--muted);font-family:"JetBrains Mono",monospace}}
.scores{{display:flex;align-items:center;gap:6px}}
.sb{{display:flex;flex-direction:column;align-items:center;background:rgba(255,255,255,.05);border-radius:7px;padding:3px 9px;min-width:46px}}
.sb .lb{{font-size:9px;color:var(--muted)}}
.sb .vl{{font-size:15px;font-weight:700}}
.sb.h .vl{{color:var(--blue)}}.sb.ai .vl{{color:var(--orange)}}
.db{{border-radius:7px;padding:3px 9px;font-size:12px;font-weight:700;font-family:"JetBrains Mono",monospace}}
.db.match{{background:rgba(34,197,94,.15);color:var(--green);border:1px solid var(--match-border)}}
.db.over{{background:rgba(239,68,68,.15);color:var(--red);border:1px solid var(--diff-border)}}
.db.under{{background:rgba(249,115,22,.15);color:var(--orange);border:1px solid rgba(249,115,22,.3)}}
.cb{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0}}
.ip{{padding:10px;border-right:1px solid rgba(255,255,255,.05);display:flex;flex-direction:column;gap:6px}}
.ip .pt{{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:2px}}
.ip img{{width:100%;border-radius:7px;cursor:zoom-in;border:1px solid rgba(255,255,255,.07);transition:opacity .2s;max-height:360px;object-fit:contain;background:#000}}
.ip img:hover{{opacity:.88}}
.tp{{padding:10px 12px;display:flex;flex-direction:column;gap:8px;overflow:hidden}}
.tp .pt{{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--muted)}}
.ans{{background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.07);border-radius:7px;padding:9px 11px;font-size:12.5px;line-height:1.75;color:#cbd5e1;flex:1;overflow-y:auto;max-height:300px;white-space:pre-wrap;word-break:break-word}}
.fbb{{background:rgba(99,102,241,.07);border:1px solid rgba(99,102,241,.15);border-radius:7px;padding:7px 9px;font-size:11px;line-height:1.6;color:#94a3b8;max-height:90px;overflow-y:auto}}
.fbl{{font-size:9px;font-weight:600;color:#6366f1;text-transform:uppercase;letter-spacing:.8px;margin-bottom:3px}}
.lightbox{{display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.93);align-items:center;justify-content:center;cursor:zoom-out}}
.lightbox.open{{display:flex}}
.lightbox img{{max-width:93vw;max-height:93vh;border-radius:9px}}
.lbc{{position:fixed;top:18px;right:24px;font-size:30px;color:#fff;cursor:pointer;background:none;border:none;font-weight:700}}
.lbi{{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:6px 18px;font-size:12px;color:#fff;font-family:"JetBrains Mono",monospace}}
@media(max-width:900px){{.cb{{grid-template-columns:1fr}}.ip{{border-right:none;border-bottom:1px solid rgba(255,255,255,.05)}}.grid{{padding:12px 16px}}.header,.filters{{padding-left:16px;padding-right:16px}}}}
</style>
</head>
<body>
<div class="header">
  <h1>🔍 Q1: ต้นฉบับ (มีคะแนน) | Clean | Text</h1>
  <div class="sub">ข้อ 1 — Row-major vs Column-major · 34 ตัวอย่าง · 3-column view: ต้นฉบับ / clean / text ใน Excel</div>
  <div class="stats">
    <div class="chip b"><span>📋 ทั้งหมด</span><span class="v">{total}</span></div>
    <div class="chip g"><span>✅ ตรงกัน</span><span class="v">{exact}/{total}</span></div>
    <div class="chip r"><span>❌ AI สูงกว่า</span><span class="v">{diffs_pos}</span></div>
  </div>
</div>
<div class="filters">
  <span class="lbl">กรอง:</span>
  <button class="fb active" data-f="all">ทั้งหมด ({total})</button>
  <button class="fb" data-f="match">✅ ตรงกัน ({exact})</button>
  <button class="fb" data-f="diff">❌ ต่างกัน ({total - exact})</button>
  <button class="fb" data-f="h2">H=2.0</button>
  <button class="fb" data-f="h1">H=1.0</button>
  <button class="fb" data-f="h0">H=0.0</button>
</div>
<div class="grid" id="grid"></div>
<div class="lightbox" id="lightbox" onclick="closeLightbox()">
  <button class="lbc" onclick="closeLightbox()">×</button>
  <img id="lb-img" src="" alt="">
  <div class="lbi" id="lb-info"></div>
</div>
<script>
const DATA = JSON.parse(atob('{items_json_b64}'));
function esc(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}}
function nl2br(s){{return esc(s).replace(/\\n/g,'<br>')}}
function dclass(d){{return d===0?'match':d>0?'over':'under'}}
function dlabel(d){{return d===0?'✓ ตรงกัน':d>0?'+'+d.toFixed(1)+' AI สูงกว่า':d.toFixed(1)+' AI ต่ำกว่า'}}
function openLightbox(src,info){{document.getElementById('lb-img').src=src;document.getElementById('lb-info').textContent=info;document.getElementById('lightbox').classList.add('open')}}
function closeLightbox(){{document.getElementById('lightbox').classList.remove('open')}}
function renderCard(item){{
  const orig='/photo_q1_original/'+item.img;
  const clean='/photo_q1_source_34/'+item.img;
  const dc=dclass(item.diff),cc=item.diff===0?'match':'diff',dl=dlabel(item.diff);
  const fb=item.teacher_fb?'<div class="fbb"><div class="fbl">💬 เหตุผล AI</div>'+nl2br(item.teacher_fb.substring(0,220))+(item.teacher_fb.length>220?'…':'')+'</div>':'';
  return '<div class="card '+cc+'" data-diff="'+item.diff+'" data-h="'+item.h+'" data-sid="'+item.sid+'">'+
    '<div class="ch">'+
      '<div class="l"><span class="sid">'+esc(item.sid)+'</span><span class="fn">'+esc(item.orig_fn)+'</span></div>'+
      '<div class="scores">'+
        '<div class="sb h"><span class="lb">อาจารย์</span><span class="vl">'+item.h.toFixed(1)+'</span></div>'+
        '<div class="sb ai"><span class="lb">AI</span><span class="vl">'+item.ai.toFixed(1)+'</span></div>'+
        '<div class="db '+dc+'">'+dl+'</div>'+
      '</div>'+
    '</div>'+
    '<div class="cb">'+
      '<div class="ip">'+
        '<div class="pt">🔴 ต้นฉบับ (มีคะแนนอาจารย์)</div>'+
        '<img src="'+orig+'" loading="lazy" onclick="openLightbox(\''+orig+'\',\''+esc(item.sid)+' — ต้นฉบับ\')" onerror="this.style.display=\'none\'">'+
      '</div>'+
      '<div class="ip">'+
        '<div class="pt">🟢 Clean (ลบคะแนนออก)</div>'+
        '<img src="'+clean+'" loading="lazy" onclick="openLightbox(\''+clean+'\',\''+esc(item.sid)+' — clean\')" onerror="this.style.display=\'none\'">'+
      '</div>'+
      '<div class="tp">'+
        '<div class="pt">📝 Text ใน Excel (ที่ใช้กับ AI)</div>'+
        '<div class="ans">'+nl2br(item.ans)+'</div>'+
        fb+
      '</div>'+
    '</div>'+
  '</div>';
}}
document.querySelectorAll('.fb').forEach(function(b){{
  b.addEventListener('click',function(){{
    document.querySelectorAll('.fb').forEach(function(x){{x.classList.remove('active')}});
    this.classList.add('active');
    const f=this.dataset.f;
    document.querySelectorAll('.card').forEach(function(c){{
      const diff=parseFloat(c.dataset.diff),h=parseFloat(c.dataset.h);
      const show=f==='all'||(f==='match'&&diff===0)||(f==='diff'&&diff!==0)||(f==='h2'&&h===2)||(f==='h1'&&h===1)||(f==='h0'&&h===0);
      c.style.display=show?'':'none';
    }});
  }});
}});
const g=document.getElementById('grid');
DATA.forEach(function(item){{g.insertAdjacentHTML('beforeend',renderCard(item))}});
document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeLightbox()}});
</script>
</body>
</html>""")

print(f"Generated: {out_path}")
print(f"URL: http://localhost:8080/q1_compare.html")
