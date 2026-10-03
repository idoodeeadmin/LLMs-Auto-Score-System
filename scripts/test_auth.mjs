import puppeteer from 'puppeteer';

const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJpZCI6MSwicm9sZSI6InRlYWNoZXIiLCJleHAiOjE3OTE0NzA0NTJ9.TakALaVVZodWpV6fM87kJugPnYXJiOIoDeo2iGCZ_L8';

async function testAuth() {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

  await page.goto('http://localhost:8080/');
  await page.evaluate((t) => {
    localStorage.setItem('token', t);
  }, teacherToken);

  console.log('Navigating to /home...');
  await page.goto('http://localhost:8080/home', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 2000));

  const html = await page.evaluate(() => document.body.innerText);
  console.log('Body text snippet:', html.slice(0, 300));
  await browser.close();
}

testAuth();
