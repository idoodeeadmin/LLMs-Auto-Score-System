import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("artifacts/q5_first10_user_rubric_results.json", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    sid = item["sample_id"]
    h = item["human_score"]
    a = item["ai_score"]
    m = item["match"]
    fb = item["feedback"]
    tr = item["transcription"]
    print(f"=== {sid} | Human: {h} | AI: {a} | Match: {m} ===")
    print(f"Transcription: {tr}")
    print(f"Feedback: {fb}\n")
