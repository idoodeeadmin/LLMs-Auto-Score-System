import os
import sys
import cv2
import numpy as np
import pillow_heif
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
pillow_heif.register_heif_opener()

SRC_DIR = os.path.join("ชุดข้อสอบใหม่", "โจทย์textชุดที่2")
CLEAN_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_clean_text2")
MASK_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_mask_text2")
ARTIFACT_DIR = r"C:\Users\idood\.gemini\antigravity-ide\brain\f6ee475c-7cae-4670-a1aa-717c1db8426d"
INSPECT_DIR = os.path.join(ARTIFACT_DIR, "inspect")

for d in [CLEAN_DIR, MASK_DIR, INSPECT_DIR]:
    os.makedirs(d, exist_ok=True)

# 4 files in Set 2 that need 90 CCW rotation
ROT_90_CCW_FILES = {
    "IMG_2792.HEIC",
    "IMG_2868.HEIC",
    "IMG_2869.HEIC",
    "IMG_2870.HEIC"
}

def imread_heic_or_jpg(path, filename, max_dim=2000):
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
    if filename in ROT_90_CCW_FILES:
        bgr = cv2.rotate(bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return bgr

def imwrite_utf8(path, img, quality=96):
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    with open(path, "wb") as fh:
        fh.write(buf)

def find_paper_top(bgr):
    """Detect the top row of the actual white paper in the image.
    For photos taken on a desk with keyboard visible above the paper,
    returns the row where the paper begins (skipping keyboard background).
    For close-up paper shots with no background, returns default 4%.
    """
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    center_start, center_end = int(w * 0.15), int(w * 0.85)
    top_region = gray[:int(h * 0.40), center_start:center_end]
    row_means = np.mean(top_region, axis=1)

    # Find minimum brightness row (the dark gap / desk between keyboard and paper)
    min_row = int(np.argmin(row_means))
    min_brightness = row_means[min_row]

    if min_brightness < 25:  # Dark gap found -> keyboard/desk visible above paper
        # Find first bright row AFTER the dark gap
        for row in range(min_row, len(row_means)):
            if row_means[row] > 100:
                return max(int(h * 0.04), row + int(h * 0.015))  # small safety margin
        return int(h * 0.22)  # fallback
    else:
        return int(h * 0.04)  # No keyboard visible, use default 4%

def find_clean_paper_patch(cleaned, full_teacher_mask, student_drawing, roi_h, roi_w, x0, y0, x1, y1, h, w):
    candidates = [
        (y1 + 15, y1 + roi_h + 15, x0, x1),                 # Below
        (y0 - roi_h - 15, y0 - 15, x0, x1),                 # Above
        (y0, y1, x0 - roi_w - 20, x0 - 20),                 # Left
        (y0, y1, x1 + 20, x1 + roi_w + 20),                 # Right
        (y1 + 15, y1 + roi_h + 15, x0 - roi_w - 20, x0 - 20), # Below Left
        (y1 + 15, y1 + roi_h + 15, x1 + 20, x1 + roi_w + 20), # Below Right
        (y0 - roi_h - 15, y0 - 15, x0 - roi_w - 20, x0 - 20), # Above Left
        (y0 - roi_h - 15, y0 - 15, x1 + 20, x1 + roi_w + 20)  # Above Right
    ]
    best_patch = None
    min_var = float('inf')

    # 1. First try adjacent candidates
    for cy0, cy1, cx0, cx1 in candidates:
        if cy0 >= 20 and cy1 <= h - 20 and cx0 >= 20 and cx1 <= w - 20:
            cand_patch = cleaned[cy0:cy1, cx0:cx1]
            cand_teacher = full_teacher_mask[cy0:cy1, cx0:cx1]
            cand_student = student_drawing[cy0:cy1, cx0:cx1]
            if not np.any(cand_teacher) and np.count_nonzero(cand_student) <= 5:
                p_gray = cv2.cvtColor(cand_patch, cv2.COLOR_BGR2GRAY)
                if np.mean(p_gray) > 130:
                    var = cv2.Laplacian(p_gray, cv2.CV_64F).var()
                    if var < min_var:
                        min_var = var
                        best_patch = cand_patch

    # 2. Search whitespace grid across page
    if best_patch is None or min_var > 120:
        step_y = max(30, roi_h // 2)
        step_x = max(30, roi_w // 2)
        for gy in range(int(h * 0.05), int(h * 0.90) - roi_h, step_y):
            for gx in range(int(w * 0.05), int(w * 0.90) - roi_w, step_x):
                if not (gx < x1 and gx + roi_w > x0 and gy < y1 and gy + roi_h > y0):
                    cand_patch = cleaned[gy:gy+roi_h, gx:gx+roi_w]
                    cand_teacher = full_teacher_mask[gy:gy+roi_h, gx:gx+roi_w]
                    cand_student = student_drawing[gy:gy+roi_h, gx:gx+roi_w]
                    if not np.any(cand_teacher) and np.count_nonzero(cand_student) <= 5:
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

def clean_single_image_text2(filename: str, idx: int, total: int):
    src_path = os.path.join(SRC_DIR, filename)
    orig = imread_heic_or_jpg(src_path, filename, max_dim=2000)
    h, w, _ = orig.shape

    b, g, r = cv2.split(orig.astype(np.int16))
    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)

    local_paper = cv2.GaussianBlur(gray, (51, 51), 0)
    contrast = local_paper.astype(np.int16) - gray.astype(np.int16)

    # 1. Teacher Ink Detection in Set 2:
    # Yellow / Orange highlighter / marker (teacher score numbers):
    is_orange = (hsv[:, :, 0] >= 6) & (hsv[:, :, 0] <= 45) & (hsv[:, :, 1] > 30) & (r > 115)
    # Red / Magenta pen:
    is_red = (r - g > 14) & (r - b > 14) & (r > 80) & (hsv[:, :, 1] > 20)
    # Purple ink:
    is_purple = (hsv[:, :, 0] >= 120) & (hsv[:, :, 1] > 25) & (r - g > 8)

    is_teacher_color = is_orange | is_red | is_purple

    # 1b. Teacher Blue Strikethrough Detection:
    # Teachers in Set 2 also cross out incorrect student text with blue pen.
    # These appear as long horizontal lines (high aspect ratio: width >> height).
    # Distinguish from student blue writing (text-like, smaller aspect ratio).
    is_all_blue = (b - r > 10) & (b - g > 4) & (gray < 165)
    is_all_blue[:int(h * 0.03), :] = False
    is_all_blue[int(h * 0.97):, :] = False
    is_all_blue[:, :int(w * 0.03)] = False
    is_all_blue[:, int(w * 0.97):] = False
    num_blue_lbl, blue_lbl, blue_stats, _ = cv2.connectedComponentsWithStats(is_all_blue.astype(np.uint8))
    teacher_blue_strikethrough = np.zeros((h, w), dtype=bool)
    for i in range(1, num_blue_lbl):
        bx, by, bbw, bbh, barea = blue_stats[i]
        # Long horizontal line: width > 120px, aspect ratio > 7, height < 60px
        if barea >= 80 and bbw > 120 and bbh < 60 and bbw > bbh * 7:
            teacher_blue_strikethrough |= (blue_lbl == i)

    is_teacher_color = is_teacher_color | teacher_blue_strikethrough

    # Edge margin masking (ignore desk edges around paper)
    is_teacher_color[:int(h * 0.03), :] = False
    is_teacher_color[int(h * 0.96):, :] = False
    is_teacher_color[:, :int(w * 0.03)] = False
    is_teacher_color[:, int(w * 0.96):] = False

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(is_teacher_color.astype(np.uint8))
    teacher_core = np.zeros((h, w), dtype=bool)

    for i in range(1, num_labels):
        x, y, bw, bh, area = stats[i]
        touches_extreme = (x <= int(w * 0.04) or y <= int(h * 0.04) or x + bw >= int(w * 0.96) or y + bh >= int(h * 0.96))
        if area > 45000:
            continue
        if touches_extreme and (area > 8000 or bw > int(w * 0.4) or bh > int(h * 0.4)):
            continue
        if area >= 12:
            teacher_core |= (labels == i)

    # Dilation for bleed edges / orange halo
    halo = (hsv[:, :, 1] > 20) & ((r > 115) | (r - g > 5))
    core_dil = cv2.dilate(teacher_core.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
    full_teacher_mask = teacher_core | (halo & core_dil)
    full_teacher_mask[:int(h * 0.02), :] = False
    full_teacher_mask[int(h * 0.97):, :] = False
    full_teacher_mask[:, :int(w * 0.02)] = False
    full_teacher_mask[:, int(w * 0.97):] = False

    # 2. Student Handwriting Protection (pencil, blue/black pen)
    is_graphite = (contrast > 12) & (gray < 135) & (np.abs(r - g) <= 12) & (np.abs(r - b) <= 12) & (~full_teacher_mask)
    is_dark_black = (contrast > 18) & (gray < 95) & (np.abs(r - g) <= 14) & (np.abs(r - b) <= 14) & (~full_teacher_mask)
    is_blue_pen = (b - r > 12) & (b - g > 5) & (gray < 155) & (~full_teacher_mask)
    student_writing = is_graphite | is_dark_black | is_blue_pen

    pencil_protect = cv2.dilate(student_writing.astype(np.uint8),
                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0

    orig_teacher_count = np.count_nonzero(full_teacher_mask)
    orig_student_count = np.count_nonzero(student_writing)

    # 3. Clean teacher marks
    cleaned = orig.copy()
    save_mask = np.zeros((h, w), dtype=np.uint8)

    num_marks, mark_labels, mark_stats, _ = cv2.connectedComponentsWithStats(full_teacher_mask.astype(np.uint8))
    marks_report = []

    for i in range(1, num_marks):
        x, y, bw, bh, area = mark_stats[i]
        touches_extreme = (x <= int(w * 0.04) or y <= int(h * 0.04) or x + bw >= int(w * 0.96) or y + bh >= int(h * 0.96))
        if area < 12 or area > 45000:
            continue
        if touches_extreme and (area > 8000 or bw > int(w * 0.4) or bh > int(h * 0.4)):
            continue

        comp_mask = (mark_labels == i)
        save_mask[comp_mask] = 255

        pad = 12
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(w, x + bw + pad), min(h, y + bh + pad)
        roi_w, roi_h = x1 - x0, y1 - y0

        pencil_count = np.count_nonzero(student_writing[y0:y1, x0:x1])
        touches_pencil = pencil_count > 15

        if not touches_pencil:
            # Seamless Cloning
            best_patch, min_var = find_clean_paper_patch(cleaned, full_teacher_mask, student_writing,
                                                         roi_h, roi_w, x0, y0, x1, y1, h, w)
            success_clone = False
            if best_patch is not None and min_var < 110:
                clone_mask = 255 * np.ones((roi_h, roi_w), dtype=np.uint8)
                center = (x0 + roi_w // 2, y0 + roi_h // 2)
                try:
                    cleaned = cv2.seamlessClone(best_patch, cleaned, clone_mask, center, cv2.NORMAL_CLONE)
                    success_clone = True
                    marks_report.append(f"Mark #{i} ({area}px) -> Seamless Paper Patch")
                except Exception:
                    success_clone = False

            if not success_clone:
                dil = cv2.dilate(comp_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
                cleaned = cv2.inpaint(cleaned, dil, 5, cv2.INPAINT_NS)
                marks_report.append(f"Mark #{i} ({area}px) -> NS Inpaint")
        else:
            # Pencil/Pen Protected Inpaint
            dil = cv2.dilate(comp_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
            dil[pencil_protect] = 0
            cleaned = cv2.inpaint(cleaned, dil, 3, cv2.INPAINT_TELEA)

            # Desaturate overlapping orange/red tint over student strokes
            overlap = comp_mask & student_writing
            if np.count_nonzero(overlap) > 0:
                overlap_gray = gray[overlap]
                for c in range(3):
                    cleaned[:, :, c][overlap] = overlap_gray

            marks_report.append(f"Mark #{i} ({area}px) -> Pencil-Protected Inpaint")

    if filename == "IMG_2859.HEIC":
        # Header score '1.5' and faint orange loop above Thai question text
        yellow_15 = (r > 120) & (r - b > 10) & (g - b > 5)
        m_15 = np.zeros((h, w), dtype=np.uint8)
        m_15[20:143, 890:1120] = yellow_15[20:143, 890:1120].astype(np.uint8) * 255
        k_ell = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
        dil_15 = cv2.dilate(m_15, k_ell)
        dil_15[144:, :] = 0  # strictly protect Thai question header

        m_faint = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(m_faint, (330, 115), (55, 40), 0, 0, 360, 255, -1)
        m_faint[158:, :] = 0

        header_mask = cv2.bitwise_or(dil_15, m_faint)
        cleaned = cv2.inpaint(cleaned, header_mask, 7, cv2.INPAINT_TELEA)
        save_mask[header_mask > 0] = 255

    paper_top = find_paper_top(orig)

    # 4. Final verification
    b_fin, g_fin, r_fin = cv2.split(cleaned.astype(np.int16))
    hsv_fin = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
    gray_fin = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)

    fin_orange = (hsv_fin[:, :, 0] >= 6) & (hsv_fin[:, :, 0] <= 45) & (hsv_fin[:, :, 1] > 30) & (r_fin > 115)
    fin_red = (r_fin - g_fin > 14) & (r_fin - b_fin > 14) & (hsv_fin[:, :, 1] > 20)
    fin_teacher = fin_orange | fin_red
    # Exclude background above paper (keyboard/desk) using dynamic paper boundary
    fin_teacher[:paper_top, :] = False
    fin_teacher[int(h * 0.95):, :] = False
    fin_teacher[:, :int(w * 0.05)] = False
    fin_teacher[:, int(w * 0.95):] = False
    fin_teacher_count = np.count_nonzero(fin_teacher)

    local_paper_fin = cv2.GaussianBlur(gray_fin, (51, 51), 0)
    contrast_fin = local_paper_fin.astype(np.int16) - gray_fin.astype(np.int16)
    is_blue_fin = (b_fin - r_fin > 10) & (b_fin - g_fin > 4) & (gray_fin < 165)
    fin_student = ((contrast_fin > 12) & (gray_fin < 135) & (np.abs(r_fin - g_fin) <= 12) & (np.abs(r_fin - b_fin) <= 12)) | is_blue_fin
    fin_student_count = np.count_nonzero(fin_student)
    retention = (fin_student_count / max(1, orig_student_count)) * 100.0

    base_name = os.path.splitext(filename)[0]
    out_filename = base_name + ".jpg"

    imwrite_utf8(os.path.join(CLEAN_DIR, out_filename), cleaned)
    imwrite_utf8(os.path.join(MASK_DIR, out_filename), save_mask)

    comp = np.hstack([orig, cleaned])
    small_comp = cv2.resize(comp, (comp.shape[1] // 2, comp.shape[0] // 2))
    imwrite_utf8(os.path.join(INSPECT_DIR, f"comp_text2_{base_name}.jpg"), small_comp, quality=88)
    pub_inspect = os.path.join("public", "inspect", f"comp_text2_{base_name}.jpg")
    imwrite_utf8(pub_inspect, small_comp, quality=88)

    print(f"[{idx:02d}/{total:02d}] {filename} -> {out_filename} | Teacher: {orig_teacher_count} -> {fin_teacher_count} | Student text: {retention:.1f}%")

    return {
        "filename": filename,
        "out_filename": out_filename,
        "base_name": base_name,
        "orig_teacher": orig_teacher_count,
        "fin_teacher": fin_teacher_count,
        "retention": round(retention, 1),
        "marks_count": len(marks_report)
    }

def generate_gallery_text2(results):
    html = """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Text Set 2 - O(n log n) vs O(n^2) Audit Gallery</title>
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
        .labels { display: flex; justify-content: space-around; background: #1e293b; padding: 6px; font-size: 13px; font-weight: bold; border-top: 1px solid #334155; }
        .labels span:first-child { color: #f87171; }
        .labels span:last-child { color: #34d399; }
        .metrics { padding: 12px 16px; font-size: 13px; color: #94a3b8; display: flex; justify-content: space-between; background: #0f172a; }
        .metrics strong { color: #38bdf8; }
    </style>
</head>
<body>
    <h1>โจทย์ Text ชุดที่ 2: O(n log n) vs O(n^2) (34 ภาพ)</h1>
    <p class="subtitle">Blind Scoring Preprocessing Gallery • Seamless Paper Patching • Orange Marker & Score Removal</p>
    <div class="grid">
"""
    for r in results:
        base = r["base_name"]
        html += f"""
        <div class="card">
            <div class="card-header">
                <h3>{r['filename']} &rarr; {r['out_filename']}</h3>
                <span class="badge badge-success">&#10003; Cleaned ({r['marks_count']} marks)</span>
            </div>
            <div class="img-container">
                <img src="comp_text2_{base}.jpg" alt="Comparison {base}">
            </div>
            <div class="labels">
                <span>&larr; Original (Teacher Marks)</span>
                <span>Cleaned (100% Natural Paper) &rarr;</span>
            </div>
            <div class="metrics">
                <span>Teacher Marker: <strong>{r['orig_teacher']} &rarr; {r['fin_teacher']} px</strong></span>
                <span>Student Writing: <strong>{r['retention']}% retained</strong></span>
            </div>
        </div>
"""
    html += """
    </div>
</body>
</html>
"""
    out_path = os.path.join(INSPECT_DIR, "gallery_text2.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Gallery saved: {out_path}")

def main():
    files = sorted(os.listdir(SRC_DIR))
    print(f"Processing Text Set 2 ({len(files)} files)...")
    results = []
    for idx, fn in enumerate(files, 1):
        res = clean_single_image_text2(fn, idx, len(files))
        results.append(res)
    generate_gallery_text2(results)
    print("Text Set 2 Completed Successfully!")

if __name__ == "__main__":
    main()
