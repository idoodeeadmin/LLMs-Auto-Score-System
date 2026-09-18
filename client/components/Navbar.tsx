import { BookOpen, History, Home, LogOut, User, UserCircle } from "lucide-react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { NotificationBell } from "@/components/NotificationBell";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface NavbarProps {
  activeTab?: string;
  setActiveTab?: (tab: unknown) => void;
  isSticky?: boolean;
}

export default function Navbar({ isSticky = true }: NavbarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className={`app-navbar z-50 border-b bg-card px-3 py-2.5 md:px-4 ${isSticky ? "sticky top-0" : "relative"}`}>
      <div className="flex w-full items-center gap-3 md:gap-6">
        <Link to="/home" aria-label="Evaly หน้าห้องเรียน" className="flex shrink-0 items-center gap-2.5 font-semibold tracking-tight text-foreground">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-800 text-white shadow-sm dark:bg-emerald-400 dark:text-emerald-950">
            <BookOpen size={20} />
          </span>
          <span className="hidden sm:inline">Evaly</span>
        </Link>

        <nav aria-label="เมนูหลัก" className="flex min-w-0 items-center gap-1">
          <NavLink
            to="/home"
            aria-label="ห้องเรียน"
            className={({ isActive }) => `app-nav-link ${isActive ? "app-nav-link-active" : ""}`}
          >
            <Home size={16} /> <span>ห้องเรียน</span>
          </NavLink>
          {user?.role === "student" && (
            <NavLink
              to="/history"
              aria-label="ประวัติการสอบ"
              className={({ isActive }) => `app-nav-link ${isActive ? "app-nav-link-active" : ""}`}
            >
              <History size={16} /> <span>ประวัติการสอบ</span>
            </NavLink>
          )}
        </nav>

        <div className="ml-auto flex items-center gap-1.5">
          <ThemeToggle />
          <NotificationBell />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                type="button"
                aria-label="เมนูบัญชี"
                className="ml-0.5 flex h-10 w-10 items-center justify-center overflow-hidden rounded-full border-2 border-transparent text-slate-600 ring-1 ring-slate-300 transition hover:ring-2 hover:ring-emerald-700 dark:text-slate-300 dark:ring-slate-600"
              >
                <span className="flex h-full w-full shrink-0 items-center justify-center overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                  {user?.avatarUrl ? (
                    <img src={/^(https?:\/\/|\/)/.test(user.avatarUrl) ? user.avatarUrl : `/uploads/avatars/${user.avatarUrl}`} alt="" className="h-full w-full object-cover" referrerPolicy="no-referrer" />
                  ) : <User size={16} />}
                </span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-60 p-2">
              <DropdownMenuLabel>
                <p className="truncate text-sm font-semibold">{user?.name}</p>
                <p className="mt-1 truncate text-xs font-normal text-slate-500">{user?.email}</p>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {user?.role === "student" && (
                <DropdownMenuItem asChild>
                  <Link to="/history" className="cursor-pointer">
                    <History className="mr-2" size={17} /> ประวัติการสอบ
                  </Link>
                </DropdownMenuItem>
              )}
              <DropdownMenuItem asChild>
                <Link to="/profile" className="cursor-pointer">
                  <UserCircle className="mr-2" size={17} /> ข้อมูลส่วนตัว
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-600 focus:text-red-700">
                <LogOut className="mr-2" size={17} /> ออกจากระบบ
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
