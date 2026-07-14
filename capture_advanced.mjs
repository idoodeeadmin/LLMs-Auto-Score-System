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
    console.log('Logged in!');

    await new Promise(r => setTimeout(r, 2000));
    
    const roomId = '240001';
    const examId = '240001';
    
    // Capture Room Detail
    console.log(`Going to Room Detail ${roomId}...`);
    try {
      await page.goto(`http://localhost:8080/room/${roomId}`, { waitUntil: 'load', timeout: 10000 });
    } catch(e) {}
    await new Promise(r => setTimeout(r, 3000));
    await page.screenshot({ path: path.join(screenshotsDir, 'room-detail.png') });
    console.log('Saved room-detail.png');

    // Capture Create Exam
    console.log(`Going to Create Exam...`);
    try {
      await page.goto(`http://localhost:8080/room/${roomId}/create-exam`, { waitUntil: 'load', timeout: 10000 });
    } catch(e) {}
    await new Promise(r => setTimeout(r, 3000));
    await page.screenshot({ path: path.join(screenshotsDir, 'create-exam.png') });
    console.log('Saved create-exam.png');

    // Capture Exam View
    console.log(`Going to Exam View...`);
    try {
      await page.goto(`http://localhost:8080/room/${roomId}/exam/${examId}`, { waitUntil: 'load', timeout: 10000 });
    } catch(e) {}
    await new Promise(r => setTimeout(r, 3000));
    await page.screenshot({ path: path.join(screenshotsDir, 'exam-view.png') });
    console.log('Saved exam-view.png');
    
    // Capture Exam Analytics
    console.log(`Going to Exam Analytics...`);
    try {
      await page.goto(`http://localhost:8080/room/${roomId}/exam/${examId}/analytics`, { waitUntil: 'load', timeout: 10000 });
    } catch(e) {}
    await new Promise(r => setTimeout(r, 3000));
    await page.screenshot({ path: path.join(screenshotsDir, 'exam-analytics.png') });
    console.log('Saved exam-analytics.png');

  } catch (e) {
    console.error('Error during capture:', e);
  }

  console.log('Closing browser...');
  await browser.close();
  process.exit(0);
})();
