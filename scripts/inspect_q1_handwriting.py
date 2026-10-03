# -*- coding: utf-8 -*-
import os
import sys
import io
import base64
import asyncio
from PIL import Image
import pillow_heif
import httpx
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
pillow_heif.register_heif_opener()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def image_to_base64_jpeg(path: str, max_size=1600) -> str:
    im = Image.open(path)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    im.thumbnail((max_size, max_size))
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=85)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

async def transcribe_image(path: str):
    b64 = image_to_base64_jpeg(path)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "นี่คือกระดาษคำตอบข้อสอบข้อ 1 (เรื่อง Row-major vs Column-major ใน Array 2 มิติ)\n"
                            "กรุณาตรวจสอบและสรุป:\n"
                            "1. ข้อความลายมือที่นิสิตตอบในข้อ 1 ทั้งหมด (ถอดความอย่างละเอียดตรงตามที่เขียน)\n"
                            "2. ลักษณะคำตอบ: เป็นการเขียนบรรยายล้วน (Pure Text) หรือมีวาดรูป/ตาราง/เมทริกซ์\n"
                            "3. คะแนนที่อาจารย์เขียนให้ในข้อ 1 นี้ (ดูรอยปากกาแดงเฉพาะข้อ 1 เช่น 2, 1, 0, /2 หรือดูรวม)"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.0
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        res = r.json()
        return res['choices'][0]['message']['content']

async def main():
    unused_files = [
        'IMG_2829.HEIC', 'IMG_2830.HEIC', 'IMG_2831.HEIC', 'IMG_2832.HEIC',
        'IMG_2833.HEIC', 'IMG_2834.HEIC', 'IMG_2835.HEIC', 'IMG_2839.HEIC'
    ]
    for f in unused_files:
        p = os.path.join('ชุดข้อสอบเก่า/Textชุดที่1', f)
        if not os.path.exists(p):
            print(f"File not found: {p}")
            continue
        print(f"\n==========================================")
        print(f"Inspecting {f}...")
        print(f"==========================================")
        text = await transcribe_image(p)
        print(text)

if __name__ == '__main__':
    asyncio.run(main())
