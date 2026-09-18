import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, ClipboardCheck, Eye, EyeOff, Loader2, Mail } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";
import economicsHero from "@/assets/economics-classroom-hero-v4.png";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

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
        body: JSON.stringify({ email, password, name, role: "unassigned" }),
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

  return (
    <div className="workspace auth-workspace register-page flex min-h-screen bg-[var(--work-canvas)]">
      <section className="relative hidden min-h-screen w-1/2 overflow-hidden bg-[#203c32] lg:flex">
        <img src={economicsHero} alt="ชั้นเรียนเศรษฐศาสตร์และการเรียนการสอน" className="absolute inset-0 h-full w-full object-cover object-[55%_center] brightness-[0.92] saturate-[0.82]" />
        <div className="absolute inset-0 bg-gradient-to-b from-[#062c25]/65 via-[#0c4a3e]/25 to-[#062c25]/95" />
        <div className="relative z-10 flex w-full flex-col justify-between p-12 xl:p-16">
          <div className="workspace-brand text-white">Evaly <span className="border-white/20 text-white/70">พื้นที่การสอบ</span></div>
          <div className="max-w-[380px] text-white">
            <p className="mb-4 text-sm font-medium text-white/80">พื้นที่การสอบสำหรับชั้นเรียนของคุณ</p>
            <h1 className="max-w-[380px] text-4xl font-semibold leading-[1.18] tracking-tight">
              สร้างชั้นเรียน
              <br />
              และจัดการข้อสอบในที่เดียว
            </h1>
            <p className="mt-5 max-w-[380px] text-base leading-7 text-white/80">
              สร้างห้องเรียน เชิญผู้เรียน มอบหมายข้อสอบ และติดตามคะแนนได้ง่าย
              ในพื้นที่เดียว
            </p>
          </div>
          <p className="text-xs text-white/60">Evaly Score · Exam workspace</p>
        </div>
      </section>

      <main className="flex min-h-screen w-full flex-1 items-center justify-center overflow-y-auto px-6 py-10 sm:px-10 lg:w-1/2 md:px-12 lg:px-16">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center justify-between lg:hidden">
            <div className="login-mobile-brand">Evaly / พื้นที่การสอบ</div>
            <Link to="/" className="text-sm text-[var(--work-muted)] hover:text-[var(--work-accent)]">เข้าสู่ระบบ</Link>
          </div>

          <Link to="/" className="mb-8 inline-flex items-center gap-2 text-sm text-[var(--work-muted)] hover:text-[var(--work-accent)]">
            <ArrowLeft className="h-4 w-4" /> กลับไปเข้าสู่ระบบ
          </Link>
          <div className="mb-8">
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--work-canvas)] text-[var(--work-accent)]"><ClipboardCheck className="h-5 w-5" /></div>
            <h2 className="text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">สร้างบัญชีผู้ใช้</h2>
            <p className="mt-2 text-sm text-[var(--work-muted)]">กรอกข้อมูลเพื่อเริ่มใช้งานระบบ</p>
          </div>

          <form onSubmit={handleRegister} className="space-y-5">
            <div className="field"><label htmlFor="register-name">ชื่อ-นามสกุล</label><Input id="register-name" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="เช่น สิทธิกร ศรีรักษ์" required className="h-11" /></div>
            <div className="field"><label htmlFor="register-email">อีเมล หรือรหัสที่ใช้เข้าสู่ระบบ</label><div className="relative"><Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--work-muted)]" /><Input id="register-email" type="text" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@example.com หรือ student001" required className="h-11 !pl-10" /></div></div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="field"><label htmlFor="register-password">รหัสผ่าน</label><div className="relative"><Input id="register-password" autoComplete="new-password" type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="อย่างน้อย 8 ตัวอักษร" required className="h-11 pr-10" /><button type="button" aria-label={showPassword ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน"} onClick={() => setShowPassword((visible) => !visible)} className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-2 text-[var(--work-muted)] hover:bg-slate-100 dark:hover:bg-slate-800">{showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button></div></div>
              <div className="field"><label htmlFor="register-confirm-password">ยืนยันรหัสผ่าน</label><div className="relative"><Input id="register-confirm-password" autoComplete="new-password" type={showConfirmPassword ? "text" : "password"} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="กรอกอีกครั้ง" required className="h-11 pr-10" /><button type="button" aria-label={showConfirmPassword ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน"} onClick={() => setShowConfirmPassword((visible) => !visible)} className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-2 text-[var(--work-muted)] hover:bg-slate-100 dark:hover:bg-slate-800">{showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button></div></div>
            </div>
            <Button type="submit" disabled={isLoading} className="primary-action h-11 w-full">{isLoading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <>สร้างบัญชี <ArrowRight className="ml-2 h-4 w-4" /></>}</Button>
          </form>

          <div className="my-6 flex items-center gap-3 text-xs text-[var(--work-muted)]"><div className="h-px flex-1 bg-[var(--work-line)]" /><span>หรือ</span><div className="h-px flex-1 bg-[var(--work-line)]" /></div>
          <GoogleSignInButton text="ลงทะเบียนด้วย Google" className="h-11 w-full" />
          <p className="mt-6 text-center text-sm text-[var(--work-muted)]">มีบัญชีอยู่แล้ว? <Link to="/" className="font-medium text-[var(--work-accent)] hover:underline">เข้าสู่ระบบ</Link></p>
        </div>
      </main>
    </div>
  );
}
