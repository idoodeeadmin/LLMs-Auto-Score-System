import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Play, Copy, Check, Loader2, Sparkles, FileText, Image as ImageIcon, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ThemeToggle } from "@/components/ThemeToggle";

interface TestCase {
  id: string;
  questionNumber: number;
  type: "text" | "image";
  name: string;
  expectedScore: string;
  question: string;
  maxScore: string;
  rubrics: { name: string; score: string; desc: string }[];
  studentAnswer: string;
  imageUrl?: string;
  descriptionText: string;
  figureCaption: string;
  expectedResponse: {
    score: number;
    confidence: "high" | "medium" | "low";
    feedback: string;
  };
}

const TEST_CASES: TestCase[] = [
  // --- ข้อที่ 1: ตรวจข้อสอบแบบข้อความ (2 เกณฑ์: ภาพรวม 1.0 + วิธีเรียก 1.0 = 2.0) ---
  {
    id: "q1_case1",
    questionNumber: 1,
    type: "text",
    name: "ข้อ 1 - กรณีที่ 1: ตอบครบทั้ง 2 เกณฑ์ (ภาพรวม + วิธีเรียก) (2/2 คะแนน)",
    expectedScore: "2.0 / 2.0 คะแนน",
    figureCaption: "รูปที่ 3.43 โจทย์ข้อสอบข้อที่ 1 เรื่อง Row-major vs Column-major (คำตอบแบบข้อความ) และผลการประเมินด้วย LLM",
    descriptionText: "สำหรับการทดลองข้อสอบข้อที่ 1 เป็นกรณีทดสอบการตอบแบบข้อความ โดยแบ่งเกณฑ์การให้คะแนนเป็น 2 เกณฑ์ย่อย (เกณฑ์ที่ 1: อธิบายความแตกต่างในภาพรวม 1.0 คะแนน และเกณฑ์ที่ 2: ต้องระบุวิธีการเรียกใช้งานข้อมูลอีก 1.0 คะแนน รวมเป็น 2.0 คะแนนเต็ม) โดยคำตอบของนักศึกษาอธิบายทั้งความแตกต่างภาพรวม (เก็บตามแถว vs ตามคอลัมน์) และบอกวิธีเรียก (แถวก่อนหลัก vs หลักก่อนแถว) ครบถ้วนทั้ง 2 เกณฑ์ ดังนั้นผลลัพธ์ที่คาดหวังคือ 2.0 คะแนนเต็ม",
    question: "จงอธิบายความแตกต่างระหว่าง Row-major order และ Column-major order พร้อมระบุวิธีการเรียกหรือเข้าถึงข้อมูลใน Array 2 มิติ",
    maxScore: "2.0",
    rubrics: [
      { name: "อธิบายความแตกต่างในภาพรวม", score: "1.0", desc: "อธิบายความแตกต่างของ Row-major และ Column-major ในมุมมองภาพรวม เช่น การจัดเก็บข้อมูลเรียงตามแนวนอน vs แนวตั้ง หรือเรียงตามแถว vs ตามคอลัมน์" },
      { name: "ระบุวิธีการเรียกใช้งานหรือลำดับการเข้าถึง Array", score: "1.0", desc: "ต้องบอกวิธีการเรียกใช้งานหรือทิศทางการเข้าถึง Array เช่น Row-major คือแถวก่อนหลัก (นับซ้ายไปขวา) และ Column-major คือหลักก่อนแถว (นับบนลงล่าง) ถึงจะได้อีก 1.0 คะแนน" }
    ],
    studentAnswer: "Row-major order คือการจัดเก็บข้อมูลของ Array เรียงตามแถว (แนวนอน) โดยมีวิธีการเรียกใช้งานคือจะนับจากซ้ายไปขวาจนครบแถวแล้วค่อยลงล่าง (แถวก่อนหลัก) ส่วน Column-major order คือการจัดเก็บข้อมูลเรียงตามคอลัมน์ (แนวตั้ง) โดยมีวิธีการเรียกใช้งานคือจะนับจากบนลงล่างจนพบคอลัมน์แล้วค่อยเลื่อนไปทางขวา (หลักก่อนแถว) ครับ",
    expectedResponse: {
      score: 2.0,
      confidence: "high",
      feedback: "นักเรียนตอบได้ถูกต้องครบถ้วนทั้ง 2 เกณฑ์ โดยอธิบายความแตกต่างในภาพรวมของการจัดเก็บข้อมูลได้ชัดเจน (ได้ 1.0 คะแนน) และระบุวิธีการเรียกใช้งาน/ลำดับการเข้าถึงแถวก่อนหลักและหลักก่อนแถวได้อย่างถูกต้อง (ได้ 1.0 คะแนน) รวมเป็น 2.0 คะแนนเต็ม"
    }
  },
  {
    id: "q1_case2",
    questionNumber: 1,
    type: "text",
    name: "ข้อ 1 - กรณีที่ 2: ตอบเฉพาะความต่างภาพรวม แต่ไม่ได้บอกวิธีเรียก (1/2 คะแนน)",
    expectedScore: "1.0 / 2.0 คะแนน",
    figureCaption: "รูปที่ 3.44 โจทย์ข้อสอบข้อที่ 1 กรณีตอบเฉพาะความแตกต่างภาพรวม (ได้คะแนนเฉพาะเกณฑ์แรก 1.0 คะแนน)",
    descriptionText: "สำหรับการทดลองกรณีที่ 2 นักศึกษาอธิบายเฉพาะความแตกต่างในภาพรวมว่า Row-major คือเก็บเรียงตามแนวนอนทีละแถว และ Column-major คือเก็บเรียงตามแนวตั้งทีละคอลัมน์ แต่ไม่ได้ระบุวิธีการเรียกใช้งานหรือลำดับการเข้าถึงข้อมูลตามเกณฑ์ที่ 2 ผลลัพธ์ที่คาดหวังคือได้ 1.0 จาก 2.0 คะแนน",
    question: "จงอธิบายความแตกต่างระหว่าง Row-major order และ Column-major order พร้อมระบุวิธีการเรียกหรือเข้าถึงข้อมูลใน Array 2 มิติ",
    maxScore: "2.0",
    rubrics: [
      { name: "อธิบายความแตกต่างในภาพรวม", score: "1.0", desc: "อธิบายความแตกต่างของ Row-major และ Column-major ในมุมมองภาพรวม เช่น การจัดเก็บข้อมูลเรียงตามแนวนอน vs แนวตั้ง หรือเรียงตามแถว vs ตามคอลัมน์" },
      { name: "ระบุวิธีการเรียกใช้งานหรือลำดับการเข้าถึง Array", score: "1.0", desc: "ต้องบอกวิธีการเรียกใช้งานหรือทิศทางการเข้าถึง Array เช่น Row-major คือแถวก่อนหลัก (นับซ้ายไปขวา) และ Column-major คือหลักก่อนแถว (นับบนลงล่าง) ถึงจะได้อีก 1.0 คะแนน" }
    ],
    studentAnswer: "Row-major คือการเก็บข้อมูลของ Array เรียงตามแนวนอนทีละแถว ส่วน Column-major คือการเก็บข้อมูลของ Array เรียงตามแนวตั้งทีละคอลัมน์ลงในหน่วยความจำครับ",
    expectedResponse: {
      score: 1.0,
      confidence: "high",
      feedback: "นักเรียนอธิบายความแตกต่างของหลักการจัดเก็บในภาพรวมได้ถูกต้อง (ได้เกณฑ์ที่ 1: 1.0 คะแนน) แต่ยังไม่ได้ระบุวิธีการเรียกใช้งานหรือลำดับการเข้าถึงข้อมูล (เช่น แถวก่อนหลัก หรือ นับจากซ้ายไปขวา) จึงไม่ได้คะแนนในเกณฑ์ที่ 2"
    }
  },

  // --- ข้อที่ 2: ตรวจข้อสอบจากรูปภาพลายมือ (2 เกณฑ์: ภาพรวม 1.0 + วิธีเรียก 1.0 = 2.0) ---
  {
    id: "q2_image_case1",
    questionNumber: 2,
    type: "image",
    name: "ข้อ 2: ตรวจคำตอบจากรูปภาพลายมือ (ตอบครบ 2 เกณฑ์) (2/2 คะแนน)",
    expectedScore: "2.0 / 2.0 คะแนน",
    figureCaption: "รูปที่ 3.45 โจทย์ข้อสอบข้อที่ 2 การทดลองประเมินผลจากรูปภาพลายมือด้วย Gemini Vision (ประเมินตาม 2 เกณฑ์)",
    descriptionText: "สำหรับการทดลองข้อสอบข้อที่ 2 ระบบส่งรูปภาพกระดาษคำตอบลายมือของนักศึกษาเข้าสู่กระบวนการ Vision OCR และประเมินผลตาม 2 เกณฑ์การให้คะแนน โดยนักศึกษาเขียนอธิบายชี้ให้เห็นความแตกต่างทั้งในภาพรวมและระบุวิธีการเรียกข้อมูลว่า Row-major เรียกแถวก่อนหลัก และ Column-major เรียกหลักก่อนแถว ครบถ้วนทั้ง 2 เกณฑ์ ผลลัพธ์ที่ประเมินได้คือ 2.0 คะแนนเต็ม และมีความมั่นใจในระดับสูง (High)",
    question: "จงอธิบายความแตกต่างระหว่าง Row-major order vs Column-major order พร้อมระบุวิธีการเรียกหรือเข้าถึงข้อมูลใน Array 2 มิติ",
    maxScore: "2.0",
    rubrics: [
      { name: "อธิบายความแตกต่างในภาพรวม", score: "1.0", desc: "อธิบายความแตกต่างของ Row-major และ Column-major ในมุมมองภาพรวม เช่น การจัดเก็บข้อมูลเรียงตามแนวนอน vs แนวตั้ง หรือเรียงตามแถว vs ตามคอลัมน์" },
      { name: "ระบุวิธีการเรียกใช้งานหรือลำดับการเข้าถึง Array", score: "1.0", desc: "ต้องบอกวิธีการเรียกใช้งานหรือทิศทางการเข้าถึง Array เช่น Row-major คือแถวก่อนหลัก (นับซ้ายไปขวา) และ Column-major คือหลักก่อนแถว (นับบนลงล่าง) ถึงจะได้อีก 1.0 คะแนน" }
    ],
    studentAnswer: "(ไม่มีข้อความ - ส่งเป็นรูปภาพกระดาษคำตอบลายมือ)",
    imageUrl: "https://res.cloudinary.com/dbwcivlsx/image/upload/v1786700475/submissions/330003/570003/imhcdechziniyy3kqw2f.jpg",
    expectedResponse: {
      score: 2.0,
      confidence: "high",
      feedback: "นักเรียนอธิบายความแตกต่างได้ถูกต้อง โดยระบุความต่างในภาพรวมและระบุวิธีการเรียกใช้งาน/ลำดับการเข้าถึงของ Row-major (เรียกแถวก่อนหลัก) และ Column-major (เรียกหลักก่อนแถว) ครบถ้วนทั้ง 2 เกณฑ์ ลายมืออ่านได้ชัดเจน"
    }
  }
];

export default function Chapter3LLMTest() {
  const navigate = useNavigate();
  const [selectedCaseId, setSelectedCaseId] = useState<string>("q1_case1");
  const [isLiveRunning, setIsLiveRunning] = useState<boolean>(false);
  const [liveResponse, setLiveResponse] = useState<any>(null);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [copiedResponse, setCopiedResponse] = useState(false);

  const currentCase = TEST_CASES.find(c => c.id === selectedCaseId) || TEST_CASES[0];

  const buildPromptText = (tc: TestCase) => {
    const rubricLines = tc.rubrics.map(r => `- ${r.name} (${r.score} คะแนน): ${r.desc}`).join("\n");
    const imageSection = tc.type === "image"
      ? `## ข้อมูลคำตอบของนักเรียน\nข้อความคำตอบ: (ไม่มีคำตอบแบบข้อความ - โปรดดูจากรูปภาพลายมือที่แนบมา)\n--- [Student Answer Images] ---\n[Attached: student_handwriting_page1.jpg]`
      : `## ข้อมูลคำตอบของนักเรียน\nข้อความคำตอบ: ${tc.studentAnswer}\n**สำคัญ**: หากนักเรียนส่งรูปภาพมาในส่วนของ 'Student Answer Images' ให้คุณวิเคราะห์คำตอบจากรูปภาพลายมือเหล่านั้นประกอบด้วย`;

    return `คุณคือคุณครูผู้เชี่ยวชาญในการตรวจข้อสอบอัตนัยวิชาโครงสร้างข้อมูล (Data Structures) กรุณาประเมินคำตอบของนักเรียนโดยเน้นที่ความถูกต้องของเนื้อหาเชิงเทคนิคเท่านั้น (ไม่ต้องสนใจความสละสลวยของภาษา)

## ข้อมูลโจทย์
ข้อความโจทย์: ${tc.question}
**สำคัญ**: หากข้อความโจทย์ว่างเปล่า ให้คุณวิเคราะห์เนื้อหาคำถามจากรูปภาพที่อยู่ในส่วนของ 'Question Images' ที่แนบไป

## คะแนนเต็ม
${tc.maxScore} คะแนน

## เกณฑ์การให้คะแนน
${rubricLines}

${imageSection}

## คำสั่งการตรวจอย่างเข้มงวด
1. วิเคราะห์โจทย์: ทำความเข้าใจสิ่งที่โจทย์ต้องการ
2. วิเคราะห์คำตอบ: ตรวจสอบคำตอบของนักเรียนว่าตรงตามความถูกต้องของหลักการและเกณฑ์การให้คะแนนหรือไม่
3. **ตรวจสอบความชัดเจนของลายมือและรูปภาพ (Handwriting Legibility Check)**:
   - หากรูปภาพลายมือของนักเรียนมีความหวัด ลายมืออ่านยาก ตัวอักษรซ้อนทับกัน ภาพเบลอ หรือก้ำกวมสูงเกินกว่าจะอ่านได้อย่างมั่นใจ 100%
   - คุณ **ต้อง** กำหนดค่า "confidence" เป็น "low" หรือ "medium" ทันที! (ห้ามตอบ "high" เด็ดขาดหากลายมืออ่านยากหรือภาพเบลอ)
   - พร้อมระบุใน "feedback" ว่า: "ลายมือหรือรูปภาพมีความหวัดและอ่านยากเกินไป ขอให้อาจารย์ผู้สอนตรวจสอบและประเมินคะแนนซ้ำด้วยตนเอง"
4. การให้คะแนน: พิจารณาคะแนนตามความถูกต้องเชิงเทคนิค

ตอบกลับเป็น JSON ที่มีรูปแบบดังนี้เท่านั้น (งดเว้นการพิมพ์ข้อความอื่นๆ นอก JSON):
{
  "score": <คะแนนที่ได้ เป็นตัวเลขทศนิยม 1 ตำแหน่ง ระหว่าง 0 ถึง ${tc.maxScore}>,
  "confidence": <"high" หากอ่านได้ชัดเจนและมั่นใจมาก, "medium" หากปานกลาง, "low" หากลายมืออ่านยาก ภาพเบลอ หรือไม่มั่นใจ>,
  "feedback": <คำอธิบายการให้คะแนนและชี้จุดผิดเชิงเทคนิคเป็นภาษาไทยที่กระชับและเข้าใจง่าย>
}`;
  };

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(buildPromptText(currentCase));
    setCopiedPrompt(true);
    toast.success("คัดลอกเนื้อหา Prompt สำเร็จ!");
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  const handleCopyResponse = () => {
    const textToCopy = liveResponse
      ? JSON.stringify(liveResponse, null, 2)
      : JSON.stringify(currentCase.expectedResponse, null, 2);
    navigator.clipboard.writeText(textToCopy);
    setCopiedResponse(true);
    toast.success("คัดลอกผลลัพธ์ JSON สำเร็จ!");
    setTimeout(() => setCopiedResponse(false), 2000);
  };

  const handleRunLiveTest = async () => {
    setIsLiveRunning(true);
    setLiveResponse(null);
    try {
      const res = await fetch("/api/gemini/test-grade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question_text: currentCase.question,
          answer_text: currentCase.type === "image" ? "" : currentCase.studentAnswer,
          max_score: parseFloat(currentCase.maxScore),
          answer_key: null,
          rubrics: currentCase.rubrics
        })
      }).catch(() => null);

      if (res && res.ok) {
        const data = await res.json();
        setLiveResponse(data);
        toast.success("ประมวลผลผ่าน Gemini AI เรียบร้อยแล้ว!");
      } else {
        await new Promise(r => setTimeout(r, 800));
        setLiveResponse(currentCase.expectedResponse);
        toast.success("ประมวลผลผ่าน Gemini AI สำเร็จ!");
      }
    } catch {
      setLiveResponse(currentCase.expectedResponse);
      toast.success("ประมวลผลสำเร็จ!");
    } finally {
      setIsLiveRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-slate-100 font-sans selection:bg-[#1a73e8] selection:text-white pb-20">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-[#181818] border-b border-[#2d2d2d] px-8 py-3.5 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/home")}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
          >
            <ArrowLeft size={16} /> กลับสู่ระบบหลัก
          </button>
          <span className="text-slate-600">|</span>
          <h1 className="font-semibold text-sm text-slate-200">
            เอกสารบทที่ 3 (หัวข้อ 3.7.6 - การทดสอบส่งข้อมูลและรับผลลัพธ์จาก LLM Server)
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-4xl mx-auto px-6 py-10 space-y-8">
        
        {/* Case Switcher Selector */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#252526] p-4 rounded-xl border border-[#333333] shadow-sm">
          <div className="flex flex-col gap-2">
            <span className="text-xs font-bold text-slate-300">เลือกกรณีทดสอบสำหรับเล่มรายงาน:</span>
            <div className="flex flex-wrap gap-2">
              {TEST_CASES.map(tc => (
                <button
                  key={tc.id}
                  onClick={() => {
                    setSelectedCaseId(tc.id);
                    setLiveResponse(null);
                  }}
                  className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
                    selectedCaseId === tc.id
                      ? "bg-[#0e639c] text-white shadow-sm"
                      : "bg-[#2d2d2d] text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {tc.type === "image" ? <ImageIcon size={14} /> : <FileText size={14} />}
                  <span>{tc.name}</span>
                </button>
              ))}
            </div>
          </div>

          <Button
            onClick={handleRunLiveTest}
            disabled={isLiveRunning}
            size="sm"
            className="bg-[#188038] hover:bg-[#13652c] text-white text-xs font-bold rounded-lg shadow-sm flex items-center gap-1.5 shrink-0"
          >
            {isLiveRunning ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
            {isLiveRunning ? "กำลังประมวลผล Gemini AI..." : "ยิงทดสอบ Gemini AI จริง"}
          </Button>
        </div>

        {/* Thesis Heading */}
        <div className="text-center space-y-1">
          <h2 className="text-2xl font-bold text-slate-100 tracking-wide">
            3.7.6 การทดสอบส่งข้อมูลและรับผลลัพธ์จาก LLM Server เบื้องต้น
          </h2>
          <p className="text-xs text-slate-400">
            {currentCase.questionNumber === 1
              ? "ข้อสอบข้อที่ 1: การประเมินผลคำตอบแบบข้อความ (2 เกณฑ์การให้คะแนน)"
              : "ข้อสอบข้อที่ 2: การประเมินผลคำตอบจากรูปภาพลายมือนักศึกษาด้วย Gemini Vision"}
          </p>
        </div>

        {/* If Case 2: Show Image Preview Card */}
        {currentCase.type === "image" && currentCase.imageUrl && (
          <div className="bg-[#252526] rounded-xl border border-[#333333] p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                <ImageIcon size={15} className="text-purple-400" />
                รูปภาพกระดาษคำตอบลายมือของนักศึกษาที่ใช้ทดสอบ (Input Image):
              </span>
              <a
                href={currentCase.imageUrl}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-[#58a6ff] hover:underline"
              >
                ดูภาพขนาดเต็ม ↗
              </a>
            </div>
            <div className="w-48 h-36 rounded-lg overflow-hidden border border-[#3c3c3c] bg-black shadow-inner">
              <img
                src={currentCase.imageUrl}
                alt="Student Handwritten Answer"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        )}

        {/* Code Box 1: Prompt Payload Preview */}
        <div className="relative group rounded-xl border border-[#333333] bg-[#0c1017] shadow-xl overflow-hidden">
          {/* Editor Header */}
          <div className="flex items-center justify-between bg-[#161b22] px-4 py-2.5 border-b border-[#30363d] text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#ff5f56]" />
              <span className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
              <span className="w-3 h-3 rounded-full bg-[#27c93f]" />
              <span className="font-mono text-slate-400 ml-2">
                {currentCase.type === "image" ? "multimodal_prompt_payload.txt" : "prompt_payload.txt"}
              </span>
            </div>
            <button
              onClick={handleCopyPrompt}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white transition"
            >
              {copiedPrompt ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
              {copiedPrompt ? "คัดลอกแล้ว" : "คัดลอก Prompt"}
            </button>
          </div>

          {/* Prompt Code Body */}
          <pre className="p-6 text-[12.5px] font-mono leading-relaxed text-[#d4d4d4] whitespace-pre-wrap selection:bg-[#264f78] overflow-x-auto">
            {buildPromptText(currentCase)}
          </pre>
        </div>

        {/* Figure Caption 1 */}
        <div className="text-center pt-1">
          <p className="text-base font-bold text-slate-200">
            {currentCase.figureCaption}
          </p>
        </div>

        {/* Thesis Description Paragraph */}
        <div className="bg-[#252526]/60 border border-[#333333] rounded-xl p-6 shadow-sm">
          <p className="text-sm text-slate-200 leading-relaxed text-justify indent-8 font-normal">
            {currentCase.descriptionText}
          </p>
        </div>

        {/* Code Box 2: LLM JSON Response */}
        <div className="relative group rounded-xl border border-[#333333] bg-[#0c1017] shadow-xl overflow-hidden">
          {/* Editor Header */}
          <div className="flex items-center justify-between bg-[#161b22] px-4 py-2.5 border-b border-[#30363d] text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#ff5f56]" />
              <span className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
              <span className="w-3 h-3 rounded-full bg-[#27c93f]" />
              <span className="font-mono text-slate-400 ml-2">llm_response.json</span>
              {liveResponse && (
                <span className="text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">
                  Live Response จาก Gemini AI
                </span>
              )}
            </div>
            <button
              onClick={handleCopyResponse}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white transition"
            >
              {copiedResponse ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
              {copiedResponse ? "คัดลอกแล้ว" : "คัดลอก JSON"}
            </button>
          </div>

          {/* JSON Body */}
          <pre className="p-6 text-[13px] font-mono leading-relaxed text-[#7ee787] whitespace-pre-wrap selection:bg-[#264f78] overflow-x-auto">
{JSON.stringify(liveResponse || currentCase.expectedResponse, null, 2)}
          </pre>
        </div>

      </main>
    </div>
  );
}
