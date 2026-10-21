import type { ReactNode } from "react";
import { ArrowLeft, Settings, CalendarDays, ChevronRight, MoreVertical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserProfileMenu } from "@/components/UserProfileMenu";

export function ExamEditorHeader({ mode, title, onTitleChange, dirty, busy, onBack, onSettings, children, mobilePrimaryAction, mobileMenuItems = [] }: {
  mode: "create" | "edit"; dirty: boolean; busy: boolean;
  title: string; onTitleChange: (title: string) => void;
  onBack: () => void; onSettings: () => void; children: ReactNode;
  mobilePrimaryAction: ReactNode;
  mobileMenuItems?: { label: string; onSelect: () => void; disabled?: boolean }[];
}) {
  return (
    <header className="exam-editor-header">
      <div className="exam-editor-navigation">
        <Button type="button" variant="ghost" size="icon" aria-label="กลับห้องเรียน" onClick={onBack}>
          <ArrowLeft size={19} />
        </Button>
        <div className="min-w-0 flex-1">
          <input className="exam-document-title" aria-label="ชื่อข้อสอบ" title="คลิกเพื่อเปลี่ยนชื่อข้อสอบ"
            value={title} onChange={(event) => onTitleChange(event.target.value)}
            placeholder="ข้อสอบไม่มีชื่อ" disabled={busy} />
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
      <div className="exam-editor-mobile-actions">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button type="button" variant="ghost" size="icon" aria-label="เมนูข้อสอบ" disabled={busy}>
              <MoreVertical size={20} />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="z-[60] min-w-44">
            <DropdownMenuItem onSelect={onSettings}><Settings size={16} className="mr-2" />ตั้งค่าข้อสอบ</DropdownMenuItem>
            {mobileMenuItems.map((item) => (
              <DropdownMenuItem key={item.label} disabled={item.disabled} onSelect={item.onSelect}>{item.label}</DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        {mobilePrimaryAction}
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
