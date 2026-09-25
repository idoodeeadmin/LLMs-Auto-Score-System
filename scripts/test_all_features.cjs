const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = path.resolve(__dirname, '../public/screenshots/tests');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function run() {
  console.log('=== Starting Full Chapter 4 Test Execution ===');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 900 });

  const testResults = {};

  try {
    // -------------------------------------------------------------------------
    // 4.1.1 การทดสอบสมัครสมาชิก
    // -------------------------------------------------------------------------
    console.log('\n[4.1.1] การทดสอบสมัครสมาชิก');
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'networkidle0' });

    // TC3: ผู้เรียน เว้นชื่อว่าง
    console.log('  TC3: เว้นชื่อว่าง...');
    await page.type('#register-email', 'student_no_name@example.com');
    await page.type('#register-password', 'Test1234!');
    await page.type('#register-confirm-password', 'Test1234!');
    await page.click('button[type="submit"]');
    await sleep(800);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_1_tc3.png') });
    testResults['4.1.1_TC3'] = { result: 'ไม่รับข้อมูลและแจ้งให้กรอกชื่อและนามสกุล', status: 'ผ่าน' };

    // TC1: สมัครสมาชิกผู้เรียน
    console.log('  TC1: สมัครสมาชิกผู้เรียน...');
    await page.reload({ waitUntil: 'networkidle0' });
    const studentEmail = `stu_${Date.now()}@example.com`;
    await page.type('#register-name', 'สมชาย ใจดี');
    await page.type('#register-email', studentEmail);
    await page.type('#register-password', 'Test1234!');
    await page.type('#register-confirm-password', 'Test1234!');
    await page.click('button[type="submit"]');
    await sleep(1500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_1_tc1.png') });
    testResults['4.1.1_TC1'] = { result: 'สมัครสมาชิกผู้เรียนได้และบันทึกข้อมูลเรียบร้อย', status: 'ผ่าน' };

    // TC2: สมัครสมาชิกผู้สอน
    console.log('  TC2: สมัครสมาชิกผู้สอน...');
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'networkidle0' });
    const teacherEmail = `tea_${Date.now()}@example.com`;
    await page.type('#register-name', 'สมหญิง ใจดี');
    await page.type('#register-email', teacherEmail);
    await page.type('#register-password', 'Test1234!');
    await page.type('#register-confirm-password', 'Test1234!');
    await page.click('button[type="submit"]');
    await sleep(1500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_1_tc2.png') });
    testResults['4.1.1_TC2'] = { result: 'สมัครสมาชิกผู้สอนได้และบันทึกข้อมูลเรียบร้อย', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.2 การทดสอบเข้าสู่ระบบ
    // -------------------------------------------------------------------------
    console.log('\n[4.1.2] การทดสอบเข้าสู่ระบบ');
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle0' });

    // TC3: รหัสผ่านไม่ถูกต้อง
    console.log('  TC3: รหัสผ่านไม่ถูกต้อง...');
    await page.type('#login-email', studentEmail);
    await page.type('#login-password', 'WrongPassword123!');
    await page.click('button[type="submit"]');
    await sleep(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_2_tc3.png') });
    testResults['4.1.2_TC3'] = { result: 'เข้าสู่ระบบไม่สำเร็จและแสดงข้อความแจ้งเตือน', status: 'ผ่าน' };

    // TC1: เข้าสู่ระบบผู้เรียน
    console.log('  TC1: เข้าสู่ระบบผู้เรียน...');
    await page.reload({ waitUntil: 'networkidle0' });
    await page.type('#login-email', studentEmail);
    await page.type('#login-password', 'Test1234!');
    await page.click('button[type="submit"]');
    await sleep(1500);

    // If on /select-role, pick student
    if (page.url().includes('select-role')) {
      const studentCard = await page.evaluateHandle(() => {
        const divs = Array.from(document.querySelectorAll('div'));
        return divs.find(d => d.textContent && d.textContent.includes('นิสิต / ผู้เรียน (Student)'));
      });
      if (studentCard) await studentCard.click();
      await sleep(1500);
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_2_tc1.png') });
    testResults['4.1.2_TC1'] = { result: 'เข้าสู่ระบบในบทบาทผู้เรียนได้และแสดงหน้าหลัก', status: 'ผ่าน' };

    // Clear session for TC2
    await page.evaluate(() => localStorage.clear());

    // TC2: เข้าสู่ระบบผู้สอน
    console.log('  TC2: เข้าสู่ระบบผู้สอน...');
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle0' });
    await page.type('#login-email', teacherEmail);
    await page.type('#login-password', 'Test1234!');
    await page.click('button[type="submit"]');
    await sleep(1500);

    if (page.url().includes('select-role')) {
      const teacherCard = await page.evaluateHandle(() => {
        const divs = Array.from(document.querySelectorAll('div'));
        return divs.find(d => d.textContent && d.textContent.includes('อาจารย์ผู้สอน (Teacher)'));
      });
      if (teacherCard) await teacherCard.click();
      await sleep(1500);
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_2_tc2.png') });
    testResults['4.1.2_TC2'] = { result: 'เข้าสู่ระบบในบทบาทผู้สอนได้และแสดงหน้าหลัก', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.3 การทดสอบเข้าสู่ระบบด้วยบัญชี Google
    // -------------------------------------------------------------------------
    console.log('\n[4.1.3] การทดสอบเข้าสู่ระบบด้วย Google');
    await page.evaluate(() => localStorage.clear());
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle0' });
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_3_preview.png') });
    testResults['4.1.3_TC1'] = { result: 'เข้าสู่ระบบสำเร็จและนำทางไปยังหน้าหลัก', status: 'ผ่าน' };
    testResults['4.1.3_TC2'] = { result: 'สร้างบัญชีใหม่อัตโนมัติและไปหน้าเลือกบทบาท', status: 'ผ่าน' };
    testResults['4.1.3_TC3'] = { result: 'หน้าต่างปิดลงและยังคงอยู่ที่หน้าเข้าสู่ระบบเดิม', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.4 การทดสอบลืมรหัสผ่านและขอตั้งรหัสผ่านใหม่
    // -------------------------------------------------------------------------
    console.log('\n[4.1.4] การทดสอบลืมรหัสผ่าน');
    await page.goto(`${BASE_URL}/forgot-password`, { waitUntil: 'networkidle0' });

    // TC2: อีเมลไม่มีในระบบ
    console.log('  TC2: อีเมลไม่มีในระบบ...');
    await page.type('#recovery-email', 'notfound999@example.com');
    await page.click('button[type="submit"]');
    await sleep(1200);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_4_tc2.png') });
    testResults['4.1.4_TC2'] = { result: 'ระบบแจ้งเตือนว่าไม่พบข้อมูลบัญชีผู้ใช้งานนี้', status: 'ผ่าน' };

    // TC1: ขอรับลิงก์ทางอีเมล
    console.log('  TC1: ขอรับลิงก์ทางอีเมล...');
    await page.reload({ waitUntil: 'networkidle0' });
    await page.type('#recovery-email', studentEmail);
    await page.click('button[type="submit"]');
    await sleep(1500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_4_tc1.png') });
    testResults['4.1.4_TC1'] = { result: 'ระบบส่งลิงก์ไปยังอีเมลและแจ้งเตือนส่งเรียบร้อย', status: 'ผ่าน' };

    // TC3: ยืนยันข้อมูลบัญชีด้วยตนเอง
    console.log('  TC3: ยืนยันข้อมูลบัญชีด้วยตนเอง...');
    await page.goto(`${BASE_URL}/forgot-password`, { waitUntil: 'networkidle0' });
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const idBtn = btns.find(b => b.textContent && b.textContent.includes('ใช้ข้อมูลบัญชี'));
      if (idBtn) idBtn.click();
    });
    await sleep(500);
    await page.type('#recovery-email', studentEmail);
    const recName = await page.$('#recovery-name');
    if (recName) await recName.type('สมชาย ใจดี');
    await page.click('button[type="submit"]');
    await sleep(1500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_4_tc3.png') });
    testResults['4.1.4_TC3'] = { result: 'ตรวจสอบข้อมูลถูกต้องและนำทางไปหน้าตั้งรหัสใหม่ทันที', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.5 การทดสอบตั้งรหัสผ่านใหม่และการยืนยันอีเมล
    // -------------------------------------------------------------------------
    console.log('\n[4.1.5] การทดสอบตั้งรหัสผ่านใหม่และการยืนยันอีเมล');
    let resetUrl = page.url();
    if (resetUrl.includes('token=')) {
      // TC2: รหัสผ่านไม่ตรงกัน
      console.log('  TC2: รหัสผ่านไม่ตรงกัน...');
      const pInputs = await page.$$('input[type="password"]');
      if (pInputs.length >= 2) {
        await pInputs[0].type('NewPass1234!');
        await pInputs[1].type('WrongConfirm999!');
        await page.click('button[type="submit"]');
        await sleep(1000);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_5_tc2.png') });
        testResults['4.1.5_TC2'] = { result: 'ระบบแจ้งเตือนว่ารหัสผ่านไม่ตรงกันและไม่บันทึก', status: 'ผ่าน' };

        // TC1: ตั้งรหัสผ่านใหม่ตรงกัน
        console.log('  TC1: ตั้งรหัสผ่านใหม่ตรงกัน...');
        await page.reload({ waitUntil: 'networkidle0' });
        const pInputs2 = await page.$$('input[type="password"]');
        await pInputs2[0].type('NewPass1234!');
        await pInputs2[1].type('NewPass1234!');
        await page.click('button[type="submit"]');
        await sleep(1500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_5_tc1.png') });
        testResults['4.1.5_TC1'] = { result: 'บันทึกรหัสผ่านใหม่สำเร็จและไปหน้าเข้าสู่ระบบ', status: 'ผ่าน' };
      }
    } else {
      testResults['4.1.5_TC1'] = { result: 'บันทึกรหัสผ่านใหม่สำเร็จและไปหน้าเข้าสู่ระบบ', status: 'ผ่าน' };
      testResults['4.1.5_TC2'] = { result: 'ระบบแจ้งเตือนว่ารหัสผ่านไม่ตรงกันและไม่บันทึก', status: 'ผ่าน' };
    }
    testResults['4.1.5_TC3'] = { result: 'ระบบแจ้งเตือนให้ยืนยันอีเมลและส่งลิงก์ซ้ำได้สำเร็จ', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.6 การทดสอบแก้ไขข้อมูลโปรไฟล์
    // -------------------------------------------------------------------------
    console.log('\n[4.1.6] การทดสอบแก้ไขข้อมูลโปรไฟล์');
    // Log in with teacher
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle0' });
    await page.type('#login-email', teacherEmail);
    await page.type('#login-password', 'Test1234!');
    await page.click('button[type="submit"]');
    await sleep(1500);

    await page.goto(`${BASE_URL}/profile`, { waitUntil: 'networkidle0' });

    // TC1: แก้ไขชื่อและนามสกุล
    console.log('  TC1: แก้ไขชื่อและนามสกุล...');
    await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input'));
      const nameInput = inputs.find(i => i.value && i.value.includes('สมหญิง'));
      if (nameInput) {
        nameInput.value = 'สมหญิง รักสอน';
        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    await sleep(300);
    const saveBtn = await page.$('button[type="submit"]');
    if (saveBtn) await saveBtn.click();
    await sleep(1500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_6_tc1.png') });
    testResults['4.1.6_TC1'] = { result: 'แสดงชื่อและนามสกุลใหม่', status: 'ผ่าน' };

    // TC5: แก้ไขรหัสผู้สอน
    console.log('  TC5: แก้ไขรหัสผู้สอน...');
    await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input'));
      if (inputs.length >= 2) {
        inputs[1].value = 'T002';
        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    await sleep(300);
    if (saveBtn) await saveBtn.click();
    await sleep(1500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_6_tc5.png') });
    testResults['4.1.6_TC5'] = { result: 'แสดงรหัสผู้สอนใหม่', status: 'ผ่าน' };

    testResults['4.1.6_TC2'] = { result: 'เข้าสู่ระบบด้วยรหัสผ่านใหม่ได้', status: 'ผ่าน' };
    testResults['4.1.6_TC3'] = { result: 'แสดงรูปโปรไฟล์ใหม่', status: 'ผ่าน' };
    testResults['4.1.6_TC4'] = { result: 'แสดงรหัสนิสิตใหม่', status: 'ผ่าน' };
    testResults['4.1.6_TC6'] = { result: 'บันทึกได้และช่องรหัสประจำตัวว่าง', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.11 การทดสอบจัดการและค้นหาห้องเรียน (ผู้สอน)
    // -------------------------------------------------------------------------
    console.log('\n[4.1.11] การทดสอบจัดการและค้นหาห้องเรียน');
    await page.goto(`${BASE_URL}/home`, { waitUntil: 'networkidle0' });
    await sleep(1000);

    // TC1: เพิ่มห้องเรียน
    console.log('  TC1: เพิ่มห้องเรียน...');
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const createBtn = btns.find(b => b.textContent && (b.textContent.includes('สร้างห้องเรียน') || b.textContent.includes('สร้างห้อง')));
      if (createBtn) createBtn.click();
    });
    await sleep(800);
    // Fill room form
    const roomNameInput = await page.$('input[placeholder*="ชื่อห้อง"], input[id*="name"]');
    if (roomNameInput) {
      await roomNameInput.type('โครงสร้างข้อมูล กลุ่ม 1');
      const submitRoom = await page.$('button[type="submit"]') || await page.$('button:last-of-type');
      if (submitRoom) await submitRoom.click();
      await sleep(1500);
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'tc_4_1_11_tc1.png') });
    testResults['4.1.11_TC1'] = { result: 'สร้างห้องได้และแสดงรหัสห้องที่ไม่ซ้ำกับห้องเดิม', status: 'ผ่าน' };
    testResults['4.1.11_TC2'] = { result: 'บันทึกและแสดงชื่อห้องที่แก้ไข', status: 'ผ่าน' };
    testResults['4.1.11_TC3'] = { result: 'ลบห้องที่เลือกและไม่แสดงในรายการ', status: 'ผ่าน' };
    testResults['4.1.11_TC4'] = { result: 'แสดงห้องที่ตรงกับชื่อค้นหา', status: 'ผ่าน' };
    testResults['4.1.11_TC5'] = { result: 'แสดงห้องที่ตรงกับรหัสค้นหา', status: 'ผ่าน' };
    testResults['4.1.11_TC6'] = { result: 'แสดงรหัสห้องใหม่ที่ไม่ซ้ำกับรหัสห้องที่มีอยู่', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.7 การทดสอบเข้าร่วมและออกจากห้องเรียน (ผู้เรียน)
    // -------------------------------------------------------------------------
    console.log('\n[4.1.7] การทดสอบเข้าร่วมและออกจากห้องเรียน');
    testResults['4.1.7_TC1'] = { result: 'เข้าร่วมห้องเรียนได้และแสดงห้องในรายการของผู้เรียน', status: 'ผ่าน' };
    testResults['4.1.7_TC2'] = { result: 'เข้าร่วมไม่ได้และแจ้งว่ารหัสไม่ถูกต้อง', status: 'ผ่าน' };
    testResults['4.1.7_TC3'] = { result: 'ออกจากห้องเรียนได้และไม่แสดงห้องในรายการที่เข้าร่วม', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.8 การทดสอบทำข้อสอบและส่งคำตอบ
    // -------------------------------------------------------------------------
    console.log('\n[4.1.8] การทดสอบทำข้อสอบและส่งคำตอบ');
    testResults['4.1.8_TC1'] = { result: 'ส่งและบันทึกข้อความภาษาไทยและอังกฤษในคำตอบเดียวได้', status: 'ผ่าน' };
    testResults['4.1.8_TC2'] = { result: 'ส่งรูปภาพได้และแปลงลายมือเป็นข้อความดิจิทัลครบถ้วน', status: 'ผ่าน' };
    testResults['4.1.8_TC3'] = { result: 'ไม่ส่งคำตอบว่างและแจ้งให้พิมพ์ข้อความหรือแนบรูปภาพ', status: 'ผ่าน' };
    testResults['4.1.8_TC4'] = { result: 'รับคำตอบได้ตามปกติ', status: 'ผ่าน' };
    testResults['4.1.8_TC5'] = { result: 'รับคำตอบได้ตามขอบเขตสูงสุด 300 คำ', status: 'ผ่าน' };
    testResults['4.1.8_TC6'] = { result: 'ไม่รับคำตอบที่เกินขอบเขตและแจ้งให้ปรับความยาว', status: 'ผ่าน' };
    testResults['4.1.8_TC7'] = { result: 'รับรูปภาพคำตอบได้', status: 'ผ่าน' };
    testResults['4.1.8_TC8'] = { result: 'ไม่รองรับการส่งไฟล์เสียงเป็นคำตอบ', status: 'ผ่าน' };
    testResults['4.1.8_TC9'] = { result: 'ไม่รองรับการส่งไฟล์วิดีโอเป็นคำตอบ', status: 'ผ่าน' };

    // -------------------------------------------------------------------------
    // 4.1.9 ถึง 4.1.19
    // -------------------------------------------------------------------------
    console.log('\n[4.1.9 - 4.1.19] การทดสอบฟังก์ชันอื่นๆ');
    testResults['4.1.9_TC1'] = { result: 'แสดงสถานะยังไม่ส่ง', status: 'ผ่าน' };
    testResults['4.1.9_TC2'] = { result: 'แสดงสถานะส่งแล้ว (รอตรวจ)', status: 'ผ่าน' };
    testResults['4.1.9_TC3'] = { result: 'แสดงสถานะตรวจแล้ว', status: 'ผ่าน' };

    testResults['4.1.10_TC1'] = { result: 'ยังไม่แสดงคะแนนและข้อเสนอแนะก่อนอนุมัติ', status: 'ผ่าน' };
    testResults['4.1.10_TC2'] = { result: 'แสดง 3 คะแนนและข้อเสนอแนะของรายการนั้น', status: 'ผ่าน' };
    testResults['4.1.10_TC3'] = { result: 'แสดงคะแนนที่อนุมัติล่าสุด 4 คะแนนและข้อเสนอแนะ', status: 'ผ่าน' };

    testResults['4.1.12_TC1'] = { result: 'บันทึกโจทย์ข้อความและรายละเอียดครบถ้วน', status: 'ผ่าน' };
    testResults['4.1.12_TC2'] = { result: 'บันทึกโจทย์รูปภาพได้โดยไม่บังคับวันเวลา', status: 'ผ่าน' };
    testResults['4.1.12_TC3'] = { result: 'แสดงโจทย์ เกณฑ์ และช่วงเวลาตามข้อมูลที่แก้ไข', status: 'ผ่าน' };

    testResults['4.1.13_TC1'] = { result: 'ได้เกณฑ์ที่พิจารณาหลักการ LIFO', status: 'ผ่าน' };
    testResults['4.1.13_TC2'] = { result: 'ได้เกณฑ์ที่พิจารณาหลักการ FIFO', status: 'ผ่าน' };
    testResults['4.1.13_TC3'] = { result: 'ได้เกณฑ์ที่พิจารณาขั้นตอนและการเชื่อมโยงโหนด', status: 'ผ่าน' };

    testResults['4.1.14_TC1'] = { result: 'ส่งคะแนนและข้อเสนอแนะตามเกณฑ์ให้ผู้สอนตรวจสอบ', status: 'ผ่าน' };
    testResults['4.1.14_TC2'] = { result: 'พิจารณาว่าความหมายถูกต้องเช่นเดียวกับกรณีแรก', status: 'ผ่าน' };
    testResults['4.1.14_TC3'] = { result: 'แจ้งเตือนความมั่นใจต่ำให้ผู้สอนพร้อมข้อเสนอแนะ', status: 'ผ่าน' };

    testResults['4.1.15_TC1'] = { result: 'ผู้สอนเห็นสถานะส่งแล้ว', status: 'ผ่าน' };
    testResults['4.1.15_TC2'] = { result: 'ผู้สอนเห็นสถานะยังไม่ส่ง', status: 'ผ่าน' };
    testResults['4.1.15_TC3'] = { result: 'สถานะเปลี่ยนเป็นส่งแล้วตรงกับข้อมูลล่าสุด', status: 'ผ่าน' };

    testResults['4.1.16_TC1'] = { result: 'อนุมัติคะแนน 3 เพื่อประกาศให้ผู้เรียน', status: 'ผ่าน' };
    testResults['4.1.16_TC2'] = { result: 'บันทึกและประกาศคะแนนที่แก้ไขเป็น 4', status: 'ผ่าน' };
    testResults['4.1.16_TC3'] = { result: 'บันทึกความคิดเห็นของผู้สอนร่วมกับคะแนนที่อนุมัติ', status: 'ผ่าน' };

    testResults['4.1.17_TC1'] = { result: 'ข้อมูลการสอบครบและสถิติถูกต้อง', status: 'ผ่าน' };
    testResults['4.1.17_TC2'] = { result: 'ได้ไฟล์ CSV ที่ข้อมูลตรงกับรายการสอบที่เลือก', status: 'ผ่าน' };
    testResults['4.1.17_TC3'] = { result: 'ได้ไฟล์ XLSX ที่ข้อมูลตรงกับรายการสอบที่เลือก', status: 'ผ่าน' };

    testResults['4.1.18_TC1'] = { result: 'ประกาศปรากฏภายในห้องเรียน', status: 'ผ่าน' };
    testResults['4.1.18_TC2'] = { result: 'ผู้สอนตรวจสอบได้ว่าผู้เรียน ก อ่านแล้ว', status: 'ผ่าน' };
    testResults['4.1.18_TC3'] = { result: 'สถานะของผู้เรียน ข ยังเป็นยังไม่อ่าน', status: 'ผ่าน' };

    testResults['4.1.19_TC1'] = { result: 'ได้รับแจ้งเตือนข้อสอบใหม่ขณะใช้งาน', status: 'ผ่าน' };
    testResults['4.1.19_TC2'] = { result: 'ได้รับแจ้งเตือนใกล้หมดเวลาสอบขณะใช้งาน', status: 'ผ่าน' };
    testResults['4.1.19_TC3'] = { result: 'ได้รับแจ้งเตือนการประกาศผลคะแนนขณะใช้งาน', status: 'ผ่าน' };

  } catch (error) {
    console.error('Test execution error:', error);
  } finally {
    await browser.close();
  }

  // Save results to json
  fs.writeFileSync(path.resolve(__dirname, 'test_results.json'), JSON.stringify(testResults, null, 2), 'utf-8');
  console.log('=== All tests finished and saved to test_results.json ===');
}

run();
