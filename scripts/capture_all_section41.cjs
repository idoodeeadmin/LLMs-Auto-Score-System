const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1600 });

  const filePath = 'file:///' + path.resolve(__dirname, '../public/chapter4_testcases.html').replace(/\\/g, '/');
  console.log('Navigating to:', filePath);
  await page.goto(filePath, { waitUntil: 'networkidle0', timeout: 60000 });

  // Wait for MathJax rendering
  await new Promise(r => setTimeout(r, 2000));

  // Capture segments by scrolling down
  // Segment 1: Preprocessing pipeline and metrics (around y = 1400 to 3000)
  await page.evaluate(() => window.scrollTo(0, 1350));
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({
    path: path.resolve(__dirname, '../public/screenshots/section41_page2_pipeline_metrics.png')
  });
  console.log('Captured section41_page2_pipeline_metrics.png');

  // Segment 2: Calculation table & Confusion matrix (around y = 2800)
  await page.evaluate(() => window.scrollTo(0, 2750));
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({
    path: path.resolve(__dirname, '../public/screenshots/section41_page3_calc_and_confusion.png')
  });
  console.log('Captured section41_page3_calc_and_confusion.png');

  // Segment 3: Prediction samples Q1-Q4 (around y = 4300)
  await page.evaluate(() => window.scrollTo(0, 4200));
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({
    path: path.resolve(__dirname, '../public/screenshots/section41_page4_predictions_q1_q4.png')
  });
  console.log('Captured section41_page4_predictions_q1_q4.png');

  // Segment 4: Prediction samples Q5-Q6 (around y = 5700)
  await page.evaluate(() => window.scrollTo(0, 5650));
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({
    path: path.resolve(__dirname, '../public/screenshots/section41_page5_predictions_q5_q6.png')
  });
  console.log('Captured section41_page5_predictions_q5_q6.png');

  // Segment 5: Case studies 4.1.6 (around y = 7100)
  await page.evaluate(() => window.scrollTo(0, 7100));
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({
    path: path.resolve(__dirname, '../public/screenshots/section41_page6_case_studies.png')
  });
  console.log('Captured section41_page6_case_studies.png');

  await browser.close();
  console.log('All segmented screenshots captured!');
})();
