import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserCheck, GraduationCap, ArrowRight, School, IdCard } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Input } from "@/components/ui/input";

export default function SelectRole() {
  const navigate = useNavigate();
  const { user, token, updateUser } = useAuth();
  const [identityId, setIdentityId] = useState("");

  const handleChooseRole = async (selectedRole: "teacher" | "student") => {
    const roleName = selectedRole === "teacher" ? "อาจารย์ผู้สอน" : "นิสิต/ผู้เรียน";
    const finalId = identityId.trim() || user?.studentId || user?.email || user?.name || (selectedRole === "teacher" ? "TEACHER" : "STUDENT");
    
    try {
      const res = await fetch("/api/auth/set-role", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify({
          role: selectedRole,
          identity_id: finalId
        })
      });
      if (res.ok) {
        updateUser({ role: selectedRole, studentId: finalId });
        toast.success(`ตั้งค่าสิทธิ์เป็น "${roleName}" เรียบร้อยแล้ว`);
        navigate("/home");
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "ไม่สามารถตั้งค่าสิทธิ์ได้");
      }
    } catch (e) {
      updateUser({ role: selectedRole, studentId: finalId });
      navigate("/home");
    }
  };

  return (
    <div className="auth-workspace relative flex min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 items-center justify-center p-6 font-sans transition-colors duration-200">
      {/* Top Right Theme Toggle */}
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-xl space-y-6 text-center">
        {/* Header */}
        <div className="space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 mx-auto flex items-center justify-center ring-1 ring-blue-200 dark:ring-blue-800">
            <School className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            เลือกสิทธิ์การเข้าใช้งาน (Select Your Role)
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto leading-relaxed">
            ยินดีต้อนรับเข้าสู่ระบบ Evaly กรุณาเลือกบทบาทของคุณเพื่อเริ่มต้นการใช้งาน
          </p>
        </div>

        {/* Optional Student / Teacher ID Input */}
        <div className="max-w-md mx-auto space-y-1.5 text-left bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center justify-between">
            <span>รหัสนิสิต / รหัสประจำตัว (Student/Teacher ID)</span>
            <span className="text-[10px] text-slate-400 font-normal">ไม่บังคับ (Optional)</span>
          </label>
          <div className="relative">
            <IdCard className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              type="text"
              value={identityId}
              onChange={(e) => setIdentityId(e.target.value)}
              placeholder="เช่น 64010001 (หากไม่กรอก ระบบจะใช้อีเมลเป็นค่าเริ่มต้น)"
              className="pl-9 bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-xs h-9"
            />
          </div>
        </div>

        {/* 2 Role Choice Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
          {/* Teacher Card */}
          <div
            onClick={() => handleChooseRole("teacher")}
            className="group bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-blue-500 dark:hover:border-blue-500 p-6 rounded-2xl cursor-pointer transition shadow-sm hover:shadow-md space-y-4 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 flex items-center justify-center">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition">
                  อาจารย์ผู้สอน (Teacher)
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  สำหรับผู้สอนที่ต้องการสร้างห้องเรียน ออกแบบเกณฑ์ Rubrics และตรวจทานคะแนน AI
                </p>
              </div>
            </div>
            <div className="flex items-center text-xs font-semibold text-blue-600 dark:text-blue-400 group-hover:translate-x-1 transition">
              เลือกบทบาทนี้ <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          {/* Student Card */}
          <div
            onClick={() => handleChooseRole("student")}
            className="group bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-emerald-500 dark:hover:border-emerald-500 p-6 rounded-2xl cursor-pointer transition shadow-sm hover:shadow-md space-y-4 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <GraduationCap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition">
                  นิสิต / ผู้เรียน (Student)
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  สำหรับผู้เรียนที่ต้องการเข้าร่วมห้องเรียน ส่งกระดาษคำตอบ และดูคะแนนประเมิน
                </p>
              </div>
            </div>
            <div className="flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400 group-hover:translate-x-1 transition">
              เลือกบทบาทนี้ <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
