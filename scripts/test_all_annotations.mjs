import puppeteer from 'puppeteer';
import { manualSteps } from './manual_steps_def.mjs';

async function testAll() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 850, deviceScaleFactor: 2 }
  });

  const page = await browser.newPage();

  for (const step of manualSteps) {
    console.log(`\n========================================`);
    console.log(`Checking ${step.filename} (${step.url})...`);

    await page.evaluateOnNewDocument((tok) => {
      if (tok) localStorage.setItem('token', tok);
      else localStorage.removeItem('token');
    }, step.token);

    await page.goto(step.url, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 1200));

    if (step.beforeAnnotate) {
      await step.beforeAnnotate(page);
    }

    const results = await page.evaluate((annList) => {
      return annList.map(({ selector, textMatch, num, shape, customFind }) => {
        let target = null;
        let method = '';

        if (customFind) {
          // evaluate custom string code if any
        }

        if (selector) {
          try {
            const els = Array.from(document.querySelectorAll(selector));
            target = els.find(el => {
              const r = el.getBoundingClientRect();
              return r.width > 0 && r.height > 0;
            }) || els[0];
            if (target) method = `selector(${selector})`;
          } catch (e) {}
        }

        if (!target && textMatch) {
          const elements = Array.from(document.querySelectorAll('button, a, input, textarea, div, span, p, label, th, td, h1, h2, h3, h4'));
          // Exact text match first
          target = elements.find(el => el.innerText && el.innerText.trim() === textMatch && el.children.length === 0);
          if (!target) {
            target = elements.find(el => el.innerText && el.innerText.includes(textMatch) && el.children.length === 0);
          }
          if (!target) {
            target = elements.find(el => el.innerText && el.innerText.includes(textMatch));
          }
          if (target) method = `textMatch(${textMatch})`;
        }

        if (!target) {
          return { num, found: false, reason: 'Target not found' };
        }

        const rect = target.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) {
          return { num, found: false, reason: `Element has 0 size: ${rect.width}x${rect.height}` };
        }

        return {
          num,
          found: true,
          method,
          tag: target.tagName.toLowerCase(),
          rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
          snippet: (target.innerText || target.placeholder || target.value || '').slice(0, 35).trim()
        };
      });
    }, step.annotations);

    let allOk = true;
    for (const r of results) {
      if (r.found) {
        console.log(`  [OK] #${r.num} (${r.method}) -> ${r.tag} [${r.rect.w}x${r.rect.h} at ${r.rect.x},${r.rect.y}] "${r.snippet}"`);
      } else {
        console.log(`  [FAIL] #${r.num} -> ${r.reason}`);
        allOk = false;
      }
    }
    if (allOk) {
      console.log(`  ==> ALL ${results.length} ANNOTATIONS FOUND FOR ${step.filename}`);
    } else {
      console.log(`  ==> MISSED SOME ANNOTATIONS FOR ${step.filename}!`);
    }
  }

  await browser.close();
}

testAll();
