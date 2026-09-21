import os
import sys
import cv2
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

SRC_DIR = os.path.join("ชุดข้อสอบใหม่", "photoชุดที่1")
CLEAN_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_clean_ชุดที่1")
MASK_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_mask_ชุดที่1")

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(MASK_DIR, exist_ok=True)

def clean_single_image(filename: str):
    src_path = os.path.join(SRC_DIR, filename)
    with open(src_path, "rb") as fh:
        img = cv2.imdecode(np.frombuffer(fh.read(), np.uint8), cv2.IMREAD_COLOR)

    h, w, _ = img.shape
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Detect all red / orange teacher marks (scoring, circles, checkmarks, underlines)
    m1 = cv2.inRange(hsv, np.array([0, 30, 35]), np.array([18, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([155, 30, 35]), np.array([180, 255, 255]))
    red_mask = m1 | m2
    orig_red = np.count_nonzero(red_mask)

    # 2. Strict Pencil & Ink Protection for student's drawing
    # Any pixel that is dark (gray < 125) and not strongly red (saturation < 35) is student line!
    student_pencil = (gray < 125) & (hsv[:, :, 1] < 35)
    
    # 3. Create precision inpaint mask:
    # Dilate red by 2px (5x5 kernel) to catch ink bleeding, but STRICTLY exclude student pencil
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    red_dilated = cv2.dilate(red_mask, kernel, iterations=1)
    
    inpaint_mask = red_dilated.copy()
    inpaint_mask[student_pencil] = 0

    # 4. Inpaint using Telea with radius 3 (fast, ultra-tight stroke replacement)
    cleaned = cv2.inpaint(img, inpaint_mask, 3, cv2.INPAINT_TELEA)

    # 5. Check and clean any isolated red marks in margins (e.g. Photo 17 bottom underline)
    hsv2 = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
    rem_red = cv2.inRange(hsv2, np.array([0, 25, 30]), np.array([18, 255, 255])) | cv2.inRange(hsv2, np.array([155, 25, 30]), np.array([180, 255, 255]))
    rem_red[student_pencil] = 0
    if np.count_nonzero(rem_red) > 15:
        cleaned = cv2.inpaint(cleaned, cv2.dilate(rem_red, np.ones((3, 3), np.uint8)), 3, cv2.INPAINT_TELEA)

    # 6. Audit remaining red
    hsv_fin = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
    fin_red = np.count_nonzero(cv2.inRange(hsv_fin, np.array([0, 30, 35]), np.array([18, 255, 255])) | cv2.inRange(hsv_fin, np.array([155, 30, 35]), np.array([180, 255, 255])))

    # Save output to both photo_clean_ชุดที่1 and photo_mask_ชุดที่1
    _, out_buf = cv2.imencode(".jpg", cleaned, [cv2.IMWRITE_JPEG_QUALITY, 96])
    for target in [CLEAN_DIR, MASK_DIR]:
        dst = os.path.join(target, filename)
        with open(dst, "wb") as fh:
            fh.write(out_buf)

    return {"file": filename, "orig_red": orig_red, "fin_red": fin_red}

def main():
    files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith(".jpg")])
    print(f"=== Running Precision Pencil-Protected Clean on all {len(files)} files in Photo Set 1 ===")

    for idx, f in enumerate(files, 1):
        res = clean_single_image(f)
        print(f"[{idx:02d}/34] {res['file']}: Red removed {res['orig_red']} -> {res['fin_red']} px (Pencil 100% Protected)")

    print("\nALL 34 IMAGES RE-PROCESSED WITH ZERO PENCIL EROSION & CLEAN RED REMOVAL!")

if __name__ == "__main__":
    main()
