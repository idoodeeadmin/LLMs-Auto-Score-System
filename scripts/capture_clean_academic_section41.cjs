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
  await new Promise(r => setTimeout(r, 2000));

  // 1. Overview & Dataset table
  await page.evaluate(() => window.scrollTo(0, 300));
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: path.resolve(__dirname, '../public/screenshots/academic_overview_dataset.png') });
  console.log('Captured academic_overview_dataset.png');

  // 2. Preprocessing pipeline & Table 4.2
  await page.evaluate(() => window.scrollTo(0, 1400));
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: path.resolve(__dirname, '../public/screenshots/academic_pipeline_and_prep.png') });
  console.log('Captured academic_pipeline_and_prep.png');

  // 3. Table 4.4 Step-by-step calculations
  const t44 = await page.$('#table-4-4');
  if (t44) {
    await t44.screenshot({ path: path.resolve(__dirname, '../public/screenshots/academic_table_44_calc.png') });
    console.log('Captured academic_table_44_calc.png');
  }

  // 4. Confusion matrix
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll('.table-title')).find(t => t.textContent.includes('4.7'));
    if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 30);
  });
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: path.resolve(__dirname, '../public/screenshots/academic_confusion_matrix.png') });
  console.log('Captured academic_confusion_matrix.png');

  // 5. Prediction samples Case 1 & Case 2 (DS-001, DS-047)
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll('.table-title')).find(t => t.textContent.includes('4.9'));
    if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 30);
  });
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: path.resolve(__dirname, '../public/screenshots/academic_predictions_ds047.png') });
  console.log('Captured academic_predictions_ds047.png');

  // 6. Prediction samples Case 4 & Case 5 (DS-104, DS-154 clean images)
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll('.table-title')).find(t => t.textContent.includes('4.11'));
    if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 30);
  });
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: path.resolve(__dirname, '../public/screenshots/academic_predictions_clean_img.png') });
  console.log('Captured academic_predictions_clean_img.png');

  // 7. Discrepancy cases (4.1.6)
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll('h3')).find(h => h.textContent.includes('4.1.6'));
    if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 20);
  });
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: path.resolve(__dirname, '../public/screenshots/academic_discrepancies.png') });
  console.log('Captured academic_discrepancies.png');

  await browser.close();
  console.log('All academic screenshots captured!');
})();
