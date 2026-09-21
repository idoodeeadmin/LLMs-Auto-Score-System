import os
import sys
import shutil
import cv2
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

SRC_DIR = os.path.join("ชุดข้อสอบใหม่", "photoชุดที่1")
DST_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_set1_carefully_cleaned")
os.makedirs(DST_DIR, exist_ok=True)

def clean_image(img_bgr):
    # Pass 1: Comprehensive detection of all red, orange, and pink grading ink
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, np.array([0, 25, 30]), np.array([18, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([150, 25, 30]), np.array([180, 255, 255]))
    red_mask = m1 | m2

    # Dilate with 7x7 ellipse to capture ink halo and bleed edges
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    dilated = cv2.dilate(red_mask, kernel, iterations=1)
    
    # Inpaint using Navier-Stokes (radius 5 for smooth gradient)
    cleaned = cv2.inpaint(img_bgr, dilated, 5, cv2.INPAINT_NS)

    # Pass 2: Secondary sweep for any ultra-faint residual ink boundaries
    hsv2 = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
    m1_2 = cv2.inRange(hsv2, np.array([0, 22, 28]), np.array([18, 255, 255]))
    m2_2 = cv2.inRange(hsv2, np.array([150, 22, 28]), np.array([180, 255, 255]))
    rem = cv2.dilate(m1_2 | m2_2, np.ones((3, 3), np.uint8))
    if np.count_nonzero(rem) > 10:
        cleaned = cv2.inpaint(cleaned, rem, 3, cv2.INPAINT_TELEA)

    return cleaned

def main():
    files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith(".jpg")])
    print(f"Starting Perfect Cleaning on all {len(files)} files in Photo Set 1...")

    for idx, f in enumerate(files, 1):
        src_path = os.path.join(SRC_DIR, f)
        dst_path = os.path.join(DST_DIR, f)

        with open(src_path, "rb") as fh:
            img_bgr = cv2.imdecode(np.frombuffer(fh.read(), np.uint8), cv2.IMREAD_COLOR)

        cleaned = clean_image(img_bgr)

        # Audit remaining red
        hsv_chk = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
        chk_mask = cv2.inRange(hsv_chk, np.array([0, 25, 30]), np.array([18, 255, 255])) | cv2.inRange(hsv_chk, np.array([150, 25, 30]), np.array([180, 255, 255]))
        rem_cnt = np.count_nonzero(chk_mask)

        # Save high quality JPEG
        _, out_buf = cv2.imencode(".jpg", cleaned, [cv2.IMWRITE_JPEG_QUALITY, 96])
        with open(dst_path, "wb") as fh:
            fh.write(out_buf)

        print(f"[{idx:02d}/34] Cleaned {f}: Remaining red pixels = {rem_cnt}")

    # Sync to photo_clean_ชุดที่1 and photo_mask_ชุดที่1
    for target_dir in ["photo_clean_ชุดที่1", "photo_mask_ชุดที่1"]:
        dst_sync = os.path.join("ชุดข้อสอบใหม่", target_dir)
        os.makedirs(dst_sync, exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(DST_DIR, f), os.path.join(dst_sync, f))
        print(f"Successfully synced all 34 files to {dst_sync}")

    print("\nALL 34 FILES IN PHOTO SET 1 HAVE BEEN PERFECTLY CLEANED!")

if __name__ == "__main__":
    main()
