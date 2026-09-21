import puppeteer from "puppeteer";
import path from "node:path";
import { mkdir } from "node:fs/promises";

const baseUrl = "http://127.0.0.1:8090";
const outputDir = path.resolve("public/screenshots");
const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: chromePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--force-color-profile=srgb"],
});

const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
await page.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
await mkdir(outputDir, { recursive: true });

page.on("console", (message) => {
  if (message.type() === "error") console.error(`[browser] ${message.text()}`);
});

async function open(route) {
  await page.goto(`${baseUrl}${route}`, { waitUntil: "networkidle2", timeout: 30000 });
  await sleep(700);
}

async function capture(filename, route) {
  await open(route);
  await page.screenshot({ path: path.join(outputDir, filename), type: "png" });
  console.log(`captured ${filename} <- ${route}`);
}

async function useRole(role) {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.evaluate((selectedRole) => {
    const selectedUser = {
      id: selectedRole === "teacher" ? 1 : 101,
      name: selectedRole === "teacher" ? "ผู้สอนทดสอบ" : "นักศึกษาทดสอบ",
      email: `${selectedRole}@example.test`,
      role: selectedRole,
      is_verified: 1,
    };
    localStorage.setItem("token", `fixture-${selectedRole}`);
    localStorage.setItem("user", JSON.stringify(selectedUser));
    localStorage.setItem("evaly-theme", "light");
  }, role);
}

try {
  await page.evaluateOnNewDocument(() => {
    localStorage.setItem("evaly-theme", "light");
  });

  await capture("home.png", "/");
  await capture("register.png", "/register");
  await capture("forgot-password.png", "/forgot-password");

  await useRole("teacher");
  await capture("dashboard.png", "/home");
  await capture("profile.png", "/profile");
  await capture("room-detail.png", "/room/10");
  await capture("create-exam.png", "/room/10/create-exam");
  await capture("exam-view.png", "/room/10/exam/1");
  await capture("exam-analytics.png", "/room/10/exam/1/analytics");
  await capture("live_scoring_experiment_result.png", "/room/10/exam/1/grading/101");
} finally {
  await browser.close();
}
