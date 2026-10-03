import puppeteer from 'puppeteer';

const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJpZCI6MSwicm9sZSI6InRlYWNoZXIiLCJleHAiOjE3OTE0NzA0NTJ9.TakALaVVZodWpV6fM87kJugPnYXJiOIoDeo2iGCZ_L8';

async function testWait() {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // Pre-seed localStorage before any document loads
  await page.evaluateOnNewDocument((token) => {
    localStorage.setItem('token', token);
  }, teacherToken);

  console.log('Navigating to http://localhost:8080/home...');
  await page.goto('http://localhost:8080/home', { waitUntil: 'networkidle2' });
  
  // Wait for loading skeleton to disappear
  await page.waitForFunction(() => {
    return !document.querySelector('.animate-pulse') && document.body.innerText.includes('ห้องเรียน');
  }, { timeout: 15000 }).catch(e => console.log('Wait timeout:', e.message));

  const text = await page.evaluate(() => document.body.innerText);
  console.log('Page title/text found:', text.slice(0, 200).replace(/\n+/g, ' '));

  await page.screenshot({ path: 'docs_and_tests/screenshots/test_home_ready.png' });
  console.log('Screenshot saved to test_home_ready.png');
  await browser.close();
}

testWait();
