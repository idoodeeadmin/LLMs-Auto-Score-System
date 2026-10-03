import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function countWords(text: string): number {
  if (!text || !text.trim()) return 0;
  // Normalize boundary between Thai script and Latin/numbers so they aren't merged
  const normalized = text
    .replace(/([\u0E00-\u0E7F])([a-zA-Z0-9])/g, "$1 $2")
    .replace(/([a-zA-Z0-9])([\u0E00-\u0E7F])/g, "$1 $2");

  if (typeof Intl !== "undefined" && (Intl as any).Segmenter) {
    const segmenter = new (Intl as any).Segmenter("th", { granularity: "word" });
    const segments = [...segmenter.segment(normalized)].filter((seg: any) => seg.isWordLike);
    return segments.length;
  }
  const thaiTokens = normalized.match(/[\u0E00-\u0E7F]+/g) || [];
  const latinTokens = normalized.replace(/[\u0E00-\u0E7F]+/g, " ").trim().split(/\s+/).filter(Boolean);
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
