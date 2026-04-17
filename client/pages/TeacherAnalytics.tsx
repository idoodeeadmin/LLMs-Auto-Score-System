import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, BarChart3 } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

interface AnalyticsResponse {
  mean_score: number;
  median_score: number;
  approved_submission_count: number;
  score_distribution: Record<string, number>;
  submission_counts: {
    submitted: number;
    missing: number;
  };
  difficulty_analysis: Array<{
    question_id: number;
    order_index: number;
    question_text: string;
    max_score: number;
    avg_score: number;
    percent_correct: number;
  }>;
}

interface ExamInfo {
  id: number;
  title: string;
  total_score: number;
}

export default function TeacherAnalytics() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();

  const [isFetching, setIsFetching] = useState(true);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [exam, setExam] = useState<ExamInfo | null>(null);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [isLoading, navigate, user]);

  useEffect(() => {
    if (!token || !roomId || !examId) return;
    const fetchData = async () => {
      setIsFetching(true);
      try {
        const [analyticsRes, examRes] = await Promise.all([
          fetch(`/api/rooms/${roomId}/exams/${examId}/analytics`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch(`/api/rooms/${roomId}/exams/${examId}`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);
        if (analyticsRes.ok) setAnalytics(await analyticsRes.json());
        else toast.error("ไม่สามารถโหลดข้อมูล analytics ได้");
        if (examRes.ok) setExam(await examRes.json());
      } catch {
        toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
      } finally {
        setIsFetching(false);
      }
    };
    fetchData();
  }, [token, roomId, examId]);

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  const distributionData = analytics
    ? Object.entries(analytics.score_distribution).map(([range, count]) => ({
        range,
        students: count,
      }))
    : [];

  return (
    <div className="min-h-screen bg-slate-50 pb-10">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 md:px-8 py-8 space-y-6">
        <button
          onClick={() => navigate(`/room/${roomId}/exam/${examId}`)}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft size={16} /> กลับหน้าข้อสอบ
        </button>

        <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="text-indigo-600" size={18} />
            <h1 className="text-xl md:text-2xl font-bold text-slate-900">Teacher Analytics</h1>
          </div>
          <p className="text-slate-500">{exam?.title ?? "Exam"} · คะแนนเต็ม {exam?.total_score ?? "-"}</p>
          <button
            onClick={() => navigate(`/room/${roomId}/exam/${examId}/scoreboard`)}
            className="mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-800"
          >
            ดูคะแนนรายนักเรียนทั้งหมดของข้อสอบนี้
          </button>
        </div>

        {analytics && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">Mean</p>
                <p className="text-2xl font-bold text-indigo-600">{analytics.mean_score}</p>
              </div>
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">Median</p>
                <p className="text-2xl font-bold text-violet-600">{analytics.median_score}</p>
              </div>
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">Submitted</p>
                <p className="text-2xl font-bold text-emerald-600">{analytics.submission_counts.submitted}</p>
              </div>
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">Missing</p>
                <p className="text-2xl font-bold text-rose-600">{analytics.submission_counts.missing}</p>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
              <h2 className="font-semibold text-slate-800 mb-3">Score Distribution</h2>
              <ChartContainer
                className="h-[280px] w-full"
                config={{ students: { label: "Students", color: "#4F46E5" } }}
              >
                <BarChart data={distributionData}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="range" tickLine={false} axisLine={false} />
                  <YAxis allowDecimals={false} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="students" fill="var(--color-students)" radius={8} />
                </BarChart>
              </ChartContainer>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
              <h2 className="font-semibold text-slate-800 mb-3">Question Difficulty</h2>
              <div className="space-y-2">
                {analytics.difficulty_analysis.map((q) => (
                  <div key={q.question_id} className="rounded-lg border border-slate-100 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm text-slate-700">
                        ข้อ {q.order_index + 1}: {q.question_text}
                      </p>
                      <span className="text-xs font-bold px-2 py-1 rounded bg-orange-50 text-orange-700 border border-orange-100">
                        {q.percent_correct}%
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      Avg {q.avg_score}/{q.max_score}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
