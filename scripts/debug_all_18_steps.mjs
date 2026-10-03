import puppeteer from 'puppeteer';

const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowLCJleHAiOjE3OTE0NzQ2NTl9.yC-M7ahrK16bmmR857qZbnulzDC7BLQ3AiTegUSISJw';
const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsInRva2VuX3ZlcnNpb24iOjAsImV4cCI6MTc5MTQ3NDY1OX0.NVFfH5jqcdY2VDKGmzob81Gfk9gUpiXKcMBrc02mkY0';

const steps = [
  {
    name: 'Step 04 Profile',
    url: 'http://localhost:8080/profile',
    token: teacherToken
  },
  {
    name: 'Step 05 Teacher Dashboard',
    url: 'http://localhost:8080/home',
    token: teacherToken
  },
  {
    name: 'Step 07 Student Dashboard',
    url: 'http://localhost:8080/home',
    token: studentToken
  },
  {
    name: 'Step 09 Room Stream',
    url: 'http://localhost:8080/room/30001',
    token: teacherToken
  },
  {
    name: 'Step 10 Room Members',
    url: 'http://localhost:8080/room/30001',
    token: teacherToken,
    action: async (page) => {
      await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button, a')).find(b => b.innerText.includes('สมาชิกในห้อง'));
        if (btn) btn.click();
      });
      await new Promise(r => setTimeout(r, 600));
    }
  },
  {
    name: 'Step 13 Student Submit',
    url: 'http://localhost:8080/room/30001/exam/30001/submit',
    token: studentToken
  },
  {
    name: 'Step 14 Teacher Review',
    url: 'http://localhost:8080/room/30001/exam/30001/review',
    token: teacherToken
  },
  {
    name: 'Step 15 Grading Detail',
    url: 'http://localhost:8080/room/30001/exam/120001/grading/30001',
    token: teacherToken
  },
  {
    name: 'Step 16 Room Analytics',
    url: 'http://localhost:8080/room/30001/analytics',
    token: teacherToken
  },
  {
    name: 'Step 17 Student History',
    url: 'http://localhost:8080/history',
    token: studentToken
  },
  {
    name: 'Step 18 Notifications & Menu',
    url: 'http://localhost:8080/home',
    token: teacherToken,
    action: async (page) => {
      await page.evaluate(() => {
        const bell = document.querySelector('button:has(svg.lucide-bell), button svg.lucide-bell');
        if (bell) (bell.closest('button') || bell).click();
      });
      await new Promise(r => setTimeout(r, 600));
    }
  }
];

async function run() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();

  for (const s of steps) {
    console.log(`\n-----------------------------------------`);
    console.log(`Inspecting ${s.name}...`);

    // Ensure origin localStorage is set properly
    await page.goto('http://localhost:8080/', { waitUntil: 'domcontentloaded' });
    await page.evaluate((tok) => {
      if (tok) localStorage.setItem('token', tok);
      else localStorage.removeItem('token');
    }, s.token);

    await page.goto(s.url, { waitUntil: 'domcontentloaded' });
    await new Promise(r => setTimeout(r, 1500));
    await page.waitForFunction(() => !document.querySelector('.animate-pulse'), { timeout: 6000 }).catch(() => {});

    if (s.action) {
      await s.action(page);
    }

    console.log(`Current URL: ${page.url()}`);
    const summary = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
      const inputs = Array.from(document.querySelectorAll('input, textarea')).map(i => ({
        tag: i.tagName.toLowerCase(),
        id: i.id,
        placeholder: i.placeholder,
        val: (i.value || '').slice(0, 15)
      }));
      const links = Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText.trim(), href: a.getAttribute('href') })).filter(a => a.text);
      return {
        btns: btns.slice(0, 12),
        inputs: inputs.slice(0, 8),
        links: links.slice(0, 6)
      };
    });
    console.log('Buttons:', summary.btns);
    console.log('Inputs:', summary.inputs);
    console.log('Links:', summary.links);
  }

  await browser.close();
}

run();
