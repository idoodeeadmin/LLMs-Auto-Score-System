import { useState, useRef, useEffect } from "react";
import { Bell, User, MoreVertical, Search, X } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { useAuth } from "@/contexts/AuthContext";

interface ExamRoom {
  id: string;
  name: string;
  section: string;
}

const GRADIENTS = [
  "from-[#5B9CF5] to-[#4A7BC8]",
  "from-[#4AEDC4] to-[#2AB894]",
  "from-[#FF8B8B] to-[#E66565]",
  "from-[#A78BFA] to-[#7C3AED]",
  "from-[#FCA5A5] to-[#DC2626]",
];

export default function Home() {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [subjectName, setSubjectName] = useState("");
  const [sectionClass, setSectionClass] = useState("");
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);
  const [editingRoom, setEditingRoom] = useState<ExamRoom | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

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


  // Initialize with sample data
  const [examRooms, setExamRooms] = useState<ExamRoom[]>([
    {
      id: "1",
      name: "โครงสร้างข้อมูล",
      section: "sec.1",
    },
    {
      id: "2",
      name: "โครงสร้างข้อมูล",
      section: "sec.7",
    },
  ]);

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

  const handleCreateRoom = () => {
    if (!subjectName.trim()) return;

    const newRoom: ExamRoom = {
      id: Date.now().toString(),
      name: subjectName,
      section: sectionClass,
    };

    setExamRooms([...examRooms, newRoom]);
    setShowCreateModal(false);
    setSubjectName("");
    setSectionClass("");
  };

  const handleEditRoom = () => {
    if (!editingRoom || !subjectName.trim()) return;

    setExamRooms(
      examRooms.map((room) =>
        room.id === editingRoom.id
          ? { ...room, name: subjectName, section: sectionClass }
          : room,
      ),
    );
    setShowEditModal(false);
    setEditingRoom(null);
    setSubjectName("");
    setSectionClass("");
    setActiveMenuId(null);
  };

  const handleDeleteRoom = (id: string) => {
    setExamRooms(examRooms.filter((room) => room.id !== id));
    setShowDeleteConfirm(false);
    setDeleteTargetId(null);
    setActiveMenuId(null);
  };

  const openEditModal = (room: ExamRoom) => {
    setEditingRoom(room);
    setSubjectName(room.name);
    setSectionClass(room.section);
    setShowEditModal(true);
    setActiveMenuId(null);
  };

  const openDeleteConfirm = (id: string) => {
    setDeleteTargetId(id);
    setShowDeleteConfirm(true);
    setActiveMenuId(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          {/* Search Bar in Main Area (since Navbar handles user info) */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <input
                type="text"
                placeholder="ค้นหาห้องสอบที่ต้องการ..."
                className="w-full px-4 py-3 pr-10 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm"
              />
              <button className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                <Search size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Welcome Section */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h2 className="text-4xl font-bold text-black mb-2">Home</h2>
            <p className="text-gray-500">ยินดีต้อนรับสู่ Evaly ({user?.role === 'teacher' ? 'อาจารย์' : 'นักศึกษา'})</p>
          </div>
          {user?.role === 'teacher' ? (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-[#3B82F6] text-white rounded-lg font-medium hover:bg-[#2563EB] transition-colors shadow-sm whitespace-nowrap"
            >
              + สร้างห้องสอบ
            </button>
          ) : (
            <button
              onClick={() => alert("ระบบเข้าร่วมห้องสอบกำลังพัฒนา...")}
              className="px-6 py-3 bg-[#10B981] text-white rounded-lg font-medium hover:bg-[#059669] transition-colors shadow-sm whitespace-nowrap"
            >
              + เข้าร่วมห้องสอบ
            </button>
          )}
        </div>

        {/* Exam Rooms Section */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-black">ห้องสอบ</h3>
            {examRooms.length > 0 && (
              <Link
                to="#"
                className="text-[#3B82F6] font-medium hover:underline"
              >
                View All
              </Link>
            )}
          </div>

          {examRooms.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
              <p className="text-gray-500 text-lg">ยังไม่มีห้องสอบ</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 px-6 py-2 bg-[#3B82F6] text-white rounded-lg font-medium hover:bg-[#2563EB] transition-colors"
              >
                สร้างห้องสอบที่แรก
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {examRooms.map((room, index) => (
                <div
                  key={room.id}
                  className="bg-white rounded-2xl shadow-sm overflow-hidden hover:shadow-md transition-shadow relative cursor-pointer"
                  onClick={() => (window.location.href = `/room/${room.id}`)}
                >
                  <div
                    className={`h-32 bg-gradient-to-br ${getGradient(index)} relative`}
                  ></div>
                  <div className="p-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="text-lg font-bold text-black mb-1">
                          {room.name}
                        </h4>
                        {room.section && (
                          <p className="text-sm text-gray-500">
                            {room.section}
                          </p>
                        )}
                      </div>
                      {user?.role === 'teacher' && (
                        <div className="relative" ref={menuRef}>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveMenuId(
                                activeMenuId === room.id ? null : room.id,
                              );
                            }}
                            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                          >
                            <MoreVertical size={20} className="text-gray-600" />
                          </button>

                          {/* Context Menu */}
                          {activeMenuId === room.id && (
                            <div
                              className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openEditModal(room);
                                }}
                                className="w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors text-black font-medium first:rounded-t-lg"
                              >
                                แก้ไข
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openDeleteConfirm(room.id);
                                }}
                                className="w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors text-red-600 font-medium last:rounded-b-lg border-t border-gray-200"
                              >
                                ลบ
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      {/* Progress bar placeholder */}
                      <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[#3B82F6] rounded-full"
                          style={{ width: "0%" }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create Exam Room Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md relative overflow-hidden">
            {/* Gradient Header */}
            <div className="h-2 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6]"></div>

            {/* Modal Content */}
            <div className="p-8">
              {/* Close Button */}
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setSubjectName("");
                  setSectionClass("");
                }}
                className="absolute top-6 right-6 p-1 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X size={24} className="text-gray-600" />
              </button>

              {/* Title */}
              <h2 className="text-2xl font-bold text-black mb-8">
                สร้างห้องสอบ
              </h2>

              {/* Form Fields */}
              <div className="space-y-6">
                {/* Subject Name */}
                <div>
                  <label className="block text-base font-medium text-black mb-2">
                    ชื่อวิชา
                  </label>
                  <input
                    type="text"
                    value={subjectName}
                    onChange={(e) => setSubjectName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
                    placeholder="เช่น วิทยาศาสตร์"
                  />
                </div>

                {/* Section/Class */}
                <div>
                  <label className="block text-base font-medium text-black mb-2">
                    เซค.ชั้น{" "}
                    <span className="text-sm text-gray-400 font-normal">
                      (ไม่บังคับ)
                    </span>
                  </label>
                  <input
                    type="text"
                    value={sectionClass}
                    onChange={(e) => setSectionClass(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
                    placeholder="เช่น sec.1"
                  />
                </div>
              </div>

              {/* Confirm Button */}
              <button
                onClick={handleCreateRoom}
                disabled={!subjectName.trim()}
                className="w-full mt-8 py-3.5 bg-[#3B82F6] text-white rounded-xl font-medium text-lg hover:bg-[#2563EB] transition-colors shadow-sm disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                ยืนยัน
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Exam Room Modal */}
      {showEditModal && editingRoom && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md relative overflow-hidden">
            {/* Gradient Header */}
            <div className="h-2 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6]"></div>

            {/* Modal Content */}
            <div className="p-8">
              {/* Close Button */}
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingRoom(null);
                  setSubjectName("");
                  setSectionClass("");
                }}
                className="absolute top-6 right-6 p-1 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X size={24} className="text-gray-600" />
              </button>

              {/* Title */}
              <h2 className="text-2xl font-bold text-black mb-8">
                แก้ไขห้องสอบ
              </h2>

              {/* Form Fields */}
              <div className="space-y-6">
                {/* Subject Name */}
                <div>
                  <label className="block text-base font-medium text-black mb-2">
                    ชื่อวิชา
                  </label>
                  <input
                    type="text"
                    value={subjectName}
                    onChange={(e) => setSubjectName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
                    placeholder="เช่น วิทยาศาสตร์"
                  />
                </div>

                {/* Section/Class */}
                <div>
                  <label className="block text-base font-medium text-black mb-2">
                    เซค.ชั้น{" "}
                    <span className="text-sm text-gray-400 font-normal">
                      (ไม่บังคับ)
                    </span>
                  </label>
                  <input
                    type="text"
                    value={sectionClass}
                    onChange={(e) => setSectionClass(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
                    placeholder="เช่น sec.1"
                  />
                </div>
              </div>

              {/* Confirm Button */}
              <button
                onClick={handleEditRoom}
                disabled={!subjectName.trim()}
                className="w-full mt-8 py-3.5 bg-[#3B82F6] text-white rounded-xl font-medium text-lg hover:bg-[#2563EB] transition-colors shadow-sm disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                บันทึก
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm">
            <div className="p-6">
              <h3 className="text-lg font-bold text-black mb-2">ยืนยันการลบ</h3>
              <p className="text-gray-600 mb-6">
                คุณแน่ใจหรือว่าต้องการลบห้องสอบนี้?
                การกระทำนี้ไม่สามารถยกเลิกได้
              </p>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowDeleteConfirm(false);
                    setDeleteTargetId(null);
                  }}
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg font-medium text-black hover:bg-gray-50 transition-colors"
                >
                  ยกเลิก
                </button>
                <button
                  onClick={() =>
                    deleteTargetId && handleDeleteRoom(deleteTargetId)
                  }
                  className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
                >
                  ลบ
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
