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
  await page.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1000));

  // 1. Filter to Question 6
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll(".pill-btn"));
    const q6Btn = buttons.find((b) => b.textContent.includes("ข้อ 6"));
    if (q6Btn) q6Btn.click();
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot1 = path.resolve(outDir, "dataset_viewer_q6_table.png");
  await page.screenshot({ path: shot1, fullPage: false });
  console.log(`Saved screenshot 1: ${shot1}`);

  // 2. Open Feedback Modal for a Q6 item (e.g. DS-172)
  await page.evaluate(() => {
    if (typeof openFeedbackModal === "function") {
      openFeedbackModal("DS-172");
    }
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot2 = path.resolve(outDir, "dataset_viewer_q6_feedback_modal.png");
  await page.screenshot({ path: shot2, fullPage: false });
  console.log(`Saved screenshot 2: ${shot2}`);

  // Close modal
  await page.evaluate(() => {
    if (typeof closeFeedbackModal === "function") {
      closeFeedbackModal();
    }
  });
  await new Promise((r) => setTimeout(r, 400));

  // 3. Switch to Analytics Tab
  await page.evaluate(() => {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const analyticsBtn = tabBtns.find((b) => b.textContent.includes("สถิติและการวิเคราะห์ผล"));
    if (analyticsBtn) analyticsBtn.click();
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot3 = path.resolve(outDir, "dataset_viewer_analytics_tab.png");
  await page.screenshot({ path: shot3, fullPage: false });
  console.log(`Saved screenshot 3: ${shot3}`);

  // 4. Switch to Rubrics Tab
  await page.evaluate(() => {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const rubricsBtn = tabBtns.find((b) => b.textContent.includes("Exam_Rubrics"));
    if (rubricsBtn) rubricsBtn.click();
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot4 = path.resolve(outDir, "dataset_viewer_rubrics_tab.png");
  await page.screenshot({ path: shot4, fullPage: false });
  console.log(`Saved screenshot 4: ${shot4}`);

} finally {
  await browser.close();
}
