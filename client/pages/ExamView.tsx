import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, FileText, ChevronDown, ChevronUp,
  CheckCircle2, Loader2, Calendar, Clock, ClipboardCheck,
  Send, AlertCircle, BarChart3, TimerReset, Users, Info, Image as ImageIcon
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
  image_paths?: string[];
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
  const [showExtensionPanel, setShowExtensionPanel] = useState(false);
  const [extStudentId, setExtStudentId] = useState<"" | number>("");
  const [extMinutes, setExtMinutes] = useState(15);
  const [extNote, setExtNote] = useState("");
  const [isGranting, setIsGranting] = useState(false);
  const [extensions, setExtensions] = useState<any[]>([]);

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

      checkStatus();
      intervalId = setInterval(checkStatus, 5000);

      return () => clearInterval(intervalId);
    }
  }, [token, roomId, examId, user?.role, navigate]);

  if (isLoading || isFetching || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-white dark:bg-slate-950">
        <Loader2 className="animate-spin text-slate-400 h-10 w-10" />
      </div>
    );
  }

  const isTeacher = user.role === "teacher";
  const formatDate = (d?: string) => d ? new Date(d).toLocaleDateString("th-TH", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "-";

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
    <div className="min-h-screen bg-white dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-100">
      <Navbar />

      <main className="max-w-6xl mx-auto px-6 py-10">

        {/* Navigation Breadcrumb */}
        <div className="mb-12">
          <button
            onClick={() => navigate(`/room/${roomId}`)}
            className="group flex items-center gap-2 text-slate-400 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors text-xs font-bold uppercase tracking-widest"
          >
            <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
            กลับหน้าห้องเรียน
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-16">

          {/* Main Content Area - Single Surface feeling */}
          <div className="flex-1 min-w-0">
            <header className="mb-16">
              <h1 className="text-4xl md:text-5xl font-black mb-6 tracking-tighter leading-tight">
                {exam?.title}
              </h1>
              {exam?.description && (
                <p className="text-slate-500 dark:text-slate-400 text-lg leading-relaxed max-w-2xl mb-8">
                  {exam.description}
                </p>
              )}

              <div className="flex flex-wrap gap-8 py-6 border-y border-slate-100 dark:border-slate-900">
                <div className="flex flex-col">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1">วันที่เริ่ม</span>
                  <span className="text-sm font-bold text-slate-700 dark:text-slate-200">{formatDate(exam?.start_date)}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1">วันที่สิ้นสุด</span>
                  <span className="text-sm font-bold text-rose-500">{formatDate(exam?.end_date)}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1">คะแนนเต็ม</span>
                  <span className="text-sm font-bold text-slate-700 dark:text-slate-200">{exam?.total_score} คะแนน</span>
                </div>
              </div>
            </header>

            <section className="space-y-16">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-xl font-black flex items-center gap-2">
                  <span className="w-1.5 h-6 bg-slate-900 dark:bg-white rounded-full" />
                  รายการคำถาม
                </h3>
              </div>

              {exam?.questions.map((q, idx) => (
                <div key={q.id} className="group pb-12 border-b border-slate-50 dark:border-slate-900 last:border-0">
                  <div className="flex gap-6">
                    <span className="text-xs font-black text-slate-300 dark:text-slate-600 pt-1">
                      {String(idx + 1).padStart(2, '0')}
                    </span>
                    <div className="flex-1 space-y-6">
                      <div className="flex justify-between items-start gap-4">
                        <p className="text-xl font-bold leading-relaxed pr-8 text-slate-900 dark:text-white">{q.text}</p>
                        <span className="text-[10px] font-black px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded uppercase tracking-widest text-slate-400 dark:text-slate-500">
                          {q.score} คะแนน
                        </span>
                      </div>

                      {/* Images */}
                      {(q.image_paths && q.image_paths.length > 0) ? (
                        <div className="flex flex-wrap gap-3">
                          {q.image_paths.map((src, i) => (
                            <img key={i} src={src} className="h-32 w-auto rounded-xl transition-all cursor-zoom-in" onClick={() => setModalImage({ src, alt: "Question" })} />
                          ))}
                        </div>
                      ) : q.image_path ? (
                        <img src={q.image_path} className="h-48 w-auto rounded-xl transition-all cursor-zoom-in" onClick={() => setModalImage({ src: q.image_path!, alt: "Question" })} />
                      ) : null}

                      {/* Teacher's Key */}
                      {isTeacher && (
                        <div className="pt-4">
                          <button onClick={() => setExpandedId(expandedId === q.id ? null : q.id)} className="text-[10px] font-black text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors uppercase tracking-[0.2em]">
                            {expandedId === q.id ? "ซ่อนรายละเอียด —" : "ดูเฉลยและเกณฑ์คะแนน +"}
                          </button>
                          <AnimatePresence>
                            {expandedId === q.id && (
                              <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-4 p-6 bg-slate-50 dark:bg-slate-900 rounded-2xl">
                                {q.answer_key && (
                                  <div className="mb-6">
                                    <p className="text-[10px] font-black uppercase text-slate-400 mb-2">แนวคำตอบ</p>
                                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{q.answer_key}</p>
                                  </div>
                                )}
                                {q.rubrics && q.rubrics.length > 0 && (
                                  <div>
                                    <p className="text-[10px] font-black uppercase text-slate-400 mb-2">เกณฑ์การให้คะแนน</p>
                                    <div className="grid gap-2">
                                      {q.rubrics.map((r, i) => (
                                        <div key={i} className="flex justify-between items-center text-xs border-b border-slate-100 dark:border-slate-800 pb-2 last:border-0">
                                          <span className="text-slate-600 dark:text-slate-400">{r.name}</span>
                                          <span className="font-bold text-slate-900 dark:text-slate-200">+{r.score}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </section>
          </div>

          {/* Sidebar Area - Subtle and Fixed when scrolling on Desktop */}
          <aside className="lg:w-80 space-y-12">

            {/* Action Section */}
            <div className="space-y-8">
              {!isTeacher ? (
                <div className="space-y-6">
                  {!mySubmission || mySubmission.status === "missing" ? (
                    <div className="p-8 bg-slate-900 dark:bg-white dark:text-slate-900 text-white rounded-[2.5rem]">
                      <h3 className="text-lg font-black mb-4">เริ่มทำข้อสอบของคุณ</h3>
                      <p className="text-xs text-slate-400 mb-8 leading-relaxed">เมื่อเริ่มแล้ว ระบบจะบันทึกความคืบหน้า โปรดตรวจสอบการเชื่อมต่อของคุณ</p>
                      <Button onClick={() => navigate(`/room/${roomId}/exam/${examId}/submit`)} className="w-full bg-white text-black dark:bg-slate-900 dark:text-white h-12 rounded-full font-black text-xs uppercase tracking-widest">
                        เข้าสู่หน้าทำข้อสอบ
                      </Button>
                    </div>
                  ) : mySubmission.status === "approved" ? (
                    <div className="text-center space-y-4">
                      <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">คะแนนที่ได้</p>
                      <div className="text-6xl font-black text-slate-900 dark:text-white">{mySubmission.total_score}<span className="text-lg text-slate-300 dark:text-slate-600 font-medium">/{exam?.total_score}</span></div>
                      <Button variant="outline" className="w-full h-11 rounded-xl text-xs font-bold border-2" onClick={() => document.getElementById('feedback')?.scrollIntoView({ behavior: 'smooth' })}>
                        ดูผลคะแนนและคำแนะนำ
                      </Button>
                    </div>
                  ) : (
                    <div className="p-8 bg-slate-50 dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 text-center">
                      <Loader2 className="animate-spin mx-auto mb-4 text-slate-300" size={24} />
                      <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                        {mySubmission.status === 'submitted' ? 'กำลังประเมินด้วย AI...' : 'รอการตรวจสอบ'}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <Button onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)} className="w-full h-12 bg-slate-900 dark:bg-white dark:text-slate-900 rounded-full font-black text-xs uppercase tracking-widest shadow-xl shadow-slate-100 dark:shadow-none">
                    ตรวจงาน
                  </Button>
                  <Button variant="outline" onClick={() => navigate(`/room/${roomId}/exam/${examId}/analytics`)} className="w-full h-12 rounded-full font-black text-xs uppercase tracking-widest border-2">
                    ดูสถิติ (Analytics)
                  </Button>
                </div>
              )}

              {/* Time Management Tool for Teacher */}
              {isTeacher && (
                <div className="pt-8 border-t border-slate-100 dark:border-slate-800 space-y-6">
                  <div className="flex justify-between items-center">
                    <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400">เครื่องมือขยายเวลา</h4>
                    <button onClick={() => setShowExtensionPanel(!showExtensionPanel)} className="text-[10px] font-black underline">
                      {showExtensionPanel ? 'ปิด' : 'จัดการ'}
                    </button>
                  </div>
                  {showExtensionPanel && (
                    <div className="space-y-3">
                      <input type="number" placeholder="รหัสนักศึกษา (ไม่บังคับ)" value={extStudentId} onChange={e => setExtStudentId(e.target.value ? parseInt(e.target.value) : "")} className="w-full h-10 px-4 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs outline-none focus:ring-1 ring-slate-200" />
                      <input type="number" value={extMinutes} onChange={e => setExtMinutes(parseInt(e.target.value) || 1)} className="w-full h-10 px-4 bg-slate-50 dark:bg-slate-800 rounded-xl text-xs font-bold outline-none" />
                      <Button onClick={handleGrantExtension} disabled={isGranting} className="w-full h-10 rounded-xl bg-slate-200 dark:bg-slate-800 dark:text-white text-black hover:bg-slate-300 text-[10px] font-black uppercase tracking-widest">ขยายเวลา</Button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Quick Insights */}
            <div className="p-8 bg-indigo-50 dark:bg-indigo-900/20 rounded-[2.5rem] border border-indigo-100 dark:border-indigo-900/30">
              <Info className="text-indigo-500 mb-4" size={18} />
              <p className="text-xs font-bold leading-relaxed text-indigo-700 dark:text-indigo-300">
                ผลคะแนนประมวลผลโดย AI เบื้องต้น แต่อาจารย์จะเป็นผู้ตรวจสอบสุดท้ายเสมอ
              </p>
            </div>
          </aside>
        </div>

        {/* Feedback Area - Also Continuous */}
        {!isTeacher && mySubmission?.status === "approved" && mySubmission.answers && (
          <div id="feedback" className="mt-32 space-y-16">
            <h2 className="text-3xl font-black tracking-tighter text-slate-900 dark:text-white">วิเคราะห์ผลคะแนนรายข้อ</h2>
            {mySubmission.answers.map((ans, idx) => (
              <div key={idx} className="pb-16 border-b border-slate-100 dark:border-slate-800 last:border-0 space-y-8">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-black text-slate-300 dark:text-slate-700">
                    {String(ans.order_index + 1).padStart(2, '0')}
                  </span>
                  <div className="text-right">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">คะแนน</p>
                    <p className="text-2xl font-black">{ans.teacher_score ?? ans.ai_score ?? 0} <span className="text-sm font-medium text-slate-300">/ {ans.max_score}</span></p>
                  </div>
                </div>

                <div className="space-y-4">
                  <p className="text-xl font-bold text-slate-900 dark:text-white">{ans.question_text}</p>
                  <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-2xl text-sm leading-relaxed border border-slate-100 dark:border-slate-800 text-slate-700 dark:text-slate-200">
                    {ans.answer_text || <span className="italic opacity-30">ไม่ได้ระบุคำตอบ</span>}
                  </div>

                  <div className="grid md:grid-cols-2 gap-6 pt-4">
                    <div className="space-y-2">
                      <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest">คำแนะนำจาก AI</p>
                      <p className="text-xs text-slate-500 italic leading-relaxed">"{ans.ai_feedback || "ไม่มีข้อมูลคำแนะนำจาก AI"}"</p>
                    </div>
                    {ans.teacher_comment && (
                      <div className="space-y-2">
                        <p className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">ความเห็นจากอาจารย์</p>
                        <p className="text-xs font-bold leading-relaxed">{ans.teacher_comment}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
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
