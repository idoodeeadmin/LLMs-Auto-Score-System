import { useState, useEffect } from "react";
import { Users, Plus, ArrowLeft, Copy, BookOpen, Loader2, UserCheck, FileText, Calendar, BarChart3, ChevronDown, ChevronUp } from "lucide-react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface RoomInfo {
  id: number;
  name: string;
  section: string;
  class_code: string;
  owner_id: number;
}

interface Member {
  id: number;
  name: string;
  email: string;
  student_id?: string;
  joined_at: string;
}

interface Exam {
  id: number;
  room_id: number;
  title: string;
  description?: string;
  total_score: number;
  start_date?: string;
  end_date?: string;
  created_at: string;
}

interface RoomAnalytics {
  total_students: number;
  exam_count: number;
  exam_summaries: Array<{
    exam_id: number;
    title: string;
    total_score: number;
    submitted_count: number;
    approved_count: number;
    approved_mean: number;
    missing_count: number;
  }>;
}

const GRADIENTS = [
  "from-indigo-500 to-purple-600",
  "from-blue-500 to-cyan-500",
  "from-rose-400 to-red-500",
  "from-amber-400 to-orange-500",
  "from-emerald-400 to-teal-500",
];

export default function RoomDetail() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user, token, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<"exams" | "members">("exams");
  const [room, setRoom] = useState<RoomInfo | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [exams, setExams] = useState<Exam[]>([]);
  const [roomAnalytics, setRoomAnalytics] = useState<RoomAnalytics | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [showExamSummary, setShowExamSummary] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
  }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || !roomId) return;
    const fetchRoom = async () => {
      try {
        const [roomRes, examsRes, analyticsRes] = await Promise.all([
          fetch(`/api/rooms/${roomId}`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`/api/rooms/${roomId}/exams`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`/api/rooms/${roomId}/analytics`, { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        if (roomRes.ok) setRoom(await roomRes.json());
        else { toast.error("ไม่พบห้องเรียนนี้"); navigate("/home"); }
        if (examsRes.ok) setExams(await examsRes.json());
        if (analyticsRes.ok) setRoomAnalytics(await analyticsRes.json());
      } catch {
        toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
      } finally {
        setIsFetching(false);
      }
    };
    fetchRoom();
  }, [token, roomId]);

  useEffect(() => {
    if (!token || !roomId || activeTab !== "members") return;
    const fetchMembers = async () => {
      try {
        const res = await fetch(`/api/rooms/${roomId}/members`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) setMembers(await res.json());
      } catch {
        console.error("Failed to fetch members");
      }
    };
    fetchMembers();
  }, [token, roomId, activeTab]);

  const handleCopyCode = () => {
    if (room?.class_code) {
      navigator.clipboard.writeText(room.class_code);
      toast.success("คัดลอกรหัสห้องแล้ว");
    }
  };

  if (isLoading || isFetching || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  const isTeacher = user.role === "teacher";
  const gradientIndex = room ? room.id % GRADIENTS.length : 0;

  const fadeUp = {
    hidden: { opacity: 0, y: 16 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.35 } },
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Back Button */}
        <button
          onClick={() => navigate("/home")}
          className="flex items-center gap-2 text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:text-slate-200 transition-colors text-sm font-medium"
        >
          <ArrowLeft size={18} /> กลับหน้าหลัก
        </button>

        {/* Room Banner */}
        <motion.div
          initial="hidden" animate="visible" variants={fadeUp}
          className={`bg-gradient-to-br ${GRADIENTS[gradientIndex]} rounded-3xl p-8 text-white shadow-xl relative overflow-hidden`}
        >
          <div className="absolute inset-0 bg-black/5" />
          <div className="relative z-10 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <p className="text-white/70 text-sm font-medium mb-1 uppercase tracking-wider">ห้องเรียน</p>
              <h1 className="text-3xl sm:text-4xl font-bold drop-shadow">{room?.name}</h1>
              {room?.section && (
                <span className="inline-block mt-2 px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm font-semibold">
                  {room.section}
                </span>
              )}
            </div>
            {/* Class Code */}
            {isTeacher && room?.class_code && (
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-2 px-4 py-2.5 bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/30 rounded-2xl transition-colors text-left"
              >
                <div>
                  <p className="text-white/70 text-xs">รหัสเชิญ</p>
                  <p className="font-mono font-bold text-xl tracking-widest">{room.class_code}</p>
                </div>
                <Copy size={16} className="opacity-70 ml-1" />
              </button>
            )}
          </div>
        </motion.div>

        {/* Tab Bar */}
        <motion.div initial="hidden" animate="visible" variants={fadeUp} className="flex items-center gap-1 bg-white dark:bg-slate-800 rounded-2xl p-1.5 shadow-sm border border-slate-100 dark:border-slate-700 w-fit">
          <button
            onClick={() => setActiveTab("exams")}
            className={`px-5 py-2 rounded-xl text-sm font-semibold transition-all ${activeTab === "exams"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-200"
                : "text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:bg-slate-900"
              }`}
          >
            <BookOpen size={15} className="inline mr-1.5 -mt-0.5" />
            ข้อสอบ
          </button>
          <button
            onClick={() => setActiveTab("members")}
            className={`px-5 py-2 rounded-xl text-sm font-semibold transition-all ${activeTab === "members"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-200"
                : "text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:bg-slate-900"
              }`}
          >
            <Users size={15} className="inline mr-1.5 -mt-0.5" />
            สมาชิก
          </button>
        </motion.div>

        <AnimatePresence mode="wait">
          {/* Exams Tab */}
          {activeTab === "exams" && (
            <motion.div key="exams" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.25 }} className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200">รายการข้อสอบ</h2>
                <div className="flex items-center gap-2">
                  {isTeacher && (
                    <Button
                      variant="outline"
                      onClick={() => navigate(`/room/${roomId}/analytics`)}
                      className="border-indigo-200 text-indigo-700 hover:bg-indigo-50 dark:bg-indigo-900/30"
                    >
                      <BarChart3 size={16} className="mr-1.5" /> วิเคราะห์ทุกชุด
                    </Button>
                  )}
                  {isTeacher && (
                    <Button onClick={() => navigate(`/room/${roomId}/create-exam`)} className="bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200">
                      <Plus size={16} className="mr-1.5" /> สร้างข้อสอบ
                    </Button>
                  )}
                </div>
              </div>

              {isTeacher && roomAnalytics && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500">นักศึกษาในห้อง</p>
                    <p className="text-2xl font-bold text-slate-800 dark:text-slate-200">{roomAnalytics.total_students}</p>
                  </div>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500">จำนวนข้อสอบ</p>
                    <p className="text-2xl font-bold text-indigo-600">{roomAnalytics.exam_count}</p>
                  </div>
                  <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500">ค่าเฉลี่ยรวม (Approved)</p>
                    <p className="text-2xl font-bold text-emerald-600">
                      {roomAnalytics.exam_summaries.length > 0
                        ? (
                            roomAnalytics.exam_summaries.reduce((sum, e) => sum + (e.approved_mean || 0), 0) /
                            roomAnalytics.exam_summaries.length
                          ).toFixed(2)
                        : "0.00"}
                    </p>
                  </div>
                </div>
              )}

              {isTeacher && roomAnalytics && roomAnalytics.exam_summaries.length > 0 && (
                <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm overflow-hidden">
                  <div className="px-5 py-3 border-b border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">ภาพรวมผลสอบรายข้อสอบ</h3>
                    <button
                      onClick={() => setShowExamSummary((prev) => !prev)}
                      className="inline-flex items-center gap-1 text-xs font-medium text-slate-600 dark:text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:text-slate-200"
                    >
                      {showExamSummary ? (
                        <>
                          <ChevronUp size={14} /> ซ่อน
                        </>
                      ) : (
                        <>
                          <ChevronDown size={14} /> แสดง
                        </>
                      )}
                    </button>
                  </div>
                  {showExamSummary && (
                    <div className="divide-y divide-slate-100">
                      {roomAnalytics.exam_summaries.slice(0, 5).map((item) => (
                        <div key={item.exam_id} className="px-5 py-3 flex flex-wrap items-center justify-between gap-3">
                          <p className="font-medium text-slate-700 dark:text-slate-300">{item.title}</p>
                          <div className="text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 flex items-center gap-4">
                            <span>ส่งแล้ว {item.submitted_count}</span>
                            <span>ยังไม่ส่ง {item.missing_count}</span>
                            <span className="font-semibold text-indigo-600">Avg {item.approved_mean}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {exams.length === 0 ? (
                <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-16 text-center shadow-sm">
                  <div className="mx-auto w-16 h-16 bg-slate-50 dark:bg-slate-900 rounded-full flex items-center justify-center mb-4">
                    <BookOpen className="h-8 w-8 text-slate-400 dark:text-slate-500" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-1">ยังไม่มีข้อสอบ</h3>
                  <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 text-sm mb-6">{isTeacher ? "กดปุ่ม 'สร้างข้อสอบ' เพื่อเพิ่มข้อสอบแรก" : "อาจารย์ยังไม่ได้สร้างข้อสอบในห้องนี้"}</p>
                  {isTeacher && (
                    <Button onClick={() => navigate(`/room/${roomId}/create-exam`)} className="bg-indigo-600 hover:bg-indigo-700">
                      <Plus size={16} className="mr-1.5" /> สร้างข้อสอบแรก
                    </Button>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  {exams.map((exam) => (
                    <div
                      key={exam.id}
                      onClick={() => navigate(`/room/${roomId}/exam/${exam.id}`)}
                      className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-5 shadow-sm hover:shadow-md hover:border-indigo-200 cursor-pointer transition-all group"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex gap-4 items-start">
                          <div className="w-10 h-10 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                            <FileText size={20} className="text-indigo-600" />
                          </div>
                          <div>
                            <h3 className="font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 transition-colors">{exam.title}</h3>
                            {exam.description && <p className="text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 mt-0.5">{exam.description}</p>}
                            {exam.start_date && (
                              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 flex items-center gap-1">
                                <Calendar size={12} /> {new Date(exam.start_date).toLocaleDateString('th-TH')}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <span className="text-lg font-bold text-indigo-600">{exam.total_score}</span>
                          <span className="text-xs text-slate-400 dark:text-slate-500 ml-1">คะแนน</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* Members Tab */}
          {activeTab === "members" && (
            <motion.div key="members" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.25 }} className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200">สมาชิกในห้อง</h2>
                <span className="text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500">{members.filter(m => (m as any).role === 'student').length} นักศึกษา</span>
              </div>

              {members.length === 0 ? (
                <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-16 text-center shadow-sm">
                  <div className="mx-auto w-16 h-16 bg-slate-50 dark:bg-slate-900 rounded-full flex items-center justify-center mb-4">
                    <Users className="h-8 w-8 text-slate-400 dark:text-slate-500" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-1">ยังไม่มีนักศึกษา</h3>
                  <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 text-sm">แชร์รหัส <span className="font-mono font-bold text-indigo-600">{room?.class_code}</span> ให้นักศึกษาเพื่อเข้าร่วม</p>
                </div>
              ) : (
                <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm overflow-hidden">
                  {members.map((m, i) => {
                    const memberRole = (m as any).role;
                    const isTeacherMember = memberRole === 'teacher';
                    return (
                      <div key={m.id} className={`flex items-center gap-4 px-6 py-4 ${i !== 0 ? "border-t border-slate-50" : ""} ${isTeacherMember ? "bg-indigo-50 dark:bg-indigo-900/30/50" : ""}`}>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 ${isTeacherMember ? "bg-indigo-100 text-indigo-700" : "bg-slate-100 text-slate-600 dark:text-slate-400 dark:text-slate-500"}`}>
                          {m.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="font-semibold text-slate-800 dark:text-slate-200 truncate">{m.name}</p>
                            {isTeacherMember && (
                              <span className="flex-shrink-0 text-xs font-bold px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full">ผู้สอน</span>
                            )}
                          </div>
                          <p className="text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 truncate">{m.email}{m.student_id ? ` · ${m.student_id}` : ""}</p>
                        </div>
                        {isTeacherMember
                          ? <span className="text-indigo-400 flex-shrink-0">👑</span>
                          : <UserCheck size={16} className="text-emerald-500 flex-shrink-0" />
                        }
                      </div>
                    );
                  })}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}