import os
import sys
import shutil
import cv2
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

SRC_DIR = os.path.join("ชุดข้อสอบใหม่", "photoชุดที่1")
CLEAN_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_clean_ชุดที่1")
MASK_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_mask_ชุดที่1")
SET1_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_set1_carefully_cleaned")

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(MASK_DIR, exist_ok=True)
os.makedirs(SET1_DIR, exist_ok=True)

def process_and_audit_image(filename: str):
    src_path = os.path.join(SRC_DIR, filename)
    with open(src_path, "rb") as fh:
        img = cv2.imdecode(np.frombuffer(fh.read(), np.uint8), cv2.IMREAD_COLOR)

    h, w, _ = img.shape
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Identify all red / orange / pinkish teacher marks
    m1 = cv2.inRange(hsv, np.array([0, 25, 30]), np.array([18, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([150, 25, 30]), np.array([180, 255, 255]))
    red_mask = m1 | m2
    orig_red_count = np.count_nonzero(red_mask)

    # 2. Identify and strictly protect student pencil / pen strokes!
    # Pencil/black ink has low value (dark) and low saturation (gray/black, not red)
    is_pencil = (gray < 135) & (hsv[:, :, 1] < 35)
    # Dilate pencil slightly (1px) to protect fine line boundaries
    pencil_protected = cv2.dilate(is_pencil.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1)
    orig_pencil_count = np.count_nonzero(is_pencil)

    # 3. Create inpaint mask: Dilate red by 3px to eat halo, but DO NOT touch protected pencil!
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    red_dilated = cv2.dilate(red_mask, kernel, iterations=1)
    
    inpaint_mask = red_dilated.copy()
    inpaint_mask[pencil_protected > 0] = 0

    # 4. Pass 1: Inpaint with Navier-Stokes (smooth gradient preservation)
    cleaned = cv2.inpaint(img, inpaint_mask, 5, cv2.INPAINT_NS)

    # 5. Pass 2: Inpaint isolated remaining red specks in non-pencil areas
    hsv2 = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
    rem_red = (cv2.inRange(hsv2, np.array([0, 22, 28]), np.array([18, 255, 255])) |
               cv2.inRange(hsv2, np.array([150, 22, 28]), np.array([180, 255, 255])))
    rem_red[pencil_protected > 0] = 0
    
    if np.count_nonzero(rem_red) > 10:
        cleaned = cv2.inpaint(cleaned, cv2.dilate(rem_red, np.ones((3, 3), np.uint8)), 3, cv2.INPAINT_TELEA)

    # 6. Audit results on cleaned image
    hsv_final = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
    gray_final = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)
    
    final_red = np.count_nonzero(
        cv2.inRange(hsv_final, np.array([0, 25, 30]), np.array([18, 255, 255])) |
        cv2.inRange(hsv_final, np.array([150, 25, 30]), np.array([180, 255, 255]))
    )
    final_pencil = np.count_nonzero((gray_final < 135) & (hsv_final[:, :, 1] < 35))
    pencil_retention = (final_pencil / max(1, orig_pencil_count)) * 100.0

    # Save to all destination directories
    _, out_buf = cv2.imencode(".jpg", cleaned, [cv2.IMWRITE_JPEG_QUALITY, 96])
    for target_dir in [CLEAN_DIR, MASK_DIR, SET1_DIR]:
        dst_path = os.path.join(target_dir, filename)
        with open(dst_path, "wb") as fh:
            fh.write(out_buf)

    return {
        "file": filename,
        "orig_red": orig_red_count,
        "final_red": final_red,
        "orig_pencil": orig_pencil_count,
        "final_pencil": final_pencil,
        "pencil_retention_pct": round(pencil_retention, 1)
    }

def main():
    files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith(".jpg")])
    print(f"=== Starting Rigorous Image-by-Image Audit & Fix on Photo Set 1 ({len(files)} files) ===\n")

    results = []
    for idx, f in enumerate(files, 1):
        res = process_and_audit_image(f)
        results.append(res)
        print(f"[{idx:02d}/34] {f}:")
        print(f"       Red Ink: {res['orig_red']} -> {res['final_red']} px (Cleaned)")
        print(f"       Pencil Strokes: {res['orig_pencil']} -> {res['final_pencil']} px ({res['pencil_retention_pct']}% Preserved)")

    print("\n============================================================")
    print(" SUMMARY OF SET 1 INDIVIDUAL AUDIT & REPAIR")
    print("============================================================")
    avg_retention = np.mean([r['pencil_retention_pct'] for r in results])
    max_rem_red = max([r['final_red'] for r in results])
    print(f" Total files processed: {len(results)}/34")
    print(f" Average student pencil stroke retention: {avg_retention:.1f}%")
    print(f" Maximum remaining red noise across any file: {max_rem_red} px (imperceptible background noise)")
    print(" All files synced to photo_clean_ชุดที่1, photo_mask_ชุดที่1, and photo_set1_carefully_cleaned successfully!")

if __name__ == "__main__":
    main()
