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
      <div className="flex h-screen items-center justify-center bg-[#F9FBFD] dark:bg-[#111111]">
        <Loader2 className="animate-spin text-blue-500 h-8 w-8" />
      </div>
    );
  }

  const isApproved = submissionStatus === "approved";
  const currentStudentName = studentInfo?.name ?? "...";

  return (
    <div className="min-h-screen bg-[#F9FBFD] dark:bg-[#111111] text-gray-900 dark:text-gray-100 font-sans">
      <Navbar activeTab="allReviews" />

      {/* Unified Header & Navigator */}
      <div className="sticky top-[64px] z-40 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800 px-4 sm:px-6 py-4 shadow-sm">
         <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
               <button onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500 dark:text-gray-400">
                  <ArrowLeft size={20} />
               </button>
               <div className="h-6 w-px bg-gray-200 dark:bg-gray-700 hidden md:block" />
               <div>
                  <h1 className="text-xl font-bold tracking-tight leading-none mb-1 text-gray-900 dark:text-white">{currentStudentName}</h1>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
                    {studentInfo?.student_code || studentInfo?.email} • ลำดับ {currentStudentIndex + 1}/{studentsList.length}
                  </p>
               </div>
            </div>

            <div className="flex items-center gap-3">
               <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1 border border-gray-200 dark:border-gray-700">
                  <button onClick={() => navigateToStudent(currentStudentIndex - 1)} disabled={currentStudentIndex === 0} className="p-1.5 disabled:opacity-30 hover:bg-white dark:hover:bg-gray-700 rounded-md transition-colors text-gray-700 dark:text-gray-300"><ChevronLeft size={18} /></button>
                  <button onClick={() => navigateToStudent(currentStudentIndex + 1)} disabled={currentStudentIndex >= studentsList.length - 1} className="p-1.5 disabled:opacity-30 hover:bg-white dark:hover:bg-gray-700 rounded-md transition-colors text-gray-700 dark:text-gray-300"><ChevronRight size={18} /></button>
               </div>
               
               <Button onClick={() => setIsConfirmOpen(true)} disabled={isApproving} className={`h-10 px-5 rounded-lg font-medium text-sm shadow-sm transition-all ${isApproved ? 'bg-amber-500 hover:bg-amber-600 text-white' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}>
                 {isApproving && <Loader2 size={16} className="animate-spin mr-2" />}
                 {isApproved ? 'บันทึกการแก้ไข' : 'อนุมัติคะแนน'}
               </Button>
            </div>
         </div>
      </div>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        {answers.length === 0 ? (
          <div className="text-center py-24 bg-white dark:bg-[#1E1E1E] rounded-xl border border-dashed border-gray-300 dark:border-gray-700 shadow-sm">
            <AlertCircle className="mx-auto mb-4 text-gray-300 dark:text-gray-600" size={48} />
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">ไม่พบข้อมูลคำตอบ</p>
          </div>
        ) : (
          <div className="space-y-16">
            {answers.map((a, index) => (
              <div key={a.question_id} className="group relative">
                
                {/* Question Section */}
                <div className="mb-6 flex gap-4">
                   <div className="shrink-0 mt-1">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 text-sm font-semibold text-gray-500 dark:text-gray-400">
                        {index + 1}
                      </span>
                   </div>
                   <div className="flex-1 space-y-4">
                      <h3 className="text-lg font-semibold leading-relaxed text-gray-900 dark:text-gray-100">{a.question_text}</h3>
                      
                      {/* Question Meta/Images */}
                      <div className="flex flex-wrap gap-6">
                         {a.answer_key && (
                           <div className="max-w-md bg-green-50/50 dark:bg-green-900/20 border-l-2 border-green-400 dark:border-green-500/50 p-3 rounded-r-lg">
                              <p className="text-xs font-semibold text-green-700 dark:text-green-400 mb-1">แนวคำตอบ (Key)</p>
                              <p className="text-sm text-gray-700 dark:text-gray-300">{a.answer_key}</p>
                           </div>
                         )}
                         {(a.q_image_paths || a.q_image_path) && (
                           <div className="flex gap-2">
                              {a.q_image_paths?.map((src, i) => (
                                <img key={i} src={src} className="h-20 w-auto rounded-lg border border-gray-200 dark:border-gray-700 object-cover cursor-zoom-in hover:opacity-90 transition-opacity" onClick={() => setModalImage({ src, alt: "Question" })} />
                              ))}
                              {a.q_image_path && !a.q_image_paths && (
                                <img src={a.q_image_path} className="h-20 w-auto rounded-lg border border-gray-200 dark:border-gray-700 object-cover cursor-zoom-in hover:opacity-90 transition-opacity" onClick={() => setModalImage({ src: a.q_image_path!, alt: "Question" })} />
                              )}
                           </div>
                         )}
                      </div>
                   </div>
                </div>

                {/* Student Answer & AI Feedback */}
                <div className="ml-12 space-y-6">
                   <div className="p-6 bg-white dark:bg-[#1A1A1A] rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
                      <div className="flex justify-between items-start mb-4">
                         <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">คำตอบของนักศึกษา</p>
                         <div className="flex gap-2">
                            {a.image_paths?.map((src, i) => <ImageIcon key={i} size={16} className="text-gray-400" />)}
                         </div>
                      </div>
                      <p className="text-base text-gray-900 dark:text-gray-100 leading-relaxed whitespace-pre-wrap">{a.answer_text || <span className="text-gray-400 italic">ไม่ได้ระบุคำตอบ</span>}</p>
                      
                      {a.image_paths && a.image_paths.length > 0 && (
                        <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-800/60">
                           {a.image_paths.map((src, i) => (
                             <img key={i} src={src} className="h-24 w-auto rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 cursor-zoom-in hover:scale-[1.02] transition-transform" onClick={() => setModalImage({ src, alt: "Student Answer" })} />
                           ))}
                        </div>
                      )}
                   </div>

                   <div className="p-6 bg-blue-50/50 dark:bg-blue-900/10 rounded-xl border border-blue-100 dark:border-blue-900/20">
                      <div className="flex flex-col md:flex-row justify-between items-start gap-6">
                         <div className="flex-1 space-y-4">
                            <div className="flex items-center gap-3">
                               <div className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 text-xs font-semibold rounded-md border border-blue-200/60 dark:border-blue-800/40">
                                 AI Assessment
                               </div>
                               <span className={`text-xs font-medium px-2 py-1 rounded-md border ${
                                 a.ai_confidence === 'low' ? 'bg-orange-50 text-orange-700 border-orange-200 dark:border-orange-800/40 dark:bg-orange-900/30 dark:text-orange-400' 
                                 : 'bg-green-50 text-green-700 border-green-200 dark:border-green-800/40 dark:bg-green-900/30 dark:text-green-400'
                               }`}>
                                 Confidence: {a.ai_confidence}
                               </span>
                            </div>
                            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed bg-white dark:bg-gray-900/50 p-4 rounded-lg border border-blue-50 dark:border-blue-900/20 shadow-sm">
                              {a.ai_feedback || <span className="text-gray-400 italic">ไม่มี Feedback จาก AI</span>}
                            </p>
                            
                            <div className="pt-4 mt-4 border-t border-blue-100 dark:border-blue-900/30">
                               <p className="text-xs font-semibold text-gray-500 mb-2">อาจารย์ให้ความเห็นเพิ่มเติม</p>
                               <Textarea 
                                 placeholder="พิมพ์คอมเมนต์ให้นักศึกษา..."
                                 className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus-visible:ring-2 focus-visible:ring-blue-500/20 focus-visible:border-blue-500 transition-all min-h-[80px] text-sm resize-y"
                                 value={comments[a.question_id] || ""}
                                 onChange={(e) => handleCommentChange(a.question_id, e.target.value)}
                               />
                            </div>
                         </div>

                         <div className="w-full md:w-36 bg-white dark:bg-gray-900 p-5 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800 text-center flex flex-col items-center justify-center shrink-0">
                            <p className="text-xs font-semibold text-gray-500 mb-3">คะแนน</p>
                            <div className="flex items-baseline gap-1">
                               <Input 
                                 type="number"
                                 className="text-2xl font-bold text-center h-12 w-20 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 focus-visible:ring-2 focus-visible:ring-blue-500/20 rounded-md"
                                 value={scores[a.question_id] ?? a.ai_score}
                                 onChange={(e) => handleScoreChange(a.question_id, e.target.value)}
                                 max={a.max_score}
                               />
                               <span className="text-sm font-medium text-gray-400">/ {a.max_score}</span>
                            </div>
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200 p-4">
           <div className="bg-white dark:bg-gray-900 rounded-2xl p-8 max-w-sm w-full shadow-2xl animate-in zoom-in-95 duration-200 border border-gray-200 dark:border-gray-800">
              <h3 className="text-xl font-bold tracking-tight mb-2 text-gray-900 dark:text-white">{isApproved ? 'ยืนยันการแก้ไข?' : 'ยืนยันการอนุมัติ?'}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">คุณต้องการบันทึกผลการตรวจของ <span className="text-gray-900 dark:text-gray-100 font-semibold">{currentStudentName}</span> ใช่หรือไม่?</p>
              <div className="flex gap-3">
                 <Button variant="outline" onClick={() => setIsConfirmOpen(false)} className="flex-1 h-10 rounded-lg font-medium border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">ยกเลิก</Button>
                 <Button onClick={confirmApprove} className="flex-1 h-10 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm">ตกลง</Button>
              </div>
           </div>
        </div>
      )}

      <ImageModal isOpen={!!modalImage} onClose={() => setModalImage(null)} src={modalImage?.src || ""} alt={modalImage?.alt} />
    </div>
  );
}