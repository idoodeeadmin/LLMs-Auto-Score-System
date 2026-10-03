"""
Generate Q1 text-vs-image comparison webpage.
Output: public/q1_compare.html
"""
import sys, openpyxl, json, shutil
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
wb = openpyxl.load_workbook(
    ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx", data_only=True
)
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
    teacher_fb = ""
    student_fb = ""
    if "[สำหรับผู้สอน]" in fb_raw:
        parts = fb_raw.split("[สำหรับนักเรียน]")
        teacher_fb = parts[0].replace("[สำหรับผู้สอน]", "").strip()
        student_fb = parts[1].strip() if len(parts) > 1 else ""
    else:
        teacher_fb = fb_raw.strip()

    orig_fn = fn_map.get(sid, "")
    img_file = f"{sid}_{orig_fn}" if orig_fn else ""
    diff = round(ai - h, 1)
    items.append(
        {
            "sid": sid,
            "img": img_file,
            "orig_fn": orig_fn,
            "ans": ans,
            "h": h,
            "ai": ai,
            "diff": diff,
            "teacher_fb": teacher_fb,
            "student_fb": student_fb,
        }
    )

total = len(items)
exact = sum(1 for x in items if x["diff"] == 0.0)
diffs_pos = sum(1 for x in items if x["diff"] > 0)
diffs_neg = sum(1 for x in items if x["diff"] < 0)

items_json = json.dumps(items, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Q1 Text vs Image Comparison — ข้อ 1 ทั้ง 34 ตัวอย่าง</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0f1117;
    --card: #1a1d2e;
    --card2: #141624;
    --border: rgba(99,102,241,0.18);
    --accent: #6366f1;
    --accent2: #8b5cf6;
    --green: #22c55e;
    --red: #ef4444;
    --orange: #f97316;
    --blue: #38bdf8;
    --text: #e2e8f0;
    --muted: #64748b;
    --match-bg: rgba(34,197,94,0.08);
    --diff-bg: rgba(239,68,68,0.08);
    --match-border: rgba(34,197,94,0.3);
    --diff-border: rgba(239,68,68,0.3);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', 'Noto Sans Thai', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }}

  /* ─── Header ─── */
  .header {{
    background: linear-gradient(135deg, #1e1b4b 0%, #1a1d2e 50%, #0f172a 100%);
    border-bottom: 1px solid var(--border);
    padding: 28px 40px 24px;
    position: sticky; top: 0; z-index: 100;
  }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: #fff; letter-spacing: -.3px; }}
  .header .sub {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}
  .stats-bar {{
    display: flex; gap: 24px; margin-top: 16px; flex-wrap: wrap;
  }}
  .stat-chip {{
    display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 6px 14px;
    font-size: 13px;
  }}
  .stat-chip .val {{ font-weight: 700; font-size: 15px; }}
  .stat-chip.green {{ border-color: var(--match-border); color: var(--green); }}
  .stat-chip.red {{ border-color: var(--diff-border); color: var(--red); }}
  .stat-chip.blue {{ border-color: rgba(56,189,248,0.3); color: var(--blue); }}

  /* ─── Filter Bar ─── */
  .filter-bar {{
    display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
    padding: 16px 40px;
    background: var(--card2);
    border-bottom: 1px solid var(--border);
  }}
  .filter-btn {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    color: var(--muted);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
    cursor: pointer;
    font-family: inherit;
    transition: all .2s;
  }}
  .filter-btn.active, .filter-btn:hover {{
    background: rgba(99,102,241,0.15);
    border-color: var(--accent);
    color: #fff;
  }}
  .filter-label {{ font-size: 12px; color: var(--muted); font-weight: 500; margin-right: 4px; }}

  /* ─── Grid ─── */
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(700px, 1fr));
    gap: 20px;
    padding: 24px 40px;
    max-width: 1800px;
    margin: 0 auto;
  }}

  /* ─── Card ─── */
  .card {{
    background: var(--card);
    border-radius: 14px;
    border: 1px solid var(--border);
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
  }}
  .card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
  }}
  .card.match {{ border-color: var(--match-border); background: var(--match-bg); }}
  .card.diff {{ border-color: var(--diff-border); background: var(--diff-bg); }}

  .card-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(0,0,0,0.2);
  }}
  .card-header .left {{ display: flex; align-items: center; gap: 10px; }}
  .sid-badge {{
    background: rgba(99,102,241,0.2);
    border: 1px solid rgba(99,102,241,0.4);
    color: #a5b4fc;
    border-radius: 6px; padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; font-weight: 600;
  }}
  .fn-badge {{
    font-size: 11px; color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
  }}
  .scores {{
    display: flex; align-items: center; gap: 8px;
  }}
  .score-box {{
    display: flex; flex-direction: column; align-items: center;
    background: rgba(255,255,255,0.05);
    border-radius: 8px; padding: 4px 10px;
    min-width: 52px;
  }}
  .score-box .label {{ font-size: 10px; color: var(--muted); font-weight: 500; }}
  .score-box .val {{ font-size: 16px; font-weight: 700; }}
  .score-box.human .val {{ color: var(--blue); }}
  .score-box.ai .val {{ color: var(--orange); }}
  .diff-badge {{
    border-radius: 8px; padding: 4px 10px;
    font-size: 13px; font-weight: 700; font-family: 'JetBrains Mono', monospace;
  }}
  .diff-badge.match {{ background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid var(--match-border); }}
  .diff-badge.over {{ background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid var(--diff-border); }}
  .diff-badge.under {{ background: rgba(249,115,22,0.15); color: var(--orange); border: 1px solid rgba(249,115,22,0.3); }}

  /* ─── Body: 3-col layout ─── */
  .card-body {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0;
  }}
  .img-panel {{
    padding: 12px;
    border-right: 1px solid rgba(255,255,255,0.06);
    display: flex; flex-direction: column; gap: 8px;
  }}
  .img-panel .panel-title {{
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1px; color: var(--muted);
  }}
  .img-panel img {{
    width: 100%;
    border-radius: 8px;
    cursor: zoom-in;
    border: 1px solid rgba(255,255,255,0.08);
    transition: opacity .2s;
  }}
  .img-panel img:hover {{ opacity: 0.9; }}

  .text-panel {{
    padding: 12px 14px;
    display: flex; flex-direction: column; gap: 10px;
    overflow: hidden;
  }}
  .text-panel .panel-title {{
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1px; color: var(--muted);
  }}
  .ans-box {{
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 13px;
    line-height: 1.7;
    color: #cbd5e1;
    flex: 1;
    overflow-y: auto;
    max-height: 260px;
    white-space: pre-wrap;
    word-break: break-word;
  }}
  .feedback-box {{
    background: rgba(99,102,241,0.07);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 11.5px;
    line-height: 1.6;
    color: #94a3b8;
    max-height: 100px;
    overflow-y: auto;
  }}
  .feedback-box .fb-label {{
    font-size: 10px; font-weight: 600; color: #6366f1;
    text-transform: uppercase; letter-spacing: .8px;
    margin-bottom: 4px;
  }}

  /* ─── Lightbox ─── */
  .lightbox {{
    display: none; position: fixed; inset: 0; z-index: 9999;
    background: rgba(0,0,0,0.92);
    align-items: center; justify-content: center;
    cursor: zoom-out;
  }}
  .lightbox.open {{ display: flex; }}
  .lightbox img {{ max-width: 92vw; max-height: 92vh; border-radius: 10px; }}
  .lightbox-close {{
    position: fixed; top: 20px; right: 28px;
    font-size: 32px; color: #fff; cursor: pointer; font-weight: 700;
    background: none; border: none;
  }}
  .lightbox-info {{
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px; padding: 8px 20px;
    font-size: 13px; color: #fff;
    font-family: 'JetBrains Mono', monospace;
  }}

  /* ─── Empty state ─── */
  .empty {{ text-align: center; padding: 80px 20px; color: var(--muted); }}

  @media (max-width: 800px) {{
    .grid {{ grid-template-columns: 1fr; padding: 16px; }}
    .card-body {{ grid-template-columns: 1fr; }}
    .img-panel {{ border-right: none; border-bottom: 1px solid rgba(255,255,255,0.06); }}
    .header, .filter-bar {{ padding-left: 16px; padding-right: 16px; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>🔍 Q1: เปรียบเทียบ Text vs ภาพต้นฉบับ</h1>
  <div class="sub">ข้อ 1 — อธิบายความต่าง Row-major vs Column-major · ชุดข้อสอบ Dataset 34 ตัวอย่าง</div>
  <div class="stats-bar">
    <div class="stat-chip blue"><span>📋 ทั้งหมด</span><span class="val">{total}</span></div>
    <div class="stat-chip green"><span>✅ AI ตรงกับอาจารย์</span><span class="val">{exact}/{total}</span></div>
    <div class="stat-chip red"><span>❌ AI ให้สูงกว่า</span><span class="val">{diffs_pos}</span></div>
  </div>
</div>

<div class="filter-bar">
  <span class="filter-label">กรอง:</span>
  <button class="filter-btn active" onclick="filterCards('all')">ทั้งหมด ({total})</button>
  <button class="filter-btn" onclick="filterCards('match')">✅ ตรงกัน ({exact})</button>
  <button class="filter-btn" onclick="filterCards('diff')">❌ ต่างกัน ({total - exact})</button>
  <button class="filter-btn" onclick="filterCards('h2')">H=2.0</button>
  <button class="filter-btn" onclick="filterCards('h1')">H=1.0</button>
  <button class="filter-btn" onclick="filterCards('h0')">H=0.0</button>
</div>

<div class="grid" id="grid">
</div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
  <button class="lightbox-close" onclick="closeLightbox()">×</button>
  <img id="lb-img" src="" alt="">
  <div class="lightbox-info" id="lb-info"></div>
</div>

<script>
const DATA = {items_json};

function esc(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function nl2br(s) {{
  return esc(s).replace(/\\n/g,'<br>');
}}

function diffClass(d) {{
  if (d === 0) return 'match';
  if (d > 0) return 'over';
  return 'under';
}}
function diffLabel(d) {{
  if (d === 0) return '✓ ตรงกัน';
  if (d > 0) return `+${{d.toFixed(1)}} AI สูงกว่า`;
  return `${{d.toFixed(1)}} AI ต่ำกว่า`;
}}

function openLightbox(imgSrc, info) {{
  document.getElementById('lb-img').src = imgSrc;
  document.getElementById('lb-info').textContent = info;
  document.getElementById('lightbox').classList.add('open');
}}
function closeLightbox() {{
  document.getElementById('lightbox').classList.remove('open');
}}

function renderCard(item) {{
  const imgSrc = `/photo_q1_source_34/${{item.img}}`;
  const dc = diffClass(item.diff);
  const cardClass = item.diff === 0 ? 'match' : 'diff';
  const dl = diffLabel(item.diff);

  const fbHtml = item.teacher_fb ? `
    <div class="feedback-box">
      <div class="fb-label">💬 เหตุผล AI</div>
      ${{nl2br(item.teacher_fb.substring(0, 220))}}${{item.teacher_fb.length > 220 ? '…' : ''}}
    </div>` : '';

  return `
    <div class="card ${{cardClass}}"
         data-diff="${{item.diff}}"
         data-h="${{item.h}}"
         data-sid="${{item.sid}}">
      <div class="card-header">
        <div class="left">
          <span class="sid-badge">${{esc(item.sid)}}</span>
          <span class="fn-badge">${{esc(item.orig_fn)}}</span>
        </div>
        <div class="scores">
          <div class="score-box human">
            <span class="label">อาจารย์</span>
            <span class="val">${{item.h.toFixed(1)}}</span>
          </div>
          <div class="score-box ai">
            <span class="label">AI</span>
            <span class="val">${{item.ai.toFixed(1)}}</span>
          </div>
          <div class="diff-badge ${{dc}}">${{dl}}</div>
        </div>
      </div>
      <div class="card-body">
        <div class="img-panel">
          <div class="panel-title">📷 ภาพต้นฉบับ</div>
          <img src="${{imgSrc}}" alt="${{esc(item.orig_fn)}}"
               onclick="openLightbox('${{imgSrc}}', '${{esc(item.sid)}} — ${{esc(item.orig_fn)}}')"
               loading="lazy"
               onerror="this.outerHTML='<div style=\\'padding:20px;text-align:center;color:#64748b;font-size:12px;\\'>ไม่พบภาพ</div>'">
        </div>
        <div class="text-panel">
          <div class="panel-title">📝 Text ที่สกัดมา (ใน Excel)</div>
          <div class="ans-box">${{nl2br(item.ans)}}</div>
          ${{fbHtml}}
        </div>
      </div>
    </div>
  `;
}}

let currentFilter = 'all';

function filterCards(filter) {{
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');

  const cards = document.querySelectorAll('.card');
  cards.forEach(card => {{
    const diff = parseFloat(card.dataset.diff);
    const h = parseFloat(card.dataset.h);
    let show = false;
    switch(filter) {{
      case 'all': show = true; break;
      case 'match': show = diff === 0; break;
      case 'diff': show = diff !== 0; break;
      case 'h2': show = h === 2.0; break;
      case 'h1': show = h === 1.0; break;
      case 'h0': show = h === 0.0; break;
    }}
    card.style.display = show ? '' : 'none';
  }});
}}

// Initial render
const grid = document.getElementById('grid');
DATA.forEach(item => {{
  grid.insertAdjacentHTML('beforeend', renderCard(item));
}});

// Keyboard: ESC to close lightbox
document.addEventListener('keydown', e => {{
  if (e.key === 'Escape') closeLightbox();
}});
</script>
</body>
</html>
"""

out = ROOT / "public" / "q1_compare.html"
out.write_text(HTML, encoding="utf-8")
print(f"Generated: {out}")
print(f"URL: http://localhost:8080/q1_compare.html")
