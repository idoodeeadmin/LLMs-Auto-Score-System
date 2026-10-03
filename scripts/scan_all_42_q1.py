# -*- coding: utf-8 -*-
import os
import sys
import io
import json
import base64
import asyncio
from pathlib import Path
from PIL import Image
import pillow_heif
import httpx
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
pillow_heif.register_heif_opener()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def image_to_base64_jpeg(path: str, max_size=800) -> str:
    im = Image.open(path)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    im.thumbnail((max_size, max_size))
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=65)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

async def analyze_file(filename: str, client: httpx.AsyncClient):
    p = os.path.join('ชุดข้อสอบเก่า/Textชุดที่1', filename)
    b64 = image_to_base64_jpeg(p)
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "นี่คือกระดาษคำตอบข้อสอบข้อ 1 (Row-major vs Column-major ใน Array 2 มิติ)\n"
                            "ตอบกลับเป็น JSON เท่านั้น รูปแบบ:\n"
                            "{\n"
                            '  "has_drawing": true/false (true ถ้ามีวาดรูป ตาราง เส้นตาราง เมทริกซ์ หรือตัวเลขเรียงเป็นบล็อกตาราง, false ถ้าเป็นข้อความบรรยายล้วนไม่มีตาราง),\n'
                            '  "answer_text": "ถอดข้อความลายมือที่นิสิตตอบในข้อ 1 ทั้งหมด",\n'
                            '  "teacher_score": ตัวเลขคะแนนเฉพาะข้อ 1 (เช่น 2.0, 1.0, 0.0),\n'
                            '  "brief_reason": "สรุปสั้นๆ ว่ามีรูปวาดหรือไม่ และตอบอะไร"\n'
                            "}"
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
        "response_format": {"type": "json_object"},
        "temperature": 0.0
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(5):
        try:
            r = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60.0)
            res_json = r.json()
            if 'choices' in res_json:
                content = res_json['choices'][0]['message']['content']
                parsed = json.loads(content)
                parsed['filename'] = filename
                return parsed
            err_msg = res_json.get('error', {}).get('message', str(res_json))
            if 'Rate limit' in err_msg or 'rate_limit' in err_msg or r.status_code == 429:
                wait_sec = 4 * (attempt + 1)
                print(f"[RateLimit, waiting {wait_sec}s...]", end=" ", flush=True)
                await asyncio.sleep(wait_sec)
                continue
            return {
                'filename': filename,
                'has_drawing': False,
                'answer_text': f'ERROR: {err_msg}',
                'teacher_score': None,
                'brief_reason': f'Error: {err_msg}'
            }
        except Exception as e:
            await asyncio.sleep(3.0)

    return {
        'filename': filename,
        'has_drawing': False,
        'answer_text': 'ERROR: Failed after 5 retries',
        'teacher_score': None,
        'brief_reason': 'Failed after 5 retries'
    }

async def main():
    out_path = Path('artifacts/q1_all_42_scan.json')
    existing = {}
    if out_path.exists():
        try:
            data = json.loads(out_path.read_text(encoding='utf-8'))
            for item in data:
                if 'ERROR' not in item.get('answer_text', ''):
                    existing[item['filename']] = item
        except:
            pass

    files = sorted(os.listdir('ชุดข้อสอบเก่า/Textชุดที่1'))
    print(f"Total files: {len(files)}, already valid: {len(existing)}")

    results = []
    async with httpx.AsyncClient() as client:
        for f in files:
            if f in existing:
                results.append(existing[f])
                print(f"Using cached: {f}")
            else:
                print(f"Scanning {f}...", end=" ", flush=True)
                res = await analyze_file(f, client)
                results.append(res)
                has_d = res.get('has_drawing', False)
                is_err = 'ERROR' in res.get('answer_text', '')
                status = "ERROR" if is_err else f"Done (Drawing={has_d})"
                print(status)
                await asyncio.sleep(1.5)

    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

    drawings = [r for r in results if r.get('has_drawing')]
    pure_text = [r for r in results if not r.get('has_drawing') and 'ERROR' not in r.get('answer_text', '')]

    print("\n" + "="*70)
    print("FINAL SCAN SUMMARY:")
    print(f"Total files:            {len(results)}")
    print(f"Pure Text (NO drawing): {len(pure_text)}")
    print(f"Has Drawing / Table:    {len(drawings)}")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
