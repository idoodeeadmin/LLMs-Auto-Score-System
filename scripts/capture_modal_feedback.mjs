import puppeteer from "puppeteer";
import path from "node:path";

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

  // Click on Q4
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll("button"));
    const q4Btn = buttons.find(b => b.textContent.includes("ข้อ 4 (34)"));
    if (q4Btn) q4Btn.click();
  });
  await new Promise((r) => setTimeout(r, 600));

  // Click on the first "อ่านคำอธิบายฉบับเต็ม"
  await page.evaluate(() => {
    const links = Array.from(document.querySelectorAll(".btn-read-more"));
    if (links.length > 0) links[0].click();
  });
  await new Promise((r) => setTimeout(r, 600));

  const outPath = path.resolve("public/screenshots/dataset_viewer_q4_modal.png");
  await page.screenshot({ path: outPath, fullPage: false });
  console.log(`Saved modal screenshot to ${outPath}`);
} finally {
  await browser.close();
}
