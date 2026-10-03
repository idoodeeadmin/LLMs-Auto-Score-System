import shutil
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
src_dir = ROOT / "ชุดข้อสอบใหม่/photo_clean_ชุดที่1"
bak_dir = ROOT / "ชุดข้อสอบใหม่/photo_clean_ชุดที่1_backup_portrait"
bak_dir.mkdir(parents=True, exist_ok=True)

# 1. Backup all 34 files
for i in range(1, 35):
    fn = f"LINE_ALBUM_Photo1_260917_{i}.jpg"
    src = src_dir / fn
    bak = bak_dir / fn
    if not bak.exists():
        shutil.copy2(src, bak)

print(f"Backup completed for 34 images into: {bak_dir}")

# 2. Rotate all 34 files to upright landscape
rotated_count = 0
for i in range(1, 35):
    fn = f"LINE_ALBUM_Photo1_260917_{i}.jpg"
    src = src_dir / fn
    im = Image.open(src)
    if im.width < im.height:
        rot = im.transpose(Image.Transpose.ROTATE_90)
        rot.save(src, quality=95)
        print(f"Photo {i:2d}: rotated from {im.size} to {rot.size}")
        rotated_count += 1
    else:
        print(f"Photo {i:2d}: already landscape {im.size}")

print(f"\nFinished: {rotated_count} images rotated upright and saved back into {src_dir}!")
