import { PageLoading } from "@/components/RouteLoading";
import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";
import { Loader2, History, ArrowRight, CheckCircle2, AlertCircle, Clock } from "lucide-react";

import { Button } from "@/components/ui/button";

interface SubmissionHistory {
  exam_id: number;
  exam_title: string;
  exam_total_score: number;
  room_id: number;
  room_name: string;
  submission_id?: number;
  status: string;
  submission_score?: number;
  submitted_at?: string;
}

export default function StudentHistory() {
  const { user, token, isLoading } = useAuth();
  const navigate = useNavigate();
  const [history, setHistory] = useState<SubmissionHistory[]>([]);
  const [isFetching, setIsFetching] = useState(true);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "student") navigate("/");
  }, [user, isLoading, navigate]);

  const loadHistory = useCallback(async () => {
    if (!token || user?.role !== "student") return;
    setIsFetching(true);
    setLoadError(false);
    try {
      const response = await fetch("/api/submissions/me", { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) throw new Error("Failed to load history");
      const rows = await response.json();
      if (!Array.isArray(rows)) throw new Error("Invalid history");
      setHistory(rows);
    } catch { setLoadError(true); }
    finally { setIsFetching(false); }
  }, [token, user?.role]);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  if (isLoading || isFetching) {
    return <PageLoading layout="table" />;
  }

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300 text-xs font-medium rounded-full"><CheckCircle2 size={12} /> อนุมัติผลแล้ว</span>;
      case "grading":
      case "submitted":
      case "needs_review":
      case "ready":
        return <span className="inline-flex items-center gap-1 px-3 py-1 bg-muted text-muted-foreground text-xs font-medium rounded-full"><Clock size={12} /> รอตรวจสอบ</span>;
      case "missing":
      default:
        return <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-500 dark:text-slate-400 text-xs font-bold rounded-full"><AlertCircle size={12} /> ยังไม่ส่งคำตอบ</span>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 pb-24">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3 text-slate-900 dark:text-white leading-tight">
              ประวัติการสอบของฉัน
            </h1>
            <p className="text-slate-500 dark:text-slate-400 mt-2 text-sm max-w-lg">
              คะแนนและข้อเสนอแนะจะแสดงหลังผู้สอนอนุมัติผล
            </p>
          </div>
        </div>

        {/* History List */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          {loadError ? (
            <div role="alert" className="p-10 text-center">
              <p>โหลดประวัติการสอบไม่สำเร็จ</p>
              <Button variant="outline" onClick={loadHistory} className="mt-4">ลองใหม่</Button>
            </div>
          ) : history.length === 0 ? (
            <div className="p-16 text-center">
              <History className="h-12 w-12 text-slate-200 mx-auto mb-4" />
              <p className="text-slate-500 dark:text-slate-400 font-medium">ยังไม่มีประวัติการสอบใด ๆ</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {history.map((h) => (
                <div
                  key={`${h.exam_id}-${h.room_id}`} 
                  className="flex flex-col sm:flex-row items-center p-5 sm:p-6 hover:bg-slate-50 dark:bg-slate-900 transition-colors gap-4"
                >
                  <div className="flex-1 w-full space-y-1">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-slate-400 dark:text-slate-500 bg-muted px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">{h.room_name}</span>
                      {renderStatusBadge(h.status)}
                    </div>
                    <Link to={`/room/${h.room_id}/exam/${h.exam_id}`} className="block">
                      <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200 hover:text-indigo-600 transition-colors">{h.exam_title}</h3>
                    </Link>
                    {h.submitted_at && (
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        ส่งเมื่อ: {new Date(h.submitted_at).toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-6 w-full sm:w-auto justify-between sm:justify-end">
                    <div className="text-right">
                      {h.status === "approved" ? (
                        <>
                          <p className="text-xs font-medium text-slate-400 dark:text-slate-500 tracking-wider">คะแนนรวม</p>
                          <p className="text-xl font-bold text-indigo-600">
                            {h.submission_score} <span className="text-sm font-normal text-slate-400 dark:text-slate-500">/ {h.exam_total_score}</span>
                          </p>
                        </>
                      ) : (
                        <>
                          <p className="text-xs font-medium text-slate-400 dark:text-slate-500 tracking-wider">สถานะคะแนน</p>
                          <p className="text-sm text-muted-foreground mt-1">ยังไม่ประกาศ</p>
                        </>
                      )}
                    </div>
                    <Button 
                      onClick={() => navigate(`/room/${h.room_id}/exam/${h.exam_id}`)}
                      variant="ghost"
                      aria-label={`ดูผล ${h.exam_title}`}
                      className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 dark:bg-indigo-900/30"
                    >
                      <span className="mr-2">ดูรายละเอียด</span><ArrowRight size={16} />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
