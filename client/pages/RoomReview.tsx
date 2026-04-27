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
      <div className="flex flex-col items-start">
        <span className="text-sm font-bold text-gray-900 dark:text-slate-100">พร้อมอนุมัติ</span>
        <span className="text-xs text-green-600 bg-green-50 dark:bg-green-900/20 px-2 py-0.5 rounded-md mt-1 border border-green-100 dark:border-green-900/40">
          AI: {score ?? "-"}/{maxScore ?? "-"}
        </span>
      </div>
    );
    if (status === "needs_review") return (
      <div className="flex flex-col items-start">
        <span className="text-sm font-bold text-gray-900 dark:text-slate-100">ต้องตรวจสอบ</span>
        <span className="text-xs text-orange-600 bg-orange-50 dark:bg-orange-900/20 px-2 py-0.5 rounded-md mt-1 border border-orange-100 dark:border-orange-900/40 flex items-center gap-1">
          <AlertTriangle size={10} /> AI ไม่มั่นใจ
        </span>
      </div>
    );
    if (status === "approved") return (
      <div className="flex items-center gap-2 text-green-600 dark:text-emerald-400 font-bold text-sm">
        <CheckCircle2 size={16} /> อนุมัติแล้ว ({score ?? "-"}/{maxScore ?? "-"})
      </div>
    );
    return <span className="text-gray-400 dark:text-slate-500 italic text-sm font-medium">ยังไม่ส่งข้อสอบ</span>;
  };

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-white dark:bg-slate-950">
        <Loader2 className="animate-spin text-slate-400 h-10 w-10" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <Navbar activeTab="allReviews" />

      <main className="max-w-6xl mx-auto px-6 py-12 space-y-12">

        {/* Unified Header Section */}
        <header>
          <button
            onClick={() => navigate(`/room/${roomId}/exam/${examId}`)}
            className="group flex items-center gap-2 text-slate-400 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors text-xs font-bold uppercase tracking-widest mb-8"
          >
            <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
            กลับหน้าข้อสอบ
          </button>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
            <div>
              <h1 className="text-4xl font-black tracking-tighter mb-2 text-slate-900 dark:text-white">{exam?.title}</h1>
              <p className="text-slate-500 dark:text-slate-400 font-medium">จัดการผลการประเมินและอนุมัติคะแนนนักศึกษา</p>
            </div>


          </div>
        </header>

        {/* Elegant Tabs & Filters */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-8 border-b border-slate-100 dark:border-slate-900 pb-2">
          <div className="flex gap-8">
            {[
              { id: "pending", label: "รอตรวจ", count: pendingCount, color: "text-blue-500" },
              { id: "approved", label: "อนุมัติแล้ว", count: approvedCount, color: "text-emerald-500" },
              { id: "missing", label: "ยังไม่ส่ง", count: missingCount, color: "text-slate-400" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`relative pb-4 text-xs font-black uppercase tracking-[0.2em] transition-all ${activeTab === tab.id ? "text-slate-900 dark:text-white" : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                  }`}
              >
                {tab.label}
                <span className={`ml-2 ${activeTab === tab.id ? tab.color : "opacity-40"}`}>({tab.count})</span>
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-0 right-0 h-1 bg-slate-900 dark:bg-white rounded-full" />
                )}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-4 w-full md:w-auto">
            <div className="relative flex-1 md:flex-none md:w-64">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 dark:text-slate-500 w-4 h-4" />
              <input
                placeholder="ค้นหาชื่อ..."
                className="w-full pl-11 pr-4 h-11 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800 rounded-full text-sm font-medium outline-none focus:ring-2 ring-slate-100 dark:ring-slate-800 transition-all text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-600"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="flex items-center gap-1 bg-slate-50 dark:bg-slate-900/50 p-1 rounded-full border border-slate-100 dark:border-slate-800">
              

              <Button 
                variant="ghost" 
                size="sm"
                className="h-9 w-9 rounded-full text-slate-400 dark:text-slate-500 hover:text-slate-900 dark:hover:text-white transition-all p-0" 
                onClick={() => setShowExportModal(true)} 
                disabled={isExportingXlsx || students.length === 0}
              >
                <FileText size={14} />
              </Button>
            </div>
          </div>
        </div>

        {/* Export Confirmation Modal */}
        <AnimatePresence>
          {showExportModal && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
              <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                exit={{ opacity: 0 }}
                onClick={() => setShowExportModal(false)}
                className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" 
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="relative bg-white dark:bg-slate-900 w-full max-w-sm rounded-[2.5rem] p-8 shadow-2xl border border-slate-100 dark:border-slate-800"
              >
                <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center mb-6 mx-auto">
                  <FileText className="text-blue-500" size={32} />
                </div>
                <h3 className="text-xl font-black text-center mb-2 text-slate-900 dark:text-white">ส่งออกข้อมูล</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 text-center mb-8">คุณต้องการส่งออกข้อมูลคะแนนนักศึกษาทั้งหมดเป็นไฟล์ Excel (.xlsx) ใช่หรือไม่?</p>
                <div className="grid grid-cols-2 gap-3">
                  <Button variant="ghost" onClick={() => setShowExportModal(false)} className="rounded-full h-12 font-bold">ยกเลิก</Button>
                  <Button 
                    onClick={() => {
                      setShowExportModal(false);
                      handleExport("xlsx");
                    }} 
                    className="rounded-full h-12 bg-slate-900 dark:bg-white dark:text-slate-900 text-white font-black"
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
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mr-2">Filters:</span>
            <div className="flex p-1 bg-slate-50 dark:bg-slate-900 rounded-full border border-slate-100 dark:border-slate-800">
              <button onClick={() => setSubFilter("all")} className={`px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-full transition-all ${subFilter === "all" ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm" : "text-slate-500 hover:text-slate-800 dark:text-slate-300"}`}>ดูทั้งหมด</button>
              <button onClick={() => setSubFilter("ready")} className={`px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-full transition-all ${subFilter === "ready" ? "bg-emerald-500 text-white shadow-sm" : "text-slate-500 hover:text-slate-800 dark:text-slate-300"}`}>AI มั่นใจ</button>
              <button onClick={() => setSubFilter("needs_review")} className={`px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-full transition-all ${subFilter === "needs_review" ? "bg-rose-500 text-white shadow-sm" : "text-slate-500 hover:text-slate-800 dark:text-slate-300"}`}>ต้องตรวจเอง</button>
            </div>

            <div className="h-4 w-px bg-slate-100 dark:bg-slate-900 mx-2 hidden sm:block" />

            <Button
              variant="outline"
              onClick={toggleSelectAllVisible}
              disabled={filteredStudents.length === 0}
              className={`h-9 px-4 rounded-full font-black text-[10px] uppercase tracking-widest border-2 transition-all flex items-center gap-2 ${selectedIds.length === filteredStudents.length && filteredStudents.length > 0
                  ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900"
                  : "border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
                }`}
            >
              {selectedIds.length === filteredStudents.length && filteredStudents.length > 0 ? (
                <><X size={14} /> ยกเลิกการเลือก</>
              ) : (
                <><CheckSquare size={14} /> เลือกทุกคนที่แสดงอยู่</>
              )}
            </Button>
          </div>
        )}

        {/* Student List - Unified Design */}
        <div className="space-y-4">
          {filteredStudents.length === 0 ? (
            <div className="py-32 text-center bg-slate-50 dark:bg-slate-900/50 rounded-[2.5rem] border border-dashed border-slate-200 dark:border-slate-800">
              <Inbox className="mx-auto mb-4 text-slate-300 dark:text-slate-700" size={48} />
              <p className="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">ไม่พบรายการนักศึกษา</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden border border-slate-100 dark:border-slate-800">
              <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-slate-50 dark:bg-slate-800/50 rounded-t-2xl text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">
                <div className="col-span-1 flex items-center justify-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded-full border-2 border-slate-300 checked:bg-slate-900"
                    checked={filteredStudents.length > 0 && selectedIds.length === filteredStudents.length}
                    onChange={toggleSelectAllVisible}
                  />
                </div>
                <div className="col-span-5">รายชื่อนักศึกษา</div>
                <div className="col-span-3">สถานะ AI</div>
                <div className="col-span-3 text-right">การดำเนินการ</div>
              </div>

              <div className="divide-y divide-slate-50 dark:divide-slate-900">
                {filteredStudents.map((student) => (
                  <div key={student.student_id} className="grid grid-cols-12 gap-4 px-6 py-6 items-center hover:bg-slate-50 dark:hover:bg-slate-900/30 transition-all group">
                    <div className="col-span-1 flex items-center justify-center">
                      <input
                        type="checkbox"
                        className="w-4 h-4 rounded-full border-2 border-slate-300 transition-all cursor-pointer"
                        checked={selectedIds.includes(student.student_id)}
                        onChange={() => toggleSelectOne(student.student_id)}
                      />
                    </div>

                    <div className="col-span-5 flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-bold text-xs text-slate-500 dark:text-slate-400">
                        {student.name.charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-black truncate text-slate-900 dark:text-slate-100">{student.name}</p>
                        <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest truncate">{student.student_code || student.email}</p>
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
                            className="h-9 px-4 rounded-full font-black text-[10px] uppercase tracking-widest border-2"
                          >
                            ตรวจสอบ
                          </Button>
                          <Button
                            onClick={() => handleApproveOne(student.student_id)}
                            disabled={student.status === "needs_review"}
                            className="h-9 w-24 bg-slate-900 dark:bg-white dark:text-slate-900 rounded-full font-black text-[10px] uppercase tracking-widest shadow-xl shadow-slate-100 dark:shadow-none"
                          >
                            อนุมัติ
                          </Button>
                        </>
                      ) : (
                        <Button
                          variant="ghost"
                          onClick={() => navigate(`/room/${roomId}/exam/${examId}/grading/${student.student_id}`)}
                          className="h-9 px-4 font-black text-[10px] uppercase tracking-widest text-slate-400 hover:text-slate-900"
                          disabled={student.status === 'missing'}
                        >
                          {student.status === 'missing' ? 'ไม่มีข้อมูล' : 'รายละเอียด'}
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

      {/* Floating Action Bar - Minimalist */}
      {selectedIds.length > 0 && activeTab === "pending" && (
        <div className="fixed bottom-12 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-8 py-4 rounded-full shadow-2xl flex items-center gap-8 animate-in slide-in-from-bottom-8 z-50">
          <div className="flex items-center gap-3">
            <span className="w-6 h-6 bg-white text-slate-900 rounded-full flex items-center justify-center text-[10px] font-black">{selectedIds.length}</span>
            <span className="text-xs font-black uppercase tracking-[0.2em]">รายการที่เลือก</span>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setSelectedIds([])} className="text-[10px] font-black uppercase tracking-widest opacity-50 hover:opacity-100 transition-opacity">ยกเลิก</button>
            <Button
              onClick={handleBulkApprove}
              disabled={isApproving}
              className="bg-white text-slate-900 hover:bg-slate-100 h-10 px-8 rounded-full font-black text-[10px] uppercase tracking-widest"
            >
              {isApproving ? <Loader2 size={12} className="animate-spin mr-2" /> : null}
              อนุมัติที่เลือก
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}