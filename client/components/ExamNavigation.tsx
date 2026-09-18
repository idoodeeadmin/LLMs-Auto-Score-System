import { NavLink } from "react-router-dom";

export function ExamNavigation({ roomId, examId }: { roomId?: string; examId?: string }) {
  const base = `/room/${roomId}/exam/${examId}`;
  return <nav aria-label="ส่วนของข้อสอบ" className="mb-6 flex gap-6 border-b">
    {[{ to: base, label: "รายละเอียดข้อสอบ" }, { to: `${base}/review`, label: "งานของผู้เรียน" }].map(item =>
      <NavLink key={item.to} to={item.to} end className={({ isActive }) =>
        `border-b-2 px-1 py-3 text-sm font-medium ${isActive ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
        {item.label}
      </NavLink>)}
  </nav>;
}
