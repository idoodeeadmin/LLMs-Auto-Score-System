import puppeteer from 'puppeteer';

const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJpZCI6MSwicm9sZSI6InRlYWNoZXIiLCJleHAiOjE3OTE0NzA0NTJ9.TakALaVVZodWpV6fM87kJugPnYXJiOIoDeo2iGCZ_L8';

async function testAnnotatedHome() {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 2 });

  await page.evaluateOnNewDocument((token) => {
    localStorage.setItem('token', token);
  }, teacherToken);

  await page.goto('http://localhost:8080/home', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForFunction(() => !document.querySelector('.animate-pulse') && document.body.innerText.includes('สร้างห้องเรียน'), { timeout: 15000 });

  await page.evaluate(() => {
    const items = [
      { textMatch: 'สร้างห้องเรียน', num: 1, shape: 'rect' },
      { selector: 'input[placeholder*="ค้นหา"]', num: 2, shape: 'rect' },
      { textMatch: 'รหัสห้องเรียน', num: 3, shape: 'rect' },
      { textMatch: 'เปิดห้องเรียน', num: 4, shape: 'rect' },
    ];

    items.forEach(({ textMatch, selector, num, shape }) => {
      let target = null;
      if (selector) {
        target = document.querySelector(selector);
      } else if (textMatch) {
        const all = Array.from(document.querySelectorAll('button, a, div, span, p'));
        target = all.find(el => el.children.length === 0 && el.innerText.trim().includes(textMatch)) ||
                 all.find(el => el.innerText.trim().includes(textMatch));
      }

      if (target) {
        const rect = target.getBoundingClientRect();
        const box = document.createElement('div');
        box.style.position = 'absolute';
        box.style.left = `${rect.left + window.scrollX - 4}px`;
        box.style.top = `${rect.top + window.scrollY - 4}px`;
        box.style.width = `${rect.width + 8}px`;
        box.style.height = `${rect.height + 8}px`;
        box.style.border = '3px solid #ef4444';
        box.style.borderRadius = shape === 'circle' ? '50%' : '8px';
        box.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.8)';
        box.style.pointerEvents = 'none';
        box.style.zIndex = '99999';

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
        badge.style.fontFamily = 'sans-serif';
        badge.innerText = String(num);

        box.appendChild(badge);
        document.body.appendChild(box);
      }
    });
  });

  const outPath = 'docs_and_tests/screenshots/test_home_annotated.png';
  await page.screenshot({ path: outPath });
  console.log(`Saved annotated screenshot to ${outPath}`);
  await browser.close();
}

testAnnotatedHome();
