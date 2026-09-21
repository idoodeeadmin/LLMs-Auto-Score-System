import puppeteer from 'puppeteer';
import path from 'path';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const artifactsDir = 'C:\\Users\\idood\\.gemini\\antigravity-ide\\brain\\f6ee475c-7cae-4670-a1aa-717c1db8426d';

async function test() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });
  
  // Student Join Form
  await page.goto('http://127.0.0.1:8090/', { waitUntil: 'networkidle0' });
  await page.evaluate(() => {
    localStorage.setItem('token', 'fixture-student');
    localStorage.setItem('user', JSON.stringify({ id: 101, name: 'นักศึกษาทดสอบ', role: 'student', email: 'student@example.test' }));
  });
  await page.goto('http://127.0.0.1:8090/home', { waitUntil: 'networkidle0' });
  await sleep(500);
  const buttons1 = await page.$$('button');
  for (const b of buttons1) {
    const txt = await page.evaluate(el => el.textContent, b);
    if (txt && txt.includes('เข้าร่วมห้องเรียน')) {
      await b.click();
      await sleep(500);
      await page.screenshot({ path: path.join(artifactsDir, 'audit_03_student_join_modal.png') });
      break;
    }
  }

  // Teacher Create Form
  await page.evaluate(() => {
    localStorage.setItem('token', 'fixture-teacher');
    localStorage.setItem('user', JSON.stringify({ id: 1, name: 'ผู้สอนทดสอบ', role: 'teacher', email: 'teacher@example.test' }));
  });
  await page.goto('http://127.0.0.1:8090/home', { waitUntil: 'networkidle0' });
  await sleep(500);
  const buttons2 = await page.$$('button');
  for (const b of buttons2) {
    const txt = await page.evaluate(el => el.textContent, b);
    if (txt && txt.includes('สร้างห้องเรียน')) {
      await b.click();
      await sleep(500);
      await page.screenshot({ path: path.join(artifactsDir, 'audit_10_teacher_create_room_modal.png') });
      break;
    }
  }

  await browser.close();
  console.log('Successfully captured forms!');
}

test();
