import { PageLoading } from "@/components/RouteLoading";
import { useState, useEffect, useCallback, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";
import {
  History,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Clock,
  Search,
  BookOpen,
  Filter,
  Check,
  Sparkles,
} from "lucide-react";
import { Input } from "@/components/ui/input";
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

  // Filters
  const [selectedRoomId, setSelectedRoomId] = useState<number | "all">("all");
  const [statusFilter, setStatusFilter] = useState<"all" | "approved" | "pending">("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "student") navigate("/");
  }, [user, isLoading, navigate]);

  const loadHistory = useCallback(async () => {
    if (!token || user?.role !== "student") return;
    setIsFetching(true);
    setLoadError(false);
    try {
      const response = await fetch("/api/submissions/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to load history");
      const rows = await response.json();
      if (!Array.isArray(rows)) throw new Error("Invalid history");
      setHistory(rows);
    } catch {
      setLoadError(true);
    } finally {
      setIsFetching(false);
    }
  }, [token, user?.role]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  // Unique rooms list
  const uniqueRooms = useMemo(() => {
    const map = new Map<number, string>();
    history.forEach((h) => {
      if (!map.has(h.room_id)) {
        map.set(h.room_id, h.room_name);
      }
    });
    return Array.from(map.entries()).map(([id, name]) => ({ id, name }));
  }, [history]);

  // Filtered submissions
  const filteredHistory = useMemo(() => {
    return history.filter((h) => {
      if (selectedRoomId !== "all" && h.room_id !== selectedRoomId) return false;
      if (statusFilter === "approved" && h.status !== "approved") return false;
      if (statusFilter === "pending" && h.status === "approved") return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = h.exam_title.toLowerCase().includes(q);
        const matchRoom = h.room_name.toLowerCase().includes(q);
        if (!matchTitle && !matchRoom) return false;
      }
      return true;
    });
  }, [history, selectedRoomId, statusFilter, searchQuery]);

  // Statistics
  const totalSubmitted = history.filter((h) => h.status !== "missing").length;
  const totalApproved = history.filter((h) => h.status === "approved").length;
  const totalScoreGained = history
    .filter((h) => h.status === "approved" && typeof h.submission_score === "number")
    .reduce((sum, h) => sum + (h.submission_score || 0), 0);
  const totalScoreMax = history
    .filter((h) => h.status === "approved" && typeof h.submission_score === "number")
    .reduce((sum, h) => sum + (h.exam_total_score || 0), 0);

  if (isLoading || isFetching) {
    return <PageLoading layout="table" />;
  }

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300 text-xs font-medium rounded-full">
            <CheckCircle2 size={12} /> อนุมัติผลแล้ว
          </span>
        );
      case "grading":
      case "submitted":
      case "needs_review":
      case "ready":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-muted text-muted-foreground text-xs font-medium rounded-full">
            <Clock size={12} /> รอตรวจสอบ
          </span>
        );
      case "missing":
      default:
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-500 dark:text-slate-400 text-xs font-bold rounded-full">
            <AlertCircle size={12} /> ยังไม่ส่งคำตอบ
          </span>
        );
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

        {/* Quick Summary Cards */}
        {history.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-4">
              <div className="w-11 h-11 rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Clock size={22} />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400">ส่งคำตอบแล้ว</p>
                <p className="text-2xl font-bold text-slate-800 dark:text-slate-100 mt-0.5">{totalSubmitted} <span className="text-xs font-normal text-slate-400">ชุด</span></p>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-4">
              <div className="w-11 h-11 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
                <CheckCircle2 size={22} />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400">ประกาศผลคะแนนแล้ว</p>
                <p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-0.5">{totalApproved} <span className="text-xs font-normal text-slate-400">ชุด</span></p>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-4">
              <div className="w-11 h-11 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0">
                <Sparkles size={22} />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-500 dark:text-slate-400">คะแนนรวมที่ได้</p>
                <p className="text-2xl font-bold text-purple-700 dark:text-purple-300 mt-0.5">
                  {totalScoreGained} <span className="text-xs font-normal text-slate-400">/ {totalScoreMax} คะแนน</span>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Filter and Search Toolbar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-white dark:bg-slate-800 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex flex-wrap items-center gap-2 flex-1">
            <div className="relative flex-1 min-w-[200px] max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
              <Input
                placeholder="ค้นหาชื่อข้อสอบ หรือวิชา..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-9 pl-9 text-xs rounded-xl bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700"
              />
            </div>

            {/* Room Filter Dropdown */}
            {uniqueRooms.length > 1 && (
              <select
                value={selectedRoomId}
                onChange={(e) => setSelectedRoomId(e.target.value === "all" ? "all" : Number(e.target.value))}
                className="h-9 px-3 text-xs rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 focus:outline-none"
              >
                <option value="all">ทุกห้องเรียน ({uniqueRooms.length})</option>
                {uniqueRooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Status Pills */}
          <div className="flex p-0.5 bg-slate-100 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 self-start sm:self-auto">
            <button
              onClick={() => setStatusFilter("all")}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                statusFilter === "all"
                  ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-300"
              }`}
            >
              ทั้งหมด
            </button>
            <button
              onClick={() => setStatusFilter("approved")}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                statusFilter === "approved"
                  ? "bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 shadow-sm"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-300"
              }`}
            >
              ประกาศผลแล้ว
            </button>
            <button
              onClick={() => setStatusFilter("pending")}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                statusFilter === "pending"
                  ? "bg-white dark:bg-slate-800 text-blue-700 dark:text-blue-400 shadow-sm"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-300"
              }`}
            >
              รอตรวจ
            </button>
          </div>
        </div>

        {/* History List */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          {loadError ? (
            <div role="alert" className="p-10 text-center">
              <p>โหลดประวัติการสอบไม่สำเร็จ</p>
              <Button variant="outline" onClick={loadHistory} className="mt-4">
                ลองใหม่
              </Button>
            </div>
          ) : filteredHistory.length === 0 ? (
            <div className="p-16 text-center">
              <History className="h-12 w-12 text-slate-200 dark:text-slate-700 mx-auto mb-4" />
              <p className="text-slate-500 dark:text-slate-400 font-medium">
                {searchQuery || selectedRoomId !== "all" || statusFilter !== "all"
                  ? "ไม่พบข้อสอบที่ตรงกับตัวกรองที่เลือก"
                  : "ยังไม่มีประวัติการสอบใด ๆ"}
              </p>
              {(searchQuery || selectedRoomId !== "all" || statusFilter !== "all") && (
                <Button
                  variant="ghost"
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedRoomId("all");
                    setStatusFilter("all");
                  }}
                  className="mt-3 text-xs text-blue-600 hover:underline"
                >
                  ล้างตัวกรองทั้งหมด
                </Button>
              )}
            </div>
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-slate-700/60">
              {filteredHistory.map((h) => (
                <div
                  key={`${h.exam_id}-${h.room_id}`}
                  className="flex flex-col sm:flex-row items-center p-5 sm:p-6 hover:bg-slate-50/70 dark:hover:bg-slate-900/50 transition-colors gap-4"
                >
                  <div className="flex-1 w-full space-y-1">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-slate-400 dark:text-slate-500 bg-muted px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">
                        {h.room_name}
                      </span>
                      {renderStatusBadge(h.status)}
                    </div>
                    <Link
                      to={`/room/${h.room_id}/exam/${h.exam_id}`}
                      className="block"
                    >
                      <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200 hover:text-emerald-700 dark:hover:text-emerald-400 transition-colors">
                        {h.exam_title}
                      </h3>
                    </Link>
                    {h.submitted_at && (
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        ส่งเมื่อ:{" "}
                        {new Date(h.submitted_at).toLocaleDateString("th-TH", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-6 w-full sm:w-auto justify-between sm:justify-end">
                    <div className="text-right">
                      {h.status === "approved" ? (
                        <>
                          <p className="text-xs font-medium text-slate-400 dark:text-slate-500 tracking-wider">
                            คะแนนรวม
                          </p>
                          <p className="text-xl font-bold text-emerald-700 dark:text-emerald-400">
                            {h.submission_score}{" "}
                            <span className="text-sm font-normal text-slate-400 dark:text-slate-500">
                              / {h.exam_total_score}
                            </span>
                          </p>
                        </>
                      ) : (
                        <>
                          <p className="text-xs font-medium text-slate-400 dark:text-slate-500 tracking-wider">
                            สถานะคะแนน
                          </p>
                          <p className="text-sm text-muted-foreground mt-1">
                            ยังไม่ประกาศ
                          </p>
                        </>
                      )}
                    </div>
                    <Button
                      onClick={() =>
                        navigate(`/room/${h.room_id}/exam/${h.exam_id}`)
                      }
                      variant="ghost"
                      aria-label={`ดูผล ${h.exam_title}`}
                      className="text-emerald-800 dark:text-emerald-300 hover:text-emerald-950 dark:hover:text-emerald-200 hover:bg-emerald-50 dark:hover:bg-emerald-950/30"
                    >
                      <span className="mr-2 text-xs font-medium">ดูรายละเอียด</span>
                      <ArrowRight size={16} />
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
