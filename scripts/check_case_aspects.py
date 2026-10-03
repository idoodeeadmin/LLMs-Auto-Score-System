import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

q_images = {
    'case1_ds001': 'ชุดข้อสอบใหม่/photo_clean_text1/IMG_2791.jpg',
    'case2_ds047': 'ชุดข้อสอบใหม่/photo_clean_text2/IMG_2853.jpg',
    'case3_ds072': 'ชุดข้อสอบใหม่/photo_clean_text3/IMG_2895.jpg',
    'case4_ds104': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่1/LINE_ALBUM_Photo1_260917_2.jpg',
    'case5_ds154': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่2/LINE_ALBUM_Photo2.1_260918_18.jpg',
    'case6_ds171': 'ชุดข้อสอบใหม่/photo_clean_ชุดที่3/LINE_ALBUM_Photo2.2_260918_1.jpg'
}

for name, path in q_images.items():
    im = Image.open(path)
    w, h = im.size
    aspect = 'Landscape' if w > h else 'Portrait'
    print(f'{name}: size=({w}, {h}) | {aspect}')
