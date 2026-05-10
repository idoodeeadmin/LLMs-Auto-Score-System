import { useState, useEffect } from "react";
import { Users, Plus, ArrowLeft, Copy, BookOpen, Loader2, UserCheck, FileText, Calendar, BarChart3, ChevronDown, ChevronUp, MoreVertical, Pencil, Trash2 } from "lucide-react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

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

interface Announcement {
  id: number;
  title: string;
  content: string;
  created_at: string;
  is_read?: number;
  read_count?: number;
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
  const [activeTab, setActiveTab] = useState<"exams" | "members" | "announcements">("exams");
  const [room, setRoom] = useState<RoomInfo | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [exams, setExams] = useState<Exam[]>([]);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [isPostingAnn, setIsPostingAnn] = useState(false);
  const [newAnn, setNewAnn] = useState({ title: "", content: "" });
  const [isFetching, setIsFetching] = useState(true);
  const [showExamSummary, setShowExamSummary] = useState(true);
  
  // Delete Exam States
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [examToDelete, setExamToDelete] = useState<Exam | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
  }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || !roomId) return;
    const fetchRoom = async (retries = 2) => {
      try {
        const promises = [
          fetch(`/api/rooms/${roomId}`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`/api/rooms/${roomId}/exams`, { headers: { Authorization: `Bearer ${token}` } })
        ];
        
        const responses = await Promise.all(promises);
        const roomRes = responses[0];
        const examsRes = responses[1];
        
        if (roomRes.ok) {
          setRoom(await roomRes.json());
          if (examsRes.ok) setExams(await examsRes.json());
          
          // Fetch announcements
          const annRes = await fetch(`/api/rooms/${roomId}/announcements`, { headers: { Authorization: `Bearer ${token}` } });
          if (annRes.ok) setAnnouncements(await annRes.json());
          
          setIsFetching(false);
        } else if (roomRes.status === 404) {
          toast.error("ไม่พบห้องเรียนนี้");
          navigate("/home");
        } else {
          throw new Error("Fetch failed");
        }
      } catch (error) {
        if (retries > 0) {
          setTimeout(() => fetchRoom(retries - 1), 1500);
        } else {
          toast.error("การเชื่อมต่อขัดข้อง กำลังพยายามเชื่อมต่อใหม่...", { duration: 2000 });
          setIsFetching(false);
        }
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

  const handleSaveToBank = async (exam: Exam) => {
    if (!token || !roomId) return;
    try {
      const res = await fetch(`/api/question-bank/save-from-exam?room_id=${roomId}&exam_id=${exam.id}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(data.message || "บันทึกข้อสอบลงคลังเรียบร้อยแล้ว");
      } else {
        const err = await res.json();
        toast.error(err.detail || "ไม่สามารถบันทึกเข้าคลัง");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    }
  };

  const handleDeleteExam = async () => {
    if (!token || !roomId || !examToDelete) return;
    setIsDeleting(true);
    try {
      const res = await fetch(`/api/rooms/${roomId}/exams/${examToDelete.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        toast.success("ลบข้อสอบเรียบร้อยแล้ว");
        setExams((prev) => prev.filter((e) => e.id !== examToDelete.id));
      } else {
        const err = await res.json();
        toast.error(err.detail || "ไม่สามารถลบข้อสอบได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
      setExamToDelete(null);
    }
  };

   const getExamStatus = (exam: Exam) => {
    const now = new Date();
    const start = exam.start_date ? new Date(exam.start_date) : null;
    const end = exam.end_date ? new Date(exam.end_date) : null;

    if (end && now > end) {
      return { 
        label: "สิ้นสุดแล้ว", 
        color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
        icon: <Trash2 size={12} className="mr-1" />,
        dateText: `สิ้นสุดเมื่อ ${end.toLocaleDateString('th-TH')} ${end.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}`
      };
    }
    
    if (start && now < start) {
      return { 
        label: "ยังไม่เริ่ม", 
        color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        icon: <Calendar size={12} className="mr-1" />,
        dateText: `เริ่ม ${start.toLocaleDateString('th-TH')} ${start.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}`
      };
    }

    if (end) {
      return { 
        label: "กำลังรับคำตอบ", 
        color: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800",
        icon: <FileText size={12} className="mr-1" />,
        dateText: `หมดเขต ${end.toLocaleDateString('th-TH')} ${end.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}`
      };
    }

    return null;
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
          className={`bg-gradient-to-br ${GRADIENTS[gradientIndex]} rounded-2xl md:rounded-3xl p-6 md:p-8 text-white shadow-xl relative overflow-hidden`}
        >
          <div className="absolute inset-0 bg-black/5" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-5">
            <div>
              <p className="text-white/70 text-[10px] md:text-sm font-medium mb-1 uppercase tracking-wider">ห้องเรียน</p>
              <h1 className="text-2xl md:text-4xl font-bold drop-shadow leading-tight">{room?.name}</h1>
              {room?.section && (
                <span className="inline-block mt-2 px-3 py-0.5 md:py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs md:text-sm font-semibold">
                  {room.section}
                </span>
              )}
            </div>
            {/* Class Code */}
            {isTeacher && room?.class_code && (
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-3 px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/30 rounded-xl md:rounded-2xl transition-colors text-left self-start md:self-auto"
              >
                <div>
                  <p className="text-white/70 text-[10px]">รหัสเชิญ</p>
                  <p className="font-mono font-bold text-lg md:text-xl tracking-widest">{room.class_code}</p>
                </div>
                <Copy size={14} className="opacity-70 ml-1" />
              </button>
            )}
          </div>
        </motion.div>

        {/* Tab Bar */}
        <motion.div 
          initial="hidden" animate="visible" variants={fadeUp} 
          className="flex items-center gap-1 bg-white dark:bg-slate-800 rounded-2xl p-1 shadow-sm border border-slate-100 dark:border-slate-700 w-full md:w-fit overflow-x-auto no-scrollbar"
        >
          <button
            onClick={() => setActiveTab("exams")}
            className={`flex-1 md:flex-none whitespace-nowrap px-4 md:px-6 py-2.5 rounded-xl text-xs md:text-sm font-bold transition-all ${activeTab === "exams"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-200"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:bg-slate-900"
              }`}
          >
            <BookOpen size={14} className="inline mr-1.5 -mt-0.5" />
            ข้อสอบ
          </button>
          <button
            onClick={() => setActiveTab("announcements")}
            className={`flex-1 md:flex-none whitespace-nowrap px-4 md:px-6 py-2.5 rounded-xl text-xs md:text-sm font-bold transition-all ${activeTab === "announcements"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-200"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:bg-slate-900"
              }`}
          >
            <Plus size={14} className="inline mr-1.5 -mt-0.5" />
            ประกาศ
          </button>
          <button
            onClick={() => setActiveTab("members")}
            className={`flex-1 md:flex-none whitespace-nowrap px-4 md:px-6 py-2.5 rounded-xl text-xs md:text-sm font-bold transition-all ${activeTab === "members"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-200"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:bg-slate-900"
              }`}
          >
            <Users size={14} className="inline mr-1.5 -mt-0.5" />
            สมาชิก
          </button>
        </motion.div>

        <AnimatePresence mode="wait">
          {/* Exams Tab */}
          {activeTab === "exams" && (
            <motion.div key="exams" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.25 }} className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200">รายการข้อสอบ</h2>
                <div className="flex items-center gap-2 w-full sm:w-auto">
                  {isTeacher && (
                    <Button
                      variant="outline"
                      onClick={() => navigate(`/room/${roomId}/analytics`)}
                      className="flex-1 sm:flex-none h-9 text-xs border-indigo-200 text-indigo-700 hover:bg-indigo-50 dark:bg-indigo-900/30"
                    >
                      <BarChart3 size={14} className="mr-1.5" /> วิเคราะห์
                    </Button>
                  )}
                  {isTeacher && (
                    <Button 
                      onClick={() => navigate(`/room/${roomId}/create-exam`)} 
                      className="flex-1 sm:flex-none h-9 text-xs bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200"
                    >
                      <Plus size={14} className="mr-1.5" /> สร้างข้อสอบ
                    </Button>
                  )}
                </div>
              </div>

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
                      className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-5 shadow-sm hover:shadow-md hover:border-indigo-200 cursor-pointer transition-all group relative"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex gap-4 items-start">
                          <div className="w-10 h-10 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                            <FileText size={20} className="text-indigo-600" />
                          </div>
                           <div>
                            <div className="flex flex-wrap items-center gap-2">
                              <h3 className="font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 transition-colors">{exam.title}</h3>
                            </div>
                            {exam.description && <p className="text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 mt-0.5 line-clamp-1">{exam.description}</p>}
                            
                            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5">
                              {exam.start_date && (
                                <p className="text-[11px] text-slate-400 dark:text-slate-500 flex items-center gap-1">
                                  <Calendar size={11} /> {new Date(exam.start_date).toLocaleDateString('th-TH')} {new Date(exam.start_date).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}
                                </p>
                              )}
                              {getExamStatus(exam)?.dateText && (
                                <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1">
                                  <span className="w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-700" />
                                  {getExamStatus(exam)?.dateText}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-start gap-4">
                          <div className="text-right flex-shrink-0 hidden sm:block">
                            <span className="text-lg font-bold text-indigo-600">{exam.total_score}</span>
                            <span className="text-xs text-slate-400 dark:text-slate-500 ml-1">คะแนน</span>
                          </div>
                          
                          {isTeacher && (
                            <div onClick={(e) => e.stopPropagation()}>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors text-slate-400 hover:text-slate-600">
                                    <MoreVertical size={18} />
                                  </button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-36">
                                  <DropdownMenuItem onClick={() => navigate(`/room/${roomId}/exam/${exam.id}/edit`)}>
                                    <Pencil size={14} className="mr-2" /> แก้ไข
                                  </DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => handleSaveToBank(exam)}>
                                    <BookOpen size={14} className="mr-2" /> บันทึกเข้าคลัง
                                  </DropdownMenuItem>
                                  <DropdownMenuItem 
                                    className="text-red-600 focus:text-red-600" 
                                    onClick={() => {
                                      setExamToDelete(exam);
                                      setShowDeleteModal(true);
                                    }}
                                  >
                                    <Trash2 size={14} className="mr-2" /> ลบ
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* Announcements Tab */}
          {activeTab === "announcements" && (
            <motion.div key="announcements" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.25 }} className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200">ประกาศจากผู้สอน</h2>
              </div>

              {isTeacher && (
                <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6 shadow-sm space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">หัวข้อประกาศ</label>
                    <input
                      type="text"
                      value={newAnn.title}
                      onChange={(e) => setNewAnn({ ...newAnn, title: e.target.value })}
                      placeholder="เช่น แจ้งเลื่อนสอบ, ประกาศผลคะแนน..."
                      className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">รายละเอียด</label>
                    <textarea
                      value={newAnn.content}
                      onChange={(e) => setNewAnn({ ...newAnn, content: e.target.value })}
                      placeholder="รายละเอียดของประกาศ..."
                      rows={3}
                      className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 focus:ring-2 focus:ring-indigo-500 outline-none transition-all resize-none"
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button
                      disabled={isPostingAnn || !newAnn.title || !newAnn.content}
                      onClick={async () => {
                        setIsPostingAnn(true);
                        try {
                          const res = await fetch(`/api/rooms/${roomId}/announcements`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                            body: JSON.stringify(newAnn),
                          });
                          if (res.ok) {
                            toast.success("ประกาศสำเร็จ");
                            setNewAnn({ title: "", content: "" });
                            // Refresh announcements
                            const annRes = await fetch(`/api/rooms/${roomId}/announcements`, { headers: { Authorization: `Bearer ${token}` } });
                            if (annRes.ok) setAnnouncements(await annRes.json());
                          }
                        } catch {
                          toast.error("ล้มเหลวในการประกาศ");
                        } finally {
                          setIsPostingAnn(false);
                        }
                      }}
                      className="bg-indigo-600 hover:bg-indigo-700"
                    >
                      {isPostingAnn ? <Loader2 className="animate-spin mr-2" size={16} /> : <Plus size={16} className="mr-2" />}
                      สร้างประกาศ
                    </Button>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {announcements.length === 0 ? (
                  <div className="text-center py-12 text-slate-400 dark:text-slate-500">
                    <Plus className="mx-auto h-12 w-12 mb-4 opacity-20" />
                    <p>ยังไม่มีการประกาศในห้องเรียนนี้</p>
                  </div>
                ) : (
                  announcements.map((ann) => (
                    <div
                      key={ann.id}
                      onMouseEnter={async () => {
                        if (!isTeacher && !ann.is_read) {
                          // Mark as read when hover or viewed
                          fetch(`/api/announcements/${ann.id}/read`, {
                            method: "POST",
                            headers: { Authorization: `Bearer ${token}` }
                          });
                          // Update local state
                          setAnnouncements(prev => prev.map(a => a.id === ann.id ? { ...a, is_read: 1 } : a));
                        }
                      }}
                      className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 p-6 shadow-sm relative overflow-hidden"
                    >
                      {!isTeacher && !ann.is_read && (
                        <div className="absolute top-0 right-0 w-3 h-3 bg-indigo-600 rounded-bl-lg" />
                      )}
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-bold text-lg text-slate-800 dark:text-slate-200">{ann.title}</h3>
                        <span className="text-xs text-slate-400 dark:text-slate-500">{new Date(ann.created_at).toLocaleString('th-TH')}</span>
                      </div>
                      <p className="text-slate-600 dark:text-slate-400 dark:text-slate-400 whitespace-pre-wrap">{ann.content}</p>
                      
                      {isTeacher && (
                        <div className="mt-4 pt-4 border-t border-slate-50 flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500">
                          <UserCheck size={14} className="text-emerald-500" />
                          <span>นักศึกษาอ่านแล้ว {ann.read_count} คน</span>
                          <button 
                            onClick={() => navigate(`/room/${roomId}/announcement/${ann.id}/stats`)}
                            className="ml-auto text-indigo-600 hover:underline"
                          >
                            ดูรายชื่อ
                          </button>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
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

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 max-w-sm w-full shadow-xl">
            <div className="text-center">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <Trash2 className="text-red-600" size={24} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">ยืนยันการลบข้อสอบ</h3>
              <p className="text-gray-500 dark:text-slate-400 mb-6 text-sm">
                คุณต้องการลบข้อสอบ "<strong>{examToDelete?.title}</strong>" ใช่หรือไม่?<br />
                <span className="text-red-500 font-bold mt-2 block">การกระทำนี้ไม่สามารถย้อนกลับได้</span>
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowDeleteModal(false);
                    setExamToDelete(null);
                  }}
                  className="flex-1"
                >
                  ยกเลิก
                </Button>
                <Button
                  onClick={handleDeleteExam}
                  disabled={isDeleting}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  {isDeleting ? <Loader2 size={16} className="animate-spin" /> : "ลบข้อสอบ"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}