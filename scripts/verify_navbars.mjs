import puppeteer from 'puppeteer';
import path from 'path';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const artifactsDir = 'C:\\Users\\idood\\.gemini\\antigravity-ide\\brain\\f6ee475c-7cae-4670-a1aa-717c1db8426d';

async function verifyNavbars() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  page.on('dialog', async d => await d.accept());

  try {
    console.log('--- 1. Set Auth as Student and check Home Navbar with Profile tab ---');
    await page.goto('http://127.0.0.1:8090/', { waitUntil: 'networkidle0' });
    await page.evaluate(() => {
      localStorage.setItem('token', 'fixture-student');
    });
    await page.goto('http://127.0.0.1:8090/home', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'navbar_01_home_student.png') });

    console.log('--- 2. Open UserProfileMenu dropdown on Home ---');
    const profileBtn = await page.$('button[aria-label="เมนูโปรไฟล์และบัญชี"]');
    if (profileBtn) {
      await profileBtn.click();
      await sleep(500);
      await page.screenshot({ path: path.join(artifactsDir, 'navbar_02_dropdown_open.png') });
      await page.keyboard.press('Escape');
      await sleep(300);
    }

    console.log('--- 3. Check Classroom RoomDetail Header with UserProfileMenu ---');
    await page.goto('http://127.0.0.1:8090/room/10', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'navbar_03_room_detail.png') });

    console.log('--- 4. Check Exam Submit Header with UserProfileMenu ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/submit', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'navbar_04_exam_submit.png') });

    console.log('--- 5. Switch to Teacher and Check Teacher Home Navbar ---');
    await page.evaluate(() => {
      localStorage.setItem('token', 'fixture-teacher');
    });
    await page.goto('http://127.0.0.1:8090/home', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'navbar_05_home_teacher.png') });

    console.log('--- 6. Check Student Grading Header with UserProfileMenu ---');
    await page.goto('http://127.0.0.1:8090/room/10/exam/1/grading/101', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'navbar_06_student_grading.png') });

    console.log('--- 7. Check Create Exam Header with UserProfileMenu ---');
    await page.goto('http://127.0.0.1:8090/room/10/create-exam', { waitUntil: 'networkidle0' });
    await sleep(1000);
    await page.screenshot({ path: path.join(artifactsDir, 'navbar_07_create_exam.png') });

    console.log('Navbar verification completed successfully!');
  } catch (err) {
    console.error('Navbar verification error:', err);
  } finally {
    await browser.close();
  }
}

verifyNavbars();
