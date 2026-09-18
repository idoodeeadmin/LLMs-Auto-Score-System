import { PageLoading } from "@/components/RouteLoading";
import { useEffect, useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, ExternalLink } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

interface ExamSummary { exam_id: number; title: string; total_score: number; submitted_count: number; approved_count: number; approved_mean: number; missing_count: number; submission_rate: number; mean_percent: number }
interface RoomAnalyticsData { total_students: number; exam_count: number; overall_mean_score: number; overall_median_score: number; overall_distribution: Record<string, number>; exam_summaries: ExamSummary[] }

export default function RoomAnalytics() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();
  const [isFetching, setIsFetching] = useState(true);
  const [analytics, setAnalytics] = useState<RoomAnalyticsData | null>(null);
  const [roomName, setRoomName] = useState("ห้องเรียน");

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [isLoading, navigate, user]);

  useEffect(() => {
    if (!token || !roomId) return;
    const run = async () => {
      setIsFetching(true);
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [analyticsResponse, roomResponse] = await Promise.all([
          fetch(`/api/rooms/${roomId}/analytics`, { headers }), fetch(`/api/rooms/${roomId}`, { headers }),
        ]);
        if (!analyticsResponse.ok) throw new Error("โหลดข้อมูลวิเคราะห์ระดับห้องไม่สำเร็จ");
        setAnalytics(await analyticsResponse.json());
        if (roomResponse.ok) setRoomName((await roomResponse.json()).name || "ห้องเรียน");
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "เกิดข้อผิดพลาดในการเชื่อมต่อ");
      } finally { setIsFetching(false); }
    };
    void run();
  }, [token, roomId]);

  const exportSummary = async () => {
    if (!token || !roomId) return;
    try {
      const response = await fetch(`/api/rooms/${roomId}/export-summary-csv`, { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) throw new Error();
      const url = URL.createObjectURL(await response.blob());
      const anchor = document.createElement("a");
      anchor.href = url; anchor.download = `room-${roomId}-summary.csv`; anchor.click(); URL.revokeObjectURL(url);
      toast.success("ดาวน์โหลดรายงานแล้ว");
    } catch { toast.error("ส่งออกรายงานไม่สำเร็จ"); }
  };

  if (isLoading || isFetching) return <PageLoading layout="analytics" />;
  const comparison = (analytics?.exam_summaries ?? []).map(exam => ({ examId: exam.exam_id, name: exam.title.length > 18 ? `${exam.title.slice(0, 18)}…` : exam.title, average: exam.mean_percent, submitted: exam.submission_rate }));
  const distribution = Object.entries(analytics?.overall_distribution ?? {}).map(([range, count]) => ({ range, students: count }));
  const hasExams = Boolean(analytics?.exam_summaries.length);

  return <div className="min-h-screen bg-[#f8f9fa] pb-12 dark:bg-slate-950">
    <Navbar />
    <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <button onClick={() => navigate(`/room/${roomId}`)} className="mb-4 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"><ArrowLeft size={16} /> กลับห้องเรียน</button>
      <header className="mb-6 w-full border-b pb-5">
        <div className="flex w-full items-start gap-5">
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-[#176b5b]">รายงานห้องเรียน · {roomName}</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight">ภาพรวมผลการเรียน</h1>
            <p className="mt-1.5 text-sm text-muted-foreground">การส่งงานและผลคะแนนของข้อสอบทุกชุด</p>
          </div>
          <button onClick={exportSummary} className="ml-auto inline-flex h-9 shrink-0 items-center justify-center gap-2 rounded-md border bg-white px-3 text-sm font-medium hover:bg-slate-50 dark:bg-slate-900 dark:hover:bg-slate-800"><Download size={15} /> <span className="hidden sm:inline">ดาวน์โหลด CSV</span></button>
        </div>
      </header>

      {analytics && <>
        <section aria-label="ข้อมูลสรุป" className="mb-6 grid overflow-hidden rounded-lg border bg-white sm:grid-cols-2 lg:grid-cols-4 dark:bg-slate-900">
          <Metric label="นิสิตในห้อง" value={`${analytics.total_students} คน`} />
          <Metric label="ข้อสอบทั้งหมด" value={`${analytics.exam_count} ชุด`} />
          <Metric label="คะแนนเฉลี่ยรวม" value={`${analytics.overall_mean_score}%`} hint="เฉพาะผลที่อนุมัติแล้ว" />
          <Metric label="ค่ากลางคะแนน" value={`${analytics.overall_median_score}%`} hint="Median" />
        </section>

        {!hasExams ? <section className="rounded-lg border border-dashed bg-white px-6 py-16 text-center dark:bg-slate-900"><h2 className="font-medium">ยังไม่มีข้อมูลสำหรับวิเคราะห์</h2><p className="mt-2 text-sm text-muted-foreground">เมื่อมีข้อสอบและผลที่อนุมัติแล้ว รายงานของห้องจะแสดงที่นี่</p></section> : <>
          <section className="mb-6 grid gap-6 lg:grid-cols-[minmax(0,1.65fr)_minmax(300px,1fr)]">
            <ReportPanel title="ผลของข้อสอบแต่ละชุด" description="คะแนนเฉลี่ยและอัตราการส่ง คิดเป็นเปอร์เซ็นต์">
              <ChartContainer className="h-[290px] w-full" config={{ average: { label: "คะแนนเฉลี่ย", color: "#176b5b" }, submitted: { label: "ส่งแล้ว", color: "#9abcb4" } }}>
                <BarChart data={comparison} margin={{ left: -18, right: 4, top: 12 }}><CartesianGrid vertical={false} stroke="#e5e7eb" /><XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} /><YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 11 }} /><ChartTooltip content={<ChartTooltipContent />} /><Bar dataKey="average" fill="var(--color-average)" radius={[3, 3, 0, 0]} maxBarSize={34} onClick={(data: any) => data?.payload?.examId && navigate(`/room/${roomId}/exam/${data.payload.examId}/scoreboard`)} /><Bar dataKey="submitted" fill="var(--color-submitted)" radius={[3, 3, 0, 0]} maxBarSize={34} onClick={(data: any) => data?.payload?.examId && navigate(`/room/${roomId}/exam/${data.payload.examId}/scoreboard`)} /></BarChart>
              </ChartContainer>
            </ReportPanel>
            <ReportPanel title="การกระจายคะแนน" description="จำนวนนิสิตในแต่ละช่วงคะแนน">
              <ChartContainer className="h-[290px] w-full" config={{ students: { label: "นิสิต", color: "#176b5b" } }}><BarChart data={distribution} margin={{ left: -22, right: 4, top: 12 }}><CartesianGrid vertical={false} stroke="#e5e7eb" /><XAxis dataKey="range" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} /><YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 11 }} /><ChartTooltip content={<ChartTooltipContent />} /><Bar dataKey="students" fill="var(--color-students)" radius={[3, 3, 0, 0]} maxBarSize={42} /></BarChart></ChartContainer>
            </ReportPanel>
          </section>

          <section className="overflow-hidden rounded-lg border bg-white dark:bg-slate-900">
            <div className="border-b px-5 py-4"><h2 className="font-semibold">รายละเอียดรายข้อสอบ</h2><p className="mt-1 text-sm text-muted-foreground">ข้อมูลการส่งและคะแนนที่อนุมัติแล้ว</p></div>
            <div className="overflow-x-auto"><table className="w-full min-w-[820px] text-left text-sm">
              <thead className="border-b bg-slate-50 text-xs text-muted-foreground dark:bg-slate-950"><tr><th className="px-5 py-3 font-medium">ข้อสอบ</th><th className="px-4 py-3 text-right font-medium">ส่งแล้ว</th><th className="px-4 py-3 text-right font-medium">ยังไม่ส่ง</th><th className="px-4 py-3 font-medium">อัตราการส่ง</th><th className="px-4 py-3 text-right font-medium">เฉลี่ย</th><th className="px-5 py-3"><span className="sr-only">เปิดรายงาน</span></th></tr></thead>
              <tbody className="divide-y">{analytics.exam_summaries.map(exam => <tr key={exam.exam_id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40">
                <td className="px-5 py-4"><p className="font-medium">{exam.title}</p><p className="mt-1 text-xs text-muted-foreground">เต็ม {exam.total_score} คะแนน · อนุมัติแล้ว {exam.approved_count} คน</p></td><td className="px-4 py-4 text-right tabular-nums">{exam.submitted_count}</td><td className="px-4 py-4 text-right tabular-nums">{exam.missing_count}</td>
                <td className="w-44 px-4 py-4"><div className="flex items-center gap-3"><div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700"><div className="h-full bg-[#176b5b]" style={{ width: `${Math.min(100, exam.submission_rate)}%` }} /></div><span className="w-10 text-right text-xs tabular-nums">{exam.submission_rate}%</span></div></td>
                <td className="px-4 py-4 text-right"><span className="font-medium tabular-nums">{exam.mean_percent}%</span><p className="text-xs text-muted-foreground">{exam.approved_mean} คะแนน</p></td><td className="px-5 py-4 text-right"><button onClick={() => navigate(`/room/${roomId}/exam/${exam.exam_id}/scoreboard`)} className="inline-flex items-center gap-1 font-medium text-[#176b5b] hover:underline">ดูรายงาน <ExternalLink size={14} /></button></td>
              </tr>)}</tbody>
            </table></div>
          </section>
        </>}
      </>}
    </main>
  </div>;
}

function Metric({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return <div className="border-b px-5 py-4 last:border-b-0 sm:[&:nth-child(odd)]:border-r sm:[&:nth-last-child(-n+2)]:border-b-0 lg:border-b-0 lg:border-r lg:last:border-r-0"><p className="text-xs font-medium text-muted-foreground">{label}</p><p className="mt-2 text-2xl font-semibold tabular-nums tracking-tight">{value}</p>{hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}</div>;
}

function ReportPanel({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return <div className="rounded-lg border bg-white p-5 dark:bg-slate-900"><h2 className="font-semibold">{title}</h2><p className="mt-1 text-xs text-muted-foreground">{description}</p><div className="mt-3">{children}</div></div>;
}
