"""Regression checks for the document gaps, using an isolated SQLite database.

The small adapter translates MySQL syntax for these tests. It does not validate
TiDB transaction locking or replace a live deployment/accuracy benchmark.
"""
import asyncio
import io
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image

from server.main import app
from server.utils import get_current_user, validate_upload_file
from server.exam_policy import count_answer_words, validate_answer_text
from server.routes import exam_routes, room_routes, system_routes, ai_routes
from server.services import openai_grading, notification_service


class Cursor:
    def __init__(self, connection):
        self.raw = connection.raw.cursor()
        self.connection = connection
    def execute(self, sql, args=()):
        sql = sql.replace(' FOR UPDATE', '').replace('%s', '?')
        sql = sql.replace('ON DUPLICATE KEY UPDATE answer_text=VALUES(answer_text), image_paths=VALUES(image_paths)',
                          'ON CONFLICT(submission_id, question_id) DO UPDATE SET answer_text=excluded.answer_text, image_paths=excluded.image_paths')
        self.connection.statements.append((sql, args))
        self.raw.execute(sql, args)
        return self
    def fetchone(self):
        row = self.raw.fetchone()
        return dict(row) if row is not None else None
    def fetchall(self):
        return [dict(row) for row in self.raw.fetchall()]
    @property
    def lastrowid(self): return self.raw.lastrowid
    @property
    def rowcount(self): return self.raw.rowcount


class Database:
    def __init__(self):
        self.raw = sqlite3.connect(':memory:', check_same_thread=False)
        self.raw.row_factory = sqlite3.Row
        self.raw.create_function('JSON_UNQUOTE', 1, lambda value: value)
        self.statements = []
        self.committed = False
    def cursor(self): return Cursor(self)
    def commit(self):
        self.raw.commit()
        self.committed = True
    def rollback(self): self.raw.rollback()
    def close(self): pass


@pytest.fixture
def db(monkeypatch):
    database = Database()
    database.raw.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, student_id TEXT);
        CREATE TABLE rooms (id INTEGER PRIMARY KEY, name TEXT, teacher_id INTEGER);
        CREATE TABLE enrollments (id INTEGER PRIMARY KEY, room_id INTEGER, user_id INTEGER);
        CREATE TABLE exams (id INTEGER PRIMARY KEY, room_id INTEGER, title TEXT, description TEXT, total_score REAL, start_date TEXT, end_date TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, is_randomized INTEGER DEFAULT 0);
        CREATE TABLE questions (id INTEGER PRIMARY KEY, exam_id INTEGER, text TEXT, score REAL, answer_key TEXT, rubrics TEXT, order_index INTEGER, image_paths TEXT);
        CREATE TABLE submissions (id INTEGER PRIMARY KEY, exam_id INTEGER, user_id INTEGER, status TEXT, total_score REAL DEFAULT 0, submitted_at TEXT, graded_by_ai INTEGER DEFAULT 0, UNIQUE(exam_id, user_id));
        CREATE TABLE submission_answers (id INTEGER PRIMARY KEY, submission_id INTEGER, question_id INTEGER, answer_text TEXT, ai_score REAL, ai_feedback TEXT, ai_confidence TEXT, teacher_score REAL, teacher_comment TEXT, image_paths TEXT, quality_metrics TEXT, UNIQUE(submission_id, question_id));
        CREATE TABLE notifications (id INTEGER PRIMARY KEY, user_id INTEGER, type TEXT, link TEXT, data TEXT);
        INSERT INTO users VALUES (101,'Student','student@example.test','001'), (102,'Other','other@example.test','002');
        INSERT INTO rooms VALUES (10,'Data Structures',1), (20,'Other Room',2);
        INSERT INTO enrollments VALUES (1,10,101), (2,20,102);
        INSERT INTO exams (id,room_id,title,total_score) VALUES (1,10,'Stack',5), (2,20,'Queue',5);
        INSERT INTO questions VALUES (11,1,'Explain Stack',5,'LIFO','[]',0,NULL), (22,2,'Explain Queue',5,'FIFO','[]',0,NULL);
    """)
    for module in (exam_routes, room_routes, system_routes, notification_service):
        monkeypatch.setattr(module, 'get_db_connection', lambda: database)
    monkeypatch.setattr(exam_routes, 'trigger_socket_notify', AsyncMock())
    monkeypatch.setattr(exam_routes, 'grading_queue', MagicMock(put=AsyncMock()))
    yield database
    database.raw.close()


def client_for(role='student', user_id=101):
    app.dependency_overrides[get_current_user] = lambda: {'id': user_id, 'role': role}
    return TestClient(app)


def seed_submission(db, status='ready', exam_id=1, user_id=101, question_id=11):
    db.raw.execute('INSERT INTO submissions VALUES (100,?,?,?,?,CURRENT_TIMESTAMP,1)', (exam_id, user_id, status, 4))
    db.raw.execute("INSERT INTO submission_answers (id,submission_id,question_id,answer_text,ai_score,ai_feedback,ai_confidence) VALUES (200,100,?,'LIFO',4,'Good','high')", (question_id,))
    db.commit()


@pytest.mark.parametrize('text,expected', [('hello world',2), ('Stack, Queue!',2), ('คำตอบ',1), ('',0), ('!!!',0)])
def test_word_count(text, expected):
    assert count_answer_words(text) == expected


@pytest.mark.parametrize('word', ['word', 'คำตอบ'])
def test_300_words_allowed_301_rejected(word):
    assert validate_answer_text(' '.join([word] * 300)) == 300
    with pytest.raises(HTTPException) as caught:
        validate_answer_text(' '.join([word] * 301))
    assert caught.value.status_code == 422


def test_word_count_endpoint_uses_same_segmentation(db):
    response = client_for().post('/api/ai/answer-word-count', json={'answers': {'11': 'คำตอบ Stack'}})
    assert response.json() == {'counts': {'11': count_answer_words('คำตอบ Stack')}, 'limit': 300}


@pytest.mark.parametrize('method,path,payload', [
    ('get','submissions/102',None), ('put','submissions/102/approve',{'teacher_scores': {'22': 5}}),
    ('post','bulk-approve',{'student_ids':[102]}), ('post','questions/22/rescore',{}),
    ('post','submissions/102/regrade',{}), ('get','submissions',None), ('get','export-csv',None),
])
def test_teacher_cannot_pair_own_room_with_foreign_exam(db, method, path, payload):
    client = client_for('teacher',1)
    response = client.request(method, f'/api/rooms/10/exams/2/{path}', **({'json':payload} if payload is not None else {}))
    assert response.status_code == 403
    assert not any(sql.startswith('UPDATE') for sql, _ in db.statements)


def test_nonmember_cannot_submit(db):
    response = client_for('student',102).post('/api/rooms/10/exams/1/submit-multipart', data={'answers':'[]'})
    assert response.status_code == 403
    assert db.raw.execute('SELECT COUNT(*) FROM submissions').fetchone()[0] == 0


def test_questions_hidden_before_start_and_direct_submit_rejected(db):
    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    db.raw.execute('UPDATE exams SET start_date = ? WHERE id=1',(future,)); db.commit()
    client = client_for()
    result = client.get('/api/rooms/10/exams/1').json()
    assert result['questions'] == [] and result['server_time']
    assert client.post('/api/rooms/10/exams/1/submit-multipart',data={'answers':'[]'}).status_code == 403


def test_expired_exam_rejected(db):
    db.raw.execute('UPDATE exams SET end_date=? WHERE id=1', ((datetime.now(timezone.utc)-timedelta(minutes=2)).isoformat(),)); db.commit()
    assert client_for().post('/api/rooms/10/exams/1/submit-multipart',data={'answers':'[]'}).status_code == 403


def test_submit_commits_before_queue_and_cannot_repeat(db, monkeypatch):
    async def enqueue(task):
        assert db.committed and task['user_id'] == 101
        assert db.raw.execute('SELECT status FROM submissions').fetchone()[0] == 'submitted'
    monkeypatch.setattr(exam_routes.grading_queue, 'put', AsyncMock(side_effect=enqueue))
    client = client_for()
    payload = {'answers':json.dumps([{'question_id':11,'answer_text':'word ' * 300}])}
    result = client.post('/api/rooms/10/exams/1/submit-multipart',data=payload)
    assert result.status_code == 200, result.text
    assert 'ai_score' not in result.json()
    assert client.post('/api/rooms/10/exams/1/submit-multipart',data=payload).status_code == 409
    exam_routes.grading_queue.put.assert_awaited_once()


@pytest.mark.parametrize('answers', [ [{'question_id':11,'answer_text':'word ' * 301}], [{'question_id':22,'answer_text':'outside'}], {'bad':'shape'} ])
def test_invalid_answers_do_not_create_submission(db, answers):
    response = client_for().post('/api/rooms/10/exams/1/submit-multipart',data={'answers':json.dumps(answers)})
    assert response.status_code == 422
    assert db.raw.execute('SELECT COUNT(*) FROM submissions').fetchone()[0] == 0
    exam_routes.grading_queue.put.assert_not_awaited()


def png_bytes():
    buf=io.BytesIO(); Image.new('RGB',(2,2),'white').save(buf,format='PNG'); return buf.getvalue()


def test_ten_images_retained_eleventh_rejected(db, monkeypatch):
    monkeypatch.setattr(exam_routes,'upload_to_cloudinary',lambda *a,**kw:'/uploads/test.png')
    files=[(f'image_11_{n}',(f'{n}.png',png_bytes(),'image/png')) for n in range(11)]
    client=client_for()
    assert client.post('/api/rooms/10/exams/1/submit-multipart',data={'answers':'[]'},files=files).status_code == 422
    assert db.raw.execute('SELECT COUNT(*) FROM submissions').fetchone()[0] == 0
    result=client.post('/api/rooms/10/exams/1/submit-multipart',data={'answers':'[]'},files=files[:10])
    assert result.status_code == 200, result.text
    assert len(json.loads(db.raw.execute('SELECT image_paths FROM submission_answers').fetchone()[0])) == 10


def test_fake_image_rejected():
    with pytest.raises(HTTPException): validate_upload_file(b'not an image',content_type='image/png')
    with pytest.raises(HTTPException): validate_upload_file(png_bytes(),content_type='image/jpeg')


@pytest.mark.parametrize('status', ['submitted','grading','ready','needs_review','approved'])
def test_history_and_own_result_hide_score_until_approved(db,status):
    seed_submission(db,status)
    client=client_for()
    history=client.get('/api/submissions/me').json()[0]
    own=client.get('/api/rooms/10/exams/1/submissions/me').json()
    if status == 'approved':
        assert history['submission_score'] == 4 and own['total_score'] == 4
    else:
        assert history['submission_score'] is None
        assert 'total_score' not in own and 'answers' not in own


def test_leave_changes_only_own_membership_and_blocks_exam(db):
    seed_submission(db)
    client=client_for()
    assert client.delete('/api/rooms/10/enrollment').status_code == 200
    assert db.raw.execute('SELECT COUNT(*) FROM rooms').fetchone()[0] == 2
    assert db.raw.execute('SELECT COUNT(*) FROM submissions').fetchone()[0] == 1
    assert db.raw.execute('SELECT COUNT(*) FROM enrollments WHERE user_id=102').fetchone()[0] == 1
    assert client.get('/api/rooms/10/exams/1').status_code == 403
    assert client.get('/api/rooms/10/exams/1/submissions/me').status_code == 403


def test_teacher_cannot_leave(db):
    assert client_for('teacher',1).delete('/api/rooms/10/enrollment').status_code == 403


@pytest.mark.parametrize('score', [-1,6,'bad'])
def test_teacher_score_bounds(db,score):
    seed_submission(db)
    response=client_for('teacher',1).put('/api/rooms/10/exams/1/submissions/101/approve',json={'teacher_scores':{'11':score}})
    assert response.status_code == 422
    assert db.raw.execute('SELECT status FROM submissions').fetchone()[0] == 'ready'


def test_approve_preserves_existing_teacher_score_when_only_comment_changes(db):
    seed_submission(db)
    db.raw.execute('UPDATE submission_answers SET teacher_score=5'); db.commit()
    response=client_for('teacher',1).put('/api/rooms/10/exams/1/submissions/101/approve',json={'teacher_comments':{'11':'Reviewed'}})
    assert response.status_code == 200, response.text
    assert response.json()['total_score'] == 5


def test_bulk_approval_skips_manual_review(db):
    seed_submission(db,'needs_review')
    result=client_for('teacher',1).post('/api/rooms/10/exams/1/bulk-approve',json={'student_ids':[101]}).json()
    assert result['approved_student_ids'] == [] and result['skipped']


def test_rescore_rejects_question_from_other_exam(db):
    assert client_for('teacher',1).post('/api/rooms/10/exams/1/questions/22/rescore').status_code == 404


def test_openai_rubric_failure_is_not_fake_success(monkeypatch):
    monkeypatch.setattr(ai_routes,'_get_openai_api_key',lambda:'test')
    monkeypatch.setattr(ai_routes,'generate_rubric_with_openai',AsyncMock(side_effect=ValueError('Bad total')))
    assert client_for('teacher',1).post('/api/ai/generate-rubric',json={'question_text':'Stack','total_score':5}).status_code == 502


def test_openai_rubric_total_checked(monkeypatch):
    monkeypatch.setattr(openai_grading,'request_structured_output',AsyncMock(return_value={'answer_key':'LIFO','rubrics':[{'name':'Accuracy','description':'LIFO','score':3}]}))
    with pytest.raises(ValueError): asyncio.run(openai_grading.generate_rubric_with_openai('Stack',5))


def test_rubric_routes_require_teacher_and_key(monkeypatch):
    client=client_for()
    assert client.post('/api/ai/generate-rubric',json={'question_text':'Stack','total_score':5}).status_code == 403
    client=client_for('teacher',1)
    monkeypatch.setattr(ai_routes,'_get_openai_api_key',lambda:None)
    assert client.post('/api/ai/generate-rubric',json={'question_text':'Stack','total_score':5}).status_code == 503


def test_transcribed_answer_over_limit_requires_review(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test')
    monkeypatch.setattr(openai_grading,'request_structured_output',AsyncMock(return_value={'score':5,'confidence':'high','feedback':'ok','transcription':'word ' * 301}))
    result=asyncio.run(openai_grading.score_with_openai('Stack','',5))
    assert result['confidence'] == 'low' and result['metrics']['word_limit_exceeded']


def test_incomplete_openai_result_falls_back(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test')
    monkeypatch.setattr(openai_grading,'request_structured_output',AsyncMock(side_effect=ValueError('incomplete')))
    result=asyncio.run(openai_grading.score_with_openai('Stack','LIFO',5))
    assert result['metrics']['manual_review_required'] and result['confidence'] == 'low'


def test_startup_recovers_user_id_and_grading_jobs(db,monkeypatch):
    from server import main
    seed_submission(db,'grading')
    monkeypatch.setattr(main,'init_db',lambda:None)
    monkeypatch.setattr(main,'get_db_connection',lambda:db)
    queue=MagicMock(put=AsyncMock()); monkeypatch.setattr(main,'grading_queue',queue)
    # Do not start perpetual background workers in this startup regression test.
    monkeypatch.setattr(main.asyncio,'create_task',lambda coroutine:coroutine.close())
    asyncio.run(main.startup_event())
    task=queue.put.await_args.args[0]
    assert task == {'submission_id':100,'room_id':10,'exam_id':1,'user_id':101}


def test_deadline_warning_skips_submitted_and_deduplicates(db,monkeypatch):
    now=datetime.now(timezone.utc)
    db.raw.execute('UPDATE exams SET end_date=? WHERE id=1',((now+timedelta(minutes=3)).isoformat(),)); db.commit()
    calls=[]
    async def notify(**kwargs):
        calls.append(kwargs)
        db.raw.execute('INSERT INTO notifications (user_id,type,link,data) VALUES (?,?,?,?)', (kwargs['user_id'],kwargs['notify_type'],kwargs['data']['link'],json.dumps(kwargs['data'])))
        db.commit()
    monkeypatch.setattr(notification_service,'trigger_socket_notify',notify)
    asyncio.run(notification_service.send_deadline_notifications(now))
    asyncio.run(notification_service.send_deadline_notifications(now))
    assert len(calls)==1 and calls[0]['notify_type']=='deadline_soon' and calls[0]['user_id']==101
    db.raw.execute('DELETE FROM notifications'); seed_submission(db,'submitted')
    asyncio.run(notification_service.send_deadline_notifications(now))
    assert len(calls)==1


@pytest.mark.parametrize('missing_image', [False, True])
def test_worker_reads_all_images_and_persists_transcription(db, monkeypatch, missing_image):
    from server.services import ai_service
    seed_submission(db, 'submitted')
    paths = [f'/uploads/{index}.png' for index in range(10)]
    db.raw.execute('UPDATE submission_answers SET image_paths=?', (json.dumps(paths),)); db.commit()
    monkeypatch.setattr(ai_service, 'get_db_connection', lambda: db)
    monkeypatch.setattr(ai_service, 'get_image_bytes', AsyncMock(return_value=None if missing_image else png_bytes()))
    score = AsyncMock(return_value={'score':4, 'feedback':'Good', 'confidence':'high', 'transcription':'LIFO', 'metrics':{'model':'fixture'}})
    monkeypatch.setattr(ai_service, 'score_with_openai', score)
    monkeypatch.setattr(ai_service, 'trigger_socket_notify', AsyncMock())
    async def run_one():
        queue=asyncio.Queue()
        monkeypatch.setattr(ai_service, 'grading_queue', queue)
        await queue.put({'submission_id':100,'room_id':10,'exam_id':1,'user_id':101})
        task=asyncio.create_task(ai_service.grading_worker())
        await asyncio.wait_for(queue.join(), 3)
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass
    asyncio.run(run_one())
    row=db.raw.execute('SELECT quality_metrics FROM submission_answers').fetchone()
    status=db.raw.execute('SELECT status FROM submissions').fetchone()[0]
    if missing_image:
        score.assert_not_awaited()
        assert status == 'needs_review' and json.loads(row[0])['manual_review_required']
    else:
        assert len(score.await_args.kwargs['image_bytes_list']) == 10
        assert json.loads(row[0])['transcription'] == 'LIFO' and status == 'ready'


def test_edit_keeps_existing_question_images(db,monkeypatch):
    db.raw.execute('UPDATE questions SET image_paths=? WHERE id=11', (json.dumps(['/uploads/questions/1/old.png']),)); db.commit()
    monkeypatch.setattr(exam_routes,'upload_to_cloudinary',MagicMock())
    result=client_for('teacher',1).put('/api/rooms/10/exams/1',json={'title':'Edited', 'questions':[{'text':'Stack','score':5,'question_images_base64':['/uploads/questions/1/old.png']}]})
    assert result.status_code == 200, result.text
    assert json.loads(db.raw.execute('SELECT image_paths FROM questions WHERE exam_id=1').fetchone()[0]) == ['/uploads/questions/1/old.png']
    exam_routes.upload_to_cloudinary.assert_not_called()


def test_bad_question_image_rolls_back_exam_creation(db):
    result=client_for('teacher',1).post('/api/rooms/10/exams',json={'title':'Invalid', 'questions':[{'text':'Stack','score':5,'question_images_base64':['data:image/png;base64,bm90LWltYWdl']}]})
    assert result.status_code == 400
    assert db.raw.execute('SELECT COUNT(*) FROM exams').fetchone()[0] == 2


def test_invalid_dates_and_negative_max_score_rejected(db):
    client=client_for('teacher',1)
    question={'text':'Stack','score':5}
    assert client.post('/api/rooms/10/exams',json={'title':'Test','start_date':'bad','questions':[question]}).status_code == 422
    assert client.post('/api/rooms/10/exams',json={'title':'Test','start_date':'2026-12-02','end_date':'2026-12-01','questions':[question]}).status_code == 422
    assert client.post('/api/rooms/10/exams',json={'title':'Test','questions':[{'text':'Stack','score':-1}]}).status_code == 422
