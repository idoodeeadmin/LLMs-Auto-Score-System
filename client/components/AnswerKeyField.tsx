import { useLayoutEffect, useRef, useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

interface AnswerKeyFieldProps {
  questionNumber: number;
  value: string;
  onChange: (value: string) => void;
}

const PREVIEW_HEIGHT = 168;

export function AnswerKeyField({ questionNumber, value, onChange }: AnswerKeyFieldProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [expanded, setExpanded] = useState(false);
  const [isLong, setIsLong] = useState(false);

  useLayoutEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    const fullHeight = textarea.scrollHeight;
    setIsLong(fullHeight > PREVIEW_HEIGHT + 2);
    textarea.style.height = `${expanded ? Math.max(PREVIEW_HEIGHT, fullHeight) : PREVIEW_HEIGHT}px`;
    if (!expanded) textarea.scrollTop = 0;
  }, [value, expanded]);

  return (
    <div className="space-y-2">
      <label htmlFor={`answer-key-${questionNumber}`} className="block text-sm font-medium text-slate-700 dark:text-slate-200">
        แนวคำตอบ
      </label>
      <div className="relative">
        <textarea
          ref={textareaRef}
          id={`answer-key-${questionNumber}`}
          aria-label={`แนวคำตอบข้อที่ ${questionNumber}`}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onFocus={() => setExpanded(true)}
          placeholder="คำตอบที่คาดหวังหรือประเด็นสำคัญที่ควรตอบ"
          className="block w-full resize-none overflow-hidden rounded-lg border border-border bg-background px-3 py-3 text-sm leading-6 text-foreground outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
        />
        {isLong && !expanded && (
          <div className="pointer-events-none absolute inset-x-px bottom-px flex h-16 items-end justify-center rounded-b-lg bg-gradient-to-b from-transparent via-background/95 to-background pb-2">
            <button
              type="button"
              aria-expanded={false}
              onClick={() => setExpanded(true)}
              className="pointer-events-auto inline-flex items-center gap-1.5 border-0 bg-transparent px-2 py-1.5 text-sm font-medium text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            >
              ดูแนวคำตอบทั้งหมด <ChevronDown size={16} aria-hidden="true" />
            </button>
          </div>
        )}
      </div>
      {isLong && expanded && (
        <button type="button" aria-expanded={true} onClick={() => setExpanded(false)}
          className="mx-auto flex items-center gap-1.5 border-0 bg-transparent px-2 py-1 text-sm font-medium text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">
          ย่อแนวคำตอบ <ChevronUp size={16} aria-hidden="true" />
        </button>
      )}
    </div>
  );
}
