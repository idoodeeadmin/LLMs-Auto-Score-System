import { describe, it, expect } from "vitest";
import { cn, countWords, formatRemainingTime } from "./utils";

describe("cn function", () => {
  it("should merge classes correctly", () => {
    expect(cn("text-red-500", "bg-blue-500")).toBe("text-red-500 bg-blue-500");
  });

  it("should handle conditional classes", () => {
    const isActive = true;
    expect(cn("base-class", isActive && "active-class")).toBe(
      "base-class active-class",
    );
  });

  it("should handle false and null conditions", () => {
    const isActive = false;
    expect(cn("base-class", isActive && "active-class", null)).toBe(
      "base-class",
    );
  });

  it("should merge tailwind classes properly", () => {
    expect(cn("px-2 py-1", "px-4")).toBe("py-1 px-4");
  });

  it("should work with object notation", () => {
    expect(cn("base", { conditional: true, "not-included": false })).toBe(
      "base conditional",
    );
  });
});

describe("countWords function", () => {
  it("should return 0 for empty or whitespace-only text", () => {
    expect(countWords("")).toBe(0);
    expect(countWords("   \n\t  ")).toBe(0);
  });

  it("should correctly count English words and ignore punctuation", () => {
    expect(countWords("Hello world! This is a test.")).toBe(6);
  });

  it("should correctly count Thai words without spaces", () => {
    const count = countWords("การให้คะแนนอัตโนมัติด้วยปัญญาประดิษฐ์");
    expect(count).toBeGreaterThanOrEqual(4);
  });

  it("should handle mixed Thai and English text", () => {
    const count = countWords("ระบบ AI สำหรับ LLMs Auto-Score");
    expect(count).toBeGreaterThanOrEqual(5);
  });
});

describe("formatRemainingTime function", () => {
  it("should format seconds under 1 hour as MM:SS", () => {
    expect(formatRemainingTime(65)).toBe("01:05");
    expect(formatRemainingTime(0)).toBe("00:00");
    expect(formatRemainingTime(3599)).toBe("59:59");
  });

  it("should format hours, minutes, and seconds as HH:MM:SS", () => {
    expect(formatRemainingTime(3600)).toBe("01:00:00");
    expect(formatRemainingTime(3665)).toBe("01:01:05");
  });
});
