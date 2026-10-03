import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { WorkspaceHeader } from "@/components/WorkspaceHeader";
import {
  ArrowRight,
  BookOpen,
  Copy,
  LogOut,
  MoreVertical,
  Pencil,
  Search,
  Trash2,
  X,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { RoomListSkeleton } from "@/components/PageSkeletons";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ExamRoom {
  id: string | number;
  name: string;
  section: string;
  class_code: string;
  teacher_name?: string;
  teacher_avatar_url?: string;
}

const roomPalettes = [
  "linear-gradient(135deg, #0f766e 0%, #115e59 100%)",
  "linear-gradient(135deg, #365f73 0%, #294858 100%)",
  "linear-gradient(135deg, #3f6b57 0%, #315444 100%)",
  "linear-gradient(135deg, #59677f 0%, #414d64 100%)",
  "linear-gradient(135deg, #7a5c48 0%, #604535 100%)",
];

const roomPalette = (id: string | number) => {
  const value = String(id).split("").reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return roomPalettes[value % roomPalettes.length];
};

const sectionLabel = (section?: string) => {
  const value = section?.trim();
  if (!value) return "ยังไม่ระบุกลุ่ม";
  if (/^\d+$/.test(value)) return `SEC ${value}`;
  if (/^sec(?:tion)?\s*/i.test(value)) {
    return `SEC ${value.replace(/^sec(?:tion)?\s*/i, "").trim()}`;
  }
  return value;
};


export default function Home() {
  const { user, token } = useAuth();

  const [rooms, setRooms] = useState<ExamRoom[]>([]);
  const [loading, setLoading] = useState(true);
  const [roomName, setRoomName] = useState("");
  const [roomSection, setRoomSection] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingRoom, setEditingRoom] = useState<ExamRoom | null>(null);
  const [roomToLeave, setRoomToLeave] = useState<ExamRoom | null>(null);
  const [leaving, setLeaving] = useState(false);
  const [leaveConfirmed, setLeaveConfirmed] = useState(false);
  const [roomToDelete, setRoomToDelete] = useState<ExamRoom | null>(null);
  const [deleting, setDeleting] = useState(false);
  const visibleRooms = rooms.filter((room) =>
    `${room.name} ${room.section} ${room.class_code}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );

  const handleLeaveRoom = async () => {
    if (!roomToLeave) return;
    setLeaving(true);
    try {
      const res = await fetch(`/api/rooms/${roomToLeave.id}/enrollment`, {
        method: "DELETE",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });
      if (res.ok) {
        setRooms((prev) => prev.filter((r) => r.id !== roomToLeave.id));
        toast.success(`ออกจากห้องเรียน "${roomToLeave.name}" เรียบร้อยแล้ว`);
        setRoomToLeave(null);
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "ไม่สามารถออกจากห้องเรียนได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการออกจากห้องเรียน");
    } finally {
      setLeaving(false);
    }
  };

  const fetchRooms = async () => {
    try {
      setLoading(true);
      setLoadError(false);
      const res = await fetch("/api/rooms", {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });
      if (res.ok) {
        const data = await res.json();
        setRooms(data);
      } else {
        setLoadError(true);
      }
    } catch (err) {
      console.error("Error fetching rooms:", err);
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRooms();
  }, [token]);

  const closeRoomForm = () => {
    setShowForm(false);
    setEditingRoom(null);
    setRoomName("");
    setRoomSection("");
  };

  const openCreateRoom = () => {
    setEditingRoom(null);
    setRoomName("");
    setRoomSection("");
    setShowForm(true);
  };

  const openEditRoom = (room: ExamRoom) => {
    setEditingRoom(room);
    setRoomName(room.name);
    setRoomSection(room.section || "");
    setShowForm(true);
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roomName.trim()) {
      toast.error("กรุณากรอกชื่อห้องเรียน");
      return;
    }

    setSaving(true);
    try {
      const isEditing = Boolean(editingRoom);
      const res = await fetch(isEditing ? `/api/rooms/${editingRoom?.id}` : "/api/rooms", {
        method: isEditing ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          name: roomName.trim(),
          section: roomSection.trim() || "Sec 1",
        }),
      });

      if (res.ok) {
        const updatedRoom = await res.json();
        if (isEditing) {
          setRooms((prev) => prev.map((room) => room.id === editingRoom?.id ? { ...room, name: roomName.trim(), section: roomSection.trim() || "Sec 1" } : room));
        } else {
          setRooms((prev) => [updatedRoom, ...prev]);
        }
        closeRoomForm();
        toast.success(isEditing ? "แก้ไขห้องเรียนเรียบร้อยแล้ว" : `สร้างห้องเรียนสำเร็จ! Class Code: ${updatedRoom.class_code}`);
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "ไม่สามารถสร้างห้องเรียนได้");
      }
    } catch (err) {
      toast.error("เกิดข้อผิดพลาดในการสร้างห้องเรียน");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteRoom = async () => {
    if (!roomToDelete) return;
    setDeleting(true);
    try {
      const res = await fetch(`/api/rooms/${roomToDelete.id}`, {
        method: "DELETE",
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });
      if (!res.ok) {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "ไม่สามารถลบห้องเรียนได้");
        return;
      }
      setRooms((prev) => prev.filter((room) => room.id !== roomToDelete.id));
      toast.success(`ลบห้องเรียน "${roomToDelete.name}" แล้ว`);
      setRoomToDelete(null);
    } catch {
      toast.error("เกิดข้อผิดพลาดในการลบห้องเรียน");
    } finally {
      setDeleting(false);
    }
  };

  const handleJoinRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!joinCode.trim()) {
      toast.error("กรุณากรอกรหัสเชิญเข้าร่วมห้องเรียน");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch("/api/rooms/join", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          class_code: joinCode.trim(),
        }),
      });

      if (res.ok) {
        const joinedRoom = await res.json();
        setRooms((prev) => [
          joinedRoom,
          ...prev.filter((room) => room.id !== joinedRoom.id),
        ]);
        setJoinCode("");
        closeRoomForm();
        toast.success(`เข้าร่วมห้องเรียน "${joinedRoom.name}" สำเร็จ!`);
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "ไม่สามารถเข้าร่วมห้องเรียนได้");
      }
    } catch (err) {
      toast.error("เกิดข้อผิดพลาดในการเข้าร่วมห้องเรียน");
    } finally {
      setSaving(false);
    }
  };

  const copyCode = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      toast.success(`คัดลอกรหัส ${code} แล้ว`);
    } catch {
      toast.error("คัดลอกไม่สำเร็จ กรุณาเลือกรหัสแล้วคัดลอกด้วยตนเอง");
    }
  };


  return (
    <div className="workspace">
      <WorkspaceHeader />
      <main className="room-workspace">
        <div className="room-page-intro">
          <div className="room-page-copy">
            <span className="room-eyebrow">EVALY SCORE</span>
            <h1 className="page-heading">ชั้นเรียน</h1>
            <p className="page-description">พื้นที่รวมชั้นเรียน ข้อสอบ และการติดตามผลของคุณ</p>
          </div>
          <Button
            variant="outline"
            className="room-create-button h-10 rounded-lg px-4 text-sm"
            aria-expanded={showForm}
            onClick={() => showForm ? closeRoomForm() : openCreateRoom()}
          >
            {user?.role === "teacher" ? "สร้างห้องเรียน" : "เข้าร่วมห้องเรียน"}
          </Button>
        </div>

        {showForm && (
          <section className="room-form">
            <div className="flex items-center justify-between gap-4">
              <h2 className="section-label">
                {user?.role === "teacher" ? (editingRoom ? "แก้ไขข้อมูลห้องเรียน" : "ข้อมูลห้องเรียนใหม่") : "เข้าร่วมด้วยรหัสห้องเรียน"}
              </h2>
              <Button type="button" variant="ghost" size="icon" aria-label="ปิดแบบฟอร์มห้องเรียน" onClick={closeRoomForm}>
                <X size={17} />
              </Button>
            </div>
            {user?.role === "teacher" ? (
              <form onSubmit={handleCreateRoom}>
                <label className="field">
                  ชื่อวิชาหรือห้องเรียน
                  <input
                    autoFocus
                    required
                    value={roomName}
                    onChange={(e) => setRoomName(e.target.value)}
                    placeholder="เช่น โครงสร้างข้อมูลและอัลกอริทึม"
                  />
                </label>
                <label className="field">
                  กลุ่มเรียน
                  <input
                    value={roomSection}
                    onChange={(e) => setRoomSection(e.target.value)}
                    placeholder="เช่น Sec 1"
                  />
                </label>
                <Button
                  disabled={saving}
                  type="submit"
                  className="primary-action"
                >
                  {saving ? "กำลังบันทึก…" : editingRoom ? "บันทึกการแก้ไข" : "บันทึกห้องเรียน"}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleJoinRoom}>
                <label className="field">
                  รหัสที่ได้รับจากผู้สอน
                  <input
                    autoFocus
                    required
                    value={joinCode}
                    onChange={(e) => setJoinCode(e.target.value)}
                    placeholder="เช่น CS101-8849"
                  />
                </label>
                <Button
                  disabled={saving}
                  type="submit"
                  className="primary-action"
                >
                  {saving ? "กำลังเข้าร่วม…" : "เข้าร่วมห้องเรียน"}
                </Button>
              </form>
            )}
          </section>
        )}

        <div className="room-toolbar">
                <div className="flex items-baseline gap-2"><h2 className="section-label">ห้องเรียนทั้งหมด</h2><span className="room-count">{visibleRooms.length}</span></div>
          <label className="room-search">
            <Search size={16} className="text-muted-foreground" />
            <input
              aria-label="ค้นหาห้องเรียน"
              placeholder="ค้นหาวิชา กลุ่มเรียน หรือรหัส"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button type="button" aria-label="ล้างคำค้น" onClick={() => setSearch("")}>
                <X size={15} />
              </button>
            )}
          </label>
        </div>
        {loading ? (
          <RoomListSkeleton />
        ) : loadError ? (
          <div role="alert" className="empty-state">
            <p>โหลดห้องเรียนไม่สำเร็จ กรุณาลองอีกครั้ง</p>
            <Button variant="outline" className="mt-4" onClick={fetchRooms}>
              ลองใหม่
            </Button>
          </div>
        ) : visibleRooms.length === 0 ? (
          <div className="empty-state">
            <p>
              {search ? "ไม่พบห้องเรียนที่ตรงกับคำค้น" : "ยังไม่มีห้องเรียน"}
            </p>
            <p className="text-sm mt-2">
              {search
                ? "ลองค้นหาด้วยชื่อวิชาหรือกลุ่มเรียนอื่น"
                : user?.role === "teacher"
                  ? "เริ่มสร้างห้องเรียน แล้วเพิ่มข้อสอบสำหรับผู้เรียนของคุณ"
                  : "กดเข้าร่วมห้องเรียน แล้วกรอกรหัสที่ได้รับจากผู้สอน"}
            </p>
          </div>
        ) : (
          <div className="room-card-grid">
            {visibleRooms.map((room) => {
              const teacherName = room.teacher_name || (user?.role === "teacher" ? user.name : "ผู้สอน");
              const teacherAvatar = room.teacher_avatar_url || (user?.role === "teacher" ? user.avatarUrl : undefined);
              return <article className="classroom-card" key={room.id}>
                {user?.role === "teacher" && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button type="button" className="classroom-card-menu" aria-label={`ตัวเลือกห้องเรียน ${room.name}`} onClick={(event) => event.stopPropagation()}>
                        <MoreVertical size={18} />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-44">
                      <DropdownMenuItem onSelect={() => openEditRoom(room)}><Pencil size={15} className="mr-2" />แก้ไขห้องเรียน</DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-red-600 focus:text-red-700" onSelect={() => setRoomToDelete(room)}><Trash2 size={15} className="mr-2" />ลบห้องเรียน</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
                <Link
                  to={`/room/${room.id}`}
                  className="classroom-card-banner"
                  style={{ background: roomPalette(room.id) }}
                >
                  <span className="classroom-card-mark" aria-hidden="true">{room.name.trim().charAt(0) || "E"}</span>
                  <div className="relative z-10 min-w-0 pr-14">
                    <h3>{room.name}</h3>
                    <p className="classroom-section">{sectionLabel(room.section)}</p>
                    <small>{teacherName}</small>
                  </div>
                  <div className="classroom-avatar" aria-hidden="true">
                    {teacherAvatar ? (
                      <img src={teacherAvatar} alt="" />
                    ) : (
                      <span>{teacherName.trim().charAt(0).toUpperCase()}</span>
                    )}
                  </div>
                </Link>
                <div className="classroom-card-body">
                  <span>รหัสห้องเรียน</span>
                  <button
                    className="classroom-code"
                    aria-label={`คัดลอกรหัสห้องเรียน ${room.class_code}`}
                    onClick={() => copyCode(room.class_code)}
                  >
                    {room.class_code}<Copy size={13} />
                  </button>
                  <p>ข้อสอบ ประกาศ และสมาชิกของห้องเรียน</p>
                </div>
                <div className="classroom-card-footer">
                  <Link to={`/room/${room.id}`} aria-label={`เปิดห้องเรียน ${room.name}`}>
                    <BookOpen size={17} />
                    <span>เปิดห้องเรียน</span>
                  </Link>
                  <div className="flex items-center gap-1">
                    {user?.role === "student" && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                            }}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                            aria-label="ตัวเลือกเพิ่มเติม"
                            title="ตัวเลือกเพิ่มเติม"
                          >
                            <MoreVertical size={15} />
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              setLeaveConfirmed(false);
                              setRoomToLeave(room);
                            }}
                            className="text-red-600 focus:text-red-700 focus:bg-red-50 dark:focus:bg-red-950/40 text-xs cursor-pointer"
                          >
                            <LogOut size={13} className="mr-2" />
                            ออกจากห้องเรียน
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                    <Link to={`/room/${room.id}`} aria-label={`ไปยังห้องเรียน ${room.name}`} className="classroom-card-arrow">
                      <ArrowRight size={17} />
                    </Link>
                  </div>
                </div>
              </article>;
            })}
          </div>
        )}
      </main>

      <AlertDialog
        open={Boolean(roomToLeave)}
        onOpenChange={(open) => {
          if (!open) {
            setRoomToLeave(null);
            setLeaveConfirmed(false);
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-red-600 dark:text-red-400">ยืนยันออกจากห้องเรียน</AlertDialogTitle>
            <AlertDialogDescription className="space-y-3">
              <span>
                คุณแน่ใจหรือไม่ว่าต้องการออกจากห้องเรียน <strong>&ldquo;{roomToLeave?.name}&rdquo;</strong>?
              </span>
              <span className="text-xs text-muted-foreground block">
                ข้อมูลการส่งงานและคะแนนที่คุณเคยทำจะยังคงอยู่ในระบบของอาจารย์ผู้สอน แต่ห้องเรียนนี้จะถูกนำออกจากรายการของคุณ
              </span>
              <label className="flex items-start gap-2.5 pt-2 cursor-pointer text-xs text-slate-700 dark:text-slate-300 select-none">
                <input
                  type="checkbox"
                  checked={leaveConfirmed}
                  onChange={(e) => setLeaveConfirmed(e.target.checked)}
                  className="mt-0.5 rounded border-slate-300 text-red-600 focus:ring-red-500"
                />
                <span>ฉันเข้าใจผลกระทบและยืนยันที่จะออกจากห้องเรียนนี้</span>
              </label>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={leaving}>ยกเลิก</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.preventDefault();
                handleLeaveRoom();
              }}
              disabled={leaving || !leaveConfirmed}
              className="bg-red-600 hover:bg-red-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {leaving ? "กำลังดำเนินการ…" : "ยืนยันออกจากห้องเรียน"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      <AlertDialog open={Boolean(roomToDelete)} onOpenChange={(open) => !open && setRoomToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>ลบห้องเรียนนี้หรือไม่?</AlertDialogTitle>
            <AlertDialogDescription>ห้องเรียน <strong>&ldquo;{roomToDelete?.name}&rdquo;</strong> และข้อมูลที่เกี่ยวข้องจะถูกลบถาวร ไม่สามารถกู้คืนได้</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>ยกเลิก</AlertDialogCancel>
            <AlertDialogAction onClick={(event) => { event.preventDefault(); void handleDeleteRoom(); }} disabled={deleting} className="bg-red-600 text-white hover:bg-red-700">{deleting ? "กำลังลบ…" : "ยืนยันลบห้องเรียน"}</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
