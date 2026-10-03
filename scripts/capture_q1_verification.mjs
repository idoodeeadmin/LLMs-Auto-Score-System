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

  // 1. Filter to Question 1 and search DS-025
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll(".pill-btn"));
    const q1Btn = buttons.find((b) => b.textContent.includes("ข้อ 1"));
    if (q1Btn) q1Btn.click();
    
    const searchInput = document.querySelector("#searchInput");
    if (searchInput) {
      searchInput.value = "DS-025";
      searchInput.dispatchEvent(new Event("input"));
    }
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot1 = path.resolve(outDir, "dataset_viewer_q1_ds025.png");
  await page.screenshot({ path: shot1, fullPage: false });
  console.log(`Saved screenshot 1: ${shot1}`);

  // 2. Open Feedback Modal for DS-025
  await page.evaluate(() => {
    if (typeof openFeedbackModal === "function") {
      openFeedbackModal("DS-025");
    }
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot2 = path.resolve(outDir, "dataset_viewer_ds025_feedback.png");
  await page.screenshot({ path: shot2, fullPage: false });
  console.log(`Saved screenshot 2: ${shot2}`);

  // Close modal
  await page.evaluate(() => {
    if (typeof closeFeedbackModal === "function") {
      closeFeedbackModal();
    }
  });
  await new Promise((r) => setTimeout(r, 400));

  // 3. Switch to Exam_Rubrics Tab
  await page.evaluate(() => {
    const tabBtns = Array.from(document.querySelectorAll(".tab-btn"));
    const rubricsBtn = tabBtns.find((b) => b.textContent.includes("Exam_Rubrics"));
    if (rubricsBtn) rubricsBtn.click();
  });
  await new Promise((r) => setTimeout(r, 600));

  const shot3 = path.resolve(outDir, "dataset_viewer_exam_rubrics_q1.png");
  await page.screenshot({ path: shot3, fullPage: false });
  console.log(`Saved screenshot 3: ${shot3}`);

} catch (err) {
  console.error("Error capturing screenshots:", err);
} finally {
  await browser.close();
}
