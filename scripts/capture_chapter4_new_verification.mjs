import puppeteer from "puppeteer";
import path from "node:path";
import fs from "node:fs";

const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const outDir = path.resolve("public/screenshots/verification");
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
  await page.setViewport({ width: 1440, height: 1080, deviceScaleFactor: 1 });

  // 1. Screenshot Chapter 4 Testcases - Table 4.4
  const htmlTestcases = path.resolve("public/chapter4_testcases.html");
  await page.goto(`file://${htmlTestcases.replace(/\\/g, "/")}`, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // Table 4.4
  await page.evaluate(() => {
    const el = document.getElementById("table-4-4") || Array.from(document.querySelectorAll(".table-title")).find(t => t.textContent.includes("ตารางที่ 4.4"));
    if (el) el.scrollIntoView({ behavior: "instant", block: "center" });
  });
  await new Promise((r) => setTimeout(r, 500));
  const shot1 = path.resolve(outDir, "testcases_table4_4.png");
  await page.screenshot({ path: shot1, fullPage: false });
  console.log(`Saved screenshot 1: ${shot1}`);

  // Table 4.5 & 4.6
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll(".table-title")).find(t => t.textContent.includes("ตารางที่ 4.5"));
    if (el) el.scrollIntoView({ behavior: "instant", block: "start" });
  });
  await new Promise((r) => setTimeout(r, 500));
  const shot2 = path.resolve(outDir, "testcases_table4_5_and_4_6.png");
  await page.screenshot({ path: shot2, fullPage: false });
  console.log(`Saved screenshot 2: ${shot2}`);

  // Table 4.7 Confusion Matrix
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll(".table-title")).find(t => t.textContent.includes("ตารางที่ 4.7"));
    if (el) el.scrollIntoView({ behavior: "instant", block: "center" });
  });
  await new Promise((r) => setTimeout(r, 500));
  const shot3 = path.resolve(outDir, "testcases_table4_7_confusion_matrix.png");
  await page.screenshot({ path: shot3, fullPage: false });
  console.log(`Saved screenshot 3: ${shot3}`);

  // Case Study 3: DS-107
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll(".table-title")).find(t => t.textContent.includes("DS-107") || t.textContent.includes("ตารางที่ 4.16"));
    if (el) el.scrollIntoView({ behavior: "instant", block: "center" });
  });
  await new Promise((r) => setTimeout(r, 500));
  const shot4 = path.resolve(outDir, "testcases_case_study_ds107.png");
  await page.screenshot({ path: shot4, fullPage: false });
  console.log(`Saved screenshot 4: ${shot4}`);

  // 2. Screenshot Chapter 4 Complete Report - Stat Grid & Tables
  const htmlReport = path.resolve("public/chapter4_complete_report.html");
  await page.goto(`file://${htmlReport.replace(/\\/g, "/")}`, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  await page.evaluate(() => {
    const el = document.querySelector(".stat-grid");
    if (el) el.scrollIntoView({ behavior: "instant", block: "center" });
  });
  await new Promise((r) => setTimeout(r, 500));
  const shot5 = path.resolve(outDir, "complete_report_statgrid_and_table42.png");
  await page.screenshot({ path: shot5, fullPage: false });
  console.log(`Saved screenshot 5: ${shot5}`);

  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll(".table-caption")).find(t => t.textContent.includes("ตารางที่ 4.3"));
    if (el) el.scrollIntoView({ behavior: "instant", block: "center" });
  });
  await new Promise((r) => setTimeout(r, 500));
  const shot6 = path.resolve(outDir, "complete_report_table43.png");
  await page.screenshot({ path: shot6, fullPage: false });
  console.log(`Saved screenshot 6: ${shot6}`);

} catch (err) {
  console.error("Error capturing verification screenshots:", err);
} finally {
  await browser.close();
}
