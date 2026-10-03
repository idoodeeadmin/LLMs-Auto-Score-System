"""Confidence threshold for sending AI-graded answers to teacher review."""


def requires_review_for_confidence(confidence: str | None) -> bool:
    return str(confidence or "").lower() in {"medium", "low"}


def submission_requires_review(confidences: list[str | None]) -> bool:
    return not confidences or any(requires_review_for_confidence(value) for value in confidences)
