import puppeteer from "puppeteer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const htmlPath = path.resolve("public/dataset_viewer.html");
const fileUrl = `file://${htmlPath.replace(/\\/g, "/")}`;

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: chromePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--force-color-profile=srgb"],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // Click on Question 4 filter tab if exists
  await page.evaluate(() => {
    // Find button with text containing 'ข้อ 4'
    const buttons = Array.from(document.querySelectorAll("button"));
    const q4Btn = buttons.find(b => b.textContent.includes("ข้อ 4") || b.textContent.includes("Q4"));
    if (q4Btn) q4Btn.click();
  });
  await new Promise((r) => setTimeout(r, 800));

  const outPath = path.resolve("public/screenshots/dataset_viewer_q4.png");
  await page.screenshot({ path: outPath, fullPage: false });
  console.log(`Saved screenshot to ${outPath}`);
} finally {
  await browser.close();
}
