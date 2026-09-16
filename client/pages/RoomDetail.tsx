import { WorkspaceBreadcrumb } from "@/components/WorkspaceHeader";
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Plus,
  FileText,
  Send,
  Loader2,
  ChevronRight,
  CheckCircle,
  Clock,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";

interface Exam {
  id: number | string;
  title: string;
  total_score: number;
  description?: string;
}

interface RoomInfo {
  id: number | string;
  name: string;
  section: string;
  class_code: string;
}

interface StudentSubmission {
  student_id: number;
  name: string;
  email: string;
  student_code?: string;
  submission_id?: number | null;
  status: string;
  total_score?: number | null;
  submitted_at?: string | null;
  graded_by_ai: boolean;
}

export default function RoomDetail() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user, token } = useAuth();

  const [room, setRoom] = useState<RoomInfo | null>(null);
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);

  // Teacher submissions per exam
  const [expandedExamId, setExpandedExamId] = useState<number | string | null>(
    null,
  );
  const [submissionsMap, setSubmissionsMap] = useState<{
    [examId: string]: StudentSubmission[];
  }>({});
  const [loadingSubmissions, setLoadingSubmissions] = useState(false);

  // Student's own submission status per exam
  const [mySubmissions, setMySubmissions] = useState<{ [examId: string]: any }>(
    {},
  );

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const headers = { Authorization: token ? `Bearer ${token}` : "" };

        // 1. Fetch Room Info
        const roomRes = await fetch(`/api/rooms/${roomId}`, { headers });
        if (roomRes.ok) {
          const roomData = await roomRes.json();
          setRoom(roomData);
        }

        // 2. Fetch Exams List
        const examsRes = await fetch(`/api/rooms/${roomId}/exams`, { headers });
        if (examsRes.ok) {
          const examsData: Exam[] = await examsRes.json();
          setExams(examsData);

          // If user is student, check status for each exam
          if (user?.role === "student") {
            const statusMap: { [examId: string]: any } = {};
            await Promise.all(
              examsData.map(async (ex) => {
                try {
                  const subRes = await fetch(
                    `/api/rooms/${roomId}/exams/${ex.id}/submissions/me`,
                    { headers },
                  );
                  if (subRes.ok) {
                    statusMap[ex.id.toString()] = await subRes.json();
                  }
                } catch {
                  // ignore
                }
              }),
            );
            setMySubmissions(statusMap);
          }
        }
      } catch (err) {
        console.error("Error fetching room detail:", err);
      } finally {
        setLoading(false);
      }
    };

    if (roomId) {
      fetchData();
    }
  }, [roomId, token, user?.role]);

  const loadSubmissionsForExam = async (examId: number | string) => {
    if (expandedExamId === examId) {
      setExpandedExamId(null);
      return;
    }

    setExpandedExamId(examId);
    setLoadingSubmissions(true);
    try {
      const res = await fetch(
        `/api/rooms/${roomId}/exams/${examId}/submissions`,
        {
          headers: { Authorization: token ? `Bearer ${token}` : "" },
        },
      );
      if (res.ok) {
        const list = await res.json();
        setSubmissionsMap((prev) => ({ ...prev, [examId.toString()]: list }));
      }
    } catch (err) {
      console.error("Error loading submissions:", err);
    } finally {
      setLoadingSubmissions(false);
    }
  };

  return (
    <div className="workspace">
      {/* Clean Top Navbar */}
      <header className="task-header border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#1E1E1E] px-8 py-3 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <button
            aria-label="กลับไปห้องเรียน"
            onClick={() => navigate("/home")}
            className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition p-1"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="task-header-title">
            <h1 className="font-bold text-base text-slate-900 dark:text-white">
              {room?.name || "กำลังโหลด..."}
            </h1>
            <p className="text-xs text-slate-400 font-mono">
              {room?.section ? `${room.section} • ` : ""}Code:{" "}
              {room?.class_code || "-"}
            </p>
          </div>
        </div>

        <div className="task-header-actions flex items-center gap-3">
          <ThemeToggle />

          {user?.role === "teacher" && (
            <Button
              onClick={() => navigate(`/room/${roomId}/create-exam`)}
              className="primary-action"
            >
              <Plus className="w-4 h-4 mr-1" /> สร้างข้อสอบ
            </Button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="document-page">
        <WorkspaceBreadcrumb current="รายการข้อสอบ" />
        <h2 className="page-heading">ข้อสอบในห้องเรียน</h2>
        <p className="page-description mb-8">
          {user?.role === "teacher"
            ? "เลือกข้อสอบเพื่อดูรายชื่อผู้เรียนและตรวจทานคำตอบ"
            : "เลือกข้อสอบที่ต้องการทำ หรือตรวจสอบสถานะการส่งคำตอบ"}
        </p>

        {loading ? (
          <div className="py-12 flex justify-center text-slate-400">
            <Loader2 className="w-6 h-6 animate-spin" />
          </div>
        ) : exams.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm bg-white dark:bg-[#1E1E1E] rounded-xl border border-slate-200 dark:border-slate-800 p-8">
            <FileText className="w-8 h-8 mx-auto mb-2 text-slate-300 dark:text-slate-600" />
            <p className="font-medium">ยังไม่มีแบบทดสอบในห้องเรียนนี้</p>
            {user?.role === "teacher" && (
              <p className="text-xs text-slate-400 mt-1">
                คลิกปุ่ม "+ สร้างข้อสอบใหม่" ด้านบนเพื่อเริ่มสร้างข้อสอบ
              </p>
            )}
          </div>
        ) : (
          /* Real Exams List */
          <div className="room-list">
            {exams.map((exam) => {
              const isExpanded = expandedExamId === exam.id;
              const submissions = submissionsMap[exam.id.toString()] || [];
              const studentStatus = mySubmissions[exam.id.toString()];

              return (
                <div
                  key={exam.id}
                  className="border-b border-slate-200 dark:border-slate-700 overflow-hidden"
                >
                  {/* Clickable Exam Card */}
                  <div
                    role="button"
                    tabIndex={0}
                    aria-expanded={
                      user?.role === "teacher" ? isExpanded : undefined
                    }
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        e.currentTarget.click();
                      }
                    }}
                    onClick={() => {
                      if (user?.role === "teacher") {
                        loadSubmissionsForExam(exam.id);
                      } else if (
                        studentStatus?.status !== "approved" &&
                        studentStatus?.status !== "submitted"
                      ) {
                        navigate(`/room/${roomId}/exam/${exam.id}/submit`);
                      }
                    }}
                    className={`exam-list-row p-5 flex items-center justify-between gap-4 select-none ${
                      user?.role === "teacher" ||
                      !studentStatus?.status ||
                      studentStatus?.status === "missing"
                        ? "cursor-pointer hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition"
                        : ""
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-slate-400 shrink-0">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                          {exam.title}
                        </h3>
                        <span className="text-xs text-slate-400 font-medium">
                          คะแนนเต็ม {exam.total_score} คะแนน
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {user?.role === "teacher" ? (
                        <>
                          <span className="text-sm text-slate-500">
                            {isExpanded ? "ซ่อนรายชื่อ" : "ตรวจคำตอบ"}
                          </span>
                          <ChevronRight
                            size={18}
                            className={`text-slate-400 dark:text-slate-500 transition-transform duration-200 ${
                              isExpanded ? "rotate-90" : ""
                            }`}
                          />
                        </>
                      ) : (
                        <div>
                          {studentStatus?.status === "approved" ? (
                            <span className="inline-flex items-center gap-1.5 text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 px-3 py-1.5 rounded-full border border-emerald-200">
                              <CheckCircle size={13} /> ตรวจเสร็จแล้ว (
                              {studentStatus.total_score} คะแนน)
                            </span>
                          ) : studentStatus?.status === "submitted" ? (
                            <span className="inline-flex items-center gap-1.5 text-xs font-semibold bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 px-3 py-1.5 rounded-full border border-blue-200">
                              <Clock size={13} /> ส่งแล้ว (รออาจารย์ตรวจ)
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-xs font-semibold bg-[#188038] text-white px-4 py-1.5 rounded-full shadow-sm">
                              <Send size={13} /> คลิกเพื่อทำข้อสอบ
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Teacher: Clickable Student Submissions Cards List */}
                  {user?.role === "teacher" && isExpanded && (
                    <div className="border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30 p-5 space-y-3">
                      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                        รายชื่อนิสิตที่ส่งข้อสอบ:
                      </h4>

                      {loadingSubmissions ? (
                        <div className="py-6 flex justify-center text-slate-400">
                          <Loader2 className="w-5 h-5 animate-spin" />
                        </div>
                      ) : submissions.length === 0 ? (
                        <p className="text-xs text-slate-400 py-3 text-center">
                          ยังไม่มีนิสิตส่งคำตอบในข้อสอบชุดนี้
                        </p>
                      ) : (
                        <div className="divide-y divide-slate-200 dark:divide-slate-700">
                          {submissions.map((sub) => {
                            const hasSubmitted =
                              sub.status !== "missing" && sub.submission_id;

                            return (
                              <div
                                key={sub.student_id}
                                role={hasSubmitted ? "button" : undefined}
                                tabIndex={hasSubmitted ? 0 : undefined}
                                onKeyDown={(e) => {
                                  if (
                                    hasSubmitted &&
                                    (e.key === "Enter" || e.key === " ")
                                  ) {
                                    e.preventDefault();
                                    e.currentTarget.click();
                                  }
                                }}
                                onClick={() => {
                                  if (hasSubmitted) {
                                    navigate(
                                      `/room/${roomId}/exam/${exam.id}/grading/${sub.student_id}`,
                                    );
                                  }
                                }}
                                className={`p-4 flex items-center justify-between gap-3 text-xs transition ${
                                  hasSubmitted
                                    ? "cursor-pointer hover:bg-slate-50/80 dark:hover:bg-slate-800/50"
                                    : "opacity-60"
                                }`}
                              >
                                <div>
                                  <span className="font-bold text-slate-900 dark:text-white block text-sm">
                                    {sub.name}{" "}
                                    {sub.student_code
                                      ? `(${sub.student_code})`
                                      : ""}
                                  </span>
                                  <span className="text-slate-400">
                                    {sub.email}
                                  </span>
                                </div>

                                <div className="flex items-center gap-2">
                                  {sub.status === "approved" ? (
                                    <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-3 py-1 rounded-full border border-emerald-200 flex items-center gap-1">
                                      <CheckCircle size={12} /> อนุมัติแล้ว:{" "}
                                      {sub.total_score} คะแนน
                                    </span>
                                  ) : sub.status === "submitted" ? (
                                    <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                                      <span>รอตรวจทาน</span>
                                      <ChevronRight
                                        size={15}
                                        className="text-slate-400"
                                      />
                                    </div>
                                  ) : (
                                    <span className="text-xs text-slate-400 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-full">
                                      ยังไม่ส่ง
                                    </span>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
