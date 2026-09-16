import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, mkdir } from "node:fs/promises";
import path from "node:path";
import puppeteer from "puppeteer";

// Serves the production build locally. Every API request is intercepted below.
const root = path.resolve("dist/spa");
const mime = { ".js": "text/javascript", ".css": "text/css", ".png": "image/png", ".html": "text/html" };
const server = createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  let file = path.resolve(root, `.${url.pathname}`);
  if (!file.startsWith(root + path.sep)) file = path.join(root, "index.html");
  try { const data = await readFile(file); res.setHeader("Content-Type", mime[path.extname(file)] || "application/octet-stream"); res.end(data); }
  catch { res.setHeader("Content-Type", "text/html"); res.end(await readFile(path.join(root, "index.html"))); }
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
let browser;
try {
  console.log("Launching fixture browser");
  browser = await puppeteer.launch({ headless: true });
  console.log("Browser ready");
  const page = await browser.newPage();
  const errors = [], writes = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("dialog", dialog => dialog.accept());
  let role = "teacher", expired = false, left = false;
  const room = { id: 10, name: "Data Structures", section: "CS201", class_code: "CS201A" };
  await page.setRequestInterception(true);
  page.on("request", request => {
    const url = new URL(request.url());
    if (url.origin !== origin) return request.abort();
    if (!url.pathname.startsWith("/api/")) return request.continue();
    const route = url.pathname;
    const payload = request.postData();
    let body = {}, status = 200;
    if (request.method() !== "GET") writes.push({ route, payload });
    if (route === "/api/auth/me") body = { id: 101, name: "Test user", email: "test@example.test", role, avatar_url: "https://res.cloudinary.com/example/avatar.png" };
    else if (route === "/api/auth/socket-token") status = 503;
    else if (route === "/api/notifications") body = [];
    else if (route === "/api/rooms") body = left ? [] : [room];
    else if (route === "/api/rooms/10") body = room;
    else if (route.endsWith("/enrollment")) { left = true; body = { message: "Left" }; }
    else if (route === "/api/ai/answer-word-count") {
      const { answers } = JSON.parse(payload);
      body = { counts: Object.fromEntries(Object.entries(answers).map(([key, value]) => [key, value.trim() ? value.trim().split(/\s+/).length : 0])), limit: 300 };
    } else if (route === "/api/ai/generate-rubric") body = { answer_key: "LIFO", rubrics: [{ name: "Accuracy", description: "Explains LIFO", score: 5 }] };
    else if (route.endsWith("/submissions/101")) body = {
      submission: { id: 1, status: "ready", total_score: 4 }, student: { id: 101, name: "Student" },
      answers: [{ id: 1, question_id: 11, question_text: "Explain Stack", max_score: 5, answer_text: "", ai_score: 4, ai_feedback: "Good", ai_confidence: "high", quality_metrics: { transcription: "Stack uses LIFO" } }],
    };
    else if (route.endsWith("/exams/1")) body = { id: 1, title: "Stack exam", total_score: 5, server_time: new Date().toISOString(), end_date: new Date(Date.now() + (expired ? -120000 : 240000)).toISOString(), submission_deadline: new Date(Date.now() + (expired ? -60000 : 300000)).toISOString(), questions: [{ id: 11, text: "Explain Stack", score: 5 }] };
    else if (route.endsWith("/exams") && request.method() === "POST") body = { id: 1 };
    else if (route.endsWith("/exams")) body = [];
    else if (route.endsWith("/submissions/me")) body = { status: "missing" };
    return request.respond({ status, contentType: "application/json", body: JSON.stringify(body) });
  });
  await page.evaluateOnNewDocument(() => { localStorage.setItem("token", "fixture"); localStorage.setItem("evaly-theme", "light"); });
  const visit = async route => {
    console.log("Checking", route);
    await page.goto(origin + route, { waitUntil: "networkidle0" });
    await page.waitForSelector(".workspace");
  };
  const fill = async (selector, value) => page.$eval(selector, (element, text) => {
    const prototype = element.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(prototype, "value").set.call(element, text);
    element.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
  const clickText = async text => {
    const button = await page.waitForFunction(text => Array.from(document.querySelectorAll("button")).find(el => el.textContent.includes(text)), {}, text);
    await button.asElement().click();
  };
  await mkdir("artifacts/ui-review", { recursive: true });
  await page.setViewport({ width: 1440, height: 1000 });
  await visit("/room/10/create-exam");
  await fill('textarea[aria-label="คำถามข้อที่ 1"]', "Explain Stack");
  await clickText("สร้างแนวคำตอบและเกณฑ์ด้วย AI");
  await page.waitForFunction(() => document.querySelector('input[aria-label="แนวคำตอบข้อที่ 1"]').value === "LIFO");
  await fill('input[type="datetime-local"]', "2026-12-01T09:00");
  await page.screenshot({ path: "artifacts/ui-review/coverage-create-desktop.png", fullPage: true });
  await clickText("บันทึกสร้างข้อสอบ");
  await page.waitForFunction(() => location.pathname === "/room/10");
  const save = writes.find(item => item.route === "/api/rooms/10/exams");
  assert.ok(JSON.parse(save.payload).start_date);
  assert.equal(JSON.parse(save.payload).questions[0].answer_key, "LIFO");
  role = "student";
  await visit("/room/10/exam/1/submit");
  await fill("textarea", "word ".repeat(301));
  await page.waitForFunction(() => document.body.textContent.includes("301 / 300 คำ"));
  assert.ok(await page.$eval('button[type="submit"]', button => button.disabled));
  await fill("textarea", "word ".repeat(300));
  await page.waitForFunction(() => document.body.textContent.includes("300 / 300 คำ"));
  assert.equal(await page.$eval('button[type="submit"]', button => button.disabled), false);
  assert.ok((await page.$eval('div[role="status"]', el => el.textContent)).includes("เหลือเวลา"));
  await page.setViewport({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.waitForSelector("[data-sonner-toast]", { hidden: true, timeout: 10000 });
  await page.screenshot({ path: "artifacts/ui-review/coverage-submit-mobile.png", fullPage: true });
  expired = true;
  await visit("/room/10/exam/1/submit");
  assert.ok(await page.$eval('button[type="submit"]', button => button.disabled));
  await visit("/home");
  await clickText("ออกจากห้อง");
  await page.waitForFunction(() => !document.querySelector(".room-row"));
  assert.ok(writes.some(item => item.route.endsWith("/enrollment")));
  role = "teacher";
  await visit("/room/10/exam/1/grading/101");
  assert.ok((await page.$eval("body", el => el.textContent)).includes("Stack uses LIFO"));
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({ path: "artifacts/ui-review/coverage-review-mobile.png", fullPage: true });
  await visit("/room/10/create-exam");
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({ path: "artifacts/ui-review/coverage-create-mobile.png", fullPage: true });
  assert.deepEqual(errors, []);
  console.log("PASS: OpenAI rubric UI, exam dates, 300/301-word boundary, server countdown, expiry, leave, transcription, mobile overflow, no page errors. All APIs mocked.");
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
