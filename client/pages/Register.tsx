import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Camera, Mail, User, Loader2, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";

export default function Register() {
  const [isStudent, setIsStudent] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [studentId, setStudentId] = useState("");
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
          role: isStudent ? "student" : "teacher",
          student_id: isStudent ? studentId : null,
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
    <div className="flex min-h-screen bg-slate-50">
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
              className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-indigo-600 transition-colors mb-2"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              ย้อนกลับหน้าล็อคอิน
            </Link>
          </motion.div>

          <motion.div variants={fadeIn} className="text-center lg:text-left">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              สร้างบัญชีผู้ใช้ใหม่
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              เข้าร่วมเป็นส่วนหนึ่งของเรา เพื่อการจัดการการเรียนการสอนที่ดีขึ้น
            </p>
          </motion.div>

          {/* Role Toggle Buttons */}
          <motion.div variants={fadeIn} className="flex gap-4 mb-2 pt-2">
            <button
              type="button"
              onClick={() => setIsStudent(true)}
              className={`flex-1 flex flex-col items-center justify-center gap-2 p-4 rounded-2xl border-2 transition-all duration-200 ease-in-out ${
                isStudent
                  ? "border-indigo-600 bg-indigo-50 text-indigo-700 shadow-sm"
                  : "border-slate-200 bg-white text-slate-500 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19.0001 5L12.0001 2L5.00006 5L8.50006 6.5V8.5M19.0001 5L15.5001 6.5V8.5M19.0001 5V9M8.50006 8.5C8.50006 8.5 9.66706 8 12.0001 8C14.3331 8 15.5001 8.5 15.5001 8.5M8.50006 8.5V9.5C8.50006 9.95963 8.59059 10.4148 8.76648 10.8394C8.94237 11.264 9.20018 11.6499 9.52519 11.9749C9.85019 12.2999 10.236 12.5577 10.6607 12.7336C11.0853 12.9095 11.5404 13 12.0001 13C12.4597 13 12.9148 12.9095 13.3395 12.7336C13.7641 12.5577 14.1499 12.2999 14.4749 11.9749C14.7999 11.6499 15.0577 11.264 15.2336 10.8394C15.4095 10.4148 15.5001 9.95963 15.5001 9.5V8.5M7.78306 16.703C6.68306 17.388 3.79706 18.785 5.55406 20.534C6.41306 21.39 7.37006 22 8.57106 22H15.4291C16.6311 22 17.5871 21.389 18.4461 20.534C20.2031 18.785 17.3181 17.388 16.2171 16.704C14.9511 15.9174 13.4905 15.5005 12.0001 15.5005C10.5097 15.5005 9.04897 15.9174 7.78306 16.704" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span className="font-semibold">นักเรียน / นักศึกษา</span>
            </button>

            <button
              type="button"
              onClick={() => setIsStudent(false)}
              className={`flex-1 flex flex-col items-center justify-center gap-2 p-4 rounded-2xl border-2 transition-all duration-200 ease-in-out ${
                !isStudent
                  ? "border-indigo-600 bg-indigo-50 text-indigo-700 shadow-sm"
                  : "border-slate-200 bg-white text-slate-500 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 17C20.5304 17 21.0391 16.7893 21.4142 16.4142C21.7893 16.0391 22 15.5304 22 15V4C22 3.46957 21.7893 2.96086 21.4142 2.58579C21.0391 2.21071 20.5304 2 20 2H9.46C9.81 2.61 10 3.3 10 4H20V15H11V17M15 7V9H9V22H7V16H5V22H3V14H1.5V9C1.5 8.46957 1.71071 7.96086 2.08579 7.58579C2.46086 7.21071 2.96957 7 3.5 7H15ZM8 4C8 4.53043 7.78929 5.03914 7.41421 5.41421C7.03914 5.78929 6.53043 6 6 6C5.46957 6 4.96086 5.78929 4.58579 5.41421C4.21071 5.03914 4 4.53043 4 4C4 3.46957 4.21071 2.96086 4.58579 2.58579C4.96086 2.21071 5.46957 2 6 2C6.53043 2 7.03914 2.21071 7.41421 2.58579C7.78929 2.96086 8 3.46957 8 4Z" fill="currentColor" />
              </svg>
              <span className="font-semibold">อาจารย์ / ผู้สอน</span>
            </button>
          </motion.div>

          {/* Google Sign-In Button */}
          <motion.div variants={fadeIn} className="pt-2">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-slate-50 px-4 text-slate-500">หรือ</span>
              </div>
            </div>
          </motion.div>

          <motion.div variants={fadeIn}>
            <GoogleSignInButton 
              text="ลงทะเบียนด้วย Google"
              className="border-2 border-slate-200 hover:border-slate-300"
            />
          </motion.div>

          <div className="relative flex items-center justify-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-slate-50 px-4 text-slate-500">หรือลงทะเบียนด้วยอีเมล</span>
            </div>
          </div>

          <form onSubmit={handleRegister} className="space-y-5">
            {/* Avatar Upload */}
            <motion.div variants={fadeIn} className="flex justify-center">
              <div className="relative group">
                <label htmlFor="avatar-upload" className="cursor-pointer block relative">
                  <div className="w-20 h-20 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center bg-slate-50 group-hover:bg-indigo-50 group-hover:border-indigo-300 transition-all overflow-hidden ring-4 ring-white shadow-sm">
                    {avatarPreview ? (
                      <img
                        src={avatarPreview}
                        alt="Avatar preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User size={32} className="text-slate-400 group-hover:text-indigo-400 transition-colors" />
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
              <label className="text-sm font-medium leading-none text-slate-700">
                ชื่อ-นามสกุล (Name)
              </label>
              <div className="relative">
                <Input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="สิทธิกร ศรีรักษ์"
                  required
                  className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
                />
              </div>
            </motion.div>

            {/* Email Input */}
            <motion.div variants={fadeIn} className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700">
                อีเมล (Email)
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="pl-9 h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
                />
              </div>
            </motion.div>

            {/* Student ID Input */}
            {isStudent && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-1.5"
              >
                <label className="text-sm font-medium leading-none text-slate-700">
                  รหัสนักศึกษา (Student ID)
                </label>
                <Input
                  type="text"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  placeholder="เช่น 64012345"
                  required={isStudent}
                  className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
                />
              </motion.div>
            )}

            {/* Password Fields */}
            <motion.div variants={fadeIn} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium leading-none text-slate-700">
                  รหัสผ่าน (Password)
                </label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium leading-none text-slate-700">
                  ยืนยันรหัสผ่าน (Confirm Password)
                </label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
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
