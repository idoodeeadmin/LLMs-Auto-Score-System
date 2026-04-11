import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import {
  ChevronLeft, ChevronRight, CheckCircle2, AlertTriangle,
  MessageSquare, BookOpen, AlertCircle, X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useNavigate, useParams } from "react-router-dom";

// Mock Data Types
interface Rubric {
  id: number;
  label: string;
  maxScore: number;
}

interface QuestionData {
  id: number;
  questionText: string;
  totalScore: number;
  studentAnswer: string;
  studentAttachment?: string;
  aiScore: number;
  aiFeedback: string;
  aiConfidence: "high" | "medium" | "low";
  rubrics: Rubric[];
}

export default function StudentGrading() {
  const navigate = useNavigate();
  const { roomId, examId, studentId } = useParams();

  // State สำหรับ Modal ยืนยัน
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  // Mock Students List
  const [studentsList, setStudentsList] = useState([
    { id: "1", name: "นาย ก", status: "needs_review" },
    { id: "2", name: "นาย ข", status: "ready" },
    { id: "3", name: "นาย ค", status: "ready" },
  ]);

  const [currentStudentIndex, setCurrentStudentIndex] = useState(0);
  const [scores, setScores] = useState<Record<number, number>>({ 1: 4, 2: 5 });

  const currentStudent = studentsList[currentStudentIndex];

  // Auto Scroll to Top
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentStudentIndex]);

  // Mock Exam Data
  const questions: QuestionData[] = [
    {
      id: 1,
      questionText: "จงอธิบายความแตกต่างระหว่าง Stack และ Queue ในเชิงการเข้าถึงข้อมูล (Data Access) พร้อมยกตัวอย่างสถานการณ์ในชีวิตจริง",
      totalScore: 5,
      studentAnswer: "Stack ใช้หลักการ LIFO (เข้าทีหลังออกก่อน) เช่น การวางจานซ้อนกัน ส่วน Queue ใช้หลักการ FIFO (เข้าก่อนออกก่อน) เช่น การต่อแถวซื้อของ",
      studentAttachment: "https://placehold.co/400x300/EEE/31343C?text=Diagram",
      aiScore: 4,
      aiFeedback: "คำตอบถูกต้องตามหลักการพื้นฐาน แต่ตัวอย่างของ Stack ยังสามารถอธิบายเพิ่มเติมเรื่องการนำไปใช้ในคอมพิวเตอร์ได้ เช่น Undo function",
      aiConfidence: "high",
      rubrics: [
        { id: 1, label: "ความถูกต้องของนิยาม", maxScore: 3 },
        { id: 2, label: "ความชัดเจนของตัวอย่าง", maxScore: 2 }
      ]
    },
    {
      id: 2,
      questionText: "Array มีประสิทธิภาพในการค้นหาข้อมูล (Search) ดีกว่า Linked List หรือไม่ เพราะเหตุใด?",
      totalScore: 5,
      studentAnswer: "ดีกว่า เพราะ Array มี Index ทำให้เข้าถึงข้อมูลได้ทันที O(1) แต่ Linked List ต้องไล่หาทีละตัว",
      aiScore: 5,
      aiFeedback: "ถูกต้องครบถ้วน อธิบายเรื่อง Big O Notation ได้ดี",
      aiConfidence: "high",
      rubrics: [
        { id: 1, label: "ความถูกต้อง", maxScore: 5 }
      ]
    }
  ];

  const handlePrev = () => {
    if (currentStudentIndex > 0) setCurrentStudentIndex(curr => curr - 1);
  };

  const handleNext = () => {
    if (currentStudentIndex < studentsList.length - 1) setCurrentStudentIndex(curr => curr + 1);
  };

  const handleScoreChange = (qId: number, val: string) => {
    const num = parseFloat(val);
    if (!isNaN(num)) {
      setScores(prev => ({ ...prev, [qId]: num }));
    }
  };

  // --- Logic การอนุมัติ ---

  // 1. กดปุ่ม -> เปิด Modal
  const onApproveClick = () => {
    setIsConfirmOpen(true);
  };

  // 2. กดยืนยันใน Modal -> ทำงานจริง
  const confirmApprove = () => {
    // ปิด Modal
    setIsConfirmOpen(false);

    // อัปเดตสถานะ
    const updatedList = [...studentsList];
    updatedList[currentStudentIndex].status = "approved";
    setStudentsList(updatedList);

    // เลื่อนไปคนถัดไป
    if (currentStudentIndex < studentsList.length - 1) {
      setTimeout(() => {
        handleNext();
      }, 300); // หน่วงเวลานิดนึงให้ user เห็นว่าสถานะเปลี่ยนแล้ว
    } else {
      alert("ตรวจครบทุกคนแล้ว!");
      navigate(`/room/${roomId}/exam/${examId}/review`);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24 relative">
      <Navbar activeTab="allReviews" />

      {/* --- CONFIRMATION MODAL --- */}
      {isConfirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all scale-100 animate-in zoom-in-95 duration-200 border border-gray-100">

            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 text-green-600">
                <CheckCircle2 size={32} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">ยืนยันการอนุมัติ?</h3>
              <p className="text-gray-500">
                คุณต้องการอนุมัติผลการตรวจของ <br />
                <span className="font-bold text-gray-800 text-lg">"{currentStudent.name}"</span> ใช่หรือไม่?
              </p>
            </div>

            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setIsConfirmOpen(false)}
                className="flex-1 h-12 text-base border-gray-300 text-gray-700 hover:bg-gray-50 rounded-xl"
              >
                ยกเลิก
              </Button>
              <Button
                onClick={confirmApprove}
                className="flex-1 h-12 text-base bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl shadow-lg shadow-green-100"
              >
                ยืนยันอนุมัติ
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Sticky Header Bar */}
      <div className="sticky top-[80px] z-30 bg-white border-b border-gray-200 shadow-sm px-4 py-3">
        <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">

          {/* Navigator */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handlePrev}
              disabled={currentStudentIndex === 0}
              className="h-9 px-2 text-gray-500 hover:text-[#3B82F6] transition-colors"
            >
              <ChevronLeft size={18} />
            </Button>
            <div className="text-center px-4 min-w-[150px]">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">ลำดับที่ {currentStudentIndex + 1} / {studentsList.length}</p>
              <h2 className="text-lg font-bold text-gray-900 leading-none mt-0.5">{currentStudent.name}</h2>
            </div>
            <Button
              variant="outline"
              onClick={handleNext}
              disabled={currentStudentIndex === studentsList.length - 1}
              className="h-9 px-2 text-gray-500 hover:text-[#3B82F6] transition-colors"
            >
              <ChevronRight size={18} />
            </Button>
          </div>

          {/* Status Badge */}
          <div className="hidden md:flex items-center gap-2 px-4 py-1.5 rounded-full border text-sm font-medium transition-colors duration-300"
            style={{
              backgroundColor: currentStudent.status === 'approved' ? '#ECFDF5' : currentStudent.status === 'needs_review' ? '#FFF7ED' : '#F0F9FF',
              color: currentStudent.status === 'approved' ? '#059669' : currentStudent.status === 'needs_review' ? '#C2410C' : '#0369A1',
              borderColor: currentStudent.status === 'approved' ? '#A7F3D0' : currentStudent.status === 'needs_review' ? '#FED7AA' : '#BAE6FD'
            }}
          >
            {currentStudent.status === 'approved' ? <CheckCircle2 size={16} /> :
              currentStudent.status === 'needs_review' ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}

            สถานะ: {
              currentStudent.status === 'approved' ? 'อนุมัติแล้ว' :
                currentStudent.status === 'needs_review' ? 'AI ไม่มั่นใจ (Needs Review)' : 'พร้อมตรวจ (Ready)'
            }
          </div>

          {/* Actions */}
          <div className="flex gap-3 w-full md:w-auto">
            <Button variant="ghost" onClick={() => navigate(-1)} className="text-gray-500 hover:text-gray-700">
              ย้อนกลับ
            </Button>

            {/* ปุ่ม Trigger Modal */}
            <Button
              onClick={onApproveClick} // เปลี่ยนมาเรียก onApproveClick แทน
              disabled={currentStudent.status === 'approved'}
              className={`
                 min-w-[140px] shadow-sm font-bold transition-all
                 ${currentStudent.status === 'approved'
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed hover:bg-gray-100'
                  : 'bg-green-600 hover:bg-green-700 text-white hover:shadow-md hover:scale-105 active:scale-95'}
               `}
            >
              {currentStudent.status === 'approved' ? (
                <><CheckCircle2 className="mr-2 w-4 h-4" /> อนุมัติแล้ว</>
              ) : (
                <><CheckCircle2 className="mr-2 w-4 h-4" /> อนุมัติผลตรวจ</>
              )}
            </Button>
          </div>
        </div>
      </div>

      <main className="max-w-[1200px] mx-auto p-4 md:p-8 space-y-8 mt-4 animate-in fade-in duration-500">

        {/* Loop Questions */}
        {questions.map((q, index) => (
          <div key={q.id} className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden flex flex-col lg:flex-row">

            {/* Left Panel */}
            <div className="lg:w-1/3 bg-gray-50 p-6 border-b lg:border-b-0 lg:border-r border-gray-200">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-[#3B82F6] text-white font-bold flex items-center justify-center shadow-sm">
                  {index + 1}
                </div>
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">โจทย์คำถาม</span>
              </div>
              <h3 className="text-gray-900 font-medium leading-relaxed mb-6">{q.questionText}</h3>
              <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
                <div className="flex items-center gap-2 mb-3 text-gray-700 font-semibold text-sm">
                  <BookOpen size={16} /> เกณฑ์การให้คะแนน
                </div>
                <ul className="space-y-3">
                  {q.rubrics.map(r => (
                    <li key={r.id} className="text-sm flex justify-between items-start border-b border-gray-100 pb-2 last:border-0 last:pb-0">
                      <span className="text-gray-600">{r.label}</span>
                      <span className="font-mono font-bold text-gray-400 text-xs bg-gray-100 px-2 py-0.5 rounded ml-2">max {r.maxScore}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Right Panel */}
            <div className="lg:w-2/3 p-6 flex flex-col">
              <div className="mb-8">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-sm font-bold text-gray-700">คำตอบของนักเรียน</h4>
                  <span className="text-xs text-gray-400">ส่งเมื่อ 10:30 น.</span>
                </div>
                <div className="p-4 rounded-xl border border-gray-200 bg-white text-gray-800 leading-relaxed text-lg shadow-sm min-h-[80px]">
                  {q.studentAnswer}
                </div>
                {q.studentAttachment && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-400 mb-1 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-400" /> ไฟล์แนบ</p>
                    <img src={q.studentAttachment} alt="attachment" className="h-32 rounded-lg border border-gray-200 object-cover hover:opacity-90 cursor-pointer" />
                  </div>
                )}
              </div>

              <div className={`rounded-xl border-2 p-5 relative transition-all ${q.aiConfidence === 'low' ? 'border-orange-100 bg-orange-50/30' : 'border-blue-100 bg-blue-50/20'}`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-2">
                    <div className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-[10px] font-bold px-2 py-1 rounded shadow-sm flex items-center gap-1">
                      ✨ AI Feedback
                    </div>
                    {q.aiConfidence === 'low' && (
                      <span className="text-xs text-orange-600 font-medium flex items-center gap-1">
                        <AlertCircle size={12} /> ความมั่นใจต่ำ โปรดตรวจสอบ
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-[10px] text-gray-500 font-medium uppercase">คะแนนประเมิน</p>
                      <div className="flex items-baseline gap-1 justify-end">
                        <span className="text-2xl font-bold text-[#3B82F6]">{scores[q.id] ?? q.aiScore}</span>
                        <span className="text-gray-400 text-sm">/ {q.totalScore}</span>
                      </div>
                    </div>
                    <Input
                      type="number"
                      className="w-20 h-12 text-center text-lg font-bold border-gray-300 focus:border-[#3B82F6] focus:ring-[#3B82F6]"
                      value={scores[q.id] ?? q.aiScore}
                      onChange={(e) => handleScoreChange(q.id, e.target.value)}
                      max={q.totalScore}
                      min={0}
                    />
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-gray-200 text-gray-700 text-sm leading-relaxed mb-4">
                  {q.aiFeedback}
                </div>
                <div className="flex items-start gap-3 mt-4 pt-4 border-t border-gray-200/50">
                  <MessageSquare className="w-5 h-5 text-gray-400 mt-2" />
                  <div className="flex-1 space-y-2">
                    <label className="text-xs font-bold text-gray-500">ความคิดเห็นเพิ่มเติม (Optional)</label>
                    <Textarea
                      placeholder="พิมพ์คำแนะนำให้นักเรียน..."
                      className="min-h-[60px] bg-white border-gray-200 focus:border-[#3B82F6] resize-none"
                    />
                  </div>
                </div>
              </div>
            </div>

          </div>
        ))}
      </main>
    </div>
  );
}