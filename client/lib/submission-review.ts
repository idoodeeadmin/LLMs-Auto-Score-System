export type SubmissionStatus = "missing" | "submitted" | "grading" | "ready" | "needs_review" | "approved";

export const submissionStatusLabel: Record<SubmissionStatus, string> = {
  missing: "ยังไม่ส่ง", submitted: "อยู่ในคิวตรวจ", grading: "AI กำลังตรวจ",
  ready: "พร้อมอนุมัติ", needs_review: "ต้องตรวจทาน", approved: "ประกาศผลแล้ว",
};

export const isPendingSubmission = (status: SubmissionStatus) =>
  ["submitted", "grading", "ready", "needs_review"].includes(status);

// The server may skip selected rows: only its confirmed IDs may change status.
export function applyApprovedIds<T extends { student_id: number; status: SubmissionStatus }>(
  rows: T[], approvedIds: number[],
): T[] {
  const confirmed = new Set(approvedIds);
  return rows.map(row => confirmed.has(row.student_id) ? { ...row, status: "approved" } : row);
}
