import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
import { WorkspaceHeader } from "@/components/WorkspaceHeader";
import {
  ArrowRight,
  Copy,
  LogOut,
  Plus,
  FileText,
  Loader2,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { toast } from "sonner";

interface ExamRoom {
  id: string | number;
  name: string;
  section: string;
  class_code: string;
}

export default function Home() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();

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
        setShowForm(false);
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
        setShowForm(false);
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
        <p className="text-xs text-muted-foreground mb-3">
          {user?.role === "teacher"
            ? "พื้นที่สำหรับผู้สอน"
            : "พื้นที่สำหรับผู้เรียน"}
        </p>
        <div className="flex flex-wrap justify-between items-start gap-5">
          <div>
            <h1 className="page-heading">ห้องเรียนของคุณ</h1>
            <p className="page-description">
              {user?.role === "teacher"
                ? "จัดการข้อสอบ ดูคำตอบ และตรวจทานคะแนนในแต่ละห้องเรียน"
                : "เลือกห้องเรียนเพื่อทำข้อสอบ ติดตามการส่งงาน และดูคะแนน"}
            </p>
          </div>
          <Button
            className="primary-action"
            aria-expanded={showForm}
            onClick={() => setShowForm(!showForm)}
          >
            <Plus size={16} />
            {user?.role === "teacher" ? "สร้างห้องเรียน" : "เข้าร่วมห้องเรียน"}
          </Button>
        </div>

        {showForm && (
          <section className="room-form">
            <h2 className="section-label">
              {user?.role === "teacher"
                ? "ข้อมูลห้องเรียนใหม่"
                : "เข้าร่วมด้วยรหัสห้องเรียน"}
            </h2>
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
          <h2 className="section-label">
            ห้องเรียนทั้งหมด{" "}
            <span className="text-muted-foreground font-normal ml-2">
              {rooms.length}
            </span>
          </h2>
          <label className="room-search">
            <Search size={16} className="text-muted-foreground" />
            <input
              aria-label="ค้นหาห้องเรียน"
              placeholder="ค้นหาวิชา กลุ่มเรียน หรือรหัส"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
        {loading ? (
          <div role="status" className="empty-state">
            <Loader2 className="animate-spin mx-auto mb-3" />
            กำลังโหลดห้องเรียน…
          </div>
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
          <div className="room-list">
            {visibleRooms.map((room) => (
              <article className="room-row" key={room.id}>
                <div>
                  <h3>
                    <Link to={`/room/${room.id}`}>{room.name}</Link>
                  </h3>
                  <p className="mt-1">{room.section}</p>
                </div>
                <div>
                  <small>รหัสห้องเรียน</small>
                  <button
                    className="room-code"
                    aria-label={`คัดลอกรหัสห้องเรียน ${room.class_code}`}
                    onClick={() => copyCode(room.class_code)}
                  >
                    {room.class_code}
                    <Copy size={13} />
                  </button>
                </div>
                <Link className="room-entry" to={`/room/${room.id}`}>
                  ดูข้อสอบ
                  <ArrowRight size={16} />
                </Link>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
