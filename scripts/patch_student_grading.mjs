import fs from 'fs';
import path from 'path';

const file = path.resolve('client/pages/StudentGrading.tsx');
let content = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');

// Target 1: Insert handleApprove, totalTeacherScore, and renderConfidenceBadge header
const marker1 = '  useEffect(() => {\n    if (!hasUnsavedChanges) return;\n    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ""; };\n    window.addEventListener("beforeunload", warn);\n    return () => window.removeEventListener("beforeunload", warn);\n  }, [hasUnsavedChanges]);';

const replacement1 = `${marker1}

  const hasNext = queueIndex >= 0 && queueIndex < reviewQueue.length - 1;
  const nextStudent = hasNext ? reviewQueue[queueIndex + 1] : null;

  const handleApprove = async (e?: React.FormEvent, andNext = false) => {
    if (e) e.preventDefault();
    if (!data) return;

    setIsApproving(true);
    try {
      const res = await fetch(
        \`/api/rooms/\${roomId}/exams/\${examId}/submissions/\${studentId}/approve\`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? \`Bearer \${token}\` : "",
          },
          body: JSON.stringify({
            teacher_scores: teacherScores,
            teacher_comments: teacherComments,
          }),
        },
      );

      if (res.ok) {
        toast.success("อนุมัติและประกาศผลคะแนนเรียบร้อยแล้ว!");
        if (andNext && nextStudent) {
          navigate(\`/room/\${roomId}/exam/\${examId}/grading/\${nextStudent.student_id}\`);
        } else {
          navigate(\`/room/\${roomId}/exam/\${examId}/review\`);
        }
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || "เกิดข้อผิดพลาดในการอนุมัติคะแนน");
      }
    } catch {
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อ");
    } finally {
      setIsApproving(false);
    }
  };

  const totalTeacherScore = Object.values(teacherScores).reduce(
    (sum, s) => sum + (Number(s) || 0),
    0,
  );
  const totalMaxScore =
    data?.answers.reduce((sum, a) => sum + (Number(a.max_score) || 0), 0) || 0;

  const renderConfidenceBadge = (confidence?: string) => {
    const conf = confidence?.toLowerCase();`;

if (!content.includes(marker1)) {
  console.error("Marker 1 not found!");
  process.exit(1);
}

content = content.replace(
  `${marker1}\n    if (conf === "high") {`,
  `${replacement1}\n    if (conf === "high") {`
);

// Target 2: Bottom action buttons
const marker2 = `            {/* Submit Approval Button */}
            <Button
              type="submit"
              disabled={isApproving}
              className="primary-action w-full mt-6"
            >
              {isApproving ? (
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <Check className="w-5 h-5 mr-2" />
              )}
              {isApproving
                ? "กำลังบันทึกคะแนน..."
                : \`อนุมัติและประกาศผลคะแนนสุทธิ (\${totalTeacherScore.toFixed(1)} / \${totalMaxScore} คะแนน)\`}
            </Button>`;

const replacement2 = `            {/* Submit Approval Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-3 mt-8 pt-4 border-t border-slate-200 dark:border-slate-800">
              <Button
                type="button"
                variant="outline"
                disabled={isApproving}
                onClick={(e) => handleApprove(e, false)}
                className="w-full sm:w-auto flex-1 h-11 text-xs font-medium border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-xl"
              >
                <Check className="w-4 h-4 mr-2 text-emerald-600 dark:text-emerald-400" />
                อนุมัติและกลับหน้ารวมตรวจงาน
              </Button>

              {hasNext ? (
                <Button
                  type="button"
                  disabled={isApproving}
                  onClick={(e) => handleApprove(e, true)}
                  className="w-full sm:w-auto flex-1 h-11 text-xs font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm"
                >
                  {isApproving ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Check className="w-4 h-4 mr-2" />
                  )}
                  อนุมัติและตรวจคนถัดไป ({nextStudent?.name?.slice(0, 12)}…) →
                </Button>
              ) : (
                <Button
                  type="submit"
                  disabled={isApproving}
                  className="primary-action w-full sm:w-auto flex-1 h-11 text-xs font-medium"
                >
                  {isApproving ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Check className="w-4 h-4 mr-2" />
                  )}
                  {isApproving
                    ? "กำลังบันทึกคะแนน..."
                    : \`อนุมัติและประกาศผลคะแนนสุทธิ (\${totalTeacherScore.toFixed(1)} / \${totalMaxScore} คะแนน)\`}
                </Button>
              )}
            </div>`;

if (!content.includes(marker2)) {
  console.error("Marker 2 not found!");
  process.exit(1);
}

content = content.replace(marker2, replacement2);

fs.writeFileSync(file, content, 'utf8');
console.log("Successfully patched StudentGrading.tsx!");
