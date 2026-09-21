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

PROMPT_DETECT = """คุณคือระบบ Computer Vision สำหรับเตรียมเอกสารสอบ Blind Test
วิเคราะห์รูปภาพนี้เพื่อค้นหา 'คะแนนและรอยตรวจของอาจารย์' ทั้งหมดอย่างแม่นยำระดับพิกเซล:
1. ระบุพิกัด 'box' [ymin, xmin, ymax, xmax] (สเกล 0-1000) ของรอยตรวจแต่ละจุด (ครอบเฉพาะรอยตรวจให้กระชับที่สุด ห้ามเผื่อขอบกว้าง)
2. 'overlaps_answer': true ถ้าเขียนทับเส้นคำตอบ ตาราง หรือรูปวาดของนิสิต / false ถ้าอยู่ในที่ว่าง ขอบกระดาษ หรือมุมกระดาษ
3. 'mark_color': สีของรอยตรวจ (เช่น 'red', 'orange', 'blue', 'pencil')
4. 'description': คำอธิบายสั้นๆ ของรอยตรวจนั้น
"""

SCHEMA_DETECT = {
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

def get_cleanest_paper_patch(img, y0, y1, x0, x1):
    """Samples the cleanest blank paper patch from nearby margin with lowest edge energy."""
    h, w, _ = img.shape
    bh, bw = y1 - y0, x1 - x0
    candidates = []
    
    # 1. Above
    if y0 - bh - 8 >= 0:
        candidates.append((y0 - bh - 8, y0 - 8, x0, x1))
    # 2. Left
    if x0 - bw - 8 >= 0:
        candidates.append((y0, y1, x0 - bw - 8, x0 - 8))
    # 3. Below
    if y1 + bh + 8 <= h:
        candidates.append((y1 + 8, y1 + bh + 8, x0, x1))
    # 4. Right
    if x1 + bw + 8 <= w:
        candidates.append((y0, y1, x1 + 8, x1 + bw + 8))
        
    best_patch = None
    min_edges = float('inf')
    for cy0, cy1, cx0, cx1 in candidates:
        patch = img[cy0:cy1, cx0:cx1]
        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
        edges = np.count_nonzero(cv2.Canny(gray, 40, 120))
        if edges < min_edges:
            min_edges = edges
            best_patch = patch
            
    if best_patch is not None and best_patch.shape[:2] == (bh, bw) and min_edges < 100:
        return best_patch
        
    # Fallback: estimate local paper color and synthesize texture with mild paper noise
    surround = img[max(0, y0-25):min(h, y1+25), max(0, x0-25):min(w, x1+25)]
    med_col = np.median(surround, axis=(0, 1)).astype(np.float32)
    # Generate realistic subtle paper noise
    noise = np.random.normal(0, 1.5, (bh, bw, 3))
    synth_patch = np.clip(med_col + noise, 0, 255).astype(np.uint8)
    return synth_patch

def apply_real_texture_patch(img, y0, y1, x0, x1):
    """Method: Real Texture Patching with Feathered Edge Blending (Seamless, zero ghost marks)."""
    h, w, _ = img.shape
    y0, y1 = max(0, y0), min(h, y1)
    x0, x1 = max(0, x0), min(w, x1)
    bh, bw = y1 - y0, x1 - x0
    if bh <= 2 or bw <= 2:
        return img
        
    patch = get_cleanest_paper_patch(img, y0, y1, x0, x1)
    
    # Smooth elliptical alpha mask
    mask = np.zeros((bh, bw), dtype=np.float32)
    cv2.ellipse(mask, (bw // 2, bh // 2), (max(1, bw // 2 - 2), max(1, bh // 2 - 2)), 0, 0, 360, 1.0, -1)
    k_size = max(5, (int(min(bw, bh) * 0.35) // 2) * 2 + 1)
    mask = cv2.GaussianBlur(mask, (k_size, k_size), 0)
    mask_3ch = np.dstack([mask, mask, mask])
    
    target_roi = img[y0:y1, x0:x1].astype(np.float32)
    patch_float = patch.astype(np.float32)
    blended = (patch_float * mask_3ch + target_roi * (1.0 - mask_3ch)).astype(np.uint8)
    img[y0:y1, x0:x1] = blended
    return img

def apply_ai_structure_edit(img, y0, y1, x0, x1, mark_color):
    """Method: AI / Structural inpainting for overlapping marks, preserving student strokes."""
    h, w, _ = img.shape
    y0, y1 = max(0, y0), min(h, y1)
    x0, x1 = max(0, x0), min(w, x1)
    bh, bw = y1 - y0, x1 - x0
    if bh <= 2 or bw <= 2:
        return img

    roi = img[y0:y1, x0:x1].copy()
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    if mark_color in ["red", "orange", "pink", "red/pink"]:
        # Wide-spectrum red mask covering faint halo edges
        m1 = cv2.inRange(hsv_roi, np.array([0, 25, 35]), np.array([18, 255, 255]))
        m2 = cv2.inRange(hsv_roi, np.array([155, 25, 35]), np.array([180, 255, 255]))
        mask_stroke = cv2.dilate(m1 | m2, np.ones((5, 5), np.uint8), iterations=1)
        if np.count_nonzero(mask_stroke) > 0:
            roi_reconstructed = cv2.inpaint(roi, mask_stroke, 5, cv2.INPAINT_NS)
            img[y0:y1, x0:x1] = roi_reconstructed
    else:
        # Complex / same color stroke removal using morphological frequency reconstruction
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Threshold top 10% darkest strokes in ROI
        _, dark_mask = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dil = cv2.dilate(dark_mask, kernel, iterations=1)
        if np.count_nonzero(dil) > 0:
            roi_reconstructed = cv2.inpaint(roi, dil, 3, cv2.INPAINT_TELEA)
            img[y0:y1, x0:x1] = roi_reconstructed
            
    return img

async def process_image_adaptive(src_path: str, dst_path: str, sem: asyncio.Semaphore, idx: int, total: int):
    async with sem:
        try:
            with open(src_path, "rb") as f:
                img_bgr = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
            h, w, _ = img_bgr.shape

            # Prepare preview for AI Vision detection
            _, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            preview_bytes = buf.tobytes()

            res = await request_structured_output([
                {"type": "input_text", "text": PROMPT_DETECT},
                _image_content(preview_bytes, "image/jpeg")
            ], SCHEMA_DETECT, "detect_teacher_marks")

            has_marks = res.get("has_marks", False)
            marks = res.get("marks", [])

            processed_img = img_bgr.copy()
            patch_cnt = 0
            ai_edit_cnt = 0

            if has_marks and marks:
                for m in marks:
                    box = m["box"]
                    ymin, xmin, ymax, xmax = box
                    ymin_c, ymax_c = min(ymin, ymax), max(ymin, ymax)
                    xmin_c, xmax_c = min(xmin, xmax), max(xmin, xmax)
                    
                    # Convert to pixel coordinates with margin
                    pad = 6
                    y0 = max(0, int(ymin_c * h / 1000) - pad)
                    y1 = min(h, int(ymax_c * h / 1000) + pad)
                    x0 = max(0, int(xmin_c * w / 1000) - pad)
                    x1 = min(w, int(xmax_c * w / 1000) + pad)

                    overlaps = m.get("overlaps_answer", False)
                    mark_color = m.get("mark_color", "red").lower()

                    if not overlaps:
                        # Strategy: Real Texture Patching (Free margin, zero ghost trace)
                        processed_img = apply_real_texture_patch(processed_img, y0, y1, x0, x1)
                        patch_cnt += 1
                    else:
                        # Strategy: AI Structural Edit (Overlapping, preserve student strokes)
                        processed_img = apply_ai_structure_edit(processed_img, y0, y1, x0, x1, mark_color)
                        ai_edit_cnt += 1

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            _, out_buf = cv2.imencode(".jpg", processed_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            with open(dst_path, "wb") as f:
                f.write(out_buf)

            print(f"[{idx}/{total}] Processed: {os.path.basename(dst_path)} (Texture Patches: {patch_cnt}, AI Edits: {ai_edit_cnt})")
            return {"file": os.path.basename(src_path), "status": "success", "patches": patch_cnt, "ai_edits": ai_edit_cnt}
        except Exception as e:
            print(f"[{idx}/{total}] ERROR processing {src_path}: {e}")
            return {"file": os.path.basename(src_path), "status": "error", "error": str(e)}

async def batch_process_folder(src_folder: str, dst_folder: str, sem: asyncio.Semaphore):
    valid_exts = ('.jpg', '.jpeg', '.png')
    files = sorted([f for f in os.listdir(src_folder) if f.lower().endswith(valid_exts)])
    print(f"\n============================================================")
    print(f" Real Texture Patching & AI Edit: {src_folder} -> {dst_folder} ({len(files)} files)")
    print(f"============================================================")

    tasks = []
    for idx, f in enumerate(files, 1):
        src_p = os.path.join(src_folder, f)
        dst_p = os.path.join(dst_folder, f)
        tasks.append(process_image_adaptive(src_p, dst_p, sem, idx, len(files)))

    results = await asyncio.gather(*tasks)
    success_cnt = sum(1 for r in results if r.get("status") == "success")
    print(f"Completed {success_cnt}/{len(files)} in {dst_folder}")
    return results

async def main():
    concurrency = 4
    sem = asyncio.Semaphore(concurrency)

    # 3 Diagram Folders (Q4 BST, Q5 Array, Q6 Tree Conversion)
    folders = [
        ("photoชุดที่1", "photo_clean_ชุดที่1"),
        ("photoชุดที่2", "photo_clean_ชุดที่2"),
        ("photoชุดที่3", "photo_clean_ชุดที่3"),
    ]

    for src_name, dst_name in folders:
        src = os.path.join("ชุดข้อสอบใหม่", src_name)
        dst = os.path.join("ชุดข้อสอบใหม่", dst_name)
        if os.path.exists(src):
            await batch_process_folder(src, dst, sem)
        else:
            print(f"Folder not found: {src}")

    # Sync to photo_mask_ชุดที่1-3 so benchmark immediately uses the best images!
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
    print(" ALL 3 PHOTO SETS PROCESSED WITH REAL TEXTURE PATCHING & AI EDIT!")
    print("============================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
