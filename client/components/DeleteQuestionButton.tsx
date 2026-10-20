import { X } from "lucide-react";
import {
  AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogDescription, AlertDialogFooter,
  AlertDialogCancel, AlertDialogAction,
} from "@/components/ui/alert-dialog";

export function DeleteQuestionButton({ questionNumber, onConfirm }: {
  questionNumber: number;
  onConfirm: () => void;
}) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <button type="button" aria-label={`ลบข้อที่ ${questionNumber}`} title="ลบข้อนี้"
          className="rounded-md p-1.5 text-red-600 transition hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950/40 dark:hover:text-red-300">
          <X size={16} />
        </button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>ลบข้อที่ {questionNumber} หรือไม่?</AlertDialogTitle>
          <AlertDialogDescription>
            คำถาม แนวคำตอบ รูปภาพ และเกณฑ์การให้คะแนนของข้อนี้จะถูกลบออก
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>ยกเลิก</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} className="bg-red-600 text-white hover:bg-red-700">
            ลบข้อนี้
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
