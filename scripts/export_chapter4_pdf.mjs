import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function exportPdf() {
  console.log('Launching browser for PDF export...');
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--allow-file-access-from-files']
  });
  const page = await browser.newPage();
  
  const htmlPath = path.resolve(__dirname, '../docs_and_tests/chapter4_testcases.html').replace(/\\/g, '/');
  const fileUrl = `file:///${htmlPath}`;
  console.log(`Navigating to ${fileUrl}...`);

  await page.goto(fileUrl, { waitUntil: 'load', timeout: 30000 });
  console.log('HTML loaded successfully in browser');

  // Let MathJax or rendering settle
  await new Promise(r => setTimeout(r, 2000));

  const outPdf = path.resolve(__dirname, '../docs_and_tests/chapter4_testcases.pdf');
  console.log(`Generating PDF to ${outPdf}...`);
  await page.pdf({
    path: outPdf,
    format: 'A4',
    printBackground: true,
    margin: {
      top: '21mm',
      right: '19mm',
      bottom: '20mm',
      left: '23mm'
    }
  });

  const stats = fs.statSync(outPdf);
  console.log(`Saved PDF to: ${outPdf}`);
  console.log(`PDF size: ${stats.size} bytes`);

  await browser.close();
  console.log('Export finished successfully!');
}

exportPdf().catch(err => {
  console.error('Error during PDF export:', err);
  process.exit(1);
});
