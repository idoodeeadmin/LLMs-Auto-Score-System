const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 1600 });
  
  const filePath = 'file://' + path.resolve(__dirname, '../docs_and_tests/chapter4_testcases.html').replace(/\\/g, '/');
  console.log('Navigating to:', filePath);
  await page.goto(filePath, { waitUntil: 'networkidle0' });

  // Capture the top sections including 4.1.1, 4.1.2, 4.1.3
  const sectionGoogle = await page.$('#test-google-login');
  if (sectionGoogle) {
    await sectionGoogle.screenshot({ path: path.resolve(__dirname, '../public/screenshots/test_google_login_preview.png') });
    console.log('Captured test_google_login_preview.png');
  }

  // Capture 4.1.4 forgot password
  const sectionForgot = await page.$('#test-forgot-password');
  if (sectionForgot) {
    await sectionForgot.screenshot({ path: path.resolve(__dirname, '../public/screenshots/test_forgot_password_preview.png') });
    console.log('Captured test_forgot_password_preview.png');
  }

  // Capture 4.1.5 reset and verify
  const sectionReset = await page.$('#test-reset-and-verify');
  if (sectionReset) {
    await sectionReset.screenshot({ path: path.resolve(__dirname, '../public/screenshots/test_reset_and_verify_preview.png') });
    console.log('Captured test_reset_and_verify_preview.png');
  }

  // Also capture overview of document
  await page.screenshot({
    path: path.resolve(__dirname, '../public/screenshots/test_chapter4_overview.png'),
    clip: { x: 150, y: 350, width: 900, height: 1200 }
  });
  console.log('Captured test_chapter4_overview.png');

  await browser.close();
})();
