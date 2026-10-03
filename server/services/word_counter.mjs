// server/services/word_counter.mjs
// Single source of truth for Thai root-word counting matching client/lib/utils.ts 100%

export function countWords(text) {
  if (!text || !text.trim()) return 0;
  const normalized = text
    .replace(/([\u0E00-\u0E7F])([a-zA-Z0-9])/g, "$1 $2")
    .replace(/([a-zA-Z0-9])([\u0E00-\u0E7F])/g, "$1 $2");

  if (typeof Intl !== "undefined" && Intl.Segmenter) {
    const segmenter = new Intl.Segmenter("th", { granularity: "word" });
    const segments = [...segmenter.segment(normalized)].filter((seg) => seg.isWordLike);
    return segments.length;
  }
  const thaiTokens = normalized.match(/[\u0E00-\u0E7F]+/g) || [];
  const latinTokens = normalized.replace(/[\u0E00-\u0E7F]+/g, " ").trim().split(/\s+/).filter(Boolean);
  return thaiTokens.length + latinTokens.length;
}

// When executed directly from CLI or stdin
if (import.meta.url === `file://${process.argv[1]?.replace(/\\/g, "/")}` || process.argv[1]?.endsWith("word_counter.mjs")) {
  const args = process.argv.slice(2);
  if (args.length > 0) {
    // Single or multiple arguments passed as strings or json
    if (args[0] === "--json") {
      try {
        const input = JSON.parse(args[1]);
        if (Array.isArray(input)) {
          console.log(JSON.stringify(input.map(countWords)));
        } else if (typeof input === "object" && input !== null) {
          const res = {};
          for (const [k, v] of Object.entries(input)) {
            res[k] = countWords(v);
          }
          console.log(JSON.stringify(res));
        } else {
          console.log(countWords(String(input)));
        }
      } catch (err) {
        console.error(err);
        process.exit(1);
      }
    } else {
      console.log(countWords(args[0]));
    }
  } else {
    // Read from STDIN
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => {
      try {
        if (!data.trim()) {
          console.log(0);
          return;
        }
        if (data.trim().startsWith("{") || data.trim().startsWith("[")) {
          const input = JSON.parse(data);
          if (Array.isArray(input)) {
            console.log(JSON.stringify(input.map(countWords)));
          } else {
            const res = {};
            for (const [k, v] of Object.entries(input)) {
              res[k] = countWords(v);
            }
            console.log(JSON.stringify(res));
          }
        } else {
          console.log(countWords(data));
        }
      } catch (err) {
        console.log(countWords(data));
      }
    });
  }
}
