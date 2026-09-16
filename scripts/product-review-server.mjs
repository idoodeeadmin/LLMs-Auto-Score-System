// Isolated, local-only UX fixture server. No database, credentials or external APIs.
// Build first, then run: node scripts/product-review-server.mjs
// Log in with teacher@example.test or student@example.test and any dummy password.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const root = path.resolve('dist/spa');
const now = Date.now();
const user = role => ({ id: role === 'teacher' ? 1 : 101, name: role === 'teacher' ? 'ผู้สอนทดสอบ' : 'นักศึกษาทดสอบ', email: `${role}@example.test`, role, is_verified: 1 });
const room = { id: 10, name: 'โครงสร้างข้อมูลและอัลกอริทึม', section: 'CS201 • กลุ่ม 1', class_code: 'CS201A', student_count: 6, teacher_id: 1 };
const exam = { id: 1, room_id: 10, title: 'แบบทดสอบ Stack และ Queue', description: 'อธิบายแนวคิดและยกตัวอย่างการใช้งาน ตอบเป็นข้อความหรือแนบภาพคำตอบ', total_score: 10, created_at: new Date(now - 86400000).toISOString(), start_date: new Date(now - 3600000).toISOString(), end_date: new Date(now + 3600000).toISOString(), questions: [{ id: 11, text: 'อธิบายความแตกต่างระหว่าง Stack และ Queue พร้อมยกตัวอย่างการใช้งาน', score: 10, order_index: 0, answer_key: 'Stack ใช้ LIFO ส่วน Queue ใช้ FIFO', image_paths: [], rubrics: [{ name: 'ความถูกต้อง', description: 'อธิบาย LIFO และ FIFO ได้ถูกต้อง', score: 6 }, { name: 'ตัวอย่าง', description: 'ยกตัวอย่างการใช้งานที่เหมาะสม', score: 4 }] }] };
const statuses = ['ready', 'needs_review', 'grading', 'submitted', 'approved', 'missing'];
const students = statuses.map((status, i) => ({ student_id: 101 + i, name: ['กานต์ ตัวอย่าง', 'ณัฐ ตัวอย่างชื่อยาวเพื่อทดสอบการจัดวาง', 'พิชญา ตัวอย่าง', 'ธนา ตัวอย่าง', 'มินตรา ตัวอย่าง', 'วิชญ์ ตัวอย่าง'][i], email: `student${i}@example.test`, student_code: `660100${i}`, submission_id: status === 'missing' ? null : i + 1, status, total_score: status === 'ready' ? 8 : status === 'approved' ? 9 : null, submitted_at: exam.created_at }));
const history = students.filter(s => s.status !== 'missing').map((s, i) => ({ id: i + 1, exam_id: i + 1, room_id: 10, room_name: room.name, exam_title: `${exam.title} (${i + 1})`, title: exam.title, status: s.status, total_score: s.status === 'approved' ? 9 : null, exam_total_score: 10, submission_score: s.status === 'approved' ? 9 : null, submitted_at: exam.created_at }));
const types = { '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.svg': 'image/svg+xml', '.html': 'text/html' };
createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://127.0.0.1:8090');
    const p = url.pathname;
    if (p.startsWith('/api/')) {
      let raw = ''; for await (const chunk of req) raw += chunk;
      const data = raw ? JSON.parse(raw) : {};
      const role = req.headers.authorization?.includes('student') ? 'student' : 'teacher';
      let body, status = 200;
      if (p === '/api/auth/login') { const r = data.email?.startsWith('student') ? 'student' : 'teacher'; body = { access_token: `fixture-${r}`, user: user(r) }; }
      else if (p === '/api/auth/me') body = user(role);
      else if (p === '/api/auth/socket-token') { status = 503; body = { detail: 'Socket disabled in isolated preview' }; }
      else if (p === '/api/notifications') body = [];
      else if (p === '/api/rooms') body = [room];
      else if (p === '/api/rooms/10') body = room;
      else if (p.endsWith('/announcements')) body = [{ id: 1, title: 'คำชี้แจงก่อนทำแบบทดสอบ', content: 'ตรวจสอบคำตอบก่อนส่ง หากแนบภาพให้ถ่ายตัวหนังสือให้ชัดเจน', created_at: exam.created_at, is_read: 1, read_count: 3 }];
      else if (p === '/api/submissions/me') body = history;
      else if (p.endsWith('/bulk-approve')) { const approved = students.filter(s => data.student_ids?.includes(s.student_id) && s.status === 'ready'); body = { approved_student_ids: approved.map(s => s.student_id), skipped: data.student_ids?.filter(id => !approved.some(s => s.student_id === id)) }; approved.forEach(s => s.status = 'approved'); }
      else if (p.endsWith('/submissions/me')) body = { status: 'missing' };
      else if (/\/submissions\/\d+$/.test(p)) { const s = students.find(s => s.student_id === Number(p.split('/').pop())); body = { submission: s, student: { id: s.student_id, name: s.name }, answers: [{ id: 1, question_id: 11, question_text: exam.questions[0].text, max_score: 10, answer_text: 'Stack ทำงานแบบ LIFO ส่วน Queue เป็น FIFO', ai_score: 8, ai_feedback: 'อธิบายหลักการถูกต้อง แต่ยังขาดตัวอย่างของ Queue', ai_confidence: s.status === 'needs_review' ? 'low' : 'high', quality_metrics: { transcription: 'Stack ทำงานแบบ LIFO ส่วน Queue เป็น FIFO' }, rubrics: exam.questions[0].rubrics }] }; }
      else if (p.endsWith('/submissions')) body = students;
      else if (p.endsWith('/exams/1')) body = { ...exam, server_time: new Date().toISOString(), submission_deadline: new Date(now + 3660000).toISOString() };
      else if (p.endsWith('/exams')) body = [exam];
      else if (p === '/api/ai/answer-word-count') body = { counts: Object.fromEntries(Object.entries(data.answers).map(([k, v]) => [k, v.trim().split(/\s+/).filter(Boolean).length])), limit: 300 };
      else { status = 501; body = { detail: 'This operation is not provided by the isolated review fixture.' }; }
      res.writeHead(status, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(body)); return;
    }
    let file = path.resolve(root, `.${decodeURIComponent(p)}`);
    if (!file.startsWith(root + path.sep)) file = path.join(root, 'index.html');
    let bytes;
    try { bytes = await readFile(file); } catch { file = path.join(root, 'index.html'); bytes = await readFile(file); }
    if (file.endsWith('index.html')) bytes = Buffer.from(bytes.toString().replace('<title>', '<title>[ข้อมูลจำลอง] '));
    res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream'); res.end(bytes);
  } catch { res.writeHead(500); res.end('Fixture error'); }
}).listen(8090, '127.0.0.1', () => console.log('Isolated product review: http://127.0.0.1:8090 — teacher@example.test / student@example.test; any dummy password.'));
