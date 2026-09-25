import puppeteer from "puppeteer";
import path from "node:path";
import fs from "node:fs";

const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const htmlPath = path.resolve("public/dataset_viewer.html");
const fileUrl = `file://${htmlPath.replace(/\\/g, "/")}`;

const outDir = path.resolve("public/screenshots");

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: chromePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--force-color-profile=srgb"],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1500, height: 1100, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // Switch to Dataset tab and filter by Q3
  await page.evaluate(() => {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const datasetBtn = tabBtns.find((b) => b.textContent.includes("ตารางข้อสอบ") || b.textContent.includes("Dataset"));
    if (datasetBtn) datasetBtn.click();
  });
  await new Promise((r) => setTimeout(r, 600));

  await page.evaluate(() => {
    const pills = Array.from(document.querySelectorAll(".pill-btn"));
    const q3Btn = pills.find((b) => b.textContent.includes("ข้อ 3"));
    if (q3Btn) q3Btn.click();
  });
  await new Promise((r) => setTimeout(r, 800));

  const shot = path.resolve(outDir, "dataset_viewer_q3_table.png");
  await page.screenshot({ path: shot, fullPage: false });
  console.log(`Saved Q3 table screenshot: ${shot}`);

} finally {
  await browser.close();
}
