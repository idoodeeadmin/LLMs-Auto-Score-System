import type { ReactNode } from "react";
import { ArrowLeft, Settings, CalendarDays, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserProfileMenu } from "@/components/UserProfileMenu";

export function ExamEditorHeader({ mode, dirty, busy, onBack, onSettings, children }: {
  mode: "create" | "edit"; dirty: boolean; busy: boolean;
  onBack: () => void; onSettings: () => void; children: ReactNode;
}) {
  return (
    <header className="exam-editor-header">
      <div className="exam-editor-navigation">
        <Button type="button" variant="ghost" size="icon" aria-label="กลับห้องเรียน" onClick={onBack}>
          <ArrowLeft size={19} />
        </Button>
        <div className="min-w-0">
          <p className="text-sm font-semibold">{mode === "create" ? "สร้างข้อสอบ" : "แก้ไขข้อสอบ"}</p>
          <p role="status" className="text-xs text-muted-foreground">
            {busy ? "กำลังดำเนินการ…" : dirty ? "มีการเปลี่ยนแปลงที่ยังไม่บันทึก" : mode === "create" ? "แบบร่างข้อสอบ" : "ไม่มีการเปลี่ยนแปลง"}
          </p>
        </div>
      </div>
      <div className="exam-editor-account"><ThemeToggle /><UserProfileMenu /></div>
      <div className="exam-editor-actions">
        <Button type="button" variant="ghost" disabled={busy} onClick={onSettings} aria-label="เปิดการตั้งค่าข้อสอบ" className="gap-2">
          <Settings size={16} /><span>ตั้งค่า</span>
        </Button>
        {children}
      </div>
    </header>
  );
}

export function ExamScheduleSummary({ start, end, randomized, disabled, onEdit }: {
  start: string; end: string; randomized: boolean; disabled: boolean; onEdit: () => void;
}) {
  const format = (value: string) => {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? "วันที่ไม่ถูกต้อง" : date.toLocaleString("th-TH", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
  };
  return (
    <button type="button" disabled={disabled} onClick={onEdit} className="exam-schedule-summary" aria-label="แก้ไขกำหนดเวลาและการเรียงข้อสอบ">
      <CalendarDays size={20} className="shrink-0 text-emerald-700 dark:text-emerald-300" />
      <span className="min-w-0 flex-1 text-left">
        <span className="block text-sm font-medium">{start || end ? `${start ? `เริ่ม ${format(start)}` : "ไม่กำหนดเวลาเริ่ม"} · ${end ? `สิ้นสุด ${format(end)}` : "ไม่กำหนดเวลาสิ้นสุด"}` : "ยังไม่กำหนดช่วงเวลาสอบ"}</span>
        <span className="mt-1 block text-xs text-muted-foreground">{randomized ? "สุ่มลำดับคำถามสำหรับผู้เรียน" : "เรียงคำถามตามลำดับที่สร้าง"} · กดเพื่อแก้ไขการตั้งค่า</span>
      </span>
      <ChevronRight size={18} className="shrink-0 text-muted-foreground" />
    </button>
  );
}
