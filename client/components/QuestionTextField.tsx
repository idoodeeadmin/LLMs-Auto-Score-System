import { useEffect, useLayoutEffect, useRef } from "react";

interface QuestionTextFieldProps {
  questionNumber: number;
  value: string;
  onChange: (value: string) => void;
}

export function QuestionTextField({ questionNumber, value, onChange }: QuestionTextFieldProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const fitContent = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.max(48, textarea.scrollHeight)}px`;
  };

  useLayoutEffect(fitContent, [value]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    let previousWidth = textarea.clientWidth;
    const observer = new ResizeObserver(() => {
      if (textarea.clientWidth !== previousWidth) {
        previousWidth = textarea.clientWidth;
        fitContent();
      }
    });
    observer.observe(textarea);
    return () => observer.disconnect();
  }, []);

  return (
    <label className="block space-y-1.5 text-sm font-medium text-slate-700 dark:text-slate-200">
      <span>คำถาม</span>
      <textarea ref={textareaRef} aria-label={`คำถามข้อที่ ${questionNumber}`} value={value}
        onChange={(event) => onChange(event.target.value)} placeholder="พิมพ์โจทย์คำถาม..." rows={1}
        className="block w-full resize-none overflow-hidden rounded-lg border border-border bg-background px-3 py-2.5 text-sm font-normal leading-6 text-foreground outline-none focus:border-primary focus:ring-2 focus:ring-primary/20" />
    </label>
  );
}
