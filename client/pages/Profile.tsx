import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Camera, User, Loader2, Save } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";

export default function Profile() {
  const { user, token, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [avatarPreview, setAvatarPreview] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!token || !user) {
      navigate("/");
      return;
    }
    setName(user.name);
    if (user.avatarUrl) {
      setAvatarPreview(`/uploads/avatars/${user.avatarUrl}`);
    }
  }, [user, token, navigate]);

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAvatarFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    if (password && password !== confirmPassword) {
      toast.error("รหัสผ่านไม่ตรงกัน");
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      if (name !== user?.name) formData.append("name", name);
      if (password) formData.append("password", password);
      if (avatarFile) formData.append("avatar", avatarFile);

      // If nothing to update
      let hasUpdate = false;
      for (let pair of formData.entries()) {
        hasUpdate = true;
        break;
      }

      if (!hasUpdate) {
        toast.info("ไม่มีการเปลี่ยนแปลงข้อมูล");
        setIsLoading(false);
        return;
      }

      const response = await fetch("/api/auth/profile", {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("อัปเดตข้อมูลส่วนตัวเรียบร้อย");
        
        const updatePayload: any = {};
        if (name !== user?.name) updatePayload.name = name;
        if (data.avatarUrl) updatePayload.avatarUrl = data.avatarUrl;
        
        updateUser(updatePayload);
        setPassword("");
        setConfirmPassword("");
      } else {
        toast.error(data.detail || "เกิดข้อผิดพลาดในการอัปเดต");
      }
    } catch (error) {
      console.error("Profile update error:", error);
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsLoading(false);
    }
  };

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };
  
  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      
      <div className="flex justify-center p-4 md:p-8 overflow-y-auto">
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="w-full max-w-lg space-y-6 bg-white p-8 rounded-3xl shadow-sm border border-slate-100"
        >
          <motion.div variants={fadeIn} className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-slate-900">ตั้งค่าโปรไฟล์</h2>
              <p className="mt-1 text-sm text-slate-500">
                แก้ไขข้อมูลส่วนตัว {user?.role === "student" ? "รหัสนักศึกษา: " + (user?.studentId || "-") : "อาจารย์ผู้สอน"}
              </p>
            </div>
          </motion.div>

          <form onSubmit={handleSave} className="space-y-6 pt-2">
            {/* Avatar Upload */}
            <motion.div variants={fadeIn} className="flex justify-center mb-6">
              <div className="relative group">
                <label htmlFor="avatar-upload" className="cursor-pointer block relative">
                  <div className="w-28 h-28 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center bg-slate-50 group-hover:bg-indigo-50 group-hover:border-indigo-300 transition-all overflow-hidden ring-4 ring-white shadow-sm">
                    {avatarPreview ? (
                      <img src={avatarPreview} alt="Avatar preview" className="w-full h-full object-cover" />
                    ) : (
                      <User size={40} className="text-slate-400 group-hover:text-indigo-400 transition-colors" />
                    )}
                  </div>
                  <div className="absolute bottom-1 right-1 w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center shadow-md ring-4 ring-white transform group-hover:scale-110 transition-transform">
                    <Camera size={16} className="text-white" />
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

            <motion.div variants={fadeIn} className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700">ชื่อ-นามสกุล</label>
              <Input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
              />
            </motion.div>

            <motion.div variants={fadeIn} className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700">เปลี่ยนรหัสผ่าน (เว้นว่างไว้หากไม่ต้องการเปลี่ยน)</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
              />
            </motion.div>

            {password && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="space-y-1.5"
              >
                <label className="text-sm font-medium leading-none text-slate-700">ยืนยันรหัสผ่านใหม่</label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white"
                />
              </motion.div>
            )}

            <motion.div variants={fadeIn} className="pt-2">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white text-base shadow-md shadow-indigo-100 transition-all active:scale-[0.98]"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" /> บันทึกการเปลี่ยนแปลง
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
