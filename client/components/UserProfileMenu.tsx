import { Link, useNavigate } from "react-router-dom";
import { History, Home, LogOut, User, UserCircle } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface UserProfileMenuProps {
  className?: string;
  align?: "end" | "start" | "center";
}

export function UserProfileMenu({ className = "", align = "end" }: UserProfileMenuProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  if (!user) return null;

  const roleLabel = user.role === "teacher" ? "อาจารย์ / ผู้สอน" : "นักศึกษา";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label="เมนูโปรไฟล์และบัญชี"
          className={`group flex h-9 w-9 items-center justify-center overflow-hidden rounded-full border-2 border-transparent text-slate-600 ring-1 ring-slate-300 transition hover:ring-2 hover:ring-emerald-600 dark:text-slate-300 dark:ring-slate-600 dark:hover:ring-emerald-400 ${className}`}
        >
          <span className="flex h-full w-full shrink-0 items-center justify-center overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            {user.avatarUrl ? (
              <img
                src={/^(https?:\/\/|\/)/.test(user.avatarUrl) ? user.avatarUrl : `/uploads/avatars/${user.avatarUrl}`}
                alt={user.name || "โปรไฟล์"}
                className="h-full w-full object-cover"
                referrerPolicy="no-referrer"
              />
            ) : (
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                {user.name ? user.name.charAt(0).toUpperCase() : <User size={15} />}
              </span>
            )}
          </span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align={align} className="w-60 p-2 z-50">
        <DropdownMenuLabel className="font-normal">
          <p className="truncate text-sm font-semibold text-foreground">{user.name}</p>
          <p className="mt-0.5 truncate text-xs text-muted-foreground">{user.email}</p>
          <div className="mt-2 flex items-center gap-1.5">
            <span className="inline-flex items-center text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20">
              {roleLabel}
            </span>
            {user.studentId && (
              <span className="text-[10px] text-muted-foreground font-mono">
                {user.studentId}
              </span>
            )}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link to="/home" className="cursor-pointer flex items-center gap-2">
            <Home size={16} /> <span>ห้องเรียนของฉัน</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link to="/profile" className="cursor-pointer flex items-center gap-2">
            <UserCircle size={16} /> <span>โปรไฟล์และข้อมูลส่วนตัว</span>
          </Link>
        </DropdownMenuItem>
        {user.role === "student" && (
          <DropdownMenuItem asChild>
            <Link to="/history" className="cursor-pointer flex items-center gap-2">
              <History size={16} /> <span>ประวัติการสอบ</span>
            </Link>
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={handleLogout}
          className="cursor-pointer text-red-600 focus:text-red-700 dark:text-red-400 dark:focus:text-red-300 flex items-center gap-2"
        >
          <LogOut size={16} /> <span>ออกจากระบบ</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default UserProfileMenu;
