import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Info, ChevronDown, ChevronUp, CheckCircle2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import ImageModal from "@/components/ImageModal";
import { ExamPageSkeleton } from "@/components/PageSkeletons";
import { ExamNavigation } from "@/components/ExamNavigation";

interface Rubric { name: string; description: string; score: number; }
interface Question {
  id: number; text: string; score: number;
  answer_key?: string; rubrics?: Rubric[];
  order_index: number; image_path?: string | null; image_paths?: string[];
}
interface Exam {
  id: number; room_id: number; title: string; description?: string;
  total_score: number; start_date?: string; end_date?: string;
  created_at: string; questions: Question[];
  server_time?: string; submission_deadline?: string;
}

export default function ExamView() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();
  const [exam, setExam] = useState<Exam | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [mySubmission, setMySubmission] = useState<{ status: string; total_score?: number; answers?: any[] } | null>(null);
  const [submissionChecked, setSubmissionChecked] = useState(false);
  const [submissionError, setSubmissionError] = useState(false);
  const [clockOffset, setClockOffset] = useState(0);
  const [clock, setClock] = useState(Date.now());
  useEffect(() => { const timer = setInterval(() => setClock(Date.now()), 1000); return () => clearInterval(timer); }, []);
  const [extStudentId, setExtStudentId] = useState<"" | number>("");
  const [extMinutes, setExtMinutes] = useState(15);
  const [extNote, setExtNote] = useState("");
  const [isGranting, setIsGranting] = useState(false);
  const [modalImage, setModalImage] = useState<{ src: string; alt: string } | null>(null);

  useEffect(() => { if (!isLoading && !user) navigate("/"); }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || !roomId || !examId) return;
    fetch(`/api/rooms/${roomId}/exams/${examId}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : Promise.reject())
      .then((data: Exam) => { setExam(data); setClockOffset(data.server_time ? new Date(data.server_time).getTime() - Date.now() : 0); })
      .catch(() => { toast.error("ไม่พบข้อสอบ"); navigate(`/room/${roomId}`); })
      .finally(() => setIsFetching(false));

    if (user?.role === "student") {
      const check = async () => {
        try {
          const r = await fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/me`, { headers: { Authorization: `Bearer ${token}` } });
          if (!r.ok) throw new Error("Unable to check submission");
          setMySubmission(await r.json()); setSubmissionChecked(true); setSubmissionError(false);
        } catch { setSubmissionError(true); }
      };
      check();
      const id = setInterval(check, 5000);
      return () => clearInterval(id);
    }
  }, [token, roomId, examId, user?.role, navigate]);
  const getExamStatus = () => {
    if (!exam) return null;
    const now = new Date(clock + clockOffset);
    const start = exam.start_date ? new Date(exam.start_date) : null;
    const end = exam.end_date ? new Date(exam.end_date) : null;

    if (end && now > end) {
      return { 
        label: "สิ้นสุดแล้ว", 
        color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
      };
    }
    
    if (start && now < start) {
      return { 
        label: "ยังไม่เริ่ม", 
        color: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
      };
    }

    if (end) {
      return { 
        label: "กำลังเปิดรับ", 
        color: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800",
      };
    }

    return null;
  };

  const fmt = (d?: string) => d ? new Date(d).toLocaleString("th-TH", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";

  if (isLoading || isFetching || !user) return <ExamPageSkeleton singleColumn={user?.role === "teacher"} />;

  const isTeacher = user.role === "teacher";
  const beforeStart = !!exam?.start_date && clock + clockOffset < new Date(exam.start_date).getTime();
  const deadline = exam?.submission_deadline || exam?.end_date;
  const afterDeadline = !!deadline && clock + clockOffset > new Date(deadline).getTime();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 pb-16 transition-colors duration-200">
      <Navbar />
      <div className={`${isTeacher ? "max-w-4xl" : "max-w-6xl"} mx-auto px-4 py-8`}>

        {/* Back */}
        <button onClick={() => navigate(`/room/${roomId}`)} className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-emerald-800 dark:hover:text-emerald-300 transition-colors mb-6">
          <ArrowLeft size={15} /> กลับห้องเรียน
        </button>

        {isTeacher && <ExamNavigation roomId={roomId} examId={examId} />}
        <div className={isTeacher ? "space-y-6" : "grid grid-cols-1 lg:grid-cols-3 gap-6 items-start"}>
          
          {/* Left Column: Main Content */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Exam Header */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-8 transition-colors duration-200">
               <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">{exam?.title}</h1>
                  </div>
                  {exam?.description && <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{exam.description}</p>}
                </div>
              </div>
              <div className="flex flex-wrap gap-8 text-sm border-t border-gray-100 dark:border-gray-800 pt-5 mt-2">
                <div><span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">เริ่มสอบ</span><span className="font-medium text-gray-800 dark:text-gray-200">{fmt(exam?.start_date)}</span></div>
                <div><span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">สิ้นสุด</span><span className="font-medium text-gray-800 dark:text-gray-200">{fmt(exam?.end_date)}</span></div>
                <div><span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">คะแนนรวม</span><span className="font-medium text-emerald-800 dark:text-emerald-300">{exam?.total_score} คะแนน</span></div>
              </div>
            </div>

            {/* Questions List */}
            <div className="space-y-4">
              <div className="px-2">
                <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300">คำถามทั้งหมด ({exam?.questions.length} ข้อ)</h2>
              </div>
              
              <div className="space-y-4">
                {exam?.questions.map((q, idx) => (
                  <div key={q.id} className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 px-6 py-6 space-y-4 hover:border-emerald-200 dark:hover:border-emerald-900/60 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex gap-4 flex-1">
                        <span className="text-sm font-medium text-gray-400 dark:text-gray-500 pt-0.5 shrink-0">{String(idx + 1).padStart(2, "0")}.</span>
                        <p className="text-base text-gray-800 dark:text-gray-200 leading-relaxed">{q.text}</p>
                      </div>
                      <span className="shrink-0 text-xs font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-700">{q.score} คะแนน</span>
                    </div>

                    {/* Images */}
                    {q.image_paths && q.image_paths.length > 0 ? (
                      <div className="flex flex-wrap gap-2 pl-14">
                        {q.image_paths.map((src, i) => (
                          <img key={i} src={src} alt="" className="h-32 w-auto rounded-xl border border-gray-200 dark:border-gray-700 cursor-zoom-in hover:opacity-90 transition-opacity shadow-sm" onClick={() => setModalImage({ src, alt: `รูป ${i+1}` })} />
                        ))}
                      </div>
                    ) : q.image_path ? (
                      <img src={q.image_path} alt="" className="h-40 w-auto rounded-xl border border-gray-200 dark:border-gray-700 pl-14 cursor-zoom-in hover:opacity-90 transition-opacity shadow-sm" onClick={() => setModalImage({ src: q.image_path!, alt: "รูปโจทย์" })} />
                    ) : null}

                    {/* Students can inspect scoring criteria; answer keys remain teacher-only. */}
                    {(isTeacher ? Boolean(q.answer_key || q.rubrics?.length) : Boolean(q.rubrics?.length)) && (
                      <div className="pl-8 pt-2 border-t border-gray-50 dark:border-gray-800 mt-4">
                        <button onClick={() => setExpandedId(expandedId === q.id ? null : q.id)} className="text-xs text-emerald-800 dark:text-emerald-300 hover:text-emerald-950 dark:hover:text-emerald-200 font-medium transition-colors flex items-center gap-1.5">
                          {expandedId === q.id
                            ? (isTeacher ? "ซ่อนเฉลยและเกณฑ์ ▲" : "ซ่อนเกณฑ์การให้คะแนน ▲")
                            : (isTeacher ? "แสดงเฉลยและเกณฑ์ ▼" : "แสดงเกณฑ์การให้คะแนน ▼")}
                        </button>
                        {expandedId === q.id && (
                          <div className="mt-4 space-y-5 text-sm animate-in fade-in slide-in-from-top-2">
                            {isTeacher && q.answer_key && (
                              <div>
                                <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">แนวคำตอบ</p>
                                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-100 dark:border-gray-700">{q.answer_key}</p>
                              </div>
                            )}
                            {q.rubrics && q.rubrics.length > 0 && (
                              <div>
                                <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">เกณฑ์การให้คะแนน</p>
                                <div className="space-y-2">
                                  {q.rubrics.map((r, i) => (
                                    <div key={i} className="flex justify-between items-start bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-100 dark:border-gray-700 gap-4">
                                      <div>
                                        <span className="text-gray-800 dark:text-gray-200 block">{r.name}</span>
                                        {r.description && <span className="text-xs text-gray-500 dark:text-gray-400 block mt-1">{r.description}</span>}
                                      </div>
                                      <span className="text-emerald-800 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-1 rounded-md shrink-0 border border-emerald-100 dark:border-emerald-900 font-medium">+{r.score}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Feedback Section (student, approved) */}
            {!isTeacher && mySubmission?.status === "approved" && mySubmission.answers && (
              <div id="feedback" className="space-y-6 pt-8 mt-4 border-t border-gray-200 dark:border-gray-800">
                <h2 className="text-lg font-medium text-gray-900 dark:text-white px-2">ผลคะแนนและคำแนะนำรายข้อ</h2>
                {mySubmission.answers.map((ans, idx) => (
                  <div key={idx} className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 space-y-5">
                    <div className="flex items-start justify-between gap-6 border-b border-gray-100 dark:border-gray-800 pb-5">
                      <p className="text-base text-gray-800 dark:text-gray-200 flex-1 leading-relaxed"><span className="text-emerald-700 dark:text-emerald-300 font-medium mr-2">{idx + 1}.</span> {ans.question_text}</p>
                      <div className="text-right shrink-0">
                        <span className="text-2xl font-semibold text-emerald-800 dark:text-emerald-300">{ans.teacher_score ?? ans.ai_score ?? 0}</span>
                        <span className="text-sm text-gray-400 dark:text-gray-500"> / {ans.max_score}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <p className="text-xs text-gray-500 dark:text-gray-400">คำตอบของคุณ</p>
                      <div className="text-sm text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700 rounded-xl p-4 leading-relaxed">
                        {ans.answer_text || <span className="italic text-gray-400 dark:text-gray-500">ไม่ได้ระบุคำตอบ</span>}
                      </div>
                    </div>

                    {ans.ai_feedback && (
                      <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl p-4 mt-2">
                        <p className="text-xs text-emerald-800 dark:text-emerald-300 font-medium mb-2">คำแนะนำจาก AI</p>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{ans.ai_feedback}</p>
                      </div>
                    )}
                    {ans.teacher_comment && (
                      <div className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-4 mt-2">
                        <p className="text-xs text-gray-600 dark:text-gray-400 font-medium mb-2">ความเห็นจากอาจารย์</p>
                        <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed">{ans.teacher_comment}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: Actions (Sticky) */}
          {!isTeacher && (
          <div className="space-y-6 lg:sticky lg:top-24">
            
            {/* Action Panel */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <>
                  {(!mySubmission || mySubmission.status === "missing") && (
                    <Button disabled={!submissionChecked || beforeStart || afterDeadline} onClick={() => navigate(`/room/${roomId}/exam/${examId}/submit`)} className="w-full h-12 bg-emerald-800 hover:bg-emerald-900 dark:bg-emerald-300 dark:hover:bg-emerald-200 dark:text-emerald-950 text-white text-base font-medium rounded-xl transition-all shadow-sm">
                      {beforeStart ? "ยังไม่ถึงเวลาเริ่มสอบ" : afterDeadline ? "ปิดรับคำตอบแล้ว" : !submissionChecked ? "กำลังตรวจสอบสถานะการส่ง" : "เริ่มต้นทำข้อสอบ"}
                    </Button>
                  )}
                  {submissionError && <p role="alert" className="text-sm text-destructive">ตรวจสอบสถานะการส่งไม่สำเร็จ ระบบจะลองใหม่อัตโนมัติ</p>}
                  {mySubmission?.status === "approved" && (
                    <div className="text-center py-6 border border-emerald-100 dark:border-emerald-900/60 bg-emerald-50/60 dark:bg-emerald-950/30 rounded-xl">
                      <p className="text-xs text-emerald-800 dark:text-emerald-300 font-medium mb-2">คะแนนที่ได้</p>
                      <p className="text-4xl font-bold text-emerald-800 dark:text-emerald-300">{mySubmission.total_score}<span className="text-lg text-emerald-600/70 dark:text-emerald-400/70 ml-1">/ {exam?.total_score}</span></p>
                      <button onClick={() => document.getElementById("feedback")?.scrollIntoView({ behavior: "smooth" })} className="text-sm text-emerald-800 dark:text-emerald-300 hover:text-emerald-950 dark:hover:text-emerald-200 mt-4 block mx-auto transition-colors">ดูผลคะแนนรายข้อ ↓</button>
                    </div>
                  )}
                  {mySubmission?.status && mySubmission.status !== "missing" && mySubmission.status !== "approved" && (
                    <div className="flex flex-col items-center gap-4 text-sm justify-center py-10 px-4 bg-green-50/50 dark:bg-green-900/10 rounded-2xl border border-green-100/50 dark:border-green-900/30">
                      <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center text-green-600 dark:text-green-400 mb-2">
                        <CheckCircle2 size={40} />
                      </div>
                      <div className="text-center space-y-2">
                        <p className="font-bold text-green-900 dark:text-green-200 text-xl">
                          ส่งคำตอบสำเร็จ!
                        </p>
                        <p className="text-[14px] text-green-700 dark:text-green-400/80 leading-relaxed max-w-[280px] mx-auto">
                          ระบบได้รับคำตอบของคุณเรียบร้อยแล้ว <br/>
                          โปรดรอการประกาศคะแนนจากอาจารย์
                        </p>
                      </div>
                    </div>
                  )}
                </>
            </div>
            
          </div>
          )}
        </div>
      </div>
      <ImageModal isOpen={!!modalImage} onClose={() => setModalImage(null)} src={modalImage?.src || ""} alt={modalImage?.alt} />
    </div>
  );
}
