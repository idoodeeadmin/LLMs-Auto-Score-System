import { useState, useEffect } from "react";
import { Bell, User, Settings, SlidersHorizontal, BarChart2, Plus } from "lucide-react";
import { Link, useParams, useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";

interface Exam {
  id: string;
  title: string;
  date: string;
  time: string;
  status: "incomplete" | "pending" | "approved";
  statusMessage?: string;
  totalQuestions?: number;
  pendingApproval?: number;
  approved?: number;
}

export default function RoomDetail() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<"created" | "allReviews" | "statistics">("created");

  // Redirect if not logged in and not loading
  useEffect(() => {
    if (!isLoading && !user) {
      navigate("/");
    }
  }, [user, isLoading, navigate]);

  if (isLoading || !user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const isTeacher = user.role === 'teacher';

  // Mock data
  const roomName = "โครงสร้างข้อมูล";
  const roomSection = "Sec.1";

  const [exams] = useState<Exam[]>([
    {
      id: "1",
      title: "สอบกลางภาค",
      date: "25 ม.ค.",
      time: "08:00-12:00",
      status: "incomplete",
      statusMessage: "ไม่ส่งเวลา 00:13:52 วินาที",
      totalQuestions: 20,
      pendingApproval: 10,
      approved: 5,
    },
    {
      id: "2",
      title: "สอบย่อยบทที่ 2",
      date: "15 ม.ค.",
      time: "08:00-10:00 น.",
      status: "pending",
      statusMessage: "สิ้นสุดแล้ว",
      totalQuestions: 10,
      approved: 25,
    },
    {
      id: "3",
      title: "สอบบทที่ 1",
      date: "3 ม.ค.",
      time: "15:00-16:30 น.",
      status: "approved",
      statusMessage: "สิ้นสุดแล้ว",
      approved: 35,
    },
  ]);

  const getStatusBadge = (status: Exam["status"]) => {
    switch (status) {
      case "incomplete":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-200 text-gray-700">
            ยังไม่เสร็จ(20)
          </span>
        );
      case "pending":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
            รอการอนุมัติ(10)
          </span>
        );
      case "approved":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
            อนุมัติแล้ว(35)
          </span>
        );
    }
  };

  const getApprovalBadges = (exam: Exam) => {
    const badges = [];
    if (exam.pendingApproval) {
      badges.push(
        <span
          key="pending"
          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700"
        >
          รอการอนุมัติ({exam.pendingApproval})
        </span>
      );
    }
    if (exam.approved) {
      badges.push(
        <span
          key="approved"
          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700"
        >
          อนุมัติแล้ว({exam.approved})
        </span>
      );
    }
    return badges;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Room Banner */}
        <div className="bg-gradient-to-br from-[#5B9CF5] to-[#4A7BC8] rounded-3xl p-8 mb-8 text-white shadow-lg">
          <h2 className="text-4xl font-bold mb-2">{roomName}</h2>
          <p className="text-white/90 text-lg">{roomSection}</p>
        </div>

        {/* Filter and Create Button */}
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between mb-8">
          <button className="flex items-center justify-center w-full sm:w-auto gap-2 px-5 py-2.5 bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 rounded-xl transition-all shadow-sm">
            <SlidersHorizontal size={18} />
            <span className="font-semibold text-sm">ตัวกรองข้อสอบ</span>
          </button>

          <div className="flex gap-3 w-full sm:w-auto">
            <button className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-50 text-indigo-600 border border-indigo-100 hover:bg-indigo-100 hover:text-indigo-700 rounded-xl font-bold transition-all shadow-sm">
              <BarChart2 size={18} />
              <span className="text-sm">สถิติรายวิชา</span>
            </button>
            {isTeacher && (
              <Link to={`/room/${roomId}/create-exam`} className="flex-1 sm:flex-none">
                <button className="w-full h-full flex items-center justify-center gap-2 px-6 py-2.5 bg-[#3B82F6] text-white rounded-xl font-bold hover:bg-[#2563EB] transition-colors shadow-md">
                  <Plus size={18} />
                  <span className="text-sm">สร้างข้อสอบ</span>
                </button>
              </Link>
            )}
          </div>
        </div>

        {/* Exams List */}
        <div className="space-y-4">
          {exams.map((exam) => (
            <div
              key={exam.id}
              // 3. เพิ่ม onClick เพื่อไปหน้า ExamView
              onClick={() => navigate(`/room/${roomId}/exam/${exam.id}`)}
              className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all border border-gray-100 cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex flex-wrap gap-2 mb-3">
                    {getStatusBadge(exam.status)}
                    {getApprovalBadges(exam)}
                  </div>

                  {/* เพิ่ม group-hover ให้ชื่อข้อสอบเปลี่ยนสีเมื่อเอาเมาส์ชี้การ์ด */}
                  <h3 className="text-xl font-bold text-black mb-2 group-hover:text-[#3B82F6] transition-colors">
                    {exam.title}
                  </h3>

                  <div className="flex items-center gap-2 text-gray-600 mb-2">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                      <line x1="16" y1="2" x2="16" y2="6" />
                      <line x1="8" y1="2" x2="8" y2="6" />
                      <line x1="3" y1="10" x2="21" y2="10" />
                    </svg>
                    <span>
                      {exam.date}, {exam.time}
                    </span>
                  </div>

                  {exam.statusMessage && (
                    <p className={`text-sm ${exam.status === "incomplete" ? "text-red-600" : "text-gray-500"}`}>
                      {exam.statusMessage}
                    </p>
                  )}
                </div>

                {/* Actions container */}
                <div className="flex flex-col items-end justify-between h-full z-10 pl-4 border-l border-gray-50 ml-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log("Open settings");
                    }}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400 hover:text-gray-700"
                  >
                    <Settings size={20} />
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log("Go to exam statistics");
                    }}
                    className="mt-6 flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 hover:bg-indigo-50 text-gray-500 hover:text-indigo-600 text-[11px] md:text-xs font-bold rounded-lg border border-gray-100 hover:border-indigo-100 transition-colors"
                  >
                    <BarChart2 size={14} />
                    <span>สถิติ</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}