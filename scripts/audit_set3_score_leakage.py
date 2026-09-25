import cv2
import numpy as np
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]

src_dir = ROOT / 'ชุดข้อสอบใหม่' / 'photoชุดที่3'
clean_dir = ROOT / 'ชุดข้อสอบใหม่' / 'photo_clean_ชุดที่3'
out_dir = ROOT / 'public' / 'audit_diffs_set3'
out_dir.mkdir(parents=True, exist_ok=True)

print("=== AUDITING ORIGINAL VS CLEANED IMAGES FOR SET 3 (Q6) ===")
def imread_utf8(path):
    with open(path, "rb") as fh:
        return cv2.imdecode(np.frombuffer(fh.read(), np.uint8), cv2.IMREAD_COLOR)

def imwrite_utf8(path, img):
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    with open(path, "wb") as fh:
        fh.write(buf)

for i in range(1, 11):
    fname = f"LINE_ALBUM_Photo2.2_260918_{i}.jpg"
    orig_p = src_dir / fname
    clean_p = clean_dir / fname
    
    orig = imread_utf8(orig_p)
    clean = imread_utf8(clean_p)
    
    if orig is None or clean is None:
        print(f"Student {i}: Error reading images")
        continue
        
    # Check if dimensions match
    if orig.shape != clean.shape:
        print(f"Student {i}: Shapes differ! Orig={orig.shape}, Clean={clean.shape}")
        # Resize clean to orig if needed or vice versa
        clean = cv2.resize(clean, (orig.shape[1], orig.shape[0]))
        
    diff = cv2.absdiff(orig, clean)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(diff_gray, 20, 255, cv2.THRESH_BINARY)
    num_diff_pixels = np.count_nonzero(thresh)
    
    # Save diff visualization
    diff_vis = orig.copy()
    diff_vis[thresh > 0] = [0, 0, 255] # Red highlight where modified
    
    # Combine side by side: Orig | Clean | Highlighted
    h, w, _ = orig.shape
    scale = 0.5
    small_orig = cv2.resize(orig, (int(w*scale), int(h*scale)))
    small_clean = cv2.resize(clean, (int(w*scale), int(h*scale)))
    small_vis = cv2.resize(diff_vis, (int(w*scale), int(h*scale)))
    
    comb = np.hstack([small_orig, small_clean, small_vis])
    imwrite_utf8(out_dir / f"audit_std_{i}.jpg", comb)
    print(f"Student {i:2d}: Modified pixels = {num_diff_pixels:6d} | Saved audit image to public/audit_diffs_set3/audit_std_{i}.jpg")
