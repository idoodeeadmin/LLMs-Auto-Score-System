"""Derive enforceable total score steps from explicit per-criterion rubric levels."""

import re
from decimal import Decimal, InvalidOperation


_SCORE_LABEL = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*คะแนน")


def allowed_total_scores(rubrics: list[dict] | None, max_score: float) -> list[float] | None:
    """Return possible sums only when every criterion explicitly lists 0 and its maximum.

    Free-form rubrics without complete levels remain unrestricted, avoiding an invented
    score scale that could discard legitimate partial credit.
    """
    if not rubrics:
        return None
    try:
        total_max = Decimal(str(max_score))
        criteria = []
        for rubric in rubrics:
            criterion_max = Decimal(str(rubric["score"]))
            if criterion_max <= 0:
                return None
            explicit = rubric.get("allowed_scores")
            if explicit is not None:
                levels = {Decimal(str(value)) for value in explicit}
            else:
                levels = {Decimal(value) for value in _SCORE_LABEL.findall(rubric.get("description") or "")}
            if Decimal(0) not in levels or criterion_max not in levels:
                return None
            if any(value < 0 or value > criterion_max for value in levels):
                return None
            criteria.append((criterion_max, levels))
        if sum((maximum for maximum, _ in criteria), Decimal(0)) != total_max:
            return None
        sums = {Decimal(0)}
        for _, levels in criteria:
            sums = {subtotal + level for subtotal in sums for level in levels}
        return [float(value) for value in sorted(sums)]
    except (KeyError, TypeError, ValueError, InvalidOperation):
        return None
