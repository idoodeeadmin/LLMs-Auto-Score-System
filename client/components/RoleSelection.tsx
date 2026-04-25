import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, BookOpen, ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export function RoleSelection() {
  const { user, token, updateUser } = useAuth();
  const [selectedRole, setSelectedRole] = useState<'teacher' | 'student' | null>(null);
  const [studentId, setStudentId] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedRole) return;
    if (selectedRole === 'student' && !studentId.trim()) {
      toast.error("กรุณากรอกรหัสนักศึกษา");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/set-role", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          role: selectedRole,
          student_id: selectedRole === 'student' ? studentId : null
        })
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("บันทึกบทบาทสำเร็จ!");
        updateUser({ 
          role: selectedRole,
          studentId: selectedRole === 'student' ? studentId : undefined
        });
      } else {
        toast.error(data.detail || "เกิดข้อผิดพลาดในการบันทึก");
      }
    } catch (error) {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <div className="fixed inset-0 z-50 flex min-h-screen items-center justify-center overflow-hidden bg-slate-900 font-sans">
      {/* Dynamic Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/50 via-slate-900 to-purple-900/50 opacity-80" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
      
      {/* Decorative Orbs */}
      <motion.div 
        animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-indigo-500/30 blur-[128px]"
      />
      <motion.div 
        animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0.4, 0.2] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-purple-500/30 blur-[128px]"
      />

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 w-full max-w-2xl px-6"
      >
        <motion.div variants={itemVariants} className="mb-10 text-center">
          <h1 className="mb-4 text-4xl font-extrabold tracking-tight text-white md:text-5xl drop-shadow-sm">
            ยินดีต้อนรับ, <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">{user?.name}</span>
          </h1>
          <p className="text-lg text-slate-300">
            กรุณาเลือกบทบาทของคุณเพื่อเริ่มต้นใช้งานระบบ Evaly
          </p>
        </motion.div>

        <motion.div variants={itemVariants} className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Teacher Card */}
          <button
            onClick={() => {
              setSelectedRole('teacher');
              setStudentId(""); // Clear student ID if they switch to teacher
            }}
            className={`group relative flex flex-col items-center justify-center gap-4 rounded-3xl border border-white/10 p-8 text-center transition-all duration-300 overflow-hidden ${
              selectedRole === 'teacher'
                ? "bg-white/20 shadow-[0_0_40px_rgba(99,102,241,0.3)] ring-2 ring-indigo-400 backdrop-blur-xl scale-[1.02]"
                : "bg-white/5 backdrop-blur-md hover:bg-white/10 hover:scale-[1.02]"
            }`}
          >
            {selectedRole === 'teacher' && (
              <motion.div layoutId="active-bg" className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-purple-500/20" />
            )}
            <div className={`relative z-10 rounded-full p-5 transition-colors duration-300 ${
              selectedRole === 'teacher' ? "bg-indigo-500/30 text-indigo-200" : "bg-white/10 text-slate-300 group-hover:bg-white/20 group-hover:text-white"
            }`}>
              <BookOpen size={40} />
            </div>
            <div className="relative z-10">
              <h3 className={`text-2xl font-bold transition-colors ${selectedRole === 'teacher' ? "text-white" : "text-slate-200 group-hover:text-white"}`}>ฉันเป็นอาจารย์</h3>
              <p className="mt-2 text-sm text-slate-400 dark:text-slate-500">สร้างห้องเรียนและการสอบ</p>
            </div>
          </button>

          {/* Student Card */}
          <button
            onClick={() => setSelectedRole('student')}
            className={`group relative flex flex-col items-center justify-center gap-4 rounded-3xl border border-white/10 p-8 text-center transition-all duration-300 overflow-hidden ${
              selectedRole === 'student'
                ? "bg-white/20 shadow-[0_0_40px_rgba(168,85,247,0.3)] ring-2 ring-purple-400 backdrop-blur-xl scale-[1.02]"
                : "bg-white/5 backdrop-blur-md hover:bg-white/10 hover:scale-[1.02]"
            }`}
          >
            {selectedRole === 'student' && (
              <motion.div layoutId="active-bg" className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20" />
            )}
            <div className={`relative z-10 rounded-full p-5 transition-colors duration-300 ${
              selectedRole === 'student' ? "bg-purple-500/30 text-purple-200" : "bg-white/10 text-slate-300 group-hover:bg-white/20 group-hover:text-white"
            }`}>
              <User size={40} />
            </div>
            <div className="relative z-10">
              <h3 className={`text-2xl font-bold transition-colors ${selectedRole === 'student' ? "text-white" : "text-slate-200 group-hover:text-white"}`}>ฉันเป็นนักเรียน</h3>
              <p className="mt-2 text-sm text-slate-400 dark:text-slate-500">เข้าร่วมห้องเรียนและทำข้อสอบ</p>
            </div>
          </button>
        </motion.div>

        {/* Student ID Input & Submit Section */}
        <div className="mt-10 h-32 flex flex-col items-center justify-start">
          <AnimatePresence mode="wait">
            {selectedRole && (
              <motion.div
                key="actions"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="w-full max-w-md space-y-6 flex flex-col items-center"
              >
                {selectedRole === 'student' && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="w-full space-y-2"
                  >
                    <label className="text-sm font-medium text-slate-300 ml-1">รหัสนักศึกษา (Student ID)</label>
                    <Input
                      autoFocus
                      type="text"
                      value={studentId}
                      onChange={(e) => setStudentId(e.target.value)}
                      placeholder="เช่น 64012345"
                      className="h-12 bg-white/10 border-white/20 text-white placeholder:text-white/40 focus-visible:ring-purple-400 text-lg"
                    />
                  </motion.div>
                )}

                <Button
                  onClick={handleSubmit}
                  disabled={isLoading || (selectedRole === 'student' && !studentId.trim())}
                  className={`h-12 w-full text-base font-semibold shadow-lg transition-all active:scale-[0.98] ${
                    selectedRole === 'student' 
                      ? "bg-purple-600 hover:bg-purple-700 shadow-purple-500/25" 
                      : "bg-indigo-600 hover:bg-indigo-700 shadow-indigo-500/25"
                  } text-white`}
                >
                  {isLoading ? (
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  ) : (
                    <>
                      ยืนยันบทบาท <ArrowRight className="ml-2 h-5 w-5" />
                    </>
                  )}
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
