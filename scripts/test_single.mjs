import puppeteer from 'puppeteer';

const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowLCJleHAiOjE3OTE0NzQ2NTl9.yC-M7ahrK16bmmR857qZbnulzDC7BLQ3AiTegUSISJw';

async function testSingle() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox']
  });
  const page = await browser.newPage();
  
  // Set localStorage directly on origin
  await page.goto('http://localhost:8080/', { waitUntil: 'domcontentloaded' });
  await page.evaluate((tok) => {
    localStorage.setItem('token', tok);
  }, teacherToken);

  console.log('Navigating to create-exam...');
  await page.goto('http://localhost:8080/room/30001/create-exam', { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 2000));
  await page.waitForFunction(() => !document.querySelector('.animate-pulse'), { timeout: 10000 }).catch(() => {});

  console.log('Final URL:', page.url());
  const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 300));
  console.log('Body text:\n', bodyText);

  // Test selectors
  const test1 = await page.$('input[placeholder*="ชื่อข้อสอบ"]');
  const test2 = await page.$('input[placeholder*="คำชี้แจงข้อสอบ"]');
  const test3 = await page.$('input[type="datetime-local"]');
  const test5 = await page.$('button[role="switch"]');

  console.log('Selectors:');
  console.log('  #1 ชื่อข้อสอบ:', !!test1);
  console.log('  #2 คำชี้แจง:', !!test2);
  console.log('  #3 datetime:', !!test3);
  console.log('  #5 switch:', !!test5);

  await browser.close();
}

testSingle();
