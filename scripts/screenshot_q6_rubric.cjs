const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 1000 });

    const filePath = 'file://' + path.resolve(__dirname, '../public/dataset_viewer.html').replace(/\\/g, '/');
    await page.goto(filePath, { waitUntil: 'networkidle0' });

    // Click tab 3 (Exam_Rubrics)
    const tabs = await page.$$('.tab-btn');
    if (tabs.length >= 3) {
        await tabs[2].click();
        await new Promise(r => setTimeout(r, 600));
    }

    // Scroll to bottom
    await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
    });

    await new Promise(r => setTimeout(r, 500));

    const outDir = path.resolve(__dirname, '../public/screenshots');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const outPath = path.join(outDir, 'q6_exam_rubric_binary.png');
    await page.screenshot({ path: outPath });
    console.log('Saved screenshot to:', outPath);

    await browser.close();
})();
