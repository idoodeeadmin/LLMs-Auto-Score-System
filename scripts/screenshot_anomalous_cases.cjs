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

    const outDir = path.resolve(__dirname, '../public/screenshots/case_studies');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const sectionEl = await page.$('#anomalous-grading-analysis');
    if (sectionEl) {
        const outSection = path.join(outDir, 'verified_anomalous_section.png');
        await sectionEl.screenshot({ path: outSection });
        console.log(`Saved whole section screenshot: ${outSection}`);
    }

    const tables = await page.$$('#anomalous-grading-analysis .table-block');
    console.log(`Found ${tables.length} anomalous table blocks`);

    for (let i = 0; i < tables.length; i++) {
        const outPath = path.join(outDir, `verified_anomaly_case_${i + 1}.png`);
        await tables[i].screenshot({ path: outPath });
        console.log(`Saved table screenshot: ${outPath}`);
    }

    await browser.close();
})();
