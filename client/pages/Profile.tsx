import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Camera, User, Loader2, Save, Trash2, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";
import { auth } from "@/lib/firebase";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";

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

  const handleLinkGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      const firebaseToken = await result.user.getIdToken();
      
      const res = await fetch("/api/auth/link-google", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ firebase_token: firebaseToken })
      });
      
      if (res.ok) {
        toast.success("ผูกบัญชี Google สำเร็จ!");
        updateUser({ is_verified: 1 });
      } else {
        const err = await res.json();
        toast.error(err.detail || "การผูกบัญชีไม่สำเร็จ");
      }
    } catch (e: any) {
      console.error(e);
      if (e.code !== 'auth/popup-closed-by-user') {
        toast.error("ยกเลิกหรือเกิดข้อผิดพลาดในการผูกบัญชี");
      }
    }
  };

  const handleDeleteAccount = async () => {
    const confirmDelete = window.confirm("คุณแน่ใจหรือไม่ว่าต้องการลบบัญชี? ข้อมูลห้องเรียนและการสอบทั้งหมดของคุณจะถูกลบถาวรและไม่สามารถกู้คืนได้");
    if (!confirmDelete) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/account", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success("ลบบัญชีของคุณเรียบร้อยแล้ว");
        logout();
        navigate("/");
      } else {
        const err = await response.json();
        toast.error(err.detail || "ไม่สามารถลบบัญชีได้");
      }
    } catch (e) {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <Navbar />
      
      <div className="flex justify-center p-4 md:p-8 overflow-y-auto">
        <motion.div 
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="w-full max-w-lg space-y-6 bg-white dark:bg-slate-800 p-8 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700"
        >
          <motion.div variants={fadeIn} className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">ตั้งค่าโปรไฟล์</h2>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 dark:text-slate-500">
                แก้ไขข้อมูลส่วนตัว {user?.role === "student" ? "รหัสนักศึกษา: " + (user?.studentId || "-") : "อาจารย์ผู้สอน"}
              </p>
            </div>
          </motion.div>

          <form onSubmit={handleSave} className="space-y-6 pt-2">
            {/* Avatar Upload */}
            <motion.div variants={fadeIn} className="flex justify-center mb-6">
              <div className="relative group">
                <label htmlFor="avatar-upload" className="cursor-pointer block relative">
                  <div className="w-28 h-28 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center bg-slate-50 dark:bg-slate-900 group-hover:bg-indigo-50 dark:bg-indigo-900/30 group-hover:border-indigo-300 transition-all overflow-hidden ring-4 ring-white shadow-sm">
                    {avatarPreview ? (
                      <img src={avatarPreview} alt="Avatar preview" className="w-full h-full object-cover" />
                    ) : (
                      <User size={40} className="text-slate-400 dark:text-slate-500 group-hover:text-indigo-400 transition-colors" />
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
              <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">ชื่อ-นามสกุล</label>
              <Input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
              />
            </motion.div>

            <motion.div variants={fadeIn} className="space-y-1.5">
              <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">เปลี่ยนรหัสผ่าน (เว้นว่างไว้หากไม่ต้องการเปลี่ยน)</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
              />
            </motion.div>

            {password && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="space-y-1.5"
              >
                <label className="text-sm font-medium leading-none text-slate-700 dark:text-slate-300">ยืนยันรหัสผ่านใหม่</label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="h-11 text-base transition-shadow focus-visible:ring-indigo-500 bg-white dark:bg-slate-800"
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
          
          <div className="pt-6 mt-6 border-t border-slate-100 dark:border-slate-700">
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-3">การเชื่อมต่อบัญชี</h3>
            {user.is_verified === 1 ? (
              <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 rounded-xl text-sm text-green-700">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                </div>
                บัญชีนี้ได้รับการยืนยันระดับความปลอดภัยแล้ว
              </div>
            ) : (
              <div className="p-4 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl">
                 <p className="text-sm text-slate-600 dark:text-slate-400 dark:text-slate-500 mb-4">บัญชีของคุณยังไม่ได้ผูกกับ Google หากลืมรหัสผ่านจะไม่สามารถกู้ผ่านอีเมลได้</p>
                 <Button onClick={handleLinkGoogle} type="button" variant="outline" className="w-full h-11 border-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700">
                    <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/><path fill="none" d="M1 1h22v22H1z"/></svg>
                    ผูกบัญชี Google ทันที
                 </Button>
              </div>
            )}
          </div>

          <div className="pt-6 mt-6 border-t border-red-100">
            <div className="flex items-center gap-2 mb-4 text-red-600">
              <AlertTriangle size={18} />
              <h3 className="text-sm font-bold uppercase tracking-wider">Danger Zone</h3>
            </div>
            <div className="p-4 bg-red-50 dark:bg-red-900/30 border border-red-100 rounded-2xl">
              <p className="text-sm text-red-700 mb-4 font-medium">
                การลบบัญชีจะส่งผลให้ข้อมูลทั้งหมดของคุณหายไปถาวร รวมถึงห้องเรียนและผลการสอบ
              </p>
              <Button 
                onClick={handleDeleteAccount} 
                type="button" 
                variant="destructive" 
                className="w-full h-11 bg-red-600 hover:bg-red-700 shadow-sm shadow-red-100"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                ลบบัญชีของฉันถาวร
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
