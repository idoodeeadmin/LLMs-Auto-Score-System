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

    const filePath = 'file://' + path.resolve(__dirname, '../docs_and_tests/chapter4_testcases.html').replace(/\\/g, '/');
    await page.goto(filePath, { waitUntil: 'networkidle0' });

    const outDir = path.resolve(__dirname, '../public/screenshots/case_studies');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    // Capture each of the 6 tables
    const tableBlocks = await page.$$('.table-block');
    console.log(`Found ${tableBlocks.length} table blocks`);

    // The 6 case study tables are the first 6 inside #evaluation-examples
    const caseTables = await page.evaluate(() => {
        const section = document.getElementById('evaluation-examples');
        const blocks = Array.from(section.querySelectorAll('.table-block'));
        return blocks.map((b, i) => {
            const title = b.querySelector('.table-title')?.textContent || `table_${i}`;
            return { index: i, title };
        });
    });

    console.log('Case tables found:', caseTables);

    for (let i = 0; i < caseTables.length; i++) {
        const selector = `#evaluation-examples .table-block:nth-of-type(${i + 1})`;
        const el = await page.$(selector);
        if (el) {
            const outPath = path.join(outDir, `verified_case_${i + 1}.png`);
            await el.screenshot({ path: outPath });
            console.log(`Saved screenshot: ${outPath}`);
        }
    }

    await browser.close();
})();
