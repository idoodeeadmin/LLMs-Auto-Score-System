import { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import {
  Search, CheckCircle2, AlertCircle,
  FileText, User, Check, AlertTriangle, Loader2, ArrowLeft, RefreshCw
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

type StudentStatus = "missing" | "ready" | "needs_review" | "approved";

interface StudentSubmission {
  student_id: number;
  name: string;
  email: string;
  student_code?: string;
  submission_id?: number;
  status: StudentStatus;
  total_score?: number;
  submitted_at?: string;
  graded_by_ai?: boolean;
}

interface ExamInfo {
  id: number;
  title: string;
  total_score: number;
}

interface Analytics {
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

export default function RoomReview() {
  const navigate = useNavigate();
  const { roomId, examId } = useParams();
  const { user, token, isLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<"missing" | "pending" | "approved">("pending");
  const [subFilter, setSubFilter] = useState<"all" | "success" | "failed">("all");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [students, setStudents] = useState<StudentSubmission[]>([]);
  const [exam, setExam] = useState<ExamInfo | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [isApproving, setIsApproving] = useState(false);
  const [isExportingCsv, setIsExportingCsv] = useState(false);
  const [isExportingXlsx, setIsExportingXlsx] = useState(false);
  const [bulkMode, setBulkMode] = useState<"ready_only" | "include_needs_review">("ready_only");

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [user, isLoading, navigate]);

  const fetchData = useCallback(async () => {
    if (!token || !roomId || !examId) return;
    setIsFetching(true);
    try {
      const [subRes, examRes, analyticsRes] = await Promise.all([
        fetch(`/api/rooms/${roomId}/exams/${examId}/submissions`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`/api/rooms/${roomId}/exams/${examId}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`/api/rooms/${roomId}/exams/${examId}/analytics`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (subRes.ok) {
        setStudents(await subRes.json());
      } else {
        toast.error("ไม่สามารถโหลดข้อมูลการส่งงานได้");
      }
      if (examRes.ok) {
        setExam(await examRes.json());
      }
      if (analyticsRes.ok) {
        setAnalytics(await analyticsRes.json());
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsFetching(false);
    }
  }, [token, roomId, examId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filtering
  const filteredStudents = students.filter((s) => {
    const matchSearch = s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (s.student_code || "").toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchSearch) return false;

    if (activeTab === "missing") return s.status === "missing";
    if (activeTab === "approved") return s.status === "approved";
    if (activeTab === "pending") {
      const isPending = s.status === "ready" || s.status === "needs_review";
      if (!isPending) return false;
      if (subFilter === "all") return true;
      if (subFilter === "success") return s.status === "ready";
      if (subFilter === "failed") return s.status === "needs_review";
    }
    return false;
  });

  const approvableStudents = filteredStudents.filter((s) => {
    if (bulkMode === "include_needs_review") return s.status === "ready" || s.status === "needs_review";
    return s.status === "ready";
  });
  const missingCount = students.filter((s) => s.status === "missing").length;
  const pendingCount = students.filter((s) => s.status === "ready" || s.status === "needs_review").length;
  const approvedCount = students.filter((s) => s.status === "approved").length;

  const toggleSelectAll = () => {
    if (approvableStudents.length > 0 && selectedIds.length === approvableStudents.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(approvableStudents.map((s) => s.student_id));
    }
  };

  const toggleSelectOne = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((x) => x !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleExport = async (format: "csv" | "xlsx") => {
    if (!token || !roomId || !examId) return;
    if (format === "csv") setIsExportingCsv(true);
    else setIsExportingXlsx(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/export?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        toast.error(`ไม่สามารถ Export ${format.toUpperCase()} ได้`);
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `exam-${examId}-scores.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success(`Export ${format.toUpperCase()} สำเร็จ`);
    } catch {
      toast.error("เกิดข้อผิดพลาดในการ Export");
    } finally {
      if (format === "csv") setIsExportingCsv(false);
      else setIsExportingXlsx(false);
    }
  };

  const handleApproveOne = async (studentId: number) => {
    if (!token) return;
    try {
      const res = await fetch(
        `/api/rooms/${roomId}/exams/${examId}/submissions/${studentId}/approve`,
        {
          method: "PUT",
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({}),
        }
      );
      if (res.ok) {
        toast.success("อนุมัติผลสำเร็จ");
        setStudents((prev) =>
          prev.map((s) =>
            s.student_id === studentId ? { ...s, status: "approved" } : s
          )
        );
        setSelectedIds(selectedIds.filter((x) => x !== studentId));
      } else {
        toast.error("ไม่สามารถอนุมัติได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    }
  };

  const handleBulkApprove = async () => {
    if (!token || selectedIds.length === 0) return;
    setIsApproving(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/bulk-approve`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ student_ids: selectedIds }),
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`อนุมัติ ${data.approved_student_ids?.length || 0} คน สำเร็จ`);
        if (data.skipped?.length) {
          toast.info(`ข้าม ${data.skipped.length} คน (สถานะไม่พร้อมอนุมัติ)`);
        }
        setStudents((prev) =>
          prev.map((s) =>
            selectedIds.includes(s.student_id) && (s.status === "ready" || s.status === "needs_review")
              ? { ...s, status: "approved" }
              : s
          )
        );
        setSelectedIds([]);
      } else {
        toast.error("ไม่สามารถอนุมัติแบบกลุ่มได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsApproving(false);
    }
  };

  const StatusBadge = ({ status, score, maxScore }: { status: StudentStatus; score?: number; maxScore?: number }) => {
    if (status === "ready") return (
      <div className="flex flex-col items-start">
        <span className="text-sm font-bold text-gray-900">สำเร็จ (รออนุมัติ)</span>
        <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-md mt-1 border border-green-100">
          คะแนน AI: {score ?? "-"}/{maxScore ?? "-"}
        </span>
      </div>
    );
    if (status === "needs_review") return (
      <div className="flex flex-col items-start">
        <span className="text-sm font-bold text-gray-900">ต้องตรวจสอบ</span>
        <span className="text-xs text-orange-600 bg-orange-50 px-2 py-0.5 rounded-md mt-1 border border-orange-100 flex items-center gap-1">
          <AlertTriangle size={10} /> AI ไม่มั่นใจ — โปรดตรวจ
        </span>
      </div>
    );
    if (status === "approved") return (
      <div className="flex items-center gap-2 text-green-600 font-medium">
        <CheckCircle2 size={16} /> อนุมัติแล้ว ({score ?? "-"}/{maxScore ?? "-"})
      </div>
    );
    return <span className="text-gray-400 italic">ยังไม่ส่งข้อสอบ</span>;
  };

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
    <div className="min-h-screen bg-[#F8F9FA] pb-20">
      <Navbar activeTab="allReviews" />

      <main className="max-w-[1440px] mx-auto p-6 md:p-8 space-y-8">

        {/* Header & Stats */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <button
              onClick={() => navigate(`/room/${roomId}/exam/${examId}`)}
              className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-700 mb-2 transition-colors"
            >
              <ArrowLeft size={15} /> กลับหน้าข้อสอบ
            </button>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-gray-900">{exam?.title ?? "..."}</h1>
              <span className="bg-blue-100 text-[#3B82F6] text-xs px-2 py-0.5 rounded font-bold">
                {exam?.total_score} คะแนน
              </span>
            </div>
            <p className="text-gray-500">จัดการผลการประเมินและอนุมัติคะแนน</p>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={fetchData} className="bg-white text-gray-700" disabled={isFetching}>
              <RefreshCw className={`mr-2 w-4 h-4 ${isFetching ? "animate-spin" : ""}`} /> รีเฟรช
            </Button>
            <Button
              variant="outline"
              className="bg-white text-gray-700"
              onClick={() => handleExport("csv")}
              disabled={isExportingCsv}
            >
              <FileText className="mr-2 w-4 h-4" /> Export CSV
            </Button>
            <Button
              variant="outline"
              className="bg-white text-gray-700"
              onClick={() => handleExport("xlsx")}
              disabled={isExportingXlsx}
            >
              <FileText className="mr-2 w-4 h-4" /> Export Excel
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            onClick={() => setActiveTab("missing")}
            className={`p-5 rounded-xl border shadow-sm flex items-center justify-between cursor-pointer transition-all hover:shadow-md ${activeTab === "missing" ? "border-gray-400 bg-gray-50 ring-1 ring-gray-400" : "bg-white border-gray-100"}`}
          >
            <div>
              <p className="text-sm text-gray-500">ยังไม่ส่ง</p>
              <p className="text-2xl font-bold text-gray-400">{missingCount} <span className="text-sm font-normal">คน</span></p>
            </div>
            <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-400"><User size={20} /></div>
          </div>

          <div
            onClick={() => setActiveTab("pending")}
            className={`p-5 rounded-xl border shadow-sm flex items-center justify-between cursor-pointer transition-all hover:shadow-md relative overflow-hidden ${activeTab === "pending" ? "border-[#3B82F6] bg-blue-50/20 ring-1 ring-[#3B82F6]" : "bg-white border-gray-100"}`}
          >
            {activeTab === "pending" && <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[#3B82F6]" />}
            <div>
              <p className={`text-sm font-medium ${activeTab === "pending" ? "text-[#3B82F6]" : "text-gray-500"}`}>รอการตรวจ/อนุมัติ</p>
              <p className="text-2xl font-bold text-gray-900">{pendingCount} <span className="text-sm font-normal text-gray-500">คน</span></p>
            </div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${activeTab === "pending" ? "bg-blue-100 text-[#3B82F6]" : "bg-gray-50 text-gray-400"}`}><AlertCircle size={20} /></div>
          </div>

          <div
            onClick={() => setActiveTab("approved")}
            className={`p-5 rounded-xl border shadow-sm flex items-center justify-between cursor-pointer transition-all hover:shadow-md ${activeTab === "approved" ? "border-green-500 bg-green-50/20 ring-1 ring-green-500" : "bg-white border-gray-100"}`}
          >
            <div>
              <p className={`text-sm font-medium ${activeTab === "approved" ? "text-green-600" : "text-gray-500"}`}>อนุมัติแล้ว</p>
              <p className="text-2xl font-bold text-gray-900">{approvedCount} <span className="text-sm font-normal text-gray-500">คน</span></p>
            </div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${activeTab === "approved" ? "bg-green-100 text-green-600" : "bg-gray-50 text-gray-400"}`}><CheckCircle2 size={20} /></div>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden min-h-[400px] flex flex-col">

          {/* Toolbar */}
          <div className="border-b border-gray-200 p-4 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex p-1 bg-gray-100 rounded-lg self-start">
              <button onClick={() => setActiveTab("missing")} className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === "missing" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}>
                ยังไม่ส่ง ({missingCount})
              </button>
              <button onClick={() => setActiveTab("pending")} className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === "pending" ? "bg-white text-[#3B82F6] shadow-sm" : "text-gray-500 hover:text-gray-700"}`}>
                รอการตรวจ ({pendingCount})
              </button>
              <button onClick={() => setActiveTab("approved")} className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === "approved" ? "bg-white text-green-600 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}>
                อนุมัติแล้ว ({approvedCount})
              </button>
            </div>

            <div className="flex gap-3 w-full md:w-auto items-center">
              {activeTab === "pending" && (
                <div className="flex gap-2 mr-2 items-center">
                  <button onClick={() => setSubFilter("all")} className={`px-3 py-1.5 text-xs font-bold rounded-full border transition-all ${subFilter === "all" ? "bg-gray-800 text-white border-gray-800" : "bg-white text-gray-500 border-gray-200 hover:border-gray-400"}`}>ทั้งหมด</button>
                  <button onClick={() => setSubFilter("failed")} className={`px-3 py-1.5 text-xs font-bold rounded-full border transition-all ${subFilter === "failed" ? "bg-orange-500 text-white border-orange-500" : "bg-white text-gray-500 border-gray-200 hover:border-orange-300"}`}>ประเมินไม่ได้</button>
                  <button onClick={() => setSubFilter("success")} className={`px-3 py-1.5 text-xs font-bold rounded-full border transition-all ${subFilter === "success" ? "bg-green-500 text-white border-green-500" : "bg-white text-gray-500 border-gray-200 hover:border-green-300"}`}>ประเมินสำเร็จ</button>
                  <div className="flex items-center bg-gray-100 rounded-full p-1 ml-2">
                    <button
                      onClick={() => {
                        setBulkMode("ready_only");
                        setSelectedIds((prev) => prev.filter((id) => students.some((s) => s.student_id === id && s.status === "ready")));
                      }}
                      className={`px-2.5 py-1 text-xs rounded-full ${bulkMode === "ready_only" ? "bg-white text-gray-800 shadow-sm" : "text-gray-500"}`}
                    >
                      Bulk: Ready
                    </button>
                    <button
                      onClick={() => setBulkMode("include_needs_review")}
                      className={`px-2.5 py-1 text-xs rounded-full ${bulkMode === "include_needs_review" ? "bg-white text-gray-800 shadow-sm" : "text-gray-500"}`}
                    >
                      +Needs Review
                    </button>
                  </div>
                </div>
              )}
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="ค้นหาชื่อ / รหัสนักศึกษา..."
                  className="pl-9 h-10 bg-gray-50 border-gray-200"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-gray-50/50 border-b border-gray-200 text-sm font-semibold text-gray-500">
            <div className="col-span-4 flex items-center gap-4">
              <div className="flex items-center justify-center w-5">
                <input
                  type="checkbox"
                  className={`w-4 h-4 rounded border-gray-300 text-[#3B82F6] focus:ring-[#3B82F6] ${activeTab === "pending" && approvableStudents.length === 0 ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                  checked={activeTab === "pending" ? (approvableStudents.length > 0 && selectedIds.length === approvableStudents.length) : false}
                  disabled={activeTab !== "pending" || approvableStudents.length === 0}
                  onChange={toggleSelectAll}
                />
              </div>
              <span>รายชื่อนักศึกษา</span>
            </div>
            <div className="col-span-4">ผลการประเมิน (AI)</div>
            <div className="col-span-4 text-right pr-4">การดำเนินการ</div>
          </div>

          {/* Student List */}
          <div className="divide-y divide-gray-100 flex-1">
            {filteredStudents.length === 0 ? (
              <div className="py-20 text-center text-gray-400">
                {students.length === 0
                  ? "ยังไม่มีนักศึกษาในห้องนี้"
                  : "ไม่มีข้อมูลในหมวดหมู่นี้"}
              </div>
            ) : (
              filteredStudents.map((student) => (
                <div key={student.student_id} className="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-gray-50/50 transition-colors group">
                  {/* Name Col */}
                  <div className="col-span-4 flex items-center gap-4">
                    <div className="flex items-center justify-center w-5">
                      <input
                        type="checkbox"
                        className={`w-4 h-4 rounded border-gray-300 text-[#3B82F6] focus:ring-[#3B82F6] ${(bulkMode === "include_needs_review" ? (student.status !== "ready" && student.status !== "needs_review") : student.status !== "ready") ? "opacity-30 cursor-not-allowed bg-gray-100" : "cursor-pointer"}`}
                        checked={selectedIds.includes(student.student_id)}
                        disabled={bulkMode === "include_needs_review" ? (student.status !== "ready" && student.status !== "needs_review") : student.status !== "ready"}
                        onChange={() => toggleSelectOne(student.student_id)}
                      />
                    </div>
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-[#3B82F6] font-bold text-sm flex-shrink-0">
                      {student.name.charAt(0)}
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 truncate">{student.name}</p>
                      <p className="text-xs text-gray-500 truncate">
                        {student.student_code || student.email}
                        {student.submitted_at && ` · ส่งเมื่อ ${new Date(student.submitted_at).toLocaleTimeString("th-TH", { hour: "2-digit", minute: "2-digit" })}`}
                      </p>
                    </div>
                  </div>

                  {/* Status Col */}
                  <div className="col-span-4">
                    <StatusBadge status={student.status} score={student.total_score ?? undefined} maxScore={exam?.total_score} />
                  </div>

                  {/* Actions Col */}
                  <div className="col-span-4 flex justify-end gap-2">
                    {activeTab === "pending" && (
                      <>
                        <Button
                          onClick={() => handleApproveOne(student.student_id)}
                          disabled={student.status === "needs_review"}
                          className={`h-9 w-24 rounded-lg font-bold shadow-sm transition-all ${student.status === "needs_review" ? "bg-gray-300 cursor-not-allowed text-gray-500" : "bg-green-500 hover:bg-green-600 text-white"}`}
                        >
                          <Check size={14} className="mr-1" />อนุมัติ
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => navigate(`/room/${roomId}/exam/${examId}/grading/${student.student_id}`)}
                          className="border-blue-200 text-[#3B82F6] hover:bg-blue-50 h-9 px-4 rounded-lg font-medium"
                        >
                          ตรวจสอบ
                        </Button>
                      </>
                    )}
                    {activeTab === "approved" && (
                      <Button
                        variant="ghost"
                        onClick={() => navigate(`/room/${roomId}/exam/${examId}/grading/${student.student_id}`)}
                        className="text-gray-400 hover:text-[#3B82F6]"
                      >
                        ดูรายละเอียด
                      </Button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Analytics Summary */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <p className="text-sm text-gray-500">คะแนนเฉลี่ย (Approved)</p>
              <p className="text-2xl font-bold text-[#3B82F6]">
                {analytics.mean_score} / {exam?.total_score ?? "-"}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <p className="text-sm text-gray-500">มัธยฐาน (Approved)</p>
              <p className="text-2xl font-bold text-violet-600">
                {analytics.median_score} / {exam?.total_score ?? "-"}
              </p>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <p className="text-sm text-gray-500">ส่งแล้ว / ยังไม่ส่ง</p>
              <p className="text-2xl font-bold text-emerald-600">
                {analytics.submission_counts.submitted} / {analytics.submission_counts.missing}
              </p>
            </div>
          </div>
        )}

        {analytics && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Score Distribution</h2>
            <ChartContainer
              className="h-[240px] w-full"
              config={{
                students: {
                  label: "จำนวนนักเรียน",
                  color: "#3B82F6",
                },
              }}
            >
              <BarChart data={distributionData}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="range" tickLine={false} axisLine={false} />
                <YAxis allowDecimals={false} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="students" radius={8} fill="var(--color-students)" />
              </BarChart>
            </ChartContainer>
          </div>
        )}

        {/* Difficulty Analysis */}
        {analytics && analytics.difficulty_analysis.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Question Difficulty Analysis</h2>
            <div className="space-y-2">
              {analytics.difficulty_analysis.slice(0, 5).map((q) => (
                <div key={q.question_id} className="border border-gray-100 rounded-lg p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      ข้อ {q.order_index + 1}: {q.question_text}
                    </p>
                    <span className="text-xs font-bold px-2 py-1 rounded bg-orange-50 text-orange-600 border border-orange-100">
                      {q.percent_correct}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    คะแนนเฉลี่ย {q.avg_score}/{q.max_score}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Floating Bulk Action Bar */}
      {selectedIds.length > 0 && activeTab === "pending" && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center gap-6 animate-in slide-in-from-bottom-4 z-50">
          <div className="flex items-center gap-3 border-r border-gray-700 pr-6">
            <div className="bg-[#3B82F6] text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold">{selectedIds.length}</div>
            <span className="font-medium">รายการที่เลือก</span>
          </div>
          <div className="flex gap-3">
            <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
              <button
                className={`px-2.5 py-1.5 text-xs rounded ${bulkMode === "ready_only" ? "bg-white text-gray-900 font-semibold" : "text-gray-300"}`}
                onClick={() => {
                  setBulkMode("ready_only");
                  setSelectedIds((prev) => prev.filter((id) => students.some((s) => s.student_id === id && s.status === "ready")));
                }}
              >
                เฉพาะ Ready
              </button>
              <button
                className={`px-2.5 py-1.5 text-xs rounded ${bulkMode === "include_needs_review" ? "bg-white text-gray-900 font-semibold" : "text-gray-300"}`}
                onClick={() => setBulkMode("include_needs_review")}
              >
                รวม Needs Review
              </button>
            </div>
            <Button variant="ghost" onClick={() => setSelectedIds([])} className="text-gray-300 hover:text-white h-8">ยกเลิก</Button>
            <Button
              onClick={handleBulkApprove}
              disabled={isApproving}
              className="bg-green-500 hover:bg-green-600 text-white h-9 px-6 rounded-lg font-bold"
            >
              {isApproving ? <Loader2 size={14} className="animate-spin mr-2" /> : null}
              อนุมัติทั้งหมด ({selectedIds.length})
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}