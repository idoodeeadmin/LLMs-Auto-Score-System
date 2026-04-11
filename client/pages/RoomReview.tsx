import { useState } from "react";
import Navbar from "@/components/Navbar";
import {
  Search, Filter, CheckCircle2, AlertCircle,
  FileText, User, ChevronDown, Check, X, AlertTriangle
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useNavigate, useParams } from "react-router-dom";

// Mock Data Types
type StudentStatus = "missing" | "ready" | "needs_review" | "approved";

interface Student {
  id: string;
  name: string;
  studentId: string;
  status: StudentStatus;
  score?: number;
  aiConfidence?: number;
  submittedAt?: string;
}

export default function RoomReview() {
  const navigate = useNavigate();
  const { roomId, examId } = useParams(); // ดึง ID ห้องและข้อสอบ

  // ... (ส่วน State และ Mock Data เหมือนเดิม ไม่ต้องแก้) ...
  const [activeTab, setActiveTab] = useState<"missing" | "pending" | "approved">("pending");
  const [subFilter, setSubFilter] = useState<"all" | "success" | "failed">("all");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const [students, setStudents] = useState<Student[]>([
    { id: "1", name: "นาย ก", studentId: "64001", status: "ready", score: 18, aiConfidence: 95, submittedAt: "10:30" },
    { id: "2", name: "นาย ข", studentId: "64002", status: "ready", score: 16, aiConfidence: 92, submittedAt: "10:32" },
    { id: "3", name: "นาย ค", studentId: "64003", status: "ready", score: 20, aiConfidence: 98, submittedAt: "10:35" },
    { id: "4", name: "นาย ง", studentId: "64004", status: "needs_review", score: 0, aiConfidence: 45, submittedAt: "10:40" },
    { id: "5", name: "นาย จ", studentId: "64005", status: "needs_review", score: 0, aiConfidence: 30, submittedAt: "10:45" },
    { id: "6", name: "นางสาว A", studentId: "64006", status: "approved", score: 19, submittedAt: "10:20" },
    { id: "7", name: "นางสาว B", studentId: "64007", status: "missing" },
  ]);

  // ... (Filter & Logic เหมือนเดิม) ...
  const filteredStudents = students.filter(s => {
    if (activeTab === "missing") return s.status === "missing";
    if (activeTab === "approved") return s.status === "approved";

    if (activeTab === "pending") {
      const isPending = s.status === "ready" || s.status === "needs_review";
      if (!isPending) return false;

      if (subFilter === "all") return true;
      if (subFilter === "success") return s.status === "ready";
      if (subFilter === "failed") return s.status === "needs_review";
    }
    return false;
  });

  const approvableStudents = filteredStudents.filter(s => s.status === 'ready');

  const toggleSelectAll = () => {
    if (approvableStudents.length > 0 && selectedIds.length === approvableStudents.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(approvableStudents.map(s => s.id));
    }
  };

  const toggleSelectOne = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(itemId => itemId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleApprove = (id: string) => {
    setStudents(prev => prev.map(s => s.id === id ? { ...s, status: "approved" } : s));
    setSelectedIds(selectedIds.filter(itemId => itemId !== id));
  };

  const handleBulkApprove = () => {
    setStudents(prev => prev.map(s => selectedIds.includes(s.id) ? { ...s, status: "approved" } : s));
    setSelectedIds([]);
  };

  const StatusBadge = ({ status, score }: { status: StudentStatus, score?: number }) => {
    // ... (Badge Code เหมือนเดิม) ...
    if (status === "ready") return (
      <div className="flex flex-col items-start">
        <span className="text-sm font-bold text-gray-900">สำเร็จ (รออนุมัติ)</span>
        <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-md mt-1 border border-green-100">
          คะแนน AI: {score}/20
        </span>
      </div>
    );
    if (status === "needs_review") return (
      <div className="flex flex-col items-start">
        <span className="text-sm font-bold text-gray-900">ไม่สำเร็จ (โปรดตรวจสอบ)</span>
        <span className="text-xs text-orange-600 bg-orange-50 px-2 py-0.5 rounded-md mt-1 border border-orange-100 flex items-center gap-1">
          <AlertTriangle size={10} /> AI ไม่มั่นใจ
        </span>
      </div>
    );
    if (status === "approved") return (
      <div className="flex items-center gap-2 text-green-600 font-medium">
        <CheckCircle2 size={16} /> อนุมัติแล้ว ({score}/20)
      </div>
    );
    return <span className="text-gray-400 italic">ยังไม่ส่งข้อสอบ</span>;
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-20">
      <Navbar activeTab="allReviews" />

      <main className="max-w-[1440px] mx-auto p-6 md:p-8 space-y-8">

        {/* Header & Stats */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-gray-900">สอบกลางภาค (AI Feedback)</h1>
              <span className="bg-blue-100 text-[#3B82F6] text-xs px-2 py-0.5 rounded font-bold">Sec.1</span>
            </div>
            <p className="text-gray-500">จัดการผลการประเมินและอนุมัติคะแนน</p>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" className="bg-white text-gray-700">
              <FileText className="mr-2 w-4 h-4" /> Export CSV
            </Button>
            <div className="flex bg-gray-200 p-1 rounded-lg">
              <button
                onClick={() => navigate(`/room/${roomId}/exam/${examId}`)}
                className="px-4 py-1.5 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
              >
                ข้อสอบ
              </button>
              <button className="px-4 py-1.5 rounded-md text-sm font-medium bg-white text-[#3B82F6] shadow-sm">
                ตรวจ/อนุมัติ
              </button>
            </div>
          </div>
        </div>

        {/* --- Stats Cards --- */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* ... (Cards Code เหมือนเดิม) ... */}
          <div onClick={() => setActiveTab("missing")} className={`p-5 rounded-xl border shadow-sm flex items-center justify-between cursor-pointer transition-all hover:shadow-md ${activeTab === 'missing' ? 'border-gray-400 bg-gray-50 ring-1 ring-gray-400' : 'bg-white border-gray-100'}`}>
            <div><p className="text-sm text-gray-500">ยังไม่ส่ง</p><p className="text-2xl font-bold text-gray-400">0 <span className="text-sm font-normal">คน</span></p></div>
            <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-400"><User size={20} /></div>
          </div>
          <div onClick={() => setActiveTab("pending")} className={`p-5 rounded-xl border shadow-sm flex items-center justify-between cursor-pointer transition-all hover:shadow-md relative overflow-hidden ${activeTab === 'pending' ? 'border-[#3B82F6] bg-blue-50/20 ring-1 ring-[#3B82F6]' : 'bg-white border-gray-100'}`}>
            {activeTab === 'pending' && <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[#3B82F6]" />}
            <div><p className={`text-sm font-medium ${activeTab === 'pending' ? 'text-[#3B82F6]' : 'text-gray-500'}`}>รอการตรวจ/อนุมัติ</p><p className="text-2xl font-bold text-gray-900">{students.filter(s => s.status === 'ready' || s.status === 'needs_review').length} <span className="text-sm font-normal text-gray-500">คน</span></p></div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${activeTab === 'pending' ? 'bg-blue-100 text-[#3B82F6]' : 'bg-gray-50 text-gray-400'}`}><AlertCircle size={20} /></div>
          </div>
          <div onClick={() => setActiveTab("approved")} className={`p-5 rounded-xl border shadow-sm flex items-center justify-between cursor-pointer transition-all hover:shadow-md ${activeTab === 'approved' ? 'border-green-500 bg-green-50/20 ring-1 ring-green-500' : 'bg-white border-gray-100'}`}>
            <div><p className={`text-sm font-medium ${activeTab === 'approved' ? 'text-green-600' : 'text-gray-500'}`}>อนุมัติแล้ว</p><p className="text-2xl font-bold text-gray-900">{students.filter(s => s.status === 'approved').length} <span className="text-sm font-normal text-gray-500">คน</span></p></div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${activeTab === 'approved' ? 'bg-green-100 text-green-600' : 'bg-gray-50 text-gray-400'}`}><CheckCircle2 size={20} /></div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden min-h-[600px] flex flex-col">

          {/* Toolbar */}
          <div className="border-b border-gray-200 p-4 flex flex-col md:flex-row justify-between items-center gap-4">
            {/* ... (Tabs & Filters เหมือนเดิม) ... */}
            <div className="flex p-1 bg-gray-100 rounded-lg self-start">
              {/* ปุ่ม Pill Tabs ... */}
              <button onClick={() => setActiveTab("missing")} className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'missing' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>ยังไม่ส่ง ({students.filter(s => s.status === 'missing').length})</button>
              <button onClick={() => setActiveTab("pending")} className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'pending' ? 'bg-white text-[#3B82F6] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>รอการตรวจ ({students.filter(s => s.status === 'ready' || s.status === 'needs_review').length})</button>
              <button onClick={() => setActiveTab("approved")} className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'approved' ? 'bg-white text-green-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>อนุมัติแล้ว ({students.filter(s => s.status === 'approved').length})</button>
            </div>

            {/* Sub Filters & Search */}
            <div className="flex gap-3 w-full md:w-auto items-center">
              {activeTab === 'pending' && (
                <div className="flex gap-2 mr-2">
                  <button onClick={() => setSubFilter("all")} className={`px-3 py-1.5 text-xs font-bold rounded-full border transition-all ${subFilter === 'all' ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-500 border-gray-200 hover:border-gray-400'}`}>ทั้งหมด</button>
                  <button onClick={() => setSubFilter("failed")} className={`px-3 py-1.5 text-xs font-bold rounded-full border transition-all ${subFilter === 'failed' ? 'bg-orange-500 text-white border-orange-500' : 'bg-white text-gray-500 border-gray-200 hover:border-orange-300'}`}>ประเมินไม่ได้</button>
                  <button onClick={() => setSubFilter("success")} className={`px-3 py-1.5 text-xs font-bold rounded-full border transition-all ${subFilter === 'success' ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-500 border-gray-200 hover:border-green-300'}`}>ประเมินสำเร็จ</button>
                </div>
              )}
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input placeholder="ค้นหาชื่อ..." className="pl-9 h-10 bg-gray-50 border-gray-200" />
              </div>
            </div>
          </div>

          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-gray-50/50 border-b border-gray-200 text-sm font-semibold text-gray-500">
            {/* ... (Header เหมือนเดิม) ... */}
            <div className="col-span-4 flex items-center gap-4">
              <div className="flex items-center justify-center w-5">
                <input
                  type="checkbox"
                  className={`w-4 h-4 rounded border-gray-300 text-[#3B82F6] focus:ring-[#3B82F6] ${activeTab === 'pending' && approvableStudents.length === 0 ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                  checked={activeTab === 'pending' ? (approvableStudents.length > 0 && selectedIds.length === approvableStudents.length) : (filteredStudents.length > 0 && selectedIds.length === filteredStudents.length)}
                  disabled={activeTab === 'pending' && approvableStudents.length === 0}
                  onChange={toggleSelectAll}
                />
              </div>
              <span>รายชื่อนักศึกษา</span>
            </div>
            <div className="col-span-4">ผลการประเมิน (AI)</div>
            <div className="col-span-4 text-right pr-4">การดำเนินการ</div>
          </div>

          {/* Student List */}
          <div className="divide-y divide-gray-100">
            {filteredStudents.length === 0 ? (
              <div className="py-20 text-center text-gray-400">ไม่มีข้อมูลในหมวดหมู่นี้</div>
            ) : (
              filteredStudents.map((student) => (
                <div key={student.id} className="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-gray-50/50 transition-colors group">
                  {/* Name Col */}
                  <div className="col-span-4 flex items-center gap-4">
                    <div className="flex items-center justify-center w-5">
                      <input
                        type="checkbox"
                        className={`w-4 h-4 rounded border-gray-300 text-[#3B82F6] focus:ring-[#3B82F6] ${student.status === 'needs_review' ? 'opacity-30 cursor-not-allowed bg-gray-100' : 'cursor-pointer'}`}
                        checked={selectedIds.includes(student.id)}
                        disabled={student.status === 'needs_review'}
                        onChange={() => toggleSelectOne(student.id)}
                      />
                    </div>
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-[#3B82F6] font-bold text-sm">
                      {student.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{student.name}</p>
                      <p className="text-xs text-gray-500">{student.studentId} • ส่งเมื่อ {student.submittedAt}</p>
                    </div>
                  </div>

                  {/* Status Col */}
                  <div className="col-span-4">
                    <StatusBadge status={student.status} score={student.score} />
                  </div>

                  {/* Actions Col */}
                  <div className="col-span-4 flex justify-end gap-2">
                    {activeTab === "pending" && (
                      <>
                        <Button
                          onClick={() => handleApprove(student.id)}
                          disabled={student.status === 'needs_review'}
                          className={`h-9 w-24 rounded-lg font-bold shadow-sm transition-all ${student.status === 'needs_review' ? 'bg-gray-300 cursor-not-allowed text-gray-500' : 'bg-green-500 hover:bg-green-600 text-white'}`}
                        >
                          อนุมัติ
                        </Button>

                        {/* ปุ่มตรวจสอบที่แก้แล้ว */}
                        <Button
                          variant="outline"
                          // ตรงนี้ครับ: สั่งให้วิ่งไปหน้า Grading พร้อม ID นักเรียน
                          onClick={() => navigate(`/room/${roomId}/exam/${examId}/grading/${student.id}`)}
                          className="border-blue-200 text-[#3B82F6] hover:bg-blue-50 h-9 px-4 rounded-lg font-medium"
                        >
                          ตรวจสอบ
                        </Button>
                      </>
                    )}
                    {activeTab === "approved" && (
                      <Button variant="ghost" className="text-gray-400 hover:text-[#3B82F6]">
                        ดูรายละเอียด
                      </Button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      {/* Floating Bulk Action */}
      {selectedIds.length > 0 && activeTab === "pending" && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center gap-6 animate-in slide-in-from-bottom-4 z-50">
          <div className="flex items-center gap-3 border-r border-gray-700 pr-6">
            <div className="bg-[#3B82F6] text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold">{selectedIds.length}</div>
            <span className="font-medium">รายการที่เลือก</span>
          </div>
          <div className="flex gap-3">
            <Button variant="ghost" onClick={() => setSelectedIds([])} className="text-gray-300 hover:text-white h-8">ยกเลิก</Button>
            <Button onClick={handleBulkApprove} className="bg-green-500 hover:bg-green-600 text-white h-9 px-6 rounded-lg font-bold">อนุมัติทั้งหมด ({selectedIds.length})</Button>
          </div>
        </div>
      )}
    </div>
  );
}