import asyncio, json, os
from dotenv import load_dotenv
load_dotenv()
from server.database import get_db_connection
from server.services.ai_service import score_with_gemini
from server.utils import get_image_bytes

async def regrade():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT sa.*, q.text as q_text, q.score as q_score, q.answer_key, q.rubrics as q_rubrics FROM submission_answers sa JOIN questions q ON sa.question_id = q.id WHERE sa.submission_id = 330004")
    answers = c.fetchall()
    for a in answers:
        img_paths = json.loads(a['image_paths']) if a['image_paths'] else []
        img_bytes = []
        img_mimes = []
        for p in img_paths:
            b = await get_image_bytes(p)
            if b:
                img_bytes.append(b)
                img_mimes.append('image/jpeg')
        rubrics = json.loads(a['q_rubrics']) if a['q_rubrics'] else []
        
        result = await score_with_gemini(
            question_text=a['q_text'],
            answer_text=a['answer_text'],
            max_score=float(a['q_score']),
            answer_key=a['answer_key'],
            rubrics=rubrics,
            image_bytes_list=img_bytes,
            image_mime_list=img_mimes
        )
        print("Updated Result:", result)
        c.execute("UPDATE submission_answers SET ai_score = ?, ai_feedback = ?, ai_confidence = ? WHERE id = ?", (result['score'], result['feedback'], result['confidence'], a['id']))
        c.execute("UPDATE submissions SET total_score = ?, status = 'needs_review' WHERE id = 330004", (result['score'],))
    conn.commit()
    conn.close()
    print("Regrading complete!")

asyncio.run(regrade())
