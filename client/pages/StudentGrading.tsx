import { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import {
  ChevronLeft, ChevronRight, CheckCircle2, AlertTriangle,
  MessageSquare, BookOpen, AlertCircle, X, Loader2, Save
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

// ---- Types ----
interface Rubric {
  id?: number;
  name?: string;
  label?: string;
  score?: number;
  maxScore?: number;
  description?: string;
}

interface AnswerData {
  id: number;
  question_id: number;
  question_text: string;
  max_score: number;
  answer_text: string;
  ai_score: number;
  ai_feedback: string;
  ai_confidence: "high" | "medium" | "low";
  teacher_score?: number;
  teacher_comment?: string;
  rubrics?: Rubric[];
  answer_key?: string;
  image_path?: string;
  image_paths?: string[];
  q_image_path?: string;
  q_image_paths?: string[];
  quality_metrics?: string;
}

interface StudentInfo {
  student_id: number;
  name: string;
  student_code?: string;
  email: string;
}

interface StudentListItem {
  student_id: number;
  name: string;
  status: string;
}

// ---- Component ----
export default function StudentGrading() {
  const navigate = useNavigate();
  const { roomId, examId, studentId } = useParams();
  const { user, token, isLoading } = useAuth();

  // Page state
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [isApproving, setIsApproving] = useState(false);

  // Data
  const [studentInfo, setStudentInfo] = useState<StudentInfo | null>(null);
  const [answers, setAnswers] = useState<AnswerData[]>([]);
  const [submissionStatus, setSubmissionStatus] = useState<string>("ready");
  const [scores, setScores] = useState<Record<number, number>>({});
  const [comments, setComments] = useState<Record<number, string>>({});

  // Navigation between students
  const [studentsList, setStudentsList] = useState<StudentListItem[]>([]);
  const [currentStudentIndex, setCurrentStudentIndex] = useState(0);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [user, isLoading, navigate]);

  // Load student list for navigation
  useEffect(() => {
    if (!token || !roomId || !examId) return;
    fetch(`/api/rooms/${roomId}/exams/${examId}/submissions`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data: StudentListItem[]) => {
        const withSubmissions = data.filter(
          (s) => s.status !== "missing"
        );
        setStudentsList(withSubmissions);
        const idx = withSubmissions.findIndex(
          (s) => String(s.student_id) === studentId
        );
        setCurrentStudentIndex(idx >= 0 ? idx : 0);
      })
      .catch(() => {});
  }, [token, roomId, examId, studentId]);

  // Load submission data for current student
  const fetchSubmission = useCallback(async (sid: string) => {
    if (!token || !roomId || !examId) return;
    setIsFetching(true);
    try {
      const res = await fetch(
        `/api/rooms/${roomId}/exams/${examId}/submissions/${sid}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) {
        toast.error("ยังไม่มีข้อมูลการส่งงานของนักเรียนคนนี้");
        setIsFetching(false);
        return;
      }
      const data = await res.json();
      setStudentInfo(data.student);
      setAnswers(data.answers || []);
      setSubmissionStatus(data.submission?.status ?? "ready");

      // Pre-fill scores with AI scores (or teacher override if already approved)
      const scoreMap: Record<number, number> = {};
      const commentMap: Record<number, string> = {};
      for (const a of data.answers || []) {
        scoreMap[a.question_id] =
          a.teacher_score !== null && a.teacher_score !== undefined
            ? a.teacher_score
            : a.ai_score;
        commentMap[a.question_id] = a.teacher_comment || "";
      }
      setScores(scoreMap);
      setComments(commentMap);
    } catch {
      toast.error("เกิดข้อผิดพลาดในการโหลดข้อมูล");
    } finally {
      setIsFetching(false);
    }
  }, [token, roomId, examId]);

  useEffect(() => {
    if (studentId) fetchSubmission(studentId);
  }, [studentId, fetchSubmission]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [studentId]);

  const handleScoreChange = (qId: number, val: string) => {
    const num = parseFloat(val);
    if (!isNaN(num)) setScores((prev) => ({ ...prev, [qId]: num }));
  };

  const handleCommentChange = (qId: number, val: string) => {
    setComments((prev) => ({ ...prev, [qId]: val }));
  };

  const navigateToStudent = (index: number) => {
    if (index < 0 || index >= studentsList.length) return;
    const target = studentsList[index];
    setCurrentStudentIndex(index);
    navigate(`/room/${roomId}/exam/${examId}/grading/${target.student_id}`, {
      replace: true,
    });
  };

  const onApproveClick = () => setIsConfirmOpen(true);

  const confirmApprove = async () => {
    if (!token) return;
    setIsApproving(true);
    setIsConfirmOpen(false);

    const teacherScores: Record<string, number> = {};
    const teacherComments: Record<string, string> = {};

    for (const a of answers) {
      teacherScores[String(a.question_id)] = scores[a.question_id] ?? a.ai_score;
      if (comments[a.question_id])
        teacherComments[String(a.question_id)] = comments[a.question_id];
    }

    try {
      const res = await fetch(
        `/api/rooms/${roomId}/exams/${examId}/submissions/${studentId}/approve`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            teacher_scores: teacherScores,
            teacher_comments: teacherComments,
          }),
        }
      );

      if (res.ok) {
        toast.success(`อนุมัติผลของ ${studentInfo?.name} สำเร็จ`);
        setSubmissionStatus("approved");

        // Update status in navigation list
        setStudentsList((prev) =>
          prev.map((s) =>
            String(s.student_id) === studentId ? { ...s, status: "approved" } : s
          )
        );

        // Auto navigate to next student
        const nextIndex = currentStudentIndex + 1;
        if (nextIndex < studentsList.length) {
          setTimeout(() => navigateToStudent(nextIndex), 400);
        } else {
          toast.info("ตรวจครบทุกคนในรายการแล้ว!");
          setTimeout(() => navigate(`/room/${roomId}/exam/${examId}/review`), 800);
        }
      } else {
        const err = await res.json();
        toast.error(err.detail || "ไม่สามารถอนุมัติได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsApproving(false);
    }
  };

  const currentStudentName =
    studentInfo?.name ?? studentsList[currentStudentIndex]?.name ?? "...";
  const isApproved = submissionStatus === "approved";

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24 relative">
      <Navbar activeTab="allReviews" />

      {/* --- CONFIRMATION MODAL --- */}
      {isConfirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all scale-100 animate-in zoom-in-95 duration-200 border border-gray-100 dark:border-slate-800">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 text-green-600">
                <CheckCircle2 size={32} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {isApproved ? "ยืนยันการแก้ไข?" : "ยืนยันการอนุมัติ?"}
              </h3>
              <p className="text-gray-500 dark:text-slate-400">
                คุณต้องการ{isApproved ? "บันทึกการแก้ไขผล" : "อนุมัติผล"}การตรวจของ <br />
                <span className="font-bold text-gray-800 dark:text-slate-200 text-lg">"{currentStudentName}"</span> ใช่หรือไม่?
                <br />
                <span className="text-sm text-gray-400 dark:text-slate-500 mt-1 block">คะแนนที่คุณแก้ไขจะถูกบันทึกด้วย</span>
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setIsConfirmOpen(false)}
                className="flex-1 h-12 text-base border-gray-300 text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:bg-slate-900 rounded-xl"
              >
                <X size={16} className="mr-2" /> ยกเลิก
              </Button>
              <Button
                onClick={confirmApprove}
                disabled={isApproving}
                className="flex-1 h-12 text-base bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl shadow-lg shadow-green-100"
              >
                {isApproving ? <Loader2 size={16} className="animate-spin mr-2" /> : null}
                {isApproved ? "ตกลง แก้ไข" : "ยืนยันอนุมัติ"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Sticky Header Bar */}
      <div className="sticky top-[80px] z-30 bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 shadow-sm px-4 py-3">
        <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">

          {/* Navigator */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => navigateToStudent(currentStudentIndex - 1)}
              disabled={currentStudentIndex === 0 || studentsList.length === 0}
              className="h-9 px-2 text-gray-500 dark:text-slate-400 hover:text-[#3B82F6] transition-colors"
            >
              <ChevronLeft size={18} />
            </Button>
            <div className="text-center px-4 min-w-[180px]">
              <p className="text-xs font-medium text-gray-400 dark:text-slate-500 uppercase tracking-wide">
                ลำดับที่ {currentStudentIndex + 1} / {studentsList.length}
              </p>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white leading-none mt-0.5">
                {currentStudentName}
              </h2>
              {studentInfo?.student_code && (
                <p className="text-xs text-gray-400 dark:text-slate-500">{studentInfo.student_code}</p>
              )}
            </div>
            <Button
              variant="outline"
              onClick={() => navigateToStudent(currentStudentIndex + 1)}
              disabled={currentStudentIndex >= studentsList.length - 1 || studentsList.length === 0}
              className="h-9 px-2 text-gray-500 dark:text-slate-400 hover:text-[#3B82F6] transition-colors"
            >
              <ChevronRight size={18} />
            </Button>
          </div>

          {/* Status Badge */}
          <div
            className="hidden md:flex items-center gap-2 px-4 py-1.5 rounded-full border text-sm font-medium transition-colors duration-300"
            style={{
              backgroundColor:
                isApproved ? "#ECFDF5" :
                submissionStatus === "needs_review" ? "#FFF7ED" : "#F0F9FF",
              color:
                isApproved ? "#059669" :
                submissionStatus === "needs_review" ? "#C2410C" : "#0369A1",
              borderColor:
                isApproved ? "#A7F3D0" :
                submissionStatus === "needs_review" ? "#FED7AA" : "#BAE6FD",
            }}
          >
            {isApproved ? <CheckCircle2 size={16} /> :
              submissionStatus === "needs_review" ? <AlertTriangle size={16} /> :
              <CheckCircle2 size={16} />}
            สถานะ: {
              isApproved ? "อนุมัติแล้ว" :
              submissionStatus === "needs_review" ? "AI ไม่มั่นใจ (Needs Review)" :
              "พร้อมตรวจ (Ready)"
            }
          </div>

          {/* Actions */}
          <div className="flex gap-3 w-full md:w-auto">
            <Button
              variant="ghost"
              onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)}
              className="text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:text-slate-300"
            >
              กลับรายชื่อ
            </Button>
            <Button
              onClick={onApproveClick}
              disabled={isApproving}
              className={`min-w-[140px] shadow-sm font-bold transition-all ${
                isApproved
                  ? "bg-amber-500 hover:bg-amber-600 text-white hover:shadow-md hover:scale-105 active:scale-95"
                  : "bg-green-600 hover:bg-green-700 text-white hover:shadow-md hover:scale-105 active:scale-95"
              }`}
            >
              {isApproved ? (
                <> <Save className="mr-2 w-4 h-4" /> บันทึกการแก้ไข</>
              ) : (
                <><CheckCircle2 className="mr-2 w-4 h-4" /> อนุมัติผลตรวจ</>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-[1200px] mx-auto p-4 md:p-8 space-y-8 mt-4 animate-in fade-in duration-500">

        {answers.length === 0 ? (
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-gray-200 dark:border-slate-700 p-20 text-center">
            <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-slate-400 font-medium">ไม่พบข้อมูลคำตอบของนักเรียนคนนี้</p>
          </div>
        ) : (
          answers.map((a, index) => (
            <div
              key={a.question_id}
              className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-gray-200 dark:border-slate-700 overflow-hidden flex flex-col lg:flex-row"
            >
              {/* Left Panel — Question & Rubrics */}
              <div className="lg:w-1/3 bg-gray-50 dark:bg-slate-900 p-6 border-b lg:border-b-0 lg:border-r border-gray-200 dark:border-slate-700">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-[#3B82F6] text-white font-bold flex items-center justify-center shadow-sm">
                    {index + 1}
                  </div>
                  <span className="text-xs font-bold text-gray-500 dark:text-slate-400 uppercase tracking-wider">โจทย์คำถาม</span>
                </div>
                <h3 className="text-gray-900 dark:text-white font-medium leading-relaxed mb-6">
                  {a.question_text}
                </h3>

                {/* Question Images */}
                {(a.q_image_paths && a.q_image_paths.length > 0) ? (
                  <div className="mb-6 grid grid-cols-1 gap-2">
                    {a.q_image_paths.map((src, i) => (
                      <img
                        key={i}
                        src={src}
                        alt={`รูปโจทย์รูปที่ ${i + 1}`}
                        className="w-full rounded-xl border border-gray-200 dark:border-slate-700 shadow-sm object-contain bg-white dark:bg-slate-800 max-h-64"
                      />
                    ))}
                  </div>
                ) : a.q_image_path ? (
                  <div className="mb-6">
                    <img
                      src={a.q_image_path}
                      alt="รูปโจทย์"
                      className="w-full rounded-xl border border-gray-200 dark:border-slate-700 shadow-sm object-contain bg-white dark:bg-slate-800 max-h-64"
                    />
                  </div>
                ) : null}

                {a.answer_key && (
                  <div className="mb-4 bg-emerald-50 rounded-xl p-4 border border-emerald-100">
                    <p className="text-xs font-bold text-emerald-700 mb-1 flex items-center gap-1">
                      <CheckCircle2 size={12} /> แนวคำตอบ
                    </p>
                    <p className="text-sm text-emerald-800 leading-relaxed">{a.answer_key}</p>
                  </div>
                )}

                {a.rubrics && a.rubrics.length > 0 && (
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-3 text-gray-700 dark:text-slate-300 font-semibold text-sm">
                      <BookOpen size={16} /> เกณฑ์การให้คะแนน
                    </div>
                    <ul className="space-y-3">
                      {a.rubrics.map((r, i) => (
                        <li key={i} className="text-sm flex justify-between items-start border-b border-gray-100 dark:border-slate-800 pb-2 last:border-0 last:pb-0">
                          <span className="text-gray-600 dark:text-slate-400">{r.name || r.label}</span>
                          <span className="font-mono font-bold text-gray-400 dark:text-slate-500 text-xs bg-gray-100 px-2 py-0.5 rounded ml-2">
                            max {r.score ?? r.maxScore}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Right Panel — Answer + AI + Score */}
              <div className="lg:w-2/3 p-6 flex flex-col">
                {/* Student Answer */}
                <div className="mb-8">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-sm font-bold text-gray-700 dark:text-slate-300">คำตอบของนักเรียน</h4>
                    <span className="text-xs text-gray-400 dark:text-slate-500">
                      {studentInfo?.student_code || studentInfo?.email}
                    </span>
                  </div>
                  <div className="p-4 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-800 dark:text-slate-200 leading-relaxed text-base shadow-sm min-h-[80px] whitespace-pre-wrap">
                    {a.answer_text || (
                      <span className="text-gray-300 italic">ไม่มีคำตอบ</span>
                    )}
                  </div>

                  {/* Student Answer Images */}
                  {(a.image_paths && a.image_paths.length > 0) ? (
                    <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {a.image_paths.map((src, i) => (
                        <div key={i} className="group relative aspect-video rounded-xl overflow-hidden border border-gray-200 dark:border-slate-700 shadow-sm bg-gray-50 dark:bg-slate-900">
                          <img
                            src={src}
                            alt={`รูปคำตอบที่ ${i + 1}`}
                            className="w-full h-full object-contain"
                          />
                          <a 
                            href={src} 
                            target="_blank" 
                            rel="noreferrer"
                            className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity text-white text-xs font-bold"
                          >
                            ดูรูปเต็ม
                          </a>
                        </div>
                      ))}
                    </div>
                  ) : a.image_path ? (
                    <div className="mt-4">
                      <img
                        src={a.image_path}
                        alt="รูปคำตอบ"
                        className="max-h-80 w-auto rounded-xl border border-gray-200 dark:border-slate-700 shadow-sm"
                      />
                    </div>
                  ) : null}
                </div>

                {/* AI Feedback Section */}
                <div
                  className={`rounded-xl border-2 p-5 relative transition-all ${
                    a.ai_confidence === "low"
                      ? "border-orange-100 bg-orange-50/30"
                      : "border-blue-100 bg-blue-50 dark:bg-blue-900/30/20"
                  }`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-2">
                      <div className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-[10px] font-bold px-2 py-1 rounded shadow-sm flex items-center gap-1">
                        ✨ AI Feedback
                      </div>
                      {a.ai_confidence === "low" && (
                        <span className="text-xs text-orange-600 font-medium flex items-center gap-1">
                          <AlertCircle size={12} /> ความมั่นใจต่ำ โปรดตรวจสอบ
                        </span>
                      )}
                      {a.ai_confidence === "medium" && (
                        <span className="text-xs text-yellow-600 font-medium flex items-center gap-1">
                          <AlertTriangle size={12} /> ความมั่นใจปานกลาง
                        </span>
                      )}
                    </div>

                    {/* Score Editor */}
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="text-[10px] text-gray-500 dark:text-slate-400 font-medium uppercase">คะแนนประเมิน</p>
                        <div className="flex items-baseline gap-1 justify-end">
                          <span className="text-2xl font-bold text-[#3B82F6]">
                            {scores[a.question_id] ?? a.ai_score}
                          </span>
                          <span className="text-gray-400 dark:text-slate-500 text-sm">/ {a.max_score}</span>
                        </div>
                      </div>
                      <Input
                        type="number"
                        id={`score-q${a.question_id}`}
                        className="w-20 h-12 text-center text-lg font-bold border-gray-300 focus:border-[#3B82F6] focus:ring-[#3B82F6]"
                        value={scores[a.question_id] ?? a.ai_score}
                        onChange={(e) => handleScoreChange(a.question_id, e.target.value)}
                        max={a.max_score}
                        min={0}
                      />
                    </div>
                  </div>

                  {/* AI Feedback Text */}
                  <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300 text-sm leading-relaxed mb-4">
                    {a.ai_feedback || "ไม่มี feedback จาก AI"}
                  </div>

                  {/* Quality Metrics */}
                  {a.quality_metrics && (
                    <div className="grid grid-cols-3 gap-2 mb-4">
                      {(() => {
                        try {
                          const m = JSON.parse(a.quality_metrics);
                          return (
                            <>
                              <div className="bg-white/50 dark:bg-slate-800/50 p-2 rounded-lg border border-gray-100 dark:border-slate-700 flex flex-col items-center text-center">
                                <span className="text-[10px] text-gray-400 dark:text-slate-500 font-bold uppercase">ความยาว</span>
                                <span className="text-xs font-semibold text-gray-700 dark:text-slate-300">{m.length_eval || "-"}</span>
                              </div>
                              <div className="bg-white/50 dark:bg-slate-800/50 p-2 rounded-lg border border-gray-100 dark:border-slate-700 flex flex-col items-center text-center">
                                <span className="text-[10px] text-gray-400 dark:text-slate-500 font-bold uppercase">ความซับซ้อน</span>
                                <span className="text-xs font-semibold text-gray-700 dark:text-slate-300">{m.complexity_eval || "-"}</span>
                              </div>
                              <div className="bg-white/50 dark:bg-slate-800/50 p-2 rounded-lg border border-gray-100 dark:border-slate-700 flex flex-col items-center text-center">
                                <span className="text-[10px] text-gray-400 dark:text-slate-500 font-bold uppercase">ความลื่นไหล</span>
                                <span className="text-xs font-semibold text-gray-700 dark:text-slate-300">{m.readability_eval || "-"}</span>
                              </div>
                            </>
                          );
                        } catch (e) { return null; }
                      })()}
                    </div>
                  )}

                  {/* Teacher Comment */}
                  <div className="flex items-start gap-3 mt-4 pt-4 border-t border-gray-200 dark:border-slate-700/50">
                    <MessageSquare className="w-5 h-5 text-gray-400 dark:text-slate-500 mt-2" />
                    <div className="flex-1 space-y-2">
                      <label className="text-xs font-bold text-gray-500 dark:text-slate-400">
                        ความคิดเห็นอาจารย์ (Optional)
                      </label>
                      <Textarea
                        id={`comment-q${a.question_id}`}
                        placeholder="พิมพ์คำแนะนำให้นักเรียน..."
                        className="min-h-[60px] bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700 focus:border-[#3B82F6] resize-none"
                        value={comments[a.question_id] || ""}
                        onChange={(e) => handleCommentChange(a.question_id, e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </main>
    </div>
  );
}