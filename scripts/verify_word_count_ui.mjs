import puppeteer from "puppeteer";
import path from "node:path";
import fs from "node:fs";

const chromePath = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const utilsContent = fs.readFileSync(path.resolve("client/lib/utils.ts"), "utf-8");

// Extract countWords implementation into a standalone HTML for visual and behavioral verification
const htmlContent = `
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <title>Word Counter Verification</title>
  <style>
    body {
      background: #0f172a;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Thai", sans-serif;
      padding: 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 24px;
      width: 700px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    .label {
      font-size: 14px;
      font-weight: 700;
      color: #cbd5e1;
    }
    .counter-badge {
      font-size: 13px;
      font-weight: 600;
      font-family: monospace;
      padding: 4px 12px;
      border-radius: 9999px;
      background: #334155;
      color: #94a3b8;
      border: 1px solid #475569;
    }
    .counter-badge.highlight {
      background: rgba(14, 165, 233, 0.15);
      color: #38bdf8;
      border-color: rgba(56, 189, 248, 0.4);
    }
    .textarea-box {
      width: 100%;
      height: 80px;
      background: #0f172a;
      border: 2px solid #22c55e;
      border-radius: 12px;
      color: #f8fafc;
      font-size: 16px;
      padding: 12px;
      box-sizing: border-box;
      outline: none;
      font-family: "Noto Sans Thai", sans-serif;
    }
    .token-breakdown {
      margin-top: 16px;
      padding: 12px;
      background: #0f172a;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.6;
    }
    .token-chip {
      display: inline-block;
      padding: 2px 8px;
      margin: 2px 4px;
      background: #0284c7;
      color: #ffffff;
      border-radius: 4px;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <h2 style="margin-bottom: 24px;">ระบบนับคำแบบตัดตามรากศัพท์ (Morpheme Root Words)</h2>
  <div class="card">
    <div class="header">
      <span class="label">คำตอบของคุณ (พิมพ์ข้อความ):</span>
      <span id="counter" class="counter-badge highlight">คำตอบ: 0 / 300 คำ</span>
    </div>
    <textarea id="input" class="textarea-box">การทำงานของStack,queue</textarea>
    <div class="token-breakdown" id="breakdown"></div>
  </div>

  <div class="card" style="margin-top: 24px;">
    <div class="header">
      <span class="label">กรณีทดสอบคำว่า "การทำงาน" อย่างเดียว:</span>
      <span id="counter2" class="counter-badge highlight">คำตอบ: 0 / 300 คำ</span>
    </div>
    <textarea id="input2" class="textarea-box" style="height: 50px;">การทำงาน</textarea>
    <div class="token-breakdown" id="breakdown2"></div>
  </div>

  <script>
    function countWordsWithDetails(text) {
      if (!text || !text.trim()) return { count: 0, tokens: [] };
      const normalized = text
        .replace(/([\\u0E00-\\u0E7F])([a-zA-Z0-9])/g, "$1 $2")
        .replace(/([a-zA-Z0-9])([\\u0E00-\\u0E7F])/g, "$1 $2");

      if (typeof Intl !== "undefined" && Intl.Segmenter) {
        const segmenter = new Intl.Segmenter("th", { granularity: "word" });
        const segments = [...segmenter.segment(normalized)].filter((seg) => seg.isWordLike);
        return { count: segments.length, tokens: segments.map(s => s.segment) };
      }
      const thaiTokens = normalized.match(/[\\u0E00-\\u0E7F]+/g) || [];
      const latinTokens = normalized.replace(/[\\u0E00-\\u0E7F]+/g, " ").trim().split(/\\s+/).filter(Boolean);
      return { count: thaiTokens.length + latinTokens.length, tokens: [...thaiTokens, ...latinTokens] };
    }

    function update() {
      const res1 = countWordsWithDetails(document.getElementById("input").value);
      document.getElementById("counter").innerText = "คำตอบ: " + res1.count + " / 300 คำ";
      document.getElementById("breakdown").innerHTML = "<strong>แจกแจงรากศัพท์ (" + res1.count + " คำ):</strong> " +
        res1.tokens.map(t => '<span class="token-chip">' + t + '</span>').join("");

      const res2 = countWordsWithDetails(document.getElementById("input2").value);
      document.getElementById("counter2").innerText = "คำตอบ: " + res2.count + " / 300 คำ";
      document.getElementById("breakdown2").innerHTML = "<strong>แจกแจงรากศัพท์ (" + res2.count + " คำ):</strong> " +
        res2.tokens.map(t => '<span class="token-chip">' + t + '</span>').join("");
    }

    document.getElementById("input").addEventListener("input", update);
    document.getElementById("input2").addEventListener("input", update);
    update();
  </script>
</body>
</html>
`;

const tempHtmlPath = path.resolve("public/test_word_count.html");
fs.writeFileSync(tempHtmlPath, htmlContent, "utf-8");

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: chromePath,
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--force-color-profile=srgb"],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 900, height: 750, deviceScaleFactor: 1 });
  await page.goto(`file://${tempHtmlPath.replace(/\\/g, "/")}`, { waitUntil: "networkidle2" });
  await new Promise((r) => setTimeout(r, 600));

  const outPath = path.resolve("public/screenshots/word_count_morpheme_verified.png");
  await page.screenshot({ path: outPath, fullPage: false });
  console.log(`Saved screenshot to ${outPath}`);
} finally {
  await browser.close();
}
