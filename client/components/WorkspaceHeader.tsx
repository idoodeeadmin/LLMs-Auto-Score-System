import { Link } from "react-router-dom";
import { BookOpen, ChevronRight, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "./ThemeToggle";

export function WorkspaceHeader() {
  const { user, logout } = useAuth();
  return (
    <header className="workspace-header">
      <Link to="/home" className="workspace-brand">
        <BookOpen size={22} /> Evaly<span>พื้นที่การสอบ</span>
      </Link>
      <div className="workspace-account">
        <span>
          {user?.name}
          <small>{user?.role === "teacher" ? "ผู้สอน" : "ผู้เรียน"}</small>
        </span>
        <ThemeToggle />
        <button
          aria-label="ออกจากระบบ"
          title="ออกจากระบบ"
          onClick={() => {
            logout();
            window.location.assign("/");
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}

export function WorkspaceBreadcrumb({
  roomId,
  current,
}: {
  roomId?: string;
  current: string;
}) {
  return (
    <nav aria-label="เส้นทางนำทาง" className="workspace-breadcrumb">
      <Link to="/home">ห้องเรียน</Link>
      <ChevronRight size={14} />
      {roomId && (
        <>
          <Link to={`/room/${roomId}`}>ข้อสอบในห้องเรียน</Link>
          <ChevronRight size={14} />
        </>
      )}
      <span aria-current="page">{current}</span>
    </nav>
  );
}
