import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Plus, Trash2, Upload, Calendar, Clock, CheckCircle2, X, ChevronDown, ChevronUp, Image as ImageIcon, Edit3, Save, ArrowLeft, Loader2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
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
  questionImages: string[];  // multiple images
  answerKey: string;
  rubrics: RubricItem[];
  isExpanded: boolean;
  isEditing: boolean;
}

export default function CreateExam() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [isSaving, setIsSaving] = useState(false);

  // Exam meta state
  const [examTitle, setExamTitle] = useState("");
  const [examDescription, setExamDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endDate, setEndDate] = useState("");
  const [endTime, setEndTime] = useState("");

  const [questions, setQuestions] = useState<Question[]>([
    {
      id: Date.now(),
      text: "",
      score: "",
      questionImages: [],
      answerKey: "",
      rubrics: [{ id: Date.now() + 1, name: "", description: "", score: "" }],
      isExpanded: false,
      isEditing: true
    }
  ]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>, qId: number) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setQuestions(prev => prev.map(q =>
          q.id === qId
            ? { ...q, questionImages: [...q.questionImages, reader.result as string] }
            : q
        ));
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (qId: number, imgIdx: number) => {
    setQuestions(prev => prev.map(q =>
      q.id === qId
        ? { ...q, questionImages: q.questionImages.filter((_, i) => i !== imgIdx) }
        : q
    ));
  };

  const addQuestion = () => {
    const updatedQs = questions.map(q => ({ ...q, isEditing: false }));
    setQuestions([...updatedQs, {
      id: Date.now(),
      text: "",
      score: "",
      questionImages: [],
      answerKey: "",
      rubrics: [{ id: Date.now() + 1, name: "", description: "", score: "" }],
      isExpanded: false,
      isEditing: true
    }]);
  };

  const toggleEdit = (qId: number) => {
    setQuestions(questions.map(q =>
      q.id === qId ? { ...q, isEditing: !q.isEditing } : q
    ));
  };

  const toggleExpand = (qId: number) => {
    setQuestions(questions.map(q =>
      q.id === qId ? { ...q, isExpanded: !q.isExpanded } : q
    ));
  };

  const addRubric = (qId: number) => {
    setQuestions(questions.map(q =>
      q.id === qId ? { ...q, rubrics: [...q.rubrics, { id: Date.now(), name: "", description: "", score: "" }] } : q
    ));
  };

  const removeRubric = (qId: number, rId: number) => {
    setQuestions(questions.map(q =>
      q.id === qId ? { ...q, rubrics: q.rubrics.filter(r => r.id !== rId) } : q
    ));
  };

  const duplicateQuestion = (qId: number) => {
    const qToCopy = questions.find(q => q.id === qId);
    if (!qToCopy) return;
    const updatedQs = questions.map(q => ({ ...q, isEditing: false }));
    const newRubrics = qToCopy.rubrics.map(r => ({ ...r, id: Date.now() + Math.random() }));
    setQuestions([...updatedQs, {
      ...qToCopy,
      id: Date.now(),
      questionImages: [...qToCopy.questionImages],
      rubrics: newRubrics,
      isEditing: true
    }]);
  }

  const deleteQuestion = (qId: number) => {
    setQuestions(questions.filter(q => q.id !== qId));
  }

  const handleSave = async () => {
    if (!examTitle.trim()) {
      toast.error("โปรดกรอกชื่อชุดข้อสอบ");
      return;
    }
    const validQs = questions.filter(q => q.text.trim());
    if (validQs.length === 0) {
      toast.error("โปรดเพิ่มคำถามอย่างน้อยหนึ่งข้อ");
      return;
    }

    setIsSaving(true);
    // คำนวณคะแนนรวมจากข้อทั้งหมดอัตโนมัติ
    const computedTotal = validQs.reduce((sum, q) => sum + (parseFloat(q.score) || 0), 0);
    try {
      const payload = {
        title: examTitle,
        description: examDescription || null,
        total_score: computedTotal,
        start_date: startDate && startTime ? `${startDate}T${startTime}` : null,
        end_date: endDate && endTime ? `${endDate}T${endTime}` : null,
        questions: validQs.map((q, i) => ({
          text: q.text,
          score: parseFloat(q.score) || 0,
          answer_key: q.answerKey || null,
          rubrics: q.rubrics.filter(r => r.name).map(r => ({ name: r.name, description: r.description, score: parseFloat(r.score) || 0 })),
          order_index: i,
          question_images_base64: q.questionImages.length > 0 ? q.questionImages : null,
        }))
      };

      const res = await fetch(`/api/rooms/${roomId}/exams`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        toast.success("สร้างข้อสอบสำเร็จ!");
        navigate(`/room/${roomId}`);
      } else {
        const err = await res.json();
        toast.error(err.detail || "บันทึกไม่สำเร็จ");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F7F9] pb-24 md:pb-12">
      <Navbar />

      <main className="max-w-[1000px] mx-auto p-4 md:p-8 space-y-6">
        <button onClick={() => navigate(`/room/${roomId}`)} className="flex items-center gap-2 text-slate-500 hover:text-slate-800 text-sm font-medium">
          <ArrowLeft size={16} /> กลับหน้าห้อง
        </button>

        {/* NEW Exam Meta Section (Distinct Blue Card) */}
        <section className="bg-gradient-to-br from-[#1E3A8A] to-[#3B82F6] p-6 md:p-8 rounded-3xl shadow-[0_10px_40px_-10px_rgba(59,130,246,0.5)] border border-blue-400/20 text-white relative overflow-hidden">
          {/* Background decoration */}
          <div className="absolute top-0 right-0 -mt-10 -mr-10 xl:block hidden opacity-20 pointer-events-none">
            <svg width="250" height="250" viewBox="0 0 250 250" fill="none">
              <circle cx="125" cy="125" r="125" fill="white" />
            </svg>
          </div>

          <div className="relative z-10">
            <h2 className="text-xl md:text-2xl font-bold text-white mb-6">
              ตั้งค่าชุดข้อสอบ
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 md:gap-6 items-end">
              <div className="lg:col-span-6 space-y-2">
                <label className="text-sm font-semibold text-blue-100">ชื่อชุดข้อสอบ</label>
                <Input value={examTitle} onChange={e => setExamTitle(e.target.value)} className="h-12 text-lg border-blue-400/30 bg-blue-900/40 text-white placeholder:text-blue-300 focus:border-white focus:ring-1 focus:ring-white transition-all shadow-inner hover:bg-blue-900/60" placeholder="เช่น สอบกลางภาควิชา..." />
              </div>
              <div className="lg:col-span-4 space-y-2">
                <label className="text-sm font-semibold text-blue-100">รายละเอียดการสอบ</label>
                <Input value={examDescription} onChange={e => setExamDescription(e.target.value)} className="h-12 text-base border-blue-400/30 bg-blue-900/40 text-white placeholder:text-blue-300 transition-all shadow-inner hover:bg-blue-900/60" placeholder="คำอธิบายเพิ่มเติม..." />
              </div>
              <div className="lg:col-span-2 flex flex-col items-center justify-center bg-white/10 rounded-xl px-4 py-3 border border-white/20">
                <span className="text-xs text-blue-200 font-semibold uppercase tracking-wider mb-1">คะแนนรวม</span>
                <span className="text-3xl font-black text-white">
                  {questions.reduce((sum, q) => sum + (parseFloat(q.score) || 0), 0)}
                </span>
                <span className="text-xs text-blue-300 mt-0.5">คะแนน (อัตโนมัติ)</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6 mt-6 pt-6 border-t border-blue-400/30">
              <div className="space-y-3">
                <label className="text-sm font-medium text-blue-100 flex items-center gap-2"><Calendar className="w-4 h-4" /> เริ่มสอบ</label>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="h-11 border-blue-400/30 bg-blue-900/40 text-white flex-1 hover:bg-blue-900/60 [color-scheme:dark]" />
                  <Input type="time" value={startTime} onChange={e => setStartTime(e.target.value)} className="h-11 border-blue-400/30 bg-blue-900/40 text-white sm:w-32 hover:bg-blue-900/60 [color-scheme:dark]" />
                </div>
              </div>
              <div className="space-y-3">
                <label className="text-sm font-medium text-blue-100 flex items-center gap-2"><Clock className="w-4 h-4" /> สิ้นสุด</label>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="h-11 border-blue-400/30 bg-blue-900/40 text-white flex-1 hover:bg-blue-900/60 [color-scheme:dark]" />
                  <Input type="time" value={endTime} onChange={e => setEndTime(e.target.value)} className="h-11 border-blue-400/30 bg-blue-900/40 text-white sm:w-32 hover:bg-blue-900/60 [color-scheme:dark]" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Questions Header */}
        <div className="flex items-center justify-between pt-4">
          <h2 className="text-xl md:text-2xl font-black text-gray-800 tracking-tight">คำถามทั้งหมด <span className="text-[#3B82F6]">({questions.length} ข้อ)</span></h2>
          {questions.length > 0 && !questions.every(q => !q.isEditing) && (
            <Button variant="ghost" className="text-sm text-gray-500 hover:bg-gray-200" onClick={() => setQuestions(questions.map(q => ({ ...q, isEditing: false })))}>
              ย่อเก็บทั้งหมด
            </Button>
          )}
        </div>

        {/* Question Cards Loop */}
        <div className="space-y-5">
          {questions.map((q, index) => (
            <div key={q.id}>
              {q.isEditing ? (
                // -------- EDIT MODE (Fully Expanded) --------
                <div className="bg-white rounded-2xl shadow-lg shadow-blue-900/5 border-2 border-[#3B82F6] overflow-hidden relative transition-all duration-300 transform origin-top animate-in fade-in-0 zoom-in-[0.98]">

                  {/* Top Control Bar for Edit Mode */}
                  <div className="bg-[#eff6ff] px-5 py-3 border-b border-blue-100 flex justify-between items-center">
                    <span className="text-sm font-bold text-[#3B82F6]">แก้ไขคำถามข้อที่ {index + 1}</span>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" onClick={() => duplicateQuestion(q.id)} className="h-8 text-[#3B82F6] bg-blue-100 hover:bg-blue-200 rounded-full px-4 text-xs font-bold">คัดลอกข้อนี้</Button>
                      <Button variant="ghost" size="icon" onClick={() => deleteQuestion(q.id)} className="h-8 w-8 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-full"><Trash2 size={16} /></Button>
                    </div>
                  </div>

                  <div className="p-5 md:p-8 relative z-10 w-full">
                    {/* Header Row */}
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-5 md:mb-6 gap-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-600 text-white rounded-xl flex items-center justify-center font-bold text-lg shadow-sm">
                          {index + 1}
                        </div>
                        <div className="bg-red-50 text-red-600 border border-red-100 px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase">
                          * จำเป็น
                        </div>
                      </div>
                      <div className="flex items-center justify-between w-full md:w-auto gap-3 bg-gray-50 px-4 py-2 rounded-xl border border-gray-200">
                        <span className="text-sm md:text-base font-semibold text-gray-700">คะแนนเต็ม :</span>
                        <Input className="w-20 h-10 border-gray-300 text-center font-bold text-xl text-[#3B82F6] bg-white shadow-inner" placeholder="0"
                          value={q.score} onChange={(e) => {
                            setQuestions(questions.map(qx => qx.id === q.id ? { ...qx, score: e.target.value } : qx))
                          }}
                        />
                      </div>
                    </div>

                    <Textarea
                      className="w-full min-h-[140px] text-base md:text-lg p-5 border-gray-300 rounded-xl bg-gray-50/50 hover:bg-white focus:bg-white transition-colors focus:ring-2 focus:ring-[#3B82F6]/20 focus:border-[#3B82F6] resize-none"
                      placeholder="พิมพ์โจทย์คำถามที่นี่..."
                      value={q.text}
                      onChange={(e) => setQuestions(questions.map(qx => qx.id === q.id ? { ...qx, text: e.target.value } : qx))}
                    />

                    {/* Multi-image gallery */}
                    {q.questionImages.length > 0 && (
                      <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-3">
                        {q.questionImages.map((img, imgIdx) => (
                          <div key={imgIdx} className="relative group rounded-xl overflow-hidden border-2 border-gray-200 aspect-video bg-gray-50">
                            <img src={img} alt={`รูป ${imgIdx + 1}`} className="w-full h-full object-cover" />
                            <button
                              onClick={() => removeImage(q.id, imgIdx)}
                              className="absolute top-1 right-1 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <X size={12} />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="mt-4">
                      <input
                        type="file"
                        id={`q-upload-${q.id}`}
                        className="hidden"
                        accept="image/*"
                        multiple
                        onChange={(e) => handleImageUpload(e, q.id)}
                      />
                      <Button
                        variant="outline"
                        onClick={() => document.getElementById(`q-upload-${q.id}`)?.click()}
                        className="h-12 px-6 border-gray-300 text-gray-700 hover:bg-blue-50 hover:text-[#3B82F6] hover:border-blue-200 font-semibold w-full md:w-auto shadow-sm transition-all rounded-xl"
                      >
                        <ImageIcon className="w-5 h-5 mr-3" />
                        {q.questionImages.length > 0 ? `เพิ่มรูปภาพ (มีแล้ว ${q.questionImages.length} รูป)` : "แนบรูปภาพประกอบคำถาม"}
                      </Button>
                    </div>

                    {/* TOGGLE BUTTON AREA */}
                    <div className="mt-8 pt-6 border-t border-gray-100 flex flex-col items-center">
                      <Button
                        variant="ghost"
                        onClick={() => toggleExpand(q.id)}
                        className={`
                          w-full md:w-auto h-12 px-8 rounded-full text-sm font-bold transition-all duration-300
                          ${q.isExpanded
                            ? "bg-gray-100 text-gray-500 hover:bg-gray-200"
                            : "bg-[#eff6ff] text-[#3B82F6] hover:bg-blue-100 border border-blue-200 hover:scale-105"
                          }
                        `}
                      >
                        {q.isExpanded ? (
                          <><ChevronUp size={18} className="mr-2" /> ซ่อนรูปแบบและเกณฑ์การให้คะแนน</>
                        ) : (
                          <><ChevronDown size={18} className="mr-2" /> เพิ่มธงคำตอบและเกณฑ์รูบริค</>
                        )}
                      </Button>
                    </div>
                  </div>

                  {/* RUBRICS & ANSWERS EXPANDED AREA */}
                  {q.isExpanded && (
                    <div className="bg-[#F8FAFC] border-t border-gray-200 p-5 md:p-8 animate-in slide-in-from-top-4 duration-300">

                      <div className="space-y-8 bg-white p-6 md:p-8 rounded-2xl border border-gray-200 shadow-sm">
                        {/* Model Answer */}
                        <div className="space-y-4">
                          <label className="text-lg font-bold text-gray-800 flex items-center justify-between">
                            <span>แนวคำตอบที่สมบูรณ์ (ธงคำตอบ)</span>
                            <span className="text-xs text-gray-400 font-bold border px-2 py-0.5 rounded uppercase tracking-wide bg-gray-50">Optional</span>
                          </label>
                          <Textarea
                            className="w-full min-h-[120px] text-base p-4 border-gray-300 rounded-xl bg-gray-50 focus:bg-white transition-colors focus:ring-2 focus:ring-[#3B82F6]/20"
                            placeholder="พิมพ์เฉลยที่ถูกต้องเพื่อใช้เป็นต้นแบบในการตรวจ..."
                            value={q.answerKey}
                            onChange={(e) => setQuestions(questions.map(qx => qx.id === q.id ? { ...qx, answerKey: e.target.value } : qx))}
                          />

                        </div>

                        {/* Rubrics */}
                        <div className="border-t border-gray-200 pt-8 mt-8">
                          <h4 className="text-xl font-bold text-[#1e293b] mb-6 flex items-center gap-3">
                            <span className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-[#3B82F6]">
                              <CheckCircle2 size={18} />
                            </span>
                            เกณฑ์การให้คะแนน (Rubrics)
                          </h4>

                          <div className="space-y-4">
                            {/* Dynamic Rows */}
                            {q.rubrics.map((r, rIndex) => (
                              <div key={r.id} className="flex flex-col md:grid md:grid-cols-12 gap-3 md:gap-4 items-start bg-white p-5 rounded-2xl border-2 border-gray-100 hover:border-[#3B82F6]/30 transition-all shadow-sm relative">
                                <div className="absolute top-4 right-4 md:hidden text-sm text-gray-300 font-black">
                                  #{rIndex + 1}
                                </div>
                                <div className="w-full md:col-span-4 flex flex-col gap-2">
                                  <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">หัวข้อเกณฑ์</label>
                                  <Input className="h-11 border-gray-200 bg-gray-50 focus:bg-white pr-8 md:pr-3 rounded-lg" placeholder="เช่น ไวยากรณ์, สูตรถูกต้อง"
                                    value={r.name} onChange={(e) => {
                                      const newRs = q.rubrics.map(rx => rx.id === r.id ? { ...rx, name: e.target.value } : rx);
                                      setQuestions(questions.map(qx => qx.id === q.id ? { ...qx, rubrics: newRs } : qx))
                                    }}
                                  />
                                </div>
                                <div className="w-full md:col-span-8 lg:col-span-6 flex flex-col gap-2">
                                  <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">รายละเอียดเกณฑ์</label>
                                  <Textarea className="min-h-[44px] h-11 py-2.5 border-gray-200 bg-gray-50 focus:bg-white resize-none rounded-lg" placeholder="อธิบายเงื่อนไข..."
                                    value={r.description} onChange={(e) => {
                                      const newRs = q.rubrics.map(rx => rx.id === r.id ? { ...rx, description: e.target.value } : rx);
                                      setQuestions(questions.map(qx => qx.id === q.id ? { ...qx, rubrics: newRs } : qx))
                                    }}
                                  />
                                </div>

                                <div className="flex w-full lg:contents items-center justify-between gap-4 mt-3 md:mt-0">
                                  <div className="flex-1 lg:flex-none w-full lg:col-span-1 flex flex-col gap-2">
                                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wider lg:text-center block">คะแนน</label>
                                    <Input className="h-11 border-blue-200 bg-blue-50 text-center font-bold w-full text-[#3B82F6] rounded-lg text-lg shadow-inner" placeholder="0"
                                      value={r.score} onChange={(e) => {
                                        const newRs = q.rubrics.map(rx => rx.id === r.id ? { ...rx, score: e.target.value } : rx);
                                        setQuestions(questions.map(qx => qx.id === q.id ? { ...qx, rubrics: newRs } : qx))
                                      }}
                                    />
                                  </div>
                                  <div className="lg:col-span-1 flex justify-center pt-6 lg:pt-8 w-auto">
                                    <button
                                      onClick={() => removeRubric(q.id, r.id)}
                                      className="text-gray-400 hover:text-red-500 transition-colors bg-white lg:bg-gray-50 rounded-xl px-4 py-2.5 lg:w-11 lg:h-11 lg:px-0 lg:py-0 flex items-center justify-center shadow-sm lg:shadow-none border border-gray-200 lg:border-none gap-2 hover:bg-red-50"
                                    >
                                      <Trash2 className="w-4 h-4 lg:w-5 lg:h-5" />
                                      <span className="text-sm font-bold lg:hidden text-red-500">ลบ</span>
                                    </button>
                                  </div>
                                </div>
                              </div>
                            ))}

                            <Button
                              variant="outline"
                              onClick={() => addRubric(q.id)}
                              className="mt-4 w-full h-12 text-[#3B82F6] hover:text-[#2563eb] border-dashed border-2 border-blue-200 hover:border-blue-400 hover:bg-blue-50 font-bold rounded-xl"
                            >
                              <Plus className="w-5 h-5 mr-2" /> เพิ่มเกณฑ์ข้อใหม่
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Bottom Finish Edit Bar */}
                  <div className="bg-gray-900 p-4 flex justify-end items-center">
                    <span className="text-gray-400 text-xs hidden md:block mr-4">ข้อสอบถูกบันทึกอัตโนมัติแล้ว</span>
                    <Button className="w-full md:w-auto bg-white text-gray-900 hover:bg-gray-100 rounded-xl h-12 px-8 font-bold text-base shadow-lg" onClick={() => toggleEdit(q.id)}>
                      <CheckCircle2 className="w-5 h-5 mr-2 text-green-500" /> พับเก็บข้อนี้ให้เรียบร้อย
                    </Button>
                  </div>
                </div>
              ) : (
                // -------- VIEW MODE (Collapsed Accordion) --------
                <div
                  onClick={() => toggleEdit(q.id)}
                  className="bg-white p-4 h-24 rounded-2xl shadow-sm border border-gray-200 cursor-pointer hover:border-[#3B82F6] hover:shadow-md transition-all flex items-center justify-between group overflow-hidden"
                >
                  <div className="flex gap-4 md:gap-5 items-center w-2/3 md:w-3/4 overflow-hidden h-full">
                    <div className="w-12 h-12 bg-gray-50 text-gray-400 group-hover:bg-[#ebf5ff] group-hover:text-[#3B82F6] rounded-xl flex items-center justify-center font-black text-lg shrink-0 transition-all group-hover:scale-105">
                      {index + 1}
                    </div>
                    <div className="truncate text-gray-700 font-semibold text-base md:text-lg">
                      {q.text ? q.text : <span className="text-gray-300 italic font-normal">กำลังสร้างคำถาม... แตะเพื่อแก้ไข</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 md:gap-4 shrink-0 px-2">
                    <div className="bg-blue-50 border border-blue-100 px-4 py-1.5 text-sm font-bold text-[#3B82F6] rounded-xl whitespace-nowrap hidden sm:block">
                      {q.score || '0'} คะแนน
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gray-50 group-hover:bg-[#3B82F6] flex items-center justify-center transition-all group-hover:shadow-[0_4px_10px_rgba(59,130,246,0.3)]">
                      <Edit3 size={18} className="text-gray-400 group-hover:text-white" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          <Button
            onClick={addQuestion}
            className="w-full h-16 mt-6 text-lg font-bold bg-white border-2 border-dashed border-[#d1d5db] text-gray-500 hover:border-[#3B82F6] hover:text-[#3B82F6] hover:bg-blue-50/50 transition-all rounded-2xl shadow-sm"
          >
            <Plus className="w-6 h-6 mr-3" /> เพิ่มโจทย์ข้อที่ {questions.length + 1}
          </Button>
          <div className="flex flex-col md:flex-row gap-4 justify-end items-center mt-10 md:mt-12 pt-8 border-t border-gray-200">
            <div className="flex-1 md:flex-none flex items-center justify-center md:justify-start w-full md:w-auto md:mr-auto">
              <span className="text-gray-400 text-sm flex items-center gap-2">
                <CheckCircle2 size={16} className="text-green-500" /> บันทึกร่างอัตโนมัติ (Autosaved)
              </span>
            </div>

            <button onClick={() => navigate(`/room/${roomId}`)} className="w-full md:w-auto h-14 md:h-12 px-8 text-gray-500 hover:bg-gray-200 font-bold rounded-xl text-base transition-colors">
              กลับไปหน้ารวม
            </button>

            <Button
              onClick={handleSave}
              disabled={isSaving}
              className="w-full md:w-auto h-14 md:h-12 px-10 bg-[#3B82F6] text-white hover:bg-blue-600 shadow-lg shadow-blue-500/25 font-black text-lg rounded-xl"
            >
              {isSaving ? <><Loader2 size={18} className="mr-2 animate-spin" /> กำลังบันทึก...</> : "บันทึกและพร้อมสอบ"}
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}