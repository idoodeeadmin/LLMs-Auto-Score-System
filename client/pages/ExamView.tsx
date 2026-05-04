import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Loader2, Info, ChevronDown, ChevronUp } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import ImageModal from "@/components/ImageModal";

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
}

export default function ExamView() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();
  const [exam, setExam] = useState<Exam | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [mySubmission, setMySubmission] = useState<{ status: string; total_score?: number; answers?: any[] } | null>(null);
  const [showExtension, setShowExtension] = useState(false);
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
      .then(setExam)
      .catch(() => { toast.error("ไม่พบข้อสอบ"); navigate(`/room/${roomId}`); })
      .finally(() => setIsFetching(false));

    if (user?.role === "student") {
      const check = async () => {
        try {
          const r = await fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/me`, { headers: { Authorization: `Bearer ${token}` } });
          if (r.ok) setMySubmission(await r.json());
        } catch { /* ignore */ }
      };
      check();
      const id = setInterval(check, 5000);
      return () => clearInterval(id);
    }
  }, [token, roomId, examId, user?.role, navigate]);

  const handleGrantExtension = async () => {
    if (!token || extMinutes <= 0) return;
    setIsGranting(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/extensions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: extStudentId !== "" ? extStudentId : null, extra_minutes: extMinutes, note: extNote || null }),
      });
      if (res.ok) { toast.success("ขยายเวลาสำเร็จ!"); setExtStudentId(""); setExtNote(""); setExtMinutes(15); }
      else toast.error((await res.json()).detail || "ไม่สามารถขยายเวลา");
    } catch { toast.error("เกิดข้อผิดพลาด"); }
    finally { setIsGranting(false); }
  };

  const fmt = (d?: string) => d ? new Date(d).toLocaleString("th-TH", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";

  if (isLoading || isFetching || !user) return <div className="flex h-screen items-center justify-center dark:bg-gray-950"><Loader2 className="animate-spin text-blue-500 h-8 w-8" /></div>;

  const isTeacher = user.role === "teacher";

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 pb-16 transition-colors duration-200">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">

        {/* Back */}
        <button onClick={() => navigate(`/room/${roomId}`)} className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors mb-6">
          <ArrowLeft size={15} /> กลับห้องเรียน
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          {/* Left Column: Main Content */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Exam Header */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-8 transition-colors duration-200">
              <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-2">
                <div className="flex-1">
                  <h1 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">{exam?.title}</h1>
                  {exam?.description && <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{exam.description}</p>}
                </div>
                {isTeacher && (
                  <Button variant="outline" onClick={() => navigate(`/room/${roomId}/exam/${examId}/analytics`)} className="shrink-0 h-10 text-sm font-medium border-gray-200 dark:border-gray-700 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-700 dark:hover:text-blue-400 hover:border-blue-200 dark:hover:border-blue-800 transition-all text-gray-700 dark:text-gray-300 w-full sm:w-auto">
                    ดูสถิติการสอบ
                  </Button>
                )}
              </div>
              <div className="flex flex-wrap gap-8 text-sm border-t border-gray-100 dark:border-gray-800 pt-5 mt-2">
                <div><span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">เริ่มสอบ</span><span className="font-medium text-gray-800 dark:text-gray-200">{fmt(exam?.start_date)}</span></div>
                <div><span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">สิ้นสุด</span><span className="font-medium text-gray-800 dark:text-gray-200">{fmt(exam?.end_date)}</span></div>
                <div><span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">คะแนนรวม</span><span className="font-medium text-blue-600 dark:text-blue-400">{exam?.total_score} คะแนน</span></div>
              </div>
            </div>

            {/* Questions List */}
            <div className="space-y-4">
              <div className="px-2">
                <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300">คำถามทั้งหมด ({exam?.questions.length} ข้อ)</h2>
              </div>
              
              <div className="space-y-4">
                {exam?.questions.map((q, idx) => (
                  <div key={q.id} className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 px-6 py-6 space-y-4 hover:border-blue-100 dark:hover:border-blue-900/50 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex gap-4 flex-1">
                        <span className="text-sm font-medium text-gray-400 dark:text-gray-500 pt-0.5 shrink-0">{String(idx + 1).padStart(2, "0")}.</span>
                        <p className="text-base text-gray-800 dark:text-gray-200 leading-relaxed">{q.text}</p>
                      </div>
                      <span className="shrink-0 text-xs font-medium text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2.5 py-1 rounded-md border border-blue-100 dark:border-blue-800/50">{q.score} คะแนน</span>
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

                    {/* Teacher: answer key toggle */}
                    {isTeacher && (q.answer_key || (q.rubrics && q.rubrics.length > 0)) && (
                      <div className="pl-8 pt-2 border-t border-gray-50 dark:border-gray-800 mt-4">
                        <button onClick={() => setExpandedId(expandedId === q.id ? null : q.id)} className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium transition-colors flex items-center gap-1.5">
                          {expandedId === q.id ? "ซ่อนเฉลยและเกณฑ์ ▲" : "แสดงเฉลยและเกณฑ์ ▼"}
                        </button>
                        {expandedId === q.id && (
                          <div className="mt-4 space-y-5 text-sm animate-in fade-in slide-in-from-top-2">
                            {q.answer_key && (
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
                                      <span className="text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-1 rounded-md shrink-0 border border-blue-100 dark:border-blue-800/50 font-medium">+{r.score}</span>
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
                      <p className="text-base text-gray-800 dark:text-gray-200 flex-1 leading-relaxed"><span className="text-blue-500 dark:text-blue-400 font-medium mr-2">{idx + 1}.</span> {ans.question_text}</p>
                      <div className="text-right shrink-0">
                        <span className="text-2xl font-semibold text-blue-600 dark:text-blue-400">{ans.teacher_score ?? ans.ai_score ?? 0}</span>
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
                      <div className="bg-blue-50/50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-900/50 rounded-xl p-4 mt-2">
                        <p className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-2">คำแนะนำจาก AI</p>
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
          <div className="space-y-6 lg:sticky lg:top-24">
            
            {/* Action Panel */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 space-y-4">
              {!isTeacher ? (
                <>
                  {(!mySubmission || mySubmission.status === "missing") && (
                    <Button onClick={() => navigate(`/room/${roomId}/exam/${examId}/submit`)} className="w-full h-12 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-500 text-white text-base font-medium rounded-xl transition-all shadow-sm">
                      เริ่มต้นทำข้อสอบ
                    </Button>
                  )}
                  {mySubmission?.status === "approved" && (
                    <div className="text-center py-6 border border-blue-100 dark:border-blue-900/50 bg-blue-50/50 dark:bg-blue-900/20 rounded-xl">
                      <p className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-2">คะแนนที่ได้</p>
                      <p className="text-4xl font-bold text-blue-600 dark:text-blue-400">{mySubmission.total_score}<span className="text-lg text-blue-400 dark:text-blue-500/70 ml-1">/ {exam?.total_score}</span></p>
                      <button onClick={() => document.getElementById("feedback")?.scrollIntoView({ behavior: "smooth" })} className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 mt-4 block mx-auto transition-colors">ดูผลคะแนนรายข้อ ↓</button>
                    </div>
                  )}
                  {mySubmission?.status && mySubmission.status !== "missing" && mySubmission.status !== "approved" && (
                    <div className="flex flex-col items-center gap-3 text-sm text-gray-600 dark:text-gray-400 justify-center py-6 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-700">
                      <Loader2 className="animate-spin text-blue-500" size={24} />
                      <span className="text-center px-4">
                        {mySubmission.status === "submitted" ? "กำลังประมวลผลคำตอบ..." : "รอการตรวจสอบและอนุมัติ"}
                      </span>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex flex-col gap-3">
                  <Button onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)} className="w-full h-12 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-500 text-white text-sm font-medium rounded-xl transition-all shadow-sm">
                    ตรวจงาน
                  </Button>
                </div>
              )}
            </div>

            {/* Teacher: Time Extension */}
            {isTeacher && (
              <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200">ขยายเวลาสอบ</h3>
                <div className="space-y-3">
                  <input type="number" placeholder="รหัสนักศึกษา (ว่าง = ทุกคน)" value={extStudentId} onChange={e => setExtStudentId(e.target.value ? parseInt(e.target.value) : "")} className="w-full h-10 px-3 text-sm border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-400 dark:focus:ring-blue-500" />
                  <div className="flex items-center gap-2">
                    <input type="number" value={extMinutes} onChange={e => setExtMinutes(parseInt(e.target.value) || 1)} className="h-10 px-3 text-sm border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-white rounded-xl w-full focus:outline-none focus:ring-1 focus:ring-blue-400 dark:focus:ring-blue-500" />
                    <span className="text-sm text-gray-500 dark:text-gray-400 shrink-0 w-10">นาที</span>
                  </div>
                  <input type="text" placeholder="หมายเหตุ (ไม่บังคับ)" value={extNote} onChange={e => setExtNote(e.target.value)} className="w-full h-10 px-3 text-sm border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-950 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-400 dark:focus:ring-blue-500" />
                  <Button onClick={handleGrantExtension} disabled={isGranting} className="w-full h-10 text-sm font-medium rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300">
                    {isGranting ? <Loader2 size={14} className="animate-spin mr-2" /> : null} ยืนยันการขยายเวลา
                  </Button>
                </div>
              </div>
            )}
            
          </div>
        </div>
      </div>
      <ImageModal isOpen={!!modalImage} onClose={() => setModalImage(null)} src={modalImage?.src || ""} alt={modalImage?.alt} />
    </div>
  );
}
