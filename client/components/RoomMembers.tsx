import { useEffect, useState } from "react";
import { Users, Search, UserRound, MoreVertical, UserMinus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

interface Member {
  id: number;
  name: string;
  email: string;
  student_id?: string | null;
  avatar_url?: string | null;
  role: string;
}

export function RoomMembers({ roomId, token, canManage = false }: { roomId: string; token: string | null; canManage?: boolean }) {
  const [open, setOpen] = useState(false);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [removingId, setRemovingId] = useState<number | null>(null);
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    setMembers([]);
    setPage(1);
    setSearch("");
    fetch(`/api/rooms/${roomId}/members`, {
      headers: { Authorization: token ? `Bearer ${token}` : "" },
      signal: controller.signal,
    }).then(async response => {
      if (!response.ok) throw new Error("Failed to load members");
      const rows: Member[] = await response.json();
      if (!controller.signal.aborted) setMembers(rows.sort((a, b) =>
        Number(b.role === "teacher") - Number(a.role === "teacher") ||
        a.name.localeCompare(b.name, "th", { numeric: true })));
    }).catch(() => {
      if (!controller.signal.aborted) setError(true);
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [open, roomId, token, retry]);

  const query = search.trim().toLocaleLowerCase();
  const filtered = members.filter(member =>
    `${member.name} ${member.email} ${member.student_id ?? ""}`.toLocaleLowerCase().includes(query));
  const teachers = filtered.filter(member => member.role === "teacher");
  const students = filtered.filter(member => member.role !== "teacher");
  const pages = Math.max(1, Math.ceil(students.length / 20));
  const currentPage = Math.min(page, pages);
  const studentRows = students.slice((currentPage - 1) * 20, currentPage * 20);

  const removeMember = async (member: Member) => {
    if (!window.confirm(`นำ “${member.name}” ออกจากห้องเรียนใช่หรือไม่`)) return;
    setRemovingId(member.id);
    try {
      const response = await fetch(`/api/rooms/${roomId}/members/${member.id}`, {
        method: "DELETE",
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
      const result = await response.json().catch(() => null);
      if (!response.ok) throw new Error(result?.detail || "นำสมาชิกออกไม่สำเร็จ");
      setMembers(current => current.filter(item => item.id !== member.id));
      toast.success(`นำ ${member.name} ออกจากห้องแล้ว`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "นำสมาชิกออกไม่สำเร็จ");
    } finally {
      setRemovingId(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="w-full justify-start gap-2 h-12">
          <Users size={18} /> สมาชิกในห้อง
        </Button>
      </DialogTrigger>
      <DialogContent className="flex max-h-[85dvh] flex-col sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>สมาชิกในห้อง</DialogTitle>
          <DialogDescription>
            {loading || error ? "รายชื่อผู้สอนและผู้เรียนที่เข้าร่วมห้อง" :
              `สมาชิกทั้งหมด ${members.length} คน · ผู้สอน ${members.filter(m => m.role === "teacher").length} คน · นิสิต ${members.filter(m => m.role !== "teacher").length} คน`}
          </DialogDescription>
        </DialogHeader>
        <div className="relative">
          <Search size={16} className="absolute left-3 top-3.5 text-muted-foreground" />
          <Input className="pl-9" aria-label="ค้นหาสมาชิก"
            placeholder="ค้นหาชื่อ รหัสประจำตัว หรืออีเมล"
            value={search} onChange={event => { setSearch(event.target.value); setPage(1); }} />
        </div>
        <div className="min-h-0 overflow-y-auto" aria-busy={loading}>
          {loading ? <p role="status" className="py-8 text-center">กำลังโหลดสมาชิก…</p> :
            error ? <div role="alert" className="py-8 text-center">
              <p>โหลดสมาชิกไม่สำเร็จ</p>
              <Button variant="outline" className="mt-3" onClick={() => setRetry(value => value + 1)}>ลองใหม่</Button>
            </div> : filtered.length === 0 ? <p className="py-8 text-center text-muted-foreground">
              {query ? "ไม่พบสมาชิกที่ตรงกับคำค้น" : "ยังไม่มีสมาชิกในห้อง"}
            </p> : <div className="space-y-6 py-2">
              {teachers.length > 0 && <section aria-labelledby="teacher-members-heading">
                <div className="flex items-center justify-between border-b pb-2">
                  <h3 id="teacher-members-heading" className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">ผู้สอน</h3>
                  <span className="text-xs text-muted-foreground">{teachers.length} คน</span>
                </div>
                <ul className="divide-y">
                  {teachers.map(member => <MemberRow key={member.id} member={member} />)}
                </ul>
              </section>}
              {students.length > 0 && <section aria-labelledby="student-members-heading">
                <div className="flex items-center justify-between border-b pb-2">
                  <h3 id="student-members-heading" className="text-sm font-semibold">นิสิต</h3>
                  <span className="text-xs text-muted-foreground">{students.length} คน</span>
                </div>
                <ul className="divide-y">
                  {studentRows.map(member => <MemberRow key={member.id} member={member} canRemove={canManage}
                    removing={removingId === member.id} onRemove={() => void removeMember(member)} />)}
                </ul>
              </section>}
            </div>}
        </div>
        {!loading && !error && <div className="flex flex-wrap items-center justify-between gap-2 border-t pt-3">
          <p className="text-sm text-muted-foreground" aria-live="polite">
            {students.length ? `นิสิต ${(currentPage - 1) * 20 + 1}–${Math.min(currentPage * 20, students.length)} จาก ${students.length} คน` : "ไม่มีรายชื่อนิสิต"}
          </p>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}>ก่อนหน้า</Button>
            <span className="text-sm">{currentPage} / {pages}</span>
            <Button size="sm" variant="outline" disabled={currentPage === pages} onClick={() => setPage(currentPage + 1)}>ถัดไป</Button>
          </div>
        </div>}
      </DialogContent>
    </Dialog>
  );
}

function MemberRow({ member, canRemove = false, removing = false, onRemove }: {
  member: Member;
  canRemove?: boolean;
  removing?: boolean;
  onRemove?: () => void;
}) {
  const isTeacher = member.role === "teacher";
  return <li className="flex items-start gap-3 py-3">
    <Avatar className="mt-0.5 h-10 w-10 border">
      {member.avatar_url && <AvatarImage src={member.avatar_url} alt={`รูปโปรไฟล์ของ ${member.name}`} className="object-cover" />}
      <AvatarFallback className="text-muted-foreground"><UserRound size={20} aria-hidden="true" /></AvatarFallback>
    </Avatar>
    <div className="min-w-0 flex-1">
      <p className="font-medium">{member.name}</p>
      {member.student_id && <p className="text-sm text-muted-foreground">
          {isTeacher ? "รหัสผู้สอน" : "รหัสนิสิต"} {member.student_id}
        </p>}
      <p className="break-all text-sm text-muted-foreground">{member.email}</p>
    </div>
    <div className="flex shrink-0 items-center gap-1">
      <span className="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground">{isTeacher ? "ผู้สอน" : "นิสิต"}</span>
      {canRemove && !isTeacher && <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button disabled={removing} aria-label={`ตัวเลือกสมาชิก ${member.name}`} className="rounded-full p-2 text-muted-foreground hover:bg-muted disabled:opacity-50">
            {removing ? <Loader2 size={17} className="animate-spin" /> : <MoreVertical size={17} />}
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onSelect={onRemove} className="text-red-600 focus:text-red-600">
            <UserMinus size={16} className="mr-2" />นำออกจากห้อง
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>}
    </div>
  </li>;
}
