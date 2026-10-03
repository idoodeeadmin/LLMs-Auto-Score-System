import puppeteer from "puppeteer";
import path from "node:path";
import fs from "node:fs";

const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const htmlPath = path.resolve("public/dataset_viewer.html");
const fileUrl = `file://${htmlPath.replace(/\\/g, "/")}`;

fs.mkdirSync("public/screenshots", { recursive: true });

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: chromePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--force-color-profile=srgb"],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 1100, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1200));

  // Click on Question 5 filter tab
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll("button, .tab, .filter-btn, [data-q]"));
    const q5Btn = buttons.find(b => b.textContent.includes("ข้อ 5") || b.textContent.includes("Q5") || b.textContent.includes("5"));
    if (q5Btn) q5Btn.click();
  });
  await new Promise((r) => setTimeout(r, 1000));

  const outPath = path.resolve("public/screenshots/dataset_viewer_q5_new.png");
  await page.screenshot({ path: outPath, fullPage: false });
  console.log(`Saved screenshot to ${outPath}`);

  // Click on Summary tab
  await page.evaluate(() => {
    const tabs = Array.from(document.querySelectorAll(".tab-btn, button, nav a"));
    const sumTab = tabs.find(t => t.textContent.includes("สรุปผลความแม่นยำ") || t.textContent.includes("Benchmark"));
    if (sumTab) sumTab.click();
  });
  await new Promise((r) => setTimeout(r, 1000));
  const sumPath = path.resolve("public/screenshots/dataset_viewer_summary.png");
  await page.screenshot({ path: sumPath, fullPage: false });
  console.log(`Saved screenshot to ${sumPath}`);
} finally {
  await browser.close();
}
