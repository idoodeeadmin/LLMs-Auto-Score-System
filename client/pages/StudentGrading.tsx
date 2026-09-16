import { WorkspaceBreadcrumb } from "@/components/WorkspaceHeader";
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Sparkles,
  Check,
  Sliders,
  Loader2,
  User,
  ImageIcon,
  ShieldCheck,
  AlertCircle,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { toast } from "sonner";

interface AnswerItem {
  id: number;
  question_id: number;
  question_text: string;
  max_score: number;
  answer_text: string;
  image_paths?: string[];
  ai_score: number;
  ai_feedback: string;
  ai_confidence?: "high" | "medium" | "low" | string;
  teacher_score?: number | null;
  teacher_comment?: string | null;
}

interface SubmissionDetail {
  submission: {
    id: number;
    status: string;
    total_score: number;
    submitted_at: string;
  };
  student: {
    id: number;
    name: string;
    email: string;
    student_code?: string;
  };
  answers: AnswerItem[];
}

export default function StudentGrading() {
  const { roomId, examId, studentId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [data, setData] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [isApproving, setIsApproving] = useState(false);

  // Per-question teacher scores and comments
  const [teacherScores, setTeacherScores] = useState<{ [qId: string]: number }>(
    {},
  );
  const [teacherComments, setTeacherComments] = useState<{
    [qId: string]: string;
  }>({});

  useEffect(() => {
    const fetchSubmission = async () => {
      try {
        setLoading(true);
        const res = await fetch(
          `/api/rooms/${roomId}/exams/${examId}/submissions/${studentId}`,
          {
            headers: { Authorization: token ? `Bearer ${token}` : "" },
          },
        );
        if (res.ok) {
          const detail: SubmissionDetail = await res.json();
          setData(detail);

          // Initialize teacher score / comment with existing or AI scores
          const scores: { [qId: string]: number } = {};
          const comments: { [qId: string]: string } = {};
          detail.answers.forEach((ans) => {
            scores[ans.question_id.toString()] =
              ans.teacher_score ?? ans.ai_score ?? 0;
            comments[ans.question_id.toString()] = ans.teacher_comment ?? "";
          });
          setTeacherScores(scores);
          setTeacherComments(comments);
        } else {
          toast.error("ไม่พบข้อมูลการส่งข้อสอบของนิสิตคนนี้");
        }
      } catch (err) {
        console.error("Error fetching student submission:", err);
      } finally {
        setLoading(false);
      }
    };

    if (roomId && examId && studentId) {
      fetchSubmission();
    }
  }, [roomId, examId, studentId, token]);

  const handleApprove = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!data) return;

    setIsApproving(true);
    try {
      const res = await fetch(
        `/api/rooms/${roomId}/exams/${examId}/submissions/${studentId}/approve`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : "",
          },
          body: JSON.stringify({
            teacher_scores: teacherScores,
            teacher_comments: teacherComments,
          }),
        },
      );

      if (res.ok) {
        toast.success("อนุมัติและประกาศผลคะแนนเรียบร้อยแล้ว!");
        navigate(`/room/${roomId}`);
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "เกิดข้อผิดพลาดในการอนุมัติคะแนน");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsApproving(false);
    }
  };

  const totalTeacherScore = Object.values(teacherScores).reduce(
    (sum, s) => sum + (Number(s) || 0),
    0,
  );
  const totalMaxScore =
    data?.answers.reduce((sum, a) => sum + (Number(a.max_score) || 0), 0) || 0;

  const renderConfidenceBadge = (confidence?: string) => {
    const conf = confidence?.toLowerCase();
    if (conf === "high") {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 px-2.5 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
          <ShieldCheck
            size={12}
            className="text-emerald-600 dark:text-emerald-400"
          />
          ระดับความมั่นใจ: สูง (High)
        </span>
      );
    }
    if (conf === "low") {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-semibold bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 px-2.5 py-0.5 rounded-full border border-rose-200 dark:border-rose-800">
          <AlertCircle size={12} className="text-rose-600 dark:text-rose-400" />
          ระดับความมั่นใจ: ต่ำ (Low - แนะนำตรวจทาน)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-semibold bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 px-2.5 py-0.5 rounded-full border border-amber-200 dark:border-amber-800">
        <AlertTriangle
          size={12}
          className="text-amber-600 dark:text-amber-400"
        />
        ระดับความมั่นใจ: ปานกลาง (Medium)
      </span>
    );
  };

  return (
    <div className="workspace">
      {/* Top Navbar */}
      <header className="task-header sticky top-0 z-40 bg-white dark:bg-[#1E1E1E] border-b border-slate-200 dark:border-slate-800 px-8 py-3.5 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(`/room/${roomId}`)}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-[#245b50] transition"
          >
            <ArrowLeft size={16} />
            <span className="task-header-back-label">กลับห้องเรียน</span>
          </button>
          <h1 className="font-semibold text-base text-slate-900 dark:text-white">
            ตรวจทานคำตอบ
          </h1>
        </div>

        <ThemeToggle />
      </header>

      <main className="document-page">
        <WorkspaceBreadcrumb roomId={roomId} current="ตรวจทานคำตอบ" />
        {loading ? (
          <div className="py-20 flex justify-center text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        ) : !data ? (
          <div className="py-16 text-center text-slate-400 bg-white dark:bg-[#1E1E1E] rounded-2xl border border-slate-200 dark:border-slate-800 p-8">
            <p>ไม่พบข้อมูลการส่งข้อสอบของนิสิต</p>
          </div>
        ) : (
          <form onSubmit={handleApprove} className="exam-paper">
            <h1 className="page-heading mb-2">ตรวจทานคำตอบ</h1>
            <p className="page-description mb-6">
              อ่านคำตอบ ตรวจสอบคะแนนที่ระบบเสนอ และปรับคะแนนก่อนประกาศผล
            </p>
            {/* Student Info Card */}
            <div className="work-summary justify-between">
              <div className="review-summary-status flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#e8eee8] dark:bg-[#1A2744] text-[#245b50] dark:text-[#91c7b8] flex items-center justify-center font-bold">
                  <User size={20} />
                </div>
                <div>
                  <h2 className="font-bold text-slate-900 dark:text-white text-base">
                    {data.student.name}{" "}
                    {data.student.student_code
                      ? `(${data.student.student_code})`
                      : ""}
                  </h2>
                  <span className="text-xs text-slate-400">
                    {data.student.email}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full border ${
                    data.submission.status === "approved"
                      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border-emerald-200"
                      : "bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300 border-blue-200"
                  }`}
                >
                  สถานะ:{" "}
                  {data.submission.status === "approved"
                    ? "อนุมัติแล้ว"
                    : "รออาจารย์ตรวจทาน"}
                </span>
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  รวม: {totalTeacherScore.toFixed(1)} / {totalMaxScore} คะแนน
                </span>
              </div>
            </div>

            {/* Questions & Answers Review List */}
            {data.answers.map((ans, idx) => {
              const qIdStr = ans.question_id.toString();
              const currentScore = teacherScores[qIdStr] ?? ans.ai_score ?? 0;
              const currentComment = teacherComments[qIdStr] ?? "";

              return (
                <div
                  key={ans.id || ans.question_id}
                  className="question-section space-y-5"
                >
                  {/* Question Header */}
                  <div className="question-heading flex justify-between items-start border-b border-slate-100 dark:border-slate-800 pb-4">
                    <div>
                      <span className="text-xs font-bold text-[#245b50] dark:text-[#91c7b8] uppercase tracking-wider block mb-1">
                        ข้อที่ {idx + 1}
                      </span>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-relaxed">
                        {ans.question_text}
                      </h3>
                    </div>
                    <span className="bg-[#e8eee8] text-[#245b50] dark:bg-[#1A2744] dark:text-[#91c7b8] text-xs font-bold px-3 py-1 rounded-full shrink-0">
                      เต็ม {ans.max_score} คะแนน
                    </span>
                  </div>

                  {/* Student Answer */}
                  <div className="space-y-2">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                      คำตอบของนิสิต:
                    </span>
                    <div className="text-xs text-slate-800 dark:text-slate-200 bg-[#F8FAFC] dark:bg-[#181818] border border-slate-100 dark:border-slate-700 rounded-xl p-4 leading-relaxed font-mono">
                      {ans.answer_text || "(ไม่มีข้อความ)"}
                    </div>

                    {/* OCR Attached Images */}
                    {ans.image_paths && ans.image_paths.length > 0 && (
                      <div className="pt-2">
                        <span className="text-xs font-semibold text-slate-500 flex items-center gap-1 mb-2">
                          <ImageIcon size={14} /> รูปภาพกระดาษคำตอบที่แนบมา:
                        </span>
                        <div className="flex flex-wrap gap-3">
                          {ans.image_paths.map((imgUrl, imgIdx) => (
                            <a
                              key={imgIdx}
                              href={imgUrl}
                              target="_blank"
                              rel="noreferrer"
                              className="block w-28 h-28 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 hover:opacity-90 transition"
                            >
                              <img
                                src={imgUrl}
                                alt={`ข้อ ${idx + 1} รูปที่ ${imgIdx + 1}`}
                                className="w-full h-full object-cover"
                              />
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Real AI Result Card with Confidence Badge */}
                  <div className="review-assistance space-y-3">
                    <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                      <span className="font-bold text-xs text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                        ผลการประเมินจาก GPT-5.6 Luna:
                      </span>

                      <div className="flex items-center gap-2 flex-wrap">
                        {renderConfidenceBadge(ans.ai_confidence)}
                        <span className="font-bold text-xs text-[#188038] dark:text-emerald-400">
                          AI ให้คะแนน: {ans.ai_score} / {ans.max_score} คะแนน
                        </span>
                      </div>
                    </div>

                    {ans.ai_feedback && (
                      <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed pl-5 border-l-2 border-slate-300 dark:border-slate-600">
                        {ans.ai_feedback}
                      </p>
                    )}
                  </div>

                  {/* Teacher Override Inputs for this Question */}
                  <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-3">
                    <div className="score-editor flex justify-between items-center">
                      <label className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                        <Sliders size={14} className="text-slate-700" />
                        คะแนนที่ให้
                      </label>
                      <div className="flex items-center gap-1">
                        <input
                          type="number"
                          step="0.5"
                          min="0"
                          max={ans.max_score}
                          value={currentScore}
                          aria-label={`คะแนนที่ให้ข้อ ${idx + 1}`}
                          onChange={(e) => {
                            const val = parseFloat(e.target.value) || 0;
                            setTeacherScores((prev) => ({
                              ...prev,
                              [qIdStr]: val,
                            }));
                          }}
                          className="w-14 text-center font-bold text-sm bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg py-1 text-slate-700 dark:text-slate-300 focus:outline-none"
                        />
                        <span className="text-xs text-slate-400">
                          / {ans.max_score}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[11px] font-medium text-slate-500">
                        ข้อเสนอแนะถึงผู้เรียน
                      </label>
                      <Textarea
                        rows={2}
                        value={currentComment}
                        aria-label={`ข้อเสนอแนะข้อ ${idx + 1}`}
                        onChange={(e) =>
                          setTeacherComments((prev) => ({
                            ...prev,
                            [qIdStr]: e.target.value,
                          }))
                        }
                        placeholder="พิมพ์คำแนะนำเพิ่มเติมให้นิสิตในข้อนี้..."
                        className="bg-[#F8FAFC] dark:bg-[#181818] border-slate-200 dark:border-slate-700 text-xs rounded-xl"
                      />
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Submit Approval Button */}
            <Button
              type="submit"
              disabled={isApproving}
              className="primary-action w-full mt-6"
            >
              {isApproving ? (
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <Check className="w-5 h-5 mr-2" />
              )}
              {isApproving
                ? "กำลังบันทึกคะแนน..."
                : `อนุมัติและประกาศผลคะแนนสุทธิ (${totalTeacherScore.toFixed(1)} / ${totalMaxScore} คะแนน)`}
            </Button>
          </form>
        )}
      </main>
    </div>
  );
}
