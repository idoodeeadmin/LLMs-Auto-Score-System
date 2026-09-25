import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function countWords(text: string): number {
  if (!text || !text.trim()) return 0;
  if (typeof Intl !== "undefined" && (Intl as any).Segmenter) {
    const segmenter = new (Intl as any).Segmenter("th", { granularity: "word" });
    const segments = [...segmenter.segment(text)].filter((seg: any) => seg.isWordLike);
    let count = 0;
    for (let i = 0; i < segments.length; i++) {
      const current = segments[i].segment;
      // Merge Thai nominalizing prefixes "การ" and "ความ" with subsequent Thai word
      if (
        (current === "การ" || current === "ความ") &&
        i + 1 < segments.length &&
        /[\u0E00-\u0E7F]/.test(segments[i + 1].segment)
      ) {
        continue;
      }
      count++;
    }
    return count;
  }
  const thaiTokens = text.match(/[\u0E00-\u0E7F]+/g) || [];
  const latinTokens = text.replace(/[\u0E00-\u0E7F]+/g, " ").trim().split(/\s+/).filter(Boolean);
  return thaiTokens.length + latinTokens.length;
}

export function formatRemainingTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) {
    return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}
