import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Mail, Loader2, ArrowRight, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [recoveryMode, setRecoveryMode] = useState<"email" | "id">("email");
  const [name, setName] = useState("");
  const [studentId, setStudentId] = useState("");
  
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [devResetLink, setDevResetLink] = useState("");
  
  const navigate = useNavigate();

  const handleResetRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      toast.error("กรุณากรอกอีเมล");
      return;
    }

    setIsLoading(true);
    try {
      const payload: any = { email };
      if (recoveryMode === "id") {
        if (!name && !studentId) {
           toast.error("กรุณากรอกชื่อ หรือ รหัสนิสิต อย่างใดอย่างหนึ่ง");
           setIsLoading(false);
           return;
        }
        payload.name = name || undefined;
        payload.student_id = studentId || undefined;
      }

      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.reset_token) {
           // Self recovery success! Direct navigate.
           toast.success("ยืนยันตัวตนสำเร็จ! กรุณาตั้งรหัสผ่านใหม่");
           navigate(`/reset-password?token=${data.reset_token}`);
           return;
        }
        setIsSuccess(true);
        if (data.dev_reset_link) {
          setDevResetLink(data.dev_reset_link);
        }
        toast.success("ส่งลิงก์รีเซ็ตรหัสผ่านเรียบร้อยแล้ว");
      } else {
        toast.error(data.detail || "เกิดข้อผิดพลาด");
      }
    } catch (error) {
      console.error("Forgot password error:", error);
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
            <img
              src="https://api.builder.io/api/v1/image/assets/TEMP/eb4441680ef793285669451cd4b222e32d202205?width=568"
              alt="Evaly Logo"
              className="h-32 w-32 drop-shadow-2xl brightness-110"
            />
          </div>
          <h1 className="mb-4 text-5xl font-extrabold tracking-tight text-white">
            Evaly <span className="text-indigo-400">Score</span>
          </h1>
          <p className="max-w-md text-lg text-slate-300">
            เริ่มต้นใช้งานระบบประเมินผลอัจฉริยะ สร้างห้องเรียนและการสอบที่ง่ายกว่าเดิม
          </p>
        </motion.div>
      </div>

      {/* Right Side - Forgot Password Form */}
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
              ย้อนกลับหน้าล็อคอิน
            </Link>
          </motion.div>

          <motion.div variants={fadeIn} className="text-center lg:text-left">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              ลืมรหัสผ่าน?
            </h2>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500">
              กรอกอีเมลของคุณเพื่อรับลิงก์สำหรับสร้างรหัสผ่านใหม่
            </p>
          </motion.div>

          <AnimatePresence mode="wait">
            {!isSuccess ? (
              <motion.form 
                key="form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                onSubmit={handleResetRequest} 
                className="space-y-5 mt-8"
              >
                <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
                  <button type="button" onClick={() => setRecoveryMode("email")} className={`flex-1 text-sm py-2 rounded-lg font-medium transition-colors ${recoveryMode === "email" ? "bg-white dark:bg-slate-800 text-indigo-700 shadow-sm" : "text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:text-slate-300"}`}>กู้ผ่านอีเมล</button>
                  <button type="button" onClick={() => setRecoveryMode("id")} className={`flex-1 text-sm py-2 rounded-lg font-medium transition-colors ${recoveryMode === "id" ? "bg-white dark:bg-slate-800 text-indigo-700 shadow-sm" : "text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:text-slate-300"}`}>กู้ด้วยรหัสนิสิต/ชื่อ</button>
                </div>

                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                      Email หรือ ID ที่ใช้สมัคร
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
                      <Input
                        type="text"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="email หรือ id ของคุณ"
                        required
                        className="pl-9 h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
                      />
                    </div>
                  </div>

                  {recoveryMode === "id" && (
                     <div className="bg-indigo-50 dark:bg-indigo-900/30 p-4 rounded-xl border border-indigo-100 space-y-4">
                        <p className="text-xs text-indigo-600 font-semibold mb-2">⭐ โหมดกู้คืน (หากใช้อีเมลปลอมตอนสมัคร)</p>
                        <div className="space-y-1.5">
                          <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">ชื่อ-นามสกุล ที่บันทึกไว้</label>
                          <Input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="เช่น สมชาย ใจดี" className="h-11 bg-white dark:bg-slate-800" />
                        </div>
                        <div className="flex items-center justify-center text-xs text-slate-400 dark:text-slate-500 font-medium tracking-widest uppercase">--- หรือ ---</div>
                        <div className="space-y-1.5">
                          <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">รหัสนิสิต ที่บันทึกไว้</label>
                          <Input type="text" value={studentId} onChange={e => setStudentId(e.target.value)} placeholder="เช่น 64012345" className="h-11 bg-white dark:bg-slate-800" />
                        </div>
                     </div>
                  )}
                </div>

                <div className="pt-2">
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white text-base shadow-lg shadow-indigo-200 transition-all active:scale-[0.98]"
                  >
                    {isLoading ? (
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    ) : (
                      <>
                        ส่งลิงก์แก้ไขรหัสผ่าน <ArrowRight className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </Button>
                </div>
              </motion.form>
            ) : (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-8 p-6 bg-green-50 dark:bg-green-900/30 border border-green-200 rounded-2xl flex flex-col items-center text-center space-y-4"
              >
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center text-green-600 mb-2">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-green-800">ส่งอีเมลสำเร็จ!</h3>
                <p className="text-sm text-green-600 max-w-[280px]">
                  เราได้ส่งลิงก์สำหรับรีเซ็ตรหัสผ่านไปที่อีเมล <span className="font-semibold">{email}</span> แล้ว กรุณาตรวจสอบกล่องจดหมายของคุณ
                </p>
                
                {devResetLink && (
                  <div className="mt-4 w-full p-4 bg-white dark:bg-slate-800 rounded-lg border border-yellow-200 text-left">
                    <p className="text-xs font-semibold text-yellow-600 mb-2 uppercase tracking-wider">🛠️ โหมดนักพัฒนา (Dev Mode)</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500 break-all mb-3">{devResetLink}</p>
                    <Button 
                      onClick={() => window.location.href = devResetLink}
                      variant="outline" 
                      className="w-full text-xs h-9 border-indigo-200 text-indigo-700"
                    >
                      ไปยังหน้าตั้งรหัสผ่านใหม่
                    </Button>
                  </div>
                )}
                
                <Button
                  onClick={() => navigate("/")}
                  variant="ghost"
                  className="mt-4 text-slate-500 dark:text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:text-slate-300 w-full"
                >
                  กลับสู่หน้าเข้าสู่ระบบ
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
