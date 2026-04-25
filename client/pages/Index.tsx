import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Eye, EyeOff, Mail, Loader2, ArrowRight } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";

export default function Index() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [unverifiedEmail, setUnverifiedEmail] = useState("");
  const [isResending, setIsResending] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("กรุณากรอกอีเมลและรหัสผ่าน");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        login(data.access_token, data.user);
        navigate("/home");
      } else {
        if (data.detail === "not_verified") {
            setUnverifiedEmail(email);
            toast.error("คุณยังไม่ได้ยืนยันอีเมล กรุณาตรวจสอบกล่องข้อความ", { duration: 5000 });
        } else {
            setUnverifiedEmail("");
            toast.error(data.detail || "อีเมลหรือรหัสผ่านไม่ถูกต้อง");
        }
      }
    } catch (error) {
      console.error("Login error:", error);
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (!unverifiedEmail) return;
    setIsResending(true);
    try {
        const res = await fetch("/api/auth/resend-verification", {
            method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({email: unverifiedEmail})
        });
        const d = await res.json();
        if (res.ok) {
            toast.success("ส่งอีเมลยืนยันอีกครั้งสำเร็จ! กรุณาตรวจสอบกล่องข้อความ");
            if (d.dev_verify_link) { toast.info("Dev Mode: ดูลิงก์ยืนยันใน Console Server หรือลองเปิดลิงก์: " + d.dev_verify_link, {duration: 8000}) }
        } else {
            toast.error(d.detail || "เกิดข้อผิดพลาด");
        }
    } catch (e) {
        toast.error("Failed to connect");
    } finally {
        setIsResending(false);
    }
  };

  // Animation variants
  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };
  
  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Left Side - Hero / Branding (Hidden on mobile) */}
      <div className="relative hidden w-1/2 flex-col items-center justify-center overflow-hidden bg-slate-900 lg:flex">
        {/* Subtle animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/30 via-slate-900 to-slate-900 opacity-80" />
        
        {/* Glassmorphism content wrapper */}
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
            ระบบตรวจข้อสอบอัตโนมัติด้วยพลังของ AI ที่จะช่วยลดภาระงานและเพิ่มความแม่นยำให้กับคุณ
          </p>
        </motion.div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex w-full flex-1 items-center justify-center p-8 lg:w-1/2">
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="w-full max-w-md space-y-8"
        >
          {/* Mobile Logo */}
          <div className="flex flex-col items-center pb-4 lg:hidden">
            <div className="rounded-full bg-slate-100 p-4 shadow-inner">
               <img
                src="https://api.builder.io/api/v1/image/assets/TEMP/eb4441680ef793285669451cd4b222e32d202205?width=568"
                alt="Evaly Logo"
                className="h-16 w-16"
              />
            </div>
            <h2 className="mt-4 text-2xl font-bold text-slate-800 dark:text-slate-200">Evaly</h2>
          </div>

          <motion.div variants={fadeIn} className="text-center lg:text-left">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              Welcome back
            </h2>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500">
              เข้าสู่ระบบเพื่อจัดการห้องเรียนและข้อสอบของคุณ
            </p>
          </motion.div>

          <form onSubmit={handleLogin} className="mt-8 space-y-6">
            <motion.div variants={fadeIn} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                  อีเมล หรือ รหัสนิสิต (Email or ID)
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
                  <Input
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com หรือ student001"
                    required
                    className="pl-10 h-12 text-base transition-shadow focus-visible:ring-indigo-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                    รหัสผ่าน (Password)
                  </label>
                  <Link to="/forgot-password" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    ลืมรหัสผ่าน?
                  </Link>
                </div>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    className="pr-10 h-12 text-base transition-shadow focus-visible:ring-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-600 dark:text-slate-400 dark:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {showPassword ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
                  </button>
                </div>
              </div>
              
              {unverifiedEmail && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 rounded-lg flex flex-col gap-2"
                  >
                    <p className="text-sm text-red-600 font-medium">คุณยังไม่ได้ยืนยันอีเมลใช่หรือไม่?</p>
                    <Button 
                      onClick={handleResend} 
                      type="button" 
                      variant="outline" 
                      size="sm" 
                      disabled={isResending}
                      className="border-red-200 text-red-700 hover:bg-red-100"
                    >
                      {isResending ? <Loader2 className="w-4 h-4 animate-spin mr-2"/> : null}
                      ส่งลิงก์ยืนยันใหม่อีกครั้ง
                    </Button>
                  </motion.div>
              )}
            </motion.div>

            <motion.div variants={fadeIn} className="space-y-4 pt-2">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white text-base shadow-lg shadow-indigo-200 transition-all active:scale-[0.98]"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                ) : (
                  <>
                    เข้าสู่ระบบ <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
              
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200 dark:border-slate-700" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="bg-slate-50 dark:bg-slate-900 px-2 text-slate-500 dark:text-slate-400 dark:text-slate-500">หรือ</span>
                </div>
              </div>

              <GoogleSignInButton
                text="เข้าสู่ระบบด้วย Google"
                onSuccess={() => navigate("/home")}
              />

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200 dark:border-slate-700" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="bg-slate-50 dark:bg-slate-900 px-2 text-slate-500 dark:text-slate-400 dark:text-slate-500">หรือ</span>
                </div>
              </div>

              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/register')}
                className="w-full h-12 border-slate-300 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:text-white transition-all active:scale-[0.98]"
              >
                สมัครสมาชิกใหม่
              </Button>
            </motion.div>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
