"""Fresh Q1-only evaluation; no edits to source workbooks or prior benchmark caches."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))
import asyncio
import json
from datetime import datetime, timezone
from scripts.run_dataset_benchmark import load_dataset, EXAM_QUESTIONS, calculate_qwk, calculate_mae, calculate_confusion_matrix
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 1]
    assert len(items) == 34 and all(x['answer_type'] == 'text' for x in items)
    folder = ROOT / 'artifacts' / ('q1-evaluation-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    folder.mkdir(parents=True)
    report = {'question_no': 1, 'model': OPENAI_MODEL, 'prompt_version': PROMPT_VERSION,
              'started_at': datetime.now(timezone.utc).isoformat(), 'expected_count': len(items),
              'max_score': 2, 'results': [], 'failures': []}
    from scripts.benchmark_rubrics import load_proposed_rubric
    q = EXAM_QUESTIONS[1]
    if '--two-criteria' in sys.argv:
        rubrics = [
            {'name': 'Row-major', 'score': 1.0, 'description': 'อธิบาย Row-major ว่าเป็นการจัดเก็บข้อมูล ลำดับการเรียง หรือการหาตำแหน่ง address ตามแนวแถว (Row/แนวนอน/แกน X)'},
            {'name': 'Column-major', 'score': 1.0, 'description': 'อธิบาย Column-major ว่าเป็นการจัดเก็บข้อมูล ลำดับการเรียง หรือการหาตำแหน่ง address ตามแนวคอลัมน์ (Column/แนวตั้ง/แกน Y)'},
        ]
        score_step = 0.5
        report['rubric_source'] = 'user-provided-two-criteria'
    else:
        rubrics, score_step = load_proposed_rubric(1, q['max_score'], items[0]['question_content'])
    report['rubric_snapshot'] = rubrics
    report['score_step'] = score_step
    report['answer_key'] = q['answer_key']
    def save():
        (folder / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    sem = asyncio.Semaphore(3)
    async def grade(item):
        async with sem:
            result = await score_with_openai(question_text=item['question_content'], answer_text=item['student_answer'],
                max_score=q['max_score'], answer_key=q['answer_key'], rubrics=rubrics, score_step=score_step)
            # Provider fallback scores must never be treated as measured model scores.
            if 'answer_word_count' not in result.get('metrics', {}):
                report['failures'].append({'sample_id':item['sample_id'], 'reason':'provider_or_processing_failure'})
                save()
                print('FAILED',item['sample_id'],flush=True)
                return False
            report['results'].append({'sample_id':item['sample_id'],'row':item['row'],
                'answer':item['student_answer'],'human_score':item['human_score'], **result})
            save()
            print(item['sample_id'], 'human=',item['human_score'], 'AI=',result['score'],flush=True)
            return True
    print('OUTPUT',folder,flush=True)
    if not await grade(items[0]):
        raise SystemExit('First request failed; stopped before sending remaining samples.')
    await asyncio.gather(*(grade(item) for item in items[1:]))
    report['results'].sort(key=lambda x:x['row'])
    results = report['results']
    truth = [r['human_score'] for r in results]
    predicted = [r['score'] for r in results]
    report['summary'] = {'successful':len(results),'failed':len(report['failures']),
        'mae':calculate_mae(truth,predicted),'qwk_step_0_5':calculate_qwk(truth,predicted,step=0.5,max_score=2.0),
        'exact_count':sum(a==b for a,b in zip(truth,predicted)),
        'confusion_matrix':calculate_confusion_matrix(truth,predicted,[0,0.5,1,1.5,2])}
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    save()
    print(json.dumps(report['summary'],ensure_ascii=False),flush=True)

if __name__ == '__main__':
    asyncio.run(main())
