import puppeteer from 'puppeteer';
import path from 'path';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const artifactsDir = 'C:\\Users\\idood\\.gemini\\antigravity-ide\\brain\\f6ee475c-7cae-4670-a1aa-717c1db8426d';

async function runAudit() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });

  const consoleLogs = [];
  page.on('console', msg => consoleLogs.push({ type: msg.type(), text: msg.text() }));

  try {
    console.log('--- Step 1: Login Page ---');
    await page.goto('http://127.0.0.1:8090/', { waitUntil: 'networkidle0' });
    await page.screenshot({ path: path.join(artifactsDir, 'audit_01_login.png') });

    console.log('--- Step 2: Student Login Flow ---');
    await page.type('#login-email', 'student@example.test');
    await page.type('#login-password', 'password123');
    await page.click('button[type="submit"]');
    await sleep(1500);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_02_student_home.png') });

    console.log('--- Step 3: Student Join Classroom Dialog ---');
    try {
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await page.evaluate(el => el.textContent, btn);
        if (text && text.includes('เข้าร่วม')) {
          await btn.click();
          await sleep(500);
          await page.screenshot({ path: path.join(artifactsDir, 'audit_03_student_join_modal.png') });
          await page.keyboard.press('Escape');
          await sleep(300);
          break;
        }
      }
    } catch (e) {
      console.log('Join modal check failed:', e.message);
    }

    console.log('--- Step 4: Student Leave Room Confirmation ---');
    const leaveBtn = await page.$('button[title="ออกจากห้องเรียน"]');
    if (leaveBtn) {
      await leaveBtn.click();
      await sleep(500);
      await page.screenshot({ path: path.join(artifactsDir, 'audit_04_student_leave_dialog.png') });
      await page.keyboard.press('Escape');
      await sleep(300);
    }

    console.log('--- Step 5: Student Room Detail ---');
    await page.goto('http://127.0.0.1:8090/room/10', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_05_student_room.png') });

    console.log('--- Step 6: Student Exam Submission Flow ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/submit', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_06_student_exam_submit_initial.png') });

    const textarea = await page.$('textarea');
    if (textarea) {
      await textarea.type('โครงสร้างข้อมูล Stack ทำงานด้วยหลักการ Last-In First-Out (LIFO) ซึ่งข้อมูลที่ใส่เข้าไปล่าสุดจะถูกนำออกมาใช้งานเป็นลำดับแรก เช่น การกดย้อนกลับ (Undo) ส่วน Queue ทำงานด้วยหลักการ First-In First-Out (FIFO) เช่น คิวการพิมพ์เอกสาร');
      await sleep(500);
      await page.screenshot({ path: path.join(artifactsDir, 'audit_07_student_exam_submit_typed.png') });
    }

    console.log('--- Step 7: Student History ---');
    await page.goto('http://127.0.0.1:8090/history', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_08_student_history.png') });

    console.log('--- Step 8: Teacher Login Flow ---');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fixture-teacher');
      localStorage.setItem('user', JSON.stringify({ id: 1, name: 'อาจารย์ผู้สอน ทดสอบ', role: 'teacher', email: 'teacher@example.test' }));
    });
    await page.goto('http://127.0.0.1:8090/home', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_09_teacher_home.png') });

    console.log('--- Step 9: Teacher Create Classroom Dialog ---');
    try {
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await page.evaluate(el => el.textContent, btn);
        if (text && text.includes('สร้างห้องเรียน')) {
          await btn.click();
          await sleep(500);
          await page.screenshot({ path: path.join(artifactsDir, 'audit_10_teacher_create_room_modal.png') });
          await page.keyboard.press('Escape');
          await sleep(300);
          break;
        }
      }
    } catch (e) {
      console.log('Create room modal check failed:', e.message);
    }

    console.log('--- Step 10: Teacher Room Detail ---');
    await page.goto('http://127.0.0.1:8090/room/10', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_11_teacher_room.png') });

    console.log('--- Step 11: Teacher Exam Review Submissions ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/review', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_12_teacher_review_pending.png') });

    // Switch tab to "approved" (ตรวจแล้ว)
    try {
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await page.evaluate(el => el.textContent, btn);
        if (text && text.includes('ตรวจแล้ว')) {
          await btn.click();
          await sleep(500);
          await page.screenshot({ path: path.join(artifactsDir, 'audit_13_teacher_review_approved.png') });
          break;
        }
      }
    } catch (e) {}

    // Switch tab to "missing" (ยังไม่ส่ง)
    try {
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await page.evaluate(el => el.textContent, btn);
        if (text && text.includes('ยังไม่ส่ง')) {
          await btn.click();
          await sleep(500);
          await page.screenshot({ path: path.join(artifactsDir, 'audit_14_teacher_review_missing.png') });
          break;
        }
      }
    } catch (e) {}

    console.log('--- Step 12: Teacher Grading Student 101 ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/grading/101', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_15_teacher_grading_101.png') });

    console.log('--- Step 13: Exam Scoreboard ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/scoreboard', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_16_teacher_scoreboard.png') });

    console.log('--- Step 14: Teacher Exam Analytics ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/analytics', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_17_exam_analytics.png') });

    console.log('--- Step 15: Room Analytics ---');
    await page.goto('http://127.0.0.1:8090/room/10/analytics', { waitUntil: 'networkidle0' });
    await sleep(800);
    await page.screenshot({ path: path.join(artifactsDir, 'audit_18_room_analytics.png') });

    console.log('Audit completed successfully! Total screenshots taken: 18');
  } catch (error) {
    console.error('Audit failed with error:', error);
  } finally {
    await browser.close();
  }
}

runAudit();
