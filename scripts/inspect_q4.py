import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))

from scripts.run_dataset_benchmark import load_dataset, EXAM_QUESTIONS

def main():
    q = EXAM_QUESTIONS[4]
    items = [x for x in load_dataset() if x['question_no'] == 4]
    
    print("=" * 80)
    print(f"QUESTION 4: {q['topic']} (Max Score: {q['max_score']})")
    print("=" * 80)
    print("Question Text:")
    print(q['question_text'])
    print("-" * 80)
    print("Answer Key:")
    print(q['answer_key'])
    print("-" * 80)
    print(f"Total Students: {len(items)}")
    print(f"Answer Types: {set(x['answer_type'] for x in items)}")
    print(f"Score Distribution: {Counter(x['human_score'] for x in items)}")
    print("=" * 80)
    
    print("\nALL 34 STUDENT SAMPLES IN QUESTION 4:")
    for it in items:
        print(f"[{it['sample_id']}] Row: {it['row']:3d} | Type: {it['answer_type']:4s} | Human: {it['human_score']:.2f} | Ans: {repr(it['student_answer'])}")
        
if __name__ == '__main__':
    main()
