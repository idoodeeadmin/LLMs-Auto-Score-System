const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 1600 });
  
  const filePath = 'file:///' + path.resolve(__dirname, '../docs_and_tests/chapter4_testcases.html').replace(/\\/g, '/');
  console.log('Navigating to:', filePath);
  await page.goto(filePath, { waitUntil: 'networkidle0' });

  // Capture the top sections including 4.1.3
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

  await browser.close();
  console.log('Finished capturing all previews!');
})();
