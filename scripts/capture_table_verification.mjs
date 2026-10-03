import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function capture() {
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--allow-file-access-from-files']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1100, height: 1200 });

  const htmlPath = path.resolve(__dirname, '../public/chapter4_testcases.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  
  // Replace relative image paths to absolute file:// URLs so images load properly
  const publicDir = path.resolve(__dirname, '../public').replace(/\\/g, '/');
  const modifiedHtml = htmlContent.replace(/src="(screenshots\/[^"]+)"/g, `src="file://${publicDir}/$1"`);

  await page.setContent(modifiedHtml, { waitUntil: 'load', timeout: 30000 });
  console.log('Page loaded successfully');

  // Let's find all .table-block elements and capture the ones for Table 4.21, 4.22, 4.27
  const blocks = await page.$$('.table-block');
  console.log(`Found ${blocks.length} table blocks`);

  let count = 0;
  for (let i = 0; i < blocks.length; i++) {
    const text = await page.evaluate(el => el.innerText, blocks[i]);
    if (text.includes('ตารางที่ 4.21') || text.includes('ตารางที่ 4.22') || text.includes('ตารางที่ 4.27')) {
      const titleLine = text.split('\n')[0].replace(/[/\\?%*:|"<>]/g, '_').trim();
      const outPath = path.resolve(__dirname, `../public/screenshots/verify_block_${i}_${titleLine.substring(0, 30)}.png`);
      await blocks[i].screenshot({ path: outPath });
      console.log(`Saved screenshot: ${outPath} (${titleLine})`);
      count++;
    }
  }

  await browser.close();
  console.log(`Capture completed! Saved ${count} screenshots.`);
}

capture().catch(err => console.error(err));
