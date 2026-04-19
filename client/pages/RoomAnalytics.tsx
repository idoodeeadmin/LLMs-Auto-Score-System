import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, BarChart3, Download } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

interface RoomAnalyticsData {
  total_students: number;
  exam_count: number;
  overall_mean_score: number;
  overall_median_score: number;
  overall_distribution: Record<string, number>;
  exam_summaries: Array<{
    exam_id: number;
    title: string;
    total_score: number;
    submitted_count: number;
    approved_count: number;
    approved_mean: number;
    missing_count: number;
    submission_rate: number;
    mean_percent: number;
  }>;
}

export default function RoomAnalytics() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();
  const [isFetching, setIsFetching] = useState(true);
  const [analytics, setAnalytics] = useState<RoomAnalyticsData | null>(null);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [isLoading, navigate, user]);

  useEffect(() => {
    if (!token || !roomId) return;
    const run = async () => {
      setIsFetching(true);
      try {
        const res = await fetch(`/api/rooms/${roomId}/analytics`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          toast.error("โหลดข้อมูลวิเคราะห์ระดับห้องไม่สำเร็จ");
          return;
        }
        setAnalytics(await res.json());
      } catch {
        toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
      } finally {
        setIsFetching(false);
      }
    };
    run();
  }, [token, roomId]);

  const handleExportSummary = async () => {
    if (!token || !roomId) return;
    try {
      const res = await fetch(`/api/rooms/${roomId}/export-summary-csv`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Summary_Room_${roomId}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        toast.success("ดาวน์โหลดสรุปคะแนนรวมสำเร็จ");
      } else {
        toast.error("ส่งออกข้อมูลไม่สำเร็จ");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    }
  };

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  const examCompareData = (analytics?.exam_summaries ?? []).map((e) => ({
    examId: e.exam_id,
    name: e.title.length > 22 ? `${e.title.slice(0, 22)}...` : e.title,
    meanPercent: e.mean_percent,
    submissionRate: e.submission_rate,
  }));

  const distributionData = analytics
    ? Object.entries(analytics.overall_distribution).map(([range, count]) => ({
        range,
        students: count,
      }))
    : [];

  return (
    <div className="min-h-screen bg-slate-50 pb-10">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 md:px-8 py-8 space-y-6">
        <button
          onClick={() => navigate(`/room/${roomId}`)}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft size={16} /> กลับหน้าห้องเรียน
        </button>

        <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="text-indigo-600" size={18} />
              <h1 className="text-xl md:text-2xl font-bold text-slate-900">
                วิเคราะห์ข้อสอบทุกชุดในห้อง
              </h1>
            </div>
            <button
              onClick={handleExportSummary}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-all shadow-sm shadow-indigo-100 active:scale-95 text-sm"
            >
              <Download size={16} />
              ส่งออกสรุปทุกชุด (CSV)
            </button>
          </div>
          <p className="text-slate-500 mt-1">เปรียบเทียบผลทุกชุดข้อสอบในห้องเดียวกัน</p>
        </div>

        {analytics && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">จำนวนนักศึกษา</p>
                <p className="text-2xl font-bold text-slate-800">{analytics.total_students}</p>
              </div>
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">จำนวนชุดข้อสอบ</p>
                <p className="text-2xl font-bold text-indigo-600">{analytics.exam_count}</p>
              </div>
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">Mean รวม (Approved)</p>
                <p className="text-2xl font-bold text-emerald-600">{analytics.overall_mean_score}</p>
              </div>
              <div className="bg-white rounded-xl border border-slate-100 p-4">
                <p className="text-sm text-slate-500">Median รวม (Approved)</p>
                <p className="text-2xl font-bold text-violet-600">{analytics.overall_median_score}</p>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
              <h2 className="font-semibold text-slate-800 mb-3">เปรียบเทียบคะแนนเฉลี่ยรายชุด (%)</h2>
              <ChartContainer
                className="h-[300px] w-full"
                config={{
                  meanPercent: { label: "คะแนนเฉลี่ย (%)", color: "#4F46E5" },
                  submissionRate: { label: "อัตราการส่ง (%)", color: "#14B8A6" },
                }}
              >
                <BarChart data={examCompareData}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="name" tickLine={false} axisLine={false} />
                  <YAxis domain={[0, 100]} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar
                    dataKey="meanPercent"
                    fill="var(--color-meanPercent)"
                    radius={6}
                    onClick={(d: any) => d?.payload?.examId && navigate(`/room/${roomId}/exam/${d.payload.examId}/scoreboard`)}
                  />
                  <Bar
                    dataKey="submissionRate"
                    fill="var(--color-submissionRate)"
                    radius={6}
                    onClick={(d: any) => d?.payload?.examId && navigate(`/room/${roomId}/exam/${d.payload.examId}/scoreboard`)}
                  />
                </BarChart>
              </ChartContainer>
              <p className="text-xs text-slate-400 mt-2">คลิกแท่งกราฟเพื่อดูคะแนนรายนักเรียนของชุดนั้น</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
              <h2 className="font-semibold text-slate-800 mb-3">การกระจายคะแนนรวมทั้งห้อง (%)</h2>
              <ChartContainer
                className="h-[260px] w-full"
                config={{ students: { label: "จำนวนนักเรียน", color: "#3B82F6" } }}
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

            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-100 bg-slate-50">
                <h2 className="font-semibold text-slate-800">ตารางสรุปทุกชุดข้อสอบ</h2>
              </div>
              <div className="grid grid-cols-12 gap-3 px-5 py-3 bg-slate-50/70 border-b border-slate-100 text-xs font-semibold text-slate-500">
                <div className="col-span-4">ชื่อข้อสอบ</div>
                <div className="col-span-1 text-right">เต็ม</div>
                <div className="col-span-1 text-right">ส่งแล้ว</div>
                <div className="col-span-1 text-right">ยังไม่ส่ง</div>
                <div className="col-span-1 text-right">% ส่ง</div>
                <div className="col-span-1 text-right">เฉลี่ย</div>
                <div className="col-span-1 text-right">% เฉลี่ย</div>
                <div className="col-span-2 text-right">ดูรายคน</div>
              </div>
              <div className="divide-y divide-slate-100">
                {analytics.exam_summaries.map((e) => (
                  <div key={e.exam_id} className="grid grid-cols-12 gap-3 px-5 py-4 items-center">
                    <div className="col-span-4 min-w-0">
                      <p className="font-medium text-slate-800">{e.title}</p>
                      <p className="text-xs text-slate-500">คะแนนเต็ม {e.total_score}</p>
                    </div>
                    <div className="col-span-1 text-right text-sm text-slate-600">{e.total_score}</div>
                    <div className="col-span-1 text-right text-sm text-slate-600">{e.submitted_count}</div>
                    <div className="col-span-1 text-right text-sm text-slate-600">{e.missing_count}</div>
                    <div className="col-span-1 text-right text-sm text-slate-600">{e.submission_rate}%</div>
                    <div className="col-span-1 text-right text-sm font-semibold text-indigo-600">{e.approved_mean}</div>
                    <div className="col-span-1 text-right text-sm font-semibold text-emerald-600">{e.mean_percent}%</div>
                    <div className="col-span-2 text-right">
                      <button
                        onClick={() => navigate(`/room/${roomId}/exam/${e.exam_id}/scoreboard`)}
                        className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
                      >
                        ดูรายคน
                      </button>
                    </div>
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
