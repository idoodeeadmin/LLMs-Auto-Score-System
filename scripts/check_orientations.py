import os
import cv2
import numpy as np

def check_orientations():
    clean_dir = os.path.join("ชุดข้อสอบใหม่", "photo_clean_ชุดที่1")
    # For each image, let's look at the black horizontal border line of question 4 box!
    # The question 4 has a big rectangular box enclosing the student answer!
    # The header line "[ 4 ]" is above the box!
    # If the page is rotated, let's find the orientation of the box and text.
    for i in range(1, 35):
        fn = f"LINE_ALBUM_Photo1_260917_{i}.jpg"
        path = os.path.join(clean_dir, fn)
        with open(path, "rb") as f:
            img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
        
        # Check mean intensity of right edge vs left edge vs top edge vs bottom edge
        # Or look at where the printed text 'Binary search tree' is:
        # In grayscale:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape # 1477, 1108
        
        # Let's check text density in strip x in [0:150] vs [w-150:w]
        left_strip = np.mean(gray[:, :120] < 120)
        right_strip = np.mean(gray[:, w-120:] < 120)
        top_strip = np.mean(gray[:120, :] < 120)
        bottom_strip = np.mean(gray[h-120:, :] < 120)
        
        print(f"[{i:2d}] left={left_strip:.4f}, right={right_strip:.4f}, top={top_strip:.4f}, bottom={bottom_strip:.4f}")

if __name__ == '__main__':
    check_orientations()
