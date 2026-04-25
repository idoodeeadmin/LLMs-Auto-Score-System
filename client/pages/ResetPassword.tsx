import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { ArrowLeft, Loader2, ArrowRight, Lock } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ResetPassword() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      toast.error("ลิงก์ไม่ถูกต้องหรือหมดอายุแล้ว");
      navigate("/");
    }
  }, [token, navigate]);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password || !confirmPassword) {
      toast.error("กรุณากรอกรหัสผ่านให้ครบถ้วน");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("รหัสผ่านไม่ตรงกัน");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("เปลี่ยนรหัสผ่านสำเร็จ กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่");
        navigate("/");
      } else {
        toast.error(data.detail || "เกิดข้อผิดพลาด ลิงก์อาจจะหมดอายุแล้ว");
        if (data.detail?.includes("expired") || data.detail?.includes("Invalid")) {
          setTimeout(() => navigate("/forgot-password"), 2000);
        }
      }
    } catch (error) {
      console.error("Reset password error:", error);
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsLoading(false);
    }
  };

  // Animation variants
  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };
  
  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  if (!token) return null; // Wait for effect to redirect

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Left Side - Hero / Branding (Hidden on mobile) */}
      <div className="relative hidden w-1/2 flex-col items-center justify-center overflow-hidden bg-slate-900 lg:flex">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/30 via-slate-900 to-slate-900 opacity-80" />
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="relative z-10 flex flex-col items-center justify-center p-12 text-center"
        >
          <div className="mb-8 rounded-full bg-white/10 p-6 backdrop-blur-md ring-1 ring-white/20">
            <Lock className="h-32 w-32 text-indigo-300 drop-shadow-2xl" />
          </div>
          <h1 className="mb-4 text-5xl font-extrabold tracking-tight text-white">
            ตั้งรหัสผ่านใหม่
          </h1>
          <p className="max-w-md text-lg text-slate-300">
            เพื่อความปลอดภัย โปรดเลือกรหัสผ่านที่คุณจำได้และคาดเดาได้ยาก
          </p>
        </motion.div>
      </div>

      {/* Right Side - Reset Form */}
      <div className="flex w-full flex-1 items-center justify-center p-8 lg:w-1/2 overflow-y-auto">
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="w-full max-w-lg space-y-6 pb-12 pt-8"
        >
          <motion.div variants={fadeIn}>
            <Link
              to="/"
              className="inline-flex items-center text-sm font-medium text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-indigo-600 transition-colors mb-2"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              กลับหน้าหลัก
            </Link>
          </motion.div>

          <motion.div variants={fadeIn} className="text-center lg:text-left">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              สร้างรหัสผ่านใหม่
            </h2>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500">
              ตั้งรหัสผ่านใหม่ของคุณเพื่อเข้าใช้งานระบบ
            </p>
          </motion.div>

          <motion.form 
            variants={fadeIn}
            onSubmit={handleResetPassword} 
            className="space-y-5 mt-8"
          >
            <div className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                รหัสผ่านใหม่ (New Password)
              </label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
              />
            </div>
            
            <div className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                ยืนยันรหัสผ่าน (Confirm Password)
              </label>
              <Input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
              />
            </div>

            <div className="pt-4">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white text-base shadow-lg shadow-indigo-200 transition-all active:scale-[0.98]"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                ) : (
                  <>
                    บันทึกรหัสผ่านใหม่ <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </motion.form>
        </motion.div>
      </div>
    </div>
  );
}
