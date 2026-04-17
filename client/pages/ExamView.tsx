import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Trophy, FileText, ChevronDown, ChevronUp,
  CheckCircle2, Loader2, Calendar, Clock, ClipboardCheck,
  Send, AlertCircle, BarChart3, Pencil, Trash2
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

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
  const [mySubmission, setMySubmission] = useState<{ status: string; total_score?: number } | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

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

    // Fetch student's own submission status
    if (user?.role === "student") {
      fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => r.json())
        .then((d) => setMySubmission(d))
        .catch(() => { });
    }
  }, [token, roomId, examId]);

  if (isLoading || isFetching || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
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

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* Back Button + Teacher Action */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate(`/room/${roomId}`)}
            className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors text-sm font-medium"
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
                className="gap-2 text-red-600 border-red-200 hover:bg-red-50"
              >
                <Trash2 size={16} /> ลบ
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
          <h2 className="text-xl font-bold text-slate-800">รายการคำถาม</h2>

          {exam?.questions.length === 0 && (
            <div className="bg-white rounded-2xl border border-slate-100 p-12 text-center shadow-sm">
              <FileText className="h-10 w-10 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-500">ยังไม่มีคำถามในข้อสอบนี้</p>
            </div>
          )}

          {exam?.questions.map((q, index) => (
            <div
              key={q.id}
              className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden hover:border-indigo-200 transition-colors"
            >
              {/* Question Header */}
              <div className="p-5 flex gap-4 items-start">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 font-bold text-sm flex items-center justify-center flex-shrink-0">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="text-slate-800 font-medium leading-relaxed">{q.text}</p>
                  {/* Question images attached by teacher — gallery */}
                  {(q.image_paths && q.image_paths.length > 0) ? (
                    <div className="mt-3 grid grid-cols-2 gap-2">
                      {q.image_paths.map((src, i) => (
                        <img
                          key={i}
                          src={src}
                          alt={`รูปโจทย์ข้อ ${index + 1} รูปที่ ${i + 1}`}
                          className="w-full rounded-xl border border-slate-200 shadow-sm object-contain bg-gray-50 max-h-56"
                        />
                      ))}
                    </div>
                  ) : q.image_path ? (
                    <div className="mt-3">
                      <img
                        src={q.image_path}
                        alt={`รูปโจทย์ข้อ ${index + 1}`}
                        className="max-h-72 w-auto rounded-xl border border-slate-200 shadow-sm object-contain bg-gray-50"
                      />
                    </div>
                  ) : null}
                </div>
                <span className="flex-shrink-0 text-sm font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
                  {q.score} คะแนน
                </span>
              </div>

              {/* Teacher sees answer key toggle */}
              {isTeacher && (q.answer_key || (q.rubrics && q.rubrics.length > 0)) && (
                <div className="border-t border-slate-50">
                  <button
                    onClick={() => setExpandedId(expandedId === q.id ? null : q.id)}
                    className="w-full flex items-center justify-center gap-2 py-2.5 text-sm text-slate-400 hover:text-indigo-600 hover:bg-indigo-50/50 transition-colors font-medium"
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
                        <div className="px-5 pb-5 pt-2 space-y-4 bg-slate-50/50">
                          {q.answer_key && (
                            <div>
                              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                <CheckCircle2 size={13} className="text-emerald-500" /> แนวคำตอบ
                              </p>
                              <p className="text-slate-700 bg-white p-4 rounded-xl border border-slate-200 text-sm leading-relaxed">
                                {q.answer_key}
                              </p>
                            </div>
                          )}

                          {q.rubrics && q.rubrics.length > 0 && (
                            <div>
                              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">เกณฑ์การให้คะแนน</p>
                              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                                {q.rubrics.map((r, i) => (
                                  <div key={i} className={`flex items-center justify-between px-4 py-3 text-sm ${i !== 0 ? "border-t border-slate-50" : ""}`}>
                                    <div>
                                      <p className="font-semibold text-slate-700">{r.name}</p>
                                      {r.description && <p className="text-slate-500 text-xs mt-0.5">{r.description}</p>}
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
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 text-center">
                <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send size={28} className="text-indigo-500" />
                </div>
                <h3 className="text-xl font-bold text-slate-700 mb-2">พร้อมทำข้อสอบ?</h3>
                <p className="text-slate-500 text-sm mb-6 leading-relaxed">
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
              <div className="bg-green-50 rounded-2xl border border-green-200 shadow-sm p-8 text-center">
                <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-3" />
                <h3 className="text-xl font-bold text-green-700 mb-1">อนุมัติแล้ว ✅</h3>
                <p className="text-green-600 text-sm">อาจารย์ตรวจและอนุมัติผลแล้ว</p>
                <div className="mt-4 bg-white rounded-xl p-4 border border-green-100 inline-block">
                  <p className="text-3xl font-bold text-green-600">{mySubmission.total_score ?? "-"}</p>
                  <p className="text-sm text-gray-400">/ {exam?.total_score} คะแนน</p>
                </div>
              </div>
            ) : (
              /* Submitted / AI graded / Waiting teacher approval — ซ่อนคะแนนทั้งหมด */
              <div className="bg-blue-50 rounded-2xl border border-blue-200 shadow-sm p-8 text-center">
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
                <div className="mt-5 inline-flex items-center gap-2 text-xs text-blue-400 bg-white px-4 py-2 rounded-full border border-blue-100">
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
            <div className="bg-white rounded-2xl p-6 max-w-sm w-full mx-4 shadow-xl">
              <div className="text-center">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Trash2 className="text-red-600" size={24} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">ยืนยันการลบข้อสอบ</h3>
                <p className="text-gray-500 mb-6">
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
    </div>
  );
}
