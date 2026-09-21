import { BookOpen, History, Home, UserCircle } from "lucide-react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { NotificationBell } from "@/components/NotificationBell";
import { UserProfileMenu } from "@/components/UserProfileMenu";

interface NavbarProps {
  activeTab?: string;
  setActiveTab?: (tab: unknown) => void;
  isSticky?: boolean;
}

export default function Navbar({ isSticky = true }: NavbarProps) {
  const { user, logout } = useAuth();
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
          <NavLink
            to="/profile"
            aria-label="โปรไฟล์"
            className={({ isActive }) => `app-nav-link ${isActive ? "app-nav-link-active" : ""}`}
          >
            <UserCircle size={16} /> <span>โปรไฟล์</span>
          </NavLink>
        </nav>

        <div className="ml-auto flex items-center gap-1.5">
          <ThemeToggle />
          <NotificationBell />
          <UserProfileMenu />
        </div>
      </div>
    </header>
  );
}
