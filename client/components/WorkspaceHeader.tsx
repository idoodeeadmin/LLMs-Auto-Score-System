import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import Navbar from "./Navbar";

export function WorkspaceHeader() { return <Navbar />; }

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
