import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1] / 'ชุดข้อสอบใหม่'

folders = ['photoชุดที่3', 'photo_clean_ชุดที่3', 'photo_crop_ชุดที่3', 'photo_mask_ชุดที่3']
for f in folders:
    p = ROOT / f
    count = len(list(p.glob('*.*'))) if p.exists() else 0
    print(f"{f}: exists={p.exists()}, count={count}")

# Check files in photoชุดที่3 vs photo_clean_ชุดที่3
orig_dir = ROOT / 'photoชุดที่3'
clean_dir = ROOT / 'photo_clean_ชุดที่3'

print("\n--- Inspecting first 10 images ---")
for i in range(1, 11):
    orig_f = orig_dir / f"LINE_ALBUM_Photo2.2_260918_{i}.jpg"
    clean_f = clean_dir / f"LINE_ALBUM_Photo2.2_260918_{i}.jpg"
    orig_sz = orig_f.stat().st_size if orig_f.exists() else 0
    clean_sz = clean_f.stat().st_size if clean_f.exists() else 0
    print(f"Student {i:2d}: Orig size={orig_sz:6d} bytes | Clean size={clean_sz:6d} bytes")
