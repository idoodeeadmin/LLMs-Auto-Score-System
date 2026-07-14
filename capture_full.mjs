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

  try {
    console.log('Going to login page...');
    await page.goto('http://localhost:8080/', { waitUntil: 'networkidle0', timeout: 20000 });
    
    console.log('Filling login form...');
    // Type email
    await page.type('input[type="text"]', 'test_bot@evaly.com');
    // Type password
    await page.type('input[type="password"]', 'password123');
    
    console.log('Submitting login form...');
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 }),
      page.click('button[type="submit"]')
    ]);

    console.log('Logged in successfully. Capturing Dashboard...');
    // Give it a bit more time for any API calls to finish rendering
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: path.join(screenshotsDir, 'dashboard.png') });
    console.log('Saved dashboard.png');
    
    console.log('Going to Profile...');
    await page.goto('http://localhost:8080/profile', { waitUntil: 'networkidle0', timeout: 20000 });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(screenshotsDir, 'profile.png') });
    console.log('Saved profile.png');

  } catch (e) {
    console.error('Error during capture:', e);
  }

  console.log('Closing browser...');
  await browser.close();
  process.exit(0);
})();
