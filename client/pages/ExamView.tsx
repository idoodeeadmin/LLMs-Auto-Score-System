import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Trophy, FileText, ChevronDown, ChevronUp,
  CheckCircle2, Loader2, Calendar, Clock, ClipboardCheck,
  Send, AlertCircle, BarChart3, Pencil, Trash2, TimerReset, Users
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import ImageModal from "@/components/ImageModal";

interface Rubric {
  name: string;
  description: string;
  score: number;
}

interface Question {
  id: number;
  text: string;
  score: number;
  answer_key?: string;
  rubrics?: Rubric[];
  order_index: number;
  image_path?: string | null;
  image_paths?: string[];  // multiple images
}

interface Exam {
  id: number;
  room_id: number;
  title: string;
  description?: string;
  total_score: number;
  start_date?: string;
  end_date?: string;
  created_at: string;
  questions: Question[];
}

export default function ExamView() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();
  const [exam, setExam] = useState<Exam | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [mySubmission, setMySubmission] = useState<{ 
    status: string; 
    total_score?: number;
    answers?: any[];
  } | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showExtensionPanel, setShowExtensionPanel] = useState(false);
  const [extStudentId, setExtStudentId] = useState<"" | number>("");
  const [extMinutes, setExtMinutes] = useState(15);
  const [extNote, setExtNote] = useState("");
  const [isGranting, setIsGranting] = useState(false);
  const [extensions, setExtensions] = useState<any[]>([]);

  // Image Modal State
  const [modalImage, setModalImage] = useState<{ src: string; alt: string } | null>(null);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
  }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || !roomId || !examId) return;
    const fetchExam = async () => {
      try {
        const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          setExam(await res.json());
        } else {
          toast.error("ไม่พบข้อสอบนี้");
          navigate(`/room/${roomId}`);
        }
      } catch {
        toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
      } finally {
        setIsFetching(false);
      }
    };
    fetchExam();

    // Fetch student's own submission status and poll if 'submitted'
    if (user?.role === "student") {
      let intervalId: NodeJS.Timeout;
      const checkStatus = async () => {
        try {
          const r = await fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (r.ok) {
            const data = await r.json();
            setMySubmission(data);
            if (data.status !== "submitted" && intervalId) {
              clearInterval(intervalId);
            }
          }
        } catch (e) {
          console.error(e);
        }
      };
      
      checkStatus(); // Initial fetch
      intervalId = setInterval(checkStatus, 5000); // Poll every 5 seconds
      
      return () => clearInterval(intervalId);
    }
  }, [token, roomId, examId, user?.role, navigate]);

  if (isLoading || isFetching || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  const isTeacher = user.role === "teacher";
  const formatDate = (d?: string) => d ? new Date(d).toLocaleDateString("th-TH", { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : null;

  const handleDeleteExam = async () => {
    if (!token || !roomId || !examId) return;
    setIsDeleting(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        toast.success("ลบข้อสอบเรียบร้อยแล้ว");
        navigate(`/room/${roomId}`);
      } else {
        const err = await res.json();
        toast.error(err.detail || "ไม่สามารถลบข้อสอบ");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const fetchExtensions = async () => {
    if (!token || !roomId || !examId) return;
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/extensions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setExtensions(await res.json());
    } catch { /* ignore */ }
  };

  const handleGrantExtension = async () => {
    if (!token || !roomId || !examId || extMinutes <= 0) return;
    setIsGranting(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/extensions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: extStudentId !== "" ? extStudentId : null,
          extra_minutes: extMinutes,
          note: extNote || null,
        }),
      });
      if (res.ok) {
        toast.success("ขยายเวลาสำเร็จ!");
        setExtStudentId("");
        setExtNote("");
        setExtMinutes(15);
        fetchExtensions();
      } else {
        const err = await res.json();
        toast.error(err.detail || "ไม่สามารถขยายเวลาได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาด");
    } finally {
      setIsGranting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 pb-24">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* Back Button + Teacher Action */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate(`/room/${roomId}`)}
            className="flex items-center gap-2 text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:text-slate-200 transition-colors text-sm font-medium"
          >
            <ArrowLeft size={18} /> กลับหน้าห้อง
          </button>
          {isTeacher && (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => navigate(`/room/${roomId}/exam/${examId}/edit`)}
                className="gap-2"
              >
                <Pencil size={16} /> แก้ไข
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowDeleteModal(true)}
                className="gap-2 text-red-600 border-red-200 hover:bg-red-50 dark:bg-red-900/30"
              >
                <Trash2 size={16} /> ลบ
              </Button>
              <Button
                variant="outline"
                onClick={() => { setShowExtensionPanel(!showExtensionPanel); if (!showExtensionPanel) fetchExtensions(); }}
                className="gap-2 text-green-700 border-green-200 hover:bg-green-50 dark:text-green-400 dark:border-green-800"
              >
                <TimerReset size={16} /> ขยายเวลา
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate(`/room/${roomId}/exam/${examId}/analytics`)}
                className="gap-2"
              >
                <BarChart3 size={16} /> Analytics
              </Button>
              <Button
                onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)}
                className="bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-100 gap-2"
              >
                <ClipboardCheck size={16} /> ตรวจ / อนุมัติผล
              </Button>
            </div>
          )}
        </div>

        {/* Time Extension Panel */}
        {isTeacher && showExtensionPanel && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-green-50 dark:bg-green-900/20 rounded-2xl border border-green-200 dark:border-green-800 p-6"
          >
            <h3 className="font-bold text-green-800 dark:text-green-300 flex items-center gap-2 mb-4">
              <TimerReset size={18} /> ขยายเวลาทำข้อสอบ
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
              <div className="md:col-span-1">
                <label className="text-xs font-bold text-gray-500 dark:text-slate-400 mb-1 block">Student ID (เว้นว่าง = ทั้งห้อง)</label>
                <input
                  type="number"
                  placeholder="เว้นว่าง = ทั้งห้อง"
                  value={extStudentId}
                  onChange={e => setExtStudentId(e.target.value ? parseInt(e.target.value) : "")}
                  className="w-full h-10 px-3 rounded-xl border border-green-200 dark:border-green-800 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-green-300"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-gray-500 dark:text-slate-400 mb-1 block">เวลาเพิ่ม (นาที)</label>
                <input
                  type="number"
                  min="1"
                  value={extMinutes}
                  onChange={e => setExtMinutes(parseInt(e.target.value) || 1)}
                  className="w-full h-10 px-3 rounded-xl border border-green-200 dark:border-green-800 bg-white dark:bg-slate-800 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-green-300"
                />
              </div>
              <div className="md:col-span-1">
                <label className="text-xs font-bold text-gray-500 dark:text-slate-400 mb-1 block">หมายเหตุ (ไม่บังคับ)</label>
                <input
                  value={extNote}
                  onChange={e => setExtNote(e.target.value)}
                  placeholder="เช่น การสอบพิเศษ..."
                  className="w-full h-10 px-3 rounded-xl border border-green-200 dark:border-green-800 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-green-300"
                />
              </div>
              <Button
                onClick={handleGrantExtension}
                disabled={isGranting || extMinutes <= 0}
                className="bg-green-600 hover:bg-green-700 text-white h-10 rounded-xl"
              >
                {isGranting ? <Loader2 size={16} className="animate-spin" /> : <><TimerReset size={15} className="mr-1" /> ยืนยันขยายเวลา</>}
              </Button>
            </div>

            {/* Extension History */}
            {extensions.length > 0 && (
              <div className="mt-4 border-t border-green-200 dark:border-green-800 pt-4">
                <p className="text-xs font-bold text-green-700 dark:text-green-400 mb-2 flex items-center gap-1">
                  <Users size={12} /> ประวัติการขยายเวลา
                </p>
                <div className="space-y-1">
                  {extensions.map((ext) => (
                    <div key={ext.id} className="flex items-center gap-3 text-xs text-gray-600 dark:text-slate-400 bg-white dark:bg-slate-800 rounded-lg px-3 py-2">
                      <span className="font-bold text-green-600">+{ext.extra_minutes}นาที</span>
                      <span>{ext.student_name ? ext.student_name : <span className="text-blue-500 font-medium">ทั้งห้อง</span>}</span>
                      {ext.note && <span className="text-gray-400">— {ext.note}</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Exam Header */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-indigo-600 to-blue-500 rounded-3xl p-8 text-white shadow-xl"
        >
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <p className="text-white/70 text-sm uppercase tracking-wider mb-1">ข้อสอบ</p>
              <h1 className="text-2xl sm:text-3xl font-bold">{exam?.title}</h1>
              {exam?.description && <p className="text-white/80 mt-1">{exam.description}</p>}
              <div className="flex flex-wrap gap-3 mt-3 text-sm text-white/80">
                {exam?.start_date && (
                  <span className="flex items-center gap-1">
                    <Calendar size={14} /> {formatDate(exam.start_date)}
                  </span>
                )}
                {exam?.end_date && (
                  <span className="flex items-center gap-1">
                    <Clock size={14} /> ถึง {formatDate(exam.end_date)}
                  </span>
                )}
              </div>
            </div>
            <div className="flex gap-4">
              <div className="text-center bg-white/10 backdrop-blur-sm rounded-2xl px-5 py-3">
                <p className="text-white/70 text-xs uppercase tracking-wide">คะแนนเต็ม</p>
                <p className="text-3xl font-bold">{exam?.total_score}</p>
              </div>
              <div className="text-center bg-white/10 backdrop-blur-sm rounded-2xl px-5 py-3">
                <p className="text-white/70 text-xs uppercase tracking-wide">จำนวนข้อ</p>
                <p className="text-3xl font-bold">{exam?.questions.length}</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Questions List */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0, transition: { delay: 0.1 } }}
          className="space-y-4"
        >
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200">รายการคำถาม</h2>

          {exam?.questions.length === 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-12 text-center shadow-sm">
              <FileText className="h-10 w-10 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500">ยังไม่มีคำถามในข้อสอบนี้</p>
            </div>
          )}

          {exam?.questions.map((q, index) => (
            <div
              key={q.id}
              className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm overflow-hidden hover:border-indigo-200 transition-colors"
            >
              {/* Question Header */}
              <div className="p-5 flex gap-4 items-start">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 font-bold text-sm flex items-center justify-center flex-shrink-0">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="text-slate-800 dark:text-slate-200 font-medium leading-relaxed">{q.text}</p>
                  {/* Question images attached by teacher — gallery */}
                  {(q.image_paths && q.image_paths.length > 0) ? (
                    <div className="mt-3 grid grid-cols-2 gap-2">
                      {q.image_paths.map((src, i) => (
                        <img
                          key={i}
                          src={src}
                          alt={`รูปโจทย์ข้อ ${index + 1} รูปที่ ${i + 1}`}
                          className="w-full rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm object-contain bg-gray-50 dark:bg-slate-900 max-h-56 cursor-zoom-in hover:opacity-90 transition-opacity"
                          onClick={() => setModalImage({ src, alt: `โจทย์ข้อ ${index + 1} (${i + 1}/${q.image_paths?.length})` })}
                        />
                      ))}
                    </div>
                  ) : q.image_path ? (
                    <div className="mt-3">
                      <img
                        src={q.image_path}
                        alt={`รูปโจทย์ข้อ ${index + 1}`}
                        className="max-h-72 w-auto rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm object-contain bg-gray-50 dark:bg-slate-900 cursor-zoom-in hover:opacity-90 transition-opacity"
                        onClick={() => setModalImage({ src: q.image_path!, alt: `โจทย์ข้อ ${index + 1}` })}
                      />
                    </div>
                  ) : null}
                </div>
                <span className="flex-shrink-0 text-sm font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1 rounded-full border border-indigo-100">
                  {q.score} คะแนน
                </span>
              </div>

              {/* Teacher sees answer key toggle */}
              {isTeacher && (q.answer_key || (q.rubrics && q.rubrics.length > 0)) && (
                <div className="border-t border-slate-50">
                  <button
                    onClick={() => setExpandedId(expandedId === q.id ? null : q.id)}
                    className="w-full flex items-center justify-center gap-2 py-2.5 text-sm text-slate-400 dark:text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 dark:bg-indigo-900/30/50 transition-colors font-medium"
                  >
                    {expandedId === q.id
                      ? <><ChevronUp size={15} /> ซ่อนเฉลย</>
                      : <><ChevronDown size={15} /> ดูเฉลยและเกณฑ์</>
                    }
                  </button>

                  <AnimatePresence>
                    {expandedId === q.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="px-5 pb-5 pt-2 space-y-4 bg-slate-50 dark:bg-slate-900/50">
                          {q.answer_key && (
                            <div>
                              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                <CheckCircle2 size={13} className="text-emerald-500" /> แนวคำตอบ
                              </p>
                              <p className="text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 text-sm leading-relaxed">
                                {q.answer_key}
                              </p>
                            </div>
                          )}

                          {q.rubrics && q.rubrics.length > 0 && (
                            <div>
                              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">เกณฑ์การให้คะแนน</p>
                              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                                {q.rubrics.map((r, i) => (
                                  <div key={i} className={`flex items-center justify-between px-4 py-3 text-sm ${i !== 0 ? "border-t border-slate-50" : ""}`}>
                                    <div>
                                      <p className="font-semibold text-slate-700 dark:text-slate-300">{r.name}</p>
                                      {r.description && <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 text-xs mt-0.5">{r.description}</p>}
                                    </div>
                                    <span className="font-bold text-indigo-600 ml-4 flex-shrink-0">{r.score} คะแนน</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </div>
          ))}
        </motion.div>

        {/* Student: Submit Section */}
        {!isTeacher && (
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0, transition: { delay: 0.2 } }}
          >
            {!mySubmission || mySubmission.status === "missing" ? (
              /* Not submitted yet */
              <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm p-8 text-center">
                <div className="w-16 h-16 bg-indigo-50 dark:bg-indigo-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send size={28} className="text-indigo-500" />
                </div>
                <h3 className="text-xl font-bold text-slate-700 dark:text-slate-300 mb-2">พร้อมทำข้อสอบ?</h3>
                <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 text-sm mb-6 leading-relaxed">
                  รองรับการตอบแบบ <strong>พิมพ์ข้อความ</strong> และ <strong>ถ่ายรูปคำตอบ</strong><br />
                  หลังส่งแล้วจะไม่สามารถแก้ไขได้
                </p>
                <Button
                  onClick={() => navigate(`/room/${roomId}/exam/${examId}/submit`)}
                  className="bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200 px-10 h-12 text-base font-bold"
                >
                  <Send size={18} className="mr-2" /> เริ่มทำข้อสอบ
                </Button>
              </div>
            ) : mySubmission.status === "approved" ? (
              /* Approved */
              <div className="space-y-6">
                <div className="bg-green-50 dark:bg-green-900/30 rounded-2xl border border-green-200 shadow-sm p-8 text-center">
                  <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-3" />
                  <h3 className="text-xl font-bold text-green-700 mb-1">ผลการประเมิน</h3>
                  <p className="text-green-600 text-sm">อาจารย์ตรวจและอนุมัติผลแล้ว</p>
                  <div className="mt-4 bg-white dark:bg-slate-800 rounded-xl p-4 border border-green-100 inline-block">
                    <p className="text-3xl font-bold text-green-600">{mySubmission.total_score ?? "-"}</p>
                    <p className="text-sm text-gray-400 dark:text-slate-500">/ {exam?.total_score} คะแนน</p>
                  </div>
                </div>

                {mySubmission.answers && mySubmission.answers.length > 0 && (
                  <div className="space-y-4 mt-8 text-left">
                    <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700 pb-3 mb-4">รายละเอียดคะแนนและข้อเสนอแนะ</h3>
                    {mySubmission.answers.map((ans, idx) => (
                      <div key={idx} className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden p-5">
                        <div className="flex flex-col gap-4">
                          {/* Top part: Question & Score */}
                          <div className="flex justify-between items-start gap-4 border-b border-slate-100 dark:border-slate-700 pb-4">
                            <div>
                              <span className="inline-block px-2.5 py-1 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-lg mb-2">
                                ข้อ {ans.order_index + 1}
                              </span>
                              <p className="text-slate-800 dark:text-slate-200 font-medium leading-relaxed">{ans.question_text}</p>
                            </div>
                            <div className="text-right flex-shrink-0 bg-slate-50 dark:bg-slate-900 px-3 py-2 rounded-xl border border-slate-100 dark:border-slate-700">
                              <p className="text-[10px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider mb-0.5">ได้คะแนน</p>
                              <div className="text-xl font-bold text-indigo-600">
                                {ans.teacher_score ?? ans.ai_score ?? 0} <span className="text-sm text-slate-400 dark:text-slate-500 font-normal">/ {ans.max_score}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Student Answer */}
                          <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500 font-bold mb-2">คำตอบของคุณ:</p>
                            <div className="bg-slate-50 dark:bg-slate-900 p-4 mb-3 rounded-xl border border-slate-200 dark:border-slate-700/60 text-slate-700 dark:text-slate-300 text-sm whitespace-pre-wrap leading-relaxed shadow-inner">
                              {ans.answer_text || <span className="italic text-slate-400 dark:text-slate-500">ไม่ได้ตอบข้อนี้</span>}
                            </div>
                            {/* Student Answer Images — multi support */}
                            {(ans.image_paths && ans.image_paths.length > 0) ? (
                              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-3">
                                {ans.image_paths.map((src: string, i: number) => (
                                  <img 
                                    key={i} 
                                    src={src} 
                                    alt={`ภาพแนบคำตอบ ${i+1}`} 
                                    className="w-full aspect-video object-contain rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm bg-slate-50 dark:bg-slate-900 cursor-zoom-in hover:opacity-90 transition-opacity" 
                                    onClick={() => setModalImage({ src, alt: `คำตอบข้อ ${ans.order_index + 1} (${i + 1}/${ans.image_paths.length})` })}
                                  />
                                ))}
                              </div>
                            ) : ans.image_path ? (
                              <img 
                                src={ans.image_path} 
                                alt="ภาพแนบคำตอบ" 
                                className="max-w-xs mt-3 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm bg-slate-50 dark:bg-slate-900 cursor-zoom-in hover:opacity-90 transition-opacity" 
                                onClick={() => setModalImage({ src: ans.image_path!, alt: `คำตอบข้อ ${ans.order_index + 1}` })}
                              />
                            ) : null}
                          </div>

                          {/* Feedbacks Grid */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                            {/* AI Feedback */}
                            <div className="bg-blue-50 dark:bg-blue-900/30/70 rounded-xl p-4 border border-blue-100 relative shadow-sm">
                              <p className="text-xs font-bold text-blue-600 mb-2 flex items-center gap-2">
                                ✨ AI Feedback 
                                <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full border border-blue-200/50">
                                  {ans.ai_score} pts
                                </span>
                              </p>
                              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                                {ans.ai_feedback || "ไม่มี Feedback จาก AI"}
                              </p>
                            </div>
                            {/* Teacher Feedback */}
                            {ans.teacher_comment && (
                              <div className="bg-emerald-50/70 rounded-xl p-4 border border-emerald-100 relative shadow-sm">
                                <p className="text-xs font-bold text-emerald-600 mb-2 flex items-center gap-2">
                                  👩‍🏫 ข้อเสนอแนะจากอาจารย์
                                </p>
                                <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                                  {ans.teacher_comment}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* Submitted / AI graded / Waiting teacher approval — ซ่อนคะแนนทั้งหมด */
              <div className="bg-blue-50 dark:bg-blue-900/30 rounded-2xl border border-blue-200 shadow-sm p-8 text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  {mySubmission.status === "submitted" ? (
                    <Loader2 size={28} className="text-blue-500 animate-spin" />
                  ) : (
                    <Clock size={28} className="text-blue-500" />
                  )}
                </div>
                <h3 className="text-xl font-bold text-blue-700 mb-2">
                  {mySubmission.status === "submitted"
                    ? "กำลังประมวลผล AI..."
                    : "รอการอนุมัติจากอาจารย์"}
                </h3>
                <p className="text-blue-500 text-sm leading-relaxed">
                  {mySubmission.status === "submitted"
                    ? "โปรดรอสักครู่ ระบบกำลังประเมินคำตอบ"
                    : "ส่งคำตอบเรียบร้อยแล้ว\nผลคะแนนจะแสดงเมื่ออาจารย์อนุมัติ"}
                </p>
                <div className="mt-5 inline-flex items-center gap-2 text-xs text-blue-400 bg-white dark:bg-slate-800 px-4 py-2 rounded-full border border-blue-100">
                  <CheckCircle2 size={13} className="text-blue-400" />
                  ส่งสำเร็จแล้ว — กรุณารอผลการตรวจ
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-xl">
              <div className="text-center">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Trash2 className="text-red-600" size={24} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">ยืนยันการลบข้อสอบ</h3>
                <p className="text-gray-500 dark:text-slate-400 mb-6">
                  คุณต้องการลบข้อสอบ "<strong>{exam?.title}</strong>" ใช่หรือไม่?<br />
                  <span className="text-red-500 text-sm">การกระทำนี้ไม่สามารถย้อนกลับได้</span>
                </p>
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteModal(false)}
                    className="flex-1"
                  >
                    ยกเลิก
                  </Button>
                  <Button
                    onClick={handleDeleteExam}
                    disabled={isDeleting}
                    className="flex-1 bg-red-600 hover:bg-red-700"
                  >
                    {isDeleting ? <Loader2 size={16} className="animate-spin" /> : "ลบข้อสอบ"}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>

      <ImageModal
        isOpen={!!modalImage}
        onClose={() => setModalImage(null)}
        src={modalImage?.src || ""}
        alt={modalImage?.alt}
      />
    </div>
  );
}
