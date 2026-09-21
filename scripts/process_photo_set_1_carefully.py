import os
import sys
import io
import json
import asyncio
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))

from server.services.openai_grading import request_structured_output, _image_content

SRC_DIR = os.path.join("ชุดข้อสอบใหม่", "photoชุดที่1")
DST_DIR = os.path.join("ชุดข้อสอบใหม่", "photo_set1_carefully_cleaned")
os.makedirs(DST_DIR, exist_ok=True)

PROMPT_BOXES = """คุณคือนักวิจัยด้าน Document Processing วิเคราะห์ภาพข้อสอบ Binary Search Tree นี้:
ระบุพิกัด 'score_boxes' ทั้งหมดที่เป็น:
1. ตัวเลขคะแนนที่อาจารย์เขียน (เช่น 0, 0.5, 1, 2)
2. วงกลมคะแนน หรือรอยปากกาตรวจของอาจารย์ที่อยู่นอกโครงสร้างต้นไม้
สำหรับแต่ละจุด ให้ระบุพิกัด [ymin, xmin, ymax, xmax] (สเกล 0-1000) ที่ครอบเฉพาะตัวเลขหรือรอยนั้นอย่างกระชับที่สุด (ห้ามครอบใหญ่จนลามไปโดนต้นไม้ของนิสิต)
"""

SCHEMA_BOXES = {
    "type": "object",
    "properties": {
        "has_scores": {"type": "boolean"},
        "score_boxes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "box": {"type": "array", "items": {"type": "integer"}, "minItems": 4, "maxItems": 4},
                    "description": {"type": "string"},
                    "score_detected": {"type": "string"}
                },
                "required": ["box", "description", "score_detected"],
                "additionalProperties": False
            }
        }
    },
    "required": ["has_scores", "score_boxes"],
    "additionalProperties": False
}

def clean_box_with_natural_paper(img_bgr, y0, y1, x0, x1):
    """Fills the box with the exact matching local paper color and subtle paper grain."""
    h, w, _ = img_bgr.shape
    y0, y1 = max(0, y0), min(h, y1)
    x0, x1 = max(0, x0), min(w, x1)
    bh, bw = y1 - y0, x1 - x0
    if bh <= 2 or bw <= 2:
        return img_bgr

    # Sample local paper from a 15px ring around the box (excluding the box itself)
    ring_mask = np.zeros((h, w), dtype=np.uint8)
    pad = 12
    ring_mask[max(0, y0-pad):min(h, y1+pad), max(0, x0-pad):min(w, x1+pad)] = 255
    ring_mask[y0:y1, x0:x1] = 0
    
    local_pixels = img_bgr[ring_mask > 0]
    if len(local_pixels) > 0:
        # Median color of surrounding paper
        paper_bgr = np.median(local_pixels, axis=0)
    else:
        paper_bgr = np.array([170, 170, 170], dtype=np.float32)

    # Smooth feathered ellipse
    mask = np.zeros((bh, bw), dtype=np.float32)
    cv2.ellipse(mask, (bw // 2, bh // 2), (max(1, bw // 2 - 2), max(1, bh // 2 - 2)), 0, 0, 360, 1.0, -1)
    k_size = max(5, (int(min(bw, bh) * 0.25) // 2) * 2 + 1)
    mask = cv2.GaussianBlur(mask, (k_size, k_size), 0)
    mask_3ch = np.dstack([mask, mask, mask])

    # Add realistic subtle paper grain noise (+- 2 levels)
    noise = np.random.normal(0, 1.2, (bh, bw, 3)).astype(np.float32)
    patch = np.clip(paper_bgr + noise, 0, 255).astype(np.float32)

    target_roi = img_bgr[y0:y1, x0:x1].astype(np.float32)
    blended = (patch * mask_3ch + target_roi * (1.0 - mask_3ch)).astype(np.uint8)
    img_bgr[y0:y1, x0:x1] = blended
    return img_bgr

async def process_photo_meticulously(filename: str, idx: int, total: int, sem: asyncio.Semaphore):
    async with sem:
        src_path = os.path.join(SRC_DIR, filename)
        dst_path = os.path.join(DST_DIR, filename)
        
        with open(src_path, "rb") as fh:
            img_bgr = cv2.imdecode(np.frombuffer(fh.read(), np.uint8), cv2.IMREAD_COLOR)
        h, w, _ = img_bgr.shape

        # Step 1: Detect exact score boxes via AI Vision
        _, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
        res = await request_structured_output([
            {"type": "input_text", "text": PROMPT_BOXES},
            _image_content(buf.tobytes(), "image/jpeg")
        ], SCHEMA_BOXES, "detect_scores")

        score_boxes = res.get("score_boxes", [])
        cleaned = img_bgr.copy()

        # Step 2: Remove isolated teacher scores with natural matching paper
        for item in score_boxes:
            box = item["box"]
            ymin, xmin, ymax, xmax = box
            ymin_c, ymax_c = min(ymin, ymax), max(ymin, ymax)
            xmin_c, xmax_c = min(xmin, xmax), max(xmin, xmax)

            # Convert to pixels with tight padding (6px)
            pad = 6
            y0 = max(0, int(ymin_c * h / 1000) - pad)
            y1 = min(h, int(ymax_c * h / 1000) + pad)
            x0 = max(0, int(xmin_c * w / 1000) - pad)
            x1 = min(w, int(xmax_c * w / 1000) + pad)

            clean_box_with_natural_paper(cleaned, y0, y1, x0, x1)

        # Step 3: Remove any stray red ink on non-student areas
        hsv = cv2.cvtColor(cleaned, cv2.COLOR_BGR2HSV)
        m1 = cv2.inRange(hsv, np.array([0, 30, 40]), np.array([15, 255, 255]))
        m2 = cv2.inRange(hsv, np.array([160, 30, 40]), np.array([180, 255, 255]))
        red = cv2.dilate(m1 | m2, np.ones((3, 3), np.uint8), iterations=1)
        
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(red)
        for i in range(1, num_labels):
            x, y, bw, bh, area = stats[i]
            # If there's a stray red checkmark/dot with area between 15 and 3000
            if 15 < area < 3000:
                pad = 4
                ry0, ry1 = max(0, y - pad), min(h, y + bh + pad)
                rx0, rx1 = max(0, x - pad), min(w, x + bw + pad)
                clean_box_with_natural_paper(cleaned, ry0, ry1, rx0, rx1)

        # Save high quality JPEG
        _, out_buf = cv2.imencode(".jpg", cleaned, [cv2.IMWRITE_JPEG_QUALITY, 96])
        with open(dst_path, "wb") as fh:
            fh.write(out_buf)

        scores_str = ", ".join([f"{s.get('score_detected')} at {s.get('box')}" for s in score_boxes]) or "None"
        print(f"[{idx:02d}/{total}] Cleaned: {filename} -> Scores removed: [{scores_str}]")
        return {"file": filename, "scores_removed": len(score_boxes)}

async def main():
    files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith(".jpg")])
    print(f"Starting Meticulous Cleaning for Photo Set 1 ({len(files)} files)...")
    sem = asyncio.Semaphore(4)
    tasks = [process_photo_meticulously(f, idx, len(files), sem) for idx, f in enumerate(files, 1)]
    results = await asyncio.gather(*tasks)
    print(f"\nAll {len(results)} files in Photo Set 1 meticulously cleaned and saved to {DST_DIR}!")

if __name__ == "__main__":
    asyncio.run(main())
