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
  await page.setViewport({ width: 1500, height: 1100, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // 1. Switch to Analytics Tab (Benchmark Summary)
  await page.evaluate(() => {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const benchmarkBtn = tabBtns.find((b) => b.textContent.includes("สรุปผลความแม่นยำ") || b.textContent.includes("Benchmark"));
    if (benchmarkBtn) benchmarkBtn.click();
  });
  await new Promise((r) => setTimeout(r, 800));

  // Screenshot 1: Benchmark Tab Top (Hero cards + Table)
  const shot1 = path.resolve(outDir, "accuracy_benchmark_summary_table.png");
  await page.screenshot({ path: shot1, fullPage: false });
  console.log(`Saved screenshot 1: ${shot1}`);

  // Screenshot 2: Scroll down to Visual Comparison Bars & Deep-dive Insights
  await page.evaluate(() => {
    window.scrollBy(0, 750);
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot2 = path.resolve(outDir, "accuracy_benchmark_bars_and_insights.png");
  await page.screenshot({ path: shot2, fullPage: false });
  console.log(`Saved screenshot 2: ${shot2}`);

  // Screenshot 3: Full Page screenshot of the entire Benchmark tab
  const shot3 = path.resolve(outDir, "accuracy_benchmark_full_tab.png");
  await page.screenshot({ path: shot3, fullPage: true });
  console.log(`Saved screenshot 3: ${shot3}`);

} finally {
  await browser.close();
}
