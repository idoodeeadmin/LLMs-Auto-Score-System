import { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import {
  Search, CheckCircle2, AlertCircle,
  FileText, User, Check, AlertTriangle, Loader2, ArrowLeft, RefreshCw, Inbox, FileX, CheckSquare, X
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
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

export default function RoomReview() {
  const navigate = useNavigate();
  const { roomId, examId } = useParams();
  const { user, token, isLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<"missing" | "pending" | "approved">("pending");
  const [subFilter, setSubFilter] = useState<"all" | "ready" | "needs_review">("all");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [students, setStudents] = useState<StudentSubmission[]>([]);
  const [exam, setExam] = useState<ExamInfo | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [isApproving, setIsApproving] = useState(false);
  const [isExportingCsv, setIsExportingCsv] = useState(false);
  const [isExportingXlsx, setIsExportingXlsx] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [user, isLoading, navigate]);

  const fetchData = useCallback(async () => {
    if (!token || !roomId || !examId) {
      setIsFetching(false);
      return;
    }
    
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

      if (subRes.ok) {
        setStudents(await subRes.json());
      } else {
        toast.error("ไม่สามารถโหลดข้อมูลการส่งงานได้");
      }
      
      if (examRes.ok) {
        setExam(await examRes.json());
      }
    } catch (error) {
      console.error("Fetch error:", error);
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsFetching(false);
    }
  }, [token, roomId, examId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Unified Filtering Logic
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
      if (subFilter === "ready") return s.status === "ready";
      if (subFilter === "needs_review") return s.status === "needs_review";
    }
    return false;
  });

  const missingCount = students.filter((s) => s.status === "missing").length;
  const pendingCount = students.filter((s) => s.status === "ready" || s.status === "needs_review").length;
  const approvedCount = students.filter((s) => s.status === "approved").length;

  const toggleSelectAllVisible = () => {
    if (filteredStudents.length > 0 && selectedIds.length === filteredStudents.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredStudents.map((s) => s.student_id));
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
      <div className="flex flex-col items-start gap-1">
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-green-50 text-green-700 border border-green-200/60 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800/40">
          <CheckCircle2 size={12} /> พร้อมอนุมัติ
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400 font-medium ml-1">
          คะแนน AI: <span className="text-gray-900 dark:text-gray-200 font-semibold">{score ?? "-"}</span>/{maxScore ?? "-"}
        </span>
      </div>
    );
    if (status === "needs_review") return (
      <div className="flex flex-col items-start gap-1">
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-orange-50 text-orange-700 border border-orange-200/60 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800/40">
          <AlertTriangle size={12} /> ต้องตรวจสอบ
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400 font-medium ml-1">
          AI ไม่มั่นใจ
        </span>
      </div>
    );
    if (status === "approved") return (
      <div className="flex flex-col items-start gap-1">
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-50 text-blue-700 border border-blue-200/60 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800/40">
          <Check size={12} /> อนุมัติแล้ว
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400 font-medium ml-1">
          คะแนน: <span className="text-gray-900 dark:text-gray-200 font-semibold">{score ?? "-"}</span>/{maxScore ?? "-"}
        </span>
      </div>
    );
    return (
      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-gray-100 text-gray-600 border border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700">
        ยังไม่ส่งข้อสอบ
      </span>
    );
  };

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#F9FBFD] dark:bg-[#111111]">
        <Loader2 className="animate-spin text-blue-500 h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F9FBFD] dark:bg-[#111111] text-gray-900 dark:text-gray-100 font-sans">
      <Navbar activeTab="allReviews" />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* Unified Header Section */}
        <header>
          <button
            onClick={() => navigate(`/room/${roomId}/exam/${examId}`)}
            className="group flex items-center gap-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors text-sm font-medium mb-6"
          >
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
            กลับหน้าข้อสอบ
          </button>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight mb-2 text-gray-900 dark:text-white">{exam?.title}</h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm">จัดการผลการประเมินและอนุมัติคะแนนนักศึกษา</p>
            </div>
          </div>
        </header>

        {/* Elegant Tabs & Filters */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-6 border-b border-gray-200 dark:border-gray-800 pb-4">
          <div className="flex gap-6 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 hide-scrollbar">
            {[
              { id: "pending", label: "รอตรวจ", count: pendingCount, color: "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30" },
              { id: "approved", label: "อนุมัติแล้ว", count: approvedCount, color: "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30" },
              { id: "missing", label: "ยังไม่ส่ง", count: missingCount, color: "text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`relative pb-3 text-sm font-medium transition-all whitespace-nowrap flex items-center gap-2 ${activeTab === tab.id ? "text-gray-900 dark:text-white" : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                  }`}
              >
                {tab.label}
                <span className={`px-2 py-0.5 rounded-full text-xs ${activeTab === tab.id ? tab.color : "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"}`}>
                  {tab.count}
                </span>
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-blue-600 dark:bg-blue-500 rounded-t-full" />
                )}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                placeholder="ค้นหาชื่อ หรือ รหัส..."
                className="w-full pl-9 pr-4 h-10 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-gray-900 dark:text-white placeholder:text-gray-400"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <Button 
              variant="outline" 
              className="h-10 px-3 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg flex items-center gap-2" 
              onClick={() => setShowExportModal(true)} 
              disabled={isExportingXlsx || students.length === 0}
            >
              <FileText size={16} />
              <span className="hidden sm:inline">ส่งออก</span>
            </Button>
          </div>
        </div>

        {/* Export Confirmation Modal */}
        <AnimatePresence>
          {showExportModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                exit={{ opacity: 0 }}
                onClick={() => setShowExportModal(false)}
                className="absolute inset-0 bg-black/40 backdrop-blur-sm" 
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="relative bg-white dark:bg-gray-900 w-full max-w-sm rounded-2xl p-6 shadow-xl border border-gray-200 dark:border-gray-800"
              >
                <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center mb-4 mx-auto">
                  <FileText className="text-blue-600 dark:text-blue-400" size={24} />
                </div>
                <h3 className="text-lg font-semibold text-center mb-2 text-gray-900 dark:text-white">ส่งออกข้อมูล</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-6">คุณต้องการส่งออกข้อมูลคะแนนนักศึกษาทั้งหมดเป็นไฟล์ Excel (.xlsx) ใช่หรือไม่?</p>
                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => setShowExportModal(false)} className="flex-1 rounded-lg h-10 font-medium border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300">ยกเลิก</Button>
                  <Button 
                    onClick={() => {
                      setShowExportModal(false);
                      handleExport("xlsx");
                    }} 
                    className="flex-1 rounded-lg h-10 bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-sm"
                  >
                    ยืนยัน
                  </Button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Action Controls for Pending Tab */}
        {activeTab === "pending" && (
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">สถานะ:</span>
              <div className="flex p-0.5 bg-gray-100 dark:bg-gray-800/80 rounded-lg border border-gray-200 dark:border-gray-700">
                <button onClick={() => setSubFilter("all")} className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${subFilter === "all" ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm" : "text-gray-500 hover:text-gray-700 dark:text-gray-300"}`}>ดูทั้งหมด</button>
                <button onClick={() => setSubFilter("ready")} className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${subFilter === "ready" ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400 shadow-sm" : "text-gray-500 hover:text-gray-700 dark:text-gray-300"}`}>AI มั่นใจ</button>
                <button onClick={() => setSubFilter("needs_review")} className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${subFilter === "needs_review" ? "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400 shadow-sm" : "text-gray-500 hover:text-gray-700 dark:text-gray-300"}`}>ต้องตรวจเอง</button>
              </div>
            </div>

            <Button
              variant="outline"
              onClick={toggleSelectAllVisible}
              disabled={filteredStudents.length === 0}
              className={`h-9 px-4 rounded-lg font-medium text-xs transition-all flex items-center gap-2 ${selectedIds.length === filteredStudents.length && filteredStudents.length > 0
                  ? "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800"
                  : "border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                }`}
            >
              {selectedIds.length === filteredStudents.length && filteredStudents.length > 0 ? (
                <><CheckSquare size={14} className="text-blue-600 dark:text-blue-400" /> ยกเลิกการเลือก</>
              ) : (
                <><CheckSquare size={14} className="text-gray-400 dark:text-gray-500" /> เลือกคนที่แสดงอยู่</>
              )}
            </Button>
          </div>
        )}

        {/* Student List */}
        <div className="space-y-4">
          {filteredStudents.length === 0 ? (
            <div className="py-24 text-center bg-white dark:bg-[#1E1E1E] rounded-xl border border-dashed border-gray-300 dark:border-gray-700 shadow-sm">
              <Inbox className="mx-auto mb-4 text-gray-300 dark:text-gray-600" size={48} />
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">ไม่พบรายการนักศึกษา</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-[#1A1A1A] rounded-xl overflow-hidden border border-gray-200 dark:border-gray-800 shadow-sm">
              {/* Header */}
              <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-gray-50/80 dark:bg-gray-900/80 border-b border-gray-200 dark:border-gray-800 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <div className="col-span-1 flex items-center justify-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                    checked={filteredStudents.length > 0 && selectedIds.length === filteredStudents.length}
                    onChange={toggleSelectAllVisible}
                  />
                </div>
                <div className="col-span-5 flex items-center">รายชื่อนักศึกษา</div>
                <div className="col-span-3 flex items-center">สถานะ / คะแนน</div>
                <div className="col-span-3 text-right">การดำเนินการ</div>
              </div>

              {/* Rows */}
              <div className="divide-y divide-gray-100 dark:divide-gray-800/60">
                {filteredStudents.map((student) => (
                  <div key={student.student_id} className="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-gray-50/50 dark:hover:bg-gray-900/20 transition-colors group">
                    <div className="col-span-1 flex items-center justify-center">
                      <input
                        type="checkbox"
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 cursor-pointer"
                        checked={selectedIds.includes(student.student_id)}
                        onChange={() => toggleSelectOne(student.student_id)}
                      />
                    </div>

                    <div className="col-span-5 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center font-medium text-sm text-blue-600 dark:text-blue-400 shrink-0">
                        {student.name.charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{student.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{student.student_code || student.email}</p>
                      </div>
                    </div>

                    <div className="col-span-3">
                      <StatusBadge status={student.status} score={student.total_score ?? undefined} maxScore={exam?.total_score} />
                    </div>

                    <div className="col-span-3 flex justify-end gap-2">
                      {activeTab === "pending" ? (
                        <>
                          <Button
                            variant="outline"
                            onClick={() => navigate(`/room/${roomId}/exam/${examId}/grading/${student.student_id}`)}
                            className="h-8 px-3 rounded-md text-xs font-medium border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
                          >
                            ตรวจสอบ
                          </Button>
                          <Button
                            onClick={() => handleApproveOne(student.student_id)}
                            disabled={student.status === "needs_review"}
                            className="h-8 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-medium shadow-sm"
                          >
                            อนุมัติ
                          </Button>
                        </>
                      ) : (
                        <Button
                          variant="ghost"
                          onClick={() => navigate(`/room/${roomId}/exam/${examId}/grading/${student.student_id}`)}
                          className="h-8 px-3 text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-md"
                          disabled={student.status === 'missing'}
                        >
                          {student.status === 'missing' ? 'ไม่มีข้อมูล' : 'ดูรายละเอียด'}
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Floating Action Bar */}
      {selectedIds.length > 0 && activeTab === "pending" && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-4 py-3 rounded-2xl shadow-xl flex items-center gap-6 animate-in slide-in-from-bottom-8 z-50">
          <div className="flex items-center gap-3">
            <span className="w-6 h-6 bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400 rounded-full flex items-center justify-center text-xs font-bold">{selectedIds.length}</span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">เลือกแล้ว</span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => setSelectedIds([])} className="text-sm font-medium text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors">ยกเลิก</button>
            <Button
              onClick={handleBulkApprove}
              disabled={isApproving}
              className="bg-blue-600 hover:bg-blue-700 text-white h-9 px-6 rounded-lg font-medium text-sm shadow-sm"
            >
              {isApproving ? <Loader2 size={14} className="animate-spin mr-2" /> : null}
              อนุมัติผลที่เลือก
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}