import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const outDir = path.join(rootDir, 'docs_and_tests', 'screenshots', 'manual_raw');

if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

// Tokens generated from server auth
const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJpZCI6MSwicm9sZSI6InRlYWNoZXIiLCJleHAiOjE3OTE0NzA0NTJ9.TakALaVVZodWpV6fM87kJugPnYXJiOIoDeo2iGCZ_L8';
const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsImlkIjoyLCJyb2xlIjoic3R1ZGVudCIsImV4cCI6MTc5MTQ3MDQ2OH0.nPZ2WH0zkwE3vgkKl4uUFeIh6Ch9qgQ5IuYi9U4PXYM';

async function run() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,850'],
    defaultViewport: { width: 1280, height: 850, deviceScaleFactor: 2 }
  });

  const page = await browser.newPage();

  // Helper to capture
  async function capture(url, filename, token = null, waitForSelector = null) {
    console.log(`Navigating to ${url}...`);
    await page.goto('http://localhost:8080/', { waitUntil: 'domcontentloaded' });
    
    if (token) {
      await page.evaluate((t) => {
        localStorage.setItem('token', t);
      }, token);
    } else {
      await page.evaluate(() => {
        localStorage.removeItem('token');
      });
    }

    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 }).catch(e => console.log('Navigation timeout, continuing...'));
    if (waitForSelector) {
      await page.waitForSelector(waitForSelector, { timeout: 10000 }).catch(() => console.log(`Selector ${waitForSelector} not found`));
    }
    await new Promise(r => setTimeout(r, 1200));

    const outPath = path.join(outDir, filename);
    await page.screenshot({ path: outPath, fullPage: false });
    console.log(`Saved ${filename} (${fs.statSync(outPath).size} bytes)`);
  }

  try {
    // 1. Login
    await capture('http://localhost:8080/', 'step1_login.png', null);
    
    // 2. Register
    await capture('http://localhost:8080/register', 'step2_register.png', null);

    // 3. Forgot Password
    await capture('http://localhost:8080/forgot-password', 'step3_forgot_pw.png', null);

    // 4. Teacher Home Dashboard
    await capture('http://localhost:8080/home', 'step4_teacher_dashboard.png', teacherToken);

    // 5. User Profile
    await capture('http://localhost:8080/profile', 'step5_profile.png', teacherToken);

    // 6. Room Detail (Stream / Announcements)
    await capture('http://localhost:8080/room/30001', 'step6_room_detail.png', teacherToken);

    // 7. Create Exam
    await capture('http://localhost:8080/room/30001/create-exam', 'step7_create_exam.png', teacherToken);

    // 8. Exam View
    await capture('http://localhost:8080/room/30001/exam/30001', 'step8_exam_view.png', teacherToken);

    // 9. Exam Submit (Student)
    await capture('http://localhost:8080/room/30001/exam/30001/submit', 'step9_exam_submit.png', studentToken);

    // 10. Room Review / Grading List (Teacher)
    await capture('http://localhost:8080/room/30001/exam/30001/review', 'step10_exam_review.png', teacherToken);

    // 11. Student Grading Detail (Teacher)
    await capture('http://localhost:8080/room/30001/exam/30001/grading/2', 'step11_student_grading.png', teacherToken);

    // 12. Room Analytics
    await capture('http://localhost:8080/room/30001/analytics', 'step12_room_analytics.png', teacherToken);

    // 13. Student History
    await capture('http://localhost:8080/history', 'step13_student_history.png', studentToken);

  } catch (err) {
    console.error('Error during capture:', err);
  } finally {
    await browser.close();
    console.log('Capture finished.');
  }
}

run();
