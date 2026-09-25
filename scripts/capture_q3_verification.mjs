import puppeteer from "puppeteer";
import path from "node:path";
import fs from "node:fs";

const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const htmlPath = path.resolve("public/dataset_viewer.html");
const fileUrl = `file://${htmlPath.replace(/\\/g, "/")}`;

const outDir = path.resolve("public/screenshots");
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: chromePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--force-color-profile=srgb"],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1100, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // 1. Q3 Table
  await page.evaluate(() => {
    const pills = Array.from(document.querySelectorAll(".pill-btn"));
    const q3Btn = pills.find((b) => b.textContent.includes("ข้อ 3"));
    if (q3Btn) q3Btn.click();
  });
  await new Promise((r) => setTimeout(r, 800));
  const shot1 = path.resolve(outDir, "q3_clean_table.png");
  await page.screenshot({ path: shot1, fullPage: false });
  console.log(`Saved Q3 table: ${shot1}`);

  // 2. Benchmark Summary tab
  await page.evaluate(() => {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const benchBtn = tabBtns.find((b) => b.textContent.includes("สรุปผลความแม่นยำ"));
    if (benchBtn) benchBtn.click();
  });
  await new Promise((r) => setTimeout(r, 800));
  const shot2 = path.resolve(outDir, "q3_clean_benchmark.png");
  await page.screenshot({ path: shot2, fullPage: false });
  console.log(`Saved benchmark tab: ${shot2}`);

  // 3. Exam Rubrics tab
  await page.evaluate(() => {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const rubBtn = tabBtns.find((b) => b.textContent.includes("Exam_Rubrics"));
    if (rubBtn) rubBtn.click();
  });
  await new Promise((r) => setTimeout(r, 800));
  const shot3 = path.resolve(outDir, "q3_clean_rubrics.png");
  await page.screenshot({ path: shot3, fullPage: false });
  console.log(`Saved rubrics tab: ${shot3}`);

} finally {
  await browser.close();
}
