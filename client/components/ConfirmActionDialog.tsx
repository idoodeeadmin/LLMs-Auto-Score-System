import { useSyncExternalStore } from "react";
import {
  AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle,
  AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction,
} from "@/components/ui/alert-dialog";

type Request = { message: string; resolve: (confirmed: boolean) => void };
let requests: Request[] = [];
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((listener) => listener());

/** Resolves only after the user confirms or cancels in the app's dialog. */
export function confirmAction(message: string): Promise<boolean> {
  return new Promise((resolve) => {
    requests = [...requests, { message, resolve }];
    notify();
  });
}

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
};

export function ConfirmActionDialog() {
  const request = useSyncExternalStore(subscribe, () => requests[0] ?? null);
  const finish = (confirmed: boolean) => {
    if (!request || requests[0] !== request) return;
    requests = requests.slice(1);
    request.resolve(confirmed);
    notify();
  };
  const destructive = request ? /ลบ|นำ.*ออก|รีเซ็ต/.test(request.message) : false;

  return (
    <AlertDialog open={Boolean(request)} onOpenChange={(open) => { if (!open) finish(false); }}>
      <AlertDialogContent className="max-w-md rounded-xl">
        <AlertDialogHeader>
          <AlertDialogTitle>{request?.message.includes("ลบ") ? "ยืนยันการลบข้อมูล" : "ยืนยันการดำเนินการ"}</AlertDialogTitle>
          <AlertDialogDescription className="whitespace-pre-wrap leading-relaxed">
            {request?.message}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={(event) => { event.preventDefault(); finish(false); }}>ยกเลิก</AlertDialogCancel>
          <AlertDialogAction className={destructive ? "bg-red-600 text-white hover:bg-red-700" : undefined}
            onClick={(event) => { event.preventDefault(); finish(true); }}>
            {destructive ? "ยืนยัน" : "ดำเนินการต่อ"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
