import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('artifacts/q4-minimal-rubric-eval-20260922-192633/q4_minimal_results.json', encoding='utf-8'))
for sid in ['DS-103', 'DS-113', 'DS-116', 'DS-129']:
    entry = next(x for x in data['results'] if x['sample_id'] == sid)
    print('=' * 60)
    print(f"[{sid}] Human: {entry['human_score']} | AI: {entry['ai_score']}")
    print("Feedback:\n" + entry['feedback'])
    print("Transcription:\n" + entry['transcription'])
