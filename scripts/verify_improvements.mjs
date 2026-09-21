import puppeteer from 'puppeteer';
import path from 'path';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const artifactsDir = 'C:\\Users\\idood\\.gemini\\antigravity-ide\\brain\\f6ee475c-7cae-4670-a1aa-717c1db8426d';

async function verify() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  page.on('dialog', async dialog => {
    console.log('Browser Dialog appeared:', dialog.type(), dialog.message());
    await dialog.accept();
  });

  try {
    console.log('--- 1. Testing /login redirect ---');
    await page.goto('http://127.0.0.1:8090/login', { waitUntil: 'networkidle0' });
    console.log('Current URL after /login:', page.url());

    console.log('--- 2. Student Login ---');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fixture-student');
    });
    await sleep(500);

    console.log('--- 3. Student Room Detail (with Submission status badge) ---');
    await page.goto('http://127.0.0.1:8090/room/10', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'verify_01_student_room_detail.png') });

    console.log('--- 4. Exam Submit Autosave & Draft Guard ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/submit', { waitUntil: 'networkidle0' });
    await sleep(1000);
    const textarea = await page.$('textarea');
    if (textarea) {
      await textarea.type('Stack ทำงานแบบ LIFO เหมาะสำหรับ Undo/Redo ในโปรแกรม');
      await sleep(1000);
    }
    await page.screenshot({ path: path.join(artifactsDir, 'verify_02_exam_submit_draft.png') });

    // Click back button to trigger exit confirmation dialog
    const allButtons = await page.$$('button');
    for (const b of allButtons) {
      const text = await page.evaluate(el => el.textContent, b);
      if (text && text.includes('กลับห้องเรียน')) {
        await b.click();
        await sleep(600);
        await page.screenshot({ path: path.join(artifactsDir, 'verify_03_exam_submit_exit_alert.png') });
        await page.keyboard.press('Escape');
        await sleep(300);
        break;
      }
    }

    console.log('--- 5. Student History with Stats & Filter ---');
    await page.goto('http://127.0.0.1:8090/history', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'verify_04_student_history.png') });

    console.log('--- 6. Teacher Switch ---');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fixture-teacher');
    });
    await sleep(500);

    console.log('--- 7. Teacher Room Detail (Review Shortcut) ---');
    await page.goto('http://127.0.0.1:8090/room/10', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'verify_05_teacher_room_detail.png') });

    console.log('--- 8. Teacher Exam View (Quick Actions Sticky Column) ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'verify_06_exam_view_teacher_panel.png') });

    console.log('--- 9. Teacher Room Review (Sort Select & Clickable Rows) ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/review', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'verify_07_room_review_sort.png') });

    console.log('--- 10. Teacher Student Grading (Approve & Next Student Button) ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/grading/101', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await sleep(500);
    await page.screenshot({ path: path.join(artifactsDir, 'verify_08_student_grading_next_btn.png') });

    console.log('All verifications completed successfully!');
  } catch (err) {
    console.error('Verification error:', err);
  } finally {
    await browser.close();
  }
}

verify();
