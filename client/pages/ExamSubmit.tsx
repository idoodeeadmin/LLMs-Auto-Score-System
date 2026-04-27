import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Camera, Image as ImageIcon, X, Send,
  Loader2, CheckCircle2, AlertCircle, BookOpen, Trash2, Clock, Save
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import ImageModal from "@/components/ImageModal";
import { Textarea } from "@/components/ui/textarea";

interface Rubric {
  name?: string;
  label?: string;
  score?: number;
  description?: string;
}

interface Question {
  id: number;
  text: string;
  score: number;
  rubrics?: Rubric[];
  order_index: number;
  image_path?: string | null;
  image_paths?: string[];
}

interface Exam {
  id: number;
  title: string;
  description?: string;
  total_score: number;
  start_date?: string;
  end_date?: string;
  questions: Question[];
}

interface AnswerState {
  text: string;
  images: File[];
  imagePreviews: string[];
}

export default function ExamSubmit() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();

  const [exam, setExam] = useState<Exam | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitConfirm, setIsSubmitConfirm] = useState(false);
  const [answers, setAnswers] = useState<Record<number, AnswerState>>({});
  const answersRef = useRef<Record<number, AnswerState>>({});
  
  const [timeLeft, setTimeLeft] = useState<string | null>(null);
  const [isTimeUp, setIsTimeUp] = useState(false);
  const [extraMinutes, setExtraMinutes] = useState(0);
  const [autoSaveStatus, setAutoSaveStatus] = useState<"idle" | "saving" | "saved">("idle");
  const autoSaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Image Modal State
  const [modalImage, setModalImage] = useState<{ src: string; alt: string } | null>(null);
  const localStorageKey = `draft_${roomId}_${examId}`;

  const fileInputRefs = useRef<Record<number, HTMLInputElement | null>>({});

  // Sync answers with ref for safe closure access in auto-submit
  useEffect(() => {
    answersRef.current = answers;
  }, [answers]);

  // Countdown timer logic — includes extra_minutes
  useEffect(() => {
    if (!exam?.end_date || isSubmitting || isTimeUp) return;

    const interval = setInterval(() => {
      const now = new Date().getTime();
      const end = new Date(exam.end_date!).getTime() + extraMinutes * 60 * 1000;
      const diff = end - now;

      if (diff <= 0) {
        clearInterval(interval);
        setTimeLeft("00:00:00");
        setIsTimeUp(true);
      } else {
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        const format = (n: number) => n.toString().padStart(2, "0");
        setTimeLeft(`${format(hours)}:${format(minutes)}:${format(seconds)}`);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [exam, isSubmitting, isTimeUp, extraMinutes]);

  // Redirect guards
  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "student") navigate("/home");
  }, [user, isLoading, navigate]);

  // Load exam
  useEffect(() => {
    if (!token || !roomId || !examId) return;
    const fetchExam = async () => {
      try {
        const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data: Exam = await res.json();
          setExam(data);
          // Initialize answers
          const initial: Record<number, AnswerState> = {};
          data.questions.forEach((q) => {
            initial[q.id] = { text: "", images: [], imagePreviews: [] };
          });
          setAnswers(initial);
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

    // Also check if already submitted
    const checkSubmission = async () => {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status && data.status !== "missing") {
          toast.info("คุณส่งคำตอบข้อสอบนี้ไปแล้ว");
          navigate(`/room/${roomId}/exam/${examId}`);
        }
      }
    };

    Promise.all([fetchExam(), checkSubmission()]);

    // Fetch time extension for this student
    const fetchExtension = async () => {
      try {
        const r = await fetch(`/api/rooms/${roomId}/exams/${examId}/extensions/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (r.ok) {
          const data = await r.json();
          setExtraMinutes(data.extra_minutes || 0);
        }
      } catch { /* ignore */ }
    };
    fetchExtension();

    // Load draft from server (prefer server over localStorage)
    const fetchDraft = async () => {
      try {
        const r = await fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (r.ok) {
          const data = await r.json();
          if (data.answers && Object.keys(data.answers).length > 0) {
            // Restore text answers from server draft
            setAnswers(prev => {
              const updated = { ...prev };
              Object.entries(data.answers).forEach(([qId, text]) => {
                const id = parseInt(qId);
                if (updated[id]) {
                  updated[id] = { ...updated[id], text: text as string };
                }
              });
              return updated;
            });
            toast.info("โหลดคำตอบที่บันทึกไว้ก่อนหน้า", { duration: 3000 });
          } else {
            // Fallback: check localStorage
            const localDraft = localStorage.getItem(localStorageKey);
            if (localDraft) {
              const parsed = JSON.parse(localDraft);
              setAnswers(prev => {
                const updated = { ...prev };
                Object.entries(parsed).forEach(([qId, text]) => {
                  const id = parseInt(qId);
                  if (updated[id]) {
                    updated[id] = { ...updated[id], text: text as string };
                  }
                });
                return updated;
              });
            }
          }
        }
      } catch { /* ignore */ }
    };
    setTimeout(fetchDraft, 300); // slight delay so exam data loads first
  }, [token, roomId, examId, navigate]);

  const answeredCount = Object.values(answers).filter(
    (a) => a.text.trim() || a.images.length > 0
  ).length;
  const totalQuestions = exam?.questions.length ?? 0;
  const progress = totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0;

  const handleTextChange = (qId: number, value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [qId]: { ...prev[qId], text: value },
    }));
    // Save to localStorage immediately
    const updated = { ...answersRef.current, [qId]: { ...answersRef.current[qId], text: value } };
    const textOnly: Record<string, string> = {};
    Object.entries(updated).forEach(([k, v]) => { textOnly[k] = v.text; });
    localStorage.setItem(localStorageKey, JSON.stringify(textOnly));

    // Debounced server save
    if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    setAutoSaveStatus("saving");
    autoSaveTimerRef.current = setTimeout(async () => {
      try {
        await fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({ answers: textOnly }),
        });
        setAutoSaveStatus("saved");
      } catch {
        setAutoSaveStatus("idle");
      }
    }, 2000);
  };

  // Force save function
  const flushSave = useCallback(async () => {
    const currentAnswers = answersRef.current;
    const textOnly: Record<string, string> = {};
    Object.entries(currentAnswers).forEach(([k, v]) => { textOnly[k] = v.text; });
    
    if (Object.keys(textOnly).length === 0) return;

    try {
      await fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ answers: textOnly }),
      });
    } catch (e) {
      console.error("Flush save failed:", e);
    }
  }, [token, roomId, examId]);

  // Handle auto-save on unmount and page leave
  useEffect(() => {
    const handleBeforeUnload = () => {
      // We use beacon or a synchronous-like fetch if possible, but for SPA unmount, flushSave is enough
      flushSave();
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
        flushSave();
      }
    };
  }, [flushSave]);

  const handleImageSelect = useCallback((qId: number, files: FileList) => {
    const newFiles = Array.from(files).filter(f => {
      if (f.size > 5 * 1024 * 1024) {
        toast.error(`${f.name}: ไฟล์ต้องไม่เกิน 5MB`);
        return false;
      }
      return true;
    });
    newFiles.forEach(file => {
      const url = URL.createObjectURL(file);
      setAnswers((prev) => ({
        ...prev,
        [qId]: {
          ...prev[qId],
          images: [...(prev[qId]?.images || []), file],
          imagePreviews: [...(prev[qId]?.imagePreviews || []), url],
        },
      }));
    });
  }, []);

  const handleRemoveImage = (qId: number, imgIdx: number) => {
    const prev = answers[qId];
    if (prev?.imagePreviews[imgIdx]) URL.revokeObjectURL(prev.imagePreviews[imgIdx]);
    setAnswers((p) => ({
      ...p,
      [qId]: {
        ...p[qId],
        images: p[qId].images.filter((_, i) => i !== imgIdx),
        imagePreviews: p[qId].imagePreviews.filter((_, i) => i !== imgIdx),
      },
    }));
  };

  const handleSubmit = useCallback(async () => {
    if (!token || !exam) return;
    setIsSubmitting(true);
    setIsSubmitConfirm(false);

    try {
      const formData = new FormData();
      const currentAnswers = answersRef.current;

      // Build answers JSON
      const answersJson = exam.questions.map((q) => ({
        question_id: q.id,
        answer_text: currentAnswers[q.id]?.text || "",
      }));
      formData.append("answers", JSON.stringify(answersJson));

      // Append all images for each question as image_{q_id}_0, image_{q_id}_1, ...
      exam.questions.forEach((q) => {
        const imgs = currentAnswers[q.id]?.images || [];
        imgs.forEach((img, idx) => {
          formData.append(`image_${q.id}_${idx}`, img, img.name);
        });
      });

      const res = await fetch(
        `/api/rooms/${roomId}/exams/${examId}/submit-multipart`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        }
      );

      const data = await res.json();

      if (res.ok) {
        // Clear draft after successful submit
        localStorage.removeItem(localStorageKey);
        fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => {});
        toast.success("ส่งคำตอบสำเร็จ! กำลังประมวลผล AI...");
        navigate(`/room/${roomId}/exam/${examId}`);
      } else if (res.status === 409) {
        toast.error(data.detail || "คุณส่งคำตอบนี้ไปแล้ว");
        navigate(`/room/${roomId}/exam/${examId}`);
      } else {
        toast.error(data.detail || "เกิดข้อผิดพลาดในการส่ง");
      }
    } catch {
      toast.error("ไม่สามารถส่งได้ กรุณาตรวจสอบการเชื่อมต่อ");
    } finally {
      setIsSubmitting(false);
    }
  }, [token, exam, roomId, examId, navigate]);

  // Auto-submit when time is up
  useEffect(() => {
    if (isTimeUp && !isSubmitting) {
      toast.error("เวลาทำข้อสอบหมดแล้ว! ระบบจะส่งคำตอบของคุณโดยอัตโนมัติ", { duration: 5000 });
      handleSubmit();
    }
  }, [isTimeUp]); // only trigger once when isTimeUp changes to true

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50/30 pb-32">
      <Navbar />

      {/* Confirm Submit Modal */}
      <AnimatePresence>
        {isSubmitConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-8 max-w-md w-full border border-gray-100 dark:border-slate-800"
            >
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send size={28} className="text-indigo-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">ยืนยันการส่ง?</h3>
                <p className="text-gray-500 dark:text-slate-400 leading-relaxed">
                  คุณตอบแล้ว{" "}
                  <span className="font-bold text-indigo-600">{answeredCount}/{totalQuestions}</span>{" "}
                  ข้อ
                  <br />
                  <span className="text-red-500 font-semibold text-sm">
                    ⚠️ ไม่สามารถแก้ไขหรือส่งซ้ำได้หลังจากนี้
                  </span>
                </p>
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setIsSubmitConfirm(false)}
                  className="flex-1 h-12 rounded-xl"
                >
                  กลับไปตรวจสอบ
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="flex-1 h-12 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold shadow-lg shadow-indigo-200"
                >
                  {isSubmitting ? (
                    <Loader2 size={18} className="animate-spin mr-2" />
                  ) : (
                    <Send size={18} className="mr-2" />
                  )}
                  ส่งคำตอบเลย
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* Back + Title */}
        <div>
          <button
            onClick={() => navigate(`/room/${roomId}/exam/${examId}`)}
            className="flex items-center gap-2 text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:text-slate-200 transition-colors text-sm font-medium mb-4"
          >
            <ArrowLeft size={16} /> กลับ
          </button>
          
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex-1 bg-gradient-to-r from-indigo-600 to-blue-500 rounded-2xl p-6 text-white shadow-lg"
            >
              <p className="text-white/70 text-sm mb-1 uppercase tracking-wide">กำลังทำข้อสอบ</p>
              <h1 className="text-2xl font-bold">{exam?.title}</h1>
              {exam?.description && (
                <p className="text-white/80 mt-1 text-sm">{exam.description}</p>
              )}
              <div className="mt-4 flex items-center gap-4">
                <div className="flex-1 bg-white/20 rounded-full h-2 overflow-hidden">
                  <motion.div
                    className="h-full bg-white dark:bg-slate-800 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.4 }}
                  />
                </div>
                <span className="text-white text-sm font-bold whitespace-nowrap">
                  {answeredCount}/{totalQuestions} ข้อ
                </span>
              </div>
            </motion.div>

            {/* Timer Card */}
            {timeLeft && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`flex flex-col items-center justify-center rounded-2xl p-6 shadow-lg min-w-[200px] border-2 transition-colors duration-300 ${
                  timeLeft.startsWith("00:0") || timeLeft.startsWith("00:1") 
                    ? "bg-red-50 dark:bg-red-900/30 border-red-200 text-red-600" 
                    : "bg-white dark:bg-slate-800 border-indigo-100 text-indigo-700"
                }`}
              >
                <div className="flex items-center gap-2 mb-2 font-bold uppercase tracking-wider text-xs opacity-80">
                  <Clock size={16} />
                  <span>เหลือเวลาทำข้อสอบ</span>
                  {extraMinutes > 0 && (
                    <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full font-bold">
                      +{extraMinutes}m
                    </span>
                  )}
                </div>
                <div className="text-4xl font-black tabular-nums tracking-tight">
                  {timeLeft}
                </div>
              </motion.div>
            )}

            {/* Auto-save badge */}
            {autoSaveStatus !== "idle" && (
              <div className="flex items-center gap-1.5 text-xs text-gray-400 self-end pb-2">
                {autoSaveStatus === "saving" ? (
                  <><Loader2 size={11} className="animate-spin" /> กำลังบันทึก...</>
                ) : (
                  <><Save size={11} className="text-green-500" /> บันทึกร่างแล้ว</>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Question Cards */}
        {exam?.questions.map((q, index) => {
          const ans = answers[q.id] || { text: "", images: [], imagePreviews: [] };
          const hasAnswer = ans.text.trim() || ans.images.length > 0;

          return (
            <motion.div
              key={q.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.06 }}
              className={`bg-white dark:bg-slate-800 rounded-2xl shadow-sm border-2 overflow-hidden transition-all duration-300 ${
                hasAnswer ? "border-indigo-200" : "border-gray-100 dark:border-slate-800"
              }`}
            >
              {/* Question Header */}
              <div className="px-6 pt-6 pb-4">
                <div className="flex items-start gap-4 mb-4">
                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold flex-shrink-0 transition-colors ${
                    hasAnswer ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-500 dark:text-slate-400"
                  }`}>
                    {hasAnswer ? <CheckCircle2 size={18} /> : index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-slate-800 dark:text-slate-200 font-medium leading-relaxed">{q.text}</p>
                    {/* รูปภาพโจทย์จากอาจารย์ — gallery */}
                    {(q.image_paths && q.image_paths.length > 0) ? (
                      <div className="mt-3 grid grid-cols-2 gap-2">
                        {q.image_paths.map((src, i) => (
                          <div key={i} className="rounded-xl overflow-hidden border border-indigo-100 bg-gray-50 dark:bg-slate-900 cursor-zoom-in hover:opacity-90 transition-opacity">
                            <img 
                              src={src} 
                              alt={`รูปโจทย์ ${i+1}`} 
                              className="w-full max-h-48 object-contain" 
                              onClick={() => setModalImage({ src, alt: `รูปโจทย์ข้อ ${index + 1} (${i + 1}/${q.image_paths?.length})` })}
                            />
                          </div>
                        ))}
                        <div className="col-span-2 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1.5 rounded-lg flex items-center gap-1.5">
                          <ImageIcon size={11} className="text-indigo-400" />
                          <span className="text-xs text-indigo-500 font-medium">รูปโจทย์จากอาจารย์ ({q.image_paths.length} รูป)</span>
                        </div>
                      </div>
                    ) : q.image_path ? (
                      <div className="mt-3 rounded-xl overflow-hidden border border-indigo-100">
                        <img src={q.image_path} alt="รูปโจทย์" className="w-full max-h-72 object-contain bg-gray-50 dark:bg-slate-900" />
                        <div className="bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1.5 flex items-center gap-1.5">
                          <ImageIcon size={11} className="text-indigo-400" />
                          <span className="text-xs text-indigo-500 font-medium">รูปโจทย์จากอาจารย์</span>
                        </div>
                      </div>
                    ) : null}
                    {q.rubrics && q.rubrics.length > 0 && (
                      <details className="mt-3">
                        <summary className="text-xs text-indigo-500 cursor-pointer font-medium flex items-center gap-1 hover:text-indigo-700">
                          <BookOpen size={12} /> ดูเกณฑ์การให้คะแนน
                        </summary>
                        <ul className="mt-2 space-y-1 pl-4">
                          {q.rubrics.map((r, i) => (
                            <li key={i} className="text-xs text-gray-500 dark:text-slate-400 flex justify-between">
                              <span>{r.name || r.label}</span>
                              <span className="font-mono text-gray-400 dark:text-slate-500">{r.score} คะแนน</span>
                            </li>
                          ))}
                        </ul>
                      </details>
                    )}
                  </div>
                  <span className="flex-shrink-0 text-sm font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1 rounded-full border border-indigo-100">
                    {q.score} คะแนน
                  </span>
                </div>

                {/* Text Answer */}
                <Textarea
                  id={`answer-${q.id}`}
                  placeholder="พิมพ์คำตอบของคุณที่นี่..."
                  className="min-h-[120px] resize-none border-gray-200 dark:border-slate-700 focus:border-indigo-400 focus:ring-indigo-400 bg-gray-50 dark:bg-slate-900/50 text-slate-800 dark:text-slate-200 placeholder:text-gray-300 rounded-xl text-base leading-relaxed"
                  value={ans.text}
                  onChange={(e) => handleTextChange(q.id, e.target.value)}
                />
              </div>

              {/* Image Section — multi upload */}
              <div className="px-6 pb-5">
                {/* Preview grid */}
                {ans.imagePreviews.length > 0 && (
                  <div className="grid grid-cols-2 gap-2 mb-2">
                    {ans.imagePreviews.map((src, imgIdx) => (
                      <div key={imgIdx} className="relative group rounded-xl overflow-hidden border border-indigo-100 cursor-zoom-in">
                        <img 
                          src={src} 
                          alt={`คำตอบ ${imgIdx+1}`} 
                          className="w-full max-h-40 object-contain bg-gray-50 dark:bg-slate-900 hover:opacity-90 transition-opacity" 
                          onClick={() => setModalImage({ src, alt: `รูปคำตอบข้อ ${index + 1} (${imgIdx + 1}/${ans.imagePreviews.length})` })}
                        />
                        <button
                          onClick={(e) => { e.stopPropagation(); handleRemoveImage(q.id, imgIdx); }}
                          className="absolute top-1 right-1 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center shadow opacity-0 group-hover:opacity-100 transition-opacity z-10"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                {/* Upload buttons */}
                <div className="flex gap-2">
                  <input
                    ref={(el) => { fileInputRefs.current[q.id] = el; }}
                    type="file"
                    accept="image/*"
                    multiple
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files) handleImageSelect(q.id, e.target.files);
                      e.target.value = "";
                    }}
                  />
                  <input
                    id={`camera-${q.id}`}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files) handleImageSelect(q.id, e.target.files);
                      e.target.value = "";
                    }}
                  />
                  <button
                    onClick={() => document.getElementById(`camera-${q.id}`)?.click()}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 border border-dashed border-gray-300 hover:border-indigo-400 hover:bg-indigo-50 dark:bg-indigo-900/30 rounded-xl text-sm text-gray-400 dark:text-slate-500 hover:text-indigo-600 transition-all"
                  >
                    <Camera size={16} /> ถ่ายรูป
                  </button>
                  <button
                    onClick={() => fileInputRefs.current[q.id]?.click()}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 border border-dashed border-gray-300 hover:border-indigo-400 hover:bg-indigo-50 dark:bg-indigo-900/30 rounded-xl text-sm text-gray-400 dark:text-slate-500 hover:text-indigo-600 transition-all"
                  >
                    <ImageIcon size={16} /> เลือกรูป{ans.images.length > 0 ? ` (+${ans.images.length})` : ""}
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}

        {/* Warning if not all answered */}
        {answeredCount < totalQuestions && (
          <div className="flex items-center gap-3 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 rounded-xl px-4 py-3 text-amber-700 text-sm">
            <AlertCircle size={16} className="flex-shrink-0" />
            <span>ยังเหลือ {totalQuestions - answeredCount} ข้อที่ยังไม่ได้ตอบ — สามารถส่งได้ แต่จะได้คะแนน 0 สำหรับข้อที่ว่าง</span>
          </div>
        )}
      </main>

      {/* Floating Submit Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-200 dark:border-slate-700 px-4 py-4 z-40">
        <div className="max-w-3xl mx-auto flex items-center gap-4">
          <div className="flex-1">
            <div className="flex justify-between text-xs text-gray-500 dark:text-slate-400 mb-1">
              <span>ความคืบหน้า</span>
              <span className="font-bold text-indigo-600">{answeredCount}/{totalQuestions} ข้อ</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
              <motion.div
                className="h-full bg-indigo-600 rounded-full"
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
          <Button
            onClick={() => setIsSubmitConfirm(true)}
            disabled={isSubmitting}
            className="px-8 h-11 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 flex-shrink-0"
          >
            {isSubmitting ? (
              <Loader2 size={16} className="animate-spin mr-2" />
            ) : (
              <Send size={16} className="mr-2" />
            )}
            ส่งคำตอบ
          </Button>
        </div>
      </div>

      <ImageModal
        isOpen={!!modalImage}
        onClose={() => setModalImage(null)}
        src={modalImage?.src || ""}
        alt={modalImage?.alt}
      />
    </div>
  );
}
