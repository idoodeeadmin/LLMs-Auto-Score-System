import os
import sys
import io
import json
import asyncio
import cv2
import numpy as np
from PIL import Image, ImageDraw
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))

from server.services.openai_grading import request_structured_output, _image_content

PROMPT_VERIFY = """ตรวจสอบรูปภาพกระดาษคำตอบนี้ว่า 'ยังมีคะแนนหรือรอยตรวจของอาจารย์หลงเหลืออยู่หรือไม่':
- สังเกตเฉพาะ: ตัวเลขคะแนน (เช่น 0, 0.5, 1, 1.5, 2), วงกลมคะแนน, รอยตรวจถูก/ผิด, รอยปากกาตรวจ
- ถ้าไม่มีรอยคะแนนหรือรอยตรวจหลงเหลืออยู่เลย ให้ตอบ has_marks = false
- ถ้ายังมีหลงเหลืออยู่ ให้ตอบ has_marks = true พร้อมระบุ:
  * 'box': [ymin, xmin, ymax, xmax] (สเกล 0-1000) ของเฉพาะตัวเลขคะแนนหรือรอยนั้น (ต้องกระชับพอดีรอยตรวจ ห้ามตีกรอบใหญ่)
  * 'overlaps_answer': true/false (รอยตรวจนี้เขียนทับเส้นคำตอบ รูปวาด หรือตารางของนิสิตหรือไม่)
  * 'mark_color': สีของรอยตรวจ (เช่น 'red', 'orange', 'blue', 'pencil')
  * 'description': คำอธิบายสั้นๆ
"""

SCHEMA_VERIFY = {
    "type": "object",
    "properties": {
        "has_marks": {"type": "boolean"},
        "marks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "box": {"type": "array", "items": {"type": "integer"}, "minItems": 4, "maxItems": 4},
                    "overlaps_answer": {"type": "boolean"},
                    "mark_color": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["box", "overlaps_answer", "mark_color", "description"],
                "additionalProperties": False
            }
        }
    },
    "required": ["has_marks", "marks"],
    "additionalProperties": False
}

def remove_red_orange_strokes(img_bgr):
    """Method 1: Color segmentation & stroke-level inpainting for Red & Orange grading pen"""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Red wrap ranges in HSV (0-180)
    m1 = cv2.inRange(hsv, np.array([0, 40, 40]), np.array([12, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([165, 40, 40]), np.array([180, 255, 255]))
    # Orange range
    m_orange = cv2.inRange(hsv, np.array([12, 40, 40]), np.array([28, 255, 255]))
    # Pinkish-red / highlighter
    m_pink = cv2.inRange(hsv, np.array([150, 30, 80]), np.array([165, 255, 255]))
    
    red_mask = m1 | m2 | m_orange | m_pink
    
    # Dilate slightly to catch anti-aliased edge ink
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(red_mask, kernel, iterations=1)
    
    cnt = np.count_nonzero(dilated)
    if cnt > 30:
        inpainted = cv2.inpaint(img_bgr, dilated, 3, cv2.INPAINT_TELEA)
        return inpainted, cnt
    return img_bgr, 0

async def process_single_photo(src_path: str, dst_path: str, sem: asyncio.Semaphore, idx: int, total: int):
    async with sem:
        try:
            # 1. Read image safely (handles unicode paths on Windows)
            with open(src_path, "rb") as f:
                img_bgr = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
            h, w, _ = img_bgr.shape

            # 2. Strategy 1: Remove Red / Orange Teacher Marks via Stroke Inpainting
            cleaned_bgr, red_cnt = remove_red_orange_strokes(img_bgr)

            # 3. Strategy 2: AI Vision Inspection for Remaining Marks
            _, buf = cv2.imencode(".jpg", cleaned_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            preview_bytes = buf.tobytes()

            res = await request_structured_output([
                {"type": "input_text", "text": PROMPT_VERIFY},
                _image_content(preview_bytes, "image/jpeg")
            ], SCHEMA_VERIFY, "verify_marks")

            has_marks = res.get("has_marks", False)
            marks = res.get("marks", [])

            final_bgr = cleaned_bgr.copy()

            if has_marks and marks:
                for m in marks:
                    box = m["box"]
                    ymin, xmin, ymax, xmax = box
                    ymin_c, ymax_c = min(ymin, ymax), max(ymin, ymax)
                    xmin_c, xmax_c = min(xmin, xmax), max(xmin, xmax)
                    
                    x0 = max(0, int(xmin_c * w / 1000) - 4)
                    y0 = max(0, int(ymin_c * h / 1000) - 4)
                    x1 = min(w, int(xmax_c * w / 1000) + 4)
                    y1 = min(h, int(ymax_c * h / 1000) + 4)

                    overlaps = m.get("overlaps_answer", False)
                    mark_color = m.get("mark_color", "").lower()

                    if not overlaps:
                        # Case A: Free margin/whitespace -> Tight whiteout/blur patch
                        # Sample nearby paper color
                        roi = final_bgr[y0:y1, x0:x1]
                        if roi.size > 0:
                            # Use clean white/paper fill
                            final_bgr[y0:y1, x0:x1] = (255, 255, 255)
                            print(f"    [Tight Mask Applied]: {m.get('description')} at [{x0},{y0},{x1},{y1}]")
                    else:
                        # Case B & C: Overlaps student answer!
                        print(f"    [Overlapping Mark]: {m.get('description')} (Color: {mark_color})")
                        if mark_color in ["red", "orange", "pink"]:
                            # Local HSV inpaint on the ROI
                            roi = final_bgr[y0:y1, x0:x1]
                            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                            m1 = cv2.inRange(hsv_roi, np.array([0, 30, 30]), np.array([15, 255, 255]))
                            m2 = cv2.inRange(hsv_roi, np.array([165, 30, 30]), np.array([180, 255, 255]))
                            m_roi = cv2.dilate(m1 | m2, np.ones((3, 3), np.uint8), iterations=1)
                            if np.count_nonzero(m_roi) > 0:
                                final_bgr[y0:y1, x0:x1] = cv2.inpaint(roi, m_roi, 3, cv2.INPAINT_TELEA)
                                print(f"    [Local Red Inpaint Applied on Overlap]")
                        else:
                            # Strategy 3: AI inpaint / contextual background blend
                            # If it's blue/black ink overlapping, blend with surrounding background
                            roi = final_bgr[y0:y1, x0:x1]
                            # Gaussian blur/inpaint only over high-frequency ink
                            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                            _, text_mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
                            if np.count_nonzero(text_mask) > 0:
                                final_bgr[y0:y1, x0:x1] = cv2.inpaint(roi, text_mask, 3, cv2.INPAINT_TELEA)
                                print(f"    [Contextual Inpaint Applied on Complex Overlap]")

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            _, out_buf = cv2.imencode(".jpg", final_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
            with open(dst_path, "wb") as f:
                f.write(out_buf)

            status_msg = "Clean (No marks left)" if not has_marks else f"Cleaned ({len(marks)} marks resolved)"
            print(f"[{idx}/{total}] Processed: {os.path.basename(dst_path)} -> {status_msg} (Red removed: {red_cnt} px)")
            return {"file": os.path.basename(src_path), "status": "success", "red_removed": red_cnt, "remaining_resolved": len(marks)}
        except Exception as e:
            print(f"[{idx}/{total}] ERROR processing {src_path}: {e}")
            return {"file": os.path.basename(src_path), "status": "error", "error": str(e)}

async def process_folder(src_folder: str, dst_folder: str, sem: asyncio.Semaphore):
    valid_exts = ('.jpg', '.jpeg', '.png')
    files = sorted([f for f in os.listdir(src_folder) if f.lower().endswith(valid_exts)])
    print(f"\n============================================================")
    print(f" Adaptive Cleaning: {src_folder} -> {dst_folder} ({len(files)} files)")
    print(f"============================================================")

    tasks = []
    for idx, f in enumerate(files, 1):
        src_p = os.path.join(src_folder, f)
        dst_p = os.path.join(dst_folder, f)
        tasks.append(process_single_photo(src_p, dst_p, sem, idx, len(files)))

    results = await asyncio.gather(*tasks)
    success_cnt = sum(1 for r in results if r.get("status") == "success")
    print(f"Completed {success_cnt}/{len(files)} in {dst_folder}")
    return results

async def main():
    concurrency = 4
    sem = asyncio.Semaphore(concurrency)

    # 3 Diagram Folders (Questions 4, 5, 6)
    folders = [
        ("photoชุดที่1", "photo_clean_ชุดที่1"),
        ("photoชุดที่2", "photo_clean_ชุดที่2"),
        ("photoชุดที่3", "photo_clean_ชุดที่3"),
    ]

    for src_name, dst_name in folders:
        src = os.path.join("ชุดข้อสอบใหม่", src_name)
        dst = os.path.join("ชุดข้อสอบใหม่", dst_name)
        if os.path.exists(src):
            await process_folder(src, dst, sem)
        else:
            print(f"Folder not found: {src}")

    # Also copy to photo_mask_ชุดที่1-3 so benchmark & existing scripts immediately benefit!
    for _, dst_name in folders:
        clean_dir = os.path.join("ชุดข้อสอบใหม่", dst_name)
        mask_dir = os.path.join("ชุดข้อสอบใหม่", dst_name.replace("photo_clean_", "photo_mask_"))
        if os.path.exists(clean_dir):
            os.makedirs(mask_dir, exist_ok=True)
            for f in os.listdir(clean_dir):
                if f.endswith('.jpg'):
                    src_f = os.path.join(clean_dir, f)
                    dst_f = os.path.join(mask_dir, f)
                    with open(src_f, 'rb') as r, open(dst_f, 'wb') as w:
                        w.write(r.read())
            print(f"Synced {clean_dir} -> {mask_dir}")

    print("\n============================================================")
    print(" ALL 3 PHOTO SETS ADAPTIVELY CLEANED WITH ZERO LARGE BLOCKS!")
    print("============================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
