import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RUNS = [
    "q5-holistic-rubric-eval-20260923-164241",
    "q5-holistic-rubric-eval-20260923-164352",
    "q5-holistic-rubric-eval-20260923-164424",
    "q5-holistic-rubric-eval-20260923-164457",
    "q5-holistic-rubric-eval-20260923-164534",
    "q5-holistic-rubric-eval-20260923-164613",
    "q5-holistic-rubric-eval-20260923-164650",
    "q5-holistic-rubric-eval-20260923-164725",
    "q5-holistic-rubric-eval-20260923-164802",
]


def calculate_mae(y_true, y_pred):
    return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)


def calculate_qwk(y_true, y_pred, step=0.25, max_score=1.0):
    k = int(round(max_score / step)) + 1
    weights = [[((i - j) ** 2) / ((k - 1) ** 2) for j in range(k)] for i in range(k)]
    observed = [[0] * k for _ in range(k)]
    true_hist = [0] * k
    pred_hist = [0] * k
    for actual, predicted in zip(y_true, y_pred):
        actual_index = max(0, min(k - 1, int(round(actual / step))))
        predicted_index = max(0, min(k - 1, int(round(predicted / step))))
        observed[actual_index][predicted_index] += 1
        true_hist[actual_index] += 1
        pred_hist[predicted_index] += 1
    total = len(y_true)
    expected = [[(true_hist[i] * pred_hist[j]) / total for j in range(k)] for i in range(k)]
    numerator = sum(weights[i][j] * observed[i][j] for i in range(k) for j in range(k))
    denominator = sum(weights[i][j] * expected[i][j] for i in range(k) for j in range(k))
    return 1.0 if denominator == 0 and numerator == 0 else (0.0 if denominator == 0 else 1.0 - numerator / denominator)


def main():
    reports = [json.loads((ROOT / "artifacts" / run / "q5_holistic_rubric_all34_results.json").read_text(encoding="utf-8")) for run in RUNS]
    results = sorted((item for report in reports for item in report["results"]), key=lambda item: item["row"])
    assert len(results) == 34 and len({item["sample_id"] for item in results}) == 34

    truth = [item["human_score"] for item in results]
    predicted = [item["ai_score"] for item in results]
    exact = sum(item["ai_score"] == item["human_score"] for item in results)
    summary = {
        "total": len(results),
        "exact_count": exact,
        "exact_pct": round(exact / len(results) * 100, 2),
        "tolerance_0_25_count": sum(abs(item["diff"]) <= 0.25 for item in results),
        "tolerance_0_25_pct": round(sum(abs(item["diff"]) <= 0.25 for item in results) / len(results) * 100, 2),
        "tolerance_0_50_count": sum(abs(item["diff"]) <= 0.5 for item in results),
        "tolerance_0_50_pct": round(sum(abs(item["diff"]) <= 0.5 for item in results) / len(results) * 100, 2),
        "mae": round(calculate_mae(truth, predicted), 4),
        "qwk": round(calculate_qwk(truth, predicted, step=0.25, max_score=1.0), 4),
        "over_count": sum(item["ai_score"] > item["human_score"] for item in results),
        "under_count": sum(item["ai_score"] < item["human_score"] for item in results),
        "match_count": exact,
        "over_sum": round(sum(max(0, item["diff"]) for item in results), 2),
        "under_sum": round(sum(max(0, -item["diff"]) for item in results), 2),
        "ai_full_score_ids": [item["sample_id"] for item in results if item["ai_score"] == 1.0],
        "ai_zero_score_ids": [item["sample_id"] for item in results if item["ai_score"] == 0.0],
    }
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test": "Q5 partial-credit grading with answer-key image",
        "rule": "Four 0.25-point criteria, scored with text and image answer keys.",
        "source_runs": RUNS,
        "rubrics": reports[0]["rubrics"],
        "answer_key": reports[0]["answer_key"],
        "summary": summary,
        "results": results,
    }
    folder = ROOT / "artifacts" / "q5-partial-answer-key-image-all34-20260923-1648"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "q5_partial_answer_key_image_all34_results.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved: {path}")


if __name__ == "__main__":
    main()
