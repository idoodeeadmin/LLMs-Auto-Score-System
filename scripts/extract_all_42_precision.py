import os
import sys
import io
import base64
import json
import asyncio
from pathlib import Path
from PIL import Image
import httpx
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IMG_DIR = 'scratch/q1_all_42_cropped'
OUT_FILE = 'artifacts/q1_42_precision_extracted.json'

PROMPT = """นี่คือภาพถ่ายกรอบคำตอบข้อ 1 (หัวข้อ: '10. อธิบายความต่างของ Row-major vs Column-major') จากกระดาษคำตอบวิชา Data Structures

กรุณาตรวจสอบและถอดความอย่างละเอียดสูงสุด ตอบเป็น JSON:
{
  "has_drawing": true/false (true หากมีภาพวาด, ตาราง, เมทริกซ์, วาดช่องสี่เหลี่ยม, ตัวเลขเรียงแถวหลักเป็นตาราง, ลูกศรชี้ทิศทางตาราง หรือรูปไดอะแกรมใดๆ / false หากเป็นข้อความบรรยายหรือสูตรคณิตศาสตร์ล้วนไม่มีรูปวาดหรือตาราง),
  "drawing_details": "ระบุอย่างชัดเจนว่ามีภาพวาด/ตารางอะไรบ้าง หรือพิมพ์ 'ไม่มีรูปวาด/ตาราง'",
  "verbatim_student_answer": "ถอดข้อความลายมือที่นิสิตตอบในกรอบนี้ 'ทุกตัวอักษร' 'ทุกคำ' และ 'ทุกสูตร' อย่างครบถ้วนสมบูรณ์ 100% ห้ามตัดทอน ห้ามสรุปความเด็ดขาด",
  "teacher_score": ตัวเลขคะแนนที่อาจารย์ตรวจให้เฉพาะข้อนี้ (เช่น 2.0, 1.5, 1.0, 0.5, 0.0),
  "teacher_notes": "รอยปากกาตรวจของอาจารย์ เช่น ขีดถูก, เขียนแก้, หรือวงกลมตรงไหน"
}"""

sem = asyncio.Semaphore(3)

async def process_image(filename: str, client: httpx.AsyncClient):
    async with sem:
        path = os.path.join(IMG_DIR, filename)
        im = Image.open(path)
        im.thumbnail((1600, 1600))
        buf = io.BytesIO()
        im.save(buf, format='JPEG', quality=92)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                                "detail": "high"
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
                res = r.json()
                if 'choices' in res:
                    data = json.loads(res['choices'][0]['message']['content'])
                    data['filename'] = filename
                    return data
                err = res.get('error', {}).get('message', str(res))
                if 'Rate limit' in err or r.status_code == 429:
                    wait_sec = 5 * (attempt + 1)
                    print(f"[{filename} rate limit, waiting {wait_sec}s...]", flush=True)
                    await asyncio.sleep(wait_sec)
                    continue
                return {'filename': filename, 'error': err}
            except Exception as e:
                await asyncio.sleep(3.0)

        return {'filename': filename, 'error': 'Timeout/Failed after retries'}

async def main():
    os.makedirs('artifacts', exist_ok=True)
    results = {}
    
    if os.path.exists(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                for item in saved:
                    if 'error' not in item and 'verbatim_student_answer' in item:
                        results[item['filename']] = item
            print(f"Loaded {len(results)} existing valid extractions.")
        except:
            pass

    files = sorted([f for f in os.listdir(IMG_DIR) if f.endswith('.jpg') and not f.startswith('.')])
    to_process = [f for f in files if f not in results]
    print(f"Total files: {len(files)}, To process: {len(to_process)}")

    async with httpx.AsyncClient(timeout=90.0) as client:
        tasks = []
        for f in to_process:
            tasks.append(process_image(f, client))
        
        # Gather with chunking to print progress
        for i in range(0, len(tasks), 5):
            chunk = tasks[i:i+5]
            chunk_files = to_process[i:i+5]
            print(f"Processing chunk {i+1}..{min(i+5, len(tasks))} of {len(tasks)}: {chunk_files}...")
            chunk_res = await asyncio.gather(*chunk)
            for res in chunk_res:
                results[res['filename']] = res
            
            # Save progressively
            all_list = [results[f] for f in sorted(results.keys())]
            with open(OUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_list, f, ensure_ascii=False, indent=2)
            await asyncio.sleep(1.0)

    # Summary
    all_list = [results[f] for f in sorted(results.keys())]
    pure_text = [r for r in all_list if not r.get('has_drawing', False) and 'error' not in r]
    with_drawings = [r for r in all_list if r.get('has_drawing', False)]

    print("\n" + "="*70)
    print("EXTRACTION COMPLETE:")
    print(f"Total processed:             {len(all_list)}")
    print(f"Pure Text (NO drawings):     {len(pure_text)}")
    print(f"Has Drawings / Diagrams:     {len(with_drawings)}")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
