import os
import cv2
import numpy as np
from PIL import Image

def get_best_upright_image(path: str) -> Image.Image:
    with open(path, "rb") as f:
        orig = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    
    # We want landscape: width = 1477, height = 1108
    # Test rotation 90 vs 270:
    rot_90 = cv2.rotate(orig, cv2.ROTATE_90_CLOCKWISE)        # shape (1108, 1477)
    rot_270 = cv2.rotate(orig, cv2.ROTATE_90_COUNTERCLOCKWISE) # shape (1108, 1477)
    
    # In upright orientation, the header line "4. จากข้อมูลต่อไปนี้..." and top border are in the top 200 pixels
    gray_90 = cv2.cvtColor(rot_90, cv2.COLOR_BGR2GRAY)
    gray_270 = cv2.cvtColor(rot_270, cv2.COLOR_BGR2GRAY)
    
    score_90 = np.sum(gray_90[:180, :] < 100) - np.sum(gray_90[-180:, :] < 100)
    score_270 = np.sum(gray_270[:180, :] < 100) - np.sum(gray_270[-180:, :] < 100)
    
    if score_90 >= score_270:
        best_cv = rot_90
        chosen = 90
    else:
        best_cv = rot_270
        chosen = 270
        
    rgb = cv2.cvtColor(best_cv, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb), chosen

def test_all():
    clean_dir = os.path.join("ชุดข้อสอบใหม่", "photo_clean_ชุดที่1")
    for i in range(1, 35):
        fn = f"LINE_ALBUM_Photo1_260917_{i}.jpg"
        p = os.path.join(clean_dir, fn)
        img, ch = get_best_upright_image(p)
        print(f"[{i:2d}] Chosen rotation: {ch} deg")

if __name__ == '__main__':
    test_all()
