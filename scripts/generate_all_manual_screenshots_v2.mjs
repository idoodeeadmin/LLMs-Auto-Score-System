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

// 100% valid tokens with token_version: 0 matching backend JWT_SECRET_KEY
const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowLCJleHAiOjE3OTE0NzQ2NTl9.yC-M7ahrK16bmmR857qZbnulzDC7BLQ3AiTegUSISJw';
const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsInRva2VuX3ZlcnNpb24iOjAsImV4cCI6MTc5MTQ3NDY1OX0.NVFfH5jqcdY2VDKGmzob81Gfk9gUpiXKcMBrc02mkY0';

const steps = [
  {
    filename: 'manual_01_login.png',
    url: 'http://localhost:8080/',
    token: null,
    expectedCount: 6,
    annotations: [
      { num: 1, selectors: ['input#login-email', 'input[type="email"]', 'input[placeholder*="email" i]'] },
      { num: 2, selectors: ['input#login-password', 'input[type="password"]'] },
      { num: 3, selectors: ['button[type="submit"]'] },
      { num: 4, textMatches: ['Google', 'เข้าสู่ระบบด้วย Google'], selectors: ['button:has(svg)'] },
      { num: 5, textMatches: ['ลืมรหัสผ่าน'], selectors: ['a[href*="forgot"]'] },
      { num: 6, textMatches: ['สร้างบัญชี'], selectors: ['a[href*="register"]'] }
    ]
  },
  {
    filename: 'manual_02_register.png',
    url: 'http://localhost:8080/register',
    token: null,
    expectedCount: 6,
    annotations: [
      { num: 1, selectors: ['input#register-name', 'input[placeholder*="สิทธิกร"]'] },
      { num: 2, selectors: ['input#register-email', 'input[type="email"]'] },
      { num: 3, selectors: ['input#register-password', 'input[placeholder*="8 ตัวอักษร"]'] },
      { num: 4, selectors: ['input#register-confirm-password', 'input[placeholder*="กรอกอีกครั้ง"]'] },
      { num: 5, selectors: ['button[type="submit"]'] },
      { num: 6, textMatches: ['เข้าสู่ระบบ', 'มีบัญชีอยู่แล้ว'], selectors: ['a[href="/"]'] }
    ]
  },
  {
    filename: 'manual_03_forgot_password.png',
    url: 'http://localhost:8080/forgot-password',
    token: null,
    expectedCount: 3,
    annotations: [
      { num: 1, selectors: ['input#forgot-email', 'input[type="email"]'] },
      { num: 2, selectors: ['button[type="submit"]'] },
      { num: 3, textMatches: ['กลับไปหน้าเข้าสู่ระบบ', 'เข้าสู่ระบบ'], selectors: ['a[href="/"]'] }
    ]
  },
  {
    filename: 'manual_04_profile.png',
    url: 'http://localhost:8080/profile',
    token: teacherToken,
    expectedCount: 5,
    annotations: [
      { num: 1, selectors: ['label[for="avatar-upload"]', '#avatar-upload', '.avatar-upload'] },
      { num: 2, selectors: ['input#profile-name', 'input[name="name"]'] },
      { num: 3, selectors: ['input#profile-identity', 'input[name="identity"]'] },
      { num: 4, selectors: ['input#profile-password', 'input[type="password"]'] },
      { num: 5, selectors: ['button[type="submit"]'], textMatches: ['บันทึกการเปลี่ยนแปลง', 'บันทึก'] }
    ]
  },
  {
    filename: 'manual_05_teacher_dashboard.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    expectedCount: 4,
    annotations: [
      { num: 1, textMatches: ['สร้างห้องเรียน'], selectors: ['.room-create-button', 'button:has-text("สร้างห้องเรียน")'] },
      { num: 2, selectors: ['input[placeholder*="ค้นหา"]'] },
      { num: 3, selectors: ['p.font-mono', 'button:has-text("คัดลอก")', 'span.font-mono'] },
      { num: 4, selectors: ['a[href*="/room/"]:not([href="/home"])', 'a:has-text("เปิดห้องเรียน")'], textMatches: ['เปิดห้องเรียน'] }
    ]
  },
  {
    filename: 'manual_06_create_room_modal.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    expectedCount: 3,
    prepare: async (page) => {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('สร้างห้องเรียน'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { num: 1, selectors: ['input[placeholder*="โครงสร้างข้อมูล"]', 'div[role="dialog"] input:first-of-type'] },
      { num: 2, selectors: ['input[placeholder*="Sec 1"]', 'div[role="dialog"] input:nth-of-type(2)'] },
      { num: 3, selectors: ['div[role="dialog"] button[type="submit"]'], textMatches: ['สร้าง'] }
    ]
  },
  {
    filename: 'manual_07_student_dashboard.png',
    url: 'http://localhost:8080/home',
    token: studentToken,
    expectedCount: 3,
    annotations: [
      { num: 1, textMatches: ['เข้าร่วมห้องเรียน'], selectors: ['.room-join-button'] },
      { num: 2, selectors: ['input[placeholder*="ค้นหา"]'] },
      { num: 3, selectors: ['a[href*="/room/"]:not([href="/home"])'] }
    ]
  },
  {
    filename: 'manual_08_join_room_modal.png',
    url: 'http://localhost:8080/home',
    token: studentToken,
    expectedCount: 2,
    prepare: async (page) => {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('เข้าร่วมห้องเรียน'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { num: 1, selectors: ['input[placeholder*="CS101"]', 'div[role="dialog"] input'] },
      { num: 2, selectors: ['div[role="dialog"] button[type="submit"]'], textMatches: ['เข้าร่วม'] }
    ]
  },
  {
    filename: 'manual_09_room_stream.png',
    url: 'http://localhost:8080/room/30001',
    token: teacherToken,
    expectedCount: 5,
    annotations: [
      { num: 1, textMatches: ['สมาชิกในห้อง'], selectors: ['button:has-text("สมาชิกในห้อง")'] },
      { num: 2, textMatches: ['คัดลอก'], selectors: ['button:has-text("คัดลอก")'] },
      { num: 3, textMatches: ['ประกาศบางอย่างให้ชั้นเรียน'], selectors: ['button:has-text("ประกาศบางอย่าง")'] },
      { num: 4, textMatches: ['มอบหมายข้อสอบ'], selectors: ['button:has-text("มอบหมายข้อสอบ")'] },
      { num: 5, textMatches: ['ตรวจงาน', 'ดูข้อสอบ'], selectors: ['button:has-text("ตรวจงาน")', 'button:has-text("ดูข้อสอบ")'] }
    ]
  },
  {
    filename: 'manual_10_room_members.png',
    url: 'http://localhost:8080/room/30001',
    token: teacherToken,
    expectedCount: 2,
    prepare: async (page) => {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes('สมาชิกในห้อง'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 800));
    },
    annotations: [
      { num: 1, selectors: ['div:has(> input[placeholder*="ค้นหาชื่อ"])', 'input[placeholder*="ค้นหาชื่อ"]', 'div[role="dialog"]'] },
      { num: 2, selectors: ['div[role="dialog"] ul', 'div[role="dialog"] table', 'div[role="dialog"] .space-y-3', 'input[placeholder*="ค้นหาชื่อ"]'] }
    ]
  },
  {
    filename: 'manual_11_create_exam_top.png',
    url: 'http://localhost:8080/room/30001/create-exam',
    token: teacherToken,
    expectedCount: 5,
    annotations: [
      { num: 1, selectors: ['input[placeholder*="ชื่อข้อสอบ"]'] },
      { num: 2, selectors: ['input[placeholder*="คำชี้แจงข้อสอบ"]', 'textarea[placeholder*="คำชี้แจง"]'] },
      { num: 3, selectors: ['input[type="datetime-local"]:first-of-type', 'input[type="datetime-local"]'] },
      { num: 4, selectors: ['input[type="datetime-local"]:nth-of-type(2)', 'div:has(> input[type="datetime-local"]) + div input'] },
      { num: 5, selectors: ['button[role="switch"]', 'button.peer', 'label:has(button[role="switch"])'] }
    ]
  },
  {
    filename: 'manual_12_create_exam_rubric.png',
    url: 'http://localhost:8080/room/30001/create-exam',
    token: teacherToken,
    expectedCount: 6,
    prepare: async (page) => {
      await page.evaluate(() => {
        const toggle = Array.from(document.querySelectorAll('button, div, span')).find(el => el.innerText.includes('แนวคำตอบและเกณฑ์คะแนน'));
        if (toggle) toggle.click();
        window.scrollBy(0, 450);
      });
      await new Promise(r => setTimeout(r, 700));
    },
    annotations: [
      { num: 1, selectors: ['textarea[placeholder*="โจทย์คำถาม"]', 'input[placeholder*="โจทย์คำถาม"]', 'textarea'] },
      { num: 2, selectors: ['input[type="number"]', 'input[placeholder*="คะแนนเต็ม"]'] },
      { num: 3, textMatches: ['แนบรูป'], selectors: ['button:has-text("แนบรูป")'] },
      { num: 4, textMatches: ['สร้างเกณฑ์ด้วย AI'], selectors: ['button:has-text("สร้างเกณฑ์ด้วย AI")'] },
      { num: 5, textMatches: ['เผยแพร่'], selectors: ['button:has-text("เผยแพร่")'] },
      { num: 6, textMatches: ['บันทึกร่าง'], selectors: ['button:has-text("บันทึกร่าง")'] }
    ]
  },
  {
    filename: 'manual_13_student_exam_submit.png',
    url: 'http://localhost:8080/room/30001/exam/30001/submit',
    token: studentToken,
    expectedCount: 4,
    prepare: async (page) => {
      await page.waitForSelector('.exam-paper, .question-section, textarea', { timeout: 15000 });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { num: 1, textMatches: ['คำตอบของคุณ (พิมพ์ข้อความ)'], selectors: ['label:has-text("พิมพ์ข้อความ")', '.space-y-2 > label'] },
      { num: 2, selectors: ['.attachment-button', 'label:has-text("แนบรูปภาพ")'], textMatches: ['แนบรูปภาพ (ภาพถ่ายกระดาษคำตอบ/ลายมือ)'] },
      { num: 3, selectors: ['textarea', 'textarea[placeholder*="พิมพ์คำตอบ"]'] },
      { num: 4, selectors: ['button[type="submit"]'], textMatches: ['ส่งคำตอบ'] }
    ]
  },
  {
    filename: 'manual_14_teacher_review_list.png',
    url: 'http://localhost:8080/room/30001/exam/30001/review',
    token: teacherToken,
    expectedCount: 4,
    prepare: async (page) => {
      await new Promise(r => setTimeout(r, 1500));
    },
    annotations: [
      { num: 1, textMatches: ['ส่งออก Excel', 'อัปเดตสถานะ', 'AI มั่นใจ'], selectors: ['button:has-text("ส่งออก Excel")', 'button:has-text("อัปเดตสถานะ")'] },
      { num: 2, textMatches: ['รอตรวจ'], selectors: ['button:has-text("รอตรวจ")'] },
      { num: 3, textMatches: ['อนุมัติแล้ว'], selectors: ['button:has-text("อนุมัติแล้ว")'] },
      { num: 4, textMatches: ['ยังไม่ส่ง', 'เลือกคนที่พร้อมอนุมัติ', 'ดูทั้งหมด'], selectors: ['button:has-text("ยังไม่ส่ง")', 'input[placeholder*="ค้นหาชื่อ"]'] }
    ]
  },
  {
    filename: 'manual_15_student_grading_detail.png',
    url: 'http://localhost:8080/room/30001/exam/120001/grading/30001',
    token: teacherToken,
    expectedCount: 5,
    prepare: async (page) => {
      await new Promise(r => setTimeout(r, 1500));
    },
    annotations: [
      { num: 1, selectors: ['.bg-white.dark\\:bg-\\[\\#1E1E1E\\], .rounded-xl, .document-page > div'], textMatches: ['คำตอบ'] },
      { num: 2, selectors: ['div:has(> input[value="10"])', '.bg-card', '.rounded-lg'], textMatches: ['คะแนน'] },
      { num: 3, selectors: ['textarea[placeholder*="พิมพ์คำแนะนำ"]', 'textarea'] },
      { num: 4, selectors: ['input[type="number"]', 'input[value="10"]'] },
      { num: 5, selectors: ['button:has-text("อนุมัติและประกาศผล")', 'button:has-text("อนุมัติ")'], textMatches: ['อนุมัติและประกาศผล'] }
    ]
  },
  {
    filename: 'manual_16_room_analytics.png',
    url: 'http://localhost:8080/room/30001/analytics',
    token: teacherToken,
    expectedCount: 3,
    prepare: async (page) => {
      await new Promise(r => setTimeout(r, 1500));
    },
    annotations: [
      { num: 1, selectors: ['.grid.grid-cols-2, .grid.grid-cols-4, div:has(> .rounded-xl)', '.stat-card'], textMatches: ['ภาพรวม', 'สรุป'] },
      { num: 2, selectors: ['div.rounded-xl.border', 'svg', '.recharts-wrapper', 'div:has(> canvas)'], textMatches: ['การกระจาย', 'สถิติ'] },
      { num: 3, selectors: ['button:has-text("ดาวน์โหลด CSV")', 'button:has-text("CSV")'], textMatches: ['ดาวน์โหลด CSV', 'CSV'] }
    ]
  },
  {
    filename: 'manual_17_student_history.png',
    url: 'http://localhost:8080/history',
    token: studentToken,
    expectedCount: 2,
    prepare: async (page) => {
      await new Promise(r => setTimeout(r, 1500));
    },
    annotations: [
      { num: 1, selectors: ['input[placeholder*="ค้นหาชื่อข้อสอบ"]', 'div.space-y-4', 'a[href*="/exam/"]'], textMatches: ['ค้นหา'] },
      { num: 2, selectors: ['button:has-text("ดูรายละเอียด")', 'button:has-text("ทั้งหมด")'], textMatches: ['ดูรายละเอียด'] }
    ]
  },
  {
    filename: 'manual_18_notifications_and_menu.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    expectedCount: 4,
    prepare: async (page) => {
      await new Promise(r => setTimeout(r, 1000));
    },
    annotations: [
      { num: 1, selectors: ['button:has(svg.lucide-bell)', 'header button:nth-of-type(1)'] },
      { num: 2, selectors: ['input[placeholder*="ค้นหา"]', 'header'] },
      { num: 3, selectors: ['button:has(svg.lucide-sun), button:has(svg.lucide-moon)', 'button:has-text("สลับธีม")'], textMatches: ['สลับธีม'] },
      { num: 4, selectors: ['header div.flex.items-center:last-child', 'header a[href="/profile"]', 'a[href="/profile"]'], textMatches: ['โปรไฟล์'] }
    ]
  }
];

async function run() {
  console.log('Starting screenshot generation with 100% badge validation...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,850'],
    defaultViewport: { width: 1280, height: 850, deviceScaleFactor: 2 }
  });

  const page = await browser.newPage();

  let totalBadgesChecked = 0;
  let totalBadgesSucceeded = 0;

  for (const step of steps) {
    console.log(`\n========================================`);
    console.log(`Generating: ${step.filename} (Expected badges: ${step.expectedCount})`);

    // Ensure origin localStorage token is correctly set
    await page.goto('http://localhost:8080/', { waitUntil: 'domcontentloaded' });
    await page.evaluate((tok) => {
      if (tok) localStorage.setItem('token', tok);
      else localStorage.removeItem('token');
    }, step.token);

    await page.goto(step.url, { waitUntil: 'domcontentloaded' });
    await new Promise(r => setTimeout(r, 1500));
    await page.waitForFunction(() => !document.querySelector('.animate-pulse'), { timeout: 8000 }).catch(() => {});

    if (step.prepare) {
      await step.prepare(page);
    }

    // Annotate and return diagnostics
    const results = await page.evaluate((annList) => {
      const logs = [];

      annList.forEach(({ num, selectors, textMatches }) => {
        let target = null;

        // Try selectors first
        if (selectors && selectors.length) {
          for (const sel of selectors) {
            try {
              if (sel.includes(':has-text(')) {
                const match = sel.match(/^(.*?):has-text\("(.*?)"\)$/);
                if (match) {
                  const [_, baseSel, txt] = match;
                  const els = Array.from(document.querySelectorAll(baseSel || '*'));
                  target = els.find(el => el.innerText.trim().includes(txt));
                  if (target) break;
                }
              } else {
                target = document.querySelector(sel);
                if (target) break;
              }
            } catch (e) {}
          }
        }

        // Try text matches
        if (!target && textMatches && textMatches.length) {
          const allEls = Array.from(document.querySelectorAll('button, a, input, textarea, div, span, p, label, th, td, h1, h2, h3'));
          for (const txt of textMatches) {
            target = allEls.find(el => el.children.length === 0 && el.innerText.trim().includes(txt)) ||
                     allEls.find(el => el.innerText.trim().includes(txt));
            if (target) break;
          }
        }

        if (target) {
          const rect = target.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0) {
            // Draw annotation box + badge
            const box = document.createElement('div');
            box.className = 'manual-annotation-box';
            box.style.position = 'absolute';
            box.style.left = `${rect.left + window.scrollX - 4}px`;
            box.style.top = `${rect.top + window.scrollY - 4}px`;
            box.style.width = `${rect.width + 8}px`;
            box.style.height = `${rect.height + 8}px`;
            box.style.border = '3px solid #ef4444';
            box.style.borderRadius = '8px';
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

            logs.push({ num, success: true, rect: { x: Math.round(rect.left), y: Math.round(rect.top), w: Math.round(rect.width), h: Math.round(rect.height) } });
            return;
          }
        }

        logs.push({ num, success: false, reason: target ? 'zero-dimension' : 'not-found' });
      });

      return logs;
    }, step.annotations);

    console.log('Annotation results:');
    let stepSuccess = true;
    for (const res of results) {
      totalBadgesChecked++;
      if (res.success) {
        totalBadgesSucceeded++;
        console.log(`  Badge [${res.num}]: OK (x=${res.rect.x}, y=${res.rect.y}, w=${res.rect.w}, h=${res.rect.h})`);
      } else {
        stepSuccess = false;
        console.error(`  Badge [${res.num}]: FAILED (${res.reason})`);
      }
    }

    if (!stepSuccess) {
      console.warn(`WARNING: Some badges failed on ${step.filename}`);
    } else {
      console.log(`All ${step.expectedCount} badges successfully placed!`);
    }

    await new Promise(r => setTimeout(r, 400));
    const targetFile = path.join(outDir, step.filename);
    await page.screenshot({ path: targetFile, fullPage: false });
    console.log(`Saved screenshot: ${step.filename} (${fs.statSync(targetFile).size} bytes)`);

    // Clean up
    await page.evaluate(() => {
      document.querySelectorAll('.manual-annotation-box').forEach(el => el.remove());
    });
  }

  await browser.close();
  console.log(`\n========================================`);
  console.log(`Finished: ${totalBadgesSucceeded} / ${totalBadgesChecked} badges placed across 18 screenshots.`);
}

run().catch(e => {
  console.error('Fatal error in generator:', e);
});
