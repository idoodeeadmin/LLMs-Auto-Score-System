const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1800 });

  const filePath = 'file:///' + path.resolve(__dirname, '../public/chapter4_testcases.html').replace(/\\/g, '/');
  console.log('Navigating to:', filePath);
  await page.goto(filePath, { waitUntil: 'networkidle0', timeout: 60000 });

  // Wait a moment for MathJax to finish rendering
  await new Promise(r => setTimeout(r, 2500));

  // Take targeted screenshots of key sections of 4.1
  const screenshots = [
    { selector: '#section-4-1', name: 'section41_overview.png', clipHeight: 1400 },
    { selector: '.figure-box', name: 'section41_figures.png' },
    { selector: '#table-4-4', name: 'section41_calc_table.png' },
    { selector: '.conf-matrix-grid', name: 'section41_confusion_matrix.png' },
    { selector: '#section-4-1-5', name: 'section41_prediction_samples.png', clipHeight: 1500 },
    { selector: '#section-4-1-6', name: 'section41_case_studies.png', clipHeight: 1500 }
  ];

  for (const item of screenshots) {
    const el = await page.$(item.selector);
    if (el) {
      if (item.clipHeight) {
        const box = await el.boundingBox();
        if (box) {
          await page.screenshot({
            path: path.resolve(__dirname, `../public/screenshots/${item.name}`),
            clip: {
              x: box.x,
              y: box.y,
              width: box.width,
              height: Math.min(box.height, item.clipHeight)
            }
          });
          console.log(`Captured ${item.name}`);
        }
      } else {
        await el.screenshot({ path: path.resolve(__dirname, `../public/screenshots/${item.name}`) });
        console.log(`Captured ${item.name}`);
      }
    } else {
      console.log(`Element not found for selector: ${item.selector}`);
    }
  }

  // Full page view of the top part of 4.1
  await page.screenshot({
    path: path.resolve(__dirname, '../public/screenshots/section41_top_view.png'),
    clip: { x: 0, y: 0, width: 1280, height: 1800 }
  });
  console.log('Captured section41_top_view.png');

  await browser.close();
  console.log('Screenshot verification completed successfully!');
})();
