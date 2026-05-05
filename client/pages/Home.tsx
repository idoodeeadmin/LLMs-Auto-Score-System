import { useState, useRef, useEffect } from "react";
import { Search, X, Loader2, BookOpen, PlusCircle, MoreVertical, Copy } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { RoleSelection } from "@/components/RoleSelection";

interface ExamRoom {
  id: string | number;
  name: string;
  section: string;
  class_code?: string;
  owner_id?: number;
}

const GRADIENTS = [
  "from-indigo-500 to-purple-600",
  "from-blue-500 to-cyan-500",
  "from-rose-400 to-red-500",
  "from-amber-400 to-orange-500",
  "from-emerald-400 to-teal-500",
];

export default function Home() {
  const { user, token, isLoading } = useAuth();
  const navigate = useNavigate();
  const [isFetchingRooms, setIsFetchingRooms] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [joinRoomCode, setJoinRoomCode] = useState("");
  const [subjectName, setSubjectName] = useState("");
  const [sectionClass, setSectionClass] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeMenuId, setActiveMenuId] = useState<string | number | null>(null);
   const [editingRoom, setEditingRoom] = useState<ExamRoom | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Redirect if not logged in and not loading
  useEffect(() => {
    if (!isLoading && !user) {
      navigate("/");
    }
  }, [user, isLoading, navigate]);


  const [examRooms, setExamRooms] = useState<ExamRoom[]>([]);

  useEffect(() => {
    if (!token || !user) return;
    const fetchRooms = async (retries = 2) => {
      try {
        const res = await fetch("/api/rooms", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setExamRooms(data);
          setIsFetchingRooms(false);
        } else if (res.status === 401) {
          // Token might be expired, let AuthContext handle it or redirect
          setIsFetchingRooms(false);
        } else {
          throw new Error("Failed to fetch");
        }
      } catch (error) {
        if (retries > 0) {
          setTimeout(() => fetchRooms(retries - 1), 1500);
        } else {
          console.error("Fetch Rooms Network Error:", error);
          toast.error("การเชื่อมต่อขัดข้องชั่วคราว กำลังพยายามเชื่อมต่อใหม่...", { duration: 2000 });
          setIsFetchingRooms(false);
        }
      }
    };
    fetchRooms();
  }, [token, user]);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setActiveMenuId(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getGradient = (index: number) => {
    return GRADIENTS[index % GRADIENTS.length];
  };

  const filteredRooms = examRooms.filter(room => 
    room.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (room.class_code && room.class_code.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (room.section && room.section.toLowerCase().includes(searchQuery.toLowerCase()))
  );

   const handleCreateRoom = async () => {
    if (!subjectName.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const res = await fetch("/api/rooms", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ name: subjectName, section: sectionClass })
      });
      
      if (res.ok) {
        const newRoom = await res.json();
        setExamRooms([...examRooms, newRoom]);
        toast.success(`สร้างห้องสอบสำเร็จ (รหัสเชิญ: ${newRoom.class_code})`);
        setShowCreateModal(false);
        setSubjectName("");
        setSectionClass("");
      } else {
        toast.error("สร้างห้องสอบไม่สำเร็จ");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsSubmitting(false);
    }
  };

   const handleEditRoom = async () => {
    if (!editingRoom || !subjectName.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const res = await fetch(`/api/rooms/${editingRoom.id}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ name: subjectName, section: sectionClass })
      });
      
      if (res.ok) {
        setExamRooms(
          examRooms.map((room) =>
            room.id === editingRoom.id ? { ...room, name: subjectName, section: sectionClass } : room
          )
        );
        toast.success("อัปเดตข้อมูลสำเร็จ");
        setShowEditModal(false);
        setEditingRoom(null);
        setSubjectName("");
        setSectionClass("");
        setActiveMenuId(null);
      }
    } catch {
      toast.error("อัปเดตไม่สำเร็จ");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteRoom = async (id: string | number) => {
    try {
      const res = await fetch(`/api/rooms/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        setExamRooms(examRooms.filter((room) => room.id !== id));
        toast.success("ลบห้องสอบเรียบร้อยแล้ว");
      }
    } catch {
      toast.error("ลบข้อมูลไม่สำเร็จ");
    }

    setShowDeleteConfirm(false);
    setDeleteTargetId(null);
    setActiveMenuId(null);
  };

   const handleJoinRoom = async () => {
    if (!joinRoomCode.trim() || isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      const res = await fetch("/api/rooms/join", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ class_code: joinRoomCode })
      });
      
      if (res.ok) {
        const joinedRoom = await res.json();
        setExamRooms([...examRooms, joinedRoom]);
        toast.success(`เข้าร่วมห้อง ${joinedRoom.name} สำเร็จ!`);
        setShowJoinModal(false);
        setJoinRoomCode("");
      } else {
        const error = await res.json();
        toast.error(error.detail || "รหัสห้องไม่ถูกต้อง หรือคุณอยู่ในห้องนี้แล้ว");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsSubmitting(false);
    }
  };

  const openEditModal = (room: ExamRoom) => {
    setEditingRoom(room);
    setSubjectName(room.name);
    setSectionClass(room.section);
    setShowEditModal(true);
    setActiveMenuId(null);
  };

  const openDeleteConfirm = (id: string | number) => {
    setDeleteTargetId(id);
    setShowDeleteConfirm(true);
    setActiveMenuId(null);
  };

  const handleCopyCode = (e: React.MouseEvent, code?: string | number) => {
    e.stopPropagation();
    if (code) {
      navigator.clipboard.writeText(String(code));
      toast.success("คัดลอกรหัสห้องแล้ว");
    }
  };

  if (isLoading || !user || isFetchingRooms) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  if (user?.role === "unassigned") {
    return <RoleSelection />;
  }

  // Animation variants
  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };
  
  const fadeUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans">
      <Navbar />

      {user?.is_verified === 0 && (
        <div className="bg-amber-50 dark:bg-amber-900/30 border-b border-amber-200">
          <div className="max-w-7xl mx-auto px-6 py-3 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm">
            <div className="flex items-center gap-2 text-amber-800">
              <span className="flex w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
              <p>บัญชีนี้ยังไม่ได้ยืนยันอีเมล หากลืมรหัสผ่านจะกู้คืนผ่านอีเมลไม่ได้ กรุณาจำ "รหัสนิสิตผูกกับบัญชี" หรือ "หน้าจอชื่อ-นามสกุลปัจจุบัน" ไว้ใช้แทน</p>
            </div>
            <Link to="/profile">
              <span className="text-amber-700 hover:text-amber-900 font-semibold underline underline-offset-4 decoration-amber-300">ผูกบัญชี Google ที่นี่</span>
            </Link>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        
        {/* Header & Search Area */}
        <motion.div 
          initial="hidden" animate="visible" variants={fadeUp}
          className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 mt-4"
        >
          <div className="flex-1">
            <h2 className="text-2xl md:text-4xl font-bold tracking-tight text-slate-900 dark:text-white mb-1 md:mb-2">Welcome, {user.name.split(' ')[0]}</h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm md:text-lg">
              ยินดีต้อนรับสู่แดชบอร์ด ({user.role === 'teacher' ? 'อาจารย์' : 'นักศึกษา'})
            </p>
          </div>
          
          <div className="flex items-center gap-4 w-full md:w-auto flex-col sm:flex-row">
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 h-4 w-4 md:h-5 md:w-5" />
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="ค้นหา..."
                className="pl-9 md:pl-10 h-10 md:h-11 bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 shadow-sm text-sm"
              />
            </div>
            
            {user?.role === 'teacher' ? (
              <Button
                onClick={() => setShowCreateModal(true)}
                className="w-full sm:w-auto h-11 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-200 transition-all active:scale-95"
              >
                <PlusCircle className="mr-2 h-5 w-5" /> สร้างห้องสอบ
              </Button>
            ) : (
              <Button
                onClick={() => setShowJoinModal(true)}
                className="w-full sm:w-auto h-11 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-200 transition-all active:scale-95"
              >
                <BookOpen className="mr-2 h-5 w-5" /> เข้าร่วมห้องเรียน
              </Button>
            )}
          </div>
        </motion.div>

        {/* Classes Section */}
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-4 md:mb-6">
            <h3 className="text-xl md:text-2xl font-bold text-slate-800 dark:text-slate-200">ห้องเรียนของฉัน</h3>
            {examRooms.length > 0 && (
              <span className="text-sm font-medium text-slate-500 dark:text-slate-400 dark:text-slate-500">
                พบ {filteredRooms.length} ห้อง
              </span>
            )}
          </div>

          {examRooms.length === 0 ? (
            <motion.div variants={fadeUp} className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-16 text-center">
              <div className="mx-auto w-16 h-16 bg-slate-50 dark:bg-slate-900 rounded-full flex items-center justify-center mb-4">
                <BookOpen className="h-8 w-8 text-slate-400 dark:text-slate-500" />
              </div>
              <h4 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-1">ยังไม่มีห้องเรียน</h4>
              <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-6 max-w-sm mx-auto">
                {user.role === 'teacher' 
                  ? "เริ่มต้นสร้างห้องเรียนแรกของคุณเพื่อเพิ่มข้อสอบและเชิญนักศึกษา" 
                  : "คุณยังไม่ได้เข้าร่วมห้องเรียนใดๆ กดเข้าร่วมด้วยรหัสประจำห้องเลย"}
              </p>
              {user.role === 'teacher' ? (
                 <Button onClick={() => setShowCreateModal(true)} className="bg-indigo-600 hover:bg-indigo-700">
                    <PlusCircle className="mr-2 h-4 w-4" /> สร้างห้องสอบที่แรก
                 </Button>
              ) : (
                 <Button onClick={() => setShowJoinModal(true)} className="bg-indigo-600 hover:bg-indigo-700">
                    <BookOpen className="mr-2 h-4 w-4" /> กรอกรหัสเข้าร่วมห้อง
                 </Button>
              )}
            </motion.div>
          ) : filteredRooms.length === 0 ? (
            <motion.div variants={fadeUp} className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-16 text-center">
              <div className="mx-auto w-16 h-16 bg-slate-50 dark:bg-slate-900 rounded-full flex items-center justify-center mb-4">
                <Search className="h-8 w-8 text-slate-400 dark:text-slate-500" />
              </div>
              <h4 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-1">ไม่พบห้องเรียนที่ค้นหา</h4>
              <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-6 max-w-sm mx-auto">
                ไม่พบข้อมูลที่ตรงกับ "{searchQuery}" ลองค้นหาด้วยคำอื่นหรือตรวจทานตัวสะกดดูอีกครั้ง
              </p>
              <Button onClick={() => setSearchQuery("")} variant="outline" className="border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 dark:text-slate-500 hover:bg-slate-50 dark:bg-slate-900">
                ล้างการค้นหา
              </Button>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredRooms.map((room, index) => (
                <motion.div
                  variants={fadeUp}
                  key={room.id}
                  className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer group"
                  onClick={() => navigate(`/room/${room.id}`)}
                >
                  {/* Card Header */}
                  <div className={`h-32 bg-gradient-to-br ${getGradient(index)} relative flex items-center justify-center p-6 rounded-t-2xl overflow-hidden`}>
                    <div className="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors z-0"></div>
                    <h4 className="text-xl font-bold text-white drop-shadow-md z-10 text-center line-clamp-2">
                       {room.name}
                    </h4>
                  </div>

                  {/* Card Body */}
                  <div className="p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        {room.section && (
                          <span className="inline-block px-2.5 py-0.5 bg-slate-100 text-slate-600 dark:text-slate-400 dark:text-slate-500 text-xs font-semibold tracking-wide rounded-full mb-2">
                            {room.section}
                          </span>
                        )}
                        {/* Copy Code Button */}
                        <button
                          onClick={(e) => handleCopyCode(e, room.class_code || room.id)}
                          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-indigo-600 transition-colors"
                        >
                          <span className="font-mono font-bold text-sm tracking-widest">{room.class_code || room.id}</span>
                          <Copy size={13} className="opacity-60 flex-shrink-0" />
                        </button>
                      </div>

                      {/* 3-dot Menu for Teacher */}
                      {user?.role === 'teacher' && (
                        <div
                          className="relative flex-shrink-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveMenuId(activeMenuId === room.id ? null : room.id);
                            }}
                            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
                          >
                            <MoreVertical size={18} className="text-slate-400 dark:text-slate-500" />
                          </button>

                          <AnimatePresence>
                            {activeMenuId === room.id && (
                              <motion.div
                                initial={{ opacity: 0, scale: 0.95, y: -4 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95, y: -4 }}
                                transition={{ duration: 0.1 }}
                                className="absolute right-0 top-full mt-1 w-36 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 z-[9999] overflow-hidden"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <button
                                  onClick={(e) => { e.stopPropagation(); openEditModal(room); }}
                                  className="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-50 dark:bg-slate-900 transition-colors text-slate-700 dark:text-slate-300 font-medium"
                                >
                                  แก้ไขข้อมูล
                                </button>
                                <div className="h-px bg-slate-100" />
                                <button
                                  onClick={(e) => { e.stopPropagation(); openDeleteConfirm(room.id); }}
                                  className="w-full text-left px-4 py-2.5 text-sm hover:bg-red-50 dark:bg-red-900/30 transition-colors text-red-600 font-medium"
                                >
                                  ลบห้องสอบ
                                </button>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </main>

      {/* Modals for Teacher Actions */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl w-full max-w-md relative overflow-hidden"
            >
              <div className="h-2 bg-gradient-to-r from-indigo-500 to-purple-600" />
              <div className="p-8 space-y-6">
                <button
                  onClick={() => { setShowCreateModal(false); setSubjectName(""); setSectionClass(""); }}
                  className="absolute top-6 right-6 p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 dark:text-slate-500"
                >
                  <X size={20} />
                </button>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">สร้างห้องสอบใหม่</h2>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">ชื่อวิชา / ชื่อห้อง</label>
                    <Input
                      type="text"
                      value={subjectName}
                      onChange={(e) => setSubjectName(e.target.value)}
                      placeholder="เช่น วิทยาการคอมพิวเตอร์ 101"
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">ระบุกลุ่ม (Section) <span className="text-slate-400 dark:text-slate-500 font-normal">(ไม่บังคับ)</span></label>
                    <Input
                      type="text"
                      value={sectionClass}
                      onChange={(e) => setSectionClass(e.target.value)}
                      placeholder="เช่น sec.1"
                      className="h-11"
                    />
                  </div>
                </div>

                 <Button
                  onClick={handleCreateRoom}
                  disabled={!subjectName.trim() || isSubmitting}
                  className="w-full h-12 text-base bg-indigo-600 hover:bg-indigo-700 mt-2"
                >
                  {isSubmitting ? <Loader2 className="animate-spin mr-2" /> : "บันทึกข้อมูล"}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showEditModal && editingRoom && (
          <motion.div 
             initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
             className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div 
                initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                className="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl w-full max-w-md relative overflow-hidden"
              >
              <div className="h-2 bg-gradient-to-r from-indigo-500 to-purple-600" />
              <div className="p-8 space-y-6">
                <button
                  onClick={() => { setShowEditModal(false); setEditingRoom(null); setSubjectName(""); setSectionClass(""); }}
                  className="absolute top-6 right-6 p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 dark:text-slate-500"
                >
                  <X size={20} />
                </button>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">แก้ไขข้อมูลห้องสอบ</h2>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">ชื่อวิชา / ชื่อห้อง</label>
                    <Input
                      type="text"
                      value={subjectName}
                      onChange={(e) => setSubjectName(e.target.value)}
                      placeholder="เช่น วิทยาการคอมพิวเตอร์ 101"
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">ระบุกลุ่ม (Section) <span className="text-slate-400 dark:text-slate-500 font-normal">(ไม่บังคับ)</span></label>
                    <Input
                      type="text"
                      value={sectionClass}
                      onChange={(e) => setSectionClass(e.target.value)}
                      placeholder="เช่น sec.1"
                      className="h-11"
                    />
                  </div>
                </div>

                 <Button
                  onClick={handleEditRoom}
                  disabled={!subjectName.trim() || isSubmitting}
                  className="w-full h-12 text-base bg-indigo-600 hover:bg-indigo-700 mt-2"
                >
                  {isSubmitting ? <Loader2 className="animate-spin mr-2" /> : "บันทึกข้อมูล"}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div 
               initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
               className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-700 w-full max-w-sm overflow-hidden"
            >
              <div className="p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">ยืนยันการลบห้องสอบ</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-6">
                  คุณแน่ใจหรือว่าต้องการลบห้องเรียนนี้? ข้อมูลเกี่ยวกับแบบทดสอบและคะแนนในห้องนี้จะหายไปทั้งหมด และการกระทำนี้ไม่สามารถยกเลิกได้
                </p>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => { setShowDeleteConfirm(false); setDeleteTargetId(null); }}
                    className="flex-1 h-11 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 dark:text-slate-500 hover:bg-slate-50 dark:bg-slate-900"
                  >
                    ยกเลิก
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => deleteTargetId && handleDeleteRoom(deleteTargetId)}
                    className="flex-1 h-11 bg-rose-600 hover:bg-rose-700"
                  >
                    ตรวจสอบและลบ
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Join Room Modal (For Students) */}
      <AnimatePresence>
        {showJoinModal && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl w-full max-w-md relative overflow-hidden"
            >
              <div className="h-2 bg-gradient-to-r from-emerald-400 to-teal-500" />
              <div className="p-8 space-y-6">
                <button
                  onClick={() => { setShowJoinModal(false); setJoinRoomCode(""); }}
                  className="absolute top-6 right-6 p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 dark:text-slate-500"
                >
                  <X size={20} />
                </button>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-teal-50 text-teal-600 rounded-full flex items-center justify-center">
                    <BookOpen size={20} />
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white">เข้าร่วมห้องสอบ</h2>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">รหัสห้องเรียน (Class Code)</label>
                    <p className="text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-2">
                      โปรดกรอกรหัสประจำห้องเรียนที่ไม่ซ้ำกันที่คุณได้รับจากอาจารย์ผู้สอน
                    </p>
                    <Input
                      type="text"
                      value={joinRoomCode}
                      onChange={(e) => setJoinRoomCode(e.target.value)}
                      placeholder="เช่น j8x9-v2m1"
                      className="h-12 text-center text-lg tracking-widest font-mono"
                      autoFocus
                    />
                  </div>
                </div>

                 <Button
                  onClick={handleJoinRoom}
                  disabled={!joinRoomCode.trim() || isSubmitting}
                  className="w-full h-12 text-base bg-teal-600 hover:bg-teal-700 mt-2"
                >
                  {isSubmitting ? <Loader2 className="animate-spin mr-2" /> : "เข้าร่วมห้องเรียน"}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
