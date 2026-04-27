import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, Search, Download } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type SubmissionStatus = "missing" | "ready" | "needs_review" | "approved";

interface StudentSubmission {
  student_id: number;
  name: string;
  email: string;
  student_code?: string;
  status: SubmissionStatus;
  total_score?: number;
  submitted_at?: string;
}

interface ExamInfo {
  id: number;
  title: string;
  total_score: number;
}

export default function ExamScoreboard() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();

  const [isFetching, setIsFetching] = useState(true);
  const [students, setStudents] = useState<StudentSubmission[]>([]);
  const [exam, setExam] = useState<ExamInfo | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [isLoading, navigate, user]);

  useEffect(() => {
    if (!token || !roomId || !examId) return;
    const run = async () => {
      setIsFetching(true);
      try {
        const [subRes, examRes] = await Promise.all([
          fetch(`/api/rooms/${roomId}/exams/${examId}/submissions`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch(`/api/rooms/${roomId}/exams/${examId}`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);
        if (subRes.ok) setStudents(await subRes.json());
        else toast.error("โหลดคะแนนนักเรียนไม่สำเร็จ");
        if (examRes.ok) setExam(await examRes.json());
      } catch {
        toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
      } finally {
        setIsFetching(false);
      }
    };
    run();
  }, [token, roomId, examId]);

  const handleExportCSV = async () => {
    if (!token) return;
    try {
      const response = await fetch(`/api/rooms/${roomId}/exams/${examId}/export-csv`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scores_${exam?.title.replace(/\s+/g, '_') || 'exam'}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        toast.success("ดาวน์โหลดไฟล์ CSV สำเร็จ");
      } else {
        toast.error("ส่งออกไฟล์ไม่สำเร็จ");
      }
    } catch (e) {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    }
  };

  const filteredAndSorted = useMemo(() => {
    const filtered = students.filter((s) => {
      const q = search.toLowerCase();
      return (
        s.name.toLowerCase().includes(q) ||
        (s.student_code || "").toLowerCase().includes(q) ||
        s.email.toLowerCase().includes(q)
      );
    });

    return filtered.sort((a, b) => {
      const aScore = a.total_score ?? -1;
      const bScore = b.total_score ?? -1;
      return bScore - aScore;
    });
  }, [search, students]);

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 pb-10">
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 md:px-8 py-8 space-y-6">
        <button
          onClick={() => navigate(`/room/${roomId}/analytics`)}
          className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:text-slate-200"
        >
          <ArrowLeft size={16} /> กลับหน้า analytics ห้อง
        </button>

        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">{exam?.title}</h1>
            <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 mt-1">คะแนนเต็ม {exam?.total_score ?? "-"} · ตารางคะแนนรายนักเรียน</p>
          </div>
          <button
            onClick={handleExportCSV}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-medium transition-all shadow-sm shadow-emerald-100 active:scale-95"
          >
            <Download size={18} />
            ส่งออก CSV
          </button>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 dark:border-slate-700">
            <div className="relative max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 w-4 h-4" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="ค้นหาชื่อ / รหัส / อีเมล"
                className="pl-9"
              />
            </div>
          </div>

          <div className="hidden md:grid grid-cols-12 gap-3 px-6 py-3 text-sm font-bold text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-700">
            <div className="col-span-5">นักเรียน</div>
            <div className="col-span-3 text-center">สถานะ</div>
            <div className="col-span-2 text-right">คะแนน</div>
            <div className="col-span-2 text-right">รายละเอียด</div>
          </div>

          <div className="divide-y divide-slate-100">
            {filteredAndSorted.length === 0 ? (
              <div className="px-4 py-12 text-center text-slate-400 dark:text-slate-500">ไม่พบข้อมูลนักเรียน</div>
            ) : (
              filteredAndSorted.map((s) => (
                <div key={s.student_id} className="flex flex-col md:grid md:grid-cols-12 gap-3 md:gap-3 px-4 md:px-6 py-4 items-start md:items-center border-b border-slate-50 dark:border-slate-800 last:border-0 hover:bg-slate-50/50 transition-colors">
                  <div className="w-full md:col-span-5 min-w-0 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-900 flex items-center justify-center text-slate-500 font-bold text-xs">
                      {s.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="font-bold md:font-medium text-slate-800 dark:text-slate-200 truncate text-sm md:text-base">{s.name}</p>
                      <p className="text-[10px] md:text-xs text-slate-500 dark:text-slate-400 truncate">{s.student_code || s.email}</p>
                    </div>
                    <div className="md:hidden">
                       <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                         s.status === 'approved' ? 'bg-green-100 text-green-700' : 
                         s.status === 'missing' ? 'bg-slate-100 text-slate-400' : 'bg-blue-100 text-blue-700'
                       }`}>
                         {s.status}
                       </span>
                    </div>
                  </div>
                  <div className="hidden md:block md:col-span-3 text-center text-sm">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                      s.status === 'approved' ? 'bg-green-100 text-green-700' : 
                      s.status === 'missing' ? 'bg-slate-100 text-slate-400' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {s.status}
                    </span>
                  </div>
                  <div className="w-full md:col-span-2 flex md:justify-end items-center justify-between border-t border-slate-50 md:border-0 pt-2 md:pt-0">
                    <span className="md:hidden text-[10px] text-slate-400 font-bold uppercase">คะแนนรวม</span>
                    <p className="font-bold text-indigo-700 text-sm md:text-base">
                      {s.total_score ?? "-"} <span className="text-slate-300 font-normal">/</span> {exam?.total_score ?? "-"}
                    </p>
                  </div>
                  <div className="w-full md:col-span-2 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/room/${roomId}/exam/${examId}/grading/${s.student_id}`)}
                      className="w-full md:w-auto text-xs text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 h-8"
                      disabled={s.status === "missing"}
                    >
                      {s.status === "missing" ? "-" : "ดูรายข้อ"}
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
