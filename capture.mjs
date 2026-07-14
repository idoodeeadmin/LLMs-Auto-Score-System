import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';

(async () => {
  const screenshotsDir = path.join(process.cwd(), 'public', 'screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  console.log('Launching browser...');
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  const capture = async (url, filename) => {
    console.log(`Capturing ${url}...`);
    try {
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 20000 });
      await new Promise(r => setTimeout(r, 2000));
      await page.screenshot({ path: path.join(screenshotsDir, filename) });
      console.log(`Saved ${filename}`);
    } catch (e) {
      console.log(`Failed to capture ${url}:`, e.message);
    }
  };

  await capture('http://localhost:8080/', 'home.png');
  await capture('http://localhost:8080/register', 'register.png');
  await capture('http://localhost:8080/forgot-password', 'forgot-password.png');

  console.log('Closing browser...');
  await browser.close();
  console.log('Done.');
  process.exit(0);
})();
