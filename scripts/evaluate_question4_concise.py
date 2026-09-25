"""Evaluate the user-approved concise Q4 rubric with the existing API service."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / '.venv/Lib/site-packages'))
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from scripts.run_dataset_benchmark import load_dataset, EXAM_QUESTIONS, calculate_mae, calculate_qwk
from scripts.test_grade_q4_all import load_upright_image_bytes
from server.services.openai_grading import score_with_openai, OPENAI_MODEL, PROMPT_VERSION

RUBRICS = [{
    'name': 'ความถูกต้องของโครงสร้าง Binary Search Tree', 'score': 1.0,
    'description': (
        '1.00 คะแนน: สร้าง Binary Search Tree จากข้อมูลที่กำหนดได้ครบถ้วนและถูกต้อง\n'
        '0.50 คะแนน: สร้างต้นไม้ได้ถูกต้องเป็นส่วนใหญ่ แต่สลับตำแหน่งโหนดหรือค่าข้อมูล 1 จุด\n'
        '0.25 คะแนน: แสดงความเข้าใจในการสร้างต้นไม้ได้บางส่วน แต่คำตอบยังไม่ครบหรือมีตำแหน่งผิดหลายจุด\n'
        '0.00 คะแนน: ไม่แสดงความเข้าใจหลักการสร้าง Binary Search Tree หรือไม่ตอบ'
    )
}]

DEDUCTION_RUBRICS = [{
    'name': 'การสร้าง Binary Search Tree', 'score': 1.0,
    'description': (
        'สร้างต้นไม้จากข้อมูลที่กำหนดได้ครบถ้วนและถูกต้อง ให้ 1 คะแนน '
        'หากผิดเล็กน้อย แต่ยังแสดงความเข้าใจหลักการ BST ให้หักจุดละ 0.25 คะแนน '
        'โดยไม่หักซ้ำจากข้อผิดพลาดเดียวกัน คะแนนต่ำสุดคือ 0 '
        'หากวางโหนดโดยไม่เป็นไปตามหลัก BST จนไม่แสดงความเข้าใจ หรือไม่ตอบ ให้ 0 คะแนนทันที'
    )
}]

TRIMMED_RUBRICS = [{
    'name': 'ความถูกต้องของโครงสร้าง Binary Search Tree (BST)', 'score': 1.0,
    'description': (
        '1.00 คะแนน: วาด BST ถูกต้องครบ 12 โหนดตามลำดับข้อมูล โดยซ้าย < โหนดแม่ < ขวา '
        'ราก 9 มีลูกซ้าย 5 และขวา 16; 16 มีลูกซ้าย 10 และขวา 76; '
        '10 มีลูกขวา 13; 13 มีลูกซ้าย 11 และขวา 15; '
        '76 มีลูกซ้าย 58 และขวา 92; 92 มีลูกซ้าย 80 และขวา 99 '
        'ยอมรับโครงร่างต้นไม้หรือวงกลมว่างประกอบ หากโหนดข้อมูลเชื่อมถูกต้อง\n'
        '0.50 คะแนน: โครงสร้างส่วนใหญ่ถูกต้อง แต่สลับฝั่งโหนด 1 จุด หรือสลับค่าข้อมูล 1 คู่\n'
        '0.25 คะแนน: ถูกบางส่วน แต่วาดไม่เสร็จ มีช่องโหนดที่ยังไม่เติมค่า หรือวางผิดหลายจุด\n'
        '0.00 คะแนน: ผิดหลัก BST ร้ายแรง เช่น 10 อยู่กิ่งซ้ายของ 9, '
        'มีลูกเกิน 2 กิ่ง, โหนดข้อมูลขาดหาย เช่น ขาด 10, '
        'ต่อโหนดผิดจนไม่เป็นโครงสร้างตามโจทย์ หรือไม่ตอบ\n'
        'ให้คะแนนเฉพาะ 1.00, 0.50, 0.25 หรือ 0.00'
    )
}]

NO_KEY_RUBRICS = [{
    'name': 'การสร้าง Binary Search Tree จากลำดับข้อมูลในโจทย์', 'score': 1.0,
    'description': (
        'ให้สร้างต้นไม้โดยแทรกข้อมูลทีละค่าตามลำดับที่โจทย์กำหนด ตรวจทั้งจำนวนโหนด '
        'ความสัมพันธ์พ่อ-ลูก และเงื่อนไขที่ค่าทุกตัวในกิ่งซ้ายต่ำกว่าโหนดแม่ '
        'ค่าทุกตัวในกิ่งขวาสูงกว่าโหนดแม่ โดยพิจารณาตลอดเส้นทางจากราก ไม่ใช่แค่โหนดที่ติดกัน '
        'ไม่นับวงกลมหรือเส้นร่างที่ยังไม่ใส่ค่าเป็นโหนดคำตอบ\n'
        '1.00 คะแนน: แทรกข้อมูลครบทุกค่าและวางโหนดถูกตำแหน่งทั้งหมด\n'
        '0.50 คะแนน: โครงสร้างหลักถูกต้อง แต่เชื่อมผิดหรือสลับค่าข้อมูลเพียงหนึ่งจุด\n'
        '0.25 คะแนน: เห็นหลักการบางส่วน แต่ต้นไม้ไม่ครบหรือมีตำแหน่งผิดหลายจุด\n'
        '0.00 คะแนน: ไม่เป็น BST จากข้อมูลที่โจทย์กำหนดอย่างมีสาระสำคัญ หรือไม่ตอบ\n'
        'ให้คะแนนเฉพาะ 1.00, 0.50, 0.25 หรือ 0.00'
    )
}]

async def main():
    items = [x for x in load_dataset() if x['question_no'] == 4]
    assert len(items) == 34 and all(x['answer_type'] == 'img' for x in items)
    q = EXAM_QUESTIONS[4]
    deduction = '--deduct-quarter' in sys.argv
    rubrics = DEDUCTION_RUBRICS if deduction else RUBRICS
    levels = (0,.25,.5,.75,1) if deduction else (0,.25,.5,1)
    prefix = 'q4-deduction-evaluation-' if deduction else 'q4-concise-evaluation-'
    if '--trim-original' in sys.argv:
        rubrics = TRIMMED_RUBRICS
        levels = (0,.25,.5,1)
        prefix = 'q4-trimmed-original-evaluation-'
    no_answer_key = '--no-answer-key' in sys.argv
    if no_answer_key:
        rubrics = NO_KEY_RUBRICS
        levels = (0,.25,.5,1)
        prefix = 'q4-no-answer-key-evaluation-'
    folder = ROOT / 'artifacts' / (prefix + datetime.now().strftime('%Y%m%d-%H%M%S'))
    folder.mkdir(parents=True)
    report = {
        'question_no': 4, 'model': OPENAI_MODEL, 'prompt_version': PROMPT_VERSION,
        'provider_sha256': hashlib.sha256((ROOT/'server/services/openai_grading.py').read_bytes()).hexdigest(),
        'rubric_snapshot': rubrics, 'answer_key': None if no_answer_key else q['answer_key'], 'max_score': 1,
        'image_processing': 'Same load_upright_image_bytes as test_grade_q4_all.py',
        'started_at': datetime.now(timezone.utc).isoformat(), 'results': [], 'failures': []
    }
    def save():
        (folder/'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    sem = asyncio.Semaphore(3)
    async def grade(item):
        async with sem:
            try:
                img = load_upright_image_bytes(item['student_img_path'])
                result = await score_with_openai(
                    question_text=q['question_text'], answer_text='', max_score=1.0,
                    answer_key=None if no_answer_key else q['answer_key'], rubrics=rubrics,
                    image_bytes_list=[img], image_mime_list=['image/jpeg'])
                if 'answer_word_count' not in result.get('metrics', {}):
                    raise RuntimeError('Provider returned fallback instead of a measured result')
                report['results'].append({
                    'sample_id': item['sample_id'], 'row': item['row'],
                    'image_path': item['student_img_path'], 'sent_image_sha256': hashlib.sha256(img).hexdigest(),
                    'human_score': item['human_score'], **result})
                print(item['sample_id'], 'human=', item['human_score'], 'AI=', result['score'], flush=True)
                save()
                return True
            except Exception as exc:
                report['failures'].append({'sample_id': item['sample_id'], 'error_type': type(exc).__name__})
                save()
                print('FAILED', item['sample_id'], type(exc).__name__, flush=True)
                return False
    print('OUTPUT', folder, flush=True)
    if not await grade(items[0]):
        raise SystemExit('First request failed; remaining requests not sent.')
    await asyncio.gather(*(grade(x) for x in items[1:]))
    report['results'].sort(key=lambda x: x['row'])
    truth = [x['human_score'] for x in report['results']]
    predicted = [x['score'] for x in report['results']]
    report['summary'] = {
        'successful': len(truth), 'failed': len(report['failures']),
        'exact_count': sum(h == p for h,p in zip(truth,predicted)),
        'exact_pct': 100*sum(h == p for h,p in zip(truth,predicted))/len(truth),
        'mae': calculate_mae(truth,predicted),
        'qwk_step_0_25': calculate_qwk(truth,predicted,step=0.25,max_score=1.0),
        'outside_rubric_levels': [x['sample_id'] for x in report['results'] if x['score'] not in levels]
    }
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    save()
    print(json.dumps(report['summary'], ensure_ascii=False), flush=True)

if __name__ == '__main__':
    asyncio.run(main())
