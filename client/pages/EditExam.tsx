import { WorkspaceBreadcrumb } from "@/components/WorkspaceHeader";
import { PageLoading } from "@/components/RouteLoading";
import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ArrowLeft,
  X,
  Loader2,
  Save,
  ImagePlus,
  Sparkles,
  ChevronDown,
  ChevronRight,
  Copy,
  Trash2,
  Settings,
  EyeOff,
  Bookmark,
  BookmarkPlus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserProfileMenu } from "@/components/UserProfileMenu";
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
  answerKeyImages?: { name: string; dataUrl: string }[];
  hideRubricFromStudents?: boolean;
}

interface RubricPreset {
  id: string;
  name: string;
  rubrics: RubricItem[];
}

const toDateTimeLocal = (value?: string | null) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
};

export default function EditExam() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { token, isLoading: authLoading } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [readingImages, setReadingImages] = useState(false);
  const imageReadLock = useRef(false);
  const [generatingId, setGeneratingId] = useState<number | null>(null);

  const [examTitle, setExamTitle] = useState("");
  const [examDescription, setExamDescription] = useState("");
  const [startDateTime, setStartDateTime] = useState("");
  const [endDateTime, setEndDateTime] = useState("");
  const [isRandomized, setIsRandomized] = useState(false);

  const [questions, setQuestions] = useState<Question[]>([]);
  const [showDetails, setShowDetails] = useState<Record<number, boolean>>({});

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [showExitModal, setShowExitModal] = useState(false);
  const [exitTarget, setExitTarget] = useState(`/room/${roomId}`);

  // Rubric presets saved in localStorage
  const [rubricPresets, setRubricPresets] = useState<RubricPreset[]>(() => {
    try {
      const saved = localStorage.getItem("evaly_rubric_presets");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [showPresetModal, setShowPresetModal] = useState<number | null>(null);
  const [presetNameInput, setPresetNameInput] = useState("");
  const [presetToDelete, setPresetToDelete] = useState<string | null>(null);

  useEffect(() => {
    try {
      localStorage.setItem("evaly_rubric_presets", JSON.stringify(rubricPresets));
    } catch {
      // ignore
    }
  }, [rubricPresets]);

  // Dirty state tracking
  const [savedSnapshot, setSavedSnapshot] = useState<string>("");
  const currentSnapshot = JSON.stringify({
    examTitle,
    examDescription,
    startDateTime,
    endDateTime,
    isRandomized,
    questions: questions.map((q) => ({
      text: q.text,
      score: q.score,
      answerKey: q.answerKey,
      rubrics: q.rubrics,
      images: q.images?.map((img) => img.dataUrl),
      answerKeyImages: q.answerKeyImages?.map((img) => img.dataUrl),
      hideRubricFromStudents: q.hideRubricFromStudents,
    })),
  });

  const isDirty = !isLoading && savedSnapshot !== "" && currentSnapshot !== savedSnapshot;

  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (isDirty || readingImages || generatingId !== null || isSaving) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [isDirty, readingImages, generatingId, isSaving]);

  // Load existing exam
  useEffect(() => {
    if (authLoading) return;
    if (!token) {
      setIsLoading(false);
      return;
    }
    if (!roomId || !examId) {
      setIsLoading(false);
      return;
    }
    let active = true;

    const fetchExam = async () => {
      try {
        const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("ไม่สามารถโหลดข้อมูลข้อสอบได้");
        const data = await res.json();
        if (!active) return;

        const title = data.title || "";
        const desc = data.description || "";
        const start = toDateTimeLocal(data.start_date);
        const end = toDateTimeLocal(data.end_date);
        const rand = Boolean(data.is_randomized);

        setExamTitle(title);
        setExamDescription(desc);
        setStartDateTime(start);
        setEndDateTime(end);
        setIsRandomized(rand);

        const loadedQuestions: Question[] =
          data.questions && data.questions.length > 0
            ? data.questions.map((q: any, i: number) => {
                const qId = Date.now() + i;
                const imgList: string[] = Array.isArray(q.image_paths) ? q.image_paths : [];
                const answerKeyImgList: string[] = Array.isArray(q.answer_key_image_paths) ? q.answer_key_image_paths : [];
                return {
                  id: qId,
                  text: q.text || "",
                  score: String(q.score ?? "5"),
                  answerKey: q.answer_key || "",
                  rubrics:
                    q.rubrics && q.rubrics.length > 0
                      ? q.rubrics.map((r: any, j: number) => ({
                          id: Date.now() + 1000 + i * 100 + j,
                          name: r.name || "",
                          description: r.description || "",
                          score: String(r.score ?? "0"),
                        }))
                      : [
                          {
                            id: Date.now() + 1000 + i * 100,
                            name: "",
                            description: "",
                            score: String(q.score ?? "5"),
                          },
                        ],
                  images: imgList.map((p: string, idx: number) => ({
                    name: `รูปประกอบ ${idx + 1}`,
                    dataUrl: p,
                  })),
                  answerKeyImages: answerKeyImgList.map((p: string, idx: number) => ({
                    name: `ภาพเฉลย ${idx + 1}`,
                    dataUrl: p,
                  })),
                  hideRubricFromStudents: Boolean(q.hide_rubric_from_students),
                };
              })
            : [
                {
                  id: Date.now(),
                  text: "",
                  score: "5",
                  answerKey: "",
                  rubrics: [
                    { id: Date.now() + 1, name: "", description: "", score: "5" },
                  ],
                  images: [],
                  hideRubricFromStudents: false,
                },
              ];

        setQuestions(loadedQuestions);

        const initialDetails: Record<number, boolean> = {};
        loadedQuestions.forEach((q) => {
          if (q.answerKey.trim() || q.rubrics.some((r) => r.name.trim())) {
            initialDetails[q.id] = true;
          }
        });
        setShowDetails(initialDetails);

        setSavedSnapshot(
          JSON.stringify({
            examTitle: title,
            examDescription: desc,
            startDateTime: start,
            endDateTime: end,
            isRandomized: rand,
            questions: loadedQuestions.map((q) => ({
              text: q.text,
              score: q.score,
              answerKey: q.answerKey,
              rubrics: q.rubrics,
              images: q.images?.map((img) => img.dataUrl),
              hideRubricFromStudents: q.hideRubricFromStudents,
            })),
          })
        );
      } catch (err: any) {
        toast.error(err.message || "เกิดข้อผิดพลาดในการโหลดข้อสอบ");
      } finally {
        if (active) setIsLoading(false);
      }
    };

    fetchExam();
    return () => {
      active = false;
    };
  }, [token, roomId, examId]);

  const attachImages = async (questionId: number, files: File[], target: "images" | "answerKeyImages" = "images") => {
    if (!files.length || imageReadLock.current || isSaving) return;
    const question = questions.find((q) => q.id === questionId);
    if (!question) return;
    if ((question[target]?.length ?? 0) + files.length > 10) {
      toast.error("แนบรูปได้ไม่เกิน 10 รูปต่อข้อ");
      return;
    }
    if (
      files.some(
        (file) =>
          !["image/jpeg", "image/png", "image/gif", "image/webp"].includes(file.type) ||
          file.size > 5 * 1024 * 1024 ||
          file.size === 0
      )
    ) {
      toast.error("ใช้รูป JPG, PNG, GIF หรือ WebP ขนาดไม่เกิน 5 MB ต่อรูป");
      return;
    }
    imageReadLock.current = true;
    setReadingImages(true);
    try {
      const images = await Promise.all(
        files.map(
          (file) =>
            new Promise<{ name: string; dataUrl: string }>((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () =>
                typeof reader.result === "string"
                  ? resolve({ name: file.name, dataUrl: reader.result })
                  : reject(new Error("อ่านรูปไม่สำเร็จ"));
              reader.onerror = () => reject(new Error("อ่านรูปไม่สำเร็จ"));
              reader.onabort = () => reject(new Error("ยกเลิกการอ่านรูป"));
              reader.readAsDataURL(file);
            })
        )
      );
      setQuestions((current) =>
        current.map((q) =>
          q.id === questionId
            ? { ...q, [target]: [...(q[target] ?? []), ...images] }
            : q
        )
      );
    } catch {
      toast.error("อ่านไฟล์รูปไม่สำเร็จ กรุณาเลือกใหม่");
    } finally {
      imageReadLock.current = false;
      setReadingImages(false);
    }
  };

  const generateRubric = async (question: Question) => {
    if (generatingId !== null || readingImages || isSaving) return;
    if (!question.text.trim() && !question.images?.length) {
      toast.error("กรอกโจทย์หรือแนบรูปก่อนสร้างเกณฑ์");
      return;
    }
    const score = Number(question.score);
    if (!Number.isFinite(score) || score <= 0) {
      toast.error("ระบุคะแนนเต็มมากกว่า 0");
      return;
    }
    if (
      (question.answerKey.trim() ||
        question.rubrics.some((r) => r.name.trim() || r.description.trim())) &&
      !window.confirm("สร้างเกณฑ์ใหม่แทนแนวคำตอบและเกณฑ์เดิมของข้อนี้หรือไม่?")
    ) {
      return;
    }
    setGeneratingId(question.id);
    try {
      const response = await fetch("/api/ai/generate-rubric", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          question_text: question.text,
          total_score: score,
          question_images_base64: question.images?.map((image) => image.dataUrl) ?? [],
          tone: "moderate",
        }),
      });
      const result = await response.json();
      if (!response.ok)
        throw new Error(
          typeof result.detail === "string" ? result.detail : "สร้างเกณฑ์ไม่สำเร็จ"
        );
      if (!Array.isArray(result.rubrics) || !result.rubrics.length)
        throw new Error("AI ไม่ส่งเกณฑ์กลับมา กรุณาลองใหม่");
      updateQuestion(question.id, {
        answerKey: result.answer_key || "",
        rubrics: result.rubrics.map(
          (r: { name: string; description: string; score: number }, i: number) => ({
            id: Date.now() + i,
            name: r.name || "",
            description: r.description || "",
            score: String(r.score ?? 0),
          })
        ),
      });
      setShowDetails((current) => ({ ...current, [question.id]: true }));
      toast.success("สร้างเกณฑ์แล้ว กรุณาตรวจทานก่อนบันทึก");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "สร้างเกณฑ์ไม่สำเร็จ");
    } finally {
      setGeneratingId(null);
    }
  };

  const updateQuestion = (id: number, patch: Partial<Question>) => {
    setQuestions((prev) =>
      prev.map((q) => (q.id === id ? { ...q, ...patch } : q))
    );
  };

  const toggleDetails = (qId: number) => {
    setShowDetails((prev) => ({ ...prev, [qId]: !(prev[qId] ?? false) }));
  };

  const duplicateQuestion = (qId: number) => {
    const src = questions.find((q) => q.id === qId);
    if (!src) return;
    const newId = Date.now();
    setQuestions((prev) => {
      const idx = prev.findIndex((q) => q.id === qId);
      const newQs = [...prev];
      newQs.splice(idx + 1, 0, {
        ...src,
        id: newId,
        rubrics: src.rubrics.map((r, i) => ({ ...r, id: newId + 100 + i })),
        images: src.images ? [...src.images] : [],
      });
      return newQs;
    });
    setShowDetails((prev) => ({ ...prev, [newId]: prev[qId] ?? false }));
  };

  const deleteQuestion = (qId: number) => {
    if (questions.length <= 1) return;
    setQuestions((prev) => prev.filter((q) => q.id !== qId));
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
          : q
      )
    );
  };

  const removeRubric = (qId: number, rId: number) => {
    setQuestions((prev) =>
      prev.map((q) =>
        q.id === qId
          ? { ...q, rubrics: q.rubrics.filter((r) => r.id !== rId) }
          : q
      )
    );
  };

  const updateRubric = (
    qId: number,
    rId: number,
    patch: Partial<RubricItem>
  ) => {
    setQuestions((prev) =>
      prev.map((q) =>
        q.id === qId
          ? {
              ...q,
              rubrics: q.rubrics.map((r) =>
                r.id === rId ? { ...r, ...patch } : r
              ),
            }
          : q
      )
    );
  };

  const saveRubricPreset = () => {
    if (showPresetModal === null || !presetNameInput.trim()) return;
    const q = questions.find((x) => x.id === showPresetModal);
    if (!q || q.rubrics.length === 0) return;
    const newPreset: RubricPreset = {
      id: Date.now().toString(),
      name: presetNameInput.trim(),
      rubrics: q.rubrics.map((r) => ({ ...r, id: Date.now() + Math.random() })),
    };
    setRubricPresets((prev) => [...prev, newPreset]);
    toast.success("บันทึกเทมเพลตเกณฑ์สำเร็จ");
    setShowPresetModal(null);
    setPresetNameInput("");
  };

  const applyRubricPreset = (qId: number, presetId: string) => {
    const preset = rubricPresets.find((p) => p.id === presetId);
    if (!preset) return;
    updateQuestion(qId, {
      rubrics: preset.rubrics.map((r) => ({
        ...r,
        id: Date.now() + Math.random(),
      })),
    });
    toast.success("นำเทมเพลตเกณฑ์มาใช้แล้ว");
  };

  const deleteRubricPreset = () => {
    if (!presetToDelete) return;
    setRubricPresets((prev) => prev.filter((p) => p.id !== presetToDelete));
    setPresetToDelete(null);
    toast.success("ลบเทมเพลตสำเร็จ");
  };

  const handleSave = async () => {
    if (isSaving || imageReadLock.current || generatingId !== null) return;
    if (questions.some((q) => q.images?.length && !q.text.trim())) {
      toast.error("กรอกคำถามหรือคำชี้แจงให้ข้อที่แนบรูปก่อนบันทึก");
      return;
    }
    if (
      startDateTime &&
      endDateTime &&
      new Date(endDateTime) <= new Date(startDateTime)
    ) {
      toast.error("เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มสอบ");
      setSettingsOpen(true);
      return;
    }
    const validQs = questions.filter(
      (q) => q.text.trim() || (q.images && q.images.length > 0)
    );
    if (!validQs.length) {
      toast.error("เพิ่มคำถามอย่างน้อยหนึ่งข้อ");
      return;
    }

    setIsSaving(true);
    const total = validQs.reduce((s, q) => s + (parseFloat(q.score) || 0), 0);

    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: examTitle.trim() || validQs[0].text.slice(0, 50) || "ข้อสอบ",
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
              .filter((r) => r.name.trim())
              .map((r) => ({
                name: r.name,
                description: r.description,
                score: parseFloat(r.score) || 0,
              })),
            order_index: i,
            question_images_base64: q.images?.length
              ? q.images.map((img) => img.dataUrl)
              : null,
            answer_key_images_base64: q.answerKeyImages?.length
              ? q.answerKeyImages.map((img) => img.dataUrl)
              : null,
            hide_rubric_from_students: Boolean(q.hideRubricFromStudents),
          })),
        }),
      });

      if (res.ok) {
        toast.success("บันทึกการแก้ไขสำเร็จ!");
        setSavedSnapshot(currentSnapshot);
        navigate(`/room/${roomId}`);
      } else {
        const error = await res.json().catch(() => null);
        toast.error(error?.detail || "ไม่สามารถบันทึกการแก้ไขได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsSaving(false);
    }
  };

  const onBack = () => {
    setExitTarget(`/room/${roomId}`);
    if (isDirty) {
      setShowExitModal(true);
    } else {
      navigate(`/room/${roomId}`);
    }
  };

  const totalScore = questions.reduce(
    (s, q) => s + (parseFloat(q.score) || 0),
    0
  );

  if (isLoading) {
    return <PageLoading layout="form" />;
  }

  return (
    <div className="workspace create-exam-page edit-exam-page">
      {/* Clean Top Navbar */}
      <div className="task-header sticky top-0 z-40 flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-2.5 shadow-sm dark:border-slate-800 dark:bg-[#1E1E1E] sm:px-6">
        <div className="flex items-center gap-3 min-w-0">
          <button
            aria-label="กลับห้องเรียน"
            onClick={onBack}
            className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition"
          >
            <ArrowLeft size={18} />
          </button>
          <div className="task-header-title flex min-w-0 flex-col sm:w-[min(34rem,42vw)]">
            <input
              type="text"
              aria-label="ชื่อข้อสอบ"
              disabled={isLoading || isSaving}
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
            <div className="hidden sm:block">
              <ThemeToggle />
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              title="การตั้งค่าข้อสอบ"
              aria-label="เปิดการตั้งค่าข้อสอบ"
              disabled={isLoading || isSaving}
              onClick={() => setSettingsOpen(true)}
            >
              <Settings size={16} />
            </Button>
          </div>
          <span
            className="mx-1 hidden h-6 w-px bg-border sm:block"
            aria-hidden="true"
          />
          <Button
            onClick={handleSave}
            title="บันทึกการแก้ไข"
            aria-label="บันทึกการแก้ไข"
            disabled={
              isLoading || isSaving || readingImages || generatingId !== null
            }
            className="primary-action h-9 gap-1.5 rounded-lg px-3.5 text-xs"
          >
            {isSaving ? (
              <Loader2 size={15} className="animate-spin" />
            ) : (
              <Save size={15} />
            )}
            <span className="hidden sm:inline">
              {isSaving ? "กำลังบันทึก…" : "บันทึก"}
            </span>
          </Button>
        </div>
        <ThemeToggle />
        <UserProfileMenu />
      </div>

      {/* Google Docs Paper Canvas */}
      <div className="document-page">
        <div
          onClickCapture={(event) => {
            const link = (event.target as HTMLElement).closest("a");
            if (isDirty && link) {
              event.preventDefault();
              event.stopPropagation();
              setExitTarget(link.pathname);
              setShowExitModal(true);
            }
          }}
        >
          <WorkspaceBreadcrumb roomId={roomId} current="แก้ไขข้อสอบ" />
        </div>
        <h1 className="page-heading mb-2">แก้ไขข้อสอบ</h1>
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
            {startDateTime
              ? `เริ่ม ${new Intl.DateTimeFormat("th-TH", {
                  dateStyle: "medium",
                  timeStyle: "short",
                }).format(new Date(startDateTime))}`
              : "ไม่กำหนดเวลาเริ่ม"}
            {" · "}
            {endDateTime
              ? `สิ้นสุด ${new Intl.DateTimeFormat("th-TH", {
                  dateStyle: "medium",
                  timeStyle: "short",
                }).format(new Date(endDateTime))}`
              : "ไม่กำหนดเวลาสิ้นสุด"}
          </p>
        )}
        <fieldset
          disabled={isLoading || isSaving || generatingId !== null}
          className="exam-paper min-w-0 space-y-8"
        >
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
                    <div className="flex items-center gap-1 shrink-0 pt-1">
                      <button
                        type="button"
                        aria-label={`คัดลอกข้อที่ ${index + 1}`}
                        title="คัดลอกข้อนี้"
                        onClick={() => duplicateQuestion(q.id)}
                        className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
                      >
                        <Copy size={15} />
                      </button>
                      {questions.length > 1 && (
                        <button
                          type="button"
                          aria-label={`ลบข้อที่ ${index + 1}`}
                          title="ลบข้อนี้"
                          onClick={() => deleteQuestion(q.id)}
                          className="p-1 text-slate-400 hover:text-red-500 transition"
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="pl-6 space-y-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <label className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-muted focus-within:ring-2 focus-within:ring-ring">
                        <ImagePlus size={16} aria-hidden="true" />
                        แนบรูป
                        <input
                          type="file"
                          className="sr-only"
                          multiple
                          aria-label={`แนบรูปโจทย์ข้อที่ ${index + 1}`}
                          accept="image/jpeg,image/png,image/gif,image/webp,image/heic,image/heif,.heic,.heif,image/*"
                          disabled={
                            isSaving ||
                            readingImages ||
                            (q.images?.length ?? 0) >= 10
                          }
                          onChange={(event) => {
                            const files = Array.from(event.target.files ?? []);
                            event.target.value = "";
                            void attachImages(q.id, files);
                          }}
                        />
                      </label>
                      <Button
                        type="button"
                        variant="ghost"
                        className="gap-2 text-sm text-primary"
                        disabled={readingImages || generatingId !== null}
                        onClick={() => generateRubric(q)}
                      >
                        {generatingId === q.id ? (
                          <Loader2 size={16} className="animate-spin" />
                        ) : (
                          <Sparkles size={16} />
                        )}
                        {generatingId === q.id
                          ? "กำลังสร้างเกณฑ์…"
                          : "สร้างเกณฑ์ด้วย AI"}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      แนบได้ 10 รูป · รูปละไม่เกิน 5 MB
                    </p>
                    {readingImages && (
                      <p role="status" className="text-xs text-muted-foreground">
                        กำลังเตรียมรูป…
                      </p>
                    )}
                    {!!q.images?.length && (
                      <div className="flex flex-wrap gap-3">
                        {q.images.map((image, imageIndex) => (
                          <figure
                            key={imageIndex}
                            className="relative w-36 rounded-lg border p-2"
                          >
                            <img
                              src={image.dataUrl}
                              alt={`รูปประกอบโจทย์ข้อ ${index + 1} รูปที่ ${
                                imageIndex + 1
                              }`}
                              className="h-28 w-full object-contain"
                            />
                            <figcaption className="mt-1 truncate text-xs text-muted-foreground">
                              {image.name}
                            </figcaption>
                            <button
                              type="button"
                              disabled={isSaving || readingImages}
                              aria-label={`ลบรูปที่ ${imageIndex + 1} ของข้อ ${
                                index + 1
                              }`}
                              onClick={() =>
                                updateQuestion(q.id, {
                                  images: q.images?.filter(
                                    (_, i) => i !== imageIndex
                                  ),
                                })
                              }
                              className="absolute right-1 top-1 rounded border bg-background p-2 hover:bg-muted"
                            >
                              <X size={16} />
                            </button>
                          </figure>
                        ))}
                      </div>
                    )}
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
                        {q.rubrics.some((r) => r.name.trim()) &&
                          ` · ${
                            q.rubrics.filter((r) => r.name.trim()).length
                          } เกณฑ์`}
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
                        <div className="flex flex-wrap items-center gap-2">
                          <label className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-dashed border-slate-300 px-2.5 py-1.5 text-xs text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800">
                            <ImagePlus size={14} aria-hidden="true" />
                            แนบภาพแนวคำตอบ
                            <input type="file" className="sr-only" multiple
                              aria-label={`แนบภาพแนวคำตอบข้อที่ ${index + 1}`}
                              accept="image/jpeg,image/png,image/gif,image/webp,image/heic,image/heif,.heic,.heif,image/*"
                              disabled={isSaving || readingImages || (q.answerKeyImages?.length ?? 0) >= 10}
                              onChange={event => {
                                const files = Array.from(event.target.files ?? []);
                                event.target.value = "";
                                void attachImages(q.id, files, "answerKeyImages");
                              }} />
                          </label>
                          <span className="text-[11px] text-muted-foreground">ใช้ตรวจโดย AI และผู้สอนเท่านั้น</span>
                        </div>
                        {!!q.answerKeyImages?.length && <div className="flex flex-wrap gap-2">
                          {q.answerKeyImages.map((image, imageIndex) => <figure key={imageIndex} className="relative w-28 rounded-lg border p-1.5">
                            <img src={image.dataUrl} alt={`ภาพแนวคำตอบข้อ ${index + 1} รูปที่ ${imageIndex + 1}`} className="h-20 w-full object-contain" />
                            <button type="button" disabled={isSaving || readingImages}
                              aria-label={`ลบภาพแนวคำตอบที่ ${imageIndex + 1} ของข้อ ${index + 1}`}
                              onClick={() => updateQuestion(q.id, { answerKeyImages: q.answerKeyImages?.filter((_, i) => i !== imageIndex) })}
                              className="absolute right-1 top-1 rounded border bg-background p-1 hover:bg-muted"><X size={13} /></button>
                          </figure>)}
                        </div>}
                      </div>

                      {/* Flat Rubrics Section */}
                      <div className="space-y-3">
                        <div className="flex flex-wrap justify-between items-center gap-2">
                          <div className="flex items-center gap-2">
                            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                              เกณฑ์การให้คะแนน
                            </label>
                            {q.rubrics.length > 0 &&
                              (() => {
                                const rSum = q.rubrics.reduce(
                                  (acc, r) => acc + (parseFloat(r.score) || 0),
                                  0
                                );
                                const targetScore = parseFloat(q.score) || 0;
                                const isMatch =
                                  Math.abs(rSum - targetScore) < 0.01;
                                return (
                                  <span
                                    className={cn(
                                      "text-[10px] px-2 py-0.5 rounded-full font-medium flex items-center gap-1 border",
                                      isMatch
                                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/50"
                                        : "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200 dark:border-amber-800/50"
                                    )}
                                    title={
                                      isMatch
                                        ? "คะแนนเกณฑ์ตรงกับคะแนนเต็มของข้อ"
                                        : "คะแนนเกณฑ์รวมกันไม่เท่ากับคะแนนข้อ"
                                    }
                                  >
                                    <span>
                                      ผลรวมเกณฑ์: {rSum} / {targetScore} คะแนน
                                    </span>
                                    {!isMatch && (
                                      <span className="font-bold underline">
                                        (ไม่ตรงกัน)
                                      </span>
                                    )}
                                  </span>
                                );
                              })()}
                          </div>

                          <label className="inline-flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300 cursor-pointer select-none bg-slate-50 dark:bg-slate-800/60 px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                            <Switch
                              checked={Boolean(q.hideRubricFromStudents)}
                              onCheckedChange={(checked) =>
                                updateQuestion(q.id, {
                                  hideRubricFromStudents: checked,
                                })
                              }
                              aria-label={`ซ่อนเกณฑ์ไม่ให้นักเรียนเห็นข้อที่ ${
                                index + 1
                              }`}
                            />
                            <span className="flex items-center gap-1 font-medium">
                              <EyeOff
                                size={13}
                                className={
                                  q.hideRubricFromStudents
                                    ? "text-amber-500"
                                    : "text-slate-400"
                                }
                              />
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
                                  คำอธิบายรายละเอียด{" "}
                                  <span className="text-[10px] font-normal text-slate-400 dark:text-slate-500">
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
                                      aria-label={`ชื่อเกณฑ์ที่ ${
                                        rIdx + 1
                                      } ของข้อ ${index + 1}`}
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
                                      aria-label={`คำอธิบายเกณฑ์ที่ ${
                                        rIdx + 1
                                      } ของข้อ ${index + 1}`}
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

                        <div className="flex items-center justify-between pt-1">
                          <div className="flex items-center gap-3">
                            <button
                              type="button"
                              onClick={() => addRubric(q.id)}
                              className="text-xs text-[#245b50] dark:text-[#91c7b8] hover:underline font-medium"
                            >
                              + เพิ่มเกณฑ์
                            </button>

                            {rubricPresets.length > 0 && (
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <button
                                    type="button"
                                    className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 font-medium transition-colors"
                                  >
                                    <Bookmark size={12} />
                                    <span>ใช้เทมเพลต</span>
                                  </button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="start" className="w-56">
                                  <DropdownMenuLabel>
                                    เทมเพลตเกณฑ์ที่บันทึกไว้
                                  </DropdownMenuLabel>
                                  <DropdownMenuSeparator />
                                  {rubricPresets.map((preset) => (
                                    <DropdownMenuItem
                                      key={preset.id}
                                      onClick={() =>
                                        applyRubricPreset(q.id, preset.id)
                                      }
                                      className="flex justify-between items-center cursor-pointer"
                                    >
                                      <span className="truncate pr-2">
                                        {preset.name}
                                      </span>
                                      <button
                                        type="button"
                                        aria-label={`ลบเทมเพลต ${preset.name}`}
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          setPresetToDelete(preset.id);
                                        }}
                                        className="text-slate-400 hover:text-red-500 p-0.5 rounded"
                                      >
                                        <X size={13} />
                                      </button>
                                    </DropdownMenuItem>
                                  ))}
                                </DropdownMenuContent>
                              </DropdownMenu>
                            )}

                            {q.rubrics.some((r) => r.name.trim()) && (
                              <button
                                type="button"
                                onClick={() => {
                                  setShowPresetModal(q.id);
                                  setPresetNameInput("");
                                }}
                                className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 font-medium transition-colors"
                              >
                                <BookmarkPlus size={12} />
                                <span>บันทึกเป็นเทมเพลต</span>
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="text-center pt-2">
            <Button
              type="button"
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
                    images: [],
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

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>การตั้งค่าข้อสอบ</DialogTitle>
            <DialogDescription>
              กำหนดช่วงเวลาที่ผู้เรียนเข้าสอบได้และรูปแบบการเรียงคำถาม
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-5 py-2">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2 text-sm font-medium">
                <span>เริ่มทำข้อสอบ</span>
                <Input
                  type="datetime-local"
                  value={startDateTime}
                  onChange={(event) => setStartDateTime(event.target.value)}
                />
              </label>
              <label className="space-y-2 text-sm font-medium">
                <span>สิ้นสุดการสอบ</span>
                <Input
                  type="datetime-local"
                  value={endDateTime}
                  min={startDateTime || undefined}
                  onChange={(event) => setEndDateTime(event.target.value)}
                />
              </label>
            </div>
            {startDateTime &&
              endDateTime &&
              new Date(endDateTime) <= new Date(startDateTime) && (
                <p role="alert" className="text-sm text-destructive">
                  เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มสอบ
                </p>
              )}
            <div className="flex items-start justify-between gap-4 rounded-lg border p-4">
              <div>
                <label
                  htmlFor="randomize-questions"
                  className="text-sm font-medium"
                >
                  สุ่มลำดับข้อสอบ
                </label>
                <p className="mt-1 text-xs text-muted-foreground">
                  ผู้เรียนแต่ละคนอาจเห็นคำถามเรียงลำดับต่างกัน
                </p>
              </div>
              <Switch
                id="randomize-questions"
                checked={isRandomized}
                onCheckedChange={setIsRandomized}
              />
            </div>
          </div>
          <div className="flex flex-wrap justify-between gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setStartDateTime("");
                setEndDateTime("");
                setIsRandomized(false);
              }}
            >
              ล้างการตั้งค่า
            </Button>
            <Button
              type="button"
              disabled={Boolean(
                startDateTime &&
                  endDateTime &&
                  new Date(endDateTime) <= new Date(startDateTime)
              )}
              onClick={() => setSettingsOpen(false)}
            >
              เสร็จสิ้น
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Exit Without Saving Confirmation Dialog */}
      <Dialog open={showExitModal} onOpenChange={setShowExitModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>ยกเลิกการแก้ไขหรือไม่?</DialogTitle>
            <DialogDescription>
              คุณมีการเปลี่ยนแปลงที่ยังไม่ได้บันทึก หากออกจากหน้านี้
              ข้อมูลที่แก้ไขจะไม่ถูกบันทึก
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-wrap justify-end gap-2">
            <Button variant="ghost" onClick={() => setShowExitModal(false)}>
              แก้ไขต่อ
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowExitModal(false);
                navigate(exitTarget);
              }}
            >
              ออกโดยไม่บันทึก
            </Button>
            <Button
              disabled={isSaving || readingImages || generatingId !== null}
              onClick={async () => {
                setShowExitModal(false);
                await handleSave();
              }}
            >
              บันทึกและออก
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Save Preset Dialog */}
      <Dialog
        open={showPresetModal !== null}
        onOpenChange={(open) => !open && setShowPresetModal(null)}
      >
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>บันทึกเทมเพลตเกณฑ์</DialogTitle>
            <DialogDescription>
              ตั้งชื่อเทมเพลตเกณฑ์การให้คะแนนนี้เพื่อนำไปใช้ซ้ำในข้ออื่น
            </DialogDescription>
          </DialogHeader>
          <div className="py-2">
            <Input
              value={presetNameInput}
              onChange={(e) => setPresetNameInput(e.target.value)}
              placeholder="เช่น เกณฑ์การเขียนอธิบาย..."
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter") saveRubricPreset();
              }}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setShowPresetModal(null)}>
              ยกเลิก
            </Button>
            <Button onClick={saveRubricPreset}>บันทึก</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Preset Confirm Dialog */}
      <Dialog
        open={presetToDelete !== null}
        onOpenChange={(open) => !open && setPresetToDelete(null)}
      >
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>ยืนยันการลบเทมเพลต</DialogTitle>
            <DialogDescription>
              คุณแน่ใจหรือไม่ว่าต้องการลบเทมเพลตนี้?
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setPresetToDelete(null)}>
              ยกเลิก
            </Button>
            <Button variant="destructive" onClick={deleteRubricPreset}>
              ลบเทมเพลต
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
