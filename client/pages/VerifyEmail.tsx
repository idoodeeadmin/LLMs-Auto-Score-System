import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { CheckCircle2, XCircle, Loader2, ArrowLeft } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("ไม่พบลิงก์ยืนยันตัวตน");
      return;
    }

    const verifyToken = async () => {
      try {
        const response = await fetch("/api/auth/verify-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        });
        const data = await response.json();
        if (response.ok) {
          setStatus("success");
          setMessage("ยืนยันบัญชีอีเมลสำเร็จ! คุณสามารถเข้าสู่ระบบได้แล้ว");
        } else {
          setStatus("error");
          setMessage(data.detail || "ลิงก์ยืนยันไม่ถูกต้องหรือหมดอายุแล้ว");
        }
      } catch (e) {
        setStatus("error");
        setMessage("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
      }
    };
    verifyToken();
  }, [token]);

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-900 items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md bg-white dark:bg-slate-800 rounded-3xl shadow-xl overflow-hidden"
      >
        <div className="p-8 text-center space-y-6">
          {status === "loading" && (
            <div className="py-12 flex flex-col items-center">
              <Loader2 className="w-16 h-16 text-indigo-500 animate-spin mb-4" />
              <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">กำลังตรวจสอบข้อมูล...</h2>
            </div>
          )}
          
          {status === "success" && (
            <div className="py-8 flex flex-col items-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center text-green-600 mb-6">
                <CheckCircle2 className="w-10 h-10" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-2">ยินดีด้วย!</h2>
              <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-8">{message}</p>
              <Button onClick={() => navigate("/")} className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-lg shadow-lg shadow-indigo-200">
                เข้าสู่ระบบทันที
              </Button>
            </div>
          )}

          {status === "error" && (
            <div className="py-8 flex flex-col items-center">
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center text-red-500 mb-6">
                <XCircle className="w-10 h-10" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-2">เกิดข้อผิดพลาด</h2>
              <p className="text-slate-500 dark:text-slate-400 dark:text-slate-500 mb-8">{message}</p>
              <Link to="/">
                 <Button variant="outline" className="w-full text-indigo-600 border-indigo-200 hover:bg-indigo-50 dark:bg-indigo-900/30 rounded-xl h-12">
                   <ArrowLeft className="w-4 h-4 mr-2" /> กลับไปหน้าเข้าสู่ระบบ
                 </Button>
              </Link>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
