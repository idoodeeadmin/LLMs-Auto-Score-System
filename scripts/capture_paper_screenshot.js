import puppeteer from 'puppeteer';

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setViewport({ width: 1400, height: 2200 });
    const fileUrl = 'file:///C:/Users/idood/Downloads/LLMs-Auto-Score-System-main/docs_and_tests/chapter4_testcases.html#research-paper';
    await page.goto(fileUrl, { waitUntil: 'load' });
    
    // Scroll into view of paper-container
    await page.evaluate(() => {
      const el = document.querySelector('.paper-container');
      if (el) el.scrollIntoView();
    });

    await new Promise(r => setTimeout(r, 1000));

    const divEl = await page.$('.paper-divider');
    if (divEl) {
      await divEl.screenshot({ path: 'public/screenshots/verify_paper_divider.png' });
    }
    const element = await page.$('.paper-container');
    if (element) {
      await element.screenshot({ path: 'public/screenshots/verify_research_paper.png' });
      console.log('Successfully captured .paper-container screenshot');
    } else {
      await page.screenshot({ path: 'public/screenshots/verify_research_paper.png', fullPage: false });
      console.log('Captured fallback viewport screenshot');
    }

    await browser.close();
  } catch (err) {
    console.error('Screenshot error:', err);
    process.exit(1);
  }
})();
