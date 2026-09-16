import asyncio, json, os, sys
from dotenv import load_dotenv
load_dotenv()
from server.utils import get_image_bytes
from server.services.ai_service import score_with_gemini

async def test():
    img_url = "https://res.cloudinary.com/dbwcivlsx/image/upload/v1786700475/submissions/330003/570003/imhcdechziniyy3kqw2f.jpg"
    print("Fetching image bytes from:", img_url)
    bts = await get_image_bytes(img_url)
    print("Image bytes size:", len(bts) if bts else None)
    
    res = await score_with_gemini(
        question_text="จงอธิบายความแตกต่างระหว่าง Row-major order vs Column-major order",
        answer_text="",
        max_score=2.0,
        answer_key="Row-major order คือการจัดเก็บเรียงตามแถว (Row by Row) ส่วน Column-major คือเรียงตามคอลัมน์ (Column by Column)",
        rubrics=[
            {"name": "อธิบายหลักการ Row-major และ Column-major", "score": 1.0, "description": "เก็บตามแถวและตามคอลัมน์"},
            {"name": "ระบุวิธีการเรียกและไล่ลำดับ Array", "score": 1.0, "description": "นับจากซ้ายไปขวา / บนลงล่าง"}
        ],
        image_bytes_list=[bts] if bts else None,
        image_mime_list=["image/jpeg"] if bts else None
    )
    print("Grading Result:", json.dumps(res, ensure_ascii=False, indent=2))

asyncio.run(test())
