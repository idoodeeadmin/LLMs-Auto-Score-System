"""Separate instructor-only reasoning from feedback shown to students."""


def split_ai_feedback(feedback: str | None) -> tuple[str, str]:
    text = (feedback or "").strip()
    teacher_marker = "[สำหรับผู้สอน]"
    student_marker = "[สำหรับนักเรียน]"
    if student_marker in text:
        before, student = text.split(student_marker, 1)
        return before.replace(teacher_marker, "", 1).strip(), student.strip()
    # Unstructured legacy feedback cannot safely be classified as student-facing.
    return text.replace(teacher_marker, "", 1).strip(), ""


def feedback_for_student(saved_feedback: str | None, ai_feedback: str | None) -> str:
    return saved_feedback if saved_feedback is not None else split_ai_feedback(ai_feedback)[1]
