import { confirmAction } from "@/components/ConfirmActionDialog";
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Info,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  EyeOff,
  Edit3,
  FileCheck,
  BarChart3,
  Users,
  Lock,
  Unlock,
  AlertCircle,
} from "lucide-react";
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
  answer_key_image_paths?: string[];
  order_index: number; image_path?: string | null; image_paths?: string[];
  hide_rubric_from_students?: boolean;
}
interface Exam {
  id: number; room_id: number; title: string; description?: string;
  total_score: number; start_date?: string; end_date?: string;
  created_at: string; questions: Question[];
  server_time?: string; submission_deadline?: string;
  is_closed?: boolean | number;
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
  const [togglingClose, setTogglingClose] = useState(false);

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

  const handleToggleClose = async () => {
    if (!exam) return;
    const willClose = !exam.is_closed;
    const confirmMessage = willClose
      ? "ต้องการปิดรับข้อสอบชุดนี้ทันทีหรือไม่? (นักเรียนจะไม่สามารถส่งคำตอบได้อีก)"
      : "ต้องการเปิดรับข้อสอบชุดนี้อีกครั้งหรือไม่? (นักเรียนจะสามารถส่งคำตอบได้ตามช่วงเวลาที่กำหนด)";
    if (!await confirmAction(confirmMessage)) return;

    setTogglingClose(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/toggle-close`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setExam((prev) => (prev ? { ...prev, is_closed: data.is_closed } : null));
        toast.success(
          data.is_closed
            ? "ปิดรับการส่งข้อสอบเรียบร้อยแล้ว"
            : "เปิดรับการส่งข้อสอบอีกครั้งเรียบร้อยแล้ว",
        );
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "ไม่สามารถเปลี่ยนสถานะการปิดรับข้อสอบได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setTogglingClose(false);
    }
  };

  const getExamStatus = () => {
    if (!exam) return null;
    if (exam.is_closed) {
      return {
        label: "ปิดรับข้อสอบแล้ว (โดยผู้สอน)",
        color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800",
      };
    }
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

    return { label: "เปิดรับคำตอบ", color: "bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300" };
  };

  const fmt = (d?: string) => d ? new Date(d).toLocaleString("th-TH", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";

  if (isLoading || isFetching || !user) return <ExamPageSkeleton singleColumn={user?.role === "teacher"} />;

  const isTeacher = user.role === "teacher";
  const beforeStart = !!exam?.start_date && clock + clockOffset < new Date(exam.start_date).getTime();
  const deadline = exam?.submission_deadline || exam?.end_date;
  const afterDeadline = !!deadline && clock + clockOffset > new Date(deadline).getTime();

  return (
    <div className="exam-detail-page min-h-screen bg-background pb-16 text-foreground transition-colors duration-200">
      <Navbar />
      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">

        {/* Back */}
        <button onClick={() => navigate(`/room/${roomId}`)} className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-emerald-800 dark:hover:text-emerald-300 transition-colors mb-6">
          <ArrowLeft size={15} /> กลับห้องเรียน
        </button>

        {isTeacher && <ExamNavigation roomId={roomId} examId={examId} />}
        {isTeacher && <div className="mb-5 flex flex-wrap gap-2 lg:hidden">
          <Button className="gap-2" onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)}><FileCheck size={16} /> ตรวจทานคะแนน</Button>
          <Button variant="outline" className="gap-2" onClick={() => navigate(`/room/${roomId}/exam/${examId}/edit`)}><Edit3 size={16} /> แก้ไขข้อสอบ</Button>
        </div>}
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_280px] gap-6 items-start">
          
          {/* Left Column: Main Content */}
          <div className="min-w-0 space-y-6">
            
            {/* Exam Header */}
            <div className="rounded-xl border border-border bg-card p-5 sm:p-7">
               <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-2">
                <div className="flex-1">
                  {exam?.description && <div className="mb-4"><p className="mb-1 text-xs font-medium text-muted-foreground">คำชี้แจง</p><p className="whitespace-pre-wrap break-words text-sm leading-7 text-foreground">{exam.description}</p></div>}
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    <h1 className="break-words text-2xl sm:text-3xl font-semibold text-foreground">{exam?.title}</h1>
                    {getExamStatus() && (
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${getExamStatus()?.color}`}>
                        {getExamStatus()?.label}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-x-6 gap-y-5 text-sm border-t border-border pt-5 mt-5">
                <div><span className="text-xs text-muted-foreground block mb-1">เริ่มรับคำตอบ</span><span className="font-medium">{exam?.start_date ? fmt(exam.start_date) : "ไม่จำกัดเวลาเริ่ม"}</span></div>
                <div><span className="text-xs text-muted-foreground block mb-1">สิ้นสุดการรับคำตอบ</span><span className="font-medium">{exam?.end_date ? fmt(exam.end_date) : "ไม่กำหนดวันสิ้นสุด"}</span></div>
                <div><span className="text-xs text-muted-foreground block mb-1">จำนวนคำถาม</span><span className="font-medium">{exam?.questions.length} ข้อ</span></div>
                <div><span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">คะแนนรวม</span><span className="font-medium text-emerald-800 dark:text-emerald-300">{exam?.total_score} คะแนน</span></div>
              </div>
            </div>

            {/* Questions List */}
            <div className="space-y-4">
              <div className="px-2">
                <h2 className="text-lg font-semibold text-foreground">คำถาม <span className="ml-2 text-sm font-normal text-muted-foreground">{exam?.questions.length} ข้อ</span></h2>
              </div>
              
              <div className="space-y-4">
                {exam?.questions.map((q, idx) => (
                  <div key={q.id} className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 px-6 py-6 space-y-4 hover:border-emerald-200 dark:hover:border-emerald-900/60 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex gap-4 flex-1">
                        <span className="text-sm font-medium text-gray-400 dark:text-gray-500 pt-0.5 shrink-0">{String(idx + 1).padStart(2, "0")}.</span>
                        <p className="min-w-0 whitespace-pre-wrap break-words text-base text-gray-800 dark:text-gray-200 leading-relaxed">{q.text}</p>
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
                    {(isTeacher ? Boolean(q.answer_key || q.answer_key_image_paths?.length || q.rubrics?.length) : Boolean(!q.hide_rubric_from_students && q.rubrics?.length)) && (
                      <div className="pl-8 pt-2 border-t border-gray-50 dark:border-gray-800 mt-4">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <button type="button" aria-expanded={expandedId === q.id} onClick={() => setExpandedId(expandedId === q.id ? null : q.id)} className="inline-flex min-h-10 items-center gap-2 border-0 bg-transparent py-2 text-sm font-medium text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                            {expandedId === q.id
                              ? (isTeacher ? "ซ่อนแนวคำตอบและเกณฑ์" : "ซ่อนเกณฑ์การให้คะแนน")
                              : (isTeacher ? "ดูแนวคำตอบและเกณฑ์" : "ดูเกณฑ์การให้คะแนน")}
                            {expandedId === q.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </button>
                          {isTeacher && q.hide_rubric_from_students && (
                            <span className="text-[11px] text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 px-2 py-0.5 rounded-full inline-flex items-center gap-1 font-medium">
                              <EyeOff size={11} />
                              ซ่อนเกณฑ์ไม่ให้นักเรียนเห็น
                            </span>
                          )}
                        </div>
                        {expandedId === q.id && (
                          <div className="mt-4 space-y-5 text-sm animate-in fade-in slide-in-from-top-2">
                            {isTeacher && q.answer_key && (
                              <div>
                                <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">แนวคำตอบ</p>
                                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-100 dark:border-gray-700">{q.answer_key}</p>
                              </div>
                            )}
                            {isTeacher && q.answer_key_image_paths && q.answer_key_image_paths.length > 0 && (
                              <div>
                                <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">ภาพแนวคำตอบ</p>
                                <div className="flex flex-wrap gap-2">
                                  {q.answer_key_image_paths.map((src, imageIndex) => (
                                    <img key={imageIndex} src={src} alt={`ภาพแนวคำตอบ ${imageIndex + 1}`} className="h-32 w-auto rounded-xl border border-gray-200 dark:border-gray-700 cursor-zoom-in" onClick={() => setModalImage({ src, alt: `ภาพแนวคำตอบ ${imageIndex + 1}` })} />
                                  ))}
                                </div>
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
                      <div className="text-sm text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700 rounded-xl p-4 leading-relaxed font-mono whitespace-pre-wrap">
                        {ans.answer_text || <span className="italic text-gray-400 dark:text-gray-500">ไม่ได้ระบุคำตอบข้อความ</span>}
                      </div>
                    </div>

                    {ans.image_paths && ans.image_paths.length > 0 && (
                      <div className="space-y-2 pt-1">
                        <p className="text-xs text-gray-500 dark:text-gray-400">ภาพคำตอบที่แนบ</p>
                        <div className="flex flex-wrap gap-3">
                          {ans.image_paths.map((img: string, imgIdx: number) => (
                            <img
                              key={imgIdx}
                              src={img}
                              alt={`ภาพคำตอบข้อ ${idx + 1} รูปที่ ${imgIdx + 1}`}
                              className="w-24 h-24 object-cover rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer hover:opacity-80 transition shadow-sm"
                              onClick={() => setModalImage({ src: img, alt: `ภาพคำตอบข้อ ${idx + 1}` })}
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    {ans.ai_feedback && (
                      <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl p-4 mt-2">
                        <p className="text-xs text-emerald-800 dark:text-emerald-300 font-medium mb-2">คำแนะนำจาก AI</p>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">{ans.ai_feedback}</p>
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

            {/* Student Submitted Answers (Pending Teacher Approval - Read Only) */}
            {!isTeacher && mySubmission?.status && mySubmission.status !== "missing" && mySubmission.status !== "approved" && mySubmission.answers && (
              <div id="submitted-answers" className="space-y-6 pt-8 mt-4 border-t border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between px-2 flex-wrap gap-2">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">คำตอบที่คุณส่ง</h2>
                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-0.5">
                      ⏳ กำลังรออาจารย์ตรวจทานและอนุมัติคะแนน (โหมดอ่านอย่างเดียว ไม่สามารถแก้ไขได้)
                    </p>
                  </div>
                  <span className="text-xs bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800 px-3 py-1 rounded-full font-medium">
                    รออนุมัติคะแนน
                  </span>
                </div>

                {mySubmission.answers.map((ans, idx) => (
                  <div key={idx} className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                    <div className="flex items-start justify-between gap-4 border-b border-gray-100 dark:border-gray-800 pb-4">
                      <p className="text-base text-gray-800 dark:text-gray-200 flex-1 leading-relaxed">
                        <span className="text-emerald-700 dark:text-emerald-300 font-semibold mr-2">{idx + 1}.</span>
                        {ans.question_text || "(ดูโจทย์จากรูปภาพแนบ)"}
                      </p>
                      <span className="shrink-0 text-xs text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md">
                        คะแนนเต็ม {ans.max_score} คะแนน
                      </span>
                    </div>

                    <div className="space-y-2">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400">คำตอบที่บันทึกไว้:</p>
                      <div className="text-sm text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700 rounded-xl p-4 leading-relaxed font-mono whitespace-pre-wrap">
                        {ans.answer_text ? ans.answer_text : <span className="italic text-gray-400 dark:text-gray-500">ไม่ได้พิมพ์คำตอบข้อความ</span>}
                      </div>
                    </div>

                    {ans.image_paths && ans.image_paths.length > 0 && (
                      <div className="space-y-2 pt-2">
                        <p className="text-xs font-medium text-gray-600 dark:text-gray-400">ภาพลายมือคำตอบที่แนบ ({ans.image_paths.length} รูป):</p>
                        <div className="flex flex-wrap gap-3">
                          {ans.image_paths.map((img: string, imgIdx: number) => (
                            <img
                              key={imgIdx}
                              src={img}
                              alt={`ภาพคำตอบข้อ ${idx + 1} รูปที่ ${imgIdx + 1}`}
                              className="w-24 h-24 object-cover rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer hover:opacity-80 transition shadow-sm"
                              onClick={() => setModalImage({ src: img, alt: `ภาพคำตอบข้อ ${idx + 1}` })}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: Actions (Sticky) */}
          {isTeacher ? (
            <aside className="space-y-4 lg:sticky lg:top-20">
              <section className="rounded-xl border border-border bg-card p-5">
                <h2 className="text-base font-semibold">งานของผู้สอน</h2>
                <p className="mt-1 mb-4 text-sm leading-6 text-muted-foreground">ตรวจคำตอบและยืนยันคะแนนก่อนเผยแพร่ให้ผู้เรียน</p>
                <Button onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)} className="w-full gap-2">
                  <FileCheck size={17} /> ตรวจทานและอนุมัติคะแนน
                </Button>
                <div className="mt-4 space-y-1 border-t border-border pt-3">
                  <Button variant="ghost" onClick={() => navigate(`/room/${roomId}/exam/${examId}/edit`)} className="w-full justify-start gap-3"><Edit3 size={17} /> แก้ไขข้อสอบ</Button>
                  <Button variant="ghost" onClick={() => navigate(`/room/${roomId}/exam/${examId}/scoreboard`)} className="w-full justify-start gap-3"><Users size={17} /> ตารางคะแนน</Button>
                  <Button variant="ghost" onClick={() => navigate(`/room/${roomId}/exam/${examId}/analytics`)} className="w-full justify-start gap-3"><BarChart3 size={17} /> สถิติการสอบ</Button>
                </div>
              </section>
              <section className="rounded-xl border border-border bg-card p-5">
                <h2 className="text-sm font-semibold">การรับคำตอบ</h2>
                <p className="mt-2 mb-4 text-sm leading-6 text-muted-foreground">{exam?.is_closed ? "ผู้เรียนไม่สามารถส่งคำตอบได้จนกว่าจะเปิดรับอีกครั้ง" : "หากปิดรับทันที ผู้เรียนจะไม่สามารถส่งคำตอบเพิ่มได้"}</p>
                <Button variant="outline" onClick={handleToggleClose} disabled={togglingClose}
                  className={`w-full gap-2 ${exam?.is_closed ? "text-primary border-primary/30" : "text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:border-red-900 dark:hover:bg-red-950/40"}`}>
                  {exam?.is_closed ? <Unlock size={16} /> : <Lock size={16} />}
                  {togglingClose ? "กำลังบันทึก…" : exam?.is_closed ? "เปิดรับคำตอบอีกครั้ง" : "ปิดรับคำตอบทันที"}
                </Button>
              </section>
            </aside>
          ) : (
          <div className="space-y-6 lg:sticky lg:top-24">
            
            {/* Action Panel */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <>
                  {Boolean(exam?.is_closed) && (
                    <div className="p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 rounded-xl text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
                      <AlertCircle size={16} className="shrink-0 text-red-600" />
                      <span>อาจารย์ผู้สอนได้ทำการปิดรับการส่งคำตอบสำหรับแบบทดสอบนี้แล้ว</span>
                    </div>
                  )}
                  {(!mySubmission || mySubmission.status === "missing") && (
                    <Button
                      disabled={!submissionChecked || beforeStart || afterDeadline || Boolean(exam?.is_closed)}
                      onClick={() => navigate(`/room/${roomId}/exam/${examId}/submit`)}
                      className="w-full h-12 bg-emerald-800 hover:bg-emerald-900 dark:bg-emerald-300 dark:hover:bg-emerald-200 dark:text-emerald-950 text-white text-base font-medium rounded-xl transition-all shadow-sm disabled:opacity-60"
                    >
                      {exam?.is_closed
                        ? "ปิดรับคำตอบแล้ว (โดยผู้สอน)"
                        : beforeStart
                        ? "ยังไม่ถึงเวลาเริ่มสอบ"
                        : afterDeadline
                        ? "ปิดรับคำตอบแล้ว"
                        : !submissionChecked
                        ? "กำลังตรวจสอบสถานะการส่ง"
                        : "เริ่มต้นทำข้อสอบ"}
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
                    <div className="flex flex-col items-center gap-4 text-sm justify-center py-8 px-4 bg-green-50/50 dark:bg-green-900/10 rounded-2xl border border-green-100/50 dark:border-green-900/30">
                      <div className="w-14 h-14 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center text-green-600 dark:text-green-400 mb-1">
                        <CheckCircle2 size={36} />
                      </div>
                      <div className="text-center space-y-1.5">
                        <p className="font-bold text-green-900 dark:text-green-200 text-lg">
                          ส่งคำตอบสำเร็จ!
                        </p>
                        <p className="text-[13px] text-green-700 dark:text-green-400/80 leading-relaxed max-w-[280px] mx-auto">
                          ระบบได้รับคำตอบของคุณเรียบร้อยแล้ว <br/>
                          โปรดรอการตรวจทานและอนุมัติคะแนนจากอาจารย์
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => document.getElementById("submitted-answers")?.scrollIntoView({ behavior: "smooth" })}
                        className="w-full mt-2 text-xs bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-slate-50"
                      >
                        ดูคำตอบที่คุณส่ง ↓
                      </Button>
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
