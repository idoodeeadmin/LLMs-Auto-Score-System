import { ContentSkeleton } from "@/components/RouteLoading";
import { WorkspaceBreadcrumb } from "@/components/WorkspaceHeader";
import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  Clock,
  Send,
  CheckCircle2,
  Sparkles,
  Loader2,
  Image as ImageIcon,
  X,
  Upload,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserProfileMenu } from "@/components/UserProfileMenu";
import { toast } from "sonner";
import { countWords, formatRemainingTime } from "@/lib/utils";

interface QuestionItem {
  id: number;
  text: string;
  score: number;
  rubrics?: any[];
  order_index: number;
  image_paths?: string[];
  hide_rubric_from_students?: boolean;
}

interface ExamData {
  id: number;
  title: string;
  total_score: number;
  questions: QuestionItem[];
  start_date?: string | null;
  end_date?: string | null;
  submission_deadline?: string | null;
  server_time?: string | null;
}

const MAX_WORDS = 300;


export default function ExamSubmit() {
  const { roomId, examId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [exam, setExam] = useState<ExamData | null>(null);
  const [loading, setLoading] = useState(true);

  // Per-question state for text answers and attached image files
  const [answers, setAnswers] = useState<{ [qId: number]: string }>({});
  const [questionImages, setQuestionImages] = useState<{
    [qId: number]: File[];
  }>({});
  const [imagePreviews, setImagePreviews] = useState<{
    [qId: number]: string[];
  }>({});

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [clockOffset, setClockOffset] = useState<number>(0);
  const [now, setNow] = useState<number>(Date.now());
  const [draftSaved, setDraftSaved] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false);

  const draftKey = `evaly_draft_${roomId}_${examId}`;
  const hasAnyAnswer = Object.values(answers).some(
    (val) => typeof val === "string" && val.trim().length > 0
  );

  // Restore draft from localStorage on mount
  useEffect(() => {
    if (!roomId || !examId) return;
    try {
      const saved = localStorage.getItem(draftKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && typeof parsed === "object" && Object.keys(parsed).length > 0) {
          setAnswers((prev) => ({ ...parsed, ...prev }));
          setDraftSaved(true);
          toast.info("กู้คืนร่างคำตอบที่บันทึกไว้ในเครื่องเรียบร้อยแล้ว", { duration: 3000 });
        }
      }
    } catch {
      // ignore JSON parse error
    }
  }, [roomId, examId, draftKey]);

  // Autosave answers to localStorage
  useEffect(() => {
    if (!roomId || !examId || isSubmitted) return;
    if (hasAnyAnswer) {
      try {
        localStorage.setItem(draftKey, JSON.stringify(answers));
        setDraftSaved(true);
      } catch {
        // ignore storage quota error
      }
    }
  }, [answers, roomId, examId, draftKey, hasAnyAnswer, isSubmitted]);

  // Prevent accidental tab close or page reload when answers are typed
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (!isSubmitted && hasAnyAnswer) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [hasAnyAnswer, isSubmitted]);

  const handleBack = () => {
    if (hasAnyAnswer && !isSubmitted) {
      setShowExitConfirm(true);
    } else {
      navigate(`/room/${roomId}`);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setNow(Date.now());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchExam = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/rooms/${roomId}/exams/${examId}`, {
          headers: { Authorization: token ? `Bearer ${token}` : "" },
        });
        if (res.ok) {
          const data = await res.json();
          setExam(data);
          if (data.server_time) {
            setClockOffset(new Date(data.server_time).getTime() - Date.now());
          }
        } else {
          toast.error("ไม่พบข้อมูลแบบทดสอบ");
        }
      } catch (err) {
        console.error("Error fetching exam:", err);
      } finally {
        setLoading(false);
      }
    };

    if (roomId && examId) {
      fetchExam();
    }
  }, [roomId, examId, token]);

  const handleImageChange = (qId: number, files: FileList | null) => {
    if (!files || files.length === 0) return;

    const newFiles = Array.from(files);
    setQuestionImages((prev) => {
      const existing = prev[qId] || [];
      return { ...prev, [qId]: [...existing, ...newFiles] };
    });

    const newPreviewUrls = newFiles.map((file) => URL.createObjectURL(file));
    setImagePreviews((prev) => {
      const existing = prev[qId] || [];
      return { ...prev, [qId]: [...existing, ...newPreviewUrls] };
    });
  };

  const removeImage = (qId: number, imgIndex: number) => {
    setQuestionImages((prev) => {
      const updated = [...(prev[qId] || [])];
      updated.splice(imgIndex, 1);
      return { ...prev, [qId]: updated };
    });

    setImagePreviews((prev) => {
      const updated = [...(prev[qId] || [])];
      URL.revokeObjectURL(updated[imgIndex]);
      updated.splice(imgIndex, 1);
      return { ...prev, [qId]: updated };
    });
  };

  const syncedNow = now + clockOffset;
  const endDateMs = exam?.end_date ? new Date(exam.end_date).getTime() : null;
  const deadlineMs = exam?.submission_deadline
    ? new Date(exam.submission_deadline).getTime()
    : endDateMs
    ? endDateMs + 60 * 1000
    : null;

  const remainingSeconds = endDateMs ? Math.max(0, Math.floor((endDateMs - syncedNow) / 1000)) : null;
  const graceRemainingSeconds = deadlineMs ? Math.max(0, Math.floor((deadlineMs - syncedNow) / 1000)) : null;
  const isExpired = deadlineMs !== null && syncedNow > deadlineMs;
  const isGracePeriod = !isExpired && endDateMs !== null && syncedNow > endDateMs;
  const isWarningPeriod = !isExpired && !isGracePeriod && remainingSeconds !== null && remainingSeconds <= 300;

  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      if (e) e.preventDefault();
      if (!exam || !exam.questions || exam.questions.length === 0) {
        toast.error("ไม่มีคำถามในแบบทดสอบนี้");
        return;
      }

      if (isExpired) {
        toast.error("หมดเวลาส่งคำตอบสำหรับแบบทดสอบนี้แล้ว");
        return;
      }

      for (let i = 0; i < exam.questions.length; i++) {
        const q = exam.questions[i];
        const count = countWords(answers[q.id] || "");
        if (count > MAX_WORDS) {
          toast.error(`ข้อที่ ${i + 1} คำตอบยาวเกิน 300 คำ (ปัจจุบัน ${count} คำ) กรุณาย่อความยาวก่อนส่ง`);
          document.getElementById(`question-${q.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
          return;
        }
      }

      setIsSubmitting(true);
      try {
        const answersPayload = exam.questions.map((q) => ({
          question_id: q.id,
          answer_text: answers[q.id] || "",
        }));

        const formData = new FormData();
        formData.append("answers", JSON.stringify(answersPayload));

        // Append images per question: image_{q_id}_{index}
        exam.questions.forEach((q) => {
          const files = questionImages[q.id] || [];
          files.forEach((file, idx) => {
            formData.append(`image_${q.id}_${idx}`, file, file.name);
          });
        });

        const res = await fetch(
          `/api/rooms/${roomId}/exams/${examId}/submit-multipart`,
          {
            method: "POST",
            headers: { Authorization: token ? `Bearer ${token}` : "" },
            body: formData,
          },
        );

        if (res.ok) {
          toast.success("ส่งคำตอบสำเร็จ!");
          setIsSubmitted(true);
          try {
            localStorage.removeItem(draftKey);
            setDraftSaved(false);
          } catch {
            // ignore
          }
        } else {
          const err = await res.json().catch(() => null);
          toast.error(err?.detail || "เกิดข้อผิดพลาดในการส่งคำตอบ");
        }
      } catch {
        toast.error("ไม่สามารถส่งได้ กรุณาตรวจสอบการเชื่อมต่อ");
      } finally {
        setIsSubmitting(false);
      }
    },
    [token, roomId, examId, exam, answers, questionImages, draftKey],
  );

  return (
    <div className="workspace">
      {/* Top Navbar */}
      <header className="task-header sticky top-0 z-40 bg-white dark:bg-[#1E1E1E] border-b border-slate-200 dark:border-slate-800 px-8 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={handleBack}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-[#245b50] transition"
          >
            <ArrowLeft size={16} />
            <span className="task-header-back-label">กลับห้องเรียน</span>
          </button>
          <div className="task-header-title">
            <h1 className="font-semibold text-base text-slate-900 dark:text-white">
              {exam?.title || "ทำข้อสอบ (Student Exam Submission)"}
            </h1>
            {exam && (
              <span className="text-xs text-[#245b50] dark:text-[#91c7b8] font-medium">
                คะแนนเต็มรวม: {exam.total_score} คะแนน
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {draftSaved && hasAnyAnswer && !isSubmitted && (
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-full border border-emerald-200/70 dark:border-emerald-800/70">
              <CheckCircle2 size={12} className="text-emerald-600 dark:text-emerald-400" />
              บันทึกร่างในเครื่องแล้ว
            </span>
          )}
          {endDateMs ? (
            <div
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold transition-all ${
                isExpired
                  ? "bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300 border border-red-300 dark:border-red-800"
                  : isGracePeriod
                  ? "bg-red-500 text-white animate-pulse shadow-sm"
                  : isWarningPeriod
                  ? "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-300 dark:border-amber-700"
                  : "bg-emerald-50 text-[#245b50] dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
              }`}
            >
              {isExpired ? (
                <>
                  <AlertCircle size={14} className="shrink-0" />
                  <span>หมดเวลา</span>
                </>
              ) : isGracePeriod ? (
                <>
                  <AlertTriangle size={14} className="shrink-0" />
                  <span>ส่งท้าย: {graceRemainingSeconds}s</span>
                </>
              ) : (
                <>
                  <Clock size={14} className="shrink-0" />
                  <span>{formatRemainingTime(remainingSeconds!)}</span>
                </>
              )}
            </div>
          ) : (
            <span className="hidden sm:inline-flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
              <Clock size={13} />
              ไม่จำกัดเวลา
            </span>
          )}
          <ThemeToggle />
          <UserProfileMenu />
        </div>
      </header>

      <main className="document-page">
        <WorkspaceBreadcrumb roomId={roomId} current="ทำข้อสอบ" />
        {loading ? (
          <ContentSkeleton />
        ) : !exam ? (
          <div className="py-16 text-center text-slate-400 bg-white dark:bg-[#1E1E1E] rounded-xl border border-slate-200 dark:border-slate-800 p-8">
            <p>ไม่พบข้อมูลแบบทดสอบ</p>
          </div>
        ) : (
          <>
            {/* Success Banner */}
            {isSubmitted && (
              <div className="bg-[#E6F4EA] dark:bg-emerald-950/40 border border-[#CEEAD6] dark:border-emerald-800 rounded-xl p-5 text-[#137333] dark:text-emerald-300 flex items-start gap-4 shadow-sm">
                <CheckCircle2 className="w-6 h-6 text-[#188038] shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h3 className="font-bold text-sm text-[#137333] dark:text-emerald-200">
                    ส่งคำตอบสำเร็จ! ระบบได้รับคำตอบของคุณเรียบร้อยแล้ว
                  </h3>
                  <p className="text-xs text-[#137333] dark:text-emerald-400 leading-relaxed">
                    ระบบได้ส่งคำตอบทุกข้อพร้อมภาพลายมือเข้าคิวประเมินผลคะแนนด้วย
                    AI เรียบร้อยแล้ว
                    อาจารย์ผู้สอนสามารถตรวจทานและอนุมัติคะแนนได้
                  </p>
                </div>
              </div>
            )}

            {!isSubmitted ? (
              <form onSubmit={handleSubmit} className="exam-paper">
                {isExpired && (
                  <div className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl p-4 text-red-800 dark:text-red-200 flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
                    <div>
                      <h4 className="font-bold text-xs">หมดเวลาการสอบแล้ว (Exam Closed)</h4>
                      <p className="text-xs text-red-600 dark:text-red-300 mt-0.5">
                        เลยกำหนดเวลาส่งคำตอบข้อสอบแล้ว ระบบได้ปิดรับการส่งคำตอบสำหรับแบบทดสอบนี้
                      </p>
                    </div>
                  </div>
                )}
                {isGracePeriod && (
                  <div className="bg-red-500 text-white rounded-xl p-4 flex items-center gap-3 shadow-md animate-pulse">
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <div>
                      <h4 className="font-bold text-xs">ช่วงเวลาผ่อนผัน 60 วินาทีสุดท้าย (Grace Period)!</h4>
                      <p className="text-xs text-red-100 mt-0.5">
                        เหลือเวลาอีกเพียง {graceRemainingSeconds} วินาที กรุณากดปุ่ม &ldquo;ส่งคำตอบ&rdquo; ด้านล่างทันที
                      </p>
                    </div>
                  </div>
                )}
                {isWarningPeriod && (
                  <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl p-3.5 text-amber-800 dark:text-amber-200 flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                    <p className="text-xs">
                      <strong>คำเตือน:</strong> เหลือเวลาทำข้อสอบน้อยกว่า 5 นาที ({formatRemainingTime(remainingSeconds!)}) กรุณาเร่งตรวจทานและเตรียมส่งคำตอบ
                    </p>
                  </div>
                )}
                <h1 className="page-heading">{exam.title}</h1>
                <div className="work-summary">
                  <span>{exam.questions.length} ข้อ</span>
                  <span>คะแนนเต็ม {exam.total_score} คะแนน</span>
                  <span>
                    ตอบแล้ว{" "}
                    {
                      exam.questions.filter(
                        (q) =>
                          answers[q.id]?.trim() || questionImages[q.id]?.length,
                      ).length
                    }{" "}
                    / {exam.questions.length} ข้อ
                  </span>
                </div>
                <nav className="question-navigation" aria-label="ไปยังคำถาม">
                  {exam.questions.map((q, i) => (
                    <a
                      key={q.id}
                      href={`#question-${q.id}`}
                      data-answered={Boolean(
                        answers[q.id]?.trim() || questionImages[q.id]?.length,
                      )}
                    >
                      ข้อ {i + 1}
                    </a>
                  ))}
                </nav>
                {exam.questions.map((q, index) => {
                  const previews = imagePreviews[q.id] || [];

                  return (
                    <div
                      key={q.id}
                      id={`question-${q.id}`}
                      className="question-section space-y-4"
                    >
                      {/* Question Title & Score */}
                      <div className="question-heading flex justify-between items-start border-b border-slate-100 dark:border-slate-800 pb-3">
                        <div>
                          <span className="text-xs font-bold text-[#245b50] dark:text-[#91c7b8] uppercase tracking-wider block mb-1">
                            ข้อที่ {index + 1}
                          </span>
                          <h2 className="text-sm font-bold text-slate-900 dark:text-white leading-relaxed">
                            {q.text}
                          </h2>
                        </div>
                        <span className="bg-[#e8eee8] text-[#245b50] dark:bg-[#1A2744] dark:text-[#91c7b8] text-xs font-bold px-3 py-1 rounded-full shrink-0">
                          {q.score} คะแนน
                        </span>
                      </div>

                      {!q.hide_rubric_from_students && q.rubrics && q.rubrics.length > 0 && (
                        <details className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs dark:border-slate-700 dark:bg-slate-900/60">
                          <summary className="cursor-pointer font-semibold text-[#245b50] dark:text-[#91c7b8]">
                            ดูเกณฑ์การให้คะแนน
                          </summary>
                          <div className="mt-3 space-y-2">
                            {q.rubrics.map((rubric, rubricIndex) => (
                              <div key={rubricIndex} className="flex items-start justify-between gap-4 border-t border-slate-200 pt-2 first:border-0 first:pt-0 dark:border-slate-700">
                                <span>
                                  <strong className="block text-slate-800 dark:text-slate-200">{rubric.name}</strong>
                                  {rubric.description && <span className="text-slate-500">{rubric.description}</span>}
                                </span>
                                <span className="shrink-0 font-semibold text-[#245b50] dark:text-[#91c7b8]">{rubric.score} คะแนน</span>
                              </div>
                            ))}
                          </div>
                        </details>
                      )}

                      {/* Text Answer Input */}
                      {(() => {
                        const qAnswer = answers[q.id] || "";
                        const wordCount = countWords(qAnswer);
                        const isOverLimit = wordCount > MAX_WORDS;
                        const isNearLimit = wordCount >= 250 && !isOverLimit;

                        return (
                          <div className="space-y-2">
                            <div className="flex items-center justify-between gap-2 flex-wrap">
                              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                คำตอบของคุณ (พิมพ์ข้อความ):
                              </label>
                              <div className="flex items-center gap-1.5">
                                <span
                                  className={`text-xs font-mono font-medium px-2 py-0.5 rounded-full transition-colors ${
                                    isOverLimit
                                      ? "bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300 font-bold"
                                      : isNearLimit
                                      ? "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
                                      : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                                  }`}
                                >
                                  คำตอบ: {wordCount} / {MAX_WORDS} คำ
                                </span>
                                {isOverLimit && (
                                  <span className="text-[11px] font-bold text-red-600 dark:text-red-400">
                                    (เกิน {wordCount - MAX_WORDS} คำ)
                                  </span>
                                )}
                                {isNearLimit && (
                                  <span className="text-[11px] text-amber-600 dark:text-amber-400">
                                    (ใกล้ครบ 300 คำ)
                                  </span>
                                )}
                              </div>
                            </div>
                            <Textarea
                              rows={3}
                              aria-label={`คำตอบข้อที่ ${index + 1}`}
                              value={answers[q.id] || ""}
                              disabled={isSubmitting || isExpired}
                              onChange={(e) =>
                                setAnswers((prev) => ({
                                  ...prev,
                                  [q.id]: e.target.value,
                                }))
                              }
                              placeholder="พิมพ์คำตอบของคุณสำหรับข้อนี้ (ไม่เกิน 300 คำ)..."
                              className={`bg-[#F8FAFC] dark:bg-[#181818] text-xs leading-relaxed rounded-xl font-mono transition-colors ${
                                isOverLimit
                                  ? "border-red-500 focus-visible:ring-red-500 dark:border-red-600"
                                  : isNearLimit
                                  ? "border-amber-400 focus-visible:ring-amber-400 dark:border-amber-600"
                                  : "border-slate-200 dark:border-slate-700"
                              }`}
                            />
                            {isOverLimit && (
                              <p className="text-[11px] font-medium text-red-600 dark:text-red-400 flex items-center gap-1 pt-0.5">
                                <AlertCircle size={13} className="shrink-0" />
                                คำตอบยาวเกินเกณฑ์ {MAX_WORDS} คำ กรุณาย่อความยาวคำตอบก่อนส่ง
                              </p>
                            )}
                          </div>
                        );
                      })()}

                      {/* Per-Question Image Attachment Section */}
                      <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800/80">
                        <label className="attachment-label text-xs font-semibold text-slate-600 dark:text-slate-400 flex items-center justify-between">
                          <span className="flex items-center gap-1.5">
                            <ImageIcon className="w-3.5 h-3.5 text-[#245b50] dark:text-[#91c7b8]" />
                            แนบรูปภาพลายมือคำตอบสำหรับข้อที่ {index + 1}:
                          </span>
                          <span className="text-[10px] text-slate-400 font-normal">
                            แนบได้ตามต้องการ
                          </span>
                        </label>

                        {/* Image Previews Grid */}
                        {previews.length > 0 && (
                          <div className="flex flex-wrap gap-3 pt-1 pb-2">
                            {previews.map((src, imgIdx) => (
                              <div
                                key={imgIdx}
                                className="relative group w-24 h-24 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800"
                              >
                                <img
                                  src={src}
                                  alt={`ข้อ ${index + 1} รูปที่ ${imgIdx + 1}`}
                                  className="w-full h-full object-cover"
                                />
                                <button
                                  type="button"
                                  aria-label={`ลบรูปที่ ${imgIdx + 1}`}
                                  onClick={() => removeImage(q.id, imgIdx)}
                                  className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 shadow-md hover:bg-red-700 transition"
                                  title="ลบรูปนี้"
                                >
                                  <X size={12} />
                                </button>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Upload Input Button */}
                        <label className="attachment-button inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-dashed border-slate-300 dark:border-slate-700 hover:border-[#1a73e8] dark:hover:border-[#8ab4f8] bg-slate-50 dark:bg-slate-900/50 hover:bg-blue-50/50 dark:hover:bg-blue-950/20 text-slate-600 dark:text-slate-400 text-xs cursor-pointer transition">
                          <Upload
                            size={14}
                            className="text-[#245b50] dark:text-[#91c7b8]"
                          />
                          <span>แนบรูปภาพ (ภาพถ่ายกระดาษคำตอบ/ลายมือ)</span>
                          <input
                            type="file"
                            accept="image/*"
                            multiple
                            onChange={(e) =>
                              handleImageChange(q.id, e.target.files)
                            }
                            className="hidden"
                          />
                        </label>
                      </div>
                    </div>
                  );
                })}

                <div className="action-footer">
                  <p>
                    {isExpired
                      ? "หมดเวลาทำข้อสอบแล้ว ไม่สามารถส่งคำตอบได้"
                      : "ตรวจสอบคำตอบและไฟล์แนบให้ครบก่อนส่ง คำตอบจะถูกส่งเมื่อกดปุ่มด้านล่าง"}
                  </p>
                  <Button
                    type="submit"
                    disabled={isSubmitting || isExpired}
                    className="primary-action w-full"
                  >
                    {isSubmitting ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : isExpired ? (
                      <AlertCircle className="w-4 h-4 mr-2" />
                    ) : (
                      <Send className="w-4 h-4 mr-2" />
                    )}
                    {isSubmitting
                      ? "กำลังส่งคำตอบ…"
                      : isExpired
                      ? "หมดเวลาการส่งข้อสอบแล้ว"
                      : "ส่งคำตอบ"}
                  </Button>
                </div>
              </form>
            ) : (
              /* Post-submission Summary */
              <div className="space-y-4">
                <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 shadow-sm">
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white border-b border-slate-100 dark:border-slate-800 pb-3">
                    สรุปคำตอบที่คุณส่ง
                  </h3>
                  {exam.questions.map((q, idx) => (
                    <div
                      key={q.id}
                      className="space-y-2 text-xs border-b border-slate-100 dark:border-slate-800 pb-3 last:border-0 last:pb-0"
                    >
                      <span className="font-semibold text-slate-700 dark:text-slate-300">
                        ข้อที่ {idx + 1}: {q.text}
                      </span>
                      <div className="p-3 bg-[#F8FAFC] dark:bg-[#181818] rounded-lg font-mono text-slate-800 dark:text-slate-200 border border-slate-100 dark:border-slate-800">
                        {answers[q.id] || "(ไม่มีข้อความคำตอบ)"}
                      </div>
                      {(imagePreviews[q.id]?.length ?? 0) > 0 && (
                        <div className="flex gap-2 pt-1">
                          {imagePreviews[q.id].map((src, i) => (
                            <img
                              key={i}
                              src={src}
                              alt=""
                              className="w-16 h-16 rounded-md object-cover border border-slate-200 dark:border-slate-700"
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <Button
                  onClick={() => navigate(`/room/${roomId}`)}
                  className="w-full bg-[#1a73e8] hover:bg-[#1557b0] text-white font-semibold text-xs h-10 rounded-full"
                >
                  กลับสู่หน้าห้องเรียน
                </Button>
              </div>
            )}
          </>
        )}
      </main>

      <AlertDialog open={showExitConfirm} onOpenChange={setShowExitConfirm}>
        <AlertDialogContent className="max-w-md">
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
              <AlertTriangle size={20} />
              ต้องการออกจากหน้าทำข้อสอบหรือไม่?
            </AlertDialogTitle>
            <AlertDialogDescription className="space-y-2 text-sm text-slate-600 dark:text-slate-300">
              <p>คุณมีคำตอบที่พิมพ์ไว้และยังไม่ได้กดส่งคำตอบ</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                (ระบบได้บันทึกร่างคำตอบไว้ในเบราว์เซอร์เครื่องนี้แล้ว คุณสามารถกลับมาทำต่อได้ตราบใดที่ยังไม่หมดเวลาสอบ)
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="gap-2">
            <AlertDialogCancel>ทำข้อสอบต่อ</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => navigate(`/room/${roomId}`)}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              ออกจากหน้านี้
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
