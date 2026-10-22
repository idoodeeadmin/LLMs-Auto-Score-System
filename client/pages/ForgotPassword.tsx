import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Mail, Loader2, ArrowRight, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { AuthLayout } from "@/components/AuthLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [recoveryMode, setRecoveryMode] = useState<"email" | "id">("email");
  const [name, setName] = useState("");
  const [studentId, setStudentId] = useState("");
  
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  
  const navigate = useNavigate();

  const handleResetRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      toast.error("กรุณากรอกอีเมล");
      return;
    }

    setIsLoading(true);
    try {
      const payload: any = { email };
      if (recoveryMode === "id") {
        if (!name && !studentId) {
           toast.error("กรุณากรอกชื่อ หรือ รหัสนิสิต อย่างใดอย่างหนึ่ง");
           setIsLoading(false);
           return;
        }
        payload.name = name || undefined;
        payload.student_id = studentId || undefined;
      }

      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        setIsSuccess(true);
        toast.success(data.message || "หากบัญชีมีอีเมลที่ยืนยันแล้ว กรุณาตรวจสอบกล่องข้อความ");
      } else {
        const errorMsg = typeof data.detail === "string" ? data.detail : (typeof data.message === "string" ? data.message : "เกิดข้อผิดพลาด");
        toast.error(errorMsg);
      }
    } catch (error) {
      console.error("Forgot password error:", error);
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <Link to="/" className="mb-8 inline-flex items-center gap-2 text-sm text-[var(--work-muted)] hover:text-[var(--work-accent)]">
        <ArrowLeft className="h-4 w-4" /> กลับไปเข้าสู่ระบบ
      </Link>
      {!isSuccess ? (
        <>
          <div className="mb-8">
            <h1 className="text-3xl font-semibold tracking-tight">ลืมรหัสผ่าน</h1>
            <p className="mt-2 text-sm text-[var(--work-muted)]">เลือกวิธียืนยันตัวตนเพื่อตั้งรหัสผ่านใหม่</p>
          </div>
          <div className="mb-6 flex gap-6 border-b border-[var(--work-line)]" aria-label="วิธีกู้คืนบัญชี">
            {([{ value: "email", label: "รับลิงก์ทางอีเมล" }, { value: "id", label: "ใช้ข้อมูลบัญชี" }] as const).map((mode) => (
              <button key={mode.value} type="button" aria-pressed={recoveryMode === mode.value} onClick={() => setRecoveryMode(mode.value)}
                className={`border-b-2 pb-3 text-sm font-medium transition-colors ${recoveryMode === mode.value ? "border-[var(--work-accent)] text-[var(--work-accent)]" : "border-transparent text-[var(--work-muted)]"}`}>
                {mode.label}
              </button>
            ))}
          </div>
          <form onSubmit={handleResetRequest} className="space-y-5">
            <p className="text-sm leading-6 text-[var(--work-muted)]">
              {recoveryMode === "email" ? "กรอกอีเมลที่ใช้สมัครหรืออีเมล Google ที่ผูกไว้ ระบบจะส่งลิงก์เฉพาะอีเมลที่ยืนยันแล้ว" : "กรอกอีเมลบัญชี พร้อมชื่อหรือรหัสนิสิต ระบบจะส่งลิงก์ไปยังอีเมลที่ยืนยันแล้ว"}
            </p>
            <div className="field">
              <label htmlFor="recovery-email">อีเมลบัญชีหรืออีเมล Google ที่ผูกไว้</label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--work-muted)]" />
                <Input id="recovery-email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="name@example.com" className="h-11 !pl-10" />
              </div>
            </div>
            {recoveryMode === "id" && (
              <>
                <div className="field"><label htmlFor="recovery-name">ชื่อ-นามสกุล</label><Input id="recovery-name" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="ชื่อที่ใช้สมัครบัญชี" className="h-11" /></div>
                <div className="field"><label htmlFor="recovery-student">รหัสนิสิต</label><Input id="recovery-student" value={studentId} onChange={(e) => setStudentId(e.target.value)} placeholder="กรอกแทนชื่อ-นามสกุลได้" className="h-11" /></div>
              </>
            )}
            <Button type="submit" disabled={isLoading} className="primary-action h-11 w-full">
              {isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> กำลังดำเนินการ</> : <>{recoveryMode === "email" ? "ส่งลิงก์ตั้งรหัสผ่านใหม่" : "ยืนยันข้อมูลบัญชี"} <ArrowRight className="ml-2 h-4 w-4" /></>}
            </Button>
          </form>
        </>
      ) : (
        <div role="status" className="space-y-5">
          <CheckCircle2 className="h-8 w-8 text-[var(--work-accent)]" />
          <h1 className="text-3xl font-semibold">ตรวจสอบอีเมลสำหรับกู้คืน</h1>
          <p className="break-words text-sm leading-7 text-[var(--work-muted)]">หากบัญชีมีอีเมลที่ยืนยันแล้ว ระบบจะส่งลิงก์ตั้งรหัสผ่านใหม่ไปที่อีเมลนั้น กรุณาตรวจสอบกล่องข้อความและจดหมายขยะ</p>
          <Button onClick={() => navigate("/")} className="primary-action h-11 w-full">กลับไปเข้าสู่ระบบ</Button>
        </div>
      )}
    </AuthLayout>
  );
}
