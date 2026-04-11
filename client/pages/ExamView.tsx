import { useState } from "react";
import Navbar from "@/components/Navbar";
import {
  Clock, Calendar, FileText, ChevronDown, ChevronUp,
  Edit3, MoreHorizontal, CheckCircle2, Trophy, ArrowLeft
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate, useParams } from "react-router-dom"; // 1. Import เพิ่ม

// Mock Data Types
interface QuestionDetail {
  id: number;
  text: string;
  score: number;
  modelAnswer?: string;
  rubrics?: { criterion: string; score: number }[];
}

export default function ExamView() {
  const navigate = useNavigate(); // 2. เรียกใช้ hook
  const { roomId, examId } = useParams(); // 3. ดึง ID จาก URL

  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);

  // Mock Data
  const examInfo = {
    title: "สอบกลางภาค (รายวิชา Data Structures)",
    description: "ทดสอบความรู้เรื่อง Stack, Queue, Linked List และการวิเคราะห์อัลกอริทึม",
    totalScore: 20,
    timeLimit: "3 ชั่วโมง",
    date: "25 ม.ค. 2026",
    questionCount: 4
  };

  const questions: QuestionDetail[] = [
    {
      id: 1,
      text: "จงอธิบายความแตกต่างระหว่าง Stack และ Queue ในเชิงการเข้าถึงข้อมูล (Data Access) พร้อมยกตัวอย่างสถานการณ์ในชีวิตจริงที่เหมาะสมกับการใช้งานโครงสร้างแต่ละแบบ",
      score: 5,
      modelAnswer: "Stack ใช้หลักการ LIFO (Last In First Out) เหมาะกับ Undo function... ส่วน Queue ใช้ FIFO (First In First Out) เหมาะกับ Printer queue...",
      rubrics: [
        { criterion: "อธิบาย concept ถูกต้อง", score: 2.5 },
        { criterion: "ยกตัวอย่างถูกต้อง", score: 2.5 }
      ]
    },
    {
      id: 2,
      text: "'Array มีประสิทธิภาพในการค้นหาข้อมูล (Search) ดีกว่า Linked List เมื่อต้องการเข้าถึงข้อมูลในตำแหน่งที่ระบุ (Index)' ข้อความนี้ถูกต้องหรือไม่ และเพราะเหตุใด",
      score: 5,
      modelAnswer: "ถูกต้อง เพราะ Array เข้าถึงด้วย Index ได้ใน O(1) ส่วน Linked List ต้อง Traverse ใน O(n)..."
    },
    {
      id: 3,
      text: "การเลือกใช้โครงสร้างข้อมูล (Selection) หากต้องออกแบบระบบ 'ลำดับความสำคัญของคิวงาน' ที่ต้องดึงงานที่สำคัญที่สุดออกมาทำก่อนเสมอ (Priority Queue) คุณจะเลือกใช้โครงสร้างข้อมูลแบบใดระหว่าง Linked List และ Binary Heap? จงให้เหตุผลประกอบในแง่ของประสิทธิภาพ (Efficiency)",
      score: 5,
      modelAnswer: "ควรใช้ Binary Heap เพราะ Insert/Delete Max ทำได้ใน O(log n)..."
    },
    {
      id: 4,
      text: "การประยุกต์ใช้ Stack (Application) จงอธิบายว่าเหตุใดโครงสร้างข้อมูลแบบ Stack (LIFO) จึงเหมาะสมที่สุดสำหรับการตรวจสอบ 'ความสมดุลของวงเล็บ' (เช่น {([])}) ในโค้ดโปรแกรม?",
      score: 5,
      modelAnswer: "เพราะ Stack สามารถเก็บวงเล็บเปิดล่าสุดไว้ และเมื่อเจอวงเล็บปิด ก็สามารถตรวจสอบคู่ของมันได้ทันที..."
    }
  ];

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24">
      <Navbar activeTab="created" />

      <main className="max-w-[1000px] mx-auto p-6 md:p-8 space-y-8">

        {/* Header & Navigation */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(`/room/${roomId}`)} // กดลูกศรย้อนกลับไปหน้ารวมห้อง
              className="text-gray-400 hover:text-gray-700"
            >
              <ArrowLeft size={24} />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{examInfo.title}</h1>
              <div className="flex items-center gap-3 text-sm text-gray-500 mt-1">
                <span className="flex items-center gap-1"><Calendar size={14} /> {examInfo.date}</span>
                <span className="flex items-center gap-1"><Clock size={14} /> {examInfo.timeLimit}</span>
              </div>
            </div>
          </div>

          {/* Toggle Switch (Exam <-> Review) */}
          <div className="bg-gray-200 p-1 rounded-lg flex w-full md:w-auto self-stretch md:self-auto mt-4 md:mt-0">
            <button
              // อยู่หน้า Exam ปุ่มนี้ Active
              className="flex-1 md:flex-none px-6 py-2 rounded-md text-sm font-bold transition-all shadow-sm bg-white text-[#3B82F6]"
            >
              ข้อสอบ
            </button>
            <button
              // 4. สั่ง Navigate ไปหน้า Review
              onClick={() => navigate(`/room/${roomId}/exam/${examId}/review`)}
              className="flex-1 md:flex-none px-6 py-2 rounded-md text-sm font-bold transition-all text-gray-500 hover:text-gray-700 hover:bg-gray-50"
            >
              ตรวจ/อนุมัติ
            </button>
          </div>
        </div>

        {/* Exam Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 border border-blue-100 p-6 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600 uppercase tracking-wide">คะแนนเต็ม</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{examInfo.totalScore}</p>
            </div>
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-[#3B82F6] shadow-sm">
              <Trophy size={24} />
            </div>
          </div>
          <div className="bg-white border border-gray-100 p-6 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">จำนวนข้อ</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{examInfo.questionCount}</p>
            </div>
            <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center text-gray-400">
              <FileText size={24} />
            </div>
          </div>
          <div className="bg-white border border-gray-100 p-6 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">เวลาสอบ</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">3 <span className="text-lg font-normal text-gray-400">ชม.</span></p>
            </div>
            <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center text-gray-400">
              <Clock size={24} />
            </div>
          </div>
        </div>

        {/* Question List */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-gray-700 ml-1">รายการคำถาม</h2>

          {questions.map((q, index) => (
            <div key={q.id} className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:border-blue-200 transition-colors group">
              {/* Card Header */}
              <div className="p-4 md:p-6 flex flex-col md:flex-row justify-between items-start gap-4">
                <div className="flex gap-3 md:gap-4 w-full">
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gray-100 text-gray-500 font-bold flex items-center justify-center flex-shrink-0 group-hover:bg-blue-50 group-hover:text-[#3B82F6] transition-colors text-sm md:text-base mt-0.5">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base md:text-lg text-gray-900 leading-relaxed font-medium">
                      {q.text}
                    </h3>
                  </div>
                </div>
                <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-start w-full md:w-auto mt-2 md:mt-0 pl-[44px] md:pl-0">
                  <span className="bg-blue-50 text-[#3B82F6] text-sm font-bold px-3 py-1 rounded-full border border-blue-100 whitespace-nowrap">
                    {q.score} คะแนน
                  </span>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-400 hover:text-gray-700 hidden md:flex">
                    <MoreHorizontal size={18} />
                  </Button>
                </div>
              </div>

              {/* Collapsible Details (Answer/Rubric) */}
              <div className="bg-gray-50/50 border-t border-gray-100">
                <button
                  onClick={() => setExpandedQuestion(expandedQuestion === q.id ? null : q.id)}
                  className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-500 hover:text-[#3B82F6] hover:bg-blue-50/50 transition-colors font-medium"
                >
                  {expandedQuestion === q.id ? (
                    <>ปิดเฉลย <ChevronUp size={16} /></>
                  ) : (
                    <>ดูเฉลยและเกณฑ์ <ChevronDown size={16} /></>
                  )}
                </button>

                {expandedQuestion === q.id && (
                  <div className="p-6 pt-2 space-y-4 animate-in slide-in-from-top-2 duration-200">
                    <div className="space-y-2">
                      <p className="text-sm font-bold text-gray-700 flex items-center gap-2">
                        <CheckCircle2 size={16} className="text-green-500" /> แนวคำตอบ (Model Answer)
                      </p>
                      <p className="text-gray-600 bg-white p-4 rounded-lg border border-gray-200 text-sm leading-relaxed">
                        {q.modelAnswer || "ไม่มีข้อมูลเฉลย"}
                      </p>
                    </div>
                    {q.rubrics && (
                      <div className="space-y-2">
                        <p className="text-sm font-bold text-gray-700">เกณฑ์การให้คะแนน</p>
                        <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
                          {q.rubrics.map((r, i) => (
                            <div key={i} className="flex justify-between items-center p-3 text-sm">
                              <span className="text-gray-600">{r.criterion}</span>
                              <span className="font-bold text-gray-900">{r.score} คะแนน</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

      </main>

      {/* Floating Action Button for Edit */}
      <div className="fixed bottom-6 right-6 md:bottom-8 md:right-8 z-50">
        <Button className="h-14 md:h-14 px-4 md:px-6 bg-[#3B82F6] hover:bg-blue-700 text-white rounded-full shadow-lg shadow-blue-200 flex items-center gap-2 md:gap-3 transition-transform hover:scale-105">
          <Edit3 size={20} />
          <span className="font-bold text-base md:text-lg hidden sm:inline-block">แก้ไขข้อสอบ</span>
        </Button>
      </div>

    </div>
  );
}