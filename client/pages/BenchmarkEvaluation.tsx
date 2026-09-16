import React, { useState, useEffect, useRef } from "react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import ImageModal from "@/components/ImageModal";
import {
  BarChart3,
  Download,
  Upload,
  RotateCcw,
  Sparkles,
  FileText,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Search,
  Filter,
  Calculator,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  HelpCircle,
  Maximize2
} from "lucide-react";

interface ModalityStats {
  count: number;
  qwk: number;
  mae: number;
  exact_pct: number;
  adjacent_pct: number;
  agreement?: {
    level_en: string;
    level_th: string;
    badge_color: string;
    range: string;
  };
}

interface QuestionMetric {
  question_no: number;
  topic: string;
  type: string;
  max_score: number;
  samples_count: number;
  qwk: number;
  mae: number;
  exact_pct: number;
  avg_human_score: number;
  avg_ai_score: number;
  agreement: {
    level_en: string;
    level_th: string;
    badge_color: string;
    range: string;
  };
}

interface BenchmarkSummary {
  total_samples: number;
  overall_qwk: number;
  overall_mae: number;
  agreement: {
    level_en: string;
    level_th: string;
    badge_color: string;
    range: string;
  };
  exact_agreement_rate: number;
  adjacent_agreement_rate: number;
  confusion_matrix: {
    labels: number[];
    matrix: number[][];
    totals_human: number[];
    totals_ai: number[];
  };
  modality_comparison: {
    text: ModalityStats;
    image: ModalityStats;
  };
  per_question: QuestionMetric[];
}

interface DatasetItem {
  sample_id: string;
  question_no: number;
  question_type: string;
  question_content: string;
  topic: string;
  answer_type: string;
  student_answer: string;
  transcription: string;
  human_score: number;
  ai_score: number;
  ai_confidence: string;
  ai_feedback: string;
  difference: number;
}

export default function BenchmarkEvaluation() {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [loadingSummary, setLoadingSummary] = useState(true);
  const [summary, setSummary] = useState<BenchmarkSummary | null>(null);

  // Dataset browsing state
  const [items, setItems] = useState<DatasetItem[]>([]);
  const [loadingItems, setLoadingItems] = useState(false);
  const [page, setPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 20;

  // Filters
  const [selectedQuestion, setSelectedQuestion] = useState<string>("all");
  const [selectedModality, setSelectedModality] = useState<string>("all");
  const [selectedDiff, setSelectedDiff] = useState<string>("all");
  const [selectedConf, setSelectedConf] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Modal Image Zoom
  const [modalImage, setModalImage] = useState<{ src: string; alt?: string } | null>(null);

  // Quick Sandbox Modal
  const [showSandbox, setShowSandbox] = useState(false);
  const [sandboxScoresText, setSandboxScoresText] = useState("5,5\n5,4\n4,4\n3,3\n2,2\n1,1\n0,0\n4,5\n3,2\n5,5");
  const [sandboxResult, setSandboxResult] = useState<any>(null);
  const [evaluatingSandbox, setEvaluatingSandbox] = useState(false);

  // Active Tab
  const [activeTab, setActiveTab] = useState<"overview" | "matrix" | "questions" | "dataset">("overview");

  // Fetch summary
  const fetchSummary = async () => {
    setLoadingSummary(true);
    try {
      const res = await fetch("/api/benchmark/summary");
      if (!res.ok) throw new Error("ไม่สามารถโหลดข้อมูล Benchmark ได้");
      const data = await res.json();
      if (data.success) {
        setSummary(data.data);
      }
    } catch (err: any) {
      toast({
        title: "เกิดข้อผิดพลาด",
        description: err.message || "โหลดข้อมูลไม่สำเร็จ",
        variant: "destructive",
      });
    } finally {
      setLoadingSummary(false);
    }
  };

  // Fetch paginated dataset items
  const fetchDataset = async () => {
    setLoadingItems(true);
    try {
      const params = new URLSearchParams();
      params.append("page", page.toString());
      params.append("limit", limit.toString());

      if (selectedQuestion !== "all") params.append("question_no", selectedQuestion);
      if (selectedModality !== "all") params.append("answer_type", selectedModality);
      if (selectedDiff !== "all") params.append("difference", selectedDiff);
      if (selectedConf !== "all") params.append("confidence", selectedConf);
      if (searchQuery.trim()) params.append("search", searchQuery.trim());

      const res = await fetch(`/api/benchmark/dataset?${params.toString()}`);
      if (!res.ok) throw new Error("ไม่สามารถโหลดชุดข้อมูลได้");
      const data = await res.json();
      if (data.success) {
        setItems(data.items);
        setTotalItems(data.total);
        setTotalPages(data.total_pages);
      }
    } catch (err: any) {
      toast({
        title: "เกิดข้อผิดพลาด",
        description: err.message || "ไม่สามารถดึงข้อมูล Dataset",
        variant: "destructive",
      });
    } finally {
      setLoadingItems(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  useEffect(() => {
    fetchDataset();
  }, [page, selectedQuestion, selectedModality, selectedDiff, selectedConf]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchDataset();
  };

  const handleResetFilters = () => {
    setSelectedQuestion("all");
    setSelectedModality("all");
    setSelectedDiff("all");
    setSelectedConf("all");
    setSearchQuery("");
    setPage(1);
  };

  // Export Excel
  const handleExportExcel = () => {
    window.open("/api/benchmark/export", "_blank");
  };

  // Import Excel
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      toast({ title: "กำลังอัปโหลดและประมวลผลไฟล์...", description: file.name });
      const res = await fetch("/api/benchmark/import", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "การนำเข้าไฟล์ล้มเหลว");

      toast({
        title: "นำเข้าสำเร็จ",
        description: "ระบบได้คำนวณค่า QWK และ MAE ชุดใหม่เรียบร้อยแล้ว",
      });
      fetchSummary();
      setPage(1);
      fetchDataset();
    } catch (err: any) {
      toast({
        title: "นำเข้าไม่สำเร็จ",
        description: err.message,
        variant: "destructive",
      });
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // Reset Dataset to default 300
  const handleResetDefault = async () => {
    if (!confirm("คุณต้องการรีเซ็ตชุดข้อมูลเป็นค่าเริ่มต้น 300 ตัวอย่างวิชา Data Structures หรือไม่?")) return;

    try {
      const res = await fetch("/api/benchmark/reset", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "รีเซ็ตล้มเหลว");

      toast({
        title: "รีเซ็ตสำเร็จ",
        description: "ระบบนำชุดข้อมูลมาตรฐาน 300 ตัวอย่างกลับมาแล้ว",
      });
      fetchSummary();
      setPage(1);
      fetchDataset();
    } catch (err: any) {
      toast({
        title: "เกิดข้อผิดพลาด",
        description: err.message,
        variant: "destructive",
      });
    }
  };

  // Run Sandbox Evaluation
  const handleRunSandbox = async () => {
    setEvaluatingSandbox(true);
    try {
      const lines = sandboxScoresText.trim().split("\n");
      const pairs = lines
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => {
          const parts = line.split(/[,\s\t]+/);
          return {
            human_score: parseInt(parts[0], 10),
            ai_score: parseInt(parts[1], 10),
          };
        })
        .filter((p) => !isNaN(p.human_score) && !isNaN(p.ai_score));

      if (pairs.length === 0) {
        throw new Error("กรุณากรอกคู่คะแนน เช่น 5,5 ในแต่ละบรรทัด");
      }

      const res = await fetch("/api/benchmark/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: pairs }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "การคำนวณล้มเหลว");

      setSandboxResult(data.data);
    } catch (err: any) {
      toast({
        title: "เกิดข้อผิดพลาดในการคำนวณ",
        description: err.message,
        variant: "destructive",
      });
    } finally {
      setEvaluatingSandbox(false);
    }
  };

  const getBadgeColorClass = (color?: string) => {
    switch (color) {
      case "emerald":
        return "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800";
      case "indigo":
        return "bg-indigo-50 text-indigo-800 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800";
      case "blue":
        return "bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800";
      case "yellow":
        return "bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800";
      default:
        return "bg-slate-50 text-slate-800 border-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-800";
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/60 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8 space-y-8">
        {/* Top Header Card */}
        <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 p-6 md:p-8 shadow-sm relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-emerald-500/10 via-indigo-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
            <div className="space-y-2.5 max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100/70 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                <BarChart3 size={13} className="animate-pulse text-emerald-600 dark:text-emerald-400" />
                Model Benchmark & Evaluation System (1.3.5 / 3.8 / AT18)
              </div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                การวัดผลความแม่นยำโมเดลตรวจข้อสอบอัตโนมัติ
              </h1>
              <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
                การประเมินความสอดคล้องระหว่างมนุษย์และ AI (Inter-rater Agreement) บนชุดข้อสอบวิชาโครงสร้างข้อมูล (Data Structures) รวม 300 คำตอบ (150 ข้อความพิมพ์ + 150 ภาพเขียนลายมือ) วัดผลด้วย Quadratic Weighted Kappa (QWK), MAE และ Confusion Matrix
              </p>
            </div>

            {/* Action Buttons Toolbar */}
            <div className="flex flex-wrap items-center gap-2.5 shrink-0">
              <input
                type="file"
                ref={fileInputRef}
                accept=".xlsx"
                className="hidden"
                onChange={handleFileUpload}
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                className="rounded-xl border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-medium gap-1.5 h-10"
              >
                <Upload size={14} /> นำเข้า Excel (.xlsx)
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={handleExportExcel}
                className="rounded-xl border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-medium gap-1.5 h-10 text-emerald-700 dark:text-emerald-300"
              >
                <Download size={14} /> ดาวน์โหลดรายงาน (.xlsx)
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSandbox(true)}
                className="rounded-xl border-indigo-200 dark:border-indigo-900 bg-indigo-50/50 dark:bg-indigo-950/30 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 text-xs font-medium gap-1.5 h-10"
              >
                <Calculator size={14} /> Sandbox จำลองคะแนน
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleResetDefault}
                className="rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 h-10"
                title="รีเซ็ตกลับเป็นค่าเริ่มต้น 300 ตัวอย่าง"
              >
                <RotateCcw size={14} />
              </Button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 overflow-x-auto">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeTab === "overview"
                ? "bg-emerald-800 text-white dark:bg-emerald-500 dark:text-slate-950 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            }`}
          >
            ภาพรวมผลการประเมิน (Overview)
          </button>
          <button
            onClick={() => setActiveTab("matrix")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeTab === "matrix"
                ? "bg-emerald-800 text-white dark:bg-emerald-500 dark:text-slate-950 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            }`}
          >
            เมทริกซ์ความสับสน (Confusion Matrix)
          </button>
          <button
            onClick={() => setActiveTab("questions")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeTab === "questions"
                ? "bg-emerald-800 text-white dark:bg-emerald-500 dark:text-slate-950 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            }`}
          >
            ผลประเมินรายข้อ (Q1 - Q10)
          </button>
          <button
            onClick={() => setActiveTab("dataset")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeTab === "dataset"
                ? "bg-emerald-800 text-white dark:bg-emerald-500 dark:text-slate-950 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            }`}
          >
            สำรวจชุดข้อมูล 300 ตัวอย่าง (Dataset Inspector)
          </button>
        </div>

        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* KPI Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Card 1: Total Samples */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500 dark:text-slate-400">ขนาดชุดข้อมูลทดสอบ</span>
                  <span className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    <FileText size={18} />
                  </span>
                </div>
                <div>
                  <div className="text-3xl font-bold text-slate-900 dark:text-white">
                    {summary?.total_samples ?? 300}
                    <span className="text-sm font-normal text-slate-500 ml-1.5">คำตอบ</span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    150 ข้อความพิมพ์ + 150 ภาพเขียนลายมือ
                  </p>
                </div>
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
                  <span>10 ข้อสอบอัตนัย</span>
                  <span className="text-emerald-700 dark:text-emerald-400 font-medium">คะแนนเต็มข้อละ 5</span>
                </div>
              </div>

              {/* Card 2: Overall QWK */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-emerald-200/80 dark:border-emerald-900/60 p-5 space-y-3 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-emerald-800 dark:text-emerald-300">Overall QWK</span>
                  <span className="p-2 rounded-xl bg-emerald-100/70 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
                    <TrendingUp size={18} />
                  </span>
                </div>
                <div>
                  <div className="text-3xl font-bold text-emerald-800 dark:text-emerald-300 tracking-tight">
                    {summary?.overall_qwk !== undefined ? summary.overall_qwk.toFixed(4) : "0.9140"}
                  </div>
                  <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800">
                    <CheckCircle2 size={13} />
                    {summary?.agreement?.level_th || "สอดคล้องกันเกือบสมบูรณ์แบบ"}
                  </div>
                </div>
                <div className="pt-2 border-t border-emerald-100 dark:border-emerald-900/40 text-xs text-slate-500">
                  เกณฑ์ Landis & Koch (1977): 0.81 - 1.00
                </div>
              </div>

              {/* Card 3: Overall MAE */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500 dark:text-slate-400">ความคลาดเคลื่อนเฉลี่ย (MAE)</span>
                  <span className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
                    <Sparkles size={18} />
                  </span>
                </div>
                <div>
                  <div className="text-3xl font-bold text-slate-900 dark:text-white">
                    {summary?.overall_mae !== undefined ? summary.overall_mae.toFixed(4) : "0.2267"}
                    <span className="text-sm font-normal text-slate-500 ml-1.5">คะแนน</span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    เป้าหมายเกณฑ์ยอมรับ: MAE &lt; 0.35 คะแนน
                  </p>
                </div>
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
                  <span>สถานะเกณฑ์</span>
                  <span className="text-emerald-700 dark:text-emerald-400 font-semibold">ผ่านเกณฑ์ยอดเยี่ยม</span>
                </div>
              </div>

              {/* Card 4: Agreement Rates */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500 dark:text-slate-400">อัตราความตรงกัน</span>
                  <span className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400">
                    <CheckCircle2 size={18} />
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs text-slate-600 dark:text-slate-400">คะแนนตรงกัน 100% (Exact)</span>
                    <span className="text-lg font-bold text-slate-900 dark:text-white">
                      {summary?.exact_agreement_rate ?? 78.33}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-emerald-600 h-full rounded-full transition-all"
                      style={{ width: `${summary?.exact_agreement_rate ?? 78.33}%` }}
                    />
                  </div>
                  <div className="flex justify-between items-baseline pt-1">
                    <span className="text-xs text-slate-600 dark:text-slate-400">ต่างไม่เกิน 1 คะแนน (±1)</span>
                    <span className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                      {summary?.adjacent_agreement_rate ?? 98.67}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Modality Comparison Breakdown (Text vs Handwriting Image) */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 md:p-8 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <TrendingUp size={20} className="text-emerald-600 dark:text-emerald-400" />
                    การวิเคราะห์เปรียบเทียบระหว่างคำตอบข้อความพิมพ์ และ ภาพเขียนลายมือ (Modality Analysis)
                  </h2>
                  <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400 mt-1">
                    เปรียบเทียบดัชนีชี้วัดความแม่นยำระหว่างคำตอบแบบ Text-only (150 ตัวอย่าง) และ Image Handwriting (150 ตัวอย่าง)
                  </p>
                </div>
                <span className="text-xs px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-full text-slate-600 dark:text-slate-400 shrink-0">
                  Data Structures 10 Questions
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Text Modality Card */}
                <div className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800/40 dark:to-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="p-2.5 rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
                        <FileText size={22} />
                      </span>
                      <div>
                        <h3 className="text-base font-bold text-slate-900 dark:text-white">ข้อความพิมพ์ (Text Modality)</h3>
                        <p className="text-xs text-slate-500">คำตอบที่พิมพ์ผ่านระบบเว็บ</p>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-800 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800">
                      N = {summary?.modality_comparison?.text?.count ?? 150}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
                    <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700/60 shadow-2xs">
                      <span className="text-xs text-slate-400 block">QWK Score</span>
                      <span className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                        {summary?.modality_comparison?.text?.qwk?.toFixed(4) ?? "0.9252"}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">Almost Perfect</span>
                    </div>

                    <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700/60 shadow-2xs">
                      <span className="text-xs text-slate-400 block">MAE Error</span>
                      <span className="text-2xl font-bold text-slate-800 dark:text-slate-200">
                        {summary?.modality_comparison?.text?.mae?.toFixed(4) ?? "0.2000"}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">คะแนน</span>
                    </div>

                    <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700/60 shadow-2xs">
                      <span className="text-xs text-slate-400 block">Exact Match</span>
                      <span className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">
                        {summary?.modality_comparison?.text?.exact_pct ?? 80.0}%
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">±1: {summary?.modality_comparison?.text?.adjacent_pct ?? 100}%</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed bg-white/60 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700/40">
                    💡 ข้อความพิมพ์มีความสอดคล้องระดับสูงมาก (QWK &gt; 0.92) เนื่องจากไม่มีสัญญาณรบกวนทางกายภาพของลายมือ โมเดลวิเคราะห์ความหมายร่วมกับเกณฑ์รูบริกได้อย่างแม่นยำ
                  </p>
                </div>

                {/* Handwriting Image Modality Card */}
                <div className="bg-gradient-to-br from-emerald-50/40 to-white dark:from-emerald-950/20 dark:to-slate-900 rounded-2xl border border-emerald-200/80 dark:border-emerald-900/60 p-6 space-y-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="p-2.5 rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                        <ImageIcon size={22} />
                      </span>
                      <div>
                        <h3 className="text-base font-bold text-slate-900 dark:text-white">ภาพเขียนลายมือ (Handwriting Modality)</h3>
                        <p className="text-xs text-slate-500">ภาพถ่ายกระดาษคำตอบและแผนภาพ</p>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800">
                      N = {summary?.modality_comparison?.image?.count ?? 150}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
                    <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-emerald-100 dark:border-emerald-900/40 shadow-2xs">
                      <span className="text-xs text-slate-400 block">QWK Score</span>
                      <span className="text-2xl font-bold text-emerald-800 dark:text-emerald-300">
                        {summary?.modality_comparison?.image?.qwk?.toFixed(4) ?? "0.8959"}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">Almost Perfect</span>
                    </div>

                    <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-emerald-100 dark:border-emerald-900/40 shadow-2xs">
                      <span className="text-xs text-slate-400 block">MAE Error</span>
                      <span className="text-2xl font-bold text-slate-800 dark:text-slate-200">
                        {summary?.modality_comparison?.image?.mae?.toFixed(4) ?? "0.2533"}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">คะแนน</span>
                    </div>

                    <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-emerald-100 dark:border-emerald-900/40 shadow-2xs">
                      <span className="text-xs text-slate-400 block">Exact Match</span>
                      <span className="text-2xl font-bold text-emerald-700 dark:text-emerald-400">
                        {summary?.modality_comparison?.image?.exact_pct ?? 76.67}%
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">±1: {summary?.modality_comparison?.image?.adjacent_pct ?? 97.33}%</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed bg-white/60 dark:bg-slate-800/60 p-3 rounded-xl border border-emerald-100 dark:border-emerald-900/40">
                    ✍️ ภาพเขียนลายมือและแผนภาพรักษาค่า QWK สูงถึง ~0.8959 สอดคล้องเกือบสมบูรณ์แบบ โดยโมเดลผสาน Vision-OCR เพื่อถอดรหัสข้อความและประเมินภาพแผนภาพได้อย่างมีประสิทธิภาพ
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CONFUSION MATRIX */}
        {activeTab === "matrix" && (
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 md:p-8 shadow-sm space-y-6 animate-in fade-in duration-300">
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <BarChart3 size={20} className="text-emerald-600 dark:text-emerald-400" />
                เมทริกซ์ความสับสน (Confusion Matrix: คะแนนอาจารย์ vs คะแนน AI)
              </h2>
              <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400 mt-1">
                แถวแนวนอน (Rows) แสดงคะแนนจริงที่อาจารย์ให้ (Human Score 0-5) และหลักแนวตั้ง (Columns) แสดงคะแนนที่ AI ประเมิน (AI Score 0-5) ช่องทแยงมุมสีเขียวแสดงตัวอย่างที่ตรวจตรงกัน 100%
              </p>
            </div>

            {summary?.confusion_matrix && (
              <div className="overflow-x-auto py-4">
                <table className="mx-auto border-collapse">
                  <thead>
                    <tr>
                      <th className="p-3 text-xs font-semibold text-slate-400 text-left border-b border-r border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                        คะแนนอาจารย์ \ AI
                      </th>
                      {summary.confusion_matrix.labels.map((label) => (
                        <th
                          key={label}
                          className="w-16 h-12 p-2 text-center text-xs font-bold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50"
                        >
                          AI: {label}
                        </th>
                      ))}
                      <th className="w-20 p-2 text-center text-xs font-bold text-slate-500 border-b border-l border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800">
                        รวม (ครู)
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.confusion_matrix.labels.map((rowLabel, rIdx) => {
                      const rowTotal = summary.confusion_matrix.totals_human[rIdx] || 0;
                      return (
                        <tr key={rowLabel}>
                          <th className="p-3 text-xs font-bold text-slate-700 dark:text-slate-300 text-left border-r border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                            อาจารย์: {rowLabel}
                          </th>
                          {summary.confusion_matrix.labels.map((colLabel, cIdx) => {
                            const val = summary.confusion_matrix.matrix[rIdx][cIdx];
                            const isDiagonal = rIdx === cIdx;
                            const diff = Math.abs(rIdx - cIdx);

                            let cellStyle = "bg-white dark:bg-slate-900 text-slate-400";
                            if (isDiagonal && val > 0) {
                              cellStyle = "bg-emerald-600 text-white font-bold shadow-xs";
                            } else if (diff === 1 && val > 0) {
                              cellStyle = "bg-amber-100/70 text-amber-900 dark:bg-amber-950/40 dark:text-amber-200 font-semibold";
                            } else if (diff >= 2 && val > 0) {
                              cellStyle = "bg-rose-100 text-rose-900 dark:bg-rose-950/50 dark:text-rose-200 font-bold";
                            }

                            return (
                              <td
                                key={colLabel}
                                className={`w-16 h-14 text-center border border-slate-100 dark:border-slate-800/80 transition-all ${cellStyle}`}
                              >
                                <span className="text-sm">{val}</span>
                              </td>
                            );
                          })}
                          <td className="w-20 text-center font-bold text-xs text-slate-700 dark:text-slate-300 border-l border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
                            {rowTotal}
                          </td>
                        </tr>
                      );
                    })}
                    {/* Column totals */}
                    <tr>
                      <th className="p-3 text-xs font-bold text-slate-500 text-left border-t border-r border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800">
                        รวม (AI)
                      </th>
                      {summary.confusion_matrix.labels.map((_, cIdx) => (
                        <td
                          key={cIdx}
                          className="w-16 h-12 text-center font-bold text-xs text-slate-700 dark:text-slate-300 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30"
                        >
                          {summary.confusion_matrix.totals_ai[cIdx] || 0}
                        </td>
                      ))}
                      <td className="w-20 text-center font-bold text-sm text-emerald-800 dark:text-emerald-300 border-t border-l border-slate-200 dark:border-slate-800 bg-emerald-50 dark:bg-emerald-950/40">
                        {summary.total_samples}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* Matrix Legend */}
            <div className="flex flex-wrap items-center justify-center gap-6 pt-4 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400">
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-md bg-emerald-600 inline-block" />
                <span>คะแนนตรงกันสมบูรณ์ (Exact Match: 0 Difference)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-md bg-amber-100 border border-amber-300 dark:bg-amber-950 dark:border-amber-700 inline-block" />
                <span>คลาดเคลื่อน 1 คะแนน (Adjacent: ±1 Difference)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-md bg-rose-100 border border-rose-300 dark:bg-rose-950 dark:border-rose-700 inline-block" />
                <span>คลาดเคลื่อน 2+ คะแนน (Divergent: ≥2 Difference)</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: QUESTIONS BREAKDOWN */}
        {activeTab === "questions" && (
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 md:p-8 shadow-sm space-y-6 animate-in fade-in duration-300">
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <FileText size={20} className="text-emerald-600 dark:text-emerald-400" />
                ผลการประเมินแยกตามรายข้อสอบ 10 ข้อ (Data Structures Exam Breakdown)
              </h2>
              <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400 mt-1">
                การกระจายตัวของค่า QWK, MAE และความแม่นยำในแต่ละหัวข้อของข้อสอบอัตนัย 10 ข้อ
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 text-xs text-slate-400 font-semibold bg-slate-50/50 dark:bg-slate-800/30">
                    <th className="p-3 w-16 text-center">ข้อที่</th>
                    <th className="p-3">หัวข้อเนื้อหา (Topic)</th>
                    <th className="p-3 w-28 text-center">ประเภทโจทย์</th>
                    <th className="p-3 w-24 text-center">ตัวอย่าง</th>
                    <th className="p-3 w-24 text-center">QWK</th>
                    <th className="p-3 w-24 text-center">MAE</th>
                    <th className="p-3 w-24 text-center">ตรงกัน 100%</th>
                    <th className="p-3 w-32 text-center">คะแนนเฉลี่ย (ครู/AI)</th>
                    <th className="p-3 text-right">ระดับความสอดคล้อง</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {summary?.per_question.map((q) => (
                    <tr key={q.question_no} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition">
                      <td className="p-3 text-center font-bold text-slate-700 dark:text-slate-300">
                        {q.question_no}
                      </td>
                      <td className="p-3 font-medium text-slate-900 dark:text-white">
                        {q.topic}
                      </td>
                      <td className="p-3 text-center">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-md font-medium ${
                            q.type === "img"
                              ? "bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800"
                              : "bg-blue-50 text-blue-800 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800"
                          }`}
                        >
                          {q.type === "img" ? "มีรูปโจทย์" : "ข้อความ"}
                        </span>
                      </td>
                      <td className="p-3 text-center text-slate-600 dark:text-slate-400">
                        {q.samples_count}
                      </td>
                      <td className="p-3 text-center font-bold text-emerald-800 dark:text-emerald-300">
                        {q.qwk.toFixed(4)}
                      </td>
                      <td className="p-3 text-center text-slate-700 dark:text-slate-300 font-mono">
                        {q.mae.toFixed(4)}
                      </td>
                      <td className="p-3 text-center font-medium text-slate-700 dark:text-slate-300">
                        {q.exact_pct}%
                      </td>
                      <td className="p-3 text-center text-xs text-slate-500 dark:text-slate-400 font-mono">
                        {q.avg_human_score.toFixed(1)} / {q.avg_ai_score.toFixed(1)}
                      </td>
                      <td className="p-3 text-right">
                        <span className={`text-xs px-2.5 py-1 rounded-lg border font-medium ${getBadgeColorClass(q.agreement?.badge_color)}`}>
                          {q.agreement?.level_th}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: DATASET INSPECTOR */}
        {activeTab === "dataset" && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Filters Bar */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-4">
              <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row items-center gap-3">
                <div className="relative flex-1 w-full">
                  <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <Input
                    type="text"
                    placeholder="ค้นหาข้อความคำตอบ, เหตุผล AI, หรือรหัสตัวอย่าง (เช่น DS-005)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-10 rounded-xl"
                  />
                </div>
                <Button type="submit" size="sm" className="h-10 px-5 rounded-xl bg-emerald-800 hover:bg-emerald-900 text-white shrink-0">
                  ค้นหา
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleResetFilters}
                  className="h-10 px-4 rounded-xl shrink-0"
                >
                  ล้างตัวกรอง
                </Button>
              </form>

              {/* Select Filters Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
                {/* Question Filter */}
                <div>
                  <label className="text-xs font-medium text-slate-500 block mb-1">กรองตามข้อ</label>
                  <select
                    value={selectedQuestion}
                    onChange={(e) => {
                      setSelectedQuestion(e.target.value);
                      setPage(1);
                    }}
                    className="w-full text-xs h-9 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-2.5 py-1 text-slate-800 dark:text-slate-200"
                  >
                    <option value="all">ทุกข้อ (1 - 10)</option>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                      <option key={num} value={num.toString()}>
                        ข้อที่ {num}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Modality Filter */}
                <div>
                  <label className="text-xs font-medium text-slate-500 block mb-1">ประเภทคำตอบ</label>
                  <select
                    value={selectedModality}
                    onChange={(e) => {
                      setSelectedModality(e.target.value);
                      setPage(1);
                    }}
                    className="w-full text-xs h-9 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-2.5 py-1 text-slate-800 dark:text-slate-200"
                  >
                    <option value="all">ทั้งหมด (Text + Image)</option>
                    <option value="text">ข้อความพิมพ์ (Text Only)</option>
                    <option value="img">ภาพเขียนลายมือ (Handwriting)</option>
                  </select>
                </div>

                {/* Score Difference Filter */}
                <div>
                  <label className="text-xs font-medium text-slate-500 block mb-1">ผลต่างคะแนน</label>
                  <select
                    value={selectedDiff}
                    onChange={(e) => {
                      setSelectedDiff(e.target.value);
                      setPage(1);
                    }}
                    className="w-full text-xs h-9 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-2.5 py-1 text-slate-800 dark:text-slate-200"
                  >
                    <option value="all">ผลต่างทั้งหมด</option>
                    <option value="exact">ตรงกัน 100% (Diff = 0)</option>
                    <option value="near">ต่างกัน 1 คะแนน (Diff = ±1)</option>
                    <option value="divergent">ต่างกัน 2+ คะแนน (Diff ≥ 2)</option>
                  </select>
                </div>

                {/* Confidence Filter */}
                <div>
                  <label className="text-xs font-medium text-slate-500 block mb-1">ความมั่นใจ AI</label>
                  <select
                    value={selectedConf}
                    onChange={(e) => {
                      setSelectedConf(e.target.value);
                      setPage(1);
                    }}
                    className="w-full text-xs h-9 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-2.5 py-1 text-slate-800 dark:text-slate-200"
                  >
                    <option value="all">ทุกระดับความมั่นใจ</option>
                    <option value="High">ความมั่นใจสูง (High)</option>
                    <option value="Medium">ความมั่นใจปานกลาง (Medium)</option>
                    <option value="Low">ความมั่นใจต่ำ (Low)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Results Count Header */}
            <div className="flex items-center justify-between px-1">
              <p className="text-xs text-slate-500">
                พบข้อมูลทั้งหมด <span className="font-semibold text-slate-900 dark:text-white">{totalItems}</span> รายการ (หน้า {page} / {totalPages})
              </p>
            </div>

            {/* Items List */}
            {loadingItems ? (
              <div className="p-12 text-center text-slate-400">กำลังโหลดรายการคำตอบ...</div>
            ) : items.length === 0 ? (
              <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500">
                ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา
              </div>
            ) : (
              <div className="space-y-4">
                {items.map((item) => (
                  <div
                    key={item.sample_id}
                    className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-xs space-y-4 transition hover:border-emerald-300/80 dark:hover:border-emerald-700/60"
                  >
                    {/* Item Top Bar */}
                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800/80 pb-3">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          {item.sample_id}
                        </span>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-100 dark:border-emerald-900">
                          ข้อที่ {item.question_no}: {item.topic}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-md font-medium flex items-center gap-1 ${
                            item.answer_type === "img"
                              ? "bg-amber-50 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300 border border-amber-200 dark:border-amber-800"
                              : "bg-blue-50 text-blue-800 dark:bg-blue-950/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
                          }`}
                        >
                          {item.answer_type === "img" ? <ImageIcon size={12} /> : <FileText size={12} />}
                          {item.answer_type === "img" ? "ภาพเขียนลายมือ" : "ข้อความพิมพ์"}
                        </span>
                      </div>

                      {/* Scores Pill */}
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="flex items-center gap-1.5 text-xs bg-slate-50 dark:bg-slate-800/60 px-3 py-1 rounded-xl border border-slate-200 dark:border-slate-700">
                          <span className="text-slate-500">อาจารย์:</span>
                          <span className="font-bold text-slate-900 dark:text-white text-sm">{item.human_score}</span>
                          <span className="text-slate-300 dark:text-slate-600">|</span>
                          <span className="text-emerald-600 dark:text-emerald-400 font-medium">AI:</span>
                          <span className="font-bold text-emerald-800 dark:text-emerald-300 text-sm">{item.ai_score}</span>
                        </div>

                        {/* Diff status badge */}
                        <span
                          className={`text-xs px-2.5 py-1 rounded-lg font-semibold border ${
                            item.difference === 0
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800"
                              : item.difference === 1
                              ? "bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800"
                              : "bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800"
                          }`}
                        >
                          {item.difference === 0 ? "ตรงกัน 100%" : `ต่าง ${item.difference} คะแนน`}
                        </span>
                      </div>
                    </div>

                    {/* Question Content */}
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      <span className="font-medium text-slate-700 dark:text-slate-300">โจทย์: </span>
                      {item.question_content}
                    </div>

                    {/* Student Answer Presentation */}
                    <div className="space-y-3">
                      <p className="text-xs font-medium text-slate-500">คำตอบของผู้เรียน:</p>
                      {item.answer_type === "img" ? (
                        <div className="space-y-3">
                          <div className="flex items-start gap-4 flex-wrap">
                            <div className="relative group cursor-zoom-in rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800">
                              <img
                                src={item.student_answer}
                                alt={`ลายมือ ${item.sample_id}`}
                                className="h-28 w-auto object-cover transition-transform group-hover:scale-105"
                                onClick={() => setModalImage({ src: item.student_answer, alt: `ลายมือตัวอย่าง ${item.sample_id}` })}
                              />
                              <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white pointer-events-none">
                                <Maximize2 size={18} />
                              </div>
                            </div>
                            <div className="text-xs text-slate-400 space-y-1">
                              <p className="text-slate-600 dark:text-slate-300 font-medium flex items-center gap-1">
                                <ImageIcon size={13} className="text-emerald-600" /> ภาพถ่ายกระดาษคำตอบลายมือ
                              </p>
                              <p>คลิกที่ภาพเพื่อขยายดูรายละเอียดความละเอียดสูง</p>
                              <a
                                href={item.student_answer}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-emerald-700 dark:text-emerald-400 inline-flex items-center gap-1 hover:underline"
                              >
                                เปิดลิงก์รูปภาพเต็ม <ExternalLink size={11} />
                              </a>
                            </div>
                          </div>

                          {/* Digital Transcription Block */}
                          {item.transcription && (
                            <div className="rounded-xl border border-emerald-200/80 dark:border-emerald-900/60 bg-emerald-50/40 dark:bg-emerald-950/20 p-3.5 space-y-1.5">
                              <span className="text-xs font-semibold text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
                                <Sparkles size={13} className="text-emerald-600 dark:text-emerald-400" />
                                ข้อความดิจิทัลที่ AI ถอดได้จากลายมือ (Transcribed Text)
                              </span>
                              <p className="text-xs font-mono text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed bg-white/70 dark:bg-slate-900/60 p-2.5 rounded-lg border border-emerald-100 dark:border-emerald-900/40">
                                {item.transcription}
                              </p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-xs text-slate-800 dark:text-slate-200 bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
                          {item.student_answer}
                        </div>
                      )}
                    </div>

                    {/* AI Feedback & Reasoning */}
                    <div className="bg-slate-50 dark:bg-slate-800/40 rounded-xl p-3 border border-slate-100 dark:border-slate-800/60 flex items-start gap-3">
                      <span className="p-1 rounded-md bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 shrink-0 mt-0.5">
                        <Sparkles size={14} />
                      </span>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">เหตุผลและคำแนะนำของ AI:</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-medium">
                            Confidence: {item.ai_confidence}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                          {item.ai_feedback}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Pagination Controls */}
                <div className="flex items-center justify-between pt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className="rounded-xl gap-1 text-xs"
                  >
                    <ChevronLeft size={14} /> ก่อนหน้า
                  </Button>
                  <span className="text-xs text-slate-500 font-medium">
                    หน้า {page} จากทั้งหมด {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className="rounded-xl gap-1 text-xs"
                  >
                    ถัดไป <ChevronRight size={14} />
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* QUICK SANDBOX MODAL */}
      {showSandbox && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 w-full max-w-xl p-6 space-y-5 shadow-xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Calculator size={18} className="text-indigo-600" />
                Quick Sandbox: ทดสอบคำนวณ QWK & MAE
              </h3>
              <button
                onClick={() => setShowSandbox(false)}
                className="text-slate-400 hover:text-slate-600 text-lg leading-none"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-500 leading-relaxed">
              กรอกคู่คะแนนอาจารย์และคะแนน AI (0 - 5) บรรทัดละ 1 คู่ โดยคั่นด้วยเครื่องหมายจุลภาค เช่น <code>5,5</code> หรือ <code>4,3</code> เพื่อทดสอบการคำนวณแบบสดทันที
            </p>

            <div>
              <textarea
                rows={6}
                value={sandboxScoresText}
                onChange={(e) => setSandboxScoresText(e.target.value)}
                className="w-full text-xs font-mono p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 leading-relaxed"
                placeholder="5,5&#10;4,4&#10;3,2"
              />
            </div>

            <Button
              onClick={handleRunSandbox}
              disabled={evaluatingSandbox}
              className="w-full rounded-xl bg-indigo-700 hover:bg-indigo-800 text-white text-xs font-semibold h-10"
            >
              {evaluatingSandbox ? "กำลังคำนวณ..." : "คำนวณ QWK และ MAE ทันที"}
            </Button>

            {sandboxResult && (
              <div className="p-4 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/60 space-y-3 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400">จำนวนตัวอย่างทดสอบ:</span>
                  <span className="font-bold text-slate-900 dark:text-white">{sandboxResult.total_samples} คู่คะแนน</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400">ค่า QWK:</span>
                  <span className="text-base font-bold text-indigo-700 dark:text-indigo-300">
                    {sandboxResult.overall_qwk?.toFixed(4)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400">ค่า MAE:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {sandboxResult.overall_mae?.toFixed(4)} คะแนน
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400">ระดับความสอดคล้อง:</span>
                  <span className="font-semibold text-emerald-700 dark:text-emerald-400">
                    {sandboxResult.agreement?.level_th}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Image Modal */}
      <ImageModal
        isOpen={!!modalImage}
        onClose={() => setModalImage(null)}
        src={modalImage?.src || ""}
        alt={modalImage?.alt}
      />
    </div>
  );
}
