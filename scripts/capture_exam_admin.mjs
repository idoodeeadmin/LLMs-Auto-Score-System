import puppeteer from 'puppeteer';
import path from 'path';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const artifactsDir = 'C:\\Users\\idood\\.gemini\\antigravity-ide\\brain\\f6ee475c-7cae-4670-a1aa-717c1db8426d';

async function test() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });

  await page.goto('http://127.0.0.1:8090/', { waitUntil: 'networkidle0' });
  await page.evaluate(() => {
    localStorage.setItem('token', 'fixture-teacher');
    localStorage.setItem('user', JSON.stringify({ id: 1, name: 'ผู้สอนทดสอบ', role: 'teacher', email: 'teacher@example.test' }));
  });

  // Create Exam Page
  await page.goto('http://127.0.0.1:8090/room/10/create-exam', { waitUntil: 'networkidle0' });
  await sleep(800);
  await page.screenshot({ path: path.join(artifactsDir, 'audit_19_create_exam.png') });

  // Edit Exam Page
  await page.goto('http://127.0.0.1:8090/room/10/exam/1/edit', { waitUntil: 'networkidle0' });
  await sleep(800);
  await page.screenshot({ path: path.join(artifactsDir, 'audit_20_edit_exam.png') });

  // Exam View Page
  await page.goto('http://127.0.0.1:8090/room/10/exam/1', { waitUntil: 'networkidle0' });
  await sleep(800);
  await page.screenshot({ path: path.join(artifactsDir, 'audit_21_exam_view.png') });

  await browser.close();
  console.log('Captured exam management pages!');
}

test();
