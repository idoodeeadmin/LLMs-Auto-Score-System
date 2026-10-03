import puppeteer from "puppeteer";
import path from "node:path";
import fs from "node:fs";

const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";
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
  await page.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 1 });

  // 1. Screenshot Chapter 4 Table 4.3 in public/chapter4_testcases.html
  const htmlPath = path.resolve("public/chapter4_testcases.html");
  await page.goto(`file://${htmlPath.replace(/\\/g, "/")}`, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // Scroll to Table 4.3
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll(".table-title")).find(t => t.textContent.includes("ตารางที่ 4.3"));
    if (el) el.scrollIntoView({ behavior: "instant", block: "center" });
  });
  await new Promise((r) => setTimeout(r, 500));

  const shot1 = path.resolve(outDir, "chapter4_table43_updated.png");
  await page.screenshot({ path: shot1, fullPage: false });
  console.log(`Saved screenshot 1: ${shot1}`);

  // 2. Screenshot DS-025 in public/audit_gallery_53.html
  const galleryPath = path.resolve("public/audit_gallery_53.html");
  await page.goto(`file://${galleryPath.replace(/\\/g, "/")}`, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // Search DS-025
  await page.evaluate(() => {
    const input = document.getElementById("search-input");
    if (input) {
      input.value = "DS-025";
      input.dispatchEvent(new Event("input"));
    }
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot2 = path.resolve(outDir, "audit_gallery_ds025_updated.png");
  await page.screenshot({ path: shot2, fullPage: false });
  console.log(`Saved screenshot 2: ${shot2}`);

} catch (err) {
  console.error("Error capturing verification screenshots:", err);
} finally {
  await browser.close();
}
