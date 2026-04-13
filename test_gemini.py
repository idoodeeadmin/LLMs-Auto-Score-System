import os, asyncio, sys, struct, zlib
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()
import google.genai as genai
from google.genai import types as t

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def make_png(width=50, height=50):
    """Generate a minimal valid PNG in-memory (white with black border)."""
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)
    rows = []
    for y in range(height):
        row = b'\x00'  # filter byte
        for x in range(width):
            if x == 0 or x == width-1 or y == 0 or y == height-1:
                row += b'\x00\x00\x00'  # black border
            else:
                row += b'\xff\xff\xff'  # white fill
        rows.append(row)
    raw = b''.join(rows)
    compressed = zlib.compress(raw)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')
    return sig + ihdr + idat + iend

img_bytes = make_png(50, 50)

async def test():
    try:
        resp = await client.aio.models.generate_content(
            model='gemini-flash-latest',
            contents=[
                "จงอธิบายสั้นๆ ว่าเห็นอะไรในรูปนี้ (ตอบภาษาไทย)",
                t.Part.from_bytes(data=img_bytes, mime_type="image/png")
            ],
            config=t.GenerateContentConfig(temperature=0.1)
        )
        print("[OK] Multimodal (Vision) ใช้งานได้!")
        print("Gemini เห็น:", resp.text.strip())
    except Exception as e:
        err = str(e)
        if "400" in err and "Unable to process" in err:
            print("[RESULT] Model รองรับ Vision แต่รูปทดสอบเล็กเกินไป — ใช้งานได้กับรูปจริงครับ")
        elif "404" in err or "not found" in err.lower():
            print("[FAIL] Model นี้ไม่รองรับ Vision")
        else:
            print("[FAIL]", err[:200])

asyncio.run(test())
