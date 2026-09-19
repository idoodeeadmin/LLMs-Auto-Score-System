import { WorkspaceBreadcrumb } from "@/components/WorkspaceHeader";
import { useEffect, useRef, useState } from "react";
import { useBlocker, useParams, useNavigate } from "react-router-dom";
import { listDrafts, readDraft, writeDraft } from "@/lib/exam-drafts";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import {
  ArrowLeft,
  Plus,
  X,
  Loader2,
  Save,
  ImagePlus,
  Sparkles,
  ChevronDown,
  ChevronRight,
  Files,
  Trash2,
  Settings,
  Send,
  EyeOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { toast } from "sonner";

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
  answerKey: string;
  rubrics: RubricItem[];
  images?: { name: string; dataUrl: string }[];
  hideRubricFromStudents?: boolean;
}

interface ExamDraft {
  examTitle: string;
  examDescription: string;
  questions: Question[];
  startDateTime?: string;
  endDateTime?: string;
  isRandomized?: boolean;
  updatedAt?: string;
}

interface CloudExamDraft {
  id: number;
  title?: string | null;
  description?: string | null;
  updated_at?: string;
  start_date?: string | null;
  end_date?: string | null;
  is_randomized?: number;
  questions: Array<{
    text: string;
    score: number;
    answer_key?: string | null;
    rubrics?: Array<{ name?: string; description?: string; score?: number }>;
    question_images_base64?: string[];
    hide_rubric_from_students?: boolean;
  }>;
}

const toDateTimeLocal = (value?: string | null) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
};

const fromCloudDraft = (value: CloudExamDraft): ExamDraft => ({
  examTitle: value.title ?? "",
  examDescription: value.description ?? "",
  startDateTime: toDateTimeLocal(value.start_date),
  endDateTime: toDateTimeLocal(value.end_date),
  isRandomized: Boolean(value.is_randomized),
  updatedAt: value.updated_at,
  questions: value.questions.map((question, questionIndex) => ({
    id: Date.now() + questionIndex,
    text: question.text,
    score: String(question.score),
    answerKey: question.answer_key ?? "",
    rubrics: question.rubrics?.length ? question.rubrics.map((rubric, rubricIndex) => ({
      id: Date.now() + 1000 + questionIndex * 100 + rubricIndex,
      name: rubric.name ?? "",
      description: rubric.description ?? "",
      score: String(rubric.score ?? 0),
    })) : [{ id: Date.now() + 1000 + questionIndex, name: "", description: "", score: String(question.score) }],
    images: (question.question_images_base64 ?? []).map((url, imageIndex) => ({ name: `รูปประกอบ ${imageIndex + 1}`, dataUrl: url })),
    hideRubricFromStudents: Boolean(question.hide_rubric_from_students),
  })),
});

export default function CreateExam() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [readingImages, setReadingImages] = useState(false);
  const imageReadLock = useRef(false);

  const attachImages = async (questionId: number, files: File[]) => {
    if (!files.length || imageReadLock.current || isSaving) return;
    const question = questions.find(q => q.id === questionId);
    if (!question) return;
    if ((question.images?.length ?? 0) + files.length > 10) {
      toast.error("แนบรูปได้ไม่เกิน 10 รูปต่อข้อ");
      return;
    }
    if (files.some(file => !["image/jpeg", "image/png", "image/gif", "image/webp"].includes(file.type) || file.size > 5 * 1024 * 1024 || file.size === 0)) {
      toast.error("ใช้รูป JPG, PNG, GIF หรือ WebP ขนาดไม่เกิน 5 MB ต่อรูป");
      return;
    }
    imageReadLock.current = true;
    setReadingImages(true);
    try {
      const images = await Promise.all(files.map(file => new Promise<{ name: string; dataUrl: string }>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => typeof reader.result === "string"
          ? resolve({ name: file.name, dataUrl: reader.result }) : reject(new Error("อ่านรูปไม่สำเร็จ"));
        reader.onerror = () => reject(new Error("อ่านรูปไม่สำเร็จ"));
        reader.onabort = () => reject(new Error("ยกเลิกการอ่านรูป"));
        reader.readAsDataURL(file);
      })));
      setQuestions(current => current.map(q => q.id === questionId
        ? { ...q, images: [...(q.images ?? []), ...images] } : q));
    } catch {
      toast.error("อ่านไฟล์รูปไม่สำเร็จ กรุณาเลือกใหม่");
    } finally {
      imageReadLock.current = false;
      setReadingImages(false);
    }
  };

  const [examTitle, setExamTitle] = useState("");
  const [examDescription, setExamDescription] = useState("");
  const [startDateTime, setStartDateTime] = useState("");
  const [endDateTime, setEndDateTime] = useState("");
  const [isRandomized, setIsRandomized] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const [questions, setQuestions] = useState<Question[]>([
    {
      id: 1,
      text: "",
      score: "5",
      answerKey: "",
      rubrics: [{ id: 101, name: "", description: "", score: "5" }],
    },
  ]);

  // Single collapsible state per question (controls both answer key and rubrics together)
  const [showDetails, setShowDetails] = useState<{ [qId: number]: boolean }>({
    1: false,
  });

  const totalScore = questions.reduce(
    (sum, q) => sum + (parseFloat(q.score) || 0),
    0,
  );
  const draftPrefix = `create-exam:${user?.id}:${roomId}:`;
  const legacyDraftKey = `create-exam:${user?.id}:${roomId}`;
  const [currentDraftId, setCurrentDraftId] = useState<string | null>(null);
  const [draftChoices, setDraftChoices] = useState<Array<{ id: string; draft: ExamDraft }>>([]);
  const [draftPickerOpen, setDraftPickerOpen] = useState(false);
  const snapshot = JSON.stringify({ examTitle, examDescription, questions, startDateTime, endDateTime, isRandomized });
  const [savedSnapshot, setSavedSnapshot] = useState(snapshot);
  const [draftLoaded, setDraftLoaded] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [generatingId, setGeneratingId] = useState<number | null>(null);
  const allowExit = useRef(false);
  const dirty = snapshot !== savedSnapshot;
  const blocker = useBlocker(() => !allowExit.current && (dirty || imageReadLock.current || generatingId !== null || isSaving));

  useEffect(() => {
    let active = true;
    const load = async () => {
      const requestedId = new URLSearchParams(window.location.search).get("draft");
      const startingNew = new URLSearchParams(window.location.search).has("new");
      let rows = await listDrafts<ExamDraft>(draftPrefix);
      const legacy = await readDraft<ExamDraft>(legacyDraftKey);
      if (legacy) {
        const migratedId = `draft-${Date.now()}`;
        const migrated = { ...legacy, updatedAt: legacy.updatedAt ?? new Date().toISOString() };
        await writeDraft(`${draftPrefix}${migratedId}`, migrated);
        await writeDraft(legacyDraftKey, undefined);
        rows.push({ key: `${draftPrefix}${migratedId}`, value: migrated });
      }
      let cloudChoices: Array<{ id: string; draft: ExamDraft }> = [];
      if (token) {
        try {
          const response = await fetch(`/api/rooms/${roomId}/exam-drafts`, { headers: { Authorization: `Bearer ${token}` } });
          if (response.ok) {
            const cloudRows: CloudExamDraft[] = await response.json();
            cloudChoices = cloudRows.map(row => ({ id: `cloud-${row.id}`, draft: fromCloudDraft(row) }));
          }
        } catch { /* Keep browser drafts available while offline. */ }
      }
      if (!active) return;
      const choices = [...cloudChoices, ...rows.map(row => ({ id: `local-${row.key.slice(draftPrefix.length)}`, draft: row.value }))]
        .sort((a, b) => new Date(b.draft.updatedAt ?? 0).getTime() - new Date(a.draft.updatedAt ?? 0).getTime());
      setDraftChoices(choices);
      if (requestedId) {
        const selected = choices.find(choice => choice.id === requestedId);
        if (selected) openDraft(selected.id, selected.draft, false);
        else toast.error("ไม่พบแบบร่างที่เลือก");
      } else if (!startingNew && choices.length === 1) {
        openDraft(choices[0].id, choices[0].draft, false);
      } else if (!startingNew && choices.length > 1) {
        setDraftPickerOpen(true);
      }
    };
    load().catch(() => { if (active) toast.error("อ่านแบบร่างไม่สำเร็จ"); })
      .finally(() => { if (active) setDraftLoaded(true); });
    return () => { active = false; };
  }, [draftPrefix, legacyDraftKey, roomId, token]);

  const openDraft = (id: string, draft: ExamDraft, notify = true) => {
    setCurrentDraftId(id);
    setExamTitle(draft.examTitle);
    setExamDescription(draft.examDescription);
    setStartDateTime(draft.startDateTime ?? "");
    setEndDateTime(draft.endDateTime ?? "");
    setIsRandomized(draft.isRandomized ?? false);
    setQuestions(draft.questions);
    setSavedSnapshot(JSON.stringify({ examTitle: draft.examTitle, examDescription: draft.examDescription, questions: draft.questions,
      startDateTime: draft.startDateTime ?? "", endDateTime: draft.endDateTime ?? "", isRandomized: draft.isRandomized ?? false }));
    setDraftPickerOpen(false);
    navigate(`/room/${roomId}/create-exam?draft=${encodeURIComponent(id)}`, { replace: true });
    if (notify) toast.info("เปิดแบบร่างแล้ว");
  };

  const startNewDraft = () => {
    setCurrentDraftId(null);
    setExamTitle("");
    setExamDescription("");
    setStartDateTime("");
    setEndDateTime("");
    setIsRandomized(false);
    const blank: Question[] = [{ id: Date.now(), text: "", score: "5", answerKey: "", rubrics: [{ id: Date.now() + 1, name: "", description: "", score: "5" }], hideRubricFromStudents: false }];
    setQuestions(blank);
    setSavedSnapshot(JSON.stringify({ examTitle: "", examDescription: "", questions: blank,
      startDateTime: "", endDateTime: "", isRandomized: false }));
    setDraftPickerOpen(false);
    navigate(`/room/${roomId}/create-exam?new=1`, { replace: true });
  };

  const deleteDraft = async (id: string, title: string) => {
    if (!window.confirm(`ลบแบบร่าง “${title || "ยังไม่ได้ตั้งชื่อ"}” ใช่หรือไม่`)) return;
    try {
      if (id.startsWith("cloud-")) {
        const response = await fetch(`/api/rooms/${roomId}/exam-drafts/${id.slice(6)}`, {
          method: "DELETE", headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error();
      } else {
        await writeDraft(`${draftPrefix}${id.slice(6)}`, undefined);
      }
      setDraftChoices(current => current.filter(choice => choice.id !== id));
      if (currentDraftId === id) startNewDraft();
      toast.success("ลบแบบร่างแล้ว");
    } catch {
      toast.error("ลบแบบร่างไม่สำเร็จ");
    }
  };

  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (!allowExit.current && (dirty || readingImages || generatingId !== null || isSaving)) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty, readingImages, generatingId, isSaving]);

  const saveDraft = async (leave = false) => {
    if (imageReadLock.current || generatingId !== null || isSaving) return;
    if (startDateTime && endDateTime && new Date(endDateTime) <= new Date(startDateTime)) {
      toast.error("เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มสอบ");
      setSettingsOpen(true);
      return;
    }
    setSavingDraft(true);
    try {
      const value: ExamDraft = { ...JSON.parse(snapshot), updatedAt: new Date().toISOString() };
      const payload = {
        title: value.examTitle || null,
        description: value.examDescription || null,
        start_date: value.startDateTime ? new Date(value.startDateTime).toISOString() : null,
        end_date: value.endDateTime ? new Date(value.endDateTime).toISOString() : null,
        is_randomized: value.isRandomized ? 1 : 0,
        questions: value.questions.map((question, index) => ({
          text: question.text,
          score: Number(question.score) || 0,
          answer_key: question.answerKey || null,
          rubrics: question.rubrics.filter(rubric => rubric.name.trim()).map(rubric => ({
            name: rubric.name, description: rubric.description, score: Number(rubric.score) || 0,
          })),
          order_index: index,
          question_images_base64: question.images?.map(image => image.dataUrl) ?? [],
          hide_rubric_from_students: Boolean(question.hideRubricFromStudents),
        })),
      };
      let id = currentDraftId;
      let savedValue = value;
      try {
        const cloudId = currentDraftId?.startsWith("cloud-") ? currentDraftId.slice(6) : null;
        const response = await fetch(`/api/rooms/${roomId}/exam-drafts${cloudId ? `/${cloudId}` : ""}`, {
          method: cloudId ? "PUT" : "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || "บันทึกแบบร่างออนไลน์ไม่สำเร็จ");
        id = `cloud-${result.id}`;
        savedValue = fromCloudDraft(result);
        if (currentDraftId?.startsWith("local-")) await writeDraft(`${draftPrefix}${currentDraftId.slice(6)}`, undefined);
      } catch (error) {
        if (currentDraftId?.startsWith("cloud-")) throw error;
        const localId = currentDraftId?.startsWith("local-") ? currentDraftId.slice(6) : `draft-${Date.now()}`;
        await writeDraft(`${draftPrefix}${localId}`, value);
        id = `local-${localId}`;
        toast.warning("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ จึงเก็บแบบร่างไว้ในเครื่องนี้ก่อน");
      }
      setQuestions(savedValue.questions);
      setStartDateTime(savedValue.startDateTime ?? "");
      setEndDateTime(savedValue.endDateTime ?? "");
      setIsRandomized(savedValue.isRandomized ?? false);
      setCurrentDraftId(id);
      setDraftChoices(current => [{ id: id!, draft: savedValue }, ...current.filter(choice => choice.id !== id && choice.id !== currentDraftId)]);
      navigate(`/room/${roomId}/create-exam?draft=${encodeURIComponent(id!)}`, { replace: true });
      setSavedSnapshot(JSON.stringify({ examTitle: savedValue.examTitle, examDescription: savedValue.examDescription, questions: savedValue.questions,
        startDateTime: savedValue.startDateTime ?? "", endDateTime: savedValue.endDateTime ?? "", isRandomized: savedValue.isRandomized ?? false }));
      toast.success(id?.startsWith("cloud-") ? "บันทึกแบบร่างลงบัญชีแล้ว" : "บันทึกแบบร่างในเครื่องนี้แล้ว");
      if (leave && blocker.state === "blocked") blocker.proceed();
    } catch {
      toast.error("บันทึกแบบร่างไม่สำเร็จ โปรดตรวจสอบพื้นที่จัดเก็บของเบราว์เซอร์");
    } finally { setSavingDraft(false); }
  };

  const generateRubric = async (question: Question) => {
    if (generatingId !== null || readingImages || isSaving) return;
    if (!question.text.trim() && !question.images?.length) {
      toast.error("กรอกโจทย์หรือแนบรูปก่อนสร้างเกณฑ์"); return;
    }
    const score = Number(question.score);
    if (!Number.isFinite(score) || score <= 0) { toast.error("ระบุคะแนนเต็มมากกว่า 0"); return; }
    if ((question.answerKey.trim() || question.rubrics.some(r => r.name.trim() || r.description.trim())) &&
      !window.confirm("สร้างเกณฑ์ใหม่แทนแนวคำตอบและเกณฑ์เดิมของข้อนี้หรือไม่?")) return;
    setGeneratingId(question.id);
    try {
      const response = await fetch("/api/ai/generate-rubric", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ question_text: question.text, total_score: score,
          question_images_base64: question.images?.map(image => image.dataUrl) ?? [], tone: "moderate" }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "สร้างเกณฑ์ไม่สำเร็จ");
      if (!Array.isArray(result.rubrics) || !result.rubrics.length) throw new Error("AI ไม่ส่งเกณฑ์กลับมา กรุณาลองใหม่");
      updateQuestion(question.id, {
        answerKey: result.answer_key || "",
        rubrics: result.rubrics.map((r: { name: string; description: string; score: number }, i: number) =>
          ({ id: Date.now() + i, name: r.name || "", description: r.description || "", score: String(r.score ?? 0) })),
      });
      setShowDetails(current => ({ ...current, [question.id]: true }));
      toast.success("สร้างเกณฑ์แล้ว กรุณาตรวจทานก่อนบันทึก");
    } catch (error) { toast.error(error instanceof Error ? error.message : "สร้างเกณฑ์ไม่สำเร็จ"); }
    finally { setGeneratingId(null); }
  };

  const updateQuestion = (id: number, patch: Partial<Question>) => {
    setQuestions((prev) =>
      prev.map((q) => (q.id === id ? { ...q, ...patch } : q)),
    );
  };

  const toggleDetails = (qId: number) => {
    setShowDetails((prev) => ({ ...prev, [qId]: !(prev[qId] ?? false) }));
  };

  const addRubric = (qId: number) => {
    setQuestions((prev) =>
      prev.map((q) =>
        q.id === qId
          ? {
              ...q,
              rubrics: [
                ...q.rubrics,
                {
                  id: Date.now() + Math.random(),
                  name: "",
                  description: "",
                  score: "1",
                },
              ],
            }
          : q,
      ),
    );
  };

  const removeRubric = (qId: number, rId: number) => {
    setQuestions((prev) =>
      prev.map((q) =>
        q.id === qId
          ? { ...q, rubrics: q.rubrics.filter((r) => r.id !== rId) }
          : q,
      ),
    );
  };

  const updateRubric = (
    qId: number,
    rId: number,
    patch: Partial<RubricItem>,
  ) => {
    setQuestions((prev) =>
      prev.map((q) =>
        q.id === qId
          ? {
              ...q,
              rubrics: q.rubrics.map((r) =>
                r.id === rId ? { ...r, ...patch } : r,
              ),
            }
          : q,
      ),
    );
  };

  const handleSave = async () => {
    if (isSaving || imageReadLock.current || generatingId !== null || savingDraft) return;
    if (questions.some(q => q.images?.length && !q.text.trim())) {
      toast.error("กรอกคำถามหรือคำชี้แจงให้ข้อที่แนบรูปก่อนบันทึก");
      return;
    }
    if (startDateTime && endDateTime && new Date(endDateTime) <= new Date(startDateTime)) {
      toast.error("เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มสอบ");
      setSettingsOpen(true);
      return;
    }
    const validQs = questions.filter((q) => q.text.trim());
    if (!validQs.length) {
      toast.error("เพิ่มคำถามอย่างน้อยหนึ่งข้อ");
      return;
    }
    setIsSaving(true);
    const total = validQs.reduce((s, q) => s + (parseFloat(q.score) || 0), 0);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title:
            examTitle.trim() || validQs[0].text.slice(0, 50) || "ข้อสอบใหม่",
          description: examDescription || null,
          total_score: total,
          start_date: startDateTime ? new Date(startDateTime).toISOString() : null,
          end_date: endDateTime ? new Date(endDateTime).toISOString() : null,
          is_randomized: isRandomized ? 1 : 0,
          questions: validQs.map((q, i) => ({
            text: q.text,
            score: parseFloat(q.score) || 0,
            answer_key: q.answerKey || null,
            rubrics: q.rubrics
              .filter((r) => r.name)
              .map((r) => ({
                name: r.name,
                description: r.description,
                score: parseFloat(r.score) || 0,
              })),
            order_index: i,
            question_images_base64: q.images?.length ? q.images.map(image => image.dataUrl) : null,
            hide_rubric_from_students: Boolean(q.hideRubricFromStudents),
          })),
          draft_id: currentDraftId?.startsWith("cloud-") ? Number(currentDraftId.slice(6)) : null,
        }),
      }).catch(() => null);

      if (res && res.ok) {
        allowExit.current = true;
        if (currentDraftId?.startsWith("local-")) await writeDraft(`${draftPrefix}${currentDraftId.slice(6)}`, undefined)
          .catch(() => toast.warning("สร้างข้อสอบแล้ว แต่ลบแบบร่างเก่าไม่สำเร็จ"));
        toast.success("สร้างข้อสอบสำเร็จ!");
        navigate(`/room/${roomId}`);
      } else {
        const err = await res?.json().catch(() => null);
        toast.error(err?.detail || "ไม่สามารถสร้างข้อสอบได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="workspace create-exam-page">
      {/* Clean Top Navbar */}
      <div className="task-header sticky top-0 z-40 flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-2.5 shadow-sm dark:border-slate-800 dark:bg-[#1E1E1E] sm:px-6">
        <div className="flex items-center gap-3 min-w-0">
          <button
            aria-label="กลับห้องเรียน"
            onClick={() => navigate(`/room/${roomId}`)}
            className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition"
          >
            <ArrowLeft size={18} />
          </button>
          <div className="task-header-title flex min-w-0 flex-col sm:w-[min(34rem,42vw)]">
            <input
              type="text"
              aria-label="ชื่อข้อสอบ"
              disabled={!draftLoaded || savingDraft || isSaving}
              value={examTitle}
              onChange={(e) => setExamTitle(e.target.value)}
              className="bg-transparent border-none focus:outline-none text-base font-bold text-slate-900 dark:text-white p-0"
              placeholder="ชื่อข้อสอบ (เช่น แบบทดสอบกลางภาค)..."
            />
            <span className="text-xs text-[#245b50] dark:text-[#91c7b8] font-medium">
              คะแนนเต็มรวม: {totalScore} คะแนน
            </span>
          </div>
        </div>

        <div className="task-header-actions flex shrink-0 items-center gap-1">
          <div className="create-exam-utilities flex items-center rounded-lg border border-border bg-muted/30 p-0.5">
            <div className="hidden sm:block"><ThemeToggle /></div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              title="การตั้งค่าข้อสอบ"
              aria-label="เปิดการตั้งค่าข้อสอบ"
              disabled={!draftLoaded || savingDraft || isSaving}
              onClick={() => setSettingsOpen(true)}
            >
              <Settings size={16} />
            </Button>
            <Button variant="ghost" size="icon" className="relative h-8 w-8" title="แบบร่างข้อสอบ" aria-label="เปิดแบบร่างข้อสอบ"
              disabled={!draftLoaded || savingDraft || isSaving}
              onClick={() => {
                if (dirty) { toast.info("บันทึกฉบับร่างปัจจุบันก่อนเปิดแบบร่างชุดอื่น"); return; }
                setDraftPickerOpen(true);
              }}>
              <Files size={16} />
              {draftChoices.length > 0 && (
                <span className="absolute -right-1 -top-1 min-w-4 rounded-full bg-primary px-1 text-center text-[9px] font-semibold leading-4 text-primary-foreground">
                  {draftChoices.length > 9 ? "9+" : draftChoices.length}
                </span>
              )}
            </Button>
          </div>
          <span className="mx-1 hidden h-6 w-px bg-border sm:block" aria-hidden="true" />
          <Button
            variant="outline"
            className="h-9 gap-1.5 rounded-lg px-3 text-xs"
            title="บันทึกแบบร่าง"
            disabled={!draftLoaded || savingDraft || isSaving || readingImages || generatingId !== null}
            onClick={() => saveDraft()}
          >
            {savingDraft ? <Loader2 size={15} className="animate-spin" /> : <Save size={15} />}
            <span className="hidden md:inline">{savingDraft ? "กำลังบันทึก…" : "บันทึกร่าง"}</span>
          </Button>
          <Button
            onClick={handleSave}
            title="เผยแพร่ข้อสอบ"
            aria-label="เผยแพร่ข้อสอบ"
            disabled={!draftLoaded || isSaving || readingImages || savingDraft || generatingId !== null}
            className="primary-action h-9 gap-1.5 rounded-lg px-3.5 text-xs"
          >
            {isSaving ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
            <span className="hidden sm:inline">{isSaving ? "กำลังเผยแพร่…" : "เผยแพร่"}</span>
          </Button>
        </div>
      </div>

      {/* Google Docs Paper Canvas */}
      <div className="document-page">
        <WorkspaceBreadcrumb roomId={roomId} current="สร้างข้อสอบ" />
        <h1 className="page-heading mb-2">สร้างข้อสอบ</h1>
        <p className="page-description mb-6">
          กำหนดคำถาม คะแนนเต็ม และเกณฑ์การให้คะแนนให้ครบก่อนบันทึก
        </p>
        <div className="work-summary">
          <span>{questions.length} ข้อ</span>
          <span>คะแนนเต็ม {totalScore} คะแนน</span>
          <span>{isRandomized ? "สุ่มลำดับข้อ" : "เรียงข้อตามที่สร้าง"}</span>
        </div>
        {(startDateTime || endDateTime) && (
          <p className="mb-4 text-xs text-muted-foreground">
            {startDateTime ? `เริ่ม ${new Intl.DateTimeFormat("th-TH", { dateStyle: "medium", timeStyle: "short" }).format(new Date(startDateTime))}` : "ไม่กำหนดเวลาเริ่ม"}
            {" · "}
            {endDateTime ? `สิ้นสุด ${new Intl.DateTimeFormat("th-TH", { dateStyle: "medium", timeStyle: "short" }).format(new Date(endDateTime))}` : "ไม่กำหนดเวลาสิ้นสุด"}
          </p>
        )}
        <p className="mb-4 text-xs text-muted-foreground">บันทึกฉบับร่างเพื่อเก็บข้อสอบทั้งชุด แล้วกลับมาแก้ต่อจากหน้าสร้างข้อสอบของห้องนี้</p>
        <fieldset disabled={!draftLoaded || isSaving || savingDraft || generatingId !== null} className="exam-paper min-w-0 space-y-8">
          {/* Header Description */}
          <div className="border-b border-slate-200 dark:border-slate-800 pb-4">
            <input
              type="text"
              aria-label="คำชี้แจงข้อสอบ"
              value={examDescription}
              onChange={(e) => setExamDescription(e.target.value)}
              placeholder="คำชี้แจงข้อสอบ (เช่น ให้นิสิตตอบคำถามและยกตัวอย่างประกอบให้ครบถ้วน)..."
              className="w-full text-sm text-slate-600 dark:text-slate-300 bg-transparent border-b border-slate-200 focus:outline-none py-3"
            />
          </div>

          {/* Flat Question Flow */}
          <div className="space-y-8">
            {questions.map((q, index) => {
              const isOpen = showDetails[q.id] ?? false;

              return (
                <div
                  key={q.id}
                  className="space-y-4 pb-8 border-b border-slate-100 dark:border-slate-800"
                >
                  {/* Question Header & Score */}
                  <div className="question-editor flex gap-3 items-start">
                    <span className="font-bold text-sm text-slate-900 dark:text-white pt-1">
                      {index + 1}.
                    </span>
                    <textarea
                      aria-label={`คำถามข้อที่ ${index + 1}`}
                      value={q.text}
                      onChange={(e) =>
                        updateQuestion(q.id, { text: e.target.value })
                      }
                      placeholder="พิมพ์โจทย์คำถาม..."
                      className="flex-1 text-sm text-slate-900 dark:text-white bg-transparent border-b border-slate-200 dark:border-slate-700 focus:border-[#1a73e8] focus:outline-none p-1 font-medium leading-relaxed resize-none"
                      rows={2}
                    />
                    <div className="question-score flex items-center gap-1 shrink-0 pt-1">
                      <input
                        type="number"
                        aria-label={`คะแนนเต็มข้อที่ ${index + 1}`}
                        min="0"
                        value={q.score}
                        onChange={(e) =>
                          updateQuestion(q.id, { score: e.target.value })
                        }
                        className="w-10 text-center text-xs font-bold bg-transparent border-b border-slate-200 dark:border-slate-700 focus:outline-none"
                      />
                      <span className="text-xs text-slate-400">คะแนน</span>
                    </div>
                  </div>

                  <div className="pl-6 space-y-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <label className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-muted focus-within:ring-2 focus-within:ring-ring">
                        <ImagePlus size={16} aria-hidden="true" />
                        แนบรูป
                        <input type="file" className="sr-only" multiple
                          aria-label={`แนบรูปโจทย์ข้อที่ ${index + 1}`}
                          accept="image/jpeg,image/png,image/gif,image/webp"
                          disabled={isSaving || readingImages || (q.images?.length ?? 0) >= 10}
                          onChange={event => {
                            const files = Array.from(event.target.files ?? []);
                            event.target.value = "";
                            void attachImages(q.id, files);
                          }} />
                      </label>
                      <Button type="button" variant="ghost" className="gap-2 text-sm text-primary"
                        disabled={readingImages || generatingId !== null} onClick={() => generateRubric(q)}>
                        {generatingId === q.id ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                        {generatingId === q.id ? "กำลังสร้างเกณฑ์…" : "สร้างเกณฑ์ด้วย AI"}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">แนบได้ 10 รูป · รูปละไม่เกิน 5 MB</p>
                    {readingImages && <p role="status" className="text-xs text-muted-foreground">กำลังเตรียมรูป…</p>}
                    {!!q.images?.length && <div className="flex flex-wrap gap-3">
                      {q.images?.map((image, imageIndex) => <figure key={imageIndex} className="relative w-36 rounded-lg border p-2">
                        <img src={image.dataUrl} alt={`รูปประกอบโจทย์ข้อ ${index + 1} รูปที่ ${imageIndex + 1}`} className="h-28 w-full object-contain" />
                        <figcaption className="mt-1 truncate text-xs text-muted-foreground">{image.name}</figcaption>
                        <button type="button" disabled={isSaving || readingImages}
                          aria-label={`ลบรูปที่ ${imageIndex + 1} ของข้อ ${index + 1}`}
                          onClick={() => updateQuestion(q.id, { images: q.images?.filter((_, i) => i !== imageIndex) })}
                          className="absolute right-1 top-1 rounded border bg-background p-2 hover:bg-muted">
                          <X size={16} />
                        </button>
                      </figure>)}
                    </div>}
                  </div>

                  {/* Single Toggle Button for Answer Key & Rubrics */}
                  <div className="pl-6">
                    <button
                      type="button"
                      aria-expanded={isOpen}
                      aria-controls={`criteria-${q.id}`}
                      onClick={() => toggleDetails(q.id)}
                      className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-[#245b50] dark:hover:text-[#8ab4f8] font-medium py-1 transition"
                    >
                      {isOpen ? (
                        <ChevronDown size={14} />
                      ) : (
                        <ChevronRight size={14} />
                      )}
                      <span>
                        แนวคำตอบและเกณฑ์คะแนน
                        {q.rubrics.some(r => r.name.trim()) && ` · ${q.rubrics.filter(r => r.name.trim()).length} เกณฑ์`}
                      </span>
                    </button>
                  </div>

                  {/* Collapsible Details Area (Answer Key + Rubrics) */}
                  {isOpen && (
                    <div id={`criteria-${q.id}`} className="pl-6 space-y-5 pt-1">
                      {/* Model Answer Key */}
                      <div className="space-y-2">
                        <label className="text-sm font-medium text-muted-foreground block">
                          แนวคำตอบ
                        </label>
                        <Textarea
                          aria-label={`แนวคำตอบข้อที่ ${index + 1}`}
                          rows={3}
                          value={q.answerKey}
                          onChange={(e) =>
                            updateQuestion(q.id, { answerKey: e.target.value })
                          }
                          placeholder="คำตอบที่คาดหวังหรือประเด็นสำคัญที่ควรตอบ"
                          className="w-full text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 focus:border-[#1a73e8] focus:outline-none p-2 rounded-md text-slate-700 dark:text-slate-300 resize-y"
                        />
                      </div>

                      {/* Flat Rubrics Section */}
                      <div className="space-y-3">
                        <div className="flex flex-wrap justify-between items-center gap-2">
                          <div className="flex items-center gap-2">
                            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                              เกณฑ์การให้คะแนน
                            </label>
                            {q.rubrics.length > 0 && (() => {
                              const rSum = q.rubrics.reduce((acc, r) => acc + (parseFloat(r.score) || 0), 0);
                              const targetScore = parseFloat(q.score) || 0;
                              const isMatch = Math.abs(rSum - targetScore) < 0.01;
                              return (
                                <span
                                  className={cn(
                                    "text-[10px] px-2 py-0.5 rounded-full font-medium flex items-center gap-1 border",
                                    isMatch
                                      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/50"
                                      : "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200 dark:border-amber-800/50"
                                  )}
                                  title={isMatch ? "คะแนนเกณฑ์ตรงกับคะแนนเต็มของข้อ" : "คะแนนเกณฑ์รวมกันไม่เท่ากับคะแนนข้อ"}
                                >
                                  <span>ผลรวมเกณฑ์: {rSum} / {targetScore} คะแนน</span>
                                  {!isMatch && <span className="font-bold underline">(ไม่ตรงกัน)</span>}
                                </span>
                              );
                            })()}
                          </div>

                          <label className="inline-flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300 cursor-pointer select-none bg-slate-50 dark:bg-slate-800/60 px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                            <Switch
                              checked={Boolean(q.hideRubricFromStudents)}
                              onCheckedChange={(checked) => updateQuestion(q.id, { hideRubricFromStudents: checked })}
                              aria-label={`ซ่อนเกณฑ์ไม่ให้นักเรียนเห็นข้อที่ ${index + 1}`}
                            />
                            <span className="flex items-center gap-1 font-medium">
                              <EyeOff size={13} className={q.hideRubricFromStudents ? "text-amber-500" : "text-slate-400"} />
                              <span>ซ่อนเกณฑ์ไม่ให้นักเรียนเห็น</span>
                            </span>
                          </label>
                        </div>
                        <p className="text-xs text-slate-500 sm:hidden">
                          กรอกหัวข้อ คำอธิบาย และคะแนนของแต่ละเกณฑ์
                        </p>
                        <div className="rubric-scroll">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead>
                              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-medium text-[11px]">
                                <th className="py-2 w-8 text-center">#</th>
                                <th className="py-2 px-2 w-1/3">หัวข้อเกณฑ์</th>
                                <th className="py-2 px-2">
                                  คำอธิบายรายละเอียด <span className="text-[10px] font-normal text-slate-400 dark:text-slate-500">
                                    {q.hideRubricFromStudents
                                      ? "(ซ่อนจากนักเรียนแล้ว เกณฑ์นี้ใช้เฉพาะระบบตรวจคะแนน)"
                                      : "(นักเรียนจะเห็นเกณฑ์นี้ ไม่ควรใส่เฉลยคำตอบ)"}
                                  </span>
                                </th>
                                <th className="py-2 text-center w-16">คะแนน</th>
                                <th className="py-2 w-8"></th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                              {q.rubrics.map((r, rIdx) => (
                                <tr key={r.id} className="rubric-row group">
                                  <td className="py-2 text-center text-slate-400">
                                    {rIdx + 1}
                                  </td>
                                  <td className="py-1 px-2">
                                    <input
                                      value={r.name}
                                      onChange={(e) =>
                                        updateRubric(q.id, r.id, {
                                          name: e.target.value,
                                        })
                                      }
                                      aria-label={`ชื่อเกณฑ์ที่ ${rIdx + 1} ของข้อ ${index + 1}`}
                                      placeholder="ชื่อเกณฑ์..."
                                      className="w-full bg-transparent border-none focus:outline-none text-xs"
                                    />
                                  </td>
                                  <td className="py-1 px-2">
                                    <input
                                      value={r.description}
                                      onChange={(e) =>
                                        updateRubric(q.id, r.id, {
                                          description: e.target.value,
                                        })
                                      }
                                      aria-label={`คำอธิบายเกณฑ์ที่ ${rIdx + 1} ของข้อ ${index + 1}`}
                                      placeholder="คำอธิบายเกณฑ์..."
                                      className="w-full bg-transparent border-none focus:outline-none text-xs text-slate-600 dark:text-slate-400"
                                    />
                                  </td>
                                  <td className="py-1 text-center">
                                    <input
                                      type="number"
                                      aria-label={`คะแนนเกณฑ์ที่ ${rIdx + 1}`}
                                      min="0"
                                      value={r.score}
                                      onChange={(e) =>
                                        updateRubric(q.id, r.id, {
                                          score: e.target.value,
                                        })
                                      }
                                      className="w-10 text-center bg-transparent border-none focus:outline-none font-bold text-xs"
                                    />
                                  </td>
                                  <td className="py-1 text-center">
                                    <button
                                      aria-label={`ลบเกณฑ์ที่ ${rIdx + 1}`}
                                      onClick={() => removeRubric(q.id, r.id)}
                                      disabled={q.rubrics.length === 1}
                                      className="text-slate-300 hover:text-red-500 disabled:opacity-0"
                                    >
                                      <X size={13} />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        <button
                          type="button"
                          onClick={() => addRubric(q.id)}
                          className="text-xs text-[#245b50] dark:text-[#91c7b8] hover:underline font-medium"
                        >
                          + เพิ่มเกณฑ์
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="text-center pt-2">
            <Button
              onClick={() => {
                const newId = Date.now();
                setQuestions([
                  ...questions,
                  {
                    id: newId,
                    text: "",
                    score: "5",
                    answerKey: "",
                    rubrics: [
                      { id: newId + 1, name: "", description: "", score: "5" },
                    ],
                    hideRubricFromStudents: false,
                  },
                ]);
                setShowDetails((prev) => ({ ...prev, [newId]: false }));
              }}
              variant="ghost"
              className="text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
            >
              + แทรกข้อสอบถัดไป
            </Button>
          </div>
        </fieldset>
      </div>
      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>การตั้งค่าข้อสอบ</DialogTitle>
            <DialogDescription>กำหนดช่วงเวลาที่ผู้เรียนเข้าสอบได้และรูปแบบการเรียงคำถาม</DialogDescription>
          </DialogHeader>
          <div className="space-y-5 py-2">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2 text-sm font-medium">
                <span>เริ่มทำข้อสอบ</span>
                <Input type="datetime-local" value={startDateTime}
                  onChange={event => setStartDateTime(event.target.value)} />
              </label>
              <label className="space-y-2 text-sm font-medium">
                <span>สิ้นสุดการสอบ</span>
                <Input type="datetime-local" value={endDateTime} min={startDateTime || undefined}
                  onChange={event => setEndDateTime(event.target.value)} />
              </label>
            </div>
            {startDateTime && endDateTime && new Date(endDateTime) <= new Date(startDateTime) && (
              <p role="alert" className="text-sm text-destructive">เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มสอบ</p>
            )}
            <div className="flex items-start justify-between gap-4 rounded-lg border p-4">
              <div>
                <label htmlFor="randomize-questions" className="text-sm font-medium">สุ่มลำดับข้อสอบ</label>
                <p className="mt-1 text-xs text-muted-foreground">ผู้เรียนแต่ละคนอาจเห็นคำถามเรียงลำดับต่างกัน</p>
              </div>
              <Switch id="randomize-questions" checked={isRandomized} onCheckedChange={setIsRandomized} />
            </div>
          </div>
          <div className="flex flex-wrap justify-between gap-2">
            <Button type="button" variant="ghost" onClick={() => {
              setStartDateTime("");
              setEndDateTime("");
              setIsRandomized(false);
            }}>ล้างการตั้งค่า</Button>
            <Button type="button" disabled={Boolean(startDateTime && endDateTime && new Date(endDateTime) <= new Date(startDateTime))}
              onClick={() => setSettingsOpen(false)}>เสร็จสิ้น</Button>
          </div>
        </DialogContent>
      </Dialog>
      <Dialog open={draftPickerOpen} onOpenChange={setDraftPickerOpen}>
        <DialogContent className="max-w-xl p-0 overflow-hidden">
          <DialogHeader className="border-b px-6 py-5">
            <DialogTitle>แบบร่างข้อสอบ</DialogTitle>
            <DialogDescription>เลือกข้อสอบที่ยังทำไม่เสร็จเพื่อกลับมาแก้ต่อ หรือเริ่มข้อสอบชุดใหม่</DialogDescription>
          </DialogHeader>
          <div className="max-h-[55vh] min-h-44 overflow-y-auto px-6">
            {draftChoices.length ? <div className="divide-y">
              {draftChoices.map(choice => (
                <div key={choice.id} className="flex items-center gap-3 py-4">
                  <button type="button" className="min-w-0 flex-1 text-left" onClick={() => openDraft(choice.id, choice.draft)}>
                    <span className="block truncate text-sm font-medium">{choice.draft.examTitle.trim() || "ยังไม่ได้ตั้งชื่อ"}</span>
                    <span className="mt-1 block text-xs text-muted-foreground">
                      {choice.draft.questions.length} ข้อ · แก้ไขล่าสุด {choice.draft.updatedAt
                        ? new Intl.DateTimeFormat("th-TH", { dateStyle: "medium", timeStyle: "short" }).format(new Date(choice.draft.updatedAt))
                        : "ไม่ทราบเวลา"}
                    </span>
                  </button>
                  <button type="button" aria-label={`ลบแบบร่าง ${choice.draft.examTitle || "ยังไม่ได้ตั้งชื่อ"}`}
                    onClick={() => void deleteDraft(choice.id, choice.draft.examTitle)}
                    className="rounded-md p-2 text-muted-foreground hover:bg-destructive/10 hover:text-destructive">
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div> : <div className="flex min-h-44 flex-col items-center justify-center text-center">
              <Files size={24} className="mb-2 text-muted-foreground" />
              <p className="text-sm font-medium">ยังไม่มีแบบร่าง</p>
              <p className="mt-1 text-xs text-muted-foreground">แบบร่างที่บันทึกไว้จะแสดงที่นี่</p>
            </div>}
          </div>
          <div className="flex justify-end border-t px-6 py-4">
            <Button onClick={startNewDraft}>สร้างข้อสอบชุดใหม่</Button>
          </div>
        </DialogContent>
      </Dialog>
      <Dialog open={blocker.state === "blocked"} onOpenChange={open => {
        if (!open && blocker.state === "blocked" && !savingDraft) blocker.reset();
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>บันทึกข้อสอบที่กำลังสร้างไว้ก่อนหรือไม่?</DialogTitle>
            <DialogDescription>บันทึกแบบร่างพร้อมรูปแนบไว้ในเครื่องนี้ เพื่อกลับมาทำต่อในห้องเดิมได้</DialogDescription>
          </DialogHeader>
          {(readingImages || generatingId !== null || isSaving) && <p role="status" className="text-sm">กรุณารอการประมวลผลให้เสร็จก่อนออกจากหน้า</p>}
          <div className="flex flex-wrap justify-end gap-2">
            <Button variant="ghost" disabled={savingDraft} onClick={() => blocker.state === "blocked" && blocker.reset()}>ทำต่อ</Button>
            <Button variant="outline" disabled={savingDraft || readingImages || generatingId !== null || isSaving}
              onClick={() => blocker.state === "blocked" && blocker.proceed()}>ออกโดยไม่บันทึก</Button>
            <Button disabled={savingDraft || readingImages || generatingId !== null || isSaving} onClick={() => saveDraft(true)}>บันทึกแบบร่างและออก</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
