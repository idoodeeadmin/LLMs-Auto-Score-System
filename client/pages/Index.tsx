import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  ClipboardCheck,
  Eye,
  EyeOff,
  Loader2,
  Mail,
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GoogleSignInButton } from "@/components/GoogleSignInButton";
import { ThemeToggle } from "@/components/ThemeToggle";
import economicsHero from "@/assets/economics-classroom-hero-v4.png";

export default function Index() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [unverifiedEmail, setUnverifiedEmail] = useState("");
  const [isResending, setIsResending] = useState(false);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
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
        navigate(data.user?.role && data.user.role !== "unassigned" ? "/home" : "/select-role");
        return;
      }

      if (data.detail === "not_verified") {
        setUnverifiedEmail(email);
        toast.error("บัญชีนี้ยังไม่ได้ยืนยันอีเมล");
      } else {
        setUnverifiedEmail("");
        const errorMsg = typeof data.detail === "string" ? data.detail : (typeof data.message === "string" ? data.message : "อีเมลหรือรหัสผ่านไม่ถูกต้อง");
        toast.error(errorMsg);
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
      const response = await fetch("/api/auth/resend-verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: unverifiedEmail }),
      });
      const data = await response.json();

      if (response.ok) {
        toast.success("ส่งอีเมลยืนยันอีกครั้งแล้ว กรุณาตรวจสอบกล่องข้อความ");
        if (data.dev_verify_link) {
          toast.info("Dev Mode: ดูลิงก์ยืนยันใน Console Server", {
            duration: 8000,
          });
        }
      } else {
        toast.error(data.detail || "ไม่สามารถส่งอีเมลยืนยันได้");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="workspace auth-workspace login-page flex min-h-screen bg-[#f3f7f5] dark:bg-[#0c1412]">
      <section className="relative hidden min-h-screen w-[46%] max-w-[760px] overflow-hidden bg-[#123d34] lg:flex">
        <img
          src={economicsHero}
          alt="ชั้นเรียนเศรษฐศาสตร์และการเรียนการสอน"
          className="absolute inset-0 h-full w-full object-cover object-[58%_center] brightness-[0.92] saturate-[0.82]"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#062c25]/65 via-[#0c4a3e]/25 to-[#062c25]/95" />

        <div className="relative z-10 flex w-full flex-col justify-between p-10 xl:p-14">
          <div className="flex items-center gap-3 text-white">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15 ring-1 ring-white/25 backdrop-blur-sm">
              <BookOpen className="h-5 w-5" />
            </span>
            <div>
              <p className="text-lg font-semibold leading-none">Evaly</p>
              <p className="mt-1 text-xs text-white/65">พื้นที่การสอบ</p>
            </div>
          </div>

          <div className="max-w-[430px] text-white">
            <span className="mb-5 inline-flex rounded-full border border-white/20 bg-black/10 px-3 py-1.5 text-xs font-medium text-white/85 backdrop-blur-sm">
              ห้องเรียนและการสอบของคุณ
            </span>
            <h1 className="text-[clamp(2.25rem,4vw,3.5rem)] font-semibold leading-[1.12] tracking-[-0.035em]">
              ประเมินงานเขียน
              <br />อย่างเป็นระบบ
            </h1>
            <p className="mt-5 max-w-[390px] text-base leading-7 text-white/78">
              สร้างข้อสอบ ตรวจคำตอบด้วยเกณฑ์เดียวกัน และติดตามผลการเรียนของทั้งชั้นในพื้นที่เดียว
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs text-white/60">
            <span className="h-px w-10 bg-white/35" />
            Evaly Score · Exam workspace
          </div>
        </div>
      </section>

      <main className="relative flex min-h-screen w-full flex-1 items-center justify-center overflow-y-auto px-5 py-20 sm:px-8 lg:px-12">
        <div className="absolute right-5 top-5 sm:right-8 sm:top-7">
          <ThemeToggle />
        </div>

        <div className="w-full max-w-[500px] rounded-2xl border border-[#dfe8e3] bg-white p-6 shadow-[0_30px_80px_-48px_rgba(17,54,45,0.45)] dark:border-[#2a3b35] dark:bg-[#15201d] sm:p-9 lg:p-10">
          <div className="mb-8 flex items-center justify-between lg:hidden">
            <div className="flex items-center gap-2.5 text-[#0f695b] dark:text-[#91c7b8]">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#e8f3ef] dark:bg-[#243a33]"><BookOpen className="h-4 w-4" /></span>
              <span className="font-semibold">Evaly</span>
            </div>
            <Link
              to="/register"
              className="text-sm font-medium text-[var(--work-accent)] hover:underline"
            >
              สร้างบัญชี
            </Link>
          </div>

          <div className="mb-8">
            <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-[#e7f3ef] text-[#0f695b] dark:bg-[#243a33] dark:text-[#91c7b8]">
              <ClipboardCheck className="h-[22px] w-[22px]" />
            </div>
            <h2 className="text-[2rem] font-semibold leading-tight tracking-tight text-[var(--work-ink)]">ยินดีต้อนรับกลับ</h2>
            <p className="mt-2 text-[15px] text-[var(--work-muted)]">
              เข้าสู่ระบบเพื่อดูชั้นเรียน ข้อสอบ และผลคะแนน
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-5">
            <div className="field">
              <label htmlFor="login-email">อีเมล หรือรหัสผู้ใช้</label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--work-muted)]" />
                <Input
                  id="login-email"
                  type="text"
                  autoComplete="username"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@example.com หรือ student001"
                  required
                  className="h-12 !rounded-xl !pl-10"
                />
              </div>
            </div>

            <div className="field">
              <div className="flex items-center justify-between gap-4">
                <label htmlFor="login-password">รหัสผ่าน</label>
                <Link
                  to="/forgot-password"
                  className="text-xs font-medium text-[var(--work-accent)] hover:underline"
                >
                  ลืมรหัสผ่าน?
                </Link>
              </div>
              <div className="relative">
                <Input
                  id="login-password"
                  autoComplete="current-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="กรอกรหัสผ่าน"
                  required
                  className="h-12 rounded-xl pr-10"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน"}
                  onClick={() => setShowPassword((visible) => !visible)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-2 text-[var(--work-muted)] hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {unverifiedEmail && (
              <div
                role="alert"
                className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-100"
              >
                <p className="font-medium">บัญชีนี้ยังไม่ได้ยืนยันอีเมล</p>
                <p className="mt-1 text-xs opacity-80">ตรวจสอบกล่องข้อความ หรือลองส่งลิงก์ใหม่อีกครั้ง</p>
                <button
                  type="button"
                  onClick={handleResend}
                  disabled={isResending}
                  className="mt-3 inline-flex items-center font-medium underline underline-offset-4 disabled:opacity-50"
                >
                  {isResending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  ส่งลิงก์ยืนยันใหม่
                </button>
              </div>
            )}

            <Button type="submit" disabled={isLoading} className="primary-action h-12 w-full text-[15px] shadow-sm">
              {isLoading ? (
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              ) : (
                <>
                  เข้าสู่ระบบ <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </form>

          <div className="my-6 flex items-center gap-3 text-xs text-[var(--work-muted)]">
            <div className="h-px flex-1 bg-[var(--work-line)]" />
            <span>หรือ</span>
            <div className="h-px flex-1 bg-[var(--work-line)]" />
          </div>

          <GoogleSignInButton
            text="เข้าสู่ระบบด้วย Google"
            onSuccess={() => navigate("/home")}
            className="h-12 w-full rounded-xl"
          />

          <p className="mt-6 text-center text-sm text-[var(--work-muted)]">
            ยังไม่มีบัญชี?{" "}
            <Link to="/register" className="font-medium text-[var(--work-accent)] hover:underline">
              สร้างบัญชี
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
