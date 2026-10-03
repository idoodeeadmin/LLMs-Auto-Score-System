import puppeteer from 'puppeteer';

const studentToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkQGQuYyIsInRva2VuX3ZlcnNpb24iOjAsImV4cCI6MTc5MTQ3NDY1OX0.NVFfH5jqcdY2VDKGmzob81Gfk9gUpiXKcMBrc02mkY0';

async function test() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:8080/', { waitUntil: 'domcontentloaded' });
  await page.evaluate((tok) => localStorage.setItem('token', tok), studentToken);
  await page.goto('http://localhost:8080/room/30001/exam/30001/submit', { waitUntil: 'domcontentloaded' });

  // Wait for the exam form to load
  await page.waitForSelector('.exam-paper, .question-section', { timeout: 15000 });
  console.log('Exam form loaded successfully!');

  const elements = await page.evaluate(() => {
    return {
      textareas: document.querySelectorAll('textarea').length,
      buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean),
      labels: Array.from(document.querySelectorAll('label')).map(l => l.innerText.trim()).filter(Boolean)
    };
  });
  console.log('Elements found:', elements);
  await browser.close();
}

test().catch(e => console.error('Test error:', e.message));
