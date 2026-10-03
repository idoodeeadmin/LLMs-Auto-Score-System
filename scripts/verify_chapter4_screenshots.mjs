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
  await page.setViewport({ width: 1200, height: 900 });

  const htmlPath = path.resolve(__dirname, '../public/chapter4_testcases.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  
  // Replace relative image paths to absolute file:// URLs so images load properly
  const publicDir = path.resolve(__dirname, '../public').replace(/\\/g, '/');
  const modifiedHtml = htmlContent.replace(/src="(screenshots\/[^"]+)"/g, `src="file://${publicDir}/$1"`);

  await page.setContent(modifiedHtml, { waitUntil: 'load', timeout: 15000 });
  console.log('Page loaded successfully');

  const tables = await page.$$('table');
  console.log('Found tables count:', tables.length);

  // Capture Table 4.4 and Table 4.5
  for (let i = 0; i < tables.length; i++) {
    const text = await page.evaluate(el => el.innerText, tables[i]);
    if (text.includes('MAE') && text.includes('RMSE') && text.includes('Pearson')) {
      await tables[i].screenshot({ path: path.resolve(__dirname, '../public/screenshots/verify_table_44.png') });
      console.log('Captured Table 4.4');
    }
    if (text.includes('Row-major vs. Column-major') && text.includes('Binary Search Tree')) {
      await tables[i].screenshot({ path: path.resolve(__dirname, '../public/screenshots/verify_table_45.png') });
      console.log('Captured Table 4.5');
    }
  }

  await browser.close();
  console.log('Done!');
}

capture().catch(err => console.error(err));
