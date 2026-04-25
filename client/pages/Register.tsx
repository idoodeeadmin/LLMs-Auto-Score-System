import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Camera, Mail, User, Loader2, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [avatarPreview, setAvatarPreview] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password || !confirmPassword) {
      toast.error("กรุณากรอกข้อมูลให้ครบถ้วน");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("รหัสผ่านไม่ตรงกัน");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          name,
          role: "unassigned",
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("ลงทะเบียนสำเร็จ กรุณาเข้าสู่ระบบ");
        navigate("/");
      } else {
        toast.error(data.detail || "เกิดข้อผิดพลาดในการลงทะเบียน");
      }
    } catch (error) {
      console.error("Register error:", error);
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
            เริ่มต้นใช้งานระบบประเมินผลอัจฉริยะ สร้างห้องเรียนและการสอบที่ง่ายกว่าเดิม
          </p>
        </motion.div>
      </div>

      {/* Right Side - Register Form */}
      <div className="flex w-full flex-1 items-center justify-center p-8 lg:w-1/2 overflow-y-auto">
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="w-full max-w-lg space-y-6 pb-12 pt-8"
        >
          {/* Back Button */}
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
              สร้างบัญชีผู้ใช้ใหม่
            </h2>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500">
              เข้าร่วมเป็นส่วนหนึ่งของเรา เพื่อการจัดการการเรียนการสอนที่ดีขึ้น
            </p>
          </motion.div>



          {/* Google Sign-In Button */}
          <motion.div variants={fadeIn} className="pt-2">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200 dark:border-slate-700" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-slate-50 dark:bg-slate-900 px-4 text-slate-500 dark:text-slate-400 dark:text-slate-500">หรือ</span>
              </div>
            </div>
          </motion.div>

          <motion.div variants={fadeIn}>
            <GoogleSignInButton 
              text="ลงทะเบียนด้วย Google"
              className="border-2 border-slate-200 dark:border-slate-700 hover:border-slate-300"
            />
          </motion.div>

          <div className="relative flex items-center justify-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-slate-50 dark:bg-slate-900 px-4 text-slate-500 dark:text-slate-400 dark:text-slate-500">หรือลงทะเบียนด้วยอีเมล</span>
            </div>
          </div>

          <form onSubmit={handleRegister} className="space-y-5">
            {/* Avatar Upload */}
            <motion.div variants={fadeIn} className="flex justify-center">
              <div className="relative group">
                <label htmlFor="avatar-upload" className="cursor-pointer block relative">
                  <div className="w-20 h-20 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center bg-slate-50 dark:bg-slate-900 group-hover:bg-indigo-50 dark:bg-indigo-900/30 group-hover:border-indigo-300 transition-all overflow-hidden ring-4 ring-white shadow-sm">
                    {avatarPreview ? (
                      <img
                        src={avatarPreview}
                        alt="Avatar preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User size={32} className="text-slate-400 dark:text-slate-500 group-hover:text-indigo-400 transition-colors" />
                    )}
                  </div>
                  <div className="absolute bottom-0 right-0 w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center shadow-md ring-2 ring-white transform group-hover:scale-110 transition-transform">
                    <Camera size={14} className="text-white" />
                  </div>
                </label>
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  className="hidden"
                />
              </div>
            </motion.div>

            {/* Name Input */}
            <motion.div variants={fadeIn} className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                ชื่อ-นามสกุล (Name)
              </label>
              <div className="relative">
                <Input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="สิทธิกร ศรีรักษ์"
                  required
                  className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
                />
              </div>
            </motion.div>

            {/* Email Input */}
            <motion.div variants={fadeIn} className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                อีเมล หรือ รหัสที่ใช้ล็อคอิน (Email or ID)
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
                <Input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com หรือ setup001"
                  required
                  className="pl-9 h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
                />
              </div>
            </motion.div>



            {/* Password Fields */}
            <motion.div variants={fadeIn} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">
                  รหัสผ่าน (Password)
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
            </motion.div>

            {/* Register Button */}
            <motion.div variants={fadeIn} className="pt-4">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white text-base shadow-lg shadow-indigo-200 transition-all active:scale-[0.98]"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                ) : (
                  <>
                    ยืนยันการลงทะเบียน <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </motion.div>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
