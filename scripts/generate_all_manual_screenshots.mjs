import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const outDir = path.join(rootDir, 'docs_and_tests', 'screenshots', 'manual');

if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJpZCI6MSwicm9sZSI6InRlYWNoZXIiLCJleHAiOjE3OTE0NzA0NTJ9.TakALaVVZodWpV6fM87kJugPnYXJiOIoDeo2iGCZ_L8';
const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsImlkIjoyLCJyb2xlIjoic3R1ZGVudCIsImV4cCI6MTc5MTQ3MDQ2OH0.nPZ2WH0zkwE3vgkKl4uUFeIh6Ch9qgQ5IuYi9U4PXYM';

const manualSteps = [
  {
    filename: 'manual_01_login.png',
    url: 'http://localhost:8080/',
    token: null,
    annotations: [
      { selector: 'input[placeholder*="email"], input[placeholder*="student"]', num: 1 },
      { selector: 'input[type="password"]', num: 2 },
      { selector: 'button[type="submit"]', num: 3 },
      { selector: 'button:has(svg), div:has(> svg):has-text("Google")', textMatch: 'Google', num: 4 },
      { textMatch: 'ลืมรหัสผ่าน', num: 5 },
      { textMatch: 'สร้างบัญชี', num: 6 }
    ]
  },
  {
    filename: 'manual_02_register.png',
    url: 'http://localhost:8080/register',
    token: null,
    annotations: [
      { selector: 'input[placeholder*="สิทธิกร"]', num: 1 },
      { selector: 'input[placeholder*="email"]', num: 2 },
      { selector: 'input[placeholder*="8 ตัวอักษร"]', num: 3 },
      { selector: 'input[placeholder*="กรอกอีกครั้ง"]', num: 4 },
      { selector: 'button[type="submit"]', num: 5 },
      { textMatch: 'เข้าสู่ระบบ', num: 6 }
    ]
  },
  {
    filename: 'manual_03_forgot_password.png',
    url: 'http://localhost:8080/forgot-password',
    token: null,
    annotations: [
      { selector: 'input[placeholder*="email"]', num: 1 },
      { selector: 'button[type="submit"]', num: 2 },
      { textMatch: 'กลับไปหน้าเข้าสู่ระบบ', num: 3 }
    ]
  },
  {
    filename: 'manual_04_profile.png',
    url: 'http://localhost:8080/profile',
    token: teacherToken,
    annotations: [
      { selector: 'input[type="file"], label:has(input[type="file"]), .avatar-upload', textMatch: 'รูปโปรไฟล์', num: 1 },
      { selector: 'input[placeholder*="ชื่อ"], input[value*="SoSad"]', num: 2 },
      { selector: 'input[placeholder*="รหัสประจำตัว"]', num: 3 },
      { selector: 'input[placeholder*="รหัสผ่านปัจจุบัน"]', num: 4 },
      { selector: 'button[type="submit"]', textMatch: 'บันทึก', num: 5 }
    ]
  },
  {
    filename: 'manual_05_teacher_dashboard.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    annotations: [
      { textMatch: 'สร้างห้องเรียน', num: 1 },
      { selector: 'input[placeholder*="ค้นหา"]', num: 2 },
      { textMatch: 'รหัสห้องเรียน', num: 3 },
      { textMatch: 'เปิดห้องเรียน', num: 4 }
    ]
  },
  {
    filename: 'manual_06_create_room_modal.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    beforeAnnotate: async (page) => {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('สร้างห้องเรียน'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { selector: 'input[placeholder*="ชื่อวิชา"], input[placeholder*="ชื่อห้องเรียน"]', num: 1 },
      { selector: 'input[placeholder*="กลุ่มเรียน"], input[placeholder*="Section"]', num: 2 },
      { selector: 'div[role="dialog"] button:has-text("สร้าง"), div[role="dialog"] button:last-child', textMatch: 'สร้าง', num: 3 }
    ]
  },
  {
    filename: 'manual_07_student_dashboard.png',
    url: 'http://localhost:8080/home',
    token: studentToken,
    annotations: [
      { textMatch: 'เข้าร่วมห้องเรียน', num: 1 },
      { selector: 'input[placeholder*="ค้นหา"]', num: 2 },
      { textMatch: 'เปิดห้องเรียน', num: 3 }
    ]
  },
  {
    filename: 'manual_08_join_room_modal.png',
    url: 'http://localhost:8080/home',
    token: studentToken,
    beforeAnnotate: async (page) => {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('เข้าร่วมห้องเรียน'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { selector: 'input[placeholder*="รหัส"], input[placeholder*="Code"]', num: 1 },
      { selector: 'div[role="dialog"] button:has-text("เข้าร่วม"), div[role="dialog"] button:last-child', textMatch: 'เข้าร่วม', num: 2 }
    ]
  },
  {
    filename: 'manual_09_room_stream.png',
    url: 'http://localhost:8080/room/30001',
    token: teacherToken,
    annotations: [
      { textMatch: 'สมาชิกในห้อง', num: 1 },
      { textMatch: 'รหัสชั้นเรียน', num: 2 },
      { selector: 'input[placeholder*="ประกาศ"], textarea[placeholder*="ประกาศ"]', num: 3 },
      { textMatch: 'มอบหมายข้อสอบ', num: 4 },
      { textMatch: 'ตรวจงาน', num: 5 }
    ]
  },
  {
    filename: 'manual_10_room_members.png',
    url: 'http://localhost:8080/room/30001',
    token: teacherToken,
    beforeAnnotate: async (page) => {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes('สมาชิกในห้อง'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { textMatch: 'ผู้สอน', num: 1 },
      { textMatch: 'ผู้เรียน', num: 2 }
    ]
  },
  {
    filename: 'manual_11_create_exam_top.png',
    url: 'http://localhost:8080/room/30001/create-exam',
    token: teacherToken,
    annotations: [
      { selector: 'input[placeholder*="ชื่อข้อสอบ"]', num: 1 },
      { selector: 'textarea[placeholder*="คำชี้แจง"]', num: 2 },
      { textMatch: 'เริ่มทำได้ทันที', num: 3 },
      { textMatch: 'ไม่มีกำหนดส่ง', num: 4 },
      { textMatch: 'สุ่มลำดับข้อ', num: 5 }
    ]
  },
  {
    filename: 'manual_12_create_exam_rubric.png',
    url: 'http://localhost:8080/room/30001/create-exam',
    token: teacherToken,
    beforeAnnotate: async (page) => {
      await page.evaluate(() => {
        const toggle = Array.from(document.querySelectorAll('button, div, span')).find(el => el.innerText.includes('แนวคำตอบและเกณฑ์คะแนน'));
        if (toggle) toggle.click();
        window.scrollBy(0, 450);
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { selector: 'textarea[placeholder*="โจทย์"], textarea[placeholder*="คำถาม"]', num: 1 },
      { selector: 'input[placeholder*="คะแนนเต็ม"], input[type="number"]', num: 2 },
      { textMatch: 'แนบรูป', num: 3 },
      { textMatch: 'สร้างเกณฑ์ด้วย AI', num: 4 },
      { textMatch: 'เผยแพร่', num: 5 },
      { textMatch: 'บันทึกร่าง', num: 6 }
    ]
  },
  {
    filename: 'manual_13_student_exam_submit.png',
    url: 'http://localhost:8080/room/30001/exam/30001/submit',
    token: studentToken,
    annotations: [
      { textMatch: 'พิมพ์คำตอบ', num: 1 },
      { textMatch: 'อัปโหลดรูปภาพ', num: 2 },
      { selector: 'textarea, input[type="file"]', num: 3 },
      { textMatch: 'ส่งข้อสอบ', num: 4 }
    ]
  },
  {
    filename: 'manual_14_teacher_review_list.png',
    url: 'http://localhost:8080/room/30001/exam/30001/review',
    token: teacherToken,
    annotations: [
      { textMatch: 'ตรวจคำตอบด้วย AI', num: 1 },
      { textMatch: 'ส่งแล้ว', num: 2 },
      { textMatch: 'อนุมัติแล้ว', num: 3 },
      { textMatch: 'ตรวจทาน', num: 4 }
    ]
  },
  {
    filename: 'manual_15_student_grading_detail.png',
    url: 'http://localhost:8080/room/30001/exam/120001/grading/30001',
    token: teacherToken,
    annotations: [
      { textMatch: 'คำตอบที่ส่ง', selector: '.answer-card, .student-answer', num: 1 },
      { textMatch: 'คะแนน AI', selector: '.ai-score-badge, [class*="score"]', num: 2 },
      { textMatch: 'ข้อเสนอแนะ', num: 3 },
      { selector: 'input[type="number"]', textMatch: 'คะแนนผู้สอน', num: 4 },
      { textMatch: 'อนุมัติผลคะแนน', num: 5 }
    ]
  },
  {
    filename: 'manual_16_room_analytics.png',
    url: 'http://localhost:8080/room/30001/analytics',
    token: teacherToken,
    annotations: [
      { textMatch: 'ภาพรวม', num: 1 },
      { textMatch: 'คะแนนเฉลี่ย', num: 2 },
      { textMatch: 'ส่งออกรายงาน', num: 3 }
    ]
  },
  {
    filename: 'manual_17_student_history.png',
    url: 'http://localhost:8080/history',
    token: studentToken,
    annotations: [
      { textMatch: 'ประวัติการส่งข้อสอบ', num: 1 },
      { textMatch: 'ผลการประเมิน', num: 2 }
    ]
  },
  {
    filename: 'manual_18_notifications_and_menu.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    beforeAnnotate: async (page) => {
      await page.evaluate(() => {
        const bell = document.querySelector('button:has(svg.lucide-bell), button svg.lucide-bell');
        if (bell) (bell.closest('button') || bell).click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { selector: 'button:has(svg.lucide-bell)', num: 1 },
      { textMatch: 'การแจ้งเตือน', num: 2 },
      { selector: 'button:has(svg.lucide-sun), button:has(svg.lucide-moon)', num: 3 },
      { selector: 'button:has(img[alt*="avatar"]), button:has(span[class*="avatar"])', num: 4 }
    ]
  }
];

async function runGenerator() {
  console.log('Launching browser with scale factor 2...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,850'],
    defaultViewport: { width: 1280, height: 850, deviceScaleFactor: 2 }
  });

  const page = await browser.newPage();

  for (const step of manualSteps) {
    try {
      console.log(`Generating ${step.filename}...`);

      // Set token before loading page
      await page.evaluateOnNewDocument((tok) => {
        if (tok) {
          localStorage.setItem('token', tok);
        } else {
          localStorage.removeItem('token');
        }
      }, step.token);

      await page.goto(step.url, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(e => console.log('Goto err:', e.message));

      // Wait for React to finish rendering
      await new Promise(r => setTimeout(r, 1500));
      await page.waitForFunction(() => !document.querySelector('.animate-pulse'), { timeout: 10000 }).catch(() => {});

      if (step.beforeAnnotate) {
        await step.beforeAnnotate(page);
      }

      // Add annotations
      if (step.annotations && step.annotations.length > 0) {
        await page.evaluate((annList) => {
          annList.forEach(({ selector, textMatch, num, shape }) => {
            let target = null;
            if (selector) {
              try {
                target = document.querySelector(selector);
              } catch (e) {}
            }
            if (!target && textMatch) {
              const elements = Array.from(document.querySelectorAll('button, a, input, div, span, p, label, th, td, h1, h2, h3'));
              target = elements.find(el => el.children.length === 0 && el.innerText.trim().includes(textMatch)) ||
                       elements.find(el => el.innerText.trim().includes(textMatch));
            }

            if (target) {
              const rect = target.getBoundingClientRect();
              if (rect.width === 0 || rect.height === 0) return;

              const box = document.createElement('div');
              box.className = 'manual-annotation-box';
              box.style.position = 'absolute';
              box.style.left = `${rect.left + window.scrollX - 4}px`;
              box.style.top = `${rect.top + window.scrollY - 4}px`;
              box.style.width = `${rect.width + 8}px`;
              box.style.height = `${rect.height + 8}px`;
              box.style.border = '3px solid #ef4444';
              box.style.borderRadius = shape === 'circle' ? '50%' : '8px';
              box.style.boxShadow = '0 0 12px rgba(239, 68, 68, 0.7)';
              box.style.pointerEvents = 'none';
              box.style.zIndex = '999999';

              const badge = document.createElement('div');
              badge.style.position = 'absolute';
              badge.style.top = '-14px';
              badge.style.left = '-14px';
              badge.style.width = '28px';
              badge.style.height = '28px';
              badge.style.backgroundColor = '#ef4444';
              badge.style.color = '#ffffff';
              badge.style.borderRadius = '50%';
              badge.style.fontWeight = 'bold';
              badge.style.fontSize = '16px';
              badge.style.display = 'flex';
              badge.style.alignItems = 'center';
              badge.style.justifyContent = 'center';
              badge.style.boxShadow = '0 2px 6px rgba(0,0,0,0.5)';
              badge.style.fontFamily = 'Arial, sans-serif';
              badge.innerText = String(num);

              box.appendChild(badge);
              document.body.appendChild(box);
            }
          });
        }, step.annotations);
      }

      await new Promise(r => setTimeout(r, 400));
      const targetFile = path.join(outDir, step.filename);
      await page.screenshot({ path: targetFile, fullPage: false });
      console.log(`  -> Saved ${step.filename} (${fs.statSync(targetFile).size} bytes)`);

      // Clean up annotations
      await page.evaluate(() => {
        document.querySelectorAll('.manual-annotation-box').forEach(el => el.remove());
      });

    } catch (err) {
      console.error(`Error in ${step.filename}:`, err.message);
    }
  }

  await browser.close();
  console.log('Complete generation finished!');
}

runGenerator();
