# -*- coding: utf-8 -*-
"""
Script to prepare 100% clean, symmetrical images for Chapter 4 thesis report.
All images (Text AND Image) are taken from the clean preprocessed folders
with NO teacher pen scores visible, strictly aligned with Section 4.1.2 pipeline.
"""

import os
import sys
import shutil
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

# Source clean images for 4.1.5 (Cases 1-6)
cases_clean = {
    'case1_ds001.jpg': 'ชุดข้อสอบใหม่/photo_clean_text1/IMG_2791.jpg',
    'case2_ds047.jpg': 'ชุดข้อสอบใหม่/photo_clean_text2/IMG_2853.jpg',
    'case3_ds072.jpg': 'ชุดข้อสอบใหม่/photo_clean_text3/IMG_2895.jpg',
    'case4_ds104.jpg': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่1/LINE_ALBUM_Photo1_260917_2.jpg',
    'case5_ds154.jpg': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่2/LINE_ALBUM_Photo2.1_260918_18.jpg',
    'case6_ds171.jpg': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่3/LINE_ALBUM_Photo2.2_260918_1.jpg',
    
    # 4.1.6 Discrepancy cases (clean photos)
    'anom_ds007.jpg': 'ชุดข้อสอบใหม่/photo_clean_text1/IMG_2799.jpg',
    'anom_ds040.jpg': 'ชุดข้อสอบใหม่/photo_clean_text2/IMG_2847.jpg',
    'anom_ds111.jpg': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่1/LINE_ALBUM_Photo1_260917_17.jpg'
}

dst_dirs = [
    'public/screenshots/case_studies',
    'docs_and_tests/screenshots/case_studies',
    'docs_and_tests/images/case_studies'
]

for d in dst_dirs:
    os.makedirs(d, exist_ok=True)

for fname, src in cases_clean.items():
    if not os.path.exists(src):
        print(f"Error: {src} not found!")
        continue
    im = Image.open(src)
    w, h = im.size
    max_dim = 1200
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        im_resized = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    else:
        im_resized = im.copy()
        
    for d in dst_dirs:
        out_p = os.path.join(d, fname)
        im_resized.save(out_p, quality=92, optimize=True)
        print(f"Saved clean {out_p} ({im_resized.size})")

# Recreate dataset_samples_image.png using CLEAN images
print("\nRecreating dataset_samples_image.png with CLEAN images (no teacher scores)...")
from PIL import ImageDraw, ImageFont

q4_clean = Image.open('ชุดข้อสอบใหม่/photo_clean_ชุดที่1/LINE_ALBUM_Photo1_260917_2.jpg')
q5_clean = Image.open('ชุดข้อสอบใหม่/photo_clean_ชุดที่2/LINE_ALBUM_Photo2.1_260918_18.jpg')
q6_clean = Image.open('ชุดข้อสอบใหม่/photo_clean_ชุดที่3/LINE_ALBUM_Photo2.2_260918_1.jpg')

target_w, target_h = 380, 260

def resize_thumb(im, tw, th):
    w, h = im.size
    scale = max(tw / float(w), th / float(h))
    nw, nh = int(w * scale), int(h * scale)
    im_r = im.resize((nw, nh), Image.Resampling.LANCZOS)
    # Center crop
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im_r.crop((left, top, left + tw, top + th))

t4 = resize_thumb(q4_clean, target_w, target_h)
t5 = resize_thumb(q5_clean, target_w, target_h)
t6 = resize_thumb(q6_clean, target_w, target_h)

banner_h = 28
panel_w = target_w
total_w = panel_w * 3 + 40 # 20px gaps
total_h = target_h + banner_h + 16

comp_img = Image.new('RGB', (total_w, total_h), (255, 255, 255))
draw = ImageDraw.Draw(comp_img)

try:
    font = ImageFont.truetype("tahoma.ttf", 13)
except:
    font = ImageFont.load_default()

panels = [
    (t4, "(ก) ข้อ 4: ผังโครงสร้าง Binary Search Tree 12 โหนด", 10),
    (t5, "(ข) ข้อ 5: แผนภาพแปลง Infix เป็น Prefix และ Postfix", 20 + panel_w),
    (t6, "(ค) ข้อ 6: ผังแปลง General Tree ตามหลัก LCRS", 30 + panel_w * 2)
]

for im_p, label, x in panels:
    # Border
    draw.rectangle([x-1, 8-1, x + panel_w, 8 + banner_h + target_h], outline=(180, 180, 180), width=1)
    # Header box
    draw.rectangle([x, 8, x + panel_w - 1, 8 + banner_h - 1], fill=(240, 240, 240))
    draw.text((x + 10, 14), label, fill=(30, 30, 30), font=font)
    # Image
    comp_img.paste(im_p, (x, 8 + banner_h))

for d in ['public/screenshots', 'docs_and_tests/screenshots']:
    p_out = os.path.join(d, 'dataset_samples_image.png')
    comp_img.save(p_out, quality=92)
    print(f"Saved clean composite: {p_out}")

print("\nAll clean images and composite figures generated successfully!")
