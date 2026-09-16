import { WorkspaceBreadcrumb } from "@/components/WorkspaceHeader";
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Plus,
  X,
  Loader2,
  Save,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
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
}

export default function CreateExam() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [isSaving, setIsSaving] = useState(false);

  const [examTitle, setExamTitle] = useState("");
  const [examDescription, setExamDescription] = useState("");

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
    1: true,
  });

  const totalScore = questions.reduce(
    (sum, q) => sum + (parseFloat(q.score) || 0),
    0,
  );

  const updateQuestion = (id: number, patch: Partial<Question>) => {
    setQuestions((prev) =>
      prev.map((q) => (q.id === id ? { ...q, ...patch } : q)),
    );
  };

  const toggleDetails = (qId: number) => {
    setShowDetails((prev) => ({ ...prev, [qId]: !(prev[qId] ?? true) }));
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
          start_date: null,
          end_date: null,
          is_randomized: 0,
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
            question_images_base64: null,
          })),
        }),
      }).catch(() => null);

      if (res && res.ok) {
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
    <div className="workspace">
      {/* Clean Top Navbar */}
      <div className="task-header sticky top-0 z-40 bg-white dark:bg-[#1E1E1E] border-b border-slate-200 dark:border-slate-800 px-8 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={() => navigate(`/room/${roomId}`)}
            className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition"
          >
            <ArrowLeft size={18} />
          </button>
          <div className="task-header-title flex flex-col min-w-0">
            <input
              type="text"
              aria-label="ชื่อข้อสอบ"
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

        <div className="task-header-actions flex items-center gap-3">
          <ThemeToggle />

          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="primary-action"
          >
            {isSaving ? (
              <Loader2 size={15} className="animate-spin mr-1" />
            ) : (
              <Save size={15} className="mr-1" />
            )}
            บันทึกสร้างข้อสอบ
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
          <span>ยังไม่บันทึก · กดบันทึกข้อสอบเมื่อพร้อม</span>
        </div>
        <div className="exam-paper space-y-8">
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
              const isOpen = showDetails[q.id] ?? true;

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

                  {/* Single Toggle Button for Answer Key & Rubrics */}
                  <div className="pl-6">
                    <button
                      type="button"
                      onClick={() => toggleDetails(q.id)}
                      className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-[#245b50] dark:hover:text-[#8ab4f8] font-medium py-1 transition"
                    >
                      {isOpen ? (
                        <ChevronDown size={14} />
                      ) : (
                        <ChevronRight size={14} />
                      )}
                      <span>
                        {isOpen
                          ? "ซ่อนแนวคำตอบและเกณฑ์คะแนน"
                          : "แสดงแนวคำตอบและเกณฑ์คะแนน (ธง & Rubrics)"}
                      </span>
                    </button>
                  </div>

                  {/* Collapsible Details Area (Answer Key + Rubrics) */}
                  {isOpen && (
                    <div className="pl-6 space-y-4 pt-1">
                      {/* Model Answer Key */}
                      <div className="space-y-1 bg-slate-50/50 dark:bg-slate-900/30 p-3 rounded-lg border border-slate-100 dark:border-slate-800/60">
                        <label className="text-[11px] font-medium text-slate-400 block">
                          แนวคำตอบ / ธงคำตอบ (Model Answer):
                        </label>
                        <Textarea
                          aria-label={`แนวคำตอบข้อที่ ${index + 1}`}
                          rows={3}
                          value={q.answerKey}
                          onChange={(e) =>
                            updateQuestion(q.id, { answerKey: e.target.value })
                          }
                          placeholder="พิมพ์แนวทางคำตอบหรือธงคำตอบสำหรับข้อนี้ เพื่อใช้เป็นเกณฑ์ประกอบการตรวจของ AI..."
                          className="w-full text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 focus:border-[#1a73e8] focus:outline-none p-2 rounded-md text-slate-700 dark:text-slate-300 resize-y"
                        />
                      </div>

                      {/* Flat Rubrics Section */}
                      <div className="space-y-3">
                        <div className="flex flex-wrap justify-between items-center gap-2">
                          <div className="flex items-center gap-2">
                            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                              เกณฑ์การให้คะแนน (Rubrics)
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
                        </div>

                        {/* Clean Flat Table */}
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
                                  คำอธิบายรายละเอียด
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
                          + เพิ่มเกณฑ์ Rubric
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
                  },
                ]);
                setShowDetails((prev) => ({ ...prev, [newId]: true }));
              }}
              variant="ghost"
              className="text-xs text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
            >
              + แทรกข้อสอบถัดไป
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
