import puppeteer from 'puppeteer';

const teacherToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpZG9vZGVlMDA3NkBnbWFpbC5jb20iLCJpZCI6MSwicm9sZSI6InRlYWNoZXIiLCJleHAiOjE3OTE0NzA0NTJ9.TakALaVVZodWpV6fM87kJugPnYXJiOIoDeo2iGCZ_L8';
const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsImlkIjoyLCJyb2xlIjoic3R1ZGVudCIsImV4cCI6MTc5MTQ3MDQ2OH0.nPZ2WH0zkwE3vgkKl4uUFeIh6Ch9qgQ5IuYi9U4PXYM';

async function checkPage(name, url, token, actions = null) {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  if (token) {
    await page.evaluateOnNewDocument(t => localStorage.setItem('token', t), token);
  } else {
    await page.evaluateOnNewDocument(() => localStorage.removeItem('token'));
  }
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 1500));
  if (actions) await actions(page);
  
  const info = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('input, textarea, button, select')).map(el => ({
      tag: el.tagName.toLowerCase(),
      type: el.type,
      placeholder: el.placeholder,
      text: el.innerText ? el.innerText.trim() : '',
      className: el.className
    }));
    return { title: document.title, inputs: inputs.slice(0, 30) };
  });
  console.log(`=== ${name} (${url}) ===`);
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
}

async function run() {
  await checkPage('Step 11 Create Exam', 'http://localhost:8080/room/30001/create-exam', teacherToken);
}

run();
