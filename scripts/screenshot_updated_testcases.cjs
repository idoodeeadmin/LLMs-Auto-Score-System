const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 1400 });

    const filePath = 'file://' + path.resolve(__dirname, '../docs_and_tests/chapter4_testcases.html').replace(/\\/g, '/');
    await page.goto(filePath, { waitUntil: 'networkidle0' });

    const outDir = path.resolve(__dirname, '../public/screenshots');

    // 1. Screenshot of Text cases
    await page.evaluate(() => {
        const el = document.getElementById('evaluation-examples');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 400));
    await page.screenshot({ path: path.join(outDir, 'case_studies_text.png') });

    // 2. Screenshot of Vision cases
    await page.evaluate(() => {
        const headers = Array.from(document.querySelectorAll('h4'));
        const visionH4 = headers.find(h => h.textContent.includes('กลุ่มข้อสอบอัตนัยแบบรูปภาพ'));
        if (visionH4) visionH4.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 400));
    await page.screenshot({ path: path.join(outDir, 'case_studies_vision.png') });

    console.log('Screenshots saved: case_studies_text.png, case_studies_vision.png');
    await browser.close();
})();
