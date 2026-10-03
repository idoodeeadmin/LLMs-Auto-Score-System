import puppeteer from 'puppeteer';

const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsInRva2VuX3ZlcnNpb24iOjAsImV4cCI6MTc5MTQ3NDY1OX0.NVFfH5jqcdY2VDKGmzob81Gfk9gUpiXKcMBrc02mkY0';

async function check() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('requestfailed', req => console.log('REQ FAIL:', req.url(), req.failure()?.errorText));
  page.on('response', res => {
    if (res.status() >= 400) console.log('HTTP ERR:', res.status(), res.url());
  });

  await page.goto('http://localhost:8080/', { waitUntil: 'domcontentloaded' });
  await page.evaluate((tok) => localStorage.setItem('token', tok), studentToken);
  await page.goto('http://localhost:8080/room/30001/exam/30001/submit', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 3000));
  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log("SUBMIT PAGE TEXT AFTER WAIT:\n" + bodyText.slice(0, 1000));

  
  // Also check if there are other exams in room 30001
  await page.goto('http://localhost:8080/room/30001', { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 2000));
  const roomText = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('a, button')).map(el => ({ text: el.innerText.trim(), href: el.getAttribute('href') })).filter(e => e.text.includes('สอบ') || e.text.includes('ทำ'));
  });
  console.log("ROOM EXAMS:", JSON.stringify(roomText, null, 2));

  await browser.close();
}

check();
