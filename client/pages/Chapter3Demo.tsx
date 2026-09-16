import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  UserPlus,
  LogIn,
  KeyRound,
  FileCheck2,
  Cpu,
  Terminal,
  Sparkles,
  Send,
  UserCheck,
  Cloud,
  ChevronLeft,
  ChevronRight,
  Play,
  RotateCcw,
  CheckCircle2,
  Copy,
  ExternalLink,
  Code2,
  Info,
  Sliders,
  ShieldCheck,
  FileText,
  Upload,
  Image as ImageIcon,
  Clock,
  Check,
  Database,
  Server,
  Zap
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

// Steps Data Structure mapping directly to Chapter 3 pages 135-160
const CHAPTER3_STEPS = [
  {
    id: 1,
    sec: "3.7.1",
    title: "การพัฒนาระบบสมัครสมาชิก (User Registration)",
    pages: "หน้า 135 - 137 (PDF หน้า 138-140)",
    figures: "รูปที่ 3.15, 3.16, 3.17, 3.18",
    icon: UserPlus,
    badge: "Auth & Email Verification",
    description: "ระบบสมัครสมาชิกแบบปกติด้วยอีเมล พร้อมการส่งลิงก์ยืนยันตัวตนผ่าน SMTP API (Google App Passwords)"
  },
  {
    id: 2,
    sec: "3.7.2",
    title: "การพัฒนาระบบล็อกอิน (Login System & JWT)",
    pages: "หน้า 138 - 141 (PDF หน้า 141-144)",
    figures: "รูปที่ 3.19, 3.20, 3.21, 3.22, 3.23",
    icon: LogIn,
    badge: "AuthContext & Bearer Token",
    description: "ระบบเข้าสู่ระบบด้วย Credentials พร้อมจัดเก็บ Token ใน AuthContext สำหรับจัดการ State และผู้ใช้งาน"
  },
  {
    id: 3,
    sec: "3.7.3",
    title: "สมัครสมาชิก/เข้าสู่ระบบด้วย Google Authentication",
    pages: "หน้า 141 - 143 (PDF หน้า 144-146)",
    figures: "รูปที่ 3.24, 3.25, 3.26, 3.27, 3.28, 3.29",
    icon: KeyRound,
    badge: "Firebase OAuth 2.0",
    description: "การยืนยันตัวตนด้วย Google Account ผ่าน Firebase Auth Service Account Key (JSON)"
  },
  {
    id: 4,
    sec: "3.7.4",
    title: "การพัฒนาระบบจัดการข้อสอบ (Exam Management)",
    pages: "หน้า 144 (PDF หน้า 147)",
    figures: "รูปที่ 3.30, 3.31",
    icon: FileCheck2,
    badge: "Exam & Rubric Creator",
    description: "หน้าจอสำหรับผู้สอนสร้างข้อสอบ กำหนดเฉลย เกณฑ์การประเมิน (Rubrics) และโจทย์รูปภาพ"
  },
  {
    id: 5,
    sec: "3.7.5",
    title: "การเชื่อมต่อ LLMs (Gemini API Integration)",
    pages: "หน้า 145 (PDF หน้า 148)",
    figures: "รูปที่ 3.32",
    icon: Cpu,
    badge: "Google AI Studio API",
    description: "การขอ API Key จาก Google AI Studio และการตั้งค่า Environment Variables สำหรับเชื่อมต่อ AI"
  },
  {
    id: 6,
    sec: "3.7.6",
    title: "การกำหนดรูปแบบการตรวจก่อนส่งข้อมูล (Prompt Engineering)",
    pages: "หน้า 148 (PDF หน้า 151)",
    figures: "รูปที่ 3.33",
    icon: Terminal,
    badge: "Prompt Formatting Schema",
    description: "การออกแบบ Prompt Structure รวมโจทย์ เฉลย คำตอบ และ Rubric แปลงเป็น JSON Schema"
  },
  {
    id: 7,
    sec: "3.7.7",
    title: "การทดสอบส่งข้อมูลและรับผลลัพธ์จาก LLM Server",
    pages: "หน้า 150 - 152 (PDF หน้า 153-155)",
    figures: "รูปที่ 3.34 - 3.38",
    icon: Sparkles,
    badge: "LLM Scoring Playground",
    description: "ทดสอบตรวจคำตอบจริงแบบ Text และแบบรูปภาพลายมือเขียน (Multimodal Vision OCR + Scoring)"
  },
  {
    id: 8,
    sec: "3.7.8",
    title: "การทำข้อสอบและส่งคำตอบของผู้เรียน (Student Exam)",
    pages: "หน้า 153 - 154 (PDF หน้า 156-157)",
    figures: "รูปที่ 3.39, 3.40, 3.41",
    icon: Send,
    badge: "Student Submission & Real-time AI",
    description: "หน้าจอผู้เรียนส่งข้อสอบ ระบบส่งต่อไปยัง AI และส่งการแจ้งเตือน Real-time เมื่อตรวจเสร็จ"
  },
  {
    id: 9,
    sec: "3.7.9",
    title: "ผู้สอนตรวจสอบและแก้ไขผลการประเมินจาก AI",
    pages: "หน้า 154 - 155 (PDF หน้า 157-158)",
    figures: "รูปที่ 3.42, 3.43",
    icon: UserCheck,
    badge: "Teacher Review & Score Override",
    description: "หน้าจอผู้สอนรีวิวผลคะแนนที่ AI ประเมิน สามารถปรับแก้ไขคะแนนและข้อเสนอแนะก่อนอนุมัติ"
  },
  {
    id: 10,
    sec: "3.7.10",
    title: "ระบบจัดเก็บรูปภาพและฐานข้อมูลบนคลาวด์",
    pages: "หน้า 155 - 157 (PDF หน้า 158-160)",
    figures: "รูปที่ 3.44, 3.45, 3.46",
    icon: Cloud,
    badge: "TiDB Cloud DB & Cloud Storage",
    description: "โครงสร้างการอัปโหลดไฟล์ไปยัง Cloud Storage และการเชื่อมต่อฐานข้อมูล TiDB Cloud MySQL"
  }
];

export default function Chapter3Demo() {
  const [currentStep, setCurrentStep] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showInspector, setShowInspector] = useState(true);

  // Step 1 State: Registration
  const [regData, setRegData] = useState({ name: "สมชาย ใจดี", email: "somchai@evaly.ac.th", password: "Password123!" });
  const [regStatus, setRegStatus] = useState<"idle" | "sending_email" | "email_sent" | "verified">("idle");
  const [otpCode, setOtpCode] = useState("");

  // Step 2 State: Login
  const [loginCreds, setLoginCreds] = useState({ email: "somchai@evaly.ac.th", password: "Password123!" });
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Step 3 State: Google Auth
  const [googleState, setGoogleState] = useState<"idle" | "authenticating" | "success">("idle");

  // Step 4 State: Exam Creator
  const [examData, setExamData] = useState({
    title: "การทดสอบวิชา Data Structures (ชุดที่ 1)",
    question: "จงอธิบายความแตกต่างระหว่าง Stack และ Queue พร้อมยกตัวอย่างการใช้งานในชีวิตจริง",
    rubric: "1. นิยาม Stack (2 คะแนน)\n2. นิยาม Queue (2 คะแนน)\n3. ยกตัวอย่างประกอบถูกต้อง (1 คะแนน)"
  });

  // Step 5 State: Gemini API
  const [geminiModel, setGeminiModel] = useState("gemini-1.5-flash");
  const [apiPingStatus, setApiPingStatus] = useState<"idle" | "testing" | "success">("idle");

  // Step 6 State: Prompt Structure
  const [enableMultimodal, setEnableMultimodal] = useState(true);

  // Step 7 State: LLM Playground
  const [testCase, setTestCase] = useState<"text" | "vision">("text");
  const [isScoring, setIsScoring] = useState(false);
  const [aiResult, setAiResult] = useState<any>(null);

  // Step 8 State: Student Exam
  const [studentAnswer, setStudentAnswer] = useState(
    "Stack คือโครงสร้างข้อมูลแบบ LIFO (Last-In, First-Out) เช่น การซ้อนจาน ใบสุดท้ายที่วางจะถูกหยิบออกก่อน ส่วน Queue คือ FIFO (First-In, First-Out) เช่น การเข้าคิวซื้อของ คนมาคนแรกได้ซื้อก่อนครับ"
  );
  const [submitState, setSubmitState] = useState<"idle" | "submitting" | "ai_evaluating" | "completed">("idle");

  // Step 9 State: Teacher Override
  const [teacherScore, setTeacherScore] = useState(5);
  const [teacherComment, setTeacherComment] = useState("ตอบได้ถูกต้อง ชัดเจน ตรงตามเกณฑ์ทุกข้อ");
  const [isApproved, setIsApproved] = useState(false);

  // Step 10 State: Cloud Status
  const [dbConnected, setDbConnected] = useState(true);
  const [cloudStorageConnected, setCloudStorageConnected] = useState(true);

  // Auto Play Handler
  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= 10) {
            setIsPlaying(false);
            return 1;
          }
          return prev + 1;
        });
      }, 7000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  const activeStepInfo = CHAPTER3_STEPS.find((s) => s.id === currentStep)!;

  // Handlers for interactive actions
  const handleSimulateReg = () => {
    setRegStatus("sending_email");
    setTimeout(() => {
      setRegStatus("email_sent");
      toast.success("ส่งอีเมลยืนยันสำเร็จ! (SMTP Google App Passwords)");
    }, 1200);
  };

  const handleVerifyOtp = () => {
    if (otpCode === "8849" || otpCode.length >= 4) {
      setRegStatus("verified");
      toast.success("ยืนยันตัวตนสำเร็จ! บัญชีของคุณพร้อมใช้งานแล้ว");
    } else {
      toast.error("รหัส OTP ไม่ถูกต้อง (ลองพิมพ์ 8849)");
    }
  };

  const handleSimulateLogin = () => {
    setAuthToken("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDEiLCJlbWFpbCI6InNvbWNoYWlAZXZhbHkuYWMudGgiLCJyb2xlIjoidGVhY2hlciIsImlhdCI6MTcwMDAwMDAwMH0");
    toast.success("เข้าสู่ระบบสำเร็จ! Token ถูกเก็บลง AuthContext");
  };

  const handleSimulateGoogle = () => {
    setGoogleState("authenticating");
    setTimeout(() => {
      setGoogleState("success");
      toast.success("Google OAuth 2.0 สำเร็จ! ยืนยันตัวตนด้วย Firebase Auth Key");
    }, 1500);
  };

  const handleTestApi = () => {
    setApiPingStatus("testing");
    setTimeout(() => {
      setApiPingStatus("success");
      toast.success(`เชื่อมต่อ Google Gemini API (${geminiModel}) สำเร็จ! Latency: 142ms`);
    }, 1000);
  };

  const handleRunAiScoring = () => {
    setIsScoring(true);
    setAiResult(null);
    setTimeout(() => {
      setIsScoring(false);
      if (testCase === "text") {
        setAiResult({
          score: 5,
          max_score: 5,
          confidence_score: 0.96,
          rationale: "ผู้เรียนอธิบายความแตกต่างระหว่าง LIFO และ FIFO ได้อย่างถูกต้องสมบูรณ์ และยกตัวอย่างการซ้อนจานกับการเข้าคิวซื้อของตรงตามบริบทจริง",
          rubric_breakdown: [
            { criteria: "นิยาม Stack (LIFO)", score: 2, max: 2, status: "Pass" },
            { criteria: "นิยาม Queue (FIFO)", score: 2, max: 2, status: "Pass" },
            { criteria: "ตัวอย่างประกอบในชีวิตจริง", score: 1, max: 1, status: "Pass" }
          ]
        });
      } else {
        setAiResult({
          score: 4,
          max_score: 5,
          confidence_score: 0.91,
          ocr_text_extracted: "Stack = LIFO (Last In First Out)\nQueue = FIFO (First In First Out)\nExample: Stack = Books pile, Queue = Line waiting for food",
          rationale: "AI สามารถอ่านลายมือจากรูปภาพได้ถูกต้อง 98% ผู้เรียนระบุหลักการ LIFO/FIFO และยกตัวอย่างได้ครบถ้วน แต่นิยามยังสั้นไปเล็กน้อย",
          rubric_breakdown: [
            { criteria: "การอ่าน OCR ลายมือ", score: 1, max: 1, status: "Verified" },
            { criteria: "นิยาม Stack & Queue", score: 3, max: 3, status: "Pass" },
            { criteria: "ตัวอย่างในชีวิตจริง", score: 1, max: 1, status: "Pass" }
          ]
        });
      }
      toast.success("AI ประเมินผลข้อสอบสำเร็จ!");
    }, 1800);
  };

  const handleStudentSubmit = () => {
    setSubmitState("submitting");
    setTimeout(() => {
      setSubmitState("ai_evaluating");
      setTimeout(() => {
        setSubmitState("completed");
        toast.success("ส่งคำตอบสำเร็จ! AI ได้ประเมินผลและส่ง Notification แล้ว");
      }, 1500);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 ring-1 ring-white/20">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg tracking-tight text-white">Evaly System Development Demo</h1>
              <Badge variant="outline" className="border-indigo-500/40 text-indigo-300 bg-indigo-500/10 text-xs">
                Chapter 3 (หน้า 135-160)
              </Badge>
            </div>
            <p className="text-xs text-slate-400">โปรแกรมสาธิตการทำงานขั้นตอนการพัฒนาระบบ (หัวข้อ 3.7.1 - 3.7.10)</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsPlaying(!isPlaying)}
            className={`border-slate-700 ${isPlaying ? "bg-amber-500/20 text-amber-300 border-amber-500/40" : "hover:bg-slate-800 text-slate-300"}`}
          >
            {isPlaying ? <RotateCcw className="w-4 h-4 mr-1.5 animate-spin" /> : <Play className="w-4 h-4 mr-1.5" />}
            {isPlaying ? "Pause Auto-Play" : "Auto-Play Presentation"}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowInspector(!showInspector)}
            className="text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <Code2 className="w-4 h-4 mr-1.5" />
            {showInspector ? "Hide Schema" : "Show Schema"}
          </Button>

          <Link to="/home">
            <Button size="sm" className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-lg shadow-indigo-600/30">
              เข้าสู่ระบบหลัก Evaly <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Stepper Bar */}
      <div className="bg-slate-900/50 border-b border-slate-800/80 px-6 py-3 overflow-x-auto scrollbar-none">
        <div className="flex items-center min-w-max gap-2">
          {CHAPTER3_STEPS.map((step) => {
            const Icon = step.icon;
            const isActive = step.id === currentStep;
            const isDone = step.id < currentStep;

            return (
              <button
                key={step.id}
                onClick={() => setCurrentStep(step.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 ring-1 ring-indigo-400/30"
                    : isDone
                    ? "bg-slate-800/60 text-slate-300 hover:bg-slate-800"
                    : "bg-slate-900 text-slate-500 hover:bg-slate-800/40 hover:text-slate-400"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isActive ? "bg-white text-indigo-600" : isDone ? "bg-indigo-500/20 text-indigo-400" : "bg-slate-800 text-slate-500"
                  }`}
                >
                  {isDone ? <Check className="w-3 h-3" /> : step.id}
                </div>
                <span>{step.sec}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Grid Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Component Demo (8 cols) */}
        <div className={`${showInspector ? "lg:col-span-8" : "lg:col-span-12"} space-y-6 transition-all duration-300`}>
          {/* Header Card for Active Step */}
          <Card className="bg-slate-900/90 border-slate-800 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2.5">
                  <Badge variant="outline" className="border-indigo-500/30 text-indigo-400 bg-indigo-500/10 font-mono">
                    หัวข้อ {activeStepInfo.sec}
                  </Badge>
                  <Badge className="bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    {activeStepInfo.badge}
                  </Badge>
                </div>
                <div className="text-xs text-slate-400 flex items-center gap-3">
                  <span>📖 {activeStepInfo.pages}</span>
                  <span>🖼️ {activeStepInfo.figures}</span>
                </div>
              </div>
              <CardTitle className="text-xl font-bold text-white flex items-center gap-2 mt-2">
                {activeStepInfo.title}
              </CardTitle>
              <CardDescription className="text-slate-400 text-sm">
                {activeStepInfo.description}
              </CardDescription>
            </CardHeader>
          </Card>

          {/* Dynamic Interactive Demo Widget per Step */}
          <Card className="bg-slate-900/90 border-slate-800 shadow-2xl min-h-[420px] flex flex-col justify-between">
            <CardContent className="p-6 flex-1">
              {/* STEP 1: Registration */}
              {currentStep === 1 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                        <UserPlus className="w-4 h-4" /> ฟอร์มสมัครสมาชิก (Normal Email Signup)
                      </h3>
                      <div>
                        <Label className="text-xs text-slate-400">ชื่อ-นามสกุล</Label>
                        <Input
                          value={regData.name}
                          onChange={(e) => setRegData({ ...regData, name: e.target.value })}
                          className="bg-slate-950 border-slate-800 mt-1"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-slate-400">อีเมลสถานศึกษา/อีเมลทั่วไป</Label>
                        <Input
                          value={regData.email}
                          onChange={(e) => setRegData({ ...regData, email: e.target.value })}
                          className="bg-slate-950 border-slate-800 mt-1"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-slate-400">รหัสผ่าน</Label>
                        <Input
                          type="password"
                          value={regData.password}
                          onChange={(e) => setRegData({ ...regData, password: e.target.value })}
                          className="bg-slate-950 border-slate-800 mt-1"
                        />
                      </div>
                      <Button
                        onClick={handleSimulateReg}
                        disabled={regStatus === "sending_email" || regStatus === "verified"}
                        className="w-full bg-indigo-600 hover:bg-indigo-500 text-white"
                      >
                        {regStatus === "sending_email" ? "กำลังส่งอีเมลผ่าน SMTP..." : "สมัครสมาชิกและส่งลิงก์ยืนยัน"}
                      </Button>
                    </div>

                    {/* Simulated Email Inbox */}
                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                          <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
                            <Clock className="w-3.5 h-3.5 text-indigo-400" /> กล่องข้อความอีเมลจำลอง (SMTP Log)
                          </span>
                          <Badge variant="outline" className="text-[10px] border-emerald-500/30 text-emerald-400">
                            Gmail SMTP Verified
                          </Badge>
                        </div>

                        {regStatus === "idle" && (
                          <div className="py-12 text-center text-xs text-slate-500">
                            กรอกข้อมูลสมัครสมาชิกแล้วกดปุ่มเพื่อทดสอบระบบส่งอีเมลยืนยันตัวตน
                          </div>
                        )}

                        {regStatus !== "idle" && (
                          <div className="mt-4 space-y-3">
                            <div className="bg-slate-900 border border-indigo-500/30 p-3 rounded-lg text-xs space-y-2">
                              <div className="flex justify-between text-slate-400">
                                <span>จาก: evaly-noreply@gmail.com</span>
                                <span>ถึง: {regData.email}</span>
                              </div>
                              <div className="font-bold text-white">กรุณายืนยันตัวตนการสมัครสมาชิก Evaly</div>
                              <p className="text-slate-300">
                                รหัสยืนยัน OTP สำหรับบัญชีคุณคือ: <span className="font-mono text-indigo-400 font-bold">8849</span>
                              </p>
                            </div>

                            {regStatus !== "verified" && (
                              <div className="flex gap-2 mt-4">
                                <Input
                                  placeholder="กรอก OTP (8849)"
                                  value={otpCode}
                                  onChange={(e) => setOtpCode(e.target.value)}
                                  className="bg-slate-900 border-slate-700 text-xs"
                                />
                                <Button onClick={handleVerifyOtp} size="sm" className="bg-emerald-600 hover:bg-emerald-500">
                                  ยืนยัน OTP
                                </Button>
                              </div>
                            )}

                            {regStatus === "verified" && (
                              <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 flex items-center gap-2 font-medium">
                                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> ยืนยันตัวตนสำเร็จแล้ว!
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-500 pt-3 border-t border-slate-800">
                        อ้างอิงเอกสาร: รูปที่ 3.16 Google App Passwords & SMTP Environment Variables
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 2: Login & JWT */}
              {currentStep === 2 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                        <LogIn className="w-4 h-4" /> ฟอร์มเข้าสู่ระบบ (Credentials Login)
                      </h3>
                      <div>
                        <Label className="text-xs text-slate-400">อีเมล/รหัสนิสิต</Label>
                        <Input
                          value={loginCreds.email}
                          onChange={(e) => setLoginCreds({ ...loginCreds, email: e.target.value })}
                          className="bg-slate-950 border-slate-800 mt-1"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-slate-400">รหัสผ่าน</Label>
                        <Input
                          type="password"
                          value={loginCreds.password}
                          onChange={(e) => setLoginCreds({ ...loginCreds, password: e.target.value })}
                          className="bg-slate-950 border-slate-800 mt-1"
                        />
                      </div>
                      <Button onClick={handleSimulateLogin} className="w-full bg-indigo-600 hover:bg-indigo-500">
                        เข้าสู่ระบบและสร้าง JWT Bearer Token
                      </Button>
                    </div>

                    {/* AuthContext State Viewer */}
                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                        <span className="text-xs font-bold text-slate-300">AuthContext State & Bearer Token</span>
                        <Badge variant="outline" className={`text-[10px] ${authToken ? "border-emerald-500/30 text-emerald-400" : "border-slate-700 text-slate-500"}`}>
                          {authToken ? "Authenticated" : "Unauthenticated"}
                        </Badge>
                      </div>

                      {authToken ? (
                        <div className="space-y-3 text-xs">
                          <div>
                            <span className="text-slate-400 block mb-1">JWT Access Token Payload:</span>
                            <pre className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-indigo-300 font-mono text-[11px] overflow-x-auto">
{`{
  "sub": "101",
  "email": "${loginCreds.email}",
  "role": "teacher",
  "name": "อาจารย์ผู้สอน",
  "iat": 1700000000,
  "exp": 1700086400
}`}
                            </pre>
                          </div>
                          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-indigo-300 text-[11px]">
                            Token ถูกบันทึกลงใน LocalStorage และ AuthContext พร้อมส่งไปกับ HTTP Header `Authorization: Bearer Token` ทุกครั้ง
                          </div>
                        </div>
                      ) : (
                        <div className="py-12 text-center text-xs text-slate-500">
                          กดปุ่มเข้าสู่ระบบเพื่อจำลองการสร้าง Token และดู AuthContext State
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 3: Google Auth */}
              {currentStep === 3 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                        <KeyRound className="w-4 h-4" /> Google OAuth 2.0 Integration (Firebase Auth)
                      </h3>
                      <p className="text-xs text-slate-400">
                        เชื่อมต่อสิทธิ์บัญชี Google เพื่อให้ผู้เรียนและผู้สอนสามารถ Sign-in เข้าใช้งานได้ในคลิกเดียว
                      </p>

                      <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                        <Button
                          onClick={handleSimulateGoogle}
                          disabled={googleState === "authenticating"}
                          className="w-full bg-white hover:bg-slate-100 text-slate-900 font-medium flex items-center justify-center gap-2"
                        >
                          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" className="w-4 h-4" alt="Google" />
                          {googleState === "authenticating" ? "กำลังตรวจสอบสิทธิ์กับ Google..." : "Sign in with Google"}
                        </Button>

                        {googleState === "success" && (
                          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> ยืนยันตัวตน Google ID Token สำเร็จ
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                        <span className="text-xs font-bold text-slate-300">Firebase Service Account Key (JSON)</span>
                        <Badge variant="outline" className="text-[10px] border-purple-500/30 text-purple-300">
                          Backend Admin SDK
                        </Badge>
                      </div>
                      <pre className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-purple-300 font-mono text-[11px] overflow-x-auto">
{`{
  "type": "service_account",
  "project_id": "evaly-llm-scoring",
  "private_key_id": "8f9a...",
  "client_email": "firebase-adminsdk@evaly.iam.gserviceaccount.com",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}`}
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 4: Exam Creator */}
              {currentStep === 4 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                      <FileCheck2 className="w-4 h-4" /> สร้างชุดข้อสอบและกำหนดเกณฑ์ (Exam & Rubric Management)
                    </h3>
                    <Badge variant="outline" className="border-indigo-500/30 text-indigo-300 text-xs">
                      รูปที่ 3.30 หน้าสร้างข้อสอบ
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <div>
                        <Label className="text-xs text-slate-400">ชื่อชุดข้อสอบ</Label>
                        <Input
                          value={examData.title}
                          onChange={(e) => setExamData({ ...examData, title: e.target.value })}
                          className="bg-slate-950 border-slate-800 text-xs mt-1"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-slate-400">คำถามข้อสอบ</Label>
                        <Textarea
                          rows={2}
                          value={examData.question}
                          onChange={(e) => setExamData({ ...examData, question: e.target.value })}
                          className="bg-slate-950 border-slate-800 text-xs mt-1"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-slate-400">เกณฑ์การประเมิน (Rubrics Points)</Label>
                        <Textarea
                          rows={3}
                          value={examData.rubric}
                          onChange={(e) => setExamData({ ...examData, rubric: e.target.value })}
                          className="bg-slate-950 border-slate-800 text-xs mt-1 font-mono text-emerald-400"
                        />
                      </div>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                      <span className="text-xs font-bold text-slate-300 block pb-2 border-b border-slate-800">
                        Exam Payload Schema (ส่งเข้า DB)
                      </span>
                      <pre className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-emerald-300 font-mono text-[11px] overflow-x-auto h-48">
{JSON.stringify(
  {
    exam_title: examData.title,
    max_score: 5,
    questions: [
      {
        id: "Q1",
        prompt: examData.question,
        rubric_criteria: examData.rubric.split("\n"),
        allow_multimodal_vision: true
      }
    ]
  },
  null,
  2
)}
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 5: Gemini API Connection */}
              {currentStep === 5 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                        <Cpu className="w-4 h-4" /> Google AI Studio API Configuration
                      </h3>

                      <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-4">
                        <div>
                          <Label className="text-xs text-slate-400">เลือกโมเดล AI (LLM Model Selection)</Label>
                          <select
                            value={geminiModel}
                            onChange={(e) => setGeminiModel(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-md p-2 mt-1"
                          >
                            <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast & Cost Efficient)</option>
                            <option value="gemini-1.5-pro">Gemini 1.5 Pro (High Reasoning & Multimodal Accuracy)</option>
                          </select>
                        </div>

                        <div>
                          <Label className="text-xs text-slate-400">GEMINI_API_KEY (Environment Variable)</Label>
                          <Input readOnly value="AIzaSyB8x..." className="bg-slate-900 border-slate-800 text-xs text-slate-500 font-mono" />
                        </div>

                        <Button onClick={handleTestApi} disabled={apiPingStatus === "testing"} className="w-full bg-indigo-600 hover:bg-indigo-500">
                          {apiPingStatus === "testing" ? "กำลังทดสอบเชื่อมต่อ API..." : "ทดสอบปิงเชื่อมต่อ LLM Server"}
                        </Button>

                        {apiPingStatus === "success" && (
                          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 flex items-center justify-between">
                            <span className="flex items-center gap-2">
                              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Status 200 OK
                            </span>
                            <span className="font-mono text-[10px]">Latency: 142ms</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                        <span className="text-xs font-bold text-slate-300">Python Backend AI Service Integration</span>
                        <Badge variant="outline" className="text-[10px] border-indigo-500/30 text-indigo-300">
                          ai_service.py
                        </Badge>
                      </div>
                      <pre className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-cyan-300 font-mono text-[11px] overflow-x-auto">
{`import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="${geminiModel}",
    generation_config={"response_mime_type": "application/json"}
)`}
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 6: Prompt Engineering */}
              {currentStep === 6 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                      <Terminal className="w-4 h-4" /> โครงสร้าง Prompt Engineering (Prompt Formatting)
                    </h3>
                    <Badge variant="outline" className="border-indigo-500/30 text-indigo-300 text-xs">
                      รูปที่ 3.33 ในเอกสาร
                    </Badge>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>System Prompt & Rubric Structure (ส่งตรงเข้า LLM)</span>
                      <div className="flex items-center gap-2">
                        <Label htmlFor="multimodal" className="text-[11px]">เปิดใช้งาน Multimodal Vision (OCR)</Label>
                        <Switch id="multimodal" checked={enableMultimodal} onCheckedChange={setEnableMultimodal} />
                      </div>
                    </div>

                    <pre className="bg-slate-900 p-3 rounded-lg border border-slate-800 text-slate-200 font-mono text-[11px] leading-relaxed overflow-x-auto max-h-64">
{`[SYSTEM INSTRUCTION]
คุณคือผู้เชี่ยวชาญด้านการตรวจข้อสอบวิชา Data Structures ให้ประเมินคำตอบของผู้เรียนตามเกณฑ์ Rubric อย่างเคร่งครัดและเที่ยงตรง

[QUESTION]: จงอธิบายความแตกต่างระหว่าง Stack และ Queue
[RUBRIC CRITERIA]: 
1. นิยาม Stack (LIFO) = 2 คะแนน
2. นิยาม Queue (FIFO) = 2 คะแนน
3. ตัวอย่างการใช้งานจริง = 1 คะแนน

[STUDENT SUBMISSION]:
"Stack คือ LIFO เช่นจาน Queue คือ FIFO เช่นคิวซื้อของ"
${enableMultimodal ? "[MULTIMODAL ATTACHMENT]: base64_image_handwriting_sample.png" : ""}

[JSON OUTPUT FORMAT REQUIREMENTS]:
{
  "score": float,
  "rationale": string,
  "rubric_breakdown": array
}`}
                    </pre>
                  </div>
                </div>
              )}

              {/* STEP 7: LLM Playground */}
              {currentStep === 7 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                      <Sparkles className="w-4 h-4" /> ทดลองส่งคำตอบตรวจจริงกับ LLM (LLM Scoring Playground)
                    </h3>

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant={testCase === "text" ? "default" : "outline"}
                        onClick={() => setTestCase("text")}
                        className={testCase === "text" ? "bg-indigo-600" : "border-slate-700 text-xs"}
                      >
                        ข้อ 1: คำตอบแบบข้อความ (Text)
                      </Button>
                      <Button
                        size="sm"
                        variant={testCase === "vision" ? "default" : "outline"}
                        onClick={() => setTestCase("vision")}
                        className={testCase === "vision" ? "bg-indigo-600" : "border-slate-700 text-xs"}
                      >
                        ข้อ 2: ลายมือเขียน (Vision OCR)
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3 bg-slate-950 border border-slate-800 p-4 rounded-xl">
                      <span className="text-xs font-bold text-slate-300 block">
                        {testCase === "text" ? "โจทย์และคำตอบแบบ Text (รูปที่ 3.34)" : "โจทย์และรูปภาพลายมือ (รูปที่ 3.36, 3.37)"}
                      </span>

                      {testCase === "text" ? (
                        <div className="space-y-2 text-xs">
                          <p className="text-slate-400">คำถาม: จงบอกความแตกต่าง Stack vs Queue</p>
                          <div className="p-2.5 bg-slate-900 border border-slate-800 rounded text-slate-200">
                            Stack เป็น LIFO ซ้อนจาน ส่วน Queue เป็น FIFO เข้าคิวซื้อสินค้าครับ
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-2 text-xs">
                          <p className="text-slate-400">ภาพลายมือเขียนนักเรียนที่อัปโหลด:</p>
                          <div className="p-3 bg-slate-900 border border-slate-700 rounded-lg flex items-center justify-center gap-3 text-slate-400">
                            <ImageIcon className="w-8 h-8 text-indigo-400" />
                            <span>[รูปถ่ายกระดาษคำตอบลายมือเขียนของนิสิต]</span>
                          </div>
                        </div>
                      )}

                      <Button onClick={handleRunAiScoring} disabled={isScoring} className="w-full bg-indigo-600 hover:bg-indigo-500">
                        {isScoring ? "กำลังประเมินผลผ่าน Gemini API..." : "ส่งให้ AI ตรวจและประเมินผล"}
                      </Button>
                    </div>

                    {/* AI Scoring Result JSON */}
                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                      <span className="text-xs font-bold text-slate-300 block">
                        ผลลัพธ์ JSON ตอบกลับจาก LLM Server (รูปที่ 3.35, 3.38)
                      </span>
                      {aiResult ? (
                        <div className="space-y-2 text-xs">
                          <div className="flex justify-between items-center bg-indigo-500/10 p-2 rounded border border-indigo-500/30">
                            <span className="font-bold text-indigo-300">คะแนนที่ได้: {aiResult.score} / {aiResult.max_score}</span>
                            <Badge className="bg-emerald-500/20 text-emerald-300">Confidence: {aiResult.confidence_score * 100}%</Badge>
                          </div>
                          <p className="text-slate-300 bg-slate-900 p-2 rounded border border-slate-800 text-[11px]">
                            {aiResult.rationale}
                          </p>
                        </div>
                      ) : (
                        <div className="py-12 text-center text-xs text-slate-500">
                          กดปุ่ม "ส่งให้ AI ตรวจ" เพื่อรับผลลัพธ์ JSON จำลอง
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 8: Student Exam */}
              {currentStep === 8 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                      <Send className="w-4 h-4" /> หน้าจอผู้เรียนทำข้อสอบ (Student Exam & Real-time AI)
                    </h3>
                    <Badge variant="outline" className="border-indigo-500/30 text-indigo-300 text-xs">
                      รูปที่ 3.39 หน้าการทำข้อสอบ
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3 bg-slate-950 border border-slate-800 p-4 rounded-xl">
                      <div className="flex justify-between text-xs">
                        <span className="font-bold text-slate-200">คำถาม: ความแตกต่าง Stack vs Queue</span>
                        <span className="text-amber-400 font-mono flex items-center gap-1">
                          <Clock className="w-3 h-3" /> เวลาคงเหลือ: 14:35 นาที
                        </span>
                      </div>

                      <Textarea
                        rows={4}
                        value={studentAnswer}
                        onChange={(e) => setStudentAnswer(e.target.value)}
                        className="bg-slate-900 border-slate-800 text-xs"
                      />

                      <Button
                        onClick={handleStudentSubmit}
                        disabled={submitState !== "idle"}
                        className="w-full bg-emerald-600 hover:bg-emerald-500"
                      >
                        {submitState === "submitting"
                          ? "กำลังส่งคำตอบ..."
                          : submitState === "ai_evaluating"
                          ? "AI กำลังประเมินผล Real-time..."
                          : "ยืนยันส่งคำตอบข้อสอบ"}
                      </Button>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                      <span className="text-xs font-bold text-slate-300 block pb-2 border-b border-slate-800">
                        Real-time Socket.io Notification Log
                      </span>
                      {submitState === "completed" ? (
                        <div className="space-y-2 text-xs">
                          <div className="p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-indigo-300 space-y-1">
                            <div className="font-bold flex items-center gap-2">
                              <Sparkles className="w-4 h-4 text-indigo-400" /> AI ได้ประเมินข้อสอบเรียบร้อยแล้ว
                            </div>
                            <p className="text-[11px] text-slate-300">
                              ระบบได้บันทึกคะแนนดิบลงฐานข้อมูล และส่งสัญญาณ Socket.io แจ้งเตือนไปยังอาจารย์ผู้สอนเพื่อรออนุมัติ
                            </p>
                          </div>
                        </div>
                      ) : (
                        <div className="py-12 text-center text-xs text-slate-500">
                          กดส่งคำตอบข้อสอบเพื่อดูการแจ้งเตือน Real-time เมื่อ AI ตรวจเสร็จ
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 9: Teacher Review & Override */}
              {currentStep === 9 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                      <UserCheck className="w-4 h-4" /> ผู้สอนตรวจสอบและปรับแก้ไขคะแนน (Teacher Grade Review & Human-in-the-loop)
                    </h3>
                    <Badge variant="outline" className="border-indigo-500/30 text-indigo-300 text-xs">
                      รูปที่ 3.42 ในเอกสาร
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-3">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-bold text-slate-300">ผลการประเมินจาก AI (ดิบ):</span>
                        <Badge className="bg-indigo-500/20 text-indigo-300">AI Score: 5/5</Badge>
                      </div>
                      <p className="text-xs text-slate-400 bg-slate-900 p-2.5 rounded border border-slate-800">
                        AI Comment: ผู้เรียนอธิบายความแตกต่างได้สมบูรณ์และถูกต้องตามเกณฑ์ Rubric
                      </p>

                      <div className="pt-2 border-t border-slate-800 space-y-3">
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>อาจารย์แก้ไขคะแนนสุทธิ (Override Score):</span>
                            <span className="font-bold text-emerald-400">{teacherScore} คะแนน</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="5"
                            value={teacherScore}
                            onChange={(e) => setTeacherScore(Number(e.target.value))}
                            className="w-full accent-indigo-500"
                          />
                        </div>

                        <div>
                          <Label className="text-xs text-slate-400">ข้อเสนอแนะเพิ่มเติมจากอาจารย์</Label>
                          <Textarea
                            rows={2}
                            value={teacherComment}
                            onChange={(e) => setTeacherComment(e.target.value)}
                            className="bg-slate-900 border-slate-800 text-xs mt-1"
                          />
                        </div>

                        <Button
                          onClick={() => {
                            setIsApproved(true);
                            toast.success("อนุมัติผลคะแนนเรียบร้อยแล้ว!");
                          }}
                          className="w-full bg-indigo-600 hover:bg-indigo-500"
                        >
                          บันทึกและอนุมัติประกาศผลคะแนน
                        </Button>
                      </div>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                      <span className="text-xs font-bold text-slate-300 block pb-2 border-b border-slate-800">
                        การบันทึกสถานะลงฐานข้อมูล (Approved Submission)
                      </span>
                      {isApproved ? (
                        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 space-y-2">
                          <div className="font-bold flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> อนุมัติการตรวจเรียบร้อยแล้ว
                          </div>
                          <pre className="bg-slate-900 p-2 rounded text-[10px] text-slate-300 font-mono overflow-x-auto">
{JSON.stringify(
  {
    submission_id: 88,
    final_score: teacherScore,
    is_teacher_overridden: teacherScore !== 5,
    teacher_feedback: teacherComment,
    status: "published"
  },
  null,
  2
)}
                          </pre>
                        </div>
                      ) : (
                        <div className="py-12 text-center text-xs text-slate-500">
                          กดปุ่ม "บันทึกและอนุมัติประกาศผลคะแนน" เพื่อดู Payload ที่บันทึก
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 10: Cloud Infrastructure */}
              {currentStep === 10 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                      <Cloud className="w-4 h-4" /> โครงสร้างบริการคลาวด์และฐานข้อมูล (Cloud Storage & TiDB Cloud)
                    </h3>
                    <Badge variant="outline" className="border-indigo-500/30 text-indigo-300 text-xs">
                      รูปที่ 3.44, 3.45, 3.46
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
                      <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs">
                        <Database className="w-4 h-4" /> TiDB Cloud MySQL DB
                      </div>
                      <p className="text-[11px] text-slate-400">
                        ฐานข้อมูลคลาวด์แบบ Serverless Distributed SQL ช่วยรองรับการขยายตัวและจัดเก็บข้อมูลอย่างปลอดภัย
                      </p>
                      <Badge className="bg-emerald-500/20 text-emerald-300 text-[10px]">Connected via TLS/SSL</Badge>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
                      <div className="flex items-center gap-2 text-purple-400 font-bold text-xs">
                        <Cloud className="w-4 h-4" /> Cloud Image Storage
                      </div>
                      <p className="text-[11px] text-slate-400">
                        จัดเก็บไฟล์รูปภาพลายมือเขียนและรูปภาพโจทย์ข้อสอบผ่าน Supabase / Firebase Cloud Bucket
                      </p>
                      <Badge className="bg-emerald-500/20 text-emerald-300 text-[10px]">Bucket Public Access Enabled</Badge>
                    </div>

                    <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
                      <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs">
                        <Server className="w-4 h-4" /> Environment Secrets
                      </div>
                      <p className="text-[11px] text-slate-400">
                        แยกแยะกุญแจสำคัญผ่าน `.env` ทั้ง API Key, DB Connection String และ Secret Token
                      </p>
                      <Badge className="bg-emerald-500/20 text-emerald-300 text-[10px]">Vault Secured</Badge>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>

            {/* Bottom Stepper Controls */}
            <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentStep((p) => Math.max(1, p - 1))}
                disabled={currentStep === 1}
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
              >
                <ChevronLeft className="w-4 h-4 mr-1" /> ย้อนกลับ (Previous Step)
              </Button>

              <span className="text-xs text-slate-500 font-mono">
                Step {currentStep} of {CHAPTER3_STEPS.length}
              </span>

              <Button
                size="sm"
                onClick={() => setCurrentStep((p) => Math.min(CHAPTER3_STEPS.length, p + 1))}
                disabled={currentStep === CHAPTER3_STEPS.length}
                className="bg-indigo-600 hover:bg-indigo-500 text-white"
              >
                ถัดไป (Next Step) <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </Card>
        </div>

        {/* Right Column: Schema Inspector & Chapter 3 Document Reference (4 cols) */}
        {showInspector && (
          <div className="lg:col-span-4 space-y-6">
            {/* PDF Page Quick Ref Card */}
            <Card className="bg-slate-900/90 border-slate-800 shadow-xl">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-2">
                  <Info className="w-4 h-4" /> สรุปข้อมูลบทที่ 3 ที่เกี่ยวข้อง
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs space-y-3 text-slate-300">
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-400">เลขหัวข้อในเอกสาร:</div>
                  <div className="font-mono text-indigo-300 font-bold">{activeStepInfo.sec}</div>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-400">ตำแหน่งในรูปเล่ม PDF:</div>
                  <div className="font-medium text-amber-300">{activeStepInfo.pages}</div>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-400">รูปภาพอ้างอิงในเอกสาร:</div>
                  <div className="font-mono text-emerald-300">{activeStepInfo.figures}</div>
                </div>
              </CardContent>
            </Card>

            {/* Live API Route & Tech Spec Card */}
            <Card className="bg-slate-900/90 border-slate-800 shadow-xl">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-2">
                  <Terminal className="w-4 h-4" /> Endpoints & Tech Specs
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs space-y-3 text-slate-300">
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Backend Endpoint:</span>
                    <Badge variant="outline" className="text-[10px] border-cyan-500/30 text-cyan-300">
                      REST API
                    </Badge>
                  </div>
                  <code className="block bg-slate-950 p-2 rounded text-cyan-300 font-mono text-[11px] border border-slate-800">
                    {currentStep === 1 && "POST /api/auth/register"}
                    {currentStep === 2 && "POST /api/auth/login"}
                    {currentStep === 3 && "POST /api/auth/google"}
                    {currentStep === 4 && "POST /api/exams/create"}
                    {currentStep === 5 && "GET /api/ai/health"}
                    {currentStep === 6 && "POST /api/ai/build-prompt"}
                    {currentStep === 7 && "POST /api/ai/score-single"}
                    {currentStep === 8 && "POST /api/submissions/submit"}
                    {currentStep === 9 && "POST /api/submissions/override-score"}
                    {currentStep === 10 && "GET /api/cloud/status"}
                  </code>
                </div>

                <div className="pt-2 border-t border-slate-800">
                  <div className="text-slate-400 mb-1">คำแนะนำในการพรีเซนต์กับกรรมการ:</div>
                  <p className="text-[11px] leading-relaxed text-slate-300">
                    หน้านี้ถูกออกแบบมาเพื่อใช้ในการสาธิต (Demo) ขั้นตอนการพัฒนาระบบโดยเฉพาะ ช่วยให้กรรมการเห็นภาพการทำงานจริงของแต่ละโมดูลอย่างเป็นลำดับ โดยไม่ต้องเปิดดูซอร์สโค้ดจำนวนมาก
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 px-6 py-4 text-center text-xs text-slate-500">
        Evaly Auto-Scoring System — Chapter 3 System Development Interactive Presentation Module
      </footer>
    </div>
  );
}
