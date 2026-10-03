import os, sys, shutil
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

q_images = {
    'case1_ds001.jpg': 'ชุดข้อสอบใหม่/photo_clean_text1/IMG_2791.jpg',
    'case2_ds047.jpg': 'ชุดข้อสอบใหม่/photo_clean_text2/IMG_2853.jpg',
    'case3_ds072.jpg': 'ชุดข้อสอบใหม่/photo_clean_text3/IMG_2895.jpg',
    'case4_ds104.jpg': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่1/LINE_ALBUM_Photo1_260917_2.jpg',
    'case5_ds154.jpg': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่2/LINE_ALBUM_Photo2.1_260918_18.jpg',
    'case6_ds171.jpg': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่3/LINE_ALBUM_Photo2.2_260918_1.jpg'
}

dst_dirs = [
    'docs_and_tests/images/case_studies',
    'public/screenshots/case_studies',
    'public/images/case_studies'
]

for d in dst_dirs:
    os.makedirs(d, exist_ok=True)

for fname, src in q_images.items():
    im = Image.open(src)
    # If landscape and height > width or needs optimization, let's verify
    # Save optimized copy (max dimension 1200px to keep file fast and crisp)
    w, h = im.size
    max_dim = 1200
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        im_resized = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    else:
        im_resized = im.copy()
        
    for d in dst_dirs:
        out_path = os.path.join(d, fname)
        im_resized.save(out_path, quality=90, optimize=True)
        print(f'Saved {out_path} ({im_resized.size})')

print('All 6 case study images prepared and copied successfully!')
