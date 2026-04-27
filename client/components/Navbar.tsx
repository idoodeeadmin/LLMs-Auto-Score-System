import { Bell, User, LogOut, Settings, UserCircle, History, Clock, CheckCircle2, ChevronRight, BookOpen, AlertTriangle, Trophy, ShieldCheck } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useState, useEffect, useRef } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";

interface NavbarProps {
  activeTab?: string;
  setActiveTab?: (tab: any) => void;
}

interface Notification {
  type: "deadline_passed" | "ai_graded" | "new_exam" | "deadline_soon" | "result_published";
  exam_id: number;
  exam_title: string;
  room_id: number;
  room_name: string;
  message: string;
  link: string;
}

export default function Navbar({ }: NavbarProps) {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [bellOpen, setBellOpen] = useState(false);
  const [readLinks, setReadLinks] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem("notif_read_links");
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch { return new Set(); }
  });

  // Fetch notifications for all logged-in users
  useEffect(() => {
    if (!token || !user) return;

    const fetchNotifications = async () => {
      try {
        const res = await fetch("/api/notifications", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setNotifications(data);
        }
      } catch { /* silent */ }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); // refresh every 60s
    return () => clearInterval(interval);
  }, [token, user?.role]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Persist readLinks to localStorage on every change
  useEffect(() => {
    localStorage.setItem("notif_read_links", JSON.stringify([...readLinks]));
  }, [readLinks]);

  const unreadCount = notifications.filter(n => !readLinks.has(n.link)).length;

  return (
    <header className="bg-white/90 dark:bg-slate-800/90 border-b border-gray-100 dark:border-slate-800 px-3 md:px-6 py-2 md:py-4 sticky top-0 z-50 shadow-sm backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3 md:gap-6">
        {/* Logo */}
        <Link to="/home" className="flex items-center gap-1.5 md:gap-3 flex-shrink-0 group">
          <div className="w-8 h-8 md:w-12 md:h-12 bg-[#eff6ff] rounded-xl md:rounded-2xl flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
            <svg width="22" height="22" viewBox="0 0 24 24" className="md:w-[28px] md:h-[28px]" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19.0001 5L12.0001 2L5.00006 5L8.50006 6.5V8.5M19.0001 5L15.5001 6.5V8.5M19.0001 5V9M8.50006 8.5C8.50006 8.5 9.66706 8 12.0001 8C14.3331 8 15.5001 8.5 15.5001 8.5M8.50006 8.5V9.5C8.50006 9.95963 8.59059 10.4148 8.76648 10.8394C8.94237 11.264 9.20018 11.6499 9.52519 11.9749C9.85019 12.2999 10.236 12.5577 10.6607 12.7336C11.0853 12.9095 11.5404 13 12.0001 13C12.4597 13 12.9148 12.9095 13.3395 12.7336C13.7641 12.5577 14.1499 12.2999 14.4749 11.9749C14.7999 11.6499 15.0577 11.264 15.2336 10.8394C15.4095 10.4148 15.5001 9.95963 15.5001 9.5V8.5M7.78306 16.703C6.68306 17.388 3.79706 18.785 5.55406 20.534C6.41306 21.39 7.37006 22 8.57106 22H15.4291C16.6311 22 17.5871 21.389 18.4461 20.534C20.2031 18.785 17.3181 17.388 16.2171 16.704C14.9511 15.9174 13.4905 15.5005 12.0001 15.5005C10.5097 15.5005 9.04897 15.9174 7.78306 16.704" stroke="#3B82F6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <h1 className="text-lg md:text-2xl font-black text-gray-900 dark:text-white tracking-tight">Evaly</h1>
        </Link>

        {/* Right side icons */}
        <div className="flex items-center gap-2 md:gap-5 ml-auto">
          
          <ThemeToggle />

          {/* Bell — All users */}
          <DropdownMenu open={bellOpen} onOpenChange={(open) => {
              setBellOpen(open);
              if (open) {
                setReadLinks(new Set(notifications.map(n => n.link)));
              }
            }}>
              <DropdownMenuTrigger asChild>
                <button className="p-1.5 md:p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-full transition-colors relative">
                  <Bell size={20} className="md:w-[22px] md:h-[22px] text-gray-600 dark:text-slate-400" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 min-w-[18px] h-[18px] px-1 bg-red-500 border-2 border-white rounded-full text-white text-[10px] font-bold flex items-center justify-center">
                      {unreadCount > 9 ? "9+" : unreadCount}
                    </span>
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80 rounded-xl mt-1 shadow-xl border-gray-100 dark:border-slate-800 p-2">
                <DropdownMenuLabel className="text-sm font-bold text-gray-800 dark:text-slate-200 px-2 py-1">
                  การแจ้งเตือน
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="my-1" />
                {notifications.length === 0 ? (
                  <div className="py-8 text-center text-gray-400 dark:text-slate-500 dark:text-slate-400 dark:text-slate-500 text-sm">
                    <Bell size={28} className="mx-auto mb-2 opacity-30" />
                    ไม่มีการแจ้งเตือนในขณะนี้
                  </div>
                ) : (
                  notifications.map((notif, idx) => {
                    const isRead = readLinks.has(notif.link);
                    return (
                      <DropdownMenuItem
                        key={idx}
                        asChild
                        className="rounded-lg p-0 cursor-pointer focus:bg-blue-50 dark:bg-blue-900/30"
                      >
                        <Link
                          to={notif.link}
                          className={`flex items-start gap-3 p-3 w-full rounded-lg transition-colors ${
                            isRead
                              ? "bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700/50"
                              : "bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-800/40"
                          }`}
                          onClick={() => {
                            setReadLinks(prev => new Set([...prev, notif.link]));
                            setBellOpen(false);
                          }}
                        >
                          <div className={`mt-0.5 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${{
                              deadline_passed: "bg-orange-100 text-orange-600",
                              ai_graded:       "bg-green-100 text-green-600",
                              new_exam:        "bg-blue-100 text-blue-600",
                              deadline_soon:   "bg-red-100 text-red-600",
                              result_published:"bg-purple-100 text-purple-600",
                            }[notif.type] ?? "bg-gray-100 text-gray-500 dark:text-slate-400 dark:text-slate-500"}`}>
                            {notif.type === "deadline_passed" && <Clock size={16} />}
                            {notif.type === "ai_graded"       && <CheckCircle2 size={16} />}
                            {notif.type === "new_exam"        && <BookOpen size={16} />}
                            {notif.type === "deadline_soon"   && <AlertTriangle size={16} />}
                            {notif.type === "result_published"&& <Trophy size={16} />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm leading-tight ${isRead ? "font-normal text-gray-600 dark:text-slate-400 dark:text-slate-500" : "font-semibold text-gray-800 dark:text-slate-200"}`}>
                              {notif.message}
                            </p>
                            <p className="text-xs text-gray-400 dark:text-slate-500 dark:text-slate-400 dark:text-slate-500 mt-0.5 truncate">{notif.room_name}</p>
                          </div>
                          <ChevronRight size={14} className="text-gray-300 mt-1 flex-shrink-0" />
                        </Link>
                      </DropdownMenuItem>
                    );
                  })
                )}
              </DropdownMenuContent>
            </DropdownMenu>

          {/* Profile avatar + dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="w-9 h-9 md:w-11 md:h-11 bg-[#eff6ff] border border-blue-100 rounded-full flex items-center justify-center hover:bg-blue-100 dark:hover:bg-blue-800/40 transition-colors shadow-sm focus:ring-2 focus:ring-blue-400 focus:outline-none overflow-hidden">
                {user?.avatarUrl ? (
                  <img 
                    src={user.avatarUrl.startsWith("http") ? user.avatarUrl : `/uploads/avatars/${user.avatarUrl}`} 
                    className="w-full h-full object-cover" 
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <User size={18} className="text-[#3B82F6] md:w-5 md:h-5" />
                )}
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 rounded-xl mt-1 shadow-lg border-gray-100 dark:border-slate-800 p-2">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-bold leading-none">{user?.name}</p>
                  <p className="text-xs leading-none text-gray-500 dark:text-slate-400 dark:text-slate-500 uppercase">
                    {user?.role === 'teacher' ? 'อาจารย์' : 'นักศึกษา'}
                  </p>
                  <p className="text-xs leading-none text-gray-400 dark:text-slate-500 dark:text-slate-400 dark:text-slate-500">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-gray-50 dark:bg-slate-900 my-2" />
              {user?.role === 'student' && (
                <DropdownMenuItem asChild className="rounded-lg gap-2 cursor-pointer focus:bg-blue-50 dark:bg-blue-900/30 focus:text-blue-600">
                  <Link to="/history" className="flex items-center w-full">
                    <History className="mr-2" size={18} />
                    <span>ประวัติการสอบ</span>
                  </Link>
                </DropdownMenuItem>
              )}
              <DropdownMenuItem asChild className="rounded-lg gap-2 cursor-pointer focus:bg-blue-50 dark:bg-blue-900/30 focus:text-blue-600">
                <Link to="/profile" className="flex items-center w-full">
                  <UserCircle className="mr-2" size={18} />
                  <span>ข้อมูลส่วนตัว</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="rounded-lg gap-2 cursor-pointer focus:bg-blue-50 dark:bg-blue-900/30 focus:text-blue-600">
                <Link to="/audit-log" className="flex items-center w-full">
                  <ShieldCheck className="mr-2" size={18} />
                  <span>ประวัติการทำรายการ</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-50 dark:bg-slate-900 my-2" />
              <DropdownMenuItem 
                onClick={handleLogout}
                className="rounded-lg gap-2 cursor-pointer text-red-500 focus:bg-red-50 dark:bg-red-900/30 focus:text-red-600 font-medium"
              >
                <LogOut size={18} />
                <span>ออกจากระบบ</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

        </div>
      </div>
    </header>
  );
}