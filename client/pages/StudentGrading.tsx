import { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import {
  ChevronLeft, ChevronRight, CheckCircle2, AlertTriangle,
  MessageSquare, BookOpen, AlertCircle, X, Loader2, Save, ArrowLeft, Image as ImageIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import ImageModal from "@/components/ImageModal";

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

export default function StudentGrading() {
  const navigate = useNavigate();
  const { roomId, examId, studentId } = useParams();
  const { user, token, isLoading } = useAuth();

  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [isApproving, setIsApproving] = useState(false);
  const [studentInfo, setStudentInfo] = useState<StudentInfo | null>(null);
  const [answers, setAnswers] = useState<AnswerData[]>([]);
  const [submissionStatus, setSubmissionStatus] = useState<string>("ready");
  const [scores, setScores] = useState<Record<number, number>>({});
  const [comments, setComments] = useState<Record<number, string>>({});
  const [modalImage, setModalImage] = useState<{ src: string; alt: string } | null>(null);
  const [studentsList, setStudentsList] = useState<StudentListItem[]>([]);
  const [currentStudentIndex, setCurrentStudentIndex] = useState(0);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "teacher") navigate("/home");
  }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || !roomId || !examId) return;
    fetch(`/api/rooms/${roomId}/exams/${examId}/submissions`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data: StudentListItem[]) => {
        const withSubmissions = data.filter((s) => s.status !== "missing");
        setStudentsList(withSubmissions);
        const idx = withSubmissions.findIndex((s) => String(s.student_id) === studentId);
        setCurrentStudentIndex(idx >= 0 ? idx : 0);
      })
      .catch(() => {});
  }, [token, roomId, examId, studentId]);

  const fetchSubmission = useCallback(async (sid: string) => {
    if (!token || !roomId || !examId) return;
    setIsFetching(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/${sid}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) {
        toast.error("ยังไม่มีข้อมูลการส่งงานของนักเรียนคนนี้");
        setIsFetching(false);
        return;
      }
      const data = await res.json();
      setStudentInfo(data.student);
      setAnswers(data.answers || []);
      setSubmissionStatus(data.submission?.status ?? "ready");

      const scoreMap: Record<number, number> = {};
      const commentMap: Record<number, string> = {};
      for (const a of data.answers || []) {
        scoreMap[a.question_id] = a.teacher_score !== null && a.teacher_score !== undefined ? a.teacher_score : a.ai_score;
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
    navigate(`/room/${roomId}/exam/${examId}/grading/${target.student_id}`, { replace: true });
  };

  const confirmApprove = async () => {
    if (!token) return;
    setIsApproving(true);
    setIsConfirmOpen(false);

    const teacherScores: Record<string, number> = {};
    const teacherComments: Record<string, string> = {};
    for (const a of answers) {
      teacherScores[String(a.question_id)] = scores[a.question_id] ?? a.ai_score;
      if (comments[a.question_id]) teacherComments[String(a.question_id)] = comments[a.question_id];
    }

    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/${studentId}/approve`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ teacher_scores: teacherScores, teacher_comments: teacherComments }),
      });

      if (res.ok) {
        toast.success(`อนุมัติผลของ ${studentInfo?.name} สำเร็จ`);
        setSubmissionStatus("approved");
        setStudentsList((prev) => prev.map((s) => String(s.student_id) === studentId ? { ...s, status: "approved" } : s));

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

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-white dark:bg-slate-950">
        <Loader2 className="animate-spin text-slate-400 h-10 w-10" />
      </div>
    );
  }

  const isApproved = submissionStatus === "approved";
  const currentStudentName = studentInfo?.name ?? "...";

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <Navbar activeTab="allReviews" />

      {/* Unified Header & Navigator */}
      <div className="sticky top-[64px] z-40 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl border-b border-slate-100 dark:border-slate-900 px-6 py-4">
         <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-6">
               <button onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)} className="p-2 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-full transition-all">
                  <ArrowLeft size={20} />
               </button>
               <div className="h-8 w-px bg-slate-100 dark:bg-slate-900 hidden md:block" />
               <div>
                  <h1 className="text-xl font-black tracking-tight leading-none mb-1">{currentStudentName}</h1>
                  <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                    {studentInfo?.student_code || studentInfo?.email} • ลำดับ {currentStudentIndex + 1}/{studentsList.length}
                  </p>
               </div>
            </div>

            <div className="flex items-center gap-4">
               <div className="flex bg-slate-50 dark:bg-slate-900 rounded-full p-1">
                  <button onClick={() => navigateToStudent(currentStudentIndex - 1)} disabled={currentStudentIndex === 0} className="p-2 disabled:opacity-30 hover:bg-white dark:hover:bg-slate-800 rounded-full shadow-sm transition-all"><ChevronLeft size={18} /></button>
                  <button onClick={() => navigateToStudent(currentStudentIndex + 1)} disabled={currentStudentIndex >= studentsList.length - 1} className="p-2 disabled:opacity-30 hover:bg-white dark:hover:bg-slate-800 rounded-full shadow-sm transition-all"><ChevronRight size={18} /></button>
               </div>
               
               <Button onClick={() => setIsConfirmOpen(true)} disabled={isApproving} className={`h-11 px-8 rounded-full font-black text-xs uppercase tracking-widest shadow-xl transition-all ${isApproved ? 'bg-amber-500 hover:bg-amber-600 text-white shadow-amber-100' : 'bg-slate-900 dark:bg-white dark:text-slate-900 text-white shadow-slate-100'}`}>
                 {isApproving && <Loader2 size={12} className="animate-spin mr-2" />}
                 {isApproved ? 'บันทึกการแก้ไข' : 'อนุมัติคะแนน'}
               </Button>
            </div>
         </div>
      </div>

      <main className="max-w-4xl mx-auto px-6 py-16">
        {answers.length === 0 ? (
          <div className="text-center py-32 bg-slate-50 dark:bg-slate-900 rounded-[2.5rem]">
            <AlertCircle className="mx-auto mb-4 text-slate-300" size={48} />
            <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">ไม่พบข้อมูลคำตอบ</p>
          </div>
        ) : (
          <div className="space-y-32">
            {answers.map((a, index) => (
              <div key={a.question_id} className="group relative">
                
                {/* Question Section */}
                <div className="mb-12">
                   <div className="flex items-center gap-4 mb-6">
                      <span className="text-xs font-black text-slate-200 dark:text-slate-800">{String(index + 1).padStart(2, '0')}</span>
                      <h3 className="text-xl font-bold leading-relaxed">{a.question_text}</h3>
                   </div>

                   {/* Question Meta/Images */}
                   <div className="flex flex-wrap gap-8 ml-8">
                      {a.answer_key && (
                        <div className="max-w-md">
                           <p className="text-[10px] font-black uppercase tracking-widest text-emerald-500 mb-2">แนวคำตอบ (Key)</p>
                           <p className="text-sm text-slate-500 italic leading-relaxed">{a.answer_key}</p>
                        </div>
                      )}
                      {(a.q_image_paths || a.q_image_path) && (
                        <div className="flex gap-2">
                           {a.q_image_paths?.map((src, i) => (
                             <img key={i} src={src} className="h-20 w-auto rounded-lg grayscale hover:grayscale-0 transition-all cursor-zoom-in" onClick={() => setModalImage({ src, alt: "Question" })} />
                           ))}
                           {a.q_image_path && !a.q_image_paths && (
                             <img src={a.q_image_path} className="h-20 w-auto rounded-lg grayscale hover:grayscale-0 transition-all cursor-zoom-in" onClick={() => setModalImage({ src: a.q_image_path!, alt: "Question" })} />
                           )}
                        </div>
                      )}
                   </div>
                </div>

                {/* Student Answer & AI Feedback */}
                <div className="ml-8 space-y-8">
                   <div className="p-8 bg-slate-50 dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800">
                      <div className="flex justify-between items-start mb-6">
                         <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">คำตอบของนักศึกษา</p>
                         <div className="flex gap-2">
                            {a.image_paths?.map((src, i) => <ImageIcon key={i} size={14} className="text-slate-300" />)}
                         </div>
                      </div>
                      <p className="text-lg font-medium leading-relaxed mb-6 whitespace-pre-wrap">{a.answer_text || "ไม่ได้ระบุคำตอบ"}</p>
                      
                      {a.image_paths && a.image_paths.length > 0 && (
                        <div className="flex flex-wrap gap-3 mb-4">
                           {a.image_paths.map((src, i) => (
                             <img key={i} src={src} className="h-24 w-auto rounded-xl shadow-sm cursor-zoom-in hover:scale-105 transition-all" onClick={() => setModalImage({ src, alt: "Student Answer" })} />
                           ))}
                        </div>
                      )}
                   </div>

                   <div className="p-8 bg-indigo-50/50 dark:bg-indigo-900/10 rounded-[2.5rem] border border-indigo-100 dark:border-indigo-900/20 relative">
                      <div className="flex flex-col md:flex-row justify-between items-start gap-8">
                         <div className="flex-1 space-y-6">
                            <div className="flex items-center gap-3">
                               <div className="bg-indigo-500 text-white text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest">AI Assessment</div>
                               <span className={`text-[10px] font-black uppercase tracking-widest ${a.ai_confidence === 'low' ? 'text-rose-500' : 'text-indigo-400'}`}>
                                 Confidence: {a.ai_confidence}
                               </span>
                            </div>
                            <p className="text-sm text-indigo-700 dark:text-indigo-300 leading-relaxed italic">"{a.ai_feedback || "ไม่มี Feedback จาก AI"}"</p>
                            
                            <div className="pt-6 border-t border-indigo-100 dark:border-indigo-900/30">
                               <p className="text-[10px] font-black uppercase tracking-widest text-indigo-400 mb-4">อาจารย์ให้ความเห็นเพิ่มเติม</p>
                               <Textarea 
                                 placeholder="พิมพ์คอมเมนต์ให้นักศึกษา..."
                                 className="bg-transparent border-0 border-b-2 border-indigo-100 dark:border-indigo-900/30 rounded-none focus-visible:ring-0 focus-visible:border-indigo-500 transition-all min-h-[60px] p-0 text-sm font-medium"
                                 value={comments[a.question_id] || ""}
                                 onChange={(e) => handleCommentChange(a.question_id, e.target.value)}
                               />
                            </div>
                         </div>

                         <div className="w-full md:w-32 bg-white dark:bg-slate-900 p-6 rounded-[2rem] shadow-xl shadow-indigo-100 dark:shadow-none border border-indigo-50 dark:border-indigo-900/30 text-center">
                            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2">คะแนน</p>
                            <Input 
                              type="number"
                              className="text-3xl font-black text-center h-16 border-0 focus-visible:ring-0 p-0"
                              value={scores[a.question_id] ?? a.ai_score}
                              onChange={(e) => handleScoreChange(a.question_id, e.target.value)}
                              max={a.max_score}
                            />
                            <p className="text-xs font-bold text-slate-300 mt-2">/ {a.max_score}</p>
                         </div>
                      </div>
                   </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Confirmation Modal */}
      {isConfirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
           <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-10 max-w-sm w-full mx-6 shadow-2xl animate-in zoom-in-95 duration-200">
              <h3 className="text-2xl font-black tracking-tight mb-4">{isApproved ? 'ยืนยันการแก้ไข?' : 'ยืนยันการอนุมัติ?'}</h3>
              <p className="text-sm text-slate-500 leading-relaxed mb-8">คุณต้องการบันทึกผลการตรวจของ <span className="text-slate-900 dark:text-white font-bold">{currentStudentName}</span> ใช่หรือไม่?</p>
              <div className="flex gap-3">
                 <Button variant="ghost" onClick={() => setIsConfirmOpen(false)} className="flex-1 h-12 rounded-full font-black text-xs uppercase tracking-widest">ยกเลิก</Button>
                 <Button onClick={confirmApprove} className="flex-1 h-12 bg-slate-900 dark:bg-white dark:text-slate-900 text-white rounded-full font-black text-xs uppercase tracking-widest">ตกลง</Button>
              </div>
           </div>
        </div>
      )}

      <ImageModal isOpen={!!modalImage} onClose={() => setModalImage(null)} src={modalImage?.src || ""} alt={modalImage?.alt} />
    </div>
  );
}