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

  const answeredCount = Object.values(answers).filter(a => a.text.trim() || a.images.length > 0).length;
  const totalQ = exam?.questions.length ?? 0;
  const progress = totalQ > 0 ? (answeredCount / totalQ) * 100 : 0;
  const isLow = timeLeft && (timeLeft.startsWith("00:0") || timeLeft.startsWith("00:1"));

  if (isLoading || isFetching) return <div className="flex h-screen items-center justify-center"><Loader2 className="animate-spin text-gray-400 h-8 w-8" /></div>;

  return (
    <div className="min-h-screen bg-gray-50 pb-28">
      <Navbar />

      {/* Confirm Modal */}
      {isSubmitConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
            <div className="text-center mb-5">
              <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-3">
                <Send size={20} className="text-blue-500" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">ยืนยันการส่ง?</h3>
              <p className="text-sm text-gray-500">
                คุณตอบแล้ว <span className="font-bold text-blue-600">{answeredCount}/{totalQ}</span> ข้อ
              </p>
              <p className="text-xs text-red-500 mt-2 font-medium">ไม่สามารถแก้ไขได้หลังส่ง</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setIsSubmitConfirm(false)} className="flex-1 h-9 text-sm">กลับไปตรวจ</Button>
              <Button onClick={handleSubmit} disabled={isSubmitting} className="flex-1 h-9 text-sm bg-blue-600 hover:bg-blue-700">
                {isSubmitting ? <Loader2 size={14} className="animate-spin mr-1" /> : <Send size={14} className="mr-1" />}
                ส่งเลย
              </Button>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-2xl mx-auto px-4 py-6 space-y-4">
        {/* Header */}
        <div>
          <button onClick={() => navigate(`/room/${roomId}/exam/${examId}`)} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-3 transition-colors">
            <ArrowLeft size={15} /> กลับ
          </button>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">{exam?.title}</h1>
              {exam?.description && <p className="text-sm text-gray-500 mt-0.5">{exam.description}</p>}
            </div>
            {/* Timer */}
            {timeLeft && (
              <div className={`shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-mono font-bold border ${isLow ? "bg-red-50 text-red-600 border-red-200" : "bg-gray-100 text-gray-700 border-gray-200"}`}>
                <Clock size={13} /> {timeLeft}
                {extraMinutes > 0 && <span className="text-xs font-sans font-medium text-green-600">+{extraMinutes}m</span>}
              </div>
            )}
          </div>
        </div>

        {/* Question Cards */}
        {exam?.questions.map((q, index) => {
          const ans = answers[q.id] || { text: "", images: [], imagePreviews: [] };
          const hasAnswer = ans.text.trim() || ans.images.length > 0;
          return (
            <div key={q.id} className={`bg-white rounded-xl border-2 overflow-hidden transition-colors ${hasAnswer ? "border-blue-200" : "border-gray-200"}`}>
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${hasAnswer ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-500"}`}>
                    {hasAnswer ? <CheckCircle2 size={13} /> : index + 1}
                  </span>
                  <span className="text-xs text-gray-500">{q.score} คะแนน</span>
                </div>
                {autoSaved && <span className="text-xs text-green-500">บันทึกแล้ว ✓</span>}
              </div>

              <div className="p-4 space-y-3">
                {/* Question text */}
                <p className="text-sm text-gray-800 leading-relaxed font-medium">{q.text}</p>

                {/* Question images */}
                {q.image_paths && q.image_paths.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {q.image_paths.map((src, i) => (
                      <img key={i} src={src} alt="" className="h-28 w-auto rounded-lg border border-gray-200 cursor-zoom-in" onClick={() => setModalImage({ src, alt: `รูปโจทย์ ${i+1}` })} />
                    ))}
                  </div>
                ) : q.image_path ? (
                  <img src={q.image_path} alt="" className="max-h-48 w-auto rounded-lg border border-gray-200 cursor-zoom-in" onClick={() => setModalImage({ src: q.image_path!, alt: "รูปโจทย์" })} />
                ) : null}

                {/* Text Answer */}
                <Textarea
                  id={`answer-${q.id}`}
                  placeholder="พิมพ์คำตอบที่นี่..."
                  className="min-h-[100px] resize-none text-sm border-gray-200 focus:border-blue-400 bg-gray-50"
                  value={ans.text}
                  onChange={e => handleTextChange(q.id, e.target.value)}
                />

                {/* Answer images preview */}
                {ans.imagePreviews.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {ans.imagePreviews.map((src, i) => (
                      <div key={i} className="relative group w-20 h-20 rounded-lg overflow-hidden border border-gray-200">
                        <img src={src} alt="" className="w-full h-full object-cover cursor-zoom-in" onClick={() => setModalImage({ src, alt: `คำตอบ ${i+1}` })} />
                        <button onClick={e => { e.stopPropagation(); handleRemoveImage(q.id, i); }} className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <Trash2 size={10} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Upload buttons */}
                <div className="flex gap-2">
                  <input ref={el => { fileInputRefs.current[q.id] = el; }} type="file" accept="image/*" multiple className="hidden" onChange={e => { if (e.target.files) handleImageSelect(q.id, e.target.files); e.target.value = ""; }} />
                  <input id={`cam-${q.id}`} type="file" accept="image/*" capture="environment" className="hidden" onChange={e => { if (e.target.files) handleImageSelect(q.id, e.target.files); e.target.value = ""; }} />
                  <button onClick={() => document.getElementById(`cam-${q.id}`)?.click()} className="flex-1 flex items-center justify-center gap-1.5 py-2 border border-dashed border-gray-200 hover:border-blue-300 hover:bg-blue-50/30 rounded-lg text-xs text-gray-400 hover:text-blue-500 transition-colors">
                    <Camera size={13} /> ถ่ายรูป
                  </button>
                  <button onClick={() => fileInputRefs.current[q.id]?.click()} className="flex-1 flex items-center justify-center gap-1.5 py-2 border border-dashed border-gray-200 hover:border-blue-300 hover:bg-blue-50/30 rounded-lg text-xs text-gray-400 hover:text-blue-500 transition-colors">
                    <ImageIcon size={13} /> เลือกรูป{ans.images.length > 0 ? ` (${ans.images.length})` : ""}
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {/* Warning */}
        {answeredCount < totalQ && (
          <div className="flex items-start gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2.5">
            <AlertCircle size={13} className="shrink-0 mt-0.5" />
            <span>ยังเหลือ {totalQ - answeredCount} ข้อที่ยังไม่ตอบ</span>
          </div>
        )}
      </main>

      {/* Floating Submit Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 z-40">
        <div className="max-w-2xl mx-auto flex items-center gap-4">
          <div className="flex-1">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>ตอบแล้ว</span>
              <span className="font-medium text-gray-600">{answeredCount}/{totalQ} ข้อ</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
          </div>
          <Button onClick={() => setIsSubmitConfirm(true)} disabled={isSubmitting} className="shrink-0 bg-blue-600 hover:bg-blue-700 h-9 px-5 text-sm font-medium">
            {isSubmitting ? <Loader2 size={14} className="animate-spin mr-1" /> : <Send size={14} className="mr-1" />}
            ส่งคำตอบ
          </Button>
        </div>
      </div>

      <ImageModal isOpen={!!modalImage} onClose={() => setModalImage(null)} src={modalImage?.src || ""} alt={modalImage?.alt} />
    </div>
  );
}
