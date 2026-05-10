import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Plus, Trash2, X, Image as ImageIcon, ArrowLeft, Loader2, BookOpen, Search, Sparkles, Copy, Settings, Check, BookmarkPlus, Bookmark } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import Navbar from "@/components/Navbar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

// A simple auto-resizing textarea component
function AutoResizingTextarea({ value, onChange, placeholder, className, minRows = 1 }: any) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [value]);

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`overflow-hidden resize-none ${className}`}
      rows={minRows}
    />
  );
}

interface RubricItem {
  id: number;
  name: string;
  description: string;
  score: string;
}

interface Question {
  id: number;
  text: string;
  score: string;
  questionImages: string[];
  answerKey: string;
  rubrics: RubricItem[];
  gradingTone: "simple" | "moderate" | "academic";
  isGenerating?: boolean;
  isExpanded?: boolean;
}

interface RubricPreset {
  id: string;
  name: string;
  rubrics: RubricItem[];
}

const newQuestion = (): Question => ({
  id: Date.now() + Math.random(),
  text: "",
  score: "1",
  questionImages: [],
  answerKey: "",
  rubrics: [{ id: Date.now() + Math.random(), name: "", description: "", score: "1" }],
  gradingTone: "moderate",
  isExpanded: false,
});

export default function EditExam() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);

  const [examTitle, setExamTitle] = useState("");
  const [examDescription, setExamDescription] = useState("");
  const [startDateTime, setStartDateTime] = useState("");
  const [endDateTime, setEndDateTime] = useState("");
  const [isRandomized, setIsRandomized] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [questions, setQuestions] = useState<Question[]>([newQuestion()]);

  const [showBankModal, setShowBankModal] = useState(false);
  const [bankQuestions, setBankQuestions] = useState<any[]>([]);
  const [bankSearch, setBankSearch] = useState("");

  const [rubricPresets, setRubricPresets] = useState<RubricPreset[]>(() => {
    try {
      const saved = localStorage.getItem("evaly_rubric_presets");
      return saved ? JSON.parse(saved) : [];
    } catch { return []; }
  });

  const [showPresetModal, setShowPresetModal] = useState<number | null>(null);
  const [presetNameInput, setPresetNameInput] = useState("");
  const [presetToDelete, setPresetToDelete] = useState<string | null>(null);

  const [showExitModal, setShowExitModal] = useState(false);
  const [draftToRestore, setDraftToRestore] = useState<any>(null);

  // Helper to format date for datetime-local input (YYYY-MM-DDTHH:mm)
  const formatDateTime = (date: Date) => {
    const tzOffset = date.getTimezoneOffset() * 60000;
    const localISOTime = new Date(date.getTime() - tzOffset).toISOString().slice(0, 16);
    return localISOTime;
  };

  const setQuickStart = (type: "now" | "15m" | "tomorrow") => {
    const d = new Date();
    if (type === "15m") d.setMinutes(d.getMinutes() + 15);
    if (type === "tomorrow") {
      d.setDate(d.getDate() + 1);
      d.setHours(8, 30, 0, 0);
    }
    setStartDateTime(formatDateTime(d));
  };

  const setQuickEnd = (minutes: number) => {
    const base = startDateTime ? new Date(startDateTime) : new Date();
    const d = new Date(base.getTime() + minutes * 60000);
    setEndDateTime(formatDateTime(d));
  };

  useEffect(() => {
    localStorage.setItem("evaly_rubric_presets", JSON.stringify(rubricPresets));
  }, [rubricPresets]);

  const DRAFT_KEY = `evaly_edit_exam_draft_${examId}`;
  const isInitialLoad = useRef(true);

  const fetchBank = async () => {
    try {
      const res = await fetch("/api/question-bank", { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setBankQuestions(await res.json());
    } catch { /* ignore */ }
  };

  useEffect(() => {
    if (showBankModal) fetchBank();
  }, [showBankModal]);

  // Load existing exam data on mount
  useEffect(() => {
    if (!token || !roomId || !examId) return;
    const fetchExam = async () => {
      try {
        const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setExamTitle(data.title || "");
          setExamDescription(data.description || "");
          setIsRandomized(data.is_randomized === 1);
          
          if (data.start_date) {
            const d = new Date(data.start_date);
            const localIso = new Date(d.getTime() - (d.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
            setStartDateTime(localIso);
          }
          if (data.end_date) {
            const d = new Date(data.end_date);
            const localIso = new Date(d.getTime() - (d.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
            setEndDateTime(localIso);
          }
          
          if (data.questions && data.questions.length > 0) {
            setQuestions(data.questions.map((q: any, i: number) => ({
              id: Date.now() + i,
              text: q.text || "",
              score: String(q.score || ""),
              questionImages: (q.image_paths || []).map((p: string) => {
                if (p.startsWith('http')) return p;
                if (p.startsWith('/')) return `${window.location.origin}${p}`;
                return p;
              }),
              answerKey: q.answer_key || "",
              rubrics: (q.rubrics || []).length > 0 ? q.rubrics.map((r: any, j: number) => ({
                id: Date.now() + j + 100,
                name: r.name || "",
                description: r.description || "",
                score: String(r.score || ""),
              })) : [{ id: Date.now() + 100, name: "", description: "", score: "" }],
              gradingTone: "moderate",
              isExpanded: false,
            })));
          }
        }
      } catch (err) {
        toast.error("ไม่สามารถโหลดข้อมูลข้อสอบ");
      } finally {
        setIsLoading(false);
      }
    };
    fetchExam();
  }, [token, roomId, examId]);

  // Draft loading
  useEffect(() => {
    if (isLoading) return;
    const savedDraft = localStorage.getItem(DRAFT_KEY);
    if (savedDraft) {
      try {
        const draft = JSON.parse(savedDraft);
        // Compare loosely to see if draft is significantly different
        if (draft.examTitle !== examTitle || draft.questions?.length !== questions.length) {
            setDraftToRestore(draft);
        }
      } catch (e) { /* ignore */ }
    }
  }, [isLoading, DRAFT_KEY]); // Dependencies should not cause infinite loop since isLoading changes once

  const confirmRestoreDraft = () => {
    if (!draftToRestore) return;
    if (draftToRestore.examTitle) setExamTitle(draftToRestore.examTitle);
    setExamDescription(draftToRestore.examDescription || "");
    setStartDateTime(draftToRestore.startDateTime || "");
    setEndDateTime(draftToRestore.endDateTime || "");
    setIsRandomized(draftToRestore.isRandomized || false);
    if (draftToRestore.questions && draftToRestore.questions.length > 0) setQuestions(draftToRestore.questions);
    toast.success("กู้คืนข้อมูลร่างแล้ว");
    setDraftToRestore(null);
  };

  const rejectRestoreDraft = () => {
    localStorage.removeItem(DRAFT_KEY);
    setDraftToRestore(null);
  };

  // Save Draft
  useEffect(() => {
    if (isLoading) return;
    if (isInitialLoad.current) {
      isInitialLoad.current = false;
      return;
    }
    setIsDirty(true);
    const draft = { examTitle, examDescription, startDateTime, endDateTime, isRandomized, questions };
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  }, [examTitle, examDescription, startDateTime, endDateTime, isRandomized, questions, isLoading, DRAFT_KEY]);

  const updateQuestion = (id: number, patch: Partial<Question>) =>
    setQuestions(prev => prev.map(q => q.id === id ? { ...q, ...patch } : q));

  const addRubric = (qId: number) =>
    setQuestions(prev => prev.map(q => q.id === qId
      ? { ...q, rubrics: [...q.rubrics, { id: Date.now() + Math.random(), name: "", description: "", score: "" }] }
      : q));

  const removeRubric = (qId: number, rId: number) =>
    setQuestions(prev => prev.map(q => q.id === qId
      ? { ...q, rubrics: q.rubrics.filter(r => r.id !== rId) }
      : q));

  const updateRubric = (qId: number, rId: number, patch: Partial<RubricItem>) =>
    setQuestions(prev => prev.map(q => q.id === qId
      ? { ...q, rubrics: q.rubrics.map(r => r.id === rId ? { ...r, ...patch } : r) }
      : q));

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>, qId: number) => {
    const files = e.target.files;
    if (!files) return;
    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () =>
        setQuestions(prev => prev.map(q => q.id === qId
          ? { ...q, questionImages: [...q.questionImages, reader.result as string] }
          : q));
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (qId: number, idx: number) =>
    setQuestions(prev => prev.map(q => q.id === qId
      ? { ...q, questionImages: q.questionImages.filter((_, i) => i !== idx) }
      : q));

  const duplicateQuestion = (qId: number) => {
    const src = questions.find(q => q.id === qId);
    if (!src) return;
    setQuestions(prev => {
      const idx = prev.findIndex(q => q.id === qId);
      const newQs = [...prev];
      newQs.splice(idx + 1, 0, {
        ...src,
        id: Date.now() + Math.random(),
        rubrics: src.rubrics.map(r => ({ ...r, id: Date.now() + Math.random() })),
      });
      return newQs;
    });
  };

  const generateRubric = async (qId: number) => {
    const q = questions.find(x => x.id === qId);
    if (!q) return;
    if (!q.text.trim() && q.questionImages.length === 0) {
      toast.error("กรอกโจทย์หรือแนบรูปก่อน"); return;
    }
    if (!parseFloat(q.score) || parseFloat(q.score) <= 0) {
      toast.error("ระบุคะแนนเต็มก่อน"); return;
    }
    updateQuestion(qId, { isGenerating: true });
    try {
      const imagesToSend = q.questionImages.map(img => {
        if (img.startsWith(window.location.origin)) return img.replace(window.location.origin, "");
        return img;
      });

      const res = await fetch("/api/gemini/generate-rubric", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ question_text: q.text, total_score: parseFloat(q.score), question_images_base64: imagesToSend, tone: q.gradingTone }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "AI Error");
      const data = await res.json();
      updateQuestion(qId, {
        answerKey: data.answer_key || "",
        rubrics: data.rubrics?.map((r: any, i: number) => ({ id: Date.now() + i, name: r.name || "", description: r.description || "", score: String(r.score || 0) })) || q.rubrics,
        isGenerating: false,
        isExpanded: true,
      });
      toast.success("AI สร้างเกณฑ์สำเร็จ!");
    } catch (e: any) {
      toast.error(e.message);
      updateQuestion(qId, { isGenerating: false });
    }
  };

  const saveRubricPreset = () => {
    if (showPresetModal === null || !presetNameInput.trim()) return;
    const q = questions.find(x => x.id === showPresetModal);
    if (!q || q.rubrics.length === 0) return;
    
    const newPreset = {
      id: Date.now().toString(),
      name: presetNameInput.trim(),
      rubrics: q.rubrics.map(r => ({ ...r, id: Date.now() + Math.random() }))
    };
    setRubricPresets(prev => [...prev, newPreset]);
    toast.success("บันทึกเทมเพลตเกณฑ์สำเร็จ");
    setShowPresetModal(null);
    setPresetNameInput("");
  };

  const applyRubricPreset = (qId: number, presetId: string) => {
    const preset = rubricPresets.find(p => p.id === presetId);
    if (!preset) return;
    updateQuestion(qId, { 
      rubrics: preset.rubrics.map(r => ({ ...r, id: Date.now() + Math.random() })) 
    });
    toast.success("นำเทมเพลตเกณฑ์มาใช้แล้ว");
  };

  const deleteRubricPreset = () => {
    if (!presetToDelete) return;
    setRubricPresets(prev => prev.filter(p => p.id !== presetToDelete));
    setPresetToDelete(null);
    toast.success("ลบเทมเพลตสำเร็จ");
  };

  const importFromBank = (bq: any) => {
    setQuestions(prev => [...prev, {
      id: Date.now() + Math.random(),
      text: bq.text,
      score: String(bq.score),
      questionImages: [],
      answerKey: bq.answer_key || "",
      rubrics: bq.rubrics?.map((r: any) => ({ id: Date.now() + Math.random(), name: r.name || "", description: r.description || "", score: String(r.score || 0) })) || [{ id: Date.now(), name: "", description: "", score: "" }],
      gradingTone: "moderate",
      isExpanded: false,
    }]);
    setShowBankModal(false);
    toast.success("นำเข้าคำถามสำเร็จ");
  };

  const handleSave = async () => {
    const validQs = questions.filter(q => q.text.trim() || q.questionImages.length > 0);
    if (!validQs.length) { toast.error("เพิ่มคำถามอย่างน้อยหนึ่งข้อ"); return; }
    setIsSaving(true);
    const total = validQs.reduce((s, q) => s + (parseFloat(q.score) || 0), 0);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          title: examTitle.trim() || (validQs[0].text.slice(0, 50) || "ข้อสอบใหม่"),
          description: examDescription || null,
          total_score: total,
          start_date: startDateTime && startDateTime !== "" ? new Date(startDateTime).toISOString() : null,
          end_date: endDateTime && endDateTime !== "" ? new Date(endDateTime).toISOString() : null,
          is_randomized: isRandomized ? 1 : 0,
          questions: validQs.map((q, i) => ({
            text: q.text, score: parseFloat(q.score) || 0,
            answer_key: q.answerKey || null,
            rubrics: q.rubrics.filter(r => r.name).map(r => ({ name: r.name, description: r.description, score: parseFloat(r.score) || 0 })),
            order_index: i,
            question_images_base64: q.questionImages.length > 0 ? q.questionImages : null,
          })),
        }),
      });
      if (res.ok) {
        toast.success("บันทึกการแก้ไขสำเร็จ!");
        localStorage.removeItem(DRAFT_KEY);
        setIsDirty(false);
        navigate(`/room/${roomId}`);
      } else {
        toast.error((await res.json()).detail || "บันทึกไม่สำเร็จ");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsSaving(false);
    }
  };

  const onBack = () => {
    if (isDirty) {
      setShowExitModal(true);
    } else {
      navigate(`/room/${roomId}`);
    }
  };

  const confirmExit = () => {
    localStorage.removeItem(DRAFT_KEY);
    navigate(`/room/${roomId}`);
  };

  const totalScore = questions.reduce((s, q) => s + (parseFloat(q.score) || 0), 0);

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center bg-[#F9FBFD] dark:bg-[#111111]"><Loader2 className="animate-spin text-blue-500 h-8 w-8" /></div>;
  }

  return (
    <div className="min-h-screen bg-[#F9FBFD] dark:bg-[#111111] transition-colors duration-200 font-sans">
      {/* Docs-style Toolbar */}
      <div className="sticky top-0 z-40 bg-[#EDF2FA] dark:bg-[#1E1E1E] border-b border-gray-300 dark:border-gray-800 px-2 sm:px-4 py-2 flex items-center justify-between gap-2 sm:gap-4">
        <div className="flex items-center gap-1 sm:gap-2 min-w-0">
          <button onClick={onBack} className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full text-gray-600 dark:text-gray-300 transition-colors shrink-0" title="กลับ">
            <ArrowLeft size={20} />
          </button>
          <div className="flex flex-col min-w-0">
            <input
              type="text"
              value={examTitle}
              onChange={e => setExamTitle(e.target.value)}
              className="bg-transparent border-none focus:bg-white dark:focus:bg-gray-800 focus:ring-1 focus:ring-blue-500 rounded px-2 py-0.5 text-base sm:text-lg text-gray-800 dark:text-gray-100 font-medium placeholder-gray-400 w-full"
              placeholder="ชื่อข้อสอบ..."
            />
            <div className="flex items-center gap-2 sm:gap-4 px-2 mt-0.5 text-[10px] sm:text-xs text-gray-500 dark:text-gray-400 truncate">
              <span className="flex items-center gap-1 shrink-0"><Check size={12} className="hidden sm:block" /> {isDirty ? "บันทึกร่างแล้ว" : "ข้อมูลล่าสุด"}</span>
              <span className="font-medium text-blue-600 dark:text-blue-400 shrink-0">คะแนน: {totalScore}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          <div className="hidden sm:block">
            <ThemeToggle />
          </div>
          <div className="hidden sm:block w-px h-6 bg-gray-300 dark:bg-gray-700 mx-1"></div>
          
          <button
            onClick={() => setShowSettings(true)}
            className="flex items-center gap-1.5 p-1.5 sm:px-3 sm:py-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded transition-colors"
            title="การตั้งค่า"
          >
            <Settings size={18} className="shrink-0" />
            <span className="text-[11px] sm:text-sm font-medium whitespace-nowrap">การตั้งค่า</span>
          </button>
          
          <button
            onClick={() => { setShowBankModal(true); fetchBank(); }}
            className="flex items-center gap-1.5 p-1.5 sm:px-3 sm:py-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded transition-colors"
            title="คลังข้อสอบ"
          >
            <BookOpen size={18} className="shrink-0" />
            <span className="text-[11px] sm:text-sm font-medium whitespace-nowrap">คลังข้อสอบ</span>
          </button>
          
          <Button onClick={handleSave} disabled={isSaving} className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-4 sm:px-5 h-8 sm:h-9 text-xs sm:text-sm font-medium shadow-sm ml-1 sm:ml-2 shrink-0">
            {isSaving ? <Loader2 size={16} className="animate-spin" /> : "บันทึก"}
          </Button>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-md flex flex-col border border-gray-200 dark:border-gray-800">
            <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-800">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Settings size={16} /> การตั้งค่าหน้ากระดาษ
              </h3>
              <button onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <X size={18} />
              </button>
            </div>
            <div className="p-5 space-y-5">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">วันและเวลาที่เริ่มสอบ (ไม่บังคับ)</label>
                  <div className="flex gap-1.5">
                    <button onClick={() => setQuickStart("now")} className="text-[10px] bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-gray-600 dark:text-gray-400 hover:text-blue-600 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700 transition-colors">ตอนนี้</button>
                    <button onClick={() => setQuickStart("tomorrow")} className="text-[10px] bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-gray-600 dark:text-gray-400 hover:text-blue-600 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700 transition-colors">พรุ่งนี้เช้า</button>
                  </div>
                </div>
                <Input type="datetime-local" value={startDateTime} onChange={e => setStartDateTime(e.target.value)} className="h-10 text-sm bg-gray-50 dark:bg-gray-950 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white [color-scheme:dark]" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">วันและเวลาที่สิ้นสุด (ไม่บังคับ)</label>
                  <div className="flex gap-1.5">
                    <button onClick={() => setQuickEnd(30)} className="text-[10px] bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-gray-600 dark:text-gray-400 hover:text-blue-600 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700 transition-colors">+30น.</button>
                    <button onClick={() => setQuickEnd(60)} className="text-[10px] bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-gray-600 dark:text-gray-400 hover:text-blue-600 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700 transition-colors">+1ชม.</button>
                    <button onClick={() => setQuickEnd(120)} className="text-[10px] bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-gray-600 dark:text-gray-400 hover:text-blue-600 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700 transition-colors">+2ชม.</button>
                    <button onClick={() => setQuickEnd(1440)} className="text-[10px] bg-gray-100 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-gray-600 dark:text-gray-400 hover:text-blue-600 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700 transition-colors">+1วัน</button>
                  </div>
                </div>
                <Input type="datetime-local" value={endDateTime} onChange={e => setEndDateTime(e.target.value)} className="h-10 text-sm bg-gray-50 dark:bg-gray-950 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white [color-scheme:dark]" />
              </div>
              <div className="flex items-center justify-between pt-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">สุ่มลำดับข้อสอบ</label>
                <button
                  onClick={() => setIsRandomized(!isRandomized)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${isRandomized ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-700"}`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${isRandomized ? "translate-x-6" : "translate-x-1"}`} />
                </button>
              </div>
            </div>
            <div className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-end">
              <Button onClick={() => setShowSettings(false)} className="bg-blue-600 hover:bg-blue-700 text-white px-6">ตกลง</Button>
            </div>
          </div>
        </div>
      )}

      {/* Question Bank Modal */}
      {showBankModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-lg max-h-[80vh] flex flex-col border border-gray-200 dark:border-gray-800">
            <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-800">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <BookOpen size={16} className="text-blue-500" /> คลังข้อสอบ
              </h3>
              <button onClick={() => setShowBankModal(false)} className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300">
                <X size={18} />
              </button>
            </div>
            <div className="p-3 border-b border-gray-100 dark:border-gray-800">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" />
                <input
                  value={bankSearch} onChange={e => setBankSearch(e.target.value)}
                  placeholder="ค้นหาคำถาม..."
                  className="w-full pl-8 pr-3 h-9 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-950 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-500 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            <div className="overflow-y-auto flex-1 p-3 space-y-2">
              {bankQuestions.filter(q => q.text.toLowerCase().includes(bankSearch.toLowerCase())).length === 0 ? (
                <p className="text-center text-gray-400 dark:text-gray-500 py-8 text-sm">ไม่พบคำถาม</p>
              ) : bankQuestions.filter(q => q.text.toLowerCase().includes(bankSearch.toLowerCase())).map(bq => (
                <div key={bq.id} className="flex items-start gap-3 p-3 rounded-lg border border-gray-100 dark:border-gray-800 hover:border-blue-200 dark:hover:border-blue-800 hover:bg-blue-50/30 dark:hover:bg-blue-900/20 transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-800 dark:text-gray-200 line-clamp-2">{bq.text}</p>
                    <span className="text-xs text-blue-600 dark:text-blue-400 font-medium mt-1 block">{bq.score} คะแนน</span>
                  </div>
                  <button onClick={() => importFromBank(bq)} className="shrink-0 text-xs font-medium px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                    เพิ่ม
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Preset Name Modal */}
      {showPresetModal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-sm flex flex-col border border-gray-200 dark:border-gray-800">
            <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-800">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <BookmarkPlus size={16} className="text-blue-500" /> บันทึกเทมเพลตเกณฑ์
              </h3>
              <button onClick={() => setShowPresetModal(null)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <X size={18} />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">ตั้งชื่อเทมเพลตเกณฑ์การให้คะแนนนี้</label>
              <Input
                value={presetNameInput}
                onChange={e => setPresetNameInput(e.target.value)}
                placeholder="เช่น เกณฑ์การเขียนเรียงความ..."
                autoFocus
                onKeyDown={e => { if (e.key === 'Enter') saveRubricPreset(); }}
              />
            </div>
            <div className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-end gap-2">
              <Button onClick={() => setShowPresetModal(null)} variant="outline" className="text-gray-600 dark:text-gray-300">ยกเลิก</Button>
              <Button onClick={saveRubricPreset} className="bg-blue-600 hover:bg-blue-700 text-white">บันทึก</Button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Preset Confirm Modal */}
      {presetToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-sm flex flex-col border border-gray-200 dark:border-gray-800">
            <div className="p-6 text-center space-y-4">
              <div className="mx-auto w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <Trash2 size={24} className="text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">ยืนยันการลบเทมเพลต</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                คุณแน่ใจหรือไม่ว่าต้องการลบเทมเพลตนี้? การกระทำนี้ไม่สามารถย้อนกลับได้
              </p>
            </div>
            <div className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-center gap-3">
              <Button onClick={() => setPresetToDelete(null)} variant="outline" className="flex-1 text-gray-600 dark:text-gray-300">ยกเลิก</Button>
              <Button onClick={deleteRubricPreset} className="flex-1 bg-red-600 hover:bg-red-700 text-white">ลบเทมเพลต</Button>
            </div>
          </div>
        </div>
      )}

      {/* Draft Restore Modal */}
      {draftToRestore && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-sm flex flex-col border border-gray-200 dark:border-gray-800">
            <div className="p-6 text-center space-y-4">
              <div className="mx-auto w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                <Check size={24} className="text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">พบข้อมูลร่างที่บันทึกไว้</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                คุณมีข้อมูลที่แก้ไขค้างไว้จากครั้งก่อน ต้องการกู้คืนเพื่อทำต่อหรือไม่?
              </p>
            </div>
            <div className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-center gap-3">
              <Button onClick={rejectRestoreDraft} variant="outline" className="flex-1 text-gray-600 dark:text-gray-300">เริ่มใหม่ทั้งหมด</Button>
              <Button onClick={confirmRestoreDraft} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white">กู้คืนข้อมูล</Button>
            </div>
          </div>
        </div>
      )}

      {/* Exit Without Saving Modal */}
      {showExitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-sm flex flex-col border border-gray-200 dark:border-gray-800">
            <div className="p-6 text-center space-y-4">
              <div className="mx-auto w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                <ArrowLeft size={24} className="text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">ยกเลิกการแก้ไข?</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                คุณมีการเปลี่ยนแปลงที่ยังไม่ได้บันทึก หากออกจากหน้านี้ ข้อมูลที่แก้ไขจะถูกลบทิ้งทั้งหมด ยืนยันหรือไม่?
              </p>
            </div>
            <div className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-center gap-3">
              <Button onClick={() => setShowExitModal(false)} variant="outline" className="flex-1 text-gray-600 dark:text-gray-300">แก้ไขต่อ</Button>
              <Button onClick={confirmExit} className="flex-1 bg-orange-600 hover:bg-orange-700 text-white">ทิ้งการแก้ไข</Button>
            </div>
          </div>
        </div>
      )}

      {/* Docs Canvas (The Paper) */}
      <div className="py-4 sm:py-8 px-2 sm:px-8">
        <div className="max-w-[816px] mx-auto bg-white dark:bg-[#1E1E1E] shadow-sm border border-gray-300 dark:border-gray-800 min-h-screen sm:min-h-[1056px] p-4 sm:p-16 flex flex-col gap-6 sm:gap-8 rounded-sm">
          
          {/* Document Header */}
          <div className="border-b-2 border-gray-900 dark:border-white pb-6 mb-2">
            <AutoResizingTextarea
              value={examDescription}
              onChange={(e: any) => setExamDescription(e.target.value)}
              placeholder="เพิ่มคำอธิบายข้อสอบ หรือคำชี้แจง (Optional)..."
              className="w-full text-center text-base text-gray-600 dark:text-gray-400 bg-transparent border-none focus:ring-0 resize-none px-0 py-1 italic"
            />
          </div>

          {/* Questions Stream */}
          <div className="space-y-8">
            {questions.map((q, index) => (
              <div key={q.id} className="group relative flex flex-col sm:flex-row gap-2 sm:gap-4 pl-0 sm:pl-4 border-l-4 border-transparent sm:hover:border-blue-200 dark:sm:hover:border-blue-900/50 transition-colors sm:-ml-5 pr-0 sm:pr-4 py-2">


                {/* Floating Actions (Left Margin - Desktop) */}
                <div className="hidden sm:flex absolute -left-12 top-1 flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                  <button onClick={() => duplicateQuestion(q.id)} className="p-2.5 text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 bg-white dark:bg-[#252525] shadow-md hover:shadow-lg border border-gray-200 dark:border-gray-700 rounded-full transition-all hover:scale-110" title="คัดลอกข้อนี้">
                    <Copy size={16} />
                  </button>
                  {questions.length > 1 && (
                    <button onClick={() => setQuestions(prev => prev.filter(x => x.id !== q.id))} className="p-2.5 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 bg-white dark:bg-[#252525] shadow-md hover:shadow-lg border border-gray-200 dark:border-gray-700 rounded-full transition-all hover:scale-110" title="ลบข้อนี้">
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>

                {/* Mobile Header (Number + Actions) */}
                <div className="flex flex-row items-center gap-2 sm:hidden mb-1">
                  <div className="font-medium text-lg text-gray-900 dark:text-gray-100 shrink-0">
                    {index + 1}.
                  </div>
                  <div className="flex flex-row gap-1.5 ml-auto">
                    <button onClick={() => duplicateQuestion(q.id)} className="p-1.5 text-gray-400 hover:text-blue-600 dark:text-gray-500 dark:hover:text-blue-400 bg-gray-50 dark:bg-gray-800/50 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-md transition-colors" title="คัดลอกข้อนี้">
                      <Copy size={16} />
                    </button>
                    {questions.length > 1 && (
                      <button onClick={() => setQuestions(prev => prev.filter(x => x.id !== q.id))} className="p-1.5 text-gray-400 hover:text-red-600 dark:text-gray-500 dark:hover:text-red-400 bg-gray-50 dark:bg-gray-800/50 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-md transition-colors" title="ลบข้อนี้">
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>

                {/* Desktop Number */}
                <div className="hidden sm:block font-medium text-lg text-gray-900 dark:text-gray-100 pt-0.5 min-w-[24px]">
                  {index + 1}.
                </div>

                <div className="flex-1 space-y-4">
                  {/* Question Text & Score inline */}
                  <div className="flex gap-4 items-start">
                    <AutoResizingTextarea
                      value={q.text}
                      onChange={(e: any) => updateQuestion(q.id, { text: e.target.value })}
                      placeholder="พิมพ์โจทย์คำถาม..."
                      className="flex-1 text-lg text-gray-900 dark:text-gray-100 bg-transparent border-none focus:ring-0 px-0 py-0 font-medium leading-relaxed"
                    />
                    <div className="shrink-0 flex items-center gap-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 px-2 py-1 rounded-md opacity-50 group-hover:opacity-100 transition-opacity">
                      <Input
                        type="number"
                        value={q.score}
                        onChange={e => updateQuestion(q.id, { score: e.target.value })}
                        className="w-12 h-6 text-center text-sm font-semibold bg-transparent border-none focus:ring-0 px-0"
                      />
                      <span className="text-xs text-gray-500">คะแนน</span>
                    </div>
                  </div>

                  {/* Images */}
                  {q.questionImages.length > 0 && (
                    <div className="flex flex-wrap gap-3">
                      {q.questionImages.map((img, i) => (
                        <div key={i} className="relative group/img max-w-[200px] rounded-sm overflow-hidden border border-gray-300 dark:border-gray-700">
                          <img src={img} alt="" className="w-full h-auto object-contain" />
                          <button
                            onClick={() => removeImage(q.id, i)}
                            className="absolute top-1 right-1 bg-black/50 hover:bg-black/80 text-white rounded-full p-1 opacity-0 group-hover/img:opacity-100 transition-opacity"
                          >
                            <X size={12} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Tools below question */}
                  <div className={`flex flex-wrap items-center gap-2 sm:gap-3 pt-2 transition-opacity ${q.isExpanded ? 'opacity-100' : 'opacity-100 sm:opacity-0 group-hover:opacity-100'}`}>
                    <input type="file" id={`img-${q.id}`} className="hidden" accept="image/*" multiple onChange={e => handleImageUpload(e, q.id)} />
                    <button onClick={() => document.getElementById(`img-${q.id}`)?.click()} className="flex items-center gap-1.5 text-[11px] sm:text-xs text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 px-3 py-1.5 rounded-full transition-colors font-medium">
                      <ImageIcon size={13} /> แนบรูปภาพ
                    </button>
                    <button onClick={() => updateQuestion(q.id, { isExpanded: !q.isExpanded })} className="flex items-center gap-1.5 text-[11px] sm:text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 px-3 py-1.5 rounded-full transition-colors font-medium">
                      {q.isExpanded ? "ซ่อนเฉลย/เกณฑ์" : "ตั้งค่าเฉลยและเกณฑ์"}
                    </button>
                  </div>

                  {/* Answer Key & Rubrics Area */}
                  {q.isExpanded && (
                    <div className="mt-4 ml-0 sm:ml-2 pl-3 sm:pl-4 border-l-2 border-blue-200 dark:border-blue-800 space-y-6 animate-in fade-in slide-in-from-top-2 duration-300 py-1">
                      
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                          แนวคำตอบ <span className="font-normal text-gray-400 text-[10px]">(Optional)</span>
                        </label>
                        <AutoResizingTextarea
                          value={q.answerKey}
                          onChange={(e: any) => updateQuestion(q.id, { answerKey: e.target.value })}
                          placeholder="พิมพ์ธงคำตอบสำหรับข้อนี้..."
                          className="w-full text-sm bg-gray-50/50 dark:bg-gray-900/30 border border-gray-200 dark:border-gray-800 focus:bg-white dark:focus:bg-gray-900 focus:ring-1 focus:ring-blue-400 rounded-lg p-3 transition-colors text-gray-800 dark:text-gray-200"
                          minRows={2}
                        />
                      </div>

                      <div className="space-y-3">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">เกณฑ์ให้คะแนน (Rubrics)</label>
                          <div className="flex items-center gap-2 w-full sm:w-auto">
                            <div className="flex items-center bg-gray-50 dark:bg-gray-800/80 rounded-lg p-1 border border-gray-200 dark:border-gray-700 w-full sm:w-auto">
                              <span className="text-[10px] text-gray-500 pl-2 pr-1 uppercase font-semibold hidden sm:inline">AI TONE:</span>
                              <select
                                value={q.gradingTone}
                                onChange={e => updateQuestion(q.id, { gradingTone: e.target.value as any })}
                                className="text-xs border-none bg-transparent text-gray-700 dark:text-gray-300 py-1 pl-1 pr-6 focus:ring-0 cursor-pointer font-medium flex-1 sm:flex-none"
                              >
                                <option value="simple">เรียบง่าย</option>
                                <option value="moderate">ปานกลาง</option>
                                <option value="academic">วิชาการ</option>
                              </select>
                              <div className="w-px h-4 bg-gray-300 dark:bg-gray-600 mx-1"></div>
                              <button
                                onClick={() => generateRubric(q.id)}
                                disabled={q.isGenerating}
                                className="flex items-center justify-center gap-1.5 text-xs font-medium px-3 py-1 bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 rounded-md shadow-sm hover:bg-purple-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 border border-gray-100 dark:border-gray-600 flex-1 sm:flex-none"
                              >
                                {q.isGenerating ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                                <span className="truncate">ให้ AI ช่วยเขียน</span>
                              </button>
                            </div>
                          </div>
                        </div>

                        <div className="bg-white dark:bg-[#1A1A1A] border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden shadow-sm">
                          {/* Header row - Hidden on mobile */}
                          <div className="hidden sm:flex bg-gray-50/80 dark:bg-gray-900/80 border-b border-gray-200 dark:border-gray-800 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
                            <div className="w-10 text-center py-2 border-r border-gray-200 dark:border-gray-800">#</div>
                            <div className="flex-[1.5] px-3 py-2 border-r border-gray-200 dark:border-gray-800">หัวข้อเกณฑ์</div>
                            <div className="flex-[3] px-3 py-2 border-r border-gray-200 dark:border-gray-800">คำอธิบายรายละเอียด</div>
                            <div className="w-20 px-3 py-2 text-center">คะแนน</div>
                            <div className="w-10"></div>
                          </div>
                          
                          <div className="divide-y divide-gray-100 dark:divide-gray-800/60">
                            {q.rubrics.map((r, rIdx) => (
                              <div key={r.id} className="flex flex-col sm:flex-row gap-0 items-stretch group/row bg-white dark:bg-transparent hover:bg-gray-50/50 dark:hover:bg-gray-900/20 transition-colors p-3 sm:p-0 relative">
                                <div className="hidden sm:flex w-10 shrink-0 items-center justify-center text-xs font-medium text-gray-400 border-r border-gray-100 dark:border-gray-800">
                                  {rIdx + 1}
                                </div>
                                <div className="flex flex-col sm:flex-row flex-1">
                                  <div className="flex-[1.5] border-b sm:border-b-0 sm:border-r border-gray-100 dark:border-gray-800">
                                    <label className="sm:hidden text-[10px] font-bold text-gray-400 uppercase mb-1 block">หัวข้อเกณฑ์</label>
                                    <Input
                                      value={r.name}
                                      onChange={e => updateRubric(q.id, r.id, { name: e.target.value })}
                                      placeholder="เช่น ความถูกต้อง"
                                      className="h-8 sm:h-10 text-xs border-none rounded-none focus:ring-0 bg-transparent w-full text-gray-800 dark:text-gray-200 px-0 sm:px-3"
                                    />
                                  </div>
                                  <div className="flex-[3] border-b sm:border-b-0 sm:border-r border-gray-100 dark:border-gray-800 pt-2 sm:pt-0">
                                    <label className="sm:hidden text-[10px] font-bold text-gray-400 uppercase mb-1 block">คำอธิบายรายละเอียด</label>
                                    <Input
                                      value={r.description}
                                      onChange={e => updateRubric(q.id, r.id, { description: e.target.value })}
                                      placeholder="คำอธิบาย (ถ้ามี)"
                                      className="h-8 sm:h-10 text-xs border-none rounded-none focus:ring-0 bg-transparent w-full text-gray-600 dark:text-gray-400 px-0 sm:px-3"
                                    />
                                  </div>
                                  <div className="w-full sm:w-20 pt-2 sm:pt-0">
                                    <label className="sm:hidden text-[10px] font-bold text-gray-400 uppercase mb-1 block">คะแนน</label>
                                    <Input
                                      type="number"
                                      value={r.score}
                                      onChange={e => updateRubric(q.id, r.id, { score: e.target.value })}
                                      placeholder="0"
                                      className="h-8 sm:h-10 text-xs w-full sm:w-20 text-left sm:text-center font-medium border-none rounded-none focus:ring-0 bg-transparent text-gray-800 dark:text-gray-200 px-0 sm:px-3"
                                    />
                                  </div>
                                </div>
                                <button
                                  onClick={() => removeRubric(q.id, r.id)}
                                  disabled={q.rubrics.length === 1}
                                  className="absolute top-2 right-2 sm:static sm:w-10 shrink-0 flex items-center justify-center text-gray-300 hover:text-red-500 opacity-100 sm:opacity-0 sm:group-hover/row:opacity-100 transition-all disabled:opacity-0"
                                >
                                  <X size={14} />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="flex items-center flex-wrap gap-2 pt-2">
                          <button
                            onClick={() => addRubric(q.id)}
                            className="flex items-center gap-1.5 text-[11px] sm:text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 px-3 py-1.5 rounded-full transition-colors"
                          >
                            <Plus size={12} /> เพิ่มเกณฑ์
                          </button>
                          
                          <div className="hidden sm:block w-px h-4 bg-gray-300 dark:bg-gray-700 mx-1"></div>

                          <button onClick={() => { setShowPresetModal(q.id); setPresetNameInput(""); }} className="flex items-center gap-1.5 text-[11px] sm:text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 px-3 py-1.5 rounded-full transition-colors">
                            <BookmarkPlus size={12} /> บันทึกเทมเพลต
                          </button>

                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <button className="flex items-center gap-1.5 text-[11px] sm:text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 px-3 py-1.5 rounded-full transition-colors">
                                <Bookmark size={12} /> เลือกเทมเพลต <span className="hidden sm:inline">▼</span>
                              </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-56">
                              <DropdownMenuLabel>เทมเพลตเกณฑ์ของคุณ</DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              {rubricPresets.length === 0 ? (
                                <div className="p-3 text-xs text-gray-400 text-center">ยังไม่มีเทมเพลต</div>
                              ) : (
                                rubricPresets.map(preset => (
                                  <DropdownMenuItem key={preset.id} onClick={() => applyRubricPreset(q.id, preset.id)} className="flex justify-between items-center cursor-pointer group">
                                    <span className="truncate pr-2">{preset.name}</span>
                                    <button onClick={(e) => { e.stopPropagation(); setPresetToDelete(preset.id); }} className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">
                                      <X size={14} />
                                    </button>
                                  </DropdownMenuItem>
                                ))
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>

                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Add Page Break / Question Button */}
          <div className="pt-8 pb-4 mt-8 border-t border-dashed border-gray-300 dark:border-gray-700 text-center">
            <button
              onClick={() => setQuestions(prev => [...prev, newQuestion()])}
              className="inline-flex items-center justify-center gap-2 px-6 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 text-sm font-medium rounded-full transition-colors"
            >
              <Plus size={16} /> แทรกข้อต่อไป
            </button>
          </div>

        </div>
      </div>

    </div>
  );
}