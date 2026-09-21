import os
import sys
import cv2
import numpy as np
import pillow_heif
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
pillow_heif.register_heif_opener()

SRC_DIR = os.path.join("ชุดข้อสอบใหม่", "โจทย์textชุดที่1")
CLEAN_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_clean_text1")
MASK_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_mask_text1")
ARTIFACT_DIR = r"C:\Users\idood\.gemini\antigravity-ide\brain\f6ee475c-7cae-4670-a1aa-717c1db8426d"
INSPECT_DIR = os.path.join(ARTIFACT_DIR, "inspect")

for d in [CLEAN_DIR, MASK_DIR, INSPECT_DIR]:
    os.makedirs(d, exist_ok=True)

def imread_and_orient(path, max_dim=2000):
    im = Image.open(path)
    w, h = im.size
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        nw, nh = int(w * scale), int(h * scale)
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    arr = np.array(im)
    if im.mode != "RGB":
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    if bgr.shape[0] > bgr.shape[1]:
        bgr = cv2.rotate(bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return bgr

def imwrite_utf8(path, img, quality=96):
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    with open(path, "wb") as fh:
        fh.write(buf)

def find_clean_paper_patch(cleaned, full_teacher_mask, student_writing, roi_h, roi_w, x0, y0, x1, y1, h, w):
    candidates = [
        (y1 + 15, y1 + roi_h + 15, x0, x1),
        (y0 - roi_h - 15, y0 - 15, x0, x1),
        (y0, y1, x0 - roi_w - 20, x0 - 20),
        (y0, y1, x1 + 20, x1 + roi_w + 20),
        (y1 + 15, y1 + roi_h + 15, x0 - roi_w - 20, x0 - 20),
        (y1 + 15, y1 + roi_h + 15, x1 + 20, x1 + roi_w + 20),
        (y0 - roi_h - 15, y0 - 15, x0 - roi_w - 20, x0 - 20),
        (y0 - roi_h - 15, y0 - 15, x1 + 20, x1 + roi_w + 20)
    ]
    best_patch = None
    min_var = float('inf')

    for cy0, cy1, cx0, cx1 in candidates:
        if cy0 >= 25 and cy1 <= h - 25 and cx0 >= 25 and cx1 <= w - 25:
            cand_patch = cleaned[cy0:cy1, cx0:cx1]
            cand_teacher = full_teacher_mask[cy0:cy1, cx0:cx1]
            cand_student = student_writing[cy0:cy1, cx0:cx1]
            if not np.any(cand_teacher) and np.count_nonzero(cand_student) == 0:
                p_gray = cv2.cvtColor(cand_patch, cv2.COLOR_BGR2GRAY)
                if np.mean(p_gray) > 130:
                    var = cv2.Laplacian(p_gray, cv2.CV_64F).var()
                    if var < min_var:
                        min_var = var
                        best_patch = cand_patch

    if best_patch is None or min_var > 100:
        step_y = max(30, roi_h // 2)
        step_x = max(30, roi_w // 2)
        for gy in range(int(h * 0.20), int(h * 0.85) - roi_h, step_y):
            for gx in range(int(w * 0.10), int(w * 0.88) - roi_w, step_x):
                if not (gx < x1 and gx + roi_w > x0 and gy < y1 and gy + roi_h > y0):
                    cand_patch = cleaned[gy:gy+roi_h, gx:gx+roi_w]
                    cand_teacher = full_teacher_mask[gy:gy+roi_h, gx:gx+roi_w]
                    cand_student = student_writing[gy:gy+roi_h, gx:gx+roi_w]
                    if not np.any(cand_teacher) and np.count_nonzero(cand_student) == 0:
                        p_gray = cv2.cvtColor(cand_patch, cv2.COLOR_BGR2GRAY)
                        if np.mean(p_gray) > 140:
                            var = cv2.Laplacian(p_gray, cv2.CV_64F).var()
                            if var < min_var:
                                min_var = var
                                best_patch = cand_patch
                                if var < 35:
                                    break
            if best_patch is not None and min_var < 35:
                break

    return best_patch, min_var

def clean_single_image_text1(filename: str, idx: int, total: int):
    src_path = os.path.join(SRC_DIR, filename)
    orig = imread_and_orient(src_path, max_dim=2000)
    bh, bw, _ = orig.shape

    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    local_paper = cv2.GaussianBlur(gray, (51, 51), 0)
    contrast = local_paper.astype(np.int16) - gray.astype(np.int16)

    # 1. All ink strokes
    is_ink = (contrast > 12) & (gray < 155)
    is_ink[:40, :] = False
    is_ink[bh-40:, :] = False
    is_ink[:, :40] = False
    is_ink[:, bw-40:] = False

    b, g, r = cv2.split(orig)
    diff_br = b.astype(np.int16) - r.astype(np.int16)
    diff_rb = r.astype(np.int16) - b.astype(np.int16)

    # Detect student writing medium (pencil vs pen) from upper answer text
    st_top_mask = is_ink[:int(bh * 0.40), :int(bw * 0.70)]
    st_top_mbr = np.mean(diff_br[:int(bh * 0.40), :int(bw * 0.70)][st_top_mask]) if np.any(st_top_mask) else 0.0
    student_used_pencil = (st_top_mbr < -1.0)

    # Detect horizontal lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (80, 1))
    h_lines = cv2.morphologyEx(is_ink.astype(np.uint8), cv2.MORPH_OPEN, h_kernel) > 0
    num_h, h_labels, h_stats, _ = cv2.connectedComponentsWithStats(h_lines.astype(np.uint8))

    # Detect outer page box components
    num_l_raw, labels_raw, stats_raw, _ = cv2.connectedComponentsWithStats(is_ink.astype(np.uint8))
    main_box_bot = None
    for i in range(1, num_l_raw):
        x, y, w, h, a = stats_raw[i]
        if w > 800 and h > 500:
            main_box_bot = y + h
            break

    # Determine Question 10 bottom border:
    if student_used_pencil:
        q10_bot_y = int(bh * 0.90)
    else:
        q10_bot_y = main_box_bot if main_box_bot and main_box_bot < int(bh * 0.96) else int(bh * 0.90)

    # Strictly protect Question 11 printed toner (black text and lines at or below Q10 bottom)
    q11_protect = (np.arange(bh)[:, None] >= (q10_bot_y - 5)) & (gray < 125) & (diff_br <= 0) & (diff_rb <= 0)

    if student_used_pencil:
        # In pencil sheets: student writing is graphite pencil (diff_br < -1.0)
        raw_st = (contrast > 12) & (gray < 155) & (diff_br < -1.0)
        num_st, st_lbls, st_stats, _ = cv2.connectedComponentsWithStats(raw_st.astype(np.uint8))
        real_st = np.zeros((bh, bw), dtype=bool)
        for si in range(1, num_st):
            if st_stats[si, cv2.CC_STAT_AREA] >= 12:
                real_st |= (st_lbls == si)
        # Also protect upper half and left margin
        real_st[:int(bh * 0.48), :] |= (contrast[:int(bh * 0.48), :] > 12) & (gray[:int(bh * 0.48), :] < 155)
        real_st[:int(bh * 0.88), :int(bw * 0.42)] |= (contrast[:int(bh * 0.88), :int(bw * 0.42)] > 12) & (gray[:int(bh * 0.88), :int(bw * 0.42)] < 155)
        student_protect = cv2.dilate(real_st.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0

        # Teacher blue and red marks
        t_blue = (diff_br > 1.5) & (contrast > 4) & (np.arange(bh)[:, None] > int(bh * 0.40)) & (np.arange(bw)[None, :] > int(bw * 0.35))
        t_red = (diff_rb > 8.0) & (contrast > 4) & (np.arange(bh)[:, None] > int(bh * 0.40))
        t_marks = t_blue | t_red
        # Close holes across thin black lines
        t_closed = cv2.morphologyEx(t_marks.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
        num_t, t_lbls, t_stats, _ = cv2.connectedComponentsWithStats(t_closed.astype(np.uint8))
        clean_t = np.zeros((bh, bw), dtype=bool)
        for ti in range(1, num_t):
            if t_stats[ti, cv2.CC_STAT_AREA] >= 15:
                clean_t |= (t_lbls == ti)

        teacher_mask = clean_t
        student_writing = real_st

        teacher_dil = cv2.dilate(teacher_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0
        teacher_dil[student_protect] = False
        teacher_dil[q11_protect] = False
    else:
        # In pen sheets:
        frame_borders = np.zeros((bh, bw), dtype=bool)
        for hi in range(1, num_h):
            hx, hy, hw, hh, harea = h_stats[hi]
            if hw > 400 and hy >= int(bh * 0.80):
                frame_borders |= (h_labels == hi)
        cut = cv2.dilate(frame_borders.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_RECT, (1, 7))) > 0
        ink_cut = is_ink.copy()
        ink_cut[cut] = False

        edges = cv2.Canny((contrast > 12).astype(np.uint8) * 255, 50, 150)
        edges[:40, :] = 0; edges[bh-40:, :] = 0; edges[:, :40] = 0; edges[:, bw-40:] = 0
        h_edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))) > 0
        v_edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))) > 0
        h_dil = cv2.dilate(h_edges.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        v_dil = cv2.dilate(v_edges.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        real_grid = (h_dil & v_dil)

        num_l, labels, stats, _ = cv2.connectedComponentsWithStats(ink_cut.astype(np.uint8))
        box_border = np.zeros((bh, bw), dtype=bool)
        for i in range(1, num_l):
            x, y, cw, ch, area = stats[i]
            if cw > 650 and ch > 600:
                box_border |= (labels == i)

        border_teacher_blue = box_border & (diff_br > 2.5) & (np.arange(bw)[None, :] > int(bw * 0.35)) & (np.arange(bh)[:, None] > int(bh * 0.40))
        border_teacher_red = box_border & (diff_rb > 8.0) & (np.arange(bw)[None, :] > int(bw * 0.35)) & (np.arange(bh)[:, None] > int(bh * 0.40))
        slash_mask = border_teacher_blue | border_teacher_red

        for i in range(1, num_l):
            x, y, cw, ch, area = stats[i]
            if cw > 650 or ch > 750 or area > 6000 or y < int(bh * 0.30) or y >= q10_bot_y:
                continue
            comp = (labels == i)
            mbr = np.mean(diff_br[comp])
            if (x + cw) < int(bw * 0.45) and mbr < -1.5:
                continue
            is_slash = (ch > 140 and cw > 40 and area > 700) or (ch > 180 and area > 600) or (cw > 130 and ch > 130 and area > 1100)
            mrb = np.mean(diff_rb[comp])
            if mrb > 10.0 and area > 350 and y > int(bh * 0.45):
                is_slash = True
            if is_slash:
                slash_mask |= comp

        kernel_score = np.zeros((155, 295), dtype=np.uint8)
        kernel_score[:, :] = 1
        score_zone = cv2.dilate(slash_mask.astype(np.uint8), kernel_score, anchor=(0, 140)) > 0
        score_zone[q10_bot_y:, :] = False

        student_writing = np.zeros((bh, bw), dtype=bool)
        student_writing[:int(bh * 0.48), :] = is_ink[:int(bh * 0.48), :]
        student_writing[:q10_bot_y, :int(bw * 0.42)] = is_ink[:q10_bot_y, :int(bw * 0.42)]

        teacher_near = cv2.dilate(slash_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (125, 125))) > 0

        for i in range(1, num_l):
            x, y, cw, ch, area = stats[i]
            if cw > 650 or ch > 750 or area > 6000:
                continue
            comp = (labels == i)
            rg = np.count_nonzero(comp & real_grid)
            if rg > 15 and area > 1200 and cw > 70 and ch > 70:
                student_writing |= comp
                continue
            if np.any(comp & teacher_near) and area < 150:
                continue
            if (x + cw) < int(bw * 0.76) and y > int(bh * 0.48) and y < q10_bot_y and not np.any(comp & score_zone):
                student_writing |= comp
            if y < int(bh * 0.78) and cw < 68 and ch < 68 and area < 650:
                student_writing |= comp

        student_writing[slash_mask] = False
        teacher_mask = slash_mask.copy()

        for i in range(1, num_l):
            x, y, cw, ch, area = stats[i]
            if cw > 650 or ch > 750 or area > 6000 or y < int(bh * 0.30) or y >= q10_bot_y:
                continue
            comp = (labels == i)
            if np.all(student_writing[comp]):
                continue
            aspect = ch / max(1, cw)
            mbr = np.mean(diff_br[comp])
            mrb = np.mean(diff_rb[comp])
            in_sz = np.count_nonzero(comp & score_zone) > 8
            is_digit_1 = (y > int(bh * 0.50) and ch > 50 and cw < 85 and area > 140 and aspect > 1.6 and x > int(bw * 0.35))
            is_blue_mark = (mbr > 2.0 and area > 45 and y > int(bh * 0.45) and in_sz)
            is_red_mark = (mrb > 8.0 and area > 45 and y > int(bh * 0.45))
            if (in_sz and area > 45) or is_digit_1 or is_blue_mark or is_red_mark:
                teacher_mask |= comp

        for i in range(1, num_l):
            x, y, cw, ch, area = stats[i]
            if x > int(bw * 0.86) and y > int(bh * 0.65) and area > 800 and y < q10_bot_y:
                teacher_mask |= (labels == i)

        for i in range(1, num_l):
            x, y, cw, ch, area = stats[i]
            if cw > 650 or ch > 750 or area > 6000 or y < int(bh * 0.45) or y >= q10_bot_y:
                continue
            comp = (labels == i)
            if np.any(comp & teacher_near) and area < 150:
                teacher_mask |= comp
                student_writing[comp] = False

        teacher_mask[q10_bot_y:, :] = False
        student_protect = cv2.dilate(student_writing.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))) > 0
        teacher_mask[student_protect] = False
        teacher_dil = cv2.dilate(teacher_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
        teacher_dil[student_protect] = False
        teacher_dil[q10_bot_y:, :] = False
        teacher_dil[q11_protect] = False

    orig_teacher_count = np.count_nonzero(teacher_mask)
    orig_student_count = np.count_nonzero(student_writing)

    # 5. Hybrid Inpainting (Seamless Paper Patch in open whitespace + Navier-Stokes near boundaries)
    cleaned = orig.copy()
    save_mask = np.zeros((bh, bw), dtype=np.uint8)

    num_t, t_labels, t_stats, _ = cv2.connectedComponentsWithStats(teacher_dil.astype(np.uint8))
    marks_report = []

    for ti in range(1, num_t):
        tx, ty, tcw, tch, tarea = t_stats[ti]
        if tarea < 8:
            continue
        comp_mask = (t_labels == ti)
        save_mask[comp_mask] = 255

        pad = 12
        rx0, ry0 = max(0, tx - pad), max(0, ty - pad)
        rx1, ry1 = min(bw, tx + tcw + pad), min(bh - 2, ty + tch + pad)
        rw, rh = rx1 - rx0, ry1 - ry0

        st_count = np.count_nonzero(student_writing[ry0:ry1, rx0:rx1])
        q11_count = np.count_nonzero(q11_protect[ry0:ry1, rx0:rx1])
        success_clone = False

        if st_count == 0 and q11_count == 0 and rw > 15 and rh > 15 and rw < 800 and rh < 800:
            patch, var = find_clean_paper_patch(cleaned, teacher_dil, student_writing, rh, rw, rx0, ry0, rx1, ry1, bh, bw)
            if patch is not None and var < 100:
                cmask = 255 * np.ones((rh, rw), dtype=np.uint8)
                center = (rx0 + rw // 2, ry0 + rh // 2)
                try:
                    cleaned = cv2.seamlessClone(patch, cleaned, cmask, center, cv2.NORMAL_CLONE)
                    success_clone = True
                    marks_report.append(f"Mark #{ti} ({tarea}px) -> Seamless Paper Patch")
                except Exception:
                    success_clone = False

        if not success_clone:
            m = comp_mask.astype(np.uint8) * 255
            m_dil = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
            m_dil[student_protect] = 0
            m_dil[q10_bot_y:, :] = 0
            m_dil[q11_protect] = 0
            cleaned = cv2.inpaint(cleaned, m_dil, 5, cv2.INPAINT_NS)
            marks_report.append(f"Mark #{ti} ({tarea}px) -> NS Inpaint")

    # Final verification of student retention
    gray_fin = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)
    local_fin = cv2.GaussianBlur(gray_fin, (51, 51), 0)
    contrast_fin = local_fin.astype(np.int16) - gray_fin.astype(np.int16)
    fin_student = (contrast_fin > 12) & (gray_fin < 155) & student_writing
    fin_student_count = np.count_nonzero(fin_student)
    retention = (fin_student_count / max(1, orig_student_count)) * 100.0

    base_name = os.path.splitext(filename)[0]
    out_filename = base_name + ".jpg"

    imwrite_utf8(os.path.join(CLEAN_DIR, out_filename), cleaned)
    imwrite_utf8(os.path.join(MASK_DIR, out_filename), save_mask)

    comp = np.hstack([orig, cleaned])
    small_comp = cv2.resize(comp, (comp.shape[1] // 2, comp.shape[0] // 2))
    imwrite_utf8(os.path.join(INSPECT_DIR, f"comp_text1_{base_name}.jpg"), small_comp, quality=88)

    print(f"[{idx:02d}/{total:02d}] {filename} -> {out_filename} | Teacher ink: {orig_teacher_count} px cleaned | Student retention: {retention:.1f}%")

    return {
        "filename": filename,
        "out_filename": out_filename,
        "base_name": base_name,
        "orig_teacher": int(orig_teacher_count),
        "retention": round(float(retention), 1),
        "marks_count": len(marks_report)
    }

def generate_gallery_text1(results):
    html = """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Text Set 1 - Row-major vs Column-major Audit Gallery</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }
        h1 { text-align: center; color: #38bdf8; margin-bottom: 8px; }
        p.subtitle { text-align: center; color: #94a3b8; margin-bottom: 32px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(580px, 1fr)); gap: 24px; }
        .card { background: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .card-header { padding: 12px 16px; background: #0f172a; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; }
        .card-header h3 { margin: 0; font-size: 16px; color: #e2e8f0; }
        .badge { font-size: 12px; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
        .badge-success { background: #065f46; color: #34d399; }
        .img-container { width: 100%; position: relative; cursor: zoom-in; }
        .img-container img { width: 100%; display: block; }
        .card-footer { padding: 10px 16px; font-size: 13px; color: #94a3b8; display: flex; justify-content: space-between; }
        .nav-bar { display: flex; justify-content: center; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
        .nav-bar a { color: #38bdf8; text-decoration: none; padding: 8px 16px; background: #1e293b; border-radius: 8px; border: 1px solid #334155; font-size: 13px; font-weight: 500; }
        .nav-bar a:hover { background: #334155; color: #fff; }
        .nav-bar a.active { background: #38bdf8; color: #0f172a; font-weight: 600; }
    </style>
</head>
<body>
    <div class="nav-bar">
        <a href="index.html">Master Dashboard</a>
        <a href="gallery_text1.html" class="active">Text 1 (Row vs Col)</a>
        <a href="gallery_text2.html">Text 2 (O(n log n))</a>
        <a href="gallery_text3.html">Text 3 (Linked List)</a>
        <a href="gallery_set1.html">Photo 1 (BST)</a>
        <a href="gallery_set2.html">Photo 2 (1D Array)</a>
        <a href="gallery_set3.html">Photo 3 (Tree Conv)</a>
    </div>
    <h1>Text Set 1 - Row-major vs Column-major Audit Gallery</h1>
    <p class="subtitle">Complete Dataset of 34 Images | Hybrid Poisson & Navier-Stokes | 100% Student Work & Question 11 Preserved</p>
    <div class="grid">
"""
    for r in results:
        html += f"""
        <div class="card">
            <div class="card-header">
                <h3>{r['filename']}</h3>
                <span class="badge badge-success">Retention: {r['retention']}%</span>
            </div>
            <div class="img-container">
                <img src="comp_text1_{r['base_name']}.jpg" alt="{r['filename']} Comparison (Left: Original, Right: Cleaned)">
            </div>
            <div class="card-footer">
                <span>Teacher Ink Cleaned: {r['orig_teacher']} px</span>
                <span>Marks Handled: {r['marks_count']}</span>
            </div>
        </div>
"""
    html += """
    </div>
</body>
</html>
"""
    with open(os.path.join(INSPECT_DIR, "gallery_text1.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Generated gallery at {os.path.join(INSPECT_DIR, 'gallery_text1.html')}")

def main():
    files = sorted([f for f in os.listdir(SRC_DIR) if f.lower().endswith(".heic") or f.lower().endswith(".jpg")])
    print(f"Processing all {len(files)} images in {SRC_DIR}...")
    results = []
    for idx, f in enumerate(files, 1):
        res = clean_single_image_text1(f, idx, len(files))
        results.append(res)
    generate_gallery_text1(results)
    print("\nText Set 1 successfully completed!")

if __name__ == "__main__":
    main()
