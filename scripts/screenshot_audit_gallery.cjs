const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1400, height: 1200 });

    const filePath = 'file://' + path.resolve(__dirname, '../public/audit_gallery_53.html').replace(/\\/g, '/');
    await page.goto(filePath, { waitUntil: 'networkidle0' });

    // Wait 2 seconds for JS loadData
    await new Promise(r => setTimeout(r, 2000));

    const outDir = path.resolve(__dirname, '../public/screenshots');
    const outPath = path.join(outDir, 'audit_gallery_preview.png');
    await page.screenshot({ path: outPath, fullPage: false });
    console.log(`Saved screenshot to ${outPath}`);

    // Click on typo filter to test interactive filtering
    await page.evaluate(() => {
        const btn = document.querySelector('[data-special="typo"]');
        if (btn) btn.click();
    });
    await new Promise(r => setTimeout(r, 1000));

    const outTypoPath = path.join(outDir, 'audit_gallery_typo_filter.png');
    await page.screenshot({ path: outTypoPath, fullPage: false });
    console.log(`Saved typo filter screenshot to ${outTypoPath}`);

    // Click on Q4 filter
    await page.evaluate(() => {
        const btn = document.querySelector('[data-q="4"]');
        if (btn) btn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    const outQ4Path = path.join(outDir, 'audit_gallery_q4_preview.png');
    await page.screenshot({ path: outQ4Path, fullPage: false });
    console.log(`Saved Q4 filter screenshot to ${outQ4Path}`);

    await browser.close();
})();
