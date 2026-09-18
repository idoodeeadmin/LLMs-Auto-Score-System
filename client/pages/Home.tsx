import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { WorkspaceHeader } from "@/components/WorkspaceHeader";
import {
  ArrowRight,
  BookOpen,
  Copy,
  Search,
  X,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { RoomListSkeleton } from "@/components/PageSkeletons";

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
  const visibleRooms = rooms.filter((room) =>
    `${room.name} ${room.section} ${room.class_code}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );

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
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roomName.trim()) {
      toast.error("กรุณากรอกชื่อห้องเรียน");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch("/api/rooms", {
        method: "POST",
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
        const createdRoom = await res.json();
        setRooms((prev) => [createdRoom, ...prev]);
        setRoomName("");
        setRoomSection("");
        closeRoomForm();
        toast.success(
          `สร้างห้องเรียนสำเร็จ! Class Code: ${createdRoom.class_code}`,
        );
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
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="page-heading">ชั้นเรียน</h1>
            <p className="page-description">{rooms.length} ห้องเรียนในบัญชีนี้</p>
          </div>
          <Button
            variant="outline"
            className="h-9 rounded-lg px-4 text-sm"
            aria-expanded={showForm}
            onClick={() => setShowForm(current => !current)}
          >
            {user?.role === "teacher" ? "สร้างห้องเรียน" : "เข้าร่วมห้องเรียน"}
          </Button>
        </div>

        {showForm && (
          <section className="room-form">
            <div className="flex items-center justify-between gap-4">
              <h2 className="section-label">
                {user?.role === "teacher"
                  ? "ข้อมูลห้องเรียนใหม่"
                  : "เข้าร่วมด้วยรหัสห้องเรียน"}
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
                  {saving ? "กำลังสร้าง…" : "บันทึกห้องเรียน"}
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
          <h2 className="section-label">ห้องเรียนทั้งหมด</h2>
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
                  <Link to={`/room/${room.id}`} aria-label={`ไปยังห้องเรียน ${room.name}`} className="classroom-card-arrow">
                    <ArrowRight size={17} />
                  </Link>
                </div>
              </article>;
            })}
          </div>
        )}
      </main>
    </div>
  );
}
