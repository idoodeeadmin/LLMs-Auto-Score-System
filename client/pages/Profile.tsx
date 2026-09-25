import { PageLoading } from "@/components/RouteLoading";
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Camera, User, Loader2, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";
import { auth } from "@/lib/firebase";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";

export default function Profile() {
  const { user, token, updateUser, logout, isLoading: isAuthLoading } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [identityId, setIdentityId] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [avatarPreview, setAvatarPreview] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isAuthLoading && (!token || !user)) {
      navigate("/");
      return;
    }
    if (user) {
      setName(user.name);
      setIdentityId(user.studentId || "");
      if (user.avatarUrl) {
        setAvatarPreview(/^https?:\/\//i.test(user.avatarUrl) || user.avatarUrl.startsWith("/") ? user.avatarUrl : `/uploads/avatars/${user.avatarUrl}`);
      }
    }
  }, [user, token, isAuthLoading, navigate]);

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
      if (identityId.trim() !== (user?.studentId || "")) formData.append("student_id", identityId.trim());
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
        if (Object.prototype.hasOwnProperty.call(data, "studentId")) updatePayload.studentId = data.studentId;
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

  if (isAuthLoading || !user) return <PageLoading layout="form" />;

  return (
    <div className="workspace min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-4xl px-6 py-8 sm:px-10 sm:py-12">
        <Link to="/home" className="mb-7 inline-flex items-center gap-2 text-sm text-[var(--work-muted)] hover:text-[var(--work-accent)]"><ArrowLeft className="h-4 w-4" /> กลับไปชั้นเรียน</Link>
        <header className="mb-8">
          <p className="mb-2 text-sm text-[var(--work-accent)]">บัญชีของคุณ</p>
          <h1 className="text-3xl font-semibold tracking-tight">ตั้งค่าโปรไฟล์</h1>
          <p className="mt-2 text-sm text-[var(--work-muted)]">จัดการข้อมูลส่วนตัวและการเข้าสู่ระบบ</p>
        </header>
        <form onSubmit={handleSave}>
          <section className="grid gap-6 border-t border-[var(--work-line)] py-8 sm:grid-cols-[190px_1fr]" aria-labelledby="personal-title">
            <div><h2 id="personal-title" className="font-semibold">ข้อมูลส่วนตัว</h2><p className="mt-2 text-sm leading-6 text-[var(--work-muted)]">ชื่อและรูปที่แสดงในชั้นเรียน</p></div>
            <div className="min-w-0 space-y-6">
              <div className="flex items-center gap-5">
                <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full border border-[var(--work-line)] bg-[var(--work-paper)]">
                  {avatarPreview ? <img src={avatarPreview} alt="รูปโปรไฟล์ของคุณ" className="h-full w-full object-cover" /> : <User className="h-8 w-8 text-[var(--work-muted)]" />}
                </div>
                <div className="min-w-0">
                  <label htmlFor="avatar-upload" className="mb-2 flex items-center gap-2 text-sm font-medium"><Camera className="h-4 w-4" /> เปลี่ยนรูปโปรไฟล์</label>
                  <input id="avatar-upload" type="file" accept="image/*" onChange={handleAvatarChange} className="block w-full min-w-0 text-xs text-[var(--work-muted)] file:mr-3 file:cursor-pointer file:rounded-md file:border file:border-solid file:border-[var(--work-line)] file:bg-[var(--work-paper)] file:px-3 file:py-2 file:text-[var(--work-ink)]" />
                </div>
              </div>
              <div className="field"><label htmlFor="profile-name">ชื่อ-นามสกุล</label><Input id="profile-name" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} required className="h-11" /></div>
              <div className="field"><label htmlFor="profile-identity">{user.role === "teacher" ? "รหัสผู้สอน" : "รหัสนิสิต"} (ไม่บังคับ)</label><Input id="profile-identity" type="text" value={identityId} onChange={(e) => setIdentityId(e.target.value)} className="h-11" /></div>
              <div className="text-sm"><p className="text-[var(--work-muted)]">บัญชีที่ใช้เข้าสู่ระบบ</p><p className="mt-1 break-all">{user.email}</p></div>
            </div>
          </section>
          <section className="grid gap-6 border-t border-[var(--work-line)] py-8 sm:grid-cols-[190px_1fr]" aria-labelledby="password-title">
            <div><h2 id="password-title" className="font-semibold">รหัสผ่าน</h2><p className="mt-2 text-sm leading-6 text-[var(--work-muted)]">เว้นว่างไว้หากไม่ต้องการเปลี่ยนรหัสผ่าน</p></div>
            <div className="space-y-5">
              <div className="field"><label htmlFor="profile-password">รหัสผ่านใหม่</label><Input id="profile-password" type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} className="h-11" /></div>
              <div className="field"><label htmlFor="profile-confirm">ยืนยันรหัสผ่านใหม่</label><Input id="profile-confirm" type="password" autoComplete="new-password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required={!!password} className="h-11" /></div>
            </div>
          </section>
          <div className="flex justify-end pb-8"><Button type="submit" disabled={isLoading} className="primary-action h-11 w-full sm:w-auto">{isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}บันทึกการเปลี่ยนแปลง</Button></div>
        </form>
        <section className="grid gap-6 border-t border-[var(--work-line)] py-8 sm:grid-cols-[190px_1fr]" aria-labelledby="verification-title">
          <h2 id="verification-title" className="font-semibold">การยืนยันบัญชี</h2>
          {user.is_verified === 1 ? <p className="flex items-center gap-2 text-sm text-[var(--work-accent)]"><CheckCircle2 className="h-4 w-4" /> ยืนยันอีเมลแล้ว</p> :
            <div><p className="mb-4 text-sm leading-6 text-[var(--work-muted)]">เชื่อมต่อบัญชี Google เพื่อยืนยันอีเมลของคุณ</p><Button onClick={handleLinkGoogle} type="button" variant="outline" disabled={isLoading}>เชื่อมต่อ Google</Button></div>}
        </section>
        <section className="grid gap-6 border-t border-[var(--work-line)] py-8 sm:grid-cols-[190px_1fr]" aria-labelledby="delete-title">
          <h2 id="delete-title" className="font-semibold">ลบบัญชี</h2>
          <div><p className="mb-4 text-sm leading-6 text-[var(--work-muted)]">ข้อมูลบัญชี ห้องเรียน และผลการสอบจะถูกลบถาวร และไม่สามารถกู้คืนได้</p><Button onClick={handleDeleteAccount} disabled={isLoading} type="button" variant="outline" className="border-red-300 text-red-700 hover:bg-red-50 hover:text-red-800 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950">ลบบัญชีถาวร</Button></div>
        </section>
      </main>
    </div>
  );
}
