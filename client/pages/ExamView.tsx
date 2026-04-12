import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Trophy, FileText, ChevronDown, ChevronUp,
  CheckCircle2, Loader2, Calendar, Clock
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";

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

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* Back Button */}
        <button
          onClick={() => navigate(`/room/${roomId}`)}
          className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors text-sm font-medium"
        >
          <ArrowLeft size={18} /> กลับหน้าห้อง
        </button>

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

        {/* Student: placeholder for future upload */}
        {!isTeacher && (
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0, transition: { delay: 0.2 } }}
            className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 text-center"
          >
            <Trophy className="h-10 w-10 text-amber-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-700 mb-1">ส่งคำตอบ</h3>
            <p className="text-slate-500 text-sm">ฟีเจอร์การส่งคำตอบกำลังจะมาเร็วๆ นี้</p>
          </motion.div>
        )}

      </main>
    </div>
  );
}