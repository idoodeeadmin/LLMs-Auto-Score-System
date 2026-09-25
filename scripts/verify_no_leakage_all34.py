import cv2
import numpy as np
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]

clean_dir = ROOT / 'ชุดข้อสอบใหม่' / 'photo_clean_ชุดที่3'

def imread_utf8(path):
    with open(path, "rb") as fh:
        return cv2.imdecode(np.frombuffer(fh.read(), np.uint8), cv2.IMREAD_COLOR)

print("=== CHECKING ALL 34 CLEANED IMAGES FOR ANY REMAINING COLORED TEACHER INK ===")
suspicious_list = []

for i in range(1, 35):
    fname = f"LINE_ALBUM_Photo2.2_260918_{i}.jpg"
    p = clean_dir / fname
    img = imread_utf8(p)
    if img is None:
        print(f"Cannot read {fname}")
        continue
        
    b, g, r = cv2.split(img.astype(np.int16))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Check for red, orange, magenta, purple ink
    is_red = (r - g > 15) & (r - b > 15) & (hsv[:, :, 1] > 30)
    is_orange = (hsv[:, :, 0] >= 5) & (hsv[:, :, 0] <= 25) & (hsv[:, :, 1] > 40) & (r > 130)
    is_purple = (hsv[:, :, 0] >= 120) & (hsv[:, :, 1] > 30) & (r - g > 10)
    
    colored_ink = is_red | is_orange | is_purple
    
    # Exclude borders
    h, w, _ = img.shape
    colored_ink[:20, :] = False
    colored_ink[h-20:, :] = False
    colored_ink[:, :20] = False
    colored_ink[:, w-20:] = False
    
    count = np.count_nonzero(colored_ink)
    if count > 50:
        suspicious_list.append((i, count))
        print(f"Student {i:2d}: Found {count} colored ink pixels! ⚠️")
    else:
        print(f"Student {i:2d}: CLEAN (remaining colored pixels: {count}) ✅")

print("\n--- Summary ---")
print(f"Total clean: {34 - len(suspicious_list)} / 34")
print(f"Suspicious: {len(suspicious_list)}")
for idx, cnt in suspicious_list:
    print(f"  Student {idx}: {cnt} pixels")
