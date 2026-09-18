import { useCallback, useEffect, useMemo, useState, type MouseEvent } from "react";
import { Bell, BookOpen, CheckCircle2, Megaphone, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface NotificationItem {
  id: number;
  type: string;
  message: string;
  link: string;
  is_read: boolean;
  created_at?: string | null;
  data?: Record<string, unknown>;
}

export function NotificationBell() {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [open, setOpen] = useState(false);

  const loadNotifications = useCallback(async () => {
    if (!token) return;
    const response = await fetch("/api/notifications", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.ok) setItems(await response.json());
  }, [token]);

  useEffect(() => {
    if (!user) return;
    loadNotifications();
    const refresh = () => loadNotifications();
    window.addEventListener("evaly:notification", refresh);
    const interval = window.setInterval(loadNotifications, 60_000);
    return () => {
      window.removeEventListener("evaly:notification", refresh);
      window.clearInterval(interval);
    };
  }, [user?.id, loadNotifications]);

  const unread = useMemo(() => items.filter((item) => !item.is_read).length, [items]);

  const markRead = async (item: NotificationItem) => {
    if (!item.is_read) {
      setItems((current) =>
        current.map((value) => value.id === item.id ? { ...value, is_read: true } : value),
      );
      await fetch(`/api/notifications/${item.id}/read`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` },
      });
    }
    setOpen(false);
    navigate(item.link || "/home");
  };

  const markAllRead = async () => {
    setItems((current) => current.map((item) => ({ ...item, is_read: true })));
    await fetch("/api/notifications/read-all", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  };

  const remove = async (event: MouseEvent, item: NotificationItem) => {
    event.stopPropagation();
    setItems((current) => current.filter((value) => value.id !== item.id));
    await fetch(`/api/notifications/${item.id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
  };

  const iconFor = (type: string) => {
    if (type.includes("announcement")) return <Megaphone size={16} />;
    if (type.includes("approved") || type.includes("graded") || type.includes("result")) {
      return <CheckCircle2 size={16} />;
    }
    return <BookOpen size={16} />;
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label={unread ? `การแจ้งเตือนที่ยังไม่อ่าน ${unread} รายการ` : "การแจ้งเตือน"}
          className="relative rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
        >
          <Bell size={19} />
          {unread > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex min-h-4 min-w-4 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white">
              {unread > 9 ? "9+" : unread}
            </span>
          )}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[min(23rem,calc(100vw-1rem))] p-2">
        <div className="flex items-center justify-between px-2 py-1">
          <DropdownMenuLabel className="p-0">การแจ้งเตือน</DropdownMenuLabel>
          {unread > 0 && (
            <button onClick={markAllRead} className="text-xs font-medium text-emerald-800 hover:underline dark:text-emerald-300">
              อ่านทั้งหมด
            </button>
          )}
        </div>
        <DropdownMenuSeparator />
        {items.length === 0 ? (
          <div className="px-4 py-10 text-center text-sm text-slate-500">
            <Bell className="mx-auto mb-2 opacity-30" size={26} />
            ยังไม่มีการแจ้งเตือน
          </div>
        ) : (
          items.map((item) => (
            <DropdownMenuItem key={item.id} onSelect={() => markRead(item)} className="group mb-1 cursor-pointer items-start gap-3 rounded-lg p-3">
              <span className={`mt-0.5 rounded-full p-2 ${item.is_read ? "bg-slate-100 text-slate-500 dark:bg-slate-800" : "bg-emerald-50 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"}`}>
                {iconFor(item.type)}
              </span>
              <span className="min-w-0 flex-1">
                <span className={`block text-sm leading-snug ${item.is_read ? "font-normal text-slate-600 dark:text-slate-400" : "font-semibold"}`}>
                  {item.message}
                </span>
                {item.created_at && (
                  <span className="mt-1 block text-xs text-slate-400">
                    {new Intl.DateTimeFormat("th-TH", { dateStyle: "medium", timeStyle: "short" }).format(new Date(item.created_at))}
                  </span>
                )}
              </span>
              <button
                type="button"
                aria-label="ลบการแจ้งเตือน"
                onClick={(event) => remove(event, item)}
                className="rounded p-1 text-slate-300 opacity-0 transition hover:bg-red-50 hover:text-red-600 group-hover:opacity-100 focus:opacity-100"
              >
                <Trash2 size={14} />
              </button>
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
