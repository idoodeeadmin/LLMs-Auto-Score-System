import os, sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

sets = [
    ('photoชุดที่1', 'LINE_ALBUM_Photo1_260917_2.jpg'),
    ('photoชุดที่2', 'LINE_ALBUM_Photo2.1_260918_18.jpg'),
    ('photoชุดที่3', 'LINE_ALBUM_Photo2.2_260918_1.jpg')
]

for s, fn in sets:
    p_orig = os.path.join('ชุดข้อสอบใหม่', s, fn)
    p_clean = os.path.join('ชุดข้อสอบใหม่', s.replace('photo', 'photo_clean_'), fn)
    im_o = np.array(Image.open(p_orig))
    im_c = np.array(Image.open(p_clean))
    print(f"{s}/{fn}: Orig shape={im_o.shape}, Clean shape={im_c.shape}")
    diff = np.abs(im_o.astype(int) - im_c.astype(int))
    diff_count = np.count_nonzero(np.max(diff, axis=-1) > 25)
    print(f"   Pixels modified during cleaning: {diff_count}")
