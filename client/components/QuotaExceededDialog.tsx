import { useSyncExternalStore } from "react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Sparkles, RefreshCw, X, AlertTriangle } from "lucide-react";

export type QuotaResolution = "fallback_3_5" | "retry" | "cancel";

export interface QuotaPromptOptions {
  currentModel?: string;
  fallbackModel?: string;
  message?: string;
}

type Request = {
  options: QuotaPromptOptions;
  resolve: (choice: QuotaResolution) => void;
};

let requests: Request[] = [];
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((l) => l());

/**
 * Prompts user when Gemini 3.8 Flash quota is full, offering fallback to 3.5 Flash, retry, or cancel.
 */
export function promptQuotaFallback(
  options: QuotaPromptOptions = {}
): Promise<QuotaResolution> {
  return new Promise((resolve) => {
    requests = [...requests, { options, resolve }];
    notify();
  });
}

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

export function QuotaExceededDialog() {
  const request = useSyncExternalStore(subscribe, () => requests[0] ?? null);

  const finish = (choice: QuotaResolution) => {
    if (!request || requests[0] !== request) return;
    requests = requests.slice(1);
    request.resolve(choice);
    notify();
  };

  const currentModel = request?.options?.currentModel || "Gemini 3.8 Flash";
  const fallbackModel = request?.options?.fallbackModel || "Gemini 3.5 Flash";

  return (
    <AlertDialog
      open={Boolean(request)}
      onOpenChange={(open) => {
        if (!open) finish("cancel");
      }}
    >
      <AlertDialogContent className="max-w-md rounded-2xl border-amber-500/30 bg-card p-6 shadow-2xl">
        <AlertDialogHeader className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <AlertDialogTitle className="text-lg font-bold text-foreground">
                โควต้า {currentModel} เต็มชั่วคราว
              </AlertDialogTitle>
              <p className="text-xs text-muted-foreground">
                Google AI Quota / Rate limit reached
              </p>
            </div>
          </div>

          <AlertDialogDescription className="text-sm leading-relaxed text-muted-foreground">
            {request?.options?.message || (
              <>
                ขณะนี้โควต้าการใช้งานของโมเดล{" "}
                <span className="font-semibold text-foreground">
                  {currentModel}
                </span>{" "}
                ถึงขีดจำกัดชั่วคราว คุณต้องการสลับไปใช้{" "}
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                  {fallbackModel}
                </span>{" "}
                แทน หรือต้องการลองใหม่อีกครั้ง?
              </>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="mt-5 flex flex-col gap-2.5">
          <Button
            type="button"
            className="w-full justify-center gap-2 bg-emerald-600 text-white shadow-sm hover:bg-emerald-700"
            onClick={(e) => {
              e.preventDefault();
              finish("fallback_3_5");
            }}
          >
            <Sparkles className="h-4 w-4" />
            สลับไปใช้ {fallbackModel}
          </Button>

          <Button
            type="button"
            variant="outline"
            className="w-full justify-center gap-2"
            onClick={(e) => {
              e.preventDefault();
              finish("retry");
            }}
          >
            <RefreshCw className="h-4 w-4" />
            ลองอีกครั้ง ({currentModel})
          </Button>

          <Button
            type="button"
            variant="ghost"
            className="w-full justify-center gap-2 text-muted-foreground hover:text-foreground"
            onClick={(e) => {
              e.preventDefault();
              finish("cancel");
            }}
          >
            <X className="h-4 w-4" />
            ยกเลิก
          </Button>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
}
