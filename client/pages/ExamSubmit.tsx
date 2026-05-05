import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Camera, Image as ImageIcon, X, Send, Loader2, CheckCircle2, AlertCircle, Clock, Trash2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import ImageModal from "@/components/ImageModal";
import { Textarea } from "@/components/ui/textarea";

interface Question {
  id: number;
  text: string;
  score: number;
  rubrics?: { name?: string; label?: string; score?: number; description?: string }[];
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
  const [autoSaved, setAutoSaved] = useState(false);
  const autoSaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [modalImage, setModalImage] = useState<{ src: string; alt: string } | null>(null);
  const [showExitModal, setShowExitModal] = useState(false);
  const localStorageKey = `draft_${roomId}_${examId}`;
  const fileInputRefs = useRef<Record<number, HTMLInputElement | null>>({});

  useEffect(() => { answersRef.current = answers; }, [answers]);

  useEffect(() => {
    if (!exam?.end_date || isSubmitting || isTimeUp) return;
    const interval = setInterval(() => {
      const diff = new Date(exam.end_date!).getTime() + extraMinutes * 60000 - Date.now();
      if (diff <= 0) { clearInterval(interval); setTimeLeft("00:00:00"); setIsTimeUp(true); }
      else {
        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        const s = Math.floor((diff % 60000) / 1000);
        setTimeLeft(`${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [exam, isSubmitting, isTimeUp, extraMinutes]);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "student") navigate("/home");
  }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || !roomId || !examId) return;

    const fetchExam = async () => {
      try {
        const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) {
          const data: Exam = await res.json();
          setExam(data);
          const initial: Record<number, AnswerState> = {};
          data.questions.forEach(q => { initial[q.id] = { text: "", images: [], imagePreviews: [] }; });
          setAnswers(initial);
        } else { toast.error("ไม่พบข้อสอบ"); navigate(`/room/${roomId}`); }
      } catch { toast.error("เกิดข้อผิดพลาด"); } finally { setIsFetching(false); }
    };

    const checkSubmission = async () => {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/submissions/me`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { const d = await res.json(); if (d.status && d.status !== "missing") { toast.info("คุณส่งคำตอบไปแล้ว"); navigate(`/room/${roomId}/exam/${examId}`); } }
    };

    const fetchExtension = async () => {
      try { const r = await fetch(`/api/rooms/${roomId}/exams/${examId}/extensions/me`, { headers: { Authorization: `Bearer ${token}` } }); if (r.ok) { const d = await r.json(); setExtraMinutes(d.extra_minutes || 0); } } catch { /* ignore */ }
    };

    const fetchDraft = async () => {
      try {
        const r = await fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, { headers: { Authorization: `Bearer ${token}` } });
        if (r.ok) {
          const data = await r.json();
          if (data.answers && Object.keys(data.answers).length > 0) {
            setAnswers(prev => { const u = { ...prev }; Object.entries(data.answers).forEach(([k, v]) => { const id = parseInt(k); if (u[id]) u[id] = { ...u[id], text: v as string }; }); return u; });
            toast.info("โหลดคำตอบที่บันทึกไว้");
          } else {
            const local = localStorage.getItem(localStorageKey);
            if (local) { const parsed = JSON.parse(local); setAnswers(prev => { const u = { ...prev }; Object.entries(parsed).forEach(([k, v]) => { const id = parseInt(k); if (u[id]) u[id] = { ...u[id], text: v as string }; }); return u; }); }
          }
        }
      } catch { /* ignore */ }
    };

    Promise.all([fetchExam(), checkSubmission(), fetchExtension()]).then(() => setTimeout(fetchDraft, 300));
  }, [token, roomId, examId, navigate]);

  const handleTextChange = (qId: number, value: string) => {
    setAnswers(prev => ({ ...prev, [qId]: { ...prev[qId], text: value } }));
    const updated = { ...answersRef.current, [qId]: { ...answersRef.current[qId], text: value } };
    const textOnly: Record<string, string> = {};
    Object.entries(updated).forEach(([k, v]) => { textOnly[k] = v.text; });
    localStorage.setItem(localStorageKey, JSON.stringify(textOnly));
    if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    setAutoSaved(false);
    autoSaveTimerRef.current = setTimeout(async () => {
      try {
        await fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, { method: "POST", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify({ answers: textOnly }) });
        setAutoSaved(true);
      } catch { /* ignore */ }
    }, 2000);
  };

  const flushSave = useCallback(async () => {
    const textOnly: Record<string, string> = {};
    Object.entries(answersRef.current).forEach(([k, v]) => { textOnly[k] = v.text; });
    if (!Object.keys(textOnly).length) return;
    try { await fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, { method: "POST", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify({ answers: textOnly }) }); } catch { /* ignore */ }
  }, [token, roomId, examId]);

  useEffect(() => {
    window.addEventListener("beforeunload", flushSave);
    return () => { window.removeEventListener("beforeunload", flushSave); if (autoSaveTimerRef.current) { clearTimeout(autoSaveTimerRef.current); flushSave(); } };
  }, [flushSave]);

  const handleImageSelect = useCallback((qId: number, files: FileList) => {
    Array.from(files).filter(f => { if (f.size > 5 * 1024 * 1024) { toast.error(`${f.name}: ไฟล์ต้องไม่เกิน 5MB`); return false; } return true; })
      .forEach(file => {
        const url = URL.createObjectURL(file);
        setAnswers(prev => ({ ...prev, [qId]: { ...prev[qId], images: [...(prev[qId]?.images || []), file], imagePreviews: [...(prev[qId]?.imagePreviews || []), url] } }));
      });
  }, []);

  const handleRemoveImage = (qId: number, idx: number) => {
    const prev = answers[qId];
    if (prev?.imagePreviews[idx]) URL.revokeObjectURL(prev.imagePreviews[idx]);
    setAnswers(p => ({ ...p, [qId]: { ...p[qId], images: p[qId].images.filter((_, i) => i !== idx), imagePreviews: p[qId].imagePreviews.filter((_, i) => i !== idx) } }));
  };

  const handleSubmit = useCallback(async () => {
    if (!token || !exam) return;
    setIsSubmitting(true);
    setIsSubmitConfirm(false);
    try {
      const formData = new FormData();
      const current = answersRef.current;
      formData.append("answers", JSON.stringify(exam.questions.map(q => ({ question_id: q.id, answer_text: current[q.id]?.text || "" }))));
      exam.questions.forEach(q => (current[q.id]?.images || []).forEach((img, i) => formData.append(`image_${q.id}_${i}`, img, img.name)));
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}/submit-multipart`, { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData });
      const data = await res.json();
      if (res.ok) {
        localStorage.removeItem(localStorageKey);
        fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } }).catch(() => {});
        toast.success("ส่งคำตอบสำเร็จ!");
        navigate(`/room/${roomId}/exam/${examId}`);
      } else if (res.status === 409) { toast.error(data.detail || "ส่งไปแล้ว"); navigate(`/room/${roomId}/exam/${examId}`); }
      else toast.error(data.detail || "เกิดข้อผิดพลาด");
    } catch { toast.error("ไม่สามารถส่งได้ กรุณาตรวจสอบการเชื่อมต่อ"); }
    finally { setIsSubmitting(false); }
  }, [token, exam, roomId, examId, navigate]);

  useEffect(() => { if (isTimeUp && !isSubmitting) { toast.error("หมดเวลา! ระบบส่งคำตอบอัตโนมัติ", { duration: 5000 }); handleSubmit(); } }, [isTimeUp]);

  const handleDiscardAndExit = async () => {
    try {
      localStorage.removeItem(localStorageKey);
      await fetch(`/api/rooms/${roomId}/exams/${examId}/draft`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      toast.success("ล้างร่างคำตอบและออกจากระบบ");
      navigate(`/room/${roomId}/exam/${examId}`);
    } catch {
      toast.error("เกิดข้อผิดพลาดในการลบร่างคำตอบ");
      navigate(`/room/${roomId}/exam/${examId}`);
    }
  };

  const answeredCount = Object.values(answers).filter(a => a.text.trim() || a.images.length > 0).length;
  const totalQ = exam?.questions.length ?? 0;
  const progress = totalQ > 0 ? (answeredCount / totalQ) * 100 : 0;
  const isLow = timeLeft && (timeLeft.startsWith("00:0") || timeLeft.startsWith("00:1"));

   if (isLoading || isFetching) return <div className="flex h-screen items-center justify-center bg-[#F9FBFD] dark:bg-[#111111]"><Loader2 className="animate-spin text-blue-500 h-8 w-8" /></div>;

  return (
    <div className="min-h-screen bg-[#F9FBFD] dark:bg-[#111111] transition-colors duration-200 font-sans">

      {/* Docs-style Toolbar */}
      <div className="sticky top-0 z-40 bg-[#EDF2FA] dark:bg-[#1E1E1E] border-b border-gray-300 dark:border-gray-800 px-2 sm:px-4 py-2 flex items-center justify-between gap-2 sm:gap-4 shadow-sm">
        <div className="flex items-center gap-1 sm:gap-2 min-w-0">
          <button 
            onClick={() => {
              if (answeredCount > 0) setShowExitModal(true);
              else navigate(`/room/${roomId}/exam/${examId}`);
            }} 
            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full text-gray-600 dark:text-gray-300 transition-colors shrink-0" 
            title="กลับ"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="flex flex-col min-w-0">
            <h1 className="text-base sm:text-lg text-gray-800 dark:text-gray-100 font-medium truncate">{exam?.title}</h1>
            <div className="flex items-center gap-2 sm:gap-4 px-0 mt-0.5 text-[10px] sm:text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1 shrink-0">{autoSaved ? <span className="text-green-600 dark:text-green-400 flex items-center gap-1">บันทึกแล้ว ✓</span> : "กำลังพิมพ์..."}</span>
              <span className="font-medium text-blue-600 dark:text-blue-400 shrink-0">ตอบแล้ว {answeredCount}/{totalQ}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          {/* Timer */}
          {timeLeft && (
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-mono font-bold border transition-colors ${isLow ? "bg-red-50 text-red-600 border-red-200 animate-pulse" : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 shadow-sm"}`}>
              <Clock size={16} className={isLow ? "text-red-500" : "text-gray-400"} />
              {timeLeft}
              {extraMinutes > 0 && <span className="text-[10px] font-sans font-medium text-green-600 ml-1">+{extraMinutes}m</span>}
            </div>
          )}

          <Button 
            onClick={() => setIsSubmitConfirm(true)} 
            disabled={isSubmitting} 
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-4 sm:px-6 h-8 sm:h-10 text-xs sm:text-sm font-medium shadow-md transition-all active:scale-95 shrink-0"
          >
            {isSubmitting ? <Loader2 size={16} className="animate-spin mr-2" /> : <Send size={16} className="mr-2" />}
            ส่งคำตอบ
          </Button>
        </div>
      </div>

      {/* Progress Bar (Subtle) */}
      <div className="sticky top-[48px] sm:top-[56px] z-30 w-full bg-gray-200 dark:bg-gray-800 h-1 overflow-hidden">
        <div className="h-full bg-blue-500 transition-all duration-500 ease-out" style={{ width: `${progress}%` }} />
      </div>

      {/* Confirm Modal */}
      {isSubmitConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 max-w-sm w-full border border-gray-200 dark:border-gray-800 animate-in zoom-in-95 duration-200">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Send size={24} className="text-blue-500" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">ยืนยันการส่งข้อสอบ?</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                คุณตอบคำถามแล้ว <span className="font-bold text-blue-600 dark:text-blue-400">{answeredCount}</span> จากทั้งหมด <span className="font-bold text-blue-600 dark:text-blue-400">{totalQ}</span> ข้อ
              </p>
              {answeredCount < totalQ && (
                <div className="bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 p-3 rounded-lg text-xs flex items-start gap-2 text-left mb-4">
                  <AlertCircle size={14} className="shrink-0 mt-0.5" />
                  <span>ยังมีข้อสอบที่ยังไม่ได้ตอบอีก {totalQ - answeredCount} ข้อ โปรดตรวจสอบให้แน่ใจก่อนส่ง</span>
                </div>
              )}
              <p className="text-xs text-gray-400 dark:text-gray-500 font-medium italic">เมื่อส่งแล้วจะไม่สามารถกลับมาแก้ไขได้อีก</p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setIsSubmitConfirm(false)} className="flex-1 h-11 rounded-xl border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300">กลับไปทวน</Button>
              <Button onClick={handleSubmit} disabled={isSubmitting} className="flex-1 h-11 rounded-xl bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-200 dark:shadow-none">
                {isSubmitting ? <Loader2 size={18} className="animate-spin mr-2" /> : "ยืนยันส่ง"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Exit Modal */}
      {showExitModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 max-w-sm w-full border border-gray-200 dark:border-gray-800 animate-in zoom-in-95 duration-200">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-amber-50 dark:bg-amber-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle size={24} className="text-amber-500" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">คุณต้องการออกจากหน้าทำข้อสอบ?</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                คุณตอบคำถามค้างไว้ <span className="font-bold text-blue-600 dark:text-blue-400">{answeredCount} ข้อ</span> ระบบได้บันทึกร่างคำตอบของคุณไว้แล้ว
              </p>
            </div>
            <div className="flex flex-col gap-2.5">
              <Button onClick={() => setShowExitModal(false)} className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium">
                ทำข้อสอบต่อ
              </Button>
              <Button variant="outline" onClick={() => navigate(`/room/${roomId}/exam/${examId}`)} className="w-full h-11 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 rounded-xl font-medium">
                บันทึกร่างและออก
              </Button>
              <Button variant="ghost" onClick={handleDiscardAndExit} className="w-full h-11 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-xl font-medium">
                ทิ้งร่างและออก
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Docs Canvas (The Paper) */}
      <div className="py-4 sm:py-10 px-2 sm:px-8">
        <div className="max-w-[816px] mx-auto bg-white dark:bg-[#1E1E1E] shadow-xl border border-gray-300 dark:border-gray-800 min-h-screen sm:min-h-[1056px] p-6 sm:p-16 flex flex-col gap-8 rounded-sm transition-colors duration-200">
          
          {/* Document Header */}
          <div className="border-b-2 border-gray-900 dark:border-white pb-6 mb-2">
             <div className="flex justify-between items-start gap-4">
               <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex-1">{exam?.title}</h2>
               <div className="text-right shrink-0">
                 <p className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">คะแนนเต็ม</p>
                 <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{exam?.total_score}</p>
               </div>
             </div>
             {exam?.description && <p className="text-base text-gray-600 dark:text-gray-400 mt-2 italic">{exam.description}</p>}
          </div>

          {/* Questions Stream */}
          <div className="space-y-12">
            {exam?.questions.map((q, index) => {
              const ans = answers[q.id] || { text: "", images: [], imagePreviews: [] };
              const hasAnswer = ans.text.trim() || ans.images.length > 0;
              
              return (
                <div key={q.id} className="group relative flex gap-4 pl-4 border-l-4 border-transparent hover:border-blue-200 dark:hover:border-blue-900/50 transition-colors -ml-5 pr-4 py-2">
                  
                  <div className={`font-medium text-lg pt-0.5 min-w-[28px] transition-colors ${hasAnswer ? "text-blue-600 dark:text-blue-400" : "text-gray-400"}`}>
                    {index + 1}.
                  </div>

                  <div className="flex-1 space-y-4">
                    {/* Question Header */}
                    <div className="flex justify-between items-start gap-4">
                      <p className="text-lg text-gray-900 dark:text-gray-100 font-medium leading-relaxed flex-1">
                        {q.text}
                      </p>
                      <div className="shrink-0 flex items-center gap-1 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 px-2 py-0.5 rounded-md text-xs font-semibold text-gray-500">
                        {q.score} คะแนน
                      </div>
                    </div>

                    {/* Question Images */}
                    {q.image_paths && q.image_paths.length > 0 ? (
                      <div className="flex flex-wrap gap-3">
                        {q.image_paths.map((src, i) => (
                          <img key={i} src={src} alt="" className="max-h-48 w-auto rounded-lg border border-gray-300 dark:border-gray-700 cursor-zoom-in hover:shadow-md transition-shadow" onClick={() => setModalImage({ src, alt: `รูปโจทย์ ${i+1}` })} />
                        ))}
                      </div>
                    ) : q.image_path ? (
                      <img src={q.image_path} alt="" className="max-h-64 w-auto rounded-lg border border-gray-300 dark:border-gray-700 cursor-zoom-in hover:shadow-md transition-shadow" onClick={() => setModalImage({ src: q.image_path!, alt: "รูปโจทย์" })} />
                    ) : null}

                    {/* Answer Input */}
                    <div className="space-y-3 pt-2">
                      <label htmlFor={`answer-${q.id}`} className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest block">คำตอบของคุณ</label>
                      <textarea
                        id={`answer-${q.id}`}
                        placeholder="พิมพ์คำตอบที่นี่..."
                        className="w-full min-h-[160px] p-4 text-base bg-gray-50/50 dark:bg-gray-900/30 border-2 border-gray-100 dark:border-gray-800 rounded-xl focus:bg-white dark:focus:bg-gray-900 focus:border-blue-400 dark:focus:border-blue-600 focus:ring-0 transition-all outline-none text-gray-800 dark:text-gray-100 resize-y"
                        value={ans.text}
                        onChange={e => handleTextChange(q.id, e.target.value)}
                      />
                      
                      {/* Answer images preview */}
                      {ans.imagePreviews.length > 0 && (
                        <div className="flex flex-wrap gap-3 pt-2">
                          {ans.imagePreviews.map((src, i) => (
                            <div key={i} className="relative group/img w-24 h-24 rounded-xl overflow-hidden border-2 border-gray-200 dark:border-gray-700 shadow-sm">
                              <img src={src} alt="" className="w-full h-full object-cover cursor-zoom-in" onClick={() => setModalImage({ src, alt: `คำตอบ ${i+1}` })} />
                              <button 
                                onClick={e => { e.stopPropagation(); handleRemoveImage(q.id, i); }} 
                                className="absolute top-1 right-1 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover/img:opacity-100 transition-all shadow-md active:scale-90"
                              >
                                <X size={12} />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Image actions */}
                      <div className="flex gap-2 pt-1">
                        <input ref={el => { fileInputRefs.current[q.id] = el; }} type="file" accept="image/*" multiple className="hidden" onChange={e => { if (e.target.files) handleImageSelect(q.id, e.target.files); e.target.value = ""; }} />
                        <input id={`cam-${q.id}`} type="file" accept="image/*" capture="environment" className="hidden" onChange={e => { if (e.target.files) handleImageSelect(q.id, e.target.files); e.target.value = ""; }} />
                        
                        <button 
                          onClick={() => document.getElementById(`cam-${q.id}`)?.click()} 
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                          <Camera size={14} /> ถ่ายรูปแนบ
                        </button>
                        
                        <button 
                          onClick={() => fileInputRefs.current[q.id]?.click()} 
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                          <ImageIcon size={14} /> เลือกรูปภาพ
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Paper Footer */}
          <div className="mt-12 pt-8 border-t border-gray-100 dark:border-gray-800 text-center">
            <p className="text-xs text-gray-400 dark:text-gray-600 font-medium">-- สิ้นสุดข้อสอบ --</p>
          </div>
        </div>
      </div>

      <ImageModal isOpen={!!modalImage} onClose={() => setModalImage(null)} src={modalImage?.src || ""} alt={modalImage?.alt} />
    </div>
  );
}
