import { describe, expect, it } from "vitest";
import { applyApprovedIds, isPendingSubmission, type SubmissionStatus } from "./submission-review";

describe("review state", () => {
  it("keeps queued and grading work visible in pending", () => {
    const statuses: SubmissionStatus[] = ["missing", "submitted", "grading", "ready", "needs_review", "approved"];
    expect(statuses.filter(isPendingSubmission)).toEqual(["submitted", "grading", "ready", "needs_review"]);
  });
  it("does not publish skipped or unconfirmed rows", () => {
    const rows = [{ student_id: 1, status: "ready" as const }, { student_id: 2, status: "needs_review" as const }, { student_id: 3, status: "ready" as const }];
    expect(applyApprovedIds(rows, [1]).map(row => row.status)).toEqual(["approved", "needs_review", "ready"]);
    expect(rows[0].status).toBe("ready");
    expect(applyApprovedIds(rows, [])).toEqual(rows);
  });
});
