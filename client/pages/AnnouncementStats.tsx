import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Loader2, CheckCircle2, Circle } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion } from "framer-motion";
import { toast } from "sonner";

interface ReadStatus {
  id: number;
  name: string;
  student_id: string;
  read_at: string | null;
}

export default function AnnouncementStats() {
  const { roomId, annId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();
  const [stats, setStats] = useState<ReadStatus[]>([]);
  const [isFetching, setIsFetching] = useState(true);

  useEffect(() => {
    if (!isLoading && (!user || user.role !== "teacher")) {
      navigate("/");
    }
  }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || !annId) return;
    const fetchStats = async () => {
      try {
        const res = await fetch(`/api/announcements/${annId}/read-status`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          setStats(await res.json());
        } else {
          toast.error("ไม่สามารถดึงข้อมูลได้");
          navigate(`/room/${roomId}`);
        }
      } catch {
        toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
      } finally {
        setIsFetching(false);
      }
    };
    fetchStats();
  }, [token, annId, roomId, navigate]);

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  const readCount = stats.filter(s => s.read_at).length;
  const totalCount = stats.length;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        <button
          onClick={() => navigate(`/room/${roomId}`)}
          className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors text-sm font-medium"
        >
          <ArrowLeft size={18} /> กลับสู่ห้องเรียน
        </button>

        <div className="bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-xl border border-slate-100 dark:border-slate-700">
          <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-2">สถานะการอ่านประกาศ</h1>
          <p className="text-slate-500 dark:text-slate-400">
            มีนักศึกษาอ่านแล้ว {readCount} จาก {totalCount} คน
          </p>

          <div className="mt-8 space-y-3">
            {stats.length === 0 ? (
              <p className="text-center py-8 text-slate-400">ยังไม่มีนักศึกษาในห้องเรียนนี้</p>
            ) : (
              stats.map((s) => (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  key={s.id}
                  className="flex items-center gap-4 p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700"
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${s.read_at ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-500"}`}>
                    {s.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <p className="font-bold text-slate-800 dark:text-slate-200">{s.name}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{s.student_id || "ไม่มีรหัสนิสิต"}</p>
                  </div>
                  <div className="text-right">
                    {s.read_at ? (
                      <div className="flex flex-col items-end">
                        <span className="flex items-center gap-1 text-emerald-600 text-sm font-bold">
                          <CheckCircle2 size={16} /> อ่านแล้ว
                        </span>
                        <span className="text-[10px] text-slate-400">{new Date(s.read_at).toLocaleString('th-TH')}</span>
                      </div>
                    ) : (
                      <span className="flex items-center gap-1 text-slate-400 text-sm">
                        <Circle size={16} /> ยังไม่อ่าน
                      </span>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
