import puppeteer from "puppeteer";
import { mkdir } from "node:fs/promises";
import assert from "node:assert/strict";

// Browser-only fixtures: no API data or authenticated accounts are modified.
const browser = await puppeteer.launch({ headless: true });
const page = await browser.newPage();
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
let role = "teacher";
let submitted = false;
const writes = [];
const room = {
  id: 1,
  name: "โครงสร้างข้อมูลและอัลกอริทึม",
  section: "CS201 · กลุ่ม 1",
  class_code: "CS201-4821",
};
const exam = {
  id: 1,
  title: "แบบทดสอบที่ 1 · การวิเคราะห์อัลกอริทึม",
  total_score: 10,
  questions: [
    {
      id: 1,
      text: "อธิบายความแตกต่างระหว่าง Stack และ Queue พร้อมยกตัวอย่างการใช้งานที่เหมาะสม",
      score: 5,
    },
    {
      id: 2,
      text: "เพราะเหตุใด Binary Search จึงต้องใช้ข้อมูลที่เรียงลำดับแล้ว อธิบายเหตุผลประกอบคำตอบ",
      score: 5,
    },
  ],
};
await page.setRequestInterception(true);
page.on("request", (request) => {
  const url = new URL(request.url());
  if (url.hostname !== "localhost" && url.hostname !== "127.0.0.1")
    return request.abort();
  if (!url.pathname.startsWith("/api/")) return request.continue();
  let body = {};
  if (request.method() !== "GET") {
    writes.push({ path: url.pathname, body: request.postData() });
    submitted = true;
  } else if (url.pathname === "/api/auth/me")
    body = {
      id: 1,
      name: role === "teacher" ? "อาจารย์ ณัฐวุฒิ" : "กมลชนก ใจดี",
      email: "preview@example.test",
      role,
    };
  else if (url.pathname === "/api/rooms")
    body = [
      room,
      {
        ...room,
        id: 2,
        name: "พื้นฐานการเขียนโปรแกรม",
        section: "CS101 · กลุ่ม 2",
        class_code: "CS101-9920",
      },
    ];
  else if (url.pathname.endsWith("/submissions/me"))
    body = { status: submitted ? "submitted" : "missing" };
  else if (url.pathname.endsWith("/submissions/1"))
    body = {
      submission: { id: 1, status: "submitted", total_score: 7 },
      student: { id: 1, name: "กมลชนก ใจดี", email: "student@example.test" },
      answers: exam.questions.map((q) => ({
        id: q.id,
        question_id: q.id,
        question_text: q.text,
        max_score: 5,
        answer_text:
          "Stack ทำงานแบบเข้าหลังออกก่อน ส่วน Queue ทำงานแบบเข้าก่อนออกก่อน ใช้จัดลำดับงานที่รอประมวลผล",
        ai_score: 3.5,
        ai_feedback:
          "อธิบายหลักการได้ถูกต้อง ควรเพิ่มตัวอย่างการใช้งานให้ชัดเจน",
        ai_confidence: "medium",
      })),
    };
  else if (url.pathname.endsWith("/submissions"))
    body = [
      {
        student_id: 1,
        name: "กมลชนก ใจดี",
        email: "student@example.test",
        submission_id: 1,
        status: "submitted",
      },
    ];
  else if (url.pathname.endsWith("/exams/1")) body = exam;
  else if (url.pathname.endsWith("/exams")) body = [exam];
  else if (url.pathname === "/api/rooms/1") body = room;
  return request.respond({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
});
await page.evaluateOnNewDocument(() => {
  localStorage.setItem("token", "browser-fixture");
  if (!localStorage.getItem("evaly-theme"))
    localStorage.setItem("evaly-theme", "light");
});
await mkdir("artifacts/ui-review", { recursive: true });
async function visit(path, name, mobile = false, viewportWidth) {
  await page.setViewport({
    width: viewportWidth ?? (mobile ? 390 : 1440),
    height: mobile ? 844 : 1000,
  });
  console.log("Checking", name);
  await page.goto(`http://localhost:8080${path}`, {
    waitUntil: "domcontentloaded",
  });
  await page.waitForSelector(".workspace");
  await page.waitForFunction(
    () => !document.body.textContent.includes("กำลังโหลด"),
  );
  await page.screenshot({
    path: `artifacts/ui-review/${name}.png`,
    fullPage: true,
  });
  assert.ok(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
    `${name}: horizontal overflow`,
  );
  if (mobile) {
    assert.ok(
      await page.$$eval("button.primary-action", (buttons) =>
        buttons.every((button) => button.getBoundingClientRect().height >= 44),
      ),
      `${name}: primary tap target is too small`,
    );
  }
}
try {
  await visit("/", "login");
  await visit("/home", "rooms");
  await page.type('input[aria-label="ค้นหาห้องเรียน"]', "CS201");
  assert.equal(await page.$$eval(".room-row", (rows) => rows.length), 1);
  await visit("/room/1", "exams");
  await page.click('[role="button"][aria-expanded]');
  await page.waitForSelector('[role="button"] [class*="font-bold"]');
  await visit("/room/1/create-exam", "create");
  await page.type('input[aria-label="ชื่อข้อสอบ"]', "ทดสอบการสร้างข้อสอบ");
  await page.type('textarea[aria-label="คำถามข้อที่ 1"]', "อธิบาย Stack");
  await page.click("button.primary-action");
  await page.waitForFunction(() => location.pathname === "/room/1");
  assert.ok(
    writes.some((w) => w.path === "/api/rooms/1/exams"),
    "create request missing",
  );
  await visit("/room/1/exam/1/grading/1", "grading");
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => location.pathname === "/room/1");
  assert.ok(
    writes.some((w) => w.path.endsWith("/approve")),
    "approval request missing",
  );
  role = "student";
  submitted = false;
  await visit("/room/1/exam/1/submit", "answer");
  await page.type('textarea[aria-label="คำตอบข้อที่ 1"]', "คำตอบทดสอบ");
  assert.match(
    await page.$eval(".work-summary", (el) => el.textContent),
    /ตอบแล้ว 1 \/ 2/,
  );
  await page.click('a[href="#question-2"]');
  await page.click('button[type="submit"]');
  await page.waitForFunction(() =>
    document.body.textContent.includes("ระบบได้รับคำตอบ"),
  );
  assert.ok(
    writes.some((w) => w.path.endsWith("/submit-multipart")),
    "submission request missing",
  );
  for (const [path, name] of [
    ["/home", "rooms-mobile"],
    ["/room/1", "exams-mobile"],
    ["/room/1/create-exam", "create-mobile"],
    ["/room/1/exam/1/submit", "answer-mobile"],
    ["/room/1/exam/1/grading/1", "grading-mobile"],
  ])
    await visit(path, name, true);
  for (const width of [320, 768]) {
    for (const [path, name] of [
      ["/home", "rooms"],
      ["/room/1/create-exam", "create"],
      ["/room/1/exam/1/submit", "answer"],
      ["/room/1/exam/1/grading/1", "grading"],
    ]) {
      await visit(path, `${name}-${width}`, true, width);
    }
  }
  await page.evaluate(() => {
    localStorage.setItem("evaly-theme", "dark");
  });
  await visit("/home", "rooms-dark");
  assert.ok(
    await page.evaluate(() =>
      document.documentElement.classList.contains("dark"),
    ),
    "dark mode must be active",
  );
  assert.deepEqual(errors, [], "browser runtime errors");
  console.log(
    "PASS: login, room search, exam navigation, create request, answer progress, submission, grade approval, mobile overflow, dark mode; browser fixtures only.",
  );
} finally {
  await browser.close();
}
