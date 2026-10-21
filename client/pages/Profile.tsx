import { confirmAction } from "@/components/ConfirmActionDialog";
import { PageLoading } from "@/components/RouteLoading";
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Camera, User, Loader2, CheckCircle2, Mail, ShieldCheck, Eye, EyeOff } from "lucide-react";
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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [otp, setOtp] = useState("");
  const [isSendingOtp, setIsSendingOtp] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [avatarPreview, setAvatarPreview] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

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

  const handleRequestOtp = async () => {
    if (!password) {
      toast.error("กรุณากรอกรหัสผ่านใหม่ก่อนขอรหัส OTP");
      return;
    }
    if (password.length < 8) {
      toast.error("รหัสผ่านใหม่ต้องมีความยาวอย่างน้อย 8 ตัวอักษร");
      return;
    }
    if (password !== confirmPassword) {
      toast.error("รหัสผ่านใหม่และยืนยันรหัสผ่านไม่ตรงกัน");
      return;
    }

    setIsSendingOtp(true);
    try {
      const res = await fetch("/api/auth/profile/request-password-otp", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      if (res.ok) {
        setOtpSent(true);
        setCountdown(60);
        toast.success(data.message || "ส่งรหัส OTP ไปยังอีเมลเรียบร้อยแล้ว");
        if (data.dev_otp) {
          toast.info(`[Dev Mode] รหัส OTP ของคุณคือ: ${data.dev_otp}`, { duration: 10000 });
        }
      } else {
        toast.error(data.detail || "ไม่สามารถส่งรหัส OTP ได้");
      }
    } catch (error) {
      console.error("Request OTP error:", error);
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsSendingOtp(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    if (password) {
      if (password.length < 8) {
        toast.error("รหัสผ่านใหม่ต้องมีความยาวอย่างน้อย 8 ตัวอักษร");
        return;
      }
      if (password !== confirmPassword) {
        toast.error("รหัสผ่านไม่ตรงกัน");
        return;
      }
      if (!otp || otp.trim().length !== 6) {
        toast.error("กรุณากรอกรหัส OTP 6 หลักที่ได้รับทางอีเมล");
        return;
      }
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      if (name !== user?.name) formData.append("name", name);
      if (identityId.trim() !== (user?.studentId || "")) formData.append("student_id", identityId.trim());
      if (password) {
        formData.append("password", password.trim());
        formData.append("otp", otp.trim());
      }
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
        if (password) {
          await logout();
          toast.success("เปลี่ยนรหัสผ่านเรียบร้อย กรุณาเข้าสู่ระบบอีกครั้ง");
          navigate("/");
          return;
        }
        toast.success("อัปเดตข้อมูลส่วนตัวเรียบร้อย");

        const updatePayload: any = {};
        if (name !== user?.name) updatePayload.name = name;
        if (Object.prototype.hasOwnProperty.call(data, "studentId")) updatePayload.studentId = data.studentId;
        if (data.avatarUrl) updatePayload.avatarUrl = data.avatarUrl;

        updateUser(updatePayload);
        setPassword("");
        setConfirmPassword("");
        setOtp("");
        setOtpSent(false);
        setCountdown(0);
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
        const data = await res.json().catch(() => ({}));
        toast.success("ผูกบัญชี Google สำเร็จ! สามารถใช้ Google บัญชีนี้เข้าสู่ระบบได้โดยตรง");
        updateUser({
          is_verified: 1,
          isGoogleLinked: true,
          googleEmail: data.googleEmail || result.user.email || undefined,
        });
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
    const confirmDelete = await confirmAction("คุณแน่ใจหรือไม่ว่าต้องการลบบัญชี? ข้อมูลห้องเรียนและการสอบทั้งหมดของคุณจะถูกลบถาวรและไม่สามารถกู้คืนได้");
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
            <div>
              <h2 id="password-title" className="font-semibold">รหัสผ่าน</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--work-muted)]">เว้นว่างไว้หากไม่ต้องการเปลี่ยนรหัสผ่าน</p>
            </div>
            <div className="space-y-5">
              <div className="field">
                <label htmlFor="profile-password">รหัสผ่านใหม่</label>
                <div className="relative">
                  <Input
                    id="profile-password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="อย่างน้อย 8 ตัวอักษร"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11 pr-10"
                  />
                  <button
                    type="button"
                    aria-label={showPassword ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน"}
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-2 text-[var(--work-muted)] hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>
              <div className="field">
                <label htmlFor="profile-confirm">ยืนยันรหัสผ่านใหม่</label>
                <div className="relative">
                  <Input
                    id="profile-confirm"
                    type={showConfirmPassword ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="กรอกรหัสผ่านใหม่อีกครั้ง"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required={!!password}
                    className="h-11 pr-10"
                  />
                  <button
                    type="button"
                    aria-label={showConfirmPassword ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน"}
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-2 text-[var(--work-muted)] hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {password && (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4 dark:border-emerald-900/50 dark:bg-emerald-950/20 space-y-3">
                  <div className="flex items-start justify-between gap-3 flex-wrap sm:flex-nowrap">
                    <div>
                      <p className="text-sm font-medium text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                        <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                        การยืนยันความปลอดภัยด้วย OTP
                      </p>
                      <p className="text-xs text-emerald-700/80 dark:text-emerald-400/80 mt-1">
                        ระบบจะส่งรหัสยืนยัน 6 หลักไปยังอีเมล <b>{user.email}</b> ก่อนทำการเปลี่ยนรหัสผ่าน
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleRequestOtp}
                      disabled={isSendingOtp || countdown > 0}
                      className="shrink-0 h-9 border-emerald-300 text-emerald-800 hover:bg-emerald-100 dark:border-emerald-800 dark:text-emerald-200 dark:hover:bg-emerald-900/50 font-medium"
                    >
                      {isSendingOtp ? (
                        <><Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> กำลังส่ง...</>
                      ) : countdown > 0 ? (
                        `ขอใหม่ใน (${countdown}s)`
                      ) : otpSent ? (
                        <><Mail className="mr-1.5 h-3.5 w-3.5" /> ส่งรหัส OTP อีกครั้ง</>
                      ) : (
                        <><Mail className="mr-1.5 h-3.5 w-3.5" /> ขอรหัส OTP ทางอีเมล</>
                      )}
                    </Button>
                  </div>

                  {otpSent && (
                    <div className="pt-2 border-t border-emerald-200/60 dark:border-emerald-800/40">
                      <label htmlFor="profile-otp" className="block text-xs font-medium text-emerald-900 dark:text-emerald-300 mb-1.5">
                        รหัส OTP 6 หลักที่ได้รับทางอีเมล
                      </label>
                      <Input
                        id="profile-otp"
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        maxLength={6}
                        autoComplete="one-time-code"
                        placeholder="123456"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                        className="h-11 max-w-[200px] font-mono text-center tracking-widest text-lg font-bold bg-white dark:bg-slate-900 border-emerald-300 focus-visible:ring-emerald-500"
                        required
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          </section>
          <div className="flex justify-end pb-8"><Button type="submit" disabled={isLoading} className="primary-action h-11 w-full sm:w-auto">{isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}บันทึกการเปลี่ยนแปลง</Button></div>
        </form>
        <section className="grid gap-6 border-t border-[var(--work-line)] py-8 sm:grid-cols-[190px_1fr]" aria-labelledby="verification-title">
          <h2 id="verification-title" className="font-semibold">การเชื่อมต่อ Google</h2>
          {user.isGoogleLinked || user.googleEmail ? (
            <div className="space-y-1.5">
              <p className="flex items-center gap-2 text-sm text-emerald-700 dark:text-emerald-400 font-medium">
                <CheckCircle2 className="h-4 w-4" /> เชื่อมต่อกับบัญชี Google แล้ว
              </p>
              <p className="text-xs text-[var(--work-muted)]">
                {user.googleEmail ? `อีเมล Google: ${user.googleEmail}` : "สามารถเข้าสู่ระบบด้วย Google ได้โดยตรง"}
              </p>
              <p className="text-[11px] text-slate-400">
                (ระบบกำหนด 1 บัญชี Google ผูกได้ 1 บัญชีเว็บเท่านั้น)
              </p>
            </div>
          ) : (
            <div>
              <p className="mb-4 text-sm leading-6 text-[var(--work-muted)]">
                เชื่อมต่อบัญชี Google เพื่อให้สามารถกดเข้าสู่ระบบด้วย Google ได้ทันที (1 บัญชี Google ผูกได้ 1 บัญชีเว็บเท่านั้น)
              </p>
              <Button onClick={handleLinkGoogle} type="button" variant="outline" disabled={isLoading}>
                เชื่อมต่อ Google
              </Button>
            </div>
          )}
        </section>
        <section className="grid gap-6 border-t border-[var(--work-line)] py-8 sm:grid-cols-[190px_1fr]" aria-labelledby="delete-title">
          <h2 id="delete-title" className="font-semibold">ลบบัญชี</h2>
          <div><p className="mb-4 text-sm leading-6 text-[var(--work-muted)]">ข้อมูลบัญชี ห้องเรียน และผลการสอบจะถูกลบถาวร และไม่สามารถกู้คืนได้</p><Button onClick={handleDeleteAccount} disabled={isLoading} type="button" variant="outline" className="border-red-300 text-red-700 hover:bg-red-50 hover:text-red-800 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950">ลบบัญชีถาวร</Button></div>
        </section>
      </main>
    </div>
  );
}
