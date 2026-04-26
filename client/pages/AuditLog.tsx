import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { 
  ShieldCheck, 
  LogIn, 
  Trash2, 
  FileEdit, 
  KeyRound,
  ShieldAlert,
  Loader2,
  Clock,
  ArrowLeft
} from "lucide-react";
import { format } from "date-fns";

interface AuditLog {
  id: number;
  action_type: string;
  entity_id: string | null;
  details: string;
  ip_address: string;
  created_at: string;
}

export default function AuditLog() {
  const { user, token, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      navigate("/");
      return;
    }

    const fetchLogs = async () => {
      try {
        const res = await fetch("/api/audit-logs", {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          setLogs(data);
        }
      } catch (error) {
        console.error("Failed to fetch audit logs:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [user, token, authLoading, navigate]);

  const getActionIcon = (action: string) => {
    switch (action) {
      case "LOGIN":
        return <LogIn className="w-5 h-5 text-emerald-500" />;
      case "DELETE_ROOM":
      case "DELETE_EXAM":
        return <Trash2 className="w-5 h-5 text-rose-500" />;
      case "PASSWORD_RESET":
        return <KeyRound className="w-5 h-5 text-amber-500" />;
      case "GRADE_CHANGE":
        return <FileEdit className="w-5 h-5 text-blue-500" />;
      default:
        return <ShieldAlert className="w-5 h-5 text-slate-500" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "LOGIN":
        return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800/50";
      case "DELETE_ROOM":
      case "DELETE_EXAM":
        return "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/30 dark:text-rose-400 dark:border-rose-800/50";
      case "PASSWORD_RESET":
        return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800/50";
      case "GRADE_CHANGE":
        return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800/50";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700";
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="animate-spin text-indigo-600 h-12 w-12" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 font-sans">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition-colors text-slate-600 dark:text-slate-400"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ShieldCheck className="w-7 h-7 text-indigo-500" />
              ประวัติความปลอดภัย (Security Audit Log)
            </h1>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
              บันทึกการเข้าสู่ระบบและการทำรายการสำคัญในบัญชีของคุณ
            </p>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
          {logs.length === 0 ? (
            <div className="p-12 text-center text-slate-500 dark:text-slate-400">
              ไม่มีประวัติการทำรายการ
            </div>
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-slate-700/50">
              {logs.map((log) => {
                const dateObj = new Date(log.created_at + 'Z');
                return (
                  <div key={log.id} className="p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors flex items-start gap-4">
                    <div className={`p-2.5 rounded-xl border ${getActionColor(log.action_type)}`}>
                      {getActionIcon(log.action_type)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-1">
                        <h3 className="font-semibold text-slate-900 dark:text-white text-base">
                          {log.details || log.action_type}
                        </h3>
                        <div className="flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 whitespace-nowrap bg-slate-100 dark:bg-slate-900 px-2.5 py-1 rounded-full font-medium">
                          <Clock className="w-3.5 h-3.5" />
                          {format(dateObj, "dd MMM yyyy, HH:mm")}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm mt-2">
                        <span className="text-slate-600 dark:text-slate-400 font-medium">
                          <span className="text-slate-400 dark:text-slate-500 font-normal mr-1.5">Action:</span>
                          {log.action_type}
                        </span>
                        
                        {log.entity_id && (
                          <>
                            <span className="w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-600"></span>
                            <span className="text-slate-600 dark:text-slate-400">
                              <span className="text-slate-400 dark:text-slate-500 mr-1.5">ID:</span>
                              {log.entity_id}
                            </span>
                          </>
                        )}

                        {log.ip_address && (
                          <>
                            <span className="w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-600"></span>
                            <span className="text-slate-600 dark:text-slate-400 font-mono text-xs mt-0.5">
                              {log.ip_address}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
