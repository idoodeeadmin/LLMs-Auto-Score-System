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

PROMPT_TEACHER_MARKS = """คุณคือระบบ Pre-processing สำหรับการทดสอบแบบ Blind Test บนกระดาษข้อสอบ
หน้าที่ของคุณคือค้นหารอยตรวจและคะแนนของอาจารย์บนกระดาษข้อสอบ เพื่อทำการถมสีขาวปิดทับ (Whiteout / Masking) โดยห้ามตัดภาพ (No Crop):
ระบุพิกัด 'teacher_marks' เป็นรายการของ [ymin, xmin, ymax, xmax] (สเกล 0-1000):
1. ตัวเลขคะแนนที่อาจารย์เขียน เช่น 0.5, 1, 1.5, 2, 0 หรือคะแนนเศษส่วน
2. รอยตรวจปากกาสีแดง ส้ม หรือน้ำเงินเข้มของอาจารย์ เช่น เครื่องหมายถูก (✓), กากบาทผิด (✗), วงกลมคะแนน, ขีดเส้นใต้ตรวจ
คำเตือนสำคัญมาก: ห้ามระบุพื้นที่คำตอบของนิสิตหรือรูปวาดของนิสิต ให้ระบุเฉพาะรอยปากกาตรวจและตัวเลขคะแนนของอาจารย์เท่านั้น เพื่อรักษารูปวาดและคำตอบของนิสิตไว้ครบ 100%"""

SCHEMA_TEACHER_MARKS = {
    "type": "object",
    "properties": {
        "teacher_marks": {
            "type": "array",
            "items": {"type": "array", "items": {"type": "integer"}, "minItems": 4, "maxItems": 4}
        },
        "description": {"type": "string"}
    },
    "required": ["teacher_marks", "description"],
    "additionalProperties": False
}

async def mask_image(src_path: str, dst_path: str, sem: asyncio.Semaphore, idx: int, total: int) -> Dict[str, Any]:
    # Skip if already masked and valid
    if os.path.exists(dst_path) and os.path.getsize(dst_path) > 1000:
        print(f"[{idx}/{total}] Already masked, skipping: {os.path.basename(dst_path)}")
        return {"src": src_path, "dst": dst_path, "status": "skipped"}

    async with sem:
        try:
            im = Image.open(src_path)
            if im.mode != "RGB":
                im = im.convert("RGB")
            w, h = im.size

            # Scaled copy for OpenAI API vision detection (max dim 1600)
            max_dim = 1600
            if max(w, h) > max_dim:
                scale = max_dim / max(w, h)
                preview = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            else:
                preview = im

            buf = io.BytesIO()
            preview.save(buf, format="JPEG", quality=85)
            preview_bytes = buf.getvalue()

            res = await request_structured_output([
                {"type": "input_text", "text": PROMPT_TEACHER_MARKS},
                _image_content(preview_bytes, "image/jpeg")
            ], SCHEMA_TEACHER_MARKS, "detect_teacher_marks")

            # Apply Whiteout/Masking on 100% Full Original Canvas
            im_masked = im.copy()
            draw = ImageDraw.Draw(im_masked)
            teacher_marks = res.get("teacher_marks", [])
            for box in teacher_marks:
                ymin, xmin, ymax, xmax = box
                ymin_c, ymax_c = min(ymin, ymax), max(ymin, ymax)
                xmin_c, xmax_c = min(xmin, xmax), max(xmin, xmax)
                x0 = max(0, int(xmin_c * w / 1000) - 8)
                y0 = max(0, int(ymin_c * h / 1000) - 8)
                x1 = min(w, int(xmax_c * w / 1000) + 8)
                y1 = min(h, int(ymax_c * h / 1000) + 8)
                draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            im_masked.save(dst_path, "JPEG", quality=95)
            print(f"[{idx}/{total}] Masked (100% Full Image): {os.path.basename(dst_path)} (Size: {w}x{h}, Marks: {len(teacher_marks)})")

            return {
                "src": src_path,
                "dst": dst_path,
                "status": "success",
                "marks_count": len(teacher_marks),
                "desc": res.get("description", "")
            }
        except Exception as e:
            print(f"[{idx}/{total}] ERROR masking {src_path}: {e}")
            return {"src": src_path, "dst": dst_path, "status": "error", "error": str(e)}

async def batch_mask_folder(src_folder: str, dst_folder: str, sem: asyncio.Semaphore):
    os.makedirs(dst_folder, exist_ok=True)
    valid_exts = ('.jpg', '.jpeg', '.png', '.heic')
    files = sorted([f for f in os.listdir(src_folder) if f.lower().endswith(valid_exts)])

    print(f"\n============================================================")
    print(f" Masking Folder: {src_folder} -> {dst_folder} ({len(files)} files)")
    print(f"============================================================")

    tasks = []
    for idx, f in enumerate(files, 1):
        src_p = os.path.join(src_folder, f)
        base_name = os.path.splitext(f)[0] + ".jpg"
        dst_p = os.path.join(dst_folder, base_name)
        tasks.append(mask_image(src_p, dst_p, sem, idx, len(files)))

    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r.get("status") in ["success", "skipped"])
    print(f"Completed {success_count}/{len(files)} in {dst_folder}")
    return results

async def main():
    concurrency = 4
    sem = asyncio.Semaphore(concurrency)

    # 1. Diagram Folders (Q4 BST, Q5 Array, Q6 Tree Conversion)
    diagram_folders = [
        ("photoชุดที่1", "photo_mask_ชุดที่1"),
        ("photoชุดที่2", "photo_mask_ชุดที่2"),
        ("photoชุดที่3", "photo_mask_ชุดที่3"),
    ]

    for src_name, dst_name in diagram_folders:
        src = os.path.join("ชุดข้อสอบใหม่", src_name)
        dst = os.path.join("ชุดข้อสอบใหม่", dst_name)
        if os.path.exists(src):
            await batch_mask_folder(src, dst, sem)
        else:
            print(f"Source folder not found: {src}")

    # 2. Text Handwriting Folders (Q1, Q2, Q3)
    text_folders = [
        ("โจทย์textชุดที่1", "photo_mask_text1"),
        ("โจทย์textชุดที่2", "photo_mask_text2"),
        ("โจทย์textชุดที่3", "photo_mask_text3"),
    ]

    for src_name, dst_name in text_folders:
        src = os.path.join("ชุดข้อสอบใหม่", src_name)
        dst = os.path.join("ชุดข้อสอบใหม่", dst_name)
        if os.path.exists(src):
            await batch_mask_folder(src, dst, sem)
        else:
            print(f"Source folder not found: {src}")

    print("\n============================================================")
    print(" ALL EXAM PHOTOS IN-PLACE MASKED WITH 100% CANVAS PRESERVED!")
    print("============================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
