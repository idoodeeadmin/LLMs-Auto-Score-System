import sys, json, asyncio
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.append(str(ROOT / '.venv/Lib/site-packages'))
from dotenv import load_dotenv
load_dotenv()
from scripts.run_dataset_benchmark import load_dataset, calculate_mae, calculate_qwk
from server.services.openai_grading import request_structured_output, OPENAI_MODEL, PROMPT_VERSION
RUBRIC = "คะแนนเต็ม 2.0 คะแนน: 1.5 คะแนน อธิบายอย่างไรก็ได้ให้เห็นว่า O(n log n) เหมาะกว่า O(n^2) ในภาพรวม; 0.5 คะแนน ยกตัวอย่าง Algorithm ที่เกี่ยวข้องได้ถูกต้อง; หากมีส่วนที่ผิดให้หักครั้งละ 0.5; หากผิดร้ายแรงให้หัก 1; ไม่อธิบายเลยให้ 0 ทันที; ให้คะแนนเฉพาะ 2.0, 1.5, 1.0, 0.5, 0.0"
SCHEMA={"type":"object","additionalProperties":False,"properties":{"score":{"type":"number","minimum":0,"maximum":2},"confidence":{"type":"string","enum":["high","medium","low"]},"feedback":{"type":"string"}},"required":["score","confidence","feedback"]}
async def main():
    items=[x for x in load_dataset() if x["question_no"]==2][:10]
    folder=ROOT/"artifacts"/("q2-direct-fields-"+datetime.now().strftime("%Y%m%d-%H%M%S")); folder.mkdir(parents=True)
    results=[]; sem=asyncio.Semaphore(4)
    async def grade(item):
        async with sem:
            prompt=f"โจทย์:\n{item['question_content']}\n\nคำตอบนักเรียน:\n{item['student_answer']}\n\nเกณฑ์การให้คะแนน:\n{RUBRIC}\n\nประเมินตามเกณฑ์เท่านั้น โดยมองเจตนาและใจความ ไม่เน้นศัพท์วิชาการ ตอบ JSON เท่านั้น"
            try:
                res=await request_structured_output([{"type":"input_text","text":prompt}],SCHEMA,"direct_exam_score",max_output_tokens=1200); score=round(float(res["score"]),2)
                entry={"sample_id":item["sample_id"],"row":item["row"],"human_score":item["human_score"],"ai_score":score,"exact":score==item["human_score"],"confidence":res["confidence"],"feedback":res["feedback"]}
            except Exception as e: entry={"sample_id":item["sample_id"],"row":item["row"],"human_score":item["human_score"],"ai_score":0.0,"exact":False,"error":type(e).__name__}
            results.append(entry); print(entry["sample_id"],"human=",entry["human_score"],"AI=",entry["ai_score"],flush=True)
    await asyncio.gather(*(grade(x) for x in items)); results.sort(key=lambda x:x["row"])
    truth=[x["human_score"] for x in results]; pred=[x["ai_score"] for x in results]
    summary={"total":len(results),"exact_count":sum(x["exact"] for x in results),"exact_pct":100*sum(x["exact"] for x in results)/len(results),"mae":calculate_mae(truth,pred),"qwk":calculate_qwk(truth,pred,step=.5,max_score=2)}
    out={"timestamp":datetime.now(timezone.utc).isoformat(),"model":OPENAI_MODEL,"prompt_version":PROMPT_VERSION,"mode":"direct fields only","rubric":RUBRIC,"summary":summary,"results":results}
    (folder/"results.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__": asyncio.run(main())
