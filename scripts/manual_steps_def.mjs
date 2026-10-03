export const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowLCJleHAiOjE3OTE0NzQ2NTl9.yC-M7ahrK16bmmR857qZbnulzDC7BLQ3AiTegUSISJw';
export const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsInRva2VuX3ZlcnNpb24iOjAsImV4cCI6MTc5MTQ3NDY1OX0.NVFfH5jqcdY2VDKGmzob81Gfk9gUpiXKcMBrc02mkY0';

export const manualSteps = [
  {
    filename: 'manual_01_login.png',
    url: 'http://localhost:8080/',
    token: null,
    annotations: [
      { selector: 'input[placeholder*="email"], input[placeholder*="student"]', num: 1 },
      { selector: 'input[type="password"]', num: 2 },
      { selector: 'button[type="submit"]', num: 3 },
      { textMatch: 'Google', num: 4 },
      { textMatch: 'ลืมรหัสผ่าน', num: 5 },
      { textMatch: 'สร้างบัญชี', num: 6 }
    ]
  },
  {
    filename: 'manual_02_register.png',
    url: 'http://localhost:8080/register',
    token: null,
    annotations: [
      { selector: 'input#register-name', num: 1 },
      { selector: 'input#register-email', num: 2 },
      { selector: 'input#register-password', num: 3 },
      { selector: 'input#register-confirm-password', num: 4 },
      { selector: 'button[type="submit"]', num: 5 },
      { textMatch: 'กลับไปเข้าสู่ระบบ', selector: 'a[href="/"]', num: 6 }
    ]
  },
  {
    filename: 'manual_03_forgot_password.png',
    url: 'http://localhost:8080/forgot-password',
    token: null,
    annotations: [
      { selector: 'input#recovery-email', num: 1 },
      { selector: 'button[type="submit"]', num: 2 },
      { textMatch: 'กลับไปเข้าสู่ระบบ', selector: 'a[href="/"]', num: 3 }
    ]
  },
  {
    filename: 'manual_04_profile.png',
    url: 'http://localhost:8080/profile',
    token: teacherToken,
    annotations: [
      { selector: 'label[for="avatar-upload"]', num: 1 },
      { selector: 'input#profile-name', num: 2 },
      { selector: 'input#profile-identity', num: 3 },
      { selector: 'input#profile-password', num: 4 },
      { selector: 'button[type="submit"]', textMatch: 'บันทึกการเปลี่ยนแปลง', num: 5 }
    ]
  },
  {
    filename: 'manual_05_teacher_dashboard.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    annotations: [
      { selector: '.room-create-button', textMatch: 'สร้างห้องเรียน', num: 1 },
      { selector: 'input[placeholder*="ค้นหา"]', num: 2 },
      { selector: '.room-card p.font-mono, p.font-mono', textMatch: 'JS1BLV', num: 3 },
      { selector: 'a[href*="/room/"]', num: 4 }
    ]
  },
  {
    filename: 'manual_06_create_room_modal.png',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    beforeAnnotate: async (page) => {
      await page.evaluate(() => {
        const btn = document.querySelector('.room-create-button') || Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('สร้างห้องเรียน'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { selector: 'input[placeholder*="เช่น โครงสร้างข้อมูล"]', num: 1 },
      { selector: 'input[placeholder*="Sec 1"]', num: 2 },
      { selector: '.room-form button[type="submit"]', textMatch: 'บันทึกห้องเรียน', num: 3 }
    ]
  },
  {
    filename: 'manual_07_student_dashboard.png',
    url: 'http://localhost:8080/home',
    token: studentToken,
    annotations: [
      { selector: '.room-create-button', textMatch: 'เข้าร่วมห้องเรียน', num: 1 },
      { selector: 'input[placeholder*="ค้นหา"]', num: 2 },
      { selector: 'a[href*="/room/"]', num: 3 }
    ]
  },
  {
    filename: 'manual_08_join_room_modal.png',
    url: 'http://localhost:8080/home',
    token: studentToken,
    beforeAnnotate: async (page) => {
      await page.evaluate(() => {
        const btn = document.querySelector('.room-create-button') || Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('เข้าร่วมห้องเรียน'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { selector: 'input[placeholder*="CS101-8849"]', num: 1 },
      { selector: '.room-form button[type="submit"]', textMatch: 'เข้าร่วมห้องเรียน', num: 2 }
    ]
  },
  {
    filename: 'manual_09_room_stream.png',
    url: 'http://localhost:8080/room/30001',
    token: teacherToken,
    annotations: [
      { textMatch: 'สมาชิกในห้อง', selector: 'aside button:has-text("สมาชิกในห้อง")', num: 1 },
      { textMatch: 'รหัสชั้นเรียน', num: 2 },
      { textMatch: 'ประกาศบางอย่างให้ชั้นเรียน…', selector: 'button:has-text("ประกาศ")', num: 3 },
      { textMatch: 'มอบหมายข้อสอบ', selector: 'button:has-text("มอบหมายข้อสอบ")', num: 4 },
      { selector: 'button:has-text("ตรวจงาน"), a[href*="/exam/"], .rounded-xl:has-text("ตรวจงาน")', textMatch: 'ตรวจงาน', num: 5 }
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
      { selector: 'input[placeholder*="คำชี้แจงข้อสอบ"]', num: 2 },
      { selector: 'input[type="datetime-local"]:first-of-type', num: 3 },
      { selector: 'input[type="datetime-local"]:nth-of-type(2)', num: 4 },
      { selector: 'button[role="switch"]', textMatch: 'สุ่มลำดับข้อ', num: 5 }
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
        window.scrollBy(0, 350);
      });
      await new Promise(r => setTimeout(r, 600));
    },
    annotations: [
      { selector: 'textarea[placeholder*="พิมพ์โจทย์คำถาม"]', num: 1 },
      { selector: 'input[type="number"][aria-label*="คะแนน"]', num: 2 },
      { selector: 'label:has(input[type="file"])', textMatch: 'แนบรูป', num: 3 },
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
      { textMatch: 'พิมพ์ข้อความ', selector: 'button:has-text("พิมพ์ข้อความ"), button:has-text("พิมพ์คำตอบ")', num: 1 },
      { textMatch: 'แนบรูปภาพ', selector: 'button:has-text("แนบรูปภาพ"), button:has-text("อัปโหลดรูปภาพ")', num: 2 },
      { selector: 'textarea, input[type="file"]', num: 3 },
      { textMatch: 'ส่งคำตอบ', selector: 'button:has-text("ส่ง")', num: 4 }
    ]
  },
  {
    filename: 'manual_14_teacher_review_list.png',
    url: 'http://localhost:8080/room/30001/exam/30001/review',
    token: teacherToken,
    annotations: [
      { textMatch: 'ตรวจคำตอบด้วย AI', selector: 'button:has-text("ตรวจคำตอบด้วย AI"), button:has-text("ตรวจด้วย AI")', num: 1 },
      { textMatch: 'ส่งแล้ว', selector: 'button:has-text("ส่งแล้ว")', num: 2 },
      { textMatch: 'อนุมัติแล้ว', selector: 'button:has-text("อนุมัติแล้ว")', num: 3 },
      { textMatch: 'ตรวจทาน', selector: 'a:has-text("ตรวจทาน"), button:has-text("ตรวจทาน"), button:has-text("ตรวจ")', num: 4 }
    ]
  },
  {
    filename: 'manual_15_student_grading_detail.png',
    url: 'http://localhost:8080/room/30001/exam/120001/grading/30001',
    token: teacherToken,
    annotations: [
      { selector: '.answer-card, .student-answer, div:has(> img), [class*="answer"]', textMatch: 'คำตอบ', num: 1 },
      { textMatch: 'คะแนน AI', selector: '[class*="score"], .badge', num: 2 },
      { textMatch: 'ข้อเสนอแนะ', num: 3 },
      { selector: 'input[type="number"]', num: 4 },
      { textMatch: 'อนุมัติผลคะแนน', selector: 'button:has-text("อนุมัติ")', num: 5 }
    ]
  },
  {
    filename: 'manual_16_room_analytics.png',
    url: 'http://localhost:8080/room/30001/analytics',
    token: teacherToken,
    annotations: [
      { textMatch: 'ภาพรวม', selector: 'h1, h2, .font-semibold', num: 1 },
      { textMatch: 'คะแนนเฉลี่ย', selector: 'div:has-text("คะแนนเฉลี่ย")', num: 2 },
      { textMatch: 'ส่งออก', selector: 'button:has-text("ส่งออก"), button:has-text("Export")', num: 3 }
    ]
  },
  {
    filename: 'manual_17_student_history.png',
    url: 'http://localhost:8080/history',
    token: studentToken,
    annotations: [
      { textMatch: 'ประวัติ', selector: 'h1, h2, .font-semibold', num: 1 },
      { selector: '.rounded-xl, .border, a[href*="/exam/"]', textMatch: 'คะแนน', num: 2 }
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
      { selector: 'button:has(img[alt*="avatar"]), button:has(span[class*="avatar"]), button.group', num: 4 }
    ]
  }
];
