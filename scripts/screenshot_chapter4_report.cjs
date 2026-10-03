const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 1200 });

    const filePath = 'file://' + path.resolve(__dirname, '../public/chapter4_complete_report.html').replace(/\\/g, '/');
    await page.goto(filePath, { waitUntil: 'networkidle0' });

    const outDir = path.resolve(__dirname, '../public/screenshots');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    // Screenshot 1: Header, Dataset, and Stat Grid
    await page.screenshot({ path: path.join(outDir, 'chapter4_report_top_benchmark.png') });
    console.log('Saved top screenshot.');

    // Screenshot 2: Scroll to Qualitative Case Studies
    await page.evaluate(() => {
        const el = document.querySelector('.case-card');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 400));
    await page.screenshot({ path: path.join(outDir, 'chapter4_report_case_studies.png') });
    console.log('Saved case studies screenshot.');

    await browser.close();
})();
