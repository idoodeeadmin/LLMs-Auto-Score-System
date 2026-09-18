import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  BarChart3,
  ClipboardList,
  Eye,
  FileText,
  Loader2,
  Megaphone,
  MoreVertical,
  Paperclip,
  File as FileIcon,
  Pencil,
  Plus,
  Send,
  Trash2,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ThemeToggle } from "@/components/ThemeToggle";
import { NotificationBell } from "@/components/NotificationBell";
import { RoomStreamSkeleton } from "@/components/PageSkeletons";
import { RoomMembers } from "@/components/RoomMembers";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

interface Exam {
  id: number;
  title: string;
  total_score: number;
  description?: string;
  start_date?: string | null;
  end_date?: string | null;
  created_at: string;
}

interface RoomInfo {
  id: number;
  name: string;
  section?: string;
  class_code: string;
}

interface Announcement {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at?: string | null;
  is_read?: number | null;
  read_count?: number;
  attachments?: AnnouncementAttachment[];
}

interface AnnouncementAttachment {
  url: string;
  name: string;
  type: string;
  size: number;
}


type FeedItem =
  | { kind: "announcement"; date: string; value: Announcement }
  | { kind: "exam"; date: string; value: Exam };

const formatDate = (value?: string | null) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("th-TH", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

export default function RoomDetail() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading: authLoading } = useAuth();
  const headers = { Authorization: token ? `Bearer ${token}` : "" };

  const [room, setRoom] = useState<RoomInfo | null>(null);
  const [exams, setExams] = useState<Exam[]>([]);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [composerOpen, setComposerOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [savingAnnouncement, setSavingAnnouncement] = useState(false);
  const [announcementFiles, setAnnouncementFiles] = useState<File[]>([]);
  const [announcementAttachments, setAnnouncementAttachments] = useState<AnnouncementAttachment[]>([]);

  const loadData = useCallback(async () => {
    if (!roomId || !token) {
      if (!authLoading) setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const [roomResponse, examsResponse, announcementResponse] = await Promise.all([
        fetch(`/api/rooms/${roomId}`, { headers }),
        fetch(`/api/rooms/${roomId}/exams`, { headers }),
        fetch(`/api/rooms/${roomId}/announcements`, { headers }),
      ]);
      if (!roomResponse.ok) throw new Error("ไม่พบห้องเรียนหรือคุณไม่มีสิทธิ์เข้าถึง");
      setRoom(await roomResponse.json());
      if (examsResponse.ok) setExams(await examsResponse.json());
      if (announcementResponse.ok) {
        const rows: Announcement[] = await announcementResponse.json();
        setAnnouncements(rows);
        if (user?.role === "student") {
          const unread = rows.filter((item) => !item.is_read);
          await Promise.all(
            unread.map((item) =>
              fetch(`/api/announcements/${item.id}/read`, { method: "POST", headers }),
            ),
          );
          if (unread.length) {
            setAnnouncements((current) => current.map((item) => ({ ...item, is_read: 1 })));
          }
        }
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "โหลดข้อมูลห้องเรียนไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }, [roomId, token, user?.role, authLoading]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (!authLoading && !user) navigate("/", { replace: true });
  }, [authLoading, user, navigate]);

  useEffect(() => {
    const refresh = () => loadData();
    window.addEventListener("evaly:notification", refresh);
    return () => window.removeEventListener("evaly:notification", refresh);
  }, [loadData]);

  useEffect(() => {
    if (!loading && window.location.hash) {
      document.querySelector(window.location.hash)?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [loading]);

  const feed = useMemo<FeedItem[]>(() => {
    const items: FeedItem[] = [
      ...announcements.map((value) => ({
        kind: "announcement" as const,
        date: value.updated_at || value.created_at,
        value,
      })),
      ...exams.map((value) => ({
        kind: "exam" as const,
        date: value.created_at,
        value,
      })),
    ];
    return items.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }, [announcements, exams]);

  const upcoming = useMemo(
    () =>
      exams
        .filter((exam) => exam.end_date && new Date(exam.end_date).getTime() > Date.now())
        .sort((a, b) => new Date(a.end_date!).getTime() - new Date(b.end_date!).getTime())
        .slice(0, 3),
    [exams],
  );

  const resetAnnouncementForm = () => {
    setTitle("");
    setContent("");
    setEditingId(null);
    setAnnouncementFiles([]);
    setAnnouncementAttachments([]);
    setComposerOpen(false);
  };

  const saveAnnouncement = async (event: FormEvent) => {
    event.preventDefault();
    if (!title.trim() || !content.trim()) {
      toast.error("กรอกหัวข้อและรายละเอียดประกาศให้ครบ");
      return;
    }
    setSavingAnnouncement(true);
    try {
      let attachments = announcementAttachments;
      if (announcementFiles.length) {
        const formData = new FormData();
        announcementFiles.forEach(file => formData.append("files", file));
        const uploadResponse = await fetch(`/api/rooms/${roomId}/announcements/attachments`, {
          method: "POST", headers, body: formData,
        });
        const uploadResult = await uploadResponse.json().catch(() => null);
        if (!uploadResponse.ok) throw new Error(uploadResult?.detail || "อัปโหลดไฟล์แนบไม่สำเร็จ");
        attachments = [...attachments, ...(uploadResult.attachments ?? [])];
      }
      const response = await fetch(
        editingId
          ? `/api/rooms/${roomId}/announcements/${editingId}`
          : `/api/rooms/${roomId}/announcements`,
        {
          method: editingId ? "PUT" : "POST",
          headers: { ...headers, "Content-Type": "application/json" },
          body: JSON.stringify({ title: title.trim(), content: content.trim(), attachments }),
        },
      );
      const data = await response.json().catch(() => null);
      if (!response.ok) throw new Error(data?.detail || "บันทึกประกาศไม่สำเร็จ");
      setAnnouncements((current) =>
        editingId
          ? current.map((item) => (item.id === editingId ? data : item))
          : [data, ...current],
      );
      toast.success(editingId ? "แก้ไขประกาศแล้ว" : "เผยแพร่ประกาศแล้ว");
      resetAnnouncementForm();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "บันทึกประกาศไม่สำเร็จ");
    } finally {
      setSavingAnnouncement(false);
    }
  };

  const beginEditAnnouncement = (item: Announcement) => {
    setEditingId(item.id);
    setTitle(item.title);
    setContent(item.content);
    setAnnouncementAttachments(item.attachments ?? []);
    setAnnouncementFiles([]);
    setComposerOpen(true);
    window.scrollTo({ top: 180, behavior: "smooth" });
  };

  const deleteAnnouncement = async (item: Announcement) => {
    if (!window.confirm(`ลบประกาศ “${item.title}” ใช่หรือไม่`)) return;
    const response = await fetch(`/api/rooms/${roomId}/announcements/${item.id}`, {
      method: "DELETE",
      headers,
    });
    if (!response.ok) {
      const data = await response.json().catch(() => null);
      toast.error(data?.detail || "ลบประกาศไม่สำเร็จ");
      return;
    }
    setAnnouncements((current) => current.filter((value) => value.id !== item.id));
    if (editingId === item.id) resetAnnouncementForm();
    toast.success("ลบประกาศแล้ว");
  };

  const deleteExam = async (exam: Exam) => {
    if (!window.confirm(`ลบข้อสอบ “${exam.title}” และคำตอบที่เกี่ยวข้องทั้งหมดใช่หรือไม่`)) return;
    const response = await fetch(`/api/rooms/${roomId}/exams/${exam.id}`, {
      method: "DELETE",
      headers,
    });
    if (!response.ok) {
      const data = await response.json().catch(() => null);
      toast.error(data?.detail || "ลบข้อสอบไม่สำเร็จ");
      return;
    }
    setExams((current) => current.filter((value) => value.id !== exam.id));
    toast.success("ลบข้อสอบแล้ว");
  };

  if (loading) {
    return <RoomStreamSkeleton />;
  }

  return (
    <div className="min-h-screen bg-[#f8f9fa] dark:bg-slate-950">
      <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-[#1E1E1E] md:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <button aria-label="กลับหน้าห้องเรียน" onClick={() => navigate("/home")} className="rounded-full p-2 text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800">
            <ArrowLeft size={20} />
          </button>
          <div className="min-w-0">
            <h1 className="truncate text-base font-semibold text-slate-900 dark:text-white">{room?.name}</h1>
            <p className="truncate text-xs text-slate-500">{room?.section || "ห้องเรียน"}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <ThemeToggle />
          <NotificationBell />
          {user?.role === "teacher" && (
            <Button onClick={() => navigate(`/room/${roomId}/create-exam`)} className="ml-2 hidden h-9 sm:flex">
              <Plus size={16} className="mr-1" /> สร้างข้อสอบ
            </Button>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-3 pb-12 pt-5 sm:px-5">
        <section className="relative mb-6 overflow-hidden rounded-xl bg-[#245b50] px-6 py-8 text-white shadow-sm sm:px-9 sm:py-10">
          <div className="relative max-w-3xl">
            <p className="mb-2 text-xs font-medium text-emerald-100">{room?.section || "พื้นที่การสอบ"}</p>
            <h2 className="text-2xl font-semibold sm:text-3xl">{room?.name}</h2>
            <p className="mt-3 text-sm text-emerald-50/85">
              ประกาศ งานที่มอบหมาย และความคืบหน้าของชั้นเรียน
            </p>
          </div>
        </section>

        <div className="grid items-start gap-5 lg:grid-cols-[230px_minmax(0,1fr)]">
          <aside className="space-y-4">
            <RoomMembers roomId={roomId!} token={token} canManage={user?.role === "teacher"} />
            <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-[#1E1E1E]">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">รหัสชั้นเรียน</p>
                <button
                  onClick={() => navigator.clipboard.writeText(room?.class_code || "")}
                  className="text-xs font-medium text-emerald-700 hover:underline dark:text-emerald-300"
                >
                  คัดลอก
                </button>
              </div>
              <p className="mt-3 break-all font-mono text-xl font-semibold tracking-wider text-emerald-800 dark:text-emerald-300">{room?.class_code}</p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-[#1E1E1E]">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{user?.role === "teacher" ? "งานล่าสุด" : "ใกล้ครบกำหนด"}</p>
                {user?.role === "teacher" && (
                  <button onClick={() => navigate(`/room/${roomId}/analytics`)} className="text-slate-400 hover:text-emerald-700" title="ภาพรวมห้องเรียน">
                    <BarChart3 size={17} />
                  </button>
                )}
              </div>
              {upcoming.length === 0 ? (
                <p className="text-xs leading-5 text-slate-500">ไม่มีงานที่ใกล้ครบกำหนด</p>
              ) : (
                <div className="space-y-3">
                  {upcoming.map((exam) => (
                    <button key={exam.id} onClick={() => navigate(`/room/${roomId}/exam/${exam.id}`)} className="block w-full text-left">
                      <span className="block truncate text-xs font-medium text-slate-700 hover:text-emerald-700 dark:text-slate-200">{exam.title}</span>
                      <span className="mt-0.5 block text-[11px] text-slate-400">ครบกำหนด {formatDate(exam.end_date)}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </aside>

          <section className="min-w-0 space-y-4">
            {user?.role === "teacher" && (
              <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-[#1E1E1E]">
                {!composerOpen ? (
                  <div className="flex items-center gap-3 p-4">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                      <Megaphone size={19} />
                    </span>
                    <button onClick={() => setComposerOpen(true)} className="flex-1 rounded-full border border-slate-300 px-5 py-2.5 text-left text-sm text-slate-500 transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-900">
                      ประกาศบางอย่างให้ชั้นเรียน…
                    </button>
                    <Button variant="outline" size="sm" onClick={() => navigate(`/room/${roomId}/create-exam`)} className="hidden sm:flex">
                      <ClipboardList size={15} className="mr-1.5" /> มอบหมายข้อสอบ
                    </Button>
                  </div>
                ) : (
                  <form onSubmit={saveAnnouncement} className="p-5">
                    <div className="mb-4 flex items-center justify-between">
                      <h3 className="text-sm font-semibold">{editingId ? "แก้ไขประกาศ" : "ประกาศถึงชั้นเรียน"}</h3>
                      <button type="button" onClick={resetAnnouncementForm} className="rounded-full p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"><X size={18} /></button>
                    </div>
                    <div className="space-y-3">
                      <Input value={title} onChange={(event) => setTitle(event.target.value)} maxLength={255} placeholder="หัวข้อ" />
                      <Textarea value={content} onChange={(event) => setContent(event.target.value)} maxLength={10000} rows={4} placeholder="เขียนประกาศให้ชั้นเรียน" />
                      <div>
                        <label className="inline-flex cursor-pointer items-center gap-2 rounded-md border px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-900">
                          <Paperclip size={16} /> แนบไฟล์
                          <input type="file" multiple className="sr-only"
                            accept="image/jpeg,image/png,image/gif,image/webp,application/pdf,text/plain,.doc,.docx,.xls,.xlsx,.ppt,.pptx"
                            onChange={event => {
                              const files = Array.from(event.target.files ?? []);
                              event.target.value = "";
                              if (announcementAttachments.length + announcementFiles.length + files.length > 10) {
                                toast.error("แนบได้ไม่เกิน 10 ไฟล์ต่อประกาศ"); return;
                              }
                              if (files.some(file => file.size === 0 || file.size > 10 * 1024 * 1024)) {
                                toast.error("แต่ละไฟล์ต้องมีขนาดไม่เกิน 10 MB"); return;
                              }
                              setAnnouncementFiles(current => [...current, ...files]);
                            }} />
                        </label>
                        <span className="ml-3 text-xs text-muted-foreground">รูปภาพ, PDF, Word, Excel, PowerPoint หรือ TXT · ไม่เกิน 10 MB</span>
                      </div>
                      {(announcementAttachments.length > 0 || announcementFiles.length > 0) && <div className="space-y-2 rounded-lg border p-3">
                        {announcementAttachments.map((attachment, index) => <AttachmentRow key={attachment.url} name={attachment.name}
                          onRemove={() => setAnnouncementAttachments(current => current.filter((_, itemIndex) => itemIndex !== index))} />)}
                        {announcementFiles.map((file, index) => <AttachmentRow key={`${file.name}-${index}`} name={file.name}
                          onRemove={() => setAnnouncementFiles(current => current.filter((_, itemIndex) => itemIndex !== index))} />)}
                      </div>}
                      <div className="flex justify-end gap-2">
                        <Button type="button" variant="ghost" onClick={resetAnnouncementForm}>ยกเลิก</Button>
                        <Button type="submit" disabled={savingAnnouncement}>
                          {savingAnnouncement ? <Loader2 size={16} className="mr-2 animate-spin" /> : <Send size={16} className="mr-2" />}
                          {editingId ? "บันทึก" : "โพสต์"}
                        </Button>
                      </div>
                    </div>
                  </form>
                )}
              </div>
            )}

            {user?.role === "teacher" && (
              <Button onClick={() => navigate(`/room/${roomId}/create-exam`)} className="flex w-full sm:hidden">
                <Plus size={16} className="mr-2" /> มอบหมายข้อสอบ
              </Button>
            )}

            {feed.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-300 bg-white py-16 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-[#1E1E1E]">
                <FileText className="mx-auto mb-2 opacity-30" />
                ยังไม่มีประกาศหรืองานในชั้นเรียนนี้
              </div>
            ) : (
              feed.map((item) =>
                item.kind === "announcement" ? (
                  <AnnouncementPost
                    key={`announcement-${item.value.id}`}
                    item={item.value}
                    isTeacher={user?.role === "teacher"}
                    onEdit={beginEditAnnouncement}
                    onDelete={deleteAnnouncement}
                    onStats={(id) => navigate(`/room/${roomId}/announcement/${id}/stats`)}
                  />
                ) : (
                  <ExamPost
                    key={`exam-${item.value.id}`}
                    exam={item.value}
                    isTeacher={user?.role === "teacher"}
                    onOpen={() => navigate(`/room/${roomId}/exam/${item.value.id}`)}
                    onEdit={() => navigate(`/room/${roomId}/exam/${item.value.id}/edit`)}
                    onDelete={() => deleteExam(item.value)}
                  />
                ),
              )
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

function AnnouncementPost({
  item,
  isTeacher,
  onEdit,
  onDelete,
  onStats,
}: {
  item: Announcement;
  isTeacher: boolean;
  onEdit: (item: Announcement) => void;
  onDelete: (item: Announcement) => void;
  onStats: (id: number) => void;
}) {
  return (
    <article id={`announcement-${item.id}`} className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-[#1E1E1E]">
      <div className="flex items-start gap-3 p-5">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          <Megaphone size={18} />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-medium text-slate-500">ผู้สอนโพสต์ประกาศ</p>
              <h3 className="mt-1 font-semibold text-slate-900 dark:text-white">{item.title}</h3>
              <p className="mt-1 text-xs text-slate-400">{formatDate(item.updated_at || item.created_at)}{item.updated_at ? " · แก้ไขแล้ว" : ""}</p>
            </div>
            {isTeacher && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button aria-label={`ตัวเลือกประกาศ ${item.title}`} className="shrink-0 rounded-full p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">
                    <MoreVertical size={18} />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-44">
                  <DropdownMenuItem onSelect={() => onStats(item.id)}><Eye size={16} className="mr-2" />สถานะการอ่าน</DropdownMenuItem>
                  <DropdownMenuItem onSelect={() => onEdit(item)}><Pencil size={16} className="mr-2" />แก้ไขประกาศ</DropdownMenuItem>
                  <DropdownMenuItem onSelect={() => onDelete(item)} className="text-red-600 focus:text-red-600"><Trash2 size={16} className="mr-2" />ลบประกาศ</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
          <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-700 dark:text-slate-300">{item.content}</p>
          {!!item.attachments?.length && <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {item.attachments.map(attachment => <a key={attachment.url} href={attachment.url} target="_blank" rel="noreferrer"
              className="flex min-w-0 items-center gap-3 rounded-lg border p-3 text-sm hover:bg-slate-50 dark:hover:bg-slate-900">
              {attachment.type.startsWith("image/")
                ? <img src={attachment.url} alt="" className="h-10 w-10 rounded object-cover" />
                : <span className="flex h-10 w-10 items-center justify-center rounded bg-muted"><FileIcon size={18} /></span>}
              <span className="min-w-0 flex-1 truncate">{attachment.name}</span>
            </a>)}
          </div>}
          {isTeacher && <p className="mt-4 text-xs text-slate-400">อ่านแล้ว {item.read_count || 0} คน</p>}
        </div>
      </div>
    </article>
  );
}

function AttachmentRow({ name, onRemove }: { name: string; onRemove: () => void }) {
  return <div className="flex items-center gap-2 text-sm">
    <FileIcon size={16} className="shrink-0 text-muted-foreground" />
    <span className="min-w-0 flex-1 truncate">{name}</span>
    <button type="button" aria-label={`นำไฟล์ ${name} ออก`} onClick={onRemove} className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground">
      <X size={15} />
    </button>
  </div>;
}

function ExamPost({
  exam,
  isTeacher,
  onOpen,
  onEdit,
  onDelete,
}: {
  exam: Exam;
  isTeacher: boolean;
  onOpen: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <article className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-[#1E1E1E]">
      <div className="flex items-start gap-3 p-5">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
          <ClipboardList size={19} />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <button onClick={onOpen} className="min-w-0 text-left">
              <p className="text-xs font-medium text-slate-500">ผู้สอนมอบหมายข้อสอบใหม่</p>
              <h3 className="mt-1 truncate font-semibold text-slate-900 hover:text-emerald-800 dark:text-white dark:hover:text-emerald-300">{exam.title}</h3>
              <p className="mt-1 text-xs text-slate-400">{formatDate(exam.created_at)}</p>
            </button>
            {isTeacher && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button aria-label={`ตัวเลือกข้อสอบ ${exam.title}`} className="shrink-0 rounded-full p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">
                    <MoreVertical size={18} />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40">
                  <DropdownMenuItem onSelect={onEdit}><Pencil size={16} className="mr-2" />แก้ไขข้อสอบ</DropdownMenuItem>
                  <DropdownMenuItem onSelect={onDelete} className="text-red-600 focus:text-red-600"><Trash2 size={16} className="mr-2" />ลบข้อสอบ</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
          {exam.description && <p className="mt-4 line-clamp-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{exam.description}</p>}
          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
            <span>{exam.total_score} คะแนน</span>
            {exam.end_date && <span>ครบกำหนด {formatDate(exam.end_date)}</span>}
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button size="sm" onClick={onOpen}>{isTeacher ? "ดูข้อสอบ" : "ดูงานและเกณฑ์"}</Button>

          </div>
        </div>
      </div>


    </article>
  );
}
