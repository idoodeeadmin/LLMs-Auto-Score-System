import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";
import { Loader2, History, ArrowRight, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

interface SubmissionHistory {
  exam_id: number;
  exam_title: string;
  exam_total_score: number;
  room_id: number;
  room_name: string;
  submission_id?: number;
  status: string;
  submission_score?: number;
  submitted_at?: string;
}

export default function StudentHistory() {
  const { user, token, isLoading } = useAuth();
  const navigate = useNavigate();
  const [history, setHistory] = useState<SubmissionHistory[]>([]);
  const [isFetching, setIsFetching] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) navigate("/");
    if (!isLoading && user?.role !== "student") navigate("/");
  }, [user, isLoading, navigate]);

  useEffect(() => {
    if (!token || user?.role !== "student") return;
    fetch("/api/submissions/me", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => setHistory(d))
      .catch(console.error)
      .finally(() => setIsFetching(false));
  }, [token, user?.role]);

  if (isLoading || isFetching) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full"><CheckCircle2 size={12} /> อนุมัติผลแล้ว</span>;
      case "submitted":
      case "needs_review":
      case "ready":
        return <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full"><Clock size={12} /> รอตรวจสอบ</span>;
      case "missing":
      default:
        return <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-500 text-xs font-bold rounded-full"><AlertCircle size={12} /> ขาดส่ง / ยังไม่เริ่ม</span>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3 text-slate-900 leading-tight">
              <div className="p-2.5 bg-indigo-100 text-indigo-600 rounded-xl">
                <History size={26} />
              </div>
              ประวัติการสอบของฉัน
            </h1>
            <p className="text-slate-500 mt-2 text-sm max-w-lg">
              ติดตามและดูผลการประเมินย้อนหลังของทุกรายวิชาที่คุณได้เข้าร่วมไว้ได้ที่นี่ ข้อมูลคะแนนและข้อเสนอแนะทั้งหมดจะปรากฏเมื่ออาจารย์อนุมัติผลแล้ว
            </p>
          </div>
        </div>

        {/* History List */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
          {history.length === 0 ? (
            <div className="p-16 text-center">
              <History className="h-12 w-12 text-slate-200 mx-auto mb-4" />
              <p className="text-slate-500 font-medium">ยังไม่มีประวัติการสอบใด ๆ</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {history.map((h, i) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  key={`${h.exam_id}-${h.room_id}`} 
                  className="flex flex-col sm:flex-row items-center p-5 sm:p-6 hover:bg-slate-50 transition-colors gap-4"
                >
                  <div className="flex-1 w-full space-y-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-xs font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md border border-slate-200">{h.room_name}</span>
                      {renderStatusBadge(h.status)}
                    </div>
                    <Link to={`/room/${h.room_id}/exam/${h.exam_id}`} className="block">
                      <h3 className="text-lg font-bold text-slate-800 hover:text-indigo-600 transition-colors">{h.exam_title}</h3>
                    </Link>
                    {h.submitted_at && (
                      <p className="text-xs text-slate-500">
                        ส่งเมื่อ: {new Date(h.submitted_at).toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-6 w-full sm:w-auto justify-between sm:justify-end">
                    <div className="text-right">
                      {h.status === "approved" ? (
                        <>
                          <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">คะแนนรวม</p>
                          <p className="text-xl font-bold text-indigo-600">
                            {h.submission_score} <span className="text-sm font-normal text-slate-400">/ {h.exam_total_score}</span>
                          </p>
                        </>
                      ) : (
                        <>
                          <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">สถานะคะแนน</p>
                          <p className="text-sm font-semibold text-slate-400 mt-1">-</p>
                        </>
                      )}
                    </div>
                    <Button 
                      onClick={() => navigate(`/room/${h.room_id}/exam/${h.exam_id}`)}
                      variant="ghost" 
                      className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
                    >
                      <ArrowRight size={20} />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
