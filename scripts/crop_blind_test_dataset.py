import os
import sys
import io
import json
import asyncio
from typing import List, Dict, Any
from PIL import Image, ImageDraw
import pillow_heif
from dotenv import load_dotenv

pillow_heif.register_heif_opener()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

from server.services.openai_grading import request_structured_output, _image_content

PROMPT_BOX = """คุณคือระบบ Pre-processing สำหรับการทดสอบแบบ Blind Test บนกระดาษข้อสอบ
วิเคราะห์รูปภาพนี้เพื่อเตรียมภาพสำหรับการตรวจแบบปิดตา (ห้าม AI เห็นคะแนนเดิมของอาจารย์เด็ดขาด):
1. "crop_box": ระบุพิกัด [ymin, xmin, ymax, xmax] (สเกล 0-1000) ที่ครอบคลุมเฉพาะพื้นที่คำตอบของนิสิต (เช่น โครงสร้างต้นไม้, ตาราง Array, หรือลายมือเขียนตอบ) โดยตัดขอบกระดาษและคะแนนอาจารย์ที่เขียนไว้ตรงมุมหรือขอบภาพออกไป
2. "teacher_marks": รายการพิกัด [ymin, xmin, ymax, xmax] (สเกล 0-1000) ของรอยตรวจของอาจารย์ทั้งหมด เช่น ตัวเลขคะแนน (เช่น 0.5, 1, 2), ปากกาสีแดง/ส้ม/น้ำเงินที่อาจารย์เขียนตรวจ, วงกลมคะแนน, รอยกาถูก/ผิด ที่ต้องถมสีขาวปิดทับ"""

SCHEMA_BOX = {
    "type": "object",
    "properties": {
        "crop_box": {"type": "array", "items": {"type": "integer"}, "minItems": 4, "maxItems": 4},
        "teacher_marks": {
            "type": "array",
            "items": {"type": "array", "items": {"type": "integer"}, "minItems": 4, "maxItems": 4}
        }
    },
    "required": ["crop_box", "teacher_marks"],
    "additionalProperties": False
}

async def process_image(src_path: str, dst_path: str, sem: asyncio.Semaphore, idx: int, total: int) -> Dict[str, Any]:
    # Skip if already cropped and valid
    if os.path.exists(dst_path) and os.path.getsize(dst_path) > 1000:
        print(f"[{idx}/{total}] Already exists, skipping: {os.path.basename(dst_path)}")
        return {"src": src_path, "dst": dst_path, "status": "skipped"}

    async with sem:
        try:
            # Load with PIL (supports both HEIC and JPG)
            im = Image.open(src_path)
            if im.mode != "RGB":
                im = im.convert("RGB")
            w, h = im.size

            # Create scaled copy for API upload (max dim 1600 to speed up upload & save tokens)
            max_dim = 1600
            if max(w, h) > max_dim:
                scale = max_dim / max(w, h)
                im_preview = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            else:
                im_preview = im

            preview_buf = io.BytesIO()
            im_preview.save(preview_buf, format="JPEG", quality=85)
            preview_bytes = preview_buf.getvalue()

            res = await request_structured_output([
                {"type": "input_text", "text": PROMPT_BOX},
                _image_content(preview_bytes, "image/jpeg")
            ], SCHEMA_BOX, "detect_blind_boxes")

            # 1. Mask teacher marks on original resolution image
            im_clean = im.copy()
            draw = ImageDraw.Draw(im_clean)
            for box in res.get("teacher_marks", []):
                ymin, xmin, ymax, xmax = box
                px_box = [xmin * w / 1000, ymin * h / 1000, xmax * w / 1000, ymax * h / 1000]
                pad = 8
                draw.rectangle([px_box[0]-pad, px_box[1]-pad, px_box[2]+pad, px_box[3]+pad], fill=(255, 255, 255))

            # 2. Crop student answer box with margin
            ymin, xmin, ymax, xmax = res["crop_box"]
            pad = 12
            crop_px = (
                max(0, int(xmin * w / 1000) - pad),
                max(0, int(ymin * h / 1000) - pad),
                min(w, int(xmax * w / 1000) + pad),
                min(h, int(ymax * h / 1000) + pad)
            )
            im_cropped = im_clean.crop(crop_px)

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            im_cropped.save(dst_path, "JPEG", quality=95)
            print(f"[{idx}/{total}] Cropped & Cleaned: {os.path.basename(dst_path)} (Orig: {w}x{h} -> Crop: {im_cropped.size[0]}x{im_cropped.size[1]})")

            return {
                "src": src_path,
                "dst": dst_path,
                "status": "success",
                "crop_box": res["crop_box"],
                "marks_count": len(res.get("teacher_marks", []))
            }
        except Exception as e:
            print(f"[{idx}/{total}] ERROR processing {src_path}: {e}")
            return {"src": src_path, "dst": dst_path, "status": "error", "error": str(e)}

async def batch_crop_folder(src_folder: str, dst_folder: str, sem: asyncio.Semaphore):
    os.makedirs(dst_folder, exist_ok=True)
    valid_exts = ('.jpg', '.jpeg', '.png', '.heic')
    files = sorted([f for f in os.listdir(src_folder) if f.lower().endswith(valid_exts)])

    print(f"\n============================================================")
    print(f" Folder: {src_folder} -> {dst_folder} ({len(files)} files)")
    print(f"============================================================")

    tasks = []
    for idx, f in enumerate(files, 1):
        src_p = os.path.join(src_folder, f)
        # Always save as .jpg for uniform compatibility
        base_name = os.path.splitext(f)[0] + ".jpg"
        dst_p = os.path.join(dst_folder, base_name)
        tasks.append(process_image(src_p, dst_p, sem, idx, len(files)))

    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r.get("status") in ["success", "skipped"])
    print(f"Completed {success_count}/{len(files)} in {dst_folder}")
    return results

async def main():
    concurrency = 4
    sem = asyncio.Semaphore(concurrency)

    # 1. Diagram Photos (Questions 4, 5, 6)
    folders_to_process = [
        ("photoชุดที่1", "photo_crop_ชุดที่1"),
        ("photoชุดที่2", "photo_crop_ชุดที่2"),
        ("photoชุดที่3", "photo_crop_ชุดที่3"),
        # 2. Handwriting Text Photos (Questions 1, 2, 3)
        ("โจทย์textชุดที่1", "photo_crop_text1"),
        ("โจทย์textชุดที่2", "photo_crop_text2"),
        ("โจทย์textชุดที่3", "photo_crop_text3"),
    ]

    for src_name, dst_name in folders_to_process:
        src = os.path.join("ชุดข้อสอบใหม่", src_name)
        dst = os.path.join("ชุดข้อสอบใหม่", dst_name)
        if os.path.exists(src):
            await batch_crop_folder(src, dst, sem)
        else:
            print(f"Source folder not found: {src}")

    print("\n============================================================")
    print(" ALL EXAM PHOTOS CROPPED & SCORES MASKED SUCCESSFULLY!")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(main())
