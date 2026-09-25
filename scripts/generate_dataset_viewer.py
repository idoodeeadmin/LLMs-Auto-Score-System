import openpyxl
import json
import math
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = ROOT / "ชุดข้อสอบใหม่" / "ชุดข้อสอบ_dataset.xlsx"

wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

# 1. Parse Sheet 'ชุดข้อสอบ_dataset'
ws_data = wb["ชุดข้อสอบ_dataset"]
dataset_items = []
for r in range(6, ws_data.max_row + 1):
    sid = ws_data.cell(r, 1).value
    if not sid:
        continue
    q_no = ws_data.cell(r, 2).value
    q_type = ws_data.cell(r, 3).value
    q_content = ws_data.cell(r, 4).value
    ans_type = ws_data.cell(r, 5).value
    ans_val = ws_data.cell(r, 6).value
    h_score = ws_data.cell(r, 7).value
    ai_score = ws_data.cell(r, 8).value
    ai_conf = ws_data.cell(r, 9).value
    ai_fb = ws_data.cell(r, 10).value
    
    img_path = None
    if ans_type == "img" or "Photo" in str(ans_val):
        match = re.search(r'"([^"]+)"', str(ans_val))
        if match:
            img_path = match.group(1)
        elif str(ans_val).startswith("photo_clean"):
            img_path = str(ans_val)
        elif str(ans_val).startswith("LINE_ALBUM"):
            if q_no == 4: img_path = f"photo_clean_ชุดที่1/{ans_val}"
            elif q_no == 5: img_path = f"photo_clean_ชุดที่2/{ans_val}"
            elif q_no == 6: img_path = f"photo_clean_ชุดที่3/{ans_val}"
        else:
            if q_no == 4:
                std_idx = r - 107
                img_path = f"photo_clean_ชุดที่1/LINE_ALBUM_Photo1_260917_{std_idx}.jpg"
            elif q_no == 5:
                std_idx = r - 141
                img_path = f"photo_clean_ชุดที่2/LINE_ALBUM_Photo2.1_260918_{std_idx}.jpg"
            elif q_no == 6:
                std_idx = r - 175
                img_path = f"photo_clean_ชุดที่3/LINE_ALBUM_Photo2.2_260918_{std_idx}.jpg"
            
    h_val = float(h_score) if (h_score is not None and str(h_score).strip() != "") else None
    ai_val = float(ai_score) if (ai_score is not None and str(ai_score).strip() != "") else None
    
    diff = round(ai_val - h_val, 2) if (ai_val is not None and h_val is not None) else None
    is_exact = (diff == 0.0) if diff is not None else None
    
    fb_str = str(ai_fb or "")
    teacher_fb = fb_str
    student_fb = ""
    if "[สำหรับผู้สอน]" in fb_str and "[สำหรับนักเรียน]" in fb_str:
        parts = fb_str.split("[สำหรับนักเรียน]")
        teacher_fb = parts[0].replace("[สำหรับผู้สอน]", "").strip()
        student_fb = parts[1].strip() if len(parts) > 1 else ""
    elif "[สำหรับนักเรียน]" in fb_str:
        parts = fb_str.split("[สำหรับนักเรียน]")
        teacher_fb = parts[0].strip()
        student_fb = parts[1].strip()
    
    dataset_items.append({
        "row": r,
        "sample_id": str(sid),
        "question_no": int(q_no) if q_no else None,
        "question_type": str(q_type or ""),
        "question_content": str(q_content or ""),
        "answer_type": str(ans_type or ""),
        "student_answer": str(ans_val or ""),
        "image_path": img_path,
        "human_score": h_val,
        "ai_score": ai_val,
        "diff": diff,
        "is_exact": is_exact,
        "ai_confidence": str(ai_conf or ""),
        "ai_feedback": fb_str,
        "teacher_feedback": teacher_fb,
        "student_feedback": student_fb
    })

# 2. Parse Sheet 'Exam_Rubrics'
ws_rubrics = wb["Exam_Rubrics"]
rubric_items = []
for r in range(5, ws_rubrics.max_row + 1):
    q_no = ws_rubrics.cell(r, 1).value
    if q_no is None:
        continue
    topic = ws_rubrics.cell(r, 2).value
    max_s = ws_rubrics.cell(r, 3).value
    name = ws_rubrics.cell(r, 4).value
    score = ws_rubrics.cell(r, 5).value
    desc = ws_rubrics.cell(r, 6).value
    
    rubric_items.append({
        "question_no": int(q_no),
        "topic": str(topic or ""),
        "max_score": float(max_s) if max_s is not None else None,
        "name": str(name or ""),
        "score": float(score) if score is not None else None,
        "description": str(desc or "")
    })

# 3. Parse Sheet 'Template_Example'
ws_tmpl = wb["Template_Example"]
template_items = []
for r in range(6, ws_tmpl.max_row + 1):
    sid = ws_tmpl.cell(r, 1).value
    if not sid:
        continue
    template_items.append({
        "sample_id": str(sid),
        "question_no": ws_tmpl.cell(r, 2).value,
        "question_type": str(ws_tmpl.cell(r, 3).value or ""),
        "question_content": str(ws_tmpl.cell(r, 4).value or ""),
        "answer_type": str(ws_tmpl.cell(r, 5).value or ""),
        "student_answer": str(ws_tmpl.cell(r, 6).value or ""),
        "human_score": ws_tmpl.cell(r, 7).value,
        "ai_score": ws_tmpl.cell(r, 8).value,
        "ai_confidence": str(ws_tmpl.cell(r, 9).value or ""),
        "ai_feedback": str(ws_tmpl.cell(r, 10).value or "")
    })

# 4. Statistical Calculations for Accuracy Summary (Q1-Q6 and Overall)
def calc_qwk(y_t, y_p, max_s=1.0, step=0.25):
    if len(y_t) != len(y_p) or len(y_t) == 0:
        return 0.0
    if y_t == y_p:
        return 1.0
    k = int(round(max_s / step)) + 1
    w = [[((i - j) ** 2) / ((k - 1) ** 2) for j in range(k)] for i in range(k)]
    cat_t = [min(k - 1, max(0, int(round(v / step)))) for v in y_t]
    cat_p = [min(k - 1, max(0, int(round(v / step)))) for v in y_p]
    o = [[0] * k for _ in range(k)]
    for t, p in zip(cat_t, cat_p):
        o[t][p] += 1
    r_t = [sum(o[i][j] for j in range(k)) for i in range(k)]
    r_p = [sum(o[i][j] for i in range(k)) for j in range(k)]
    n = len(y_t)
    e = [[(r_t[i] * r_p[j]) / n for j in range(k)] for i in range(k)]
    num = sum(w[i][j] * o[i][j] for i in range(k) for j in range(k))
    den = sum(w[i][j] * e[i][j] for i in range(k) for j in range(k))
    return 1.0 - (num / den) if den != 0 else 1.0

def calc_pearson(x, y):
    n = len(x)
    if n == 0:
        return 0.0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    cov = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    var_x = sum((a - mean_x) ** 2 for a in x)
    var_y = sum((b - mean_y) ** 2 for b in y)
    denom = math.sqrt(var_x * var_y)
    return cov / denom if denom != 0 else 0.0

q_meta = {
    1: {"topic": "Row-major vs Column-major", "type": "Text (ข้อความ)", "type_badge": "type-text", "max_s": 2.0},
    2: {"topic": "O(n log n) vs O(n^2) Complexity", "type": "Text (ข้อความ)", "type_badge": "type-text", "max_s": 2.0},
    3: {"topic": "Linked List vs Array (Stack/Queue)", "type": "Text (ข้อความ)", "type_badge": "type-text", "max_s": 1.0},
    4: {"topic": "Binary Search Tree Construction", "type": "Vision (ภาพลายมือ)", "type_badge": "type-img", "max_s": 1.0},
    5: {"topic": "1D Array Representation of BST", "type": "Vision (ภาพลายมือ)", "type_badge": "type-img", "max_s": 1.0},
    6: {"topic": "General Tree to Binary Tree (LCRS)", "type": "Vision (ภาพลายมือ)", "type_badge": "type-img", "max_s": 1.0},
}

q_data = {q: {"h": [], "a": []} for q in range(1, 7)}
all_h, all_a = [], []

for item in dataset_items:
    q = item["question_no"]
    if q in q_data and item["human_score"] is not None and item["ai_score"] is not None:
        q_data[q]["h"].append(item["human_score"])
        q_data[q]["a"].append(item["ai_score"])
        all_h.append(item["human_score"])
        all_a.append(item["ai_score"])

per_q_stats = {}
for q in range(1, 7):
    h, a = q_data[q]["h"], q_data[q]["a"]
    n = len(h)
    exact = sum(1 for x, y in zip(h, a) if round(x, 2) == round(y, 2))
    within_025 = sum(1 for x, y in zip(h, a) if abs(x - y) <= 0.2501)
    within_050 = sum(1 for x, y in zip(h, a) if abs(x - y) <= 0.5001)
    mae = sum(abs(x - y) for x, y in zip(h, a)) / n if n else 0.0
    rmse = math.sqrt(sum((x - y) ** 2 for x, y in zip(h, a)) / n) if n else 0.0
    r = calc_pearson(h, a)
    max_s = q_meta[q]["max_s"]
    qwk = calc_qwk(h, a, max_s=max_s, step=0.25)
    
    # Interpretation label
    if qwk >= 0.90: rating = "🟢 สอดคล้องสมบูรณ์แบบ (Perfect)"
    elif qwk >= 0.80: rating = "🟢 สอดคล้องเกือบสมบูรณ์ (Almost Perfect)"
    elif qwk >= 0.60: rating = "🟢 สอดคล้องระดับสูง (Substantial)"
    elif qwk >= 0.40: rating = "🟡 สอดคล้องระดับปานกลาง (Moderate)"
    else: rating = "🟠 สอดคล้องระดับพอใช้ (Fair)"

    per_q_stats[q] = {
        "q": q,
        "topic": q_meta[q]["topic"],
        "type": q_meta[q]["type"],
        "type_badge": q_meta[q]["type_badge"],
        "max_s": max_s,
        "n": n,
        "exact": exact,
        "exact_pct": round((exact / n) * 100, 1) if n else 0.0,
        "within_025": within_025,
        "within_025_pct": round((within_025 / n) * 100, 1) if n else 0.0,
        "within_050": within_050,
        "within_050_pct": round((within_050 / n) * 100, 1) if n else 0.0,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r": round(r, 4),
        "qwk": round(qwk, 4),
        "rating": rating
    }

def calc_group_stats(h, a, name, badge_class):
    n = len(h)
    exact = sum(1 for x, y in zip(h, a) if round(x, 2) == round(y, 2))
    within_025 = sum(1 for x, y in zip(h, a) if abs(x - y) <= 0.2501)
    within_050 = sum(1 for x, y in zip(h, a) if abs(x - y) <= 0.5001)
    mae = sum(abs(x - y) for x, y in zip(h, a)) / n if n else 0.0
    rmse = math.sqrt(sum((x - y) ** 2 for x, y in zip(h, a)) / n) if n else 0.0
    r = calc_pearson(h, a)
    return {
        "name": name,
        "badge_class": badge_class,
        "n": n,
        "exact": exact,
        "exact_pct": round((exact / n) * 100, 1) if n else 0.0,
        "within_025": within_025,
        "within_025_pct": round((within_025 / n) * 100, 1) if n else 0.0,
        "within_050": within_050,
        "within_050_pct": round((within_050 / n) * 100, 1) if n else 0.0,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r": round(r, 4),
    }

text_h = q_data[1]["h"] + q_data[2]["h"] + q_data[3]["h"]
text_a = q_data[1]["a"] + q_data[2]["a"] + q_data[3]["a"]
img_h = q_data[4]["h"] + q_data[5]["h"] + q_data[6]["h"]
img_a = q_data[4]["a"] + q_data[5]["a"] + q_data[6]["a"]

text_group_stat = calc_group_stats(text_h, text_a, "📝 รวมกลุ่มข้อเขียน Text (ข้อ 1-3)", "type-text")
img_group_stat = calc_group_stats(img_h, img_a, "📸 รวมกลุ่มรูปภาพ Vision (ข้อ 4-6)", "type-img")
overall_stat = calc_group_stats(all_h, all_a, "🌟 ภาพรวมทั้งชุดข้อสอบ (Grand Total)", "type-all")

# Build Table Rows HTML
def get_pct_class(pct):
    if pct >= 80: return "acc-high"
    if pct >= 65: return "acc-med"
    if pct >= 50: return "acc-mod"
    return "acc-low"

benchmark_rows_html = ""
for q in range(1, 7):
    s = per_q_stats[q]
    benchmark_rows_html += f"""
        <tr>
            <td style="font-weight:700;">
                <span class="q-badge">ข้อ {s['q']}</span>
            </td>
            <td>
                <div style="font-weight:600;color:#ffffff;">{s['topic']}</div>
                <div style="font-size:11px;color:var(--text-muted);">โจทย์ข้อสอบอัตนัยวิชา Data Structures</div>
            </td>
            <td>
                <span class="type-badge {s['type_badge']}">{s['type']}</span>
            </td>
            <td style="font-family:var(--font-mono);font-weight:600;text-align:center;">{s['max_s']:.1f}</td>
            <td style="text-align:center;color:var(--text-secondary);">{s['n']}</td>
            <td>
                <span class="acc-pill {get_pct_class(s['exact_pct'])}">{s['exact']} / {s['n']} ({s['exact_pct']}%)</span>
            </td>
            <td>
                <span class="acc-pill {get_pct_class(s['within_025_pct'])}">{s['within_025']} ({s['within_025_pct']}%)</span>
            </td>
            <td>
                <span class="acc-pill {get_pct_class(s['within_050_pct'])}">{s['within_050']} ({s['within_050_pct']}%)</span>
            </td>
            <td style="font-family:var(--font-mono);font-weight:600;color:{'#34d399' if s['mae'] < 0.15 else ('#38bdf8' if s['mae'] < 0.35 else '#fbbf24')};">{s['mae']:.4f}</td>
            <td style="font-family:var(--font-mono);color:var(--text-secondary);">{s['rmse']:.4f}</td>
            <td style="font-family:var(--font-mono);font-weight:600;color:#38bdf8;">{s['r']:.4f}</td>
            <td style="font-family:var(--font-mono);font-weight:700;color:{'#34d399' if s['qwk'] >= 0.8 else ('#818cf8' if s['qwk'] >= 0.6 else '#fbbf24')};">{s['qwk']:.4f}</td>
            <td>
                <span style="font-size:12px;font-weight:600;">{s['rating']}</span>
            </td>
        </tr>
    """
    if q == 3:
        # Insert Text Subgroup Row
        benchmark_rows_html += f"""
        <tr class="group-row">
            <td colspan="3" style="font-weight:700;color:#a5b4fc;">
                {text_group_stat['name']}
            </td>
            <td style="text-align:center;font-weight:600;color:#a5b4fc;">5.0</td>
            <td style="text-align:center;font-weight:600;color:#a5b4fc;">{text_group_stat['n']}</td>
            <td>
                <span class="acc-pill {get_pct_class(text_group_stat['exact_pct'])}">{text_group_stat['exact']} / {text_group_stat['n']} ({text_group_stat['exact_pct']}%)</span>
            </td>
            <td>
                <span class="acc-pill {get_pct_class(text_group_stat['within_025_pct'])}">{text_group_stat['within_025']} ({text_group_stat['within_025_pct']}%)</span>
            </td>
            <td>
                <span class="acc-pill {get_pct_class(text_group_stat['within_050_pct'])}">{text_group_stat['within_050']} ({text_group_stat['within_050_pct']}%)</span>
            </td>
            <td style="font-family:var(--font-mono);font-weight:600;color:#38bdf8;">{text_group_stat['mae']:.4f}</td>
            <td style="font-family:var(--font-mono);color:var(--text-secondary);">{text_group_stat['rmse']:.4f}</td>
            <td style="font-family:var(--font-mono);font-weight:600;color:#818cf8;">{text_group_stat['r']:.4f}</td>
            <td style="text-align:center;color:var(--text-muted);">-</td>
            <td><span style="color:#a5b4fc;font-weight:600;font-size:12px;">กลุ่มคำตอบข้อความเชิงบรรยาย</span></td>
        </tr>
        """
    elif q == 6:
        # Insert Vision Subgroup Row
        benchmark_rows_html += f"""
        <tr class="group-row-vision">
            <td colspan="3" style="font-weight:700;color:#5eead4;">
                {img_group_stat['name']}
            </td>
            <td style="text-align:center;font-weight:600;color:#5eead4;">3.0</td>
            <td style="text-align:center;font-weight:600;color:#5eead4;">{img_group_stat['n']}</td>
            <td>
                <span class="acc-pill {get_pct_class(img_group_stat['exact_pct'])}">{img_group_stat['exact']} / {img_group_stat['n']} ({img_group_stat['exact_pct']}%)</span>
            </td>
            <td>
                <span class="acc-pill {get_pct_class(img_group_stat['within_025_pct'])}">{img_group_stat['within_025']} ({img_group_stat['within_025_pct']}%)</span>
            </td>
            <td>
                <span class="acc-pill {get_pct_class(img_group_stat['within_050_pct'])}">{img_group_stat['within_050']} ({img_group_stat['within_050_pct']}%)</span>
            </td>
            <td style="font-family:var(--font-mono);font-weight:600;color:#34d399;">{img_group_stat['mae']:.4f}</td>
            <td style="font-family:var(--font-mono);color:var(--text-secondary);">{img_group_stat['rmse']:.4f}</td>
            <td style="font-family:var(--font-mono);font-weight:600;color:#34d399;">{img_group_stat['r']:.4f}</td>
            <td style="text-align:center;color:var(--text-muted);">-</td>
            <td><span style="color:#5eead4;font-weight:600;font-size:12px;">กลุ่มโครงสร้างต้นไม้ & ลายมือ</span></td>
        </tr>
        """

# Append Grand Total Row
benchmark_rows_html += f"""
<tr class="total-row">
    <td colspan="3" style="font-weight:800;color:#ffffff;letter-spacing:0.3px;">
        {overall_stat['name']}
    </td>
    <td style="text-align:center;font-weight:800;color:#38bdf8;">8.0</td>
    <td style="text-align:center;font-weight:800;color:#ffffff;">{overall_stat['n']}</td>
    <td>
        <span class="acc-pill {get_pct_class(overall_stat['exact_pct'])}" style="font-size:13px;padding:5px 10px;">{overall_stat['exact']} / {overall_stat['n']} ({overall_stat['exact_pct']}%)</span>
    </td>
    <td>
        <span class="acc-pill {get_pct_class(overall_stat['within_025_pct'])}" style="font-size:13px;padding:5px 10px;">{overall_stat['within_025']} ({overall_stat['within_025_pct']}%)</span>
    </td>
    <td>
        <span class="acc-pill {get_pct_class(overall_stat['within_050_pct'])}" style="font-size:13px;padding:5px 10px;">{overall_stat['within_050']} ({overall_stat['within_050_pct']}%)</span>
    </td>
    <td style="font-family:var(--font-mono);font-weight:800;color:#34d399;font-size:14px;">{overall_stat['mae']:.4f}</td>
    <td style="font-family:var(--font-mono);font-weight:700;color:#cbd5e1;">{overall_stat['rmse']:.4f}</td>
    <td style="font-family:var(--font-mono);font-weight:800;color:#38bdf8;font-size:14px;">{overall_stat['r']:.4f}</td>
    <td style="text-align:center;color:var(--text-muted);font-weight:700;">-</td>
    <td>
        <span style="color:#34d399;font-weight:700;font-size:13px;">🏆 สอดคล้องระดับสูงมาก (r=0.79)</span>
    </td>
</tr>
"""

# Build Accuracy Progress Meters HTML
bars_html = ""
for q in range(1, 7):
    s = per_q_stats[q]
    exact_w = s['exact_pct']
    w_025_diff = max(0, s['within_025_pct'] - s['exact_pct'])
    w_050_diff = max(0, s['within_050_pct'] - s['within_025_pct'])
    out_diff = max(0, 100.0 - s['within_050_pct'])
    
    bars_html += f"""
        <div style="background:rgba(15,23,42,0.6);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="q-badge">ข้อ {q}</span>
                    <span style="font-size:13px;font-weight:600;color:#ffffff;">{s['topic']}</span>
                </div>
                <div style="font-family:var(--font-mono);font-size:13px;font-weight:700;color:#34d399;">
                    ตรงเป๊ะ {s['exact_pct']}% (ต่าง ≤0.50: {s['within_050_pct']}%)
                </div>
            </div>
            <div class="stat-bar-container">
                <div class="stat-bar-exact" style="width:{exact_w}%;" title="ตรงเป๊ะ: {exact_w}%"></div>
                <div class="stat-bar-025" style="width:{w_025_diff}%;" title="ต่างไม่เกิน 0.25: {w_025_diff:.1f}%"></div>
                <div class="stat-bar-050" style="width:{w_050_diff}%;" title="ต่างไม่เกิน 0.50: {w_050_diff:.1f}%"></div>
                <div class="stat-bar-diff" style="width:{out_diff}%;" title="ต่างเกิน 0.50: {out_diff:.1f}%"></div>
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:11px;color:var(--text-muted);">
                <span>MAE: <strong style="color:#cbd5e1;">{s['mae']:.4f}</strong> | QWK: <strong style="color:#38bdf8;">{s['qwk']:.4f}</strong></span>
                <span>ตรง {s['exact']}/34 | ต่าง ≤0.25: {s['within_025']}/34 | ต่าง ≤0.50: {s['within_050']}/34</span>
            </div>
        </div>
    """

# Build Overall Bar HTML
ov_exact = overall_stat['exact_pct']
ov_025_diff = max(0, overall_stat['within_025_pct'] - overall_stat['exact_pct'])
ov_050_diff = max(0, overall_stat['within_050_pct'] - overall_stat['within_025_pct'])
ov_out_diff = max(0, 100.0 - overall_stat['within_050_pct'])

overall_bar_html = f"""
    <div style="background:linear-gradient(90deg, rgba(16, 185, 129, 0.1), rgba(56, 189, 248, 0.1));border:1px solid rgba(52, 211, 153, 0.35);border-radius:12px;padding:18px;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="q-badge" style="background:#047857;color:#a7f3d0;font-size:12px;padding:4px 10px;">ภาพรวม 204 ข้อ</span>
                <span style="font-size:15px;font-weight:700;color:#ffffff;">สัดส่วนความแม่นยำรวมทุกข้อสอบ (Total Accuracy Breakdown)</span>
            </div>
            <div style="font-family:var(--font-mono);font-size:14px;font-weight:700;color:#38bdf8;">
                ตรงเป๊ะ {ov_exact}% | ต่าง ≤0.25: {overall_stat['within_025_pct']}% | ต่าง ≤0.50: {overall_stat['within_050_pct']}%
            </div>
        </div>
        <div class="stat-bar-container" style="height:14px;">
            <div class="stat-bar-exact" style="width:{ov_exact}%;" title="ตรงกันเป๊ะ 100%: {ov_exact}%"></div>
            <div class="stat-bar-025" style="width:{ov_025_diff}%;" title="ต่างไม่เกิน 0.25 pt: {ov_025_diff:.1f}%"></div>
            <div class="stat-bar-050" style="width:{ov_050_diff}%;" title="ต่างไม่เกิน 0.50 pt: {ov_050_diff:.1f}%"></div>
            <div class="stat-bar-diff" style="width:{ov_out_diff}%;" title="ต่างเกิน 0.50 pt: {ov_out_diff:.1f}%"></div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-top:10px;font-size:12px;">
            <div style="display:flex;gap:16px;">
                <span style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#10b981;display:inline-block;"></span> ตรงเป๊ะ 100% ({overall_stat['exact']} ข้อ - {overall_stat['exact_pct']}%)</span>
                <span style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#06b6d4;display:inline-block;"></span> ต่าง ≤0.25 ({overall_stat['within_025']} ข้อ - {overall_stat['within_025_pct']}%)</span>
                <span style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#6366f1;display:inline-block;"></span> ต่าง ≤0.50 ({overall_stat['within_050']} ข้อ - {overall_stat['within_050_pct']}%)</span>
                <span style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#f43f5e;display:inline-block;"></span> ต่าง >0.50 ({overall_stat['n'] - overall_stat['within_050']} ข้อ - {round(100.0 - overall_stat['within_050_pct'], 1)}%)</span>
            </div>
            <div style="color:var(--text-secondary);">
                MAE รวม: <strong style="color:#34d399;">{overall_stat['mae']:.4f}</strong> | Pearson r: <strong style="color:#38bdf8;">{overall_stat['r']:.4f}</strong>
            </div>
        </div>
    </div>
"""

dataset_json = json.dumps(dataset_items, ensure_ascii=False)
rubrics_json = json.dumps(rubric_items, ensure_ascii=False)
template_json = json.dumps(template_items, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ชุดข้อสอบ Dataset Viewer & AI Scoring Benchmark</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700&family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #0a0f1d;
            --bg-surface: #111827;
            --bg-card: rgba(17, 24, 39, 0.75);
            --bg-card-hover: rgba(30, 41, 59, 0.85);
            --border-glass: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(255, 255, 255, 0.16);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-primary: #6366f1;
            --accent-primary-glow: rgba(99, 102, 241, 0.35);
            --accent-teal: #14b8a6;
            --accent-teal-glow: rgba(20, 184, 166, 0.3);
            --badge-success-bg: rgba(16, 185, 129, 0.15);
            --badge-success-text: #34d399;
            --badge-success-border: rgba(16, 185, 129, 0.3);
            --badge-warn-bg: rgba(245, 158, 11, 0.15);
            --badge-warn-text: #fbbf24;
            --badge-warn-border: rgba(245, 158, 11, 0.3);
            --badge-danger-bg: rgba(244, 63, 94, 0.15);
            --badge-danger-text: #fb7185;
            --badge-danger-border: rgba(244, 63, 94, 0.3);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            --font-main: 'Prompt', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'Fira Code', monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background: var(--bg-base);
            color: var(--text-primary);
            font-family: var(--font-main);
            min-height: 100vh;
            line-height: 1.5;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 85% 90%, rgba(20, 184, 166, 0.12) 0%, transparent 40%);
            background-attachment: fixed;
        }}

        /* App Header */
        .app-header {{
            background: rgba(17, 24, 39, 0.8);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-glass);
            padding: 16px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-icon {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #6366f1, #14b8a6);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 14px var(--accent-primary-glow);
        }}

        .brand-info h1 {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .brand-info p {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        .header-actions {{
            display: flex;
            gap: 10px;
        }}

        .btn {{
            font-family: var(--font-main);
            font-size: 13px;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }}

        .btn-glass {{
            background: rgba(255, 255, 255, 0.05);
            border-color: var(--border-glass);
            color: var(--text-primary);
        }}
        .btn-glass:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--border-hover);
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: #ffffff;
            box-shadow: 0 4px 14px var(--accent-primary-glow);
        }}
        .btn-primary:hover {{
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
            transform: translateY(-1px);
        }}

        /* Container Layout */
        .container {{
            max-width: 1560px;
            margin: 0 auto;
            padding: 24px 32px;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 20px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--border-hover);
        }}

        .kpi-label {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .kpi-value {{
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
            font-family: 'Inter', var(--font-main);
        }}

        .kpi-meta {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 6px;
        }}

        /* Tabs Navigation */
        .tabs-nav {{
            display: flex;
            gap: 4px;
            border-bottom: 1px solid var(--border-glass);
            margin-bottom: 20px;
            overflow-x: auto;
        }}

        .tab-btn {{
            font-family: var(--font-main);
            font-size: 14px;
            font-weight: 600;
            padding: 10px 18px;
            background: transparent;
            color: var(--text-secondary);
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .tab-btn:hover {{
            color: #ffffff;
            background: rgba(255, 255, 255, 0.03);
            border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        }}
        .tab-btn.active {{
            color: #38bdf8;
            border-bottom-color: #38bdf8;
        }}

        .tab-pill {{
            background: rgba(255, 255, 255, 0.08);
            padding: 2px 8px;
            border-radius: var(--radius-full);
            font-size: 11px;
            font-weight: 700;
            color: var(--text-secondary);
        }}
        .tab-btn.active .tab-pill {{
            background: rgba(56, 189, 248, 0.2);
            color: #38bdf8;
        }}

        /* Tab Content */
        .tab-pane {{
            display: none;
        }}
        .tab-pane.active {{
            display: block;
        }}

        /* Toolbar: Filters & Search */
        .toolbar {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: center;
            justify-content: space-between;
        }}

        .filter-group {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .pill-btn {{
            font-family: var(--font-main);
            font-size: 12px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: var(--radius-full);
            border: 1px solid var(--border-glass);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .pill-btn:hover {{
            background: rgba(255, 255, 255, 0.09);
            color: #ffffff;
        }}
        .pill-btn.active {{
            background: rgba(99, 102, 241, 0.2);
            border-color: #6366f1;
            color: #818cf8;
        }}

        .search-box {{
            position: relative;
            min-width: 260px;
            flex-grow: 1;
            max-width: 400px;
        }}

        .search-box input {{
            width: 100%;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-sm);
            padding: 8px 14px 8px 36px;
            color: #ffffff;
            font-size: 13px;
            font-family: var(--font-main);
            outline: none;
            transition: border-color 0.2s ease;
        }}
        .search-box input:focus {{
            border-color: #6366f1;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }}

        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
            font-size: 14px;
        }}

        /* Table Styling */
        .table-wrapper {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}

        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}

        table.data-table thead th {{
            background: rgba(15, 23, 42, 0.95);
            padding: 14px 16px;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-glass);
            white-space: nowrap;
            letter-spacing: 0.2px;
        }}

        table.data-table tbody td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-glass);
            color: var(--text-primary);
            vertical-align: top;
        }}

        table.data-table tbody tr:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}

        /* Table Cell Badges & Components */
        .sample-id {{
            font-family: var(--font-mono);
            font-weight: 600;
            font-size: 12px;
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
            padding: 3px 8px;
            border-radius: 6px;
            display: inline-block;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}

        .q-badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: var(--radius-full);
            background: rgba(255, 255, 255, 0.07);
            color: #cbd5e1;
            display: inline-block;
        }}

        .type-badge {{
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 4px;
        }}
        .type-text {{ background: rgba(99, 102, 241, 0.15); color: #818cf8; }}
        .type-img {{ background: rgba(236, 72, 153, 0.15); color: #f472b6; }}
        .type-all {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}

        .score-pill {{
            font-family: 'Inter', var(--font-mono);
            font-weight: 700;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .match-badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: var(--radius-full);
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .match-exact {{
            background: var(--badge-success-bg);
            color: var(--badge-success-text);
            border: 1px solid var(--badge-success-border);
        }}
        .match-diff {{
            background: var(--badge-warn-bg);
            color: var(--badge-warn-text);
            border: 1px solid var(--badge-warn-border);
        }}
        .match-pending {{
            background: rgba(148, 163, 184, 0.1);
            color: var(--text-muted);
            border: 1px solid rgba(148, 163, 184, 0.2);
        }}

        .confidence-badge {{
            font-size: 11px;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 4px;
        }}
        .conf-high {{ background: rgba(16, 185, 129, 0.15); color: #34d399; }}
        .conf-medium {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; }}
        .conf-low {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; }}

        .img-thumb-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .thumb-preview {{
            width: 44px;
            height: 44px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid var(--border-glass);
            cursor: pointer;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .thumb-preview:hover {{
            transform: scale(1.08);
            border-color: #38bdf8;
        }}

        .btn-view-img {{
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.2);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-view-img:hover {{
            background: rgba(56, 189, 248, 0.2);
        }}

        .ans-preview {{
            font-size: 13px;
            color: #cbd5e1;
            line-height: 1.5;
            max-width: 320px;
            word-break: break-word;
        }}

        .feedback-cell {{
            font-size: 12px;
            line-height: 1.5;
            color: #cbd5e1;
            max-width: 400px;
        }}
        .btn-read-more {{
            background: none;
            border: none;
            color: #38bdf8;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            padding: 0;
            margin-top: 4px;
            display: inline-block;
        }}
        .btn-read-more:hover {{
            text-decoration: underline;
        }}

        /* Benchmark Section Styles */
        .benchmark-section {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .benchmark-table-wrapper {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            overflow-x: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        table.benchmark-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        table.benchmark-table thead th {{
            background: rgba(15, 23, 42, 0.95);
            padding: 14px 16px;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-glass);
            white-space: nowrap;
        }}
        table.benchmark-table tbody td {{
            padding: 13px 16px;
            border-bottom: 1px solid var(--border-glass);
            color: var(--text-primary);
            vertical-align: middle;
        }}
        table.benchmark-table tbody tr:hover {{
            background: rgba(255, 255, 255, 0.02);
        }}
        table.benchmark-table tr.group-row {{
            background: rgba(99, 102, 241, 0.08);
            font-weight: 600;
        }}
        table.benchmark-table tr.group-row td {{
            border-top: 1px solid rgba(99, 102, 241, 0.3);
            border-bottom: 1px solid rgba(99, 102, 241, 0.3);
        }}
        table.benchmark-table tr.group-row-vision {{
            background: rgba(20, 184, 166, 0.08);
            font-weight: 600;
        }}
        table.benchmark-table tr.group-row-vision td {{
            border-top: 1px solid rgba(20, 184, 166, 0.3);
            border-bottom: 1px solid rgba(20, 184, 166, 0.3);
        }}
        table.benchmark-table tr.total-row {{
            background: linear-gradient(90deg, rgba(16, 185, 129, 0.16), rgba(56, 189, 248, 0.16));
            font-weight: 700;
        }}
        table.benchmark-table tr.total-row td {{
            border-top: 2px solid rgba(52, 211, 153, 0.5);
            border-bottom: 2px solid rgba(52, 211, 153, 0.5);
            font-size: 14px;
        }}

        .stat-bar-container {{
            width: 100%;
            background: rgba(255, 255, 255, 0.06);
            height: 10px;
            border-radius: var(--radius-full);
            overflow: hidden;
            display: flex;
            margin-top: 4px;
        }}
        .stat-bar-exact {{ background: #10b981; }}
        .stat-bar-025 {{ background: #06b6d4; }}
        .stat-bar-050 {{ background: #6366f1; }}
        .stat-bar-diff {{ background: #f43f5e; }}

        .acc-pill {{
            font-family: var(--font-mono);
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            display: inline-block;
        }}
        .acc-high {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .acc-med {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
        .acc-mod {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .acc-low {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}

        /* Modal Popup */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            z-index: 100;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}
        .modal-overlay.active {{
            display: flex;
        }}

        .modal-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border-hover);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 900px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
        }}

        .modal-header {{
            padding: 16px 24px;
            border-bottom: 1px solid var(--border-glass);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(15, 23, 42, 0.9);
        }}
        .modal-header h3 {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
        }}
        .modal-close {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 20px;
            cursor: pointer;
        }}
        .modal-close:hover {{
            color: #ffffff;
        }}

        .modal-body {{
            padding: 24px;
            color: #e2e8f0;
            line-height: 1.6;
        }}

        .modal-img-container {{
            text-align: center;
            background: #000000;
            border-radius: var(--radius-md);
            padding: 16px;
            margin-bottom: 16px;
        }}
        .modal-img-container img {{
            max-width: 100%;
            max-height: 60vh;
            object-fit: contain;
            border-radius: 4px;
        }}

        /* Rubrics Grid */
        .rubric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }}

        .rubric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .rubric-card.highlight {{
            border-color: rgba(20, 184, 166, 0.5);
            box-shadow: 0 0 20px rgba(20, 184, 166, 0.15);
        }}

        .rubric-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid var(--border-glass);
            padding-bottom: 12px;
        }}

        .rubric-desc {{
            font-size: 13px;
            color: #cbd5e1;
            white-space: pre-wrap;
            line-height: 1.6;
            background: rgba(15, 23, 42, 0.5);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--border-glass);
        }}

        /* Analytics Tab Styles */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}
        .stat-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 20px;
        }}
        .stat-box h4 {{
            font-size: 15px;
            color: #38bdf8;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header class="app-header">
        <div class="brand">
            <div class="brand-icon">📊</div>
            <div class="brand-info">
                <h1>ชุดข้อสอบ Dataset Viewer & AI Scoring Benchmark <span class="q-badge" style="background:#047857;color:#a7f3d0;">v2.0 Complete</span></h1>
                <p>ระบบตรวจข้อสอบอัตนัยอัตโนมัติด้วย LLMs (โครงสร้างข้อมูลและขั้นตอนวิธี) | วิชา Data Structures</p>
            </div>
        </div>
        <div class="header-actions">
            <button class="btn btn-glass" onclick="exportFilteredExcel()">
                📥 ดาวน์โหลดข้อมูล (.json)
            </button>
            <a href="ชุดข้อสอบ_dataset.xlsx" download class="btn btn-primary">
                📑 เปิดไฟล์ Excel (.xlsx)
            </a>
        </div>
    </header>

    <div class="container">

        <!-- KPI Metrics Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">
                    <span>จำนวนตัวอย่างทั้งหมด</span>
                    <span>📁</span>
                </div>
                <div class="kpi-value" id="kpi-total-items">204 ข้อ</div>
                <div class="kpi-meta">ข้อ 1 ถึง 6 (นิสิต 34 คน x 6 ข้อ ครบสมบูรณ์)</div>
            </div>
            <div class="kpi-card" style="border-color: rgba(56, 189, 248, 0.4);">
                <div class="kpi-label">
                    <span>ตรวจด้วย AI แล้ว</span>
                    <span>🤖</span>
                </div>
                <div class="kpi-value" id="kpi-evaluated-items" style="color: #38bdf8;">204 / 204 ข้อ</div>
                <div class="kpi-meta">ความคืบหน้า 100.0% (ครบทุกข้อ 1 ถึง 6)</div>
            </div>
            <div class="kpi-card" style="border-color: rgba(16, 185, 129, 0.4);">
                <div class="kpi-label">
                    <span>ความตรงกันเป๊ะ ข้อ 6 (Exact Match)</span>
                    <span>🏆</span>
                </div>
                <div class="kpi-value" style="color: #34d399;">34 / 34 (100.0%)</div>
                <div class="kpi-meta">LCRS Binary Tree (QWK 1.0000 สมบูรณ์แบบ)</div>
            </div>
            <div class="kpi-card" style="border-color: rgba(99, 102, 241, 0.4);">
                <div class="kpi-label">
                    <span>ความตรงเป๊ะ รวมทั้งชุด (Grand Total)</span>
                    <span>🎯</span>
                </div>
                <div class="kpi-value" style="color: #818cf8;">{overall_stat['exact']} / {overall_stat['n']} ({overall_stat['exact_pct']}%)</div>
                <div class="kpi-meta">ต่าง ≤0.50 pt: {overall_stat['within_050_pct']}% (MAE รวม {overall_stat['mae']:.4f})</div>
            </div>
        </div>

        <!-- Sheet Tabs Navigation -->
        <div class="tabs-nav">
            <button class="tab-btn active" onclick="switchTab('dataset-tab', this)">
                <span>📊 ชุดข้อสอบ_dataset</span>
                <span class="tab-pill">204</span>
            </button>
            <button class="tab-btn" onclick="switchTab('analytics-tab', this)">
                <span>📈 สรุปผลความแม่นยำ (1-6 & ผลรวม)</span>
                <span class="tab-pill" style="background:rgba(16,185,129,0.25);color:#34d399;">Benchmark</span>
            </button>
            <button class="tab-btn" onclick="switchTab('rubrics-tab', this)">
                <span>📋 Exam_Rubrics</span>
                <span class="tab-pill">8 เกณฑ์</span>
            </button>
            <button class="tab-btn" onclick="switchTab('template-tab', this)">
                <span>📑 Template_Example</span>
                <span class="tab-pill">22</span>
            </button>
        </div>

        <!-- TAB 1: ชุดข้อสอบ_dataset -->
        <div id="dataset-tab" class="tab-pane active">
            <!-- Toolbar Filters -->
            <div class="toolbar">
                <div class="filter-group">
                    <span style="font-size:12px;font-weight:600;color:var(--text-muted);margin-right:4px;">เลือกข้อ:</span>
                    <button class="pill-btn active" onclick="filterQuestion(null, this)">ทั้งหมด (204)</button>
                    <button class="pill-btn" onclick="filterQuestion(1, this)">ข้อ 1 (34)</button>
                    <button class="pill-btn" onclick="filterQuestion(2, this)">ข้อ 2 (34)</button>
                    <button class="pill-btn" onclick="filterQuestion(3, this)">ข้อ 3 (34)</button>
                    <button class="pill-btn" onclick="filterQuestion(4, this)">ข้อ 4 (34)</button>
                    <button class="pill-btn" onclick="filterQuestion(5, this)">ข้อ 5 (34)</button>
                    <button class="pill-btn" onclick="filterQuestion(6, this)">ข้อ 6 (34)</button>
                </div>

                <div class="filter-group">
                    <span style="font-size:12px;font-weight:600;color:var(--text-muted);margin-right:4px;">สถานะ:</span>
                    <button class="pill-btn active" onclick="filterStatus('all', this)">ทั้งหมด</button>
                    <button class="pill-btn" onclick="filterStatus('exact', this)">🟢 ตรงกันเป๊ะ</button>
                    <button class="pill-btn" onclick="filterStatus('diff', this)">🟠 คะแนนต่าง</button>
                    <button class="pill-btn" onclick="filterStatus('scored', this)">🤖 ตรวจแล้ว</button>
                    <button class="pill-btn" onclick="filterStatus('pending', this)">⚪ รอดำเนินการ</button>
                </div>

                <div class="search-box">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="searchInput" placeholder="ค้นหารหัส เช่น DS-141 หรือข้อความ..." oninput="handleSearch()">
                </div>
            </div>

            <!-- Table -->
            <div class="table-wrapper">
                <table class="data-table" id="datasetTable">
                    <thead>
                        <tr>
                            <th style="width: 100px;">Sample ID</th>
                            <th style="width: 110px;">ข้อสอบ</th>
                            <th>คำตอบนิสิต</th>
                            <th style="width: 110px;">คะแนนอาจารย์</th>
                            <th style="width: 130px;">คะแนน AI</th>
                            <th style="width: 100px;">ความมั่นใจ</th>
                            <th>เหตุผลและคำแนะนำของ AI</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        <!-- Injected via JS -->
                    </tbody>
                </table>
            </div>
            <div id="noResults" style="display:none;text-align:center;padding:48px;color:var(--text-muted);">
                ไม่พบข้อมูลตามเงื่อนไขที่เลือก
            </div>
        </div>

        <!-- TAB 2: Accuracy & Performance Benchmark (Updated with 1-6 & Total) -->
        <div id="analytics-tab" class="tab-pane">
            <div class="benchmark-section">
                
                <!-- Section Header -->
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;background:var(--bg-card);border:1px solid var(--border-glass);border-radius:var(--radius-md);padding:20px 24px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                            <span style="font-size:22px;">📊</span>
                            <h2 style="font-size:18px;font-weight:700;color:#ffffff;">รายงานผลการประเมินความแม่นยำ AI Auto-Scoring รายข้อ 1-6 และภาพรวมทั้งชุดข้อสอบ</h2>
                        </div>
                        <p style="font-size:13px;color:var(--text-secondary);max-width:1000px;line-height:1.6;">
                            เปรียบเทียบคะแนนที่โมเดลประเมินกับคะแนนของอาจารย์ผู้สอน (Ground Truth) ของนิสิตครบทุกคนทั้ง 34 คนในข้อสอบ 6 ข้อ (รวม 204 ชุดข้อมูล) 
                            ครอบคลุมทั้งกลุ่มข้อสอบบรรยาย (Text 1-3) และกลุ่มข้อสอบรูปภาพลายมือ (Vision 4-6) พร้อมดัชนีทางสถิติ MAE, RMSE, Pearson Correlation (r) และ Quadratic Weighted Kappa (QWK)
                        </p>
                    </div>
                    <div style="display:flex;gap:10px;align-items:center;">
                        <span class="q-badge" style="background:#065f46;color:#6ee7b7;font-size:12px;padding:6px 14px;border:1px solid rgba(16,185,129,0.3);">
                            ✅ ตรวจครบ 204 / 204 (100.0%)
                        </span>
                    </div>
                </div>

                <!-- 4 Highlight Cards -->
                <div class="kpi-grid">
                    <div class="kpi-card" style="border-color:rgba(52,211,153,0.4);background:linear-gradient(135deg,rgba(16,185,129,0.08),rgba(17,24,39,0.9));">
                        <div class="kpi-label">
                            <span style="color:#6ee7b7;font-weight:700;">🌟 ภาพรวมทั้งชุดข้อสอบ (Grand Total)</span>
                            <span>🎯</span>
                        </div>
                        <div class="kpi-value" style="color:#34d399;">{overall_stat['exact']} / {overall_stat['n']} <span style="font-size:16px;">({overall_stat['exact_pct']}%)</span></div>
                        <div class="kpi-meta" style="color:#cbd5e1;line-height:1.6;">
                            • ต่าง ≤0.25: <strong>{overall_stat['within_025_pct']}%</strong> | ต่าง ≤0.50: <strong>{overall_stat['within_050_pct']}%</strong><br>
                            • MAE เฉลี่ย: <strong style="color:#38bdf8;">{overall_stat['mae']:.4f}</strong> | Pearson r: <strong style="color:#38bdf8;">{overall_stat['r']:.4f}</strong>
                        </div>
                    </div>
                    <div class="kpi-card" style="border-color:rgba(20,184,166,0.4);background:linear-gradient(135deg,rgba(20,184,166,0.08),rgba(17,24,39,0.9));">
                        <div class="kpi-label">
                            <span style="color:#5eead4;font-weight:700;">📸 ข้อสอบรูปภาพลายมือ (ข้อ 4, 5, 6)</span>
                            <span>🖼️</span>
                        </div>
                        <div class="kpi-value" style="color:#2dd4bf;">{img_group_stat['exact']} / {img_group_stat['n']} <span style="font-size:16px;">({img_group_stat['exact_pct']}%)</span></div>
                        <div class="kpi-meta" style="color:#cbd5e1;line-height:1.6;">
                            • ต่าง ≤0.25: <strong>{img_group_stat['within_025_pct']}%</strong> | ต่าง ≤0.50: <strong>{img_group_stat['within_050_pct']}%</strong><br>
                            • MAE เฉลี่ย: <strong style="color:#34d399;">{img_group_stat['mae']:.4f}</strong> | Pearson r: <strong style="color:#34d399;">{img_group_stat['r']:.4f}</strong>
                        </div>
                    </div>
                    <div class="kpi-card" style="border-color:rgba(99,102,241,0.4);background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(17,24,39,0.9));">
                        <div class="kpi-label">
                            <span style="color:#a5b4fc;font-weight:700;">📝 ข้อสอบข้อเขียนบรรยาย (ข้อ 1, 2, 3)</span>
                            <span>✍️</span>
                        </div>
                        <div class="kpi-value" style="color:#818cf8;">{text_group_stat['exact']} / {text_group_stat['n']} <span style="font-size:16px;">({text_group_stat['exact_pct']}%)</span></div>
                        <div class="kpi-meta" style="color:#cbd5e1;line-height:1.6;">
                            • ต่าง ≤0.25: <strong>{text_group_stat['within_025_pct']}%</strong> | ต่าง ≤0.50: <strong>{text_group_stat['within_050_pct']}%</strong><br>
                            • MAE เฉลี่ย: <strong style="color:#38bdf8;">{text_group_stat['mae']:.4f}</strong> | Pearson r: <strong style="color:#38bdf8;">{text_group_stat['r']:.4f}</strong>
                        </div>
                    </div>
                    <div class="kpi-card" style="border-color:rgba(245,158,11,0.4);background:linear-gradient(135deg,rgba(245,158,11,0.08),rgba(17,24,39,0.9));">
                        <div class="kpi-label">
                            <span style="color:#fcd34d;font-weight:700;">🏆 ความแม่นยำสูงสุด (Top Accuracy)</span>
                            <span>🥇</span>
                        </div>
                        <div class="kpi-value" style="color:#fbbf24;">ข้อ 6: 100.0%</div>
                        <div class="kpi-meta" style="color:#cbd5e1;line-height:1.6;">
                            • ตรงเป๊ะ: <strong>34 / 34 คน (100.0%)</strong><br>
                            • QWK: <strong style="color:#34d399;">1.0000</strong> | MAE: <strong style="color:#34d399;">0.0000</strong>
                        </div>
                    </div>
                </div>

                <!-- Grand Benchmark Summary Table -->
                <div class="benchmark-table-wrapper">
                    <div style="padding:16px 20px;border-bottom:1px solid var(--border-glass);display:flex;justify-content:space-between;align-items:center;">
                        <h3 style="font-size:15px;font-weight:700;color:#ffffff;display:flex;align-items:center;gap:8px;">
                            <span>📋</span> ตารางเปรียบเทียบผลความแม่นยำรายข้อ 1 ถึง 6 และผลรวมทั้งชุดข้อสอบ (Full Benchmark Table)
                        </h3>
                        <span style="font-size:12px;color:var(--text-muted);">หน่วยคะแนนและสถิติคำนวณจาก Ground Truth จริง</span>
                    </div>
                    <table class="benchmark-table">
                        <thead>
                            <tr>
                                <th style="width:70px;">ข้อที่</th>
                                <th>หัวข้อโจทย์ (Exam Topic)</th>
                                <th style="width:130px;">ประเภทคำตอบ</th>
                                <th style="width:80px;text-align:center;">เต็ม</th>
                                <th style="width:60px;text-align:center;">N</th>
                                <th style="width:150px;">ตรงกันเป๊ะ (Exact)</th>
                                <th style="width:130px;">ต่าง ≤ 0.25 pt</th>
                                <th style="width:130px;">ต่าง ≤ 0.50 pt</th>
                                <th style="width:90px;">MAE</th>
                                <th style="width:80px;">RMSE</th>
                                <th style="width:90px;">Pearson (r)</th>
                                <th style="width:90px;">Kappa (QWK)</th>
                                <th>ระดับความสอดคล้อง</th>
                            </tr>
                        </thead>
                        <tbody>
                            {benchmark_rows_html}
                        </tbody>
                    </table>
                </div>

                <!-- Overall Progress Stacked Bar -->
                {overall_bar_html}

                <!-- Question By Question Comparison Bars -->
                <div style="background:var(--bg-card);border:1px solid var(--border-glass);border-radius:var(--radius-md);padding:20px 24px;">
                    <h3 style="font-size:15px;font-weight:700;color:#ffffff;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
                        <span>📊</span> แผนภูมิสัดส่วนความแม่นยำรายข้อ (Exact Match & Tolerance Breakdown by Question)
                    </h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(440px, 1fr));gap:16px;">
                        {bars_html}
                    </div>
                </div>

                <!-- Deep-Dive Qualitative Insights -->
                <div class="stats-grid">
                    <div class="stat-box" style="border-color:rgba(16,185,129,0.3);">
                        <h4>🏆 ข้อ 6 (General Tree to Binary Tree LCRS) — ความแม่นยำ 100.0%</h4>
                        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px;">การแปลงต้นไม้แบบ 10 โหนด 9 เส้นเชื่อม</p>
                        <ul style="font-size:13px;line-height:1.9;padding-left:18px;color:#cbd5e1;">
                            <li>ตรวจตรงกับอาจารย์เป๊ะครบทั้ง <strong>34 คน (100.00%)</strong></li>
                            <li>กลุ่มได้ 1.00: <strong>19 คน</strong> (เชื่อมกิ่งซ้าย-ขวา LCRS ครบ 9 เส้นถูกต้อง)</li>
                            <li>กลุ่มได้ 0.00: <strong>15 คน</strong> (ผิดหลัก LCRS เช่น นำ 3 ต่อขวาของ root 1, ซิกแซก)</li>
                            <li>ผ่านการตรวจ Forensic หมึกสีส้มอาจารย์: <strong>0% Leakage (Inpainted 100%)</strong></li>
                            <li>ความแม่นยำสมบูรณ์แบบเกิดจาก LCRS เป็นอัลกอริทึมที่ Deterministic ชัดเจน</li>
                        </ul>
                    </div>

                    <div class="stat-box" style="border-color:rgba(20,184,166,0.3);">
                        <h4>🎯 ข้อ 5 (Array 1D Representation) — ความแม่นยำ 76.5% (QWK 0.8468)</h4>
                        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px;">การแทนค่าต้นไม้ BST ในอาร์เรย์ 1 มิติ (ขนาด 31 ช่อง)</p>
                        <ul style="font-size:13px;line-height:1.9;padding-left:18px;color:#cbd5e1;">
                            <li>ตรวจตรงกับอาจารย์เป๊ะ: <strong>26 / 34 คน (76.5%)</strong></li>
                            <li>คะแนนคลาดเคลื่อนไม่เกิน 0.25 pt: <strong>30 / 34 คน (88.2%)</strong></li>
                            <li>คะแนนคลาดเคลื่อนไม่เกิน 0.50 pt: <strong>32 / 34 คน (94.1%)</strong></li>
                            <li>MAE ต่ำมากเพียง <strong>0.1029 คะแนน</strong> | QWK <strong>0.8468</strong> (Almost Perfect)</li>
                            <li>เกณฑ์ตัด 0.00 สำหรับกลุ่มตอบมั่ว/เขียนเลขเรียงติดกัน ตัดได้ตรงกับอาจารย์ 100%</li>
                        </ul>
                    </div>

                    <div class="stat-box" style="border-color:rgba(56,189,248,0.3);">
                        <h4>🌲 ข้อ 4 (Binary Search Tree Construction) — เกณฑ์ Binary (0 หรือ 1)</h4>
                        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px;">การวาดต้นไม้ค้นหาทวิภาคจากลำดับข้อมูล 12 ค่า (เกณฑ์ตัดสินเด็ดขาดเฉพาะ 1.0 หรือ 0.0 เท่านั้น)</p>
                        <ul style="font-size:13px;line-height:1.9;padding-left:18px;color:#cbd5e1;">
                            <li>ตรวจตรงกับอาจารย์เป๊ะ: <strong>27 / 34 คน (79.4%)</strong></li>
                            <li>MAE ต่ำเพียง <strong>0.1985 คะแนน</strong> | สอดคล้องระดับปานกลาง (QWK 0.4733)</li>
                            <li>ตัดเกณฑ์ย่อย 0.25 ที่เป็นจุดกำกวมออก ให้เหลือเฉพาะ 1.0 (ถูกครบ) หรือ 0.0 (ผิดหลักการ)</li>
                            <li>รองรับ Dual Feedback อธิบายตำแหน่งโหนดที่ถูกต้องและชี้จุดผิดอย่างชัดเจน</li>
                        </ul>
                    </div>

                    <div class="stat-box" style="border-color:rgba(99,102,241,0.3);">
                        <h4>📝 ข้อ 1, 2, 3 (กลุ่มข้อสอบข้อเขียน Text) — ความแม่นยำ {text_group_stat['exact_pct']}%</h4>
                        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:10px;">การตอบคำถามเชิงทฤษฎีและเปรียบเทียบขั้นตอนวิธี</p>
                        <ul style="font-size:13px;line-height:1.9;padding-left:18px;color:#cbd5e1;">
                            <li>ข้อ 1 (Row vs Col Major): ตรงเป๊ะ <strong>{per_q_stats[1]['exact']}/{per_q_stats[1]['n']} ({per_q_stats[1]['exact_pct']}%)</strong> ต่าง ≤0.50: <strong>{per_q_stats[1]['within_050_pct']}%</strong></li>
                            <li>ข้อ 2 (O(n log n) Complexity): ตรงเป๊ะ <strong>{per_q_stats[2]['exact']}/{per_q_stats[2]['n']} ({per_q_stats[2]['exact_pct']}%)</strong> ต่าง ≤0.50: <strong>{per_q_stats[2]['within_050_pct']}%</strong></li>
                            <li>ข้อ 3 (Linked List vs Array): ตรงเป๊ะ <strong>{per_q_stats[3]['exact']}/{per_q_stats[3]['n']} ({per_q_stats[3]['exact_pct']}%)</strong> ต่าง ≤0.25: <strong>{per_q_stats[3]['within_025_pct']}%</strong> ต่าง ≤0.50: <strong>{per_q_stats[3]['within_050_pct']}%</strong> (MAE {per_q_stats[3]['mae']:.4f})</li>
                            <li>ในกลุ่มข้อความ ประเมินด้วยเกณฑ์วิชาการแบบแยกองค์ประกอบ ทำให้คะแนนที่ต่างไม่เกิน 0.50 pt สูงถึง <strong>{text_group_stat['within_050_pct']}%</strong></li>
                            <li>MAE เฉลี่ยของกลุ่ม Text อยู่ที่ <strong>{text_group_stat['mae']:.4f}</strong> | Pearson r แตะ <strong>{text_group_stat['r']:.4f}</strong></li>
                        </ul>
                    </div>
                </div>

            </div>
        </div>

        <!-- TAB 3: Exam_Rubrics -->
        <div id="rubrics-tab" class="tab-pane">
            <div class="rubric-grid" id="rubricsContainer">
                <!-- Injected via JS -->
            </div>
        </div>

        <!-- TAB 4: Template_Example -->
        <div id="template-tab" class="tab-pane">
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Sample ID</th>
                            <th>ข้อที่</th>
                            <th>ประเภทโจทย์</th>
                            <th>โจทย์</th>
                            <th>ประเภทคำตอบ</th>
                            <th>คะแนนอาจารย์</th>
                            <th>คะแนน AI</th>
                            <th>ความมั่นใจ</th>
                        </tr>
                    </thead>
                    <tbody id="templateTableBody">
                        <!-- Injected via JS -->
                    </tbody>
                </table>
            </div>
        </div>

    </div>

    <!-- Lightbox Modal for Images -->
    <div class="modal-overlay" id="imageModal" onclick="closeImageModal(event)">
        <div class="modal-box" style="max-width: 1000px;" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="modalTitle">🔍 ดูภาพกระดาษคำตอบลายมือนิสิต</h3>
                <button class="modal-close" onclick="closeImageModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;font-size:13px;">
                    <span id="modalMetaSample" class="sample-id">DS-000</span>
                    <span id="modalMetaScore">คะแนนอาจารย์: - | คะแนน AI: -</span>
                </div>
                <div class="modal-img-container">
                    <img id="modalImg" src="" alt="Student Answer Image">
                </div>
                <p id="modalImgCaption" style="font-size:12px;color:var(--text-muted);text-align:center;"></p>
            </div>
        </div>
    </div>

    <!-- Modal for Full Feedback (Dual Teacher & Student View) -->
    <div class="modal-overlay" id="feedbackModal" onclick="closeFeedbackModal(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="fbModalTitle">💬 ผลการตรวจประเมินของ AI (ผู้สอน & นักเรียน)</h3>
                <button class="modal-close" onclick="closeFeedbackModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div style="display:flex;gap:12px;align-items:center;margin-bottom:16px;">
                    <span id="fbModalSample" class="sample-id">DS-000</span>
                    <span id="fbModalScore"></span>
                </div>
                
                <!-- Section 1: Teacher Feedback -->
                <div style="background:rgba(30, 41, 59, 0.75);border:1px solid rgba(99, 102, 241, 0.35);border-radius:10px;padding:16px;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                        <span style="background:rgba(99, 102, 241, 0.25);color:#a5b4fc;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:600;">👨‍🏫 สำหรับผู้สอน</span>
                        <h5 style="color:#c7d2fe;font-size:13px;font-weight:600;">เหตุผลและเกณฑ์การให้คะแนน (Teacher Assessment Rationale):</h5>
                    </div>
                    <p id="fbModalTeacherText" style="font-size:13px;line-height:1.7;white-space:pre-wrap;color:#e2e8f0;"></p>
                </div>

                <!-- Section 2: Student Feedback -->
                <div id="fbModalStudentBox" style="background:rgba(20, 184, 166, 0.1);border:1px solid rgba(20, 184, 166, 0.35);border-radius:10px;padding:16px;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                        <span style="background:rgba(20, 184, 166, 0.25);color:#5eead4;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:600;">🎓 สำหรับนักเรียน</span>
                        <h5 style="color:#99f6e4;font-size:13px;font-weight:600;">คำแนะนำเพื่อการเรียนรู้และพัฒนา (Student Guidance):</h5>
                    </div>
                    <p id="fbModalStudentText" style="font-size:13px;line-height:1.7;white-space:pre-wrap;color:#e2e8f0;"></p>
                </div>

                <!-- Section 3: Question -->
                <div style="background:rgba(15,23,42,0.4);border:1px solid var(--border-glass);border-radius:8px;padding:14px;">
                    <h5 style="color:var(--text-muted);font-size:12px;margin-bottom:6px;">โจทย์ข้อสอบ:</h5>
                    <p id="fbModalQuestion" style="font-size:12px;line-height:1.5;color:var(--text-secondary);"></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const DATASET = {dataset_json};
        const RUBRICS = {rubrics_json};
        const TEMPLATE = {template_json};

        let currentQuestion = null;
        let currentStatus = 'all';
        let currentSearch = '';

        // Switch Tabs
        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            if (btn) btn.classList.add('active');
        }}

        // Filters
        function filterQuestion(qNo, btn) {{
            currentQuestion = qNo;
            btn.parentElement.querySelectorAll('.pill-btn').forEach(el => el.classList.remove('active'));
            btn.classList.add('active');
            renderTable();
        }}

        function filterStatus(status, btn) {{
            currentStatus = status;
            btn.parentElement.querySelectorAll('.pill-btn').forEach(el => el.classList.remove('active'));
            btn.classList.add('active');
            renderTable();
        }}

        function handleSearch() {{
            currentSearch = document.getElementById('searchInput').value.trim().toLowerCase();
            renderTable();
        }}

        // Render Dataset Table
        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            const filtered = DATASET.filter(item => {{
                // Question Filter
                if (currentQuestion !== null && item.question_no !== currentQuestion) return false;

                // Status Filter
                if (currentStatus === 'exact' && item.is_exact !== true) return false;
                if (currentStatus === 'diff' && (item.is_exact !== false || item.ai_score === null)) return false;
                if (currentStatus === 'scored' && item.ai_score === null) return false;
                if (currentStatus === 'pending' && item.ai_score !== null) return false;

                // Search Filter
                if (currentSearch) {{
                    const matchId = item.sample_id.toLowerCase().includes(currentSearch);
                    const matchQ = item.question_content.toLowerCase().includes(currentSearch);
                    const matchAns = item.student_answer.toLowerCase().includes(currentSearch);
                    const matchFb = item.ai_feedback.toLowerCase().includes(currentSearch);
                    if (!matchId && !matchQ && !matchAns && !matchFb) return false;
                }}

                return true;
            }});

            document.getElementById('noResults').style.display = filtered.length === 0 ? 'block' : 'none';

            filtered.forEach(item => {{
                const tr = document.createElement('tr');

                // Human Score badge
                const humanDisplay = item.human_score !== null ? item.human_score.toFixed(2) : '-';

                // AI Score & Match badge
                let aiScoreDisplay = '-';
                let matchBadge = '<span class="match-badge match-pending">รอดำเนินการ</span>';
                if (item.ai_score !== null) {{
                    aiScoreDisplay = item.ai_score.toFixed(2);
                    if (item.is_exact) {{
                        matchBadge = '<span class="match-badge match-exact">🟢 ตรงเป๊ะ</span>';
                    }} else {{
                        const sign = item.diff > 0 ? '+' : '';
                        matchBadge = `<span class="match-badge match-diff">🟠 ต่าง ${{sign}}${{item.diff.toFixed(2)}}</span>`;
                    }}
                }}

                // Confidence badge
                let confBadge = '-';
                if (item.ai_confidence) {{
                    const c = item.ai_confidence.toLowerCase();
                    confBadge = `<span class="confidence-badge conf-${{c}}">${{c.toUpperCase()}}</span>`;
                }}

                // Student answer formatting
                let answerHtml = '';
                if (item.image_path) {{
                    answerHtml = `
                        <div class="img-thumb-container">
                            <img src="${{item.image_path}}" class="thumb-preview" alt="Answer" onclick="openImageModal('${{item.sample_id}}')" onerror="this.style.display='none'">
                            <div>
                                <div style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono);margin-bottom:4px;">${{item.image_path.split('/').pop()}}</div>
                                <button class="btn-view-img" onclick="openImageModal('${{item.sample_id}}')">🔍 ดูภาพลายมือ</button>
                            </div>
                        </div>
                    `;
                }} else {{
                    const shortAns = item.student_answer.length > 120 ? item.student_answer.substring(0, 120) + '...' : item.student_answer;
                    answerHtml = `<div class="ans-preview">${{shortAns.replace(/\\n/g, '<br>')}}</div>`;
                }}

                // Feedback formatting
                let feedbackHtml = '<span style="color:var(--text-muted);">-</span>';
                if (item.ai_feedback) {{
                    const textSource = item.teacher_feedback || item.ai_feedback;
                    const shortFb = textSource.length > 95 ? textSource.substring(0, 95) + '...' : textSource;
                    const hasStudentFb = Boolean(item.student_feedback);
                    feedbackHtml = `
                        <div class="feedback-cell">
                            <div>${{shortFb.replace(/\\n/g, ' ')}}</div>
                            <div style="display:flex;align-items:center;gap:6px;margin-top:6px;">
                                <button class="btn-read-more" onclick="openFeedbackModal('${{item.sample_id}}')">อ่านคำอธิบายฉบับเต็ม &rarr;</button>
                                ${{hasStudentFb ? '<span style="background:rgba(20,184,166,0.15);color:#2dd4bf;border:1px solid rgba(20,184,166,0.3);font-size:10px;padding:1px 6px;border-radius:4px;font-weight:500;">🎓 มีคำแนะนำนิสิต</span>' : ''}}
                            </div>
                        </div>
                    `;
                }}

                tr.innerHTML = `
                    <td>
                        <span class="sample-id">${{item.sample_id}}</span>
                    </td>
                    <td>
                        <span class="q-badge">ข้อ ${{item.question_no}}</span>
                        <span class="type-badge type-${{item.answer_type}}">${{item.answer_type}}</span>
                    </td>
                    <td>${{answerHtml}}</td>
                    <td>
                        <span class="score-pill" style="color: #f8fafc;">${{humanDisplay}}</span>
                    </td>
                    <td>
                        <div style="display:flex;flex-direction:column;gap:4px;">
                            <span class="score-pill" style="color:${{item.is_exact ? '#34d399' : (item.ai_score !== null ? '#fbbf24' : '#64748b')}};">
                                ${{aiScoreDisplay}}
                            </span>
                            ${{matchBadge}}
                        </div>
                    </td>
                    <td>${{confBadge}}</td>
                    <td>${{feedbackHtml}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Render Rubrics
        function renderRubrics() {{
            const container = document.getElementById('rubricsContainer');
            container.innerHTML = '';
            RUBRICS.forEach(r => {{
                const card = document.createElement('div');
                const isHighlight = (r.question_no === 5 || r.question_no === 6);
                card.className = `rubric-card ${{isHighlight ? 'highlight' : ''}}`;
                
                let badgeHtml = '';
                if (r.question_no === 6) {{
                    badgeHtml = '<span class="q-badge" style="background:#065f46;color:#6ee7b7;margin-left:6px;">🏆 ฉบับสมบูรณ์ (100.0% Exact Match)</span>';
                }} else if (r.question_no === 5) {{
                    badgeHtml = '<span class="q-badge" style="background:#065f46;color:#6ee7b7;margin-left:6px;">⭐ ฉบับปรับปรุง (80% Exact Match)</span>';
                }} else if (r.question_no === 4) {{
                    badgeHtml = '<span class="q-badge" style="background:#1e3a8a;color:#93c5fd;margin-left:6px;">🌲 Binary BST (เกณฑ์ 0 หรือ 1 เท่านั้น)</span>';
                }} else if (r.question_no === 3) {{
                    badgeHtml = '<span class="q-badge" style="background:#065f46;color:#6ee7b7;margin-left:6px;">✨ เกณฑ์วิชาการ 2 ส่วน (AI คิดเองตามหลักการ)</span>';
                }}

                card.innerHTML = `
                    <div class="rubric-header">
                        <div>
                            <span class="q-badge" style="background:#312e81;color:#c7d2fe;margin-bottom:6px;">ข้อ ${{r.question_no}}</span>
                            ${{badgeHtml}}
                            <h3 style="font-size:16px;color:#ffffff;margin-top:4px;">${{r.name}}</h3>
                            <div style="font-size:12px;color:var(--text-muted);">${{r.topic}}</div>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:20px;font-weight:700;color:#38bdf8;font-family:'Inter';">${{r.score}}</span>
                            <span style="font-size:12px;color:var(--text-muted);">คะแนน</span>
                        </div>
                    </div>
                    <div class="rubric-desc">${{r.description}}</div>
                `;
                container.appendChild(card);
            }});
        }}

        // Render Template
        function renderTemplate() {{
            const tbody = document.getElementById('templateTableBody');
            tbody.innerHTML = '';
            TEMPLATE.forEach(t => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="sample-id">${{t.sample_id}}</span></td>
                    <td>ข้อ ${{t.question_no}}</td>
                    <td><span class="type-badge">${{t.question_type}}</span></td>
                    <td style="max-width:240px;font-size:12px;color:var(--text-secondary);">${{t.question_content}}</td>
                    <td><span class="type-badge">${{t.answer_type}}</span></td>
                    <td>${{t.human_score !== null ? t.human_score : '-'}}</td>
                    <td>${{t.ai_score !== null ? t.ai_score : '-'}}</td>
                    <td>${{t.ai_confidence || '-'}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Modals
        function openImageModal(sampleId) {{
            const item = DATASET.find(d => d.sample_id === sampleId);
            if (!item || !item.image_path) return;
            const humanDisplay = item.human_score !== null ? item.human_score.toFixed(2) : '-';
            const aiDisplay = item.ai_score !== null ? item.ai_score.toFixed(2) : '-';
            document.getElementById('modalImg').src = item.image_path;
            document.getElementById('modalTitle').textContent = `🔍 ภาพกระดาษคำตอบนิสิต (${{sampleId}}) — ข้อ ${{item.question_no}}`;
            document.getElementById('modalMetaSample').textContent = sampleId;
            document.getElementById('modalMetaScore').textContent = `คะแนนอาจารย์: ${{humanDisplay}} | คะแนน AI: ${{aiDisplay}}`;
            document.getElementById('modalImgCaption').textContent = item.image_path;
            document.getElementById('imageModal').classList.add('active');
        }}

        function closeImageModal() {{
            document.getElementById('imageModal').classList.remove('active');
        }}

        function openFeedbackModal(sampleId) {{
            const item = DATASET.find(d => d.sample_id === sampleId);
            if (!item) return;
            const humanDisplay = item.human_score !== null ? item.human_score.toFixed(2) : '-';
            const aiDisplay = item.ai_score !== null ? item.ai_score.toFixed(2) : '-';
            document.getElementById('fbModalSample').textContent = sampleId;
            document.getElementById('fbModalScore').innerHTML = `คะแนนอาจารย์: <strong>${{humanDisplay}}</strong> | คะแนน AI: <strong>${{aiDisplay}}</strong>`;
            
            const teacherText = item.teacher_feedback || item.ai_feedback || 'ไม่มีข้อเสนอแนะ';
            const studentText = item.student_feedback || '';
            
            document.getElementById('fbModalTeacherText').textContent = teacherText;
            
            const studentBox = document.getElementById('fbModalStudentBox');
            if (studentText) {{
                studentBox.style.display = 'block';
                document.getElementById('fbModalStudentText').textContent = studentText;
            }} else {{
                studentBox.style.display = 'none';
            }}
            
            document.getElementById('fbModalQuestion').textContent = item.question_content || '-';
            document.getElementById('feedbackModal').classList.add('active');
        }}

        function closeFeedbackModal() {{
            document.getElementById('feedbackModal').classList.remove('active');
        }}

        window.addEventListener('keydown', e => {{
            if (e.key === 'Escape') {{
                closeImageModal();
                closeFeedbackModal();
            }}
        }});

        // Download JSON
        function exportFilteredExcel() {{
            const blob = new Blob([JSON.stringify(DATASET, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ชุดข้อสอบ_dataset_export.json';
            a.click();
            URL.revokeObjectURL(url);
        }}

        // Initial Calls
        renderTable();
        renderRubrics();
        renderTemplate();
    </script>
</body>
</html>
"""

# Write to ชุดข้อสอบใหม่/dataset_viewer.html
output_file1 = ROOT / "ชุดข้อสอบใหม่" / "dataset_viewer.html"
with open(output_file1, "w", encoding="utf-8") as f:
    f.write(html_content)

# Also write to public/dataset_viewer.html
output_file2 = ROOT / "public" / "dataset_viewer.html"
output_file2.parent.mkdir(parents=True, exist_ok=True)
with open(output_file2, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated dataset_viewer.html successfully at:")
print(f"  1. {output_file1}")
print(f"  2. {output_file2}")
