import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.services.benchmark_service import (
    calculate_qwk,
    calculate_mae,
    calculate_confusion_matrix,
    get_agreement_interpretation,
    compute_benchmark_metrics,
    export_benchmark_excel,
    CANONICAL_QUESTIONS
)

@pytest.fixture
def client():
    return TestClient(app)

def test_calculate_qwk_identical():
    # If predictions match perfectly, QWK must be 1.0
    y_true = [5, 4, 3, 2, 1, 0]
    y_pred = [5, 4, 3, 2, 1, 0]
    assert calculate_qwk(y_true, y_pred) == 1.0

def test_calculate_qwk_high_agreement():
    y_true = [5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0]
    y_pred = [5, 4, 4, 4, 3, 2, 2, 2, 1, 1, 0, 1]
    qwk = calculate_qwk(y_true, y_pred)
    assert qwk > 0.85

def test_calculate_mae():
    y_true = [5, 4, 3, 2, 1]
    y_pred = [4, 4, 2, 2, 0]
    mae = calculate_mae(y_true, y_pred)
    # diffs: 1 + 0 + 1 + 0 + 1 = 3 / 5 = 0.6
    assert mae == 0.6

def test_calculate_confusion_matrix():
    y_true = [0, 1, 2, 3, 4, 5]
    y_pred = [0, 1, 2, 3, 4, 5]
    cm = calculate_confusion_matrix(y_true, y_pred)
    assert len(cm["labels"]) == 6
    assert len(cm["matrix"]) == 6
    for i in range(6):
        assert cm["matrix"][i][i] == 1

def test_agreement_interpretation():
    almost_perfect = get_agreement_interpretation(0.92)
    assert almost_perfect["level_en"] == "Almost Perfect"
    assert almost_perfect["badge_color"] == "emerald"

    moderate = get_agreement_interpretation(0.55)
    assert moderate["level_en"] == "Moderate"

def test_canonical_questions():
    assert len(CANONICAL_QUESTIONS) == 10
    for idx, q in enumerate(CANONICAL_QUESTIONS, 1):
        assert q["question_no"] == idx
        assert q["max_score"] == 5
        assert q["type"] in ["text", "img"]

def test_benchmark_summary_api(client):
    res = client.get("/api/benchmark/summary")
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["total_samples"] == 300
    assert data["overall_qwk"] > 0.85
    assert data["overall_mae"] < 0.40
    assert "modality_comparison" in data
    assert data["modality_comparison"]["text"]["count"] == 150
    assert data["modality_comparison"]["image"]["count"] == 150
    assert len(data["per_question"]) == 10

def test_benchmark_dataset_api(client):
    # Test getting dataset
    res = client.get("/api/benchmark/dataset?limit=10")
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["total"] == 300
    assert len(payload["items"]) == 10

    # Test filtering by question_no
    res_q1 = client.get("/api/benchmark/dataset?question_no=1&limit=50")
    assert res_q1.status_code == 200
    items_q1 = res_q1.json()["items"]
    assert all(it["question_no"] == 1 for it in items_q1)

    # Test filtering by answer_type
    res_img = client.get("/api/benchmark/dataset?answer_type=img&limit=200")
    assert res_img.status_code == 200
    items_img = res_img.json()["items"]
    assert all(it["answer_type"] == "img" for it in items_img)

def test_benchmark_evaluate_custom_api(client):
    body = {
        "items": [
            {"human_score": 5, "ai_score": 5},
            {"human_score": 4, "ai_score": 4},
            {"human_score": 3, "ai_score": 2},
            {"human_score": 2, "ai_score": 2},
            {"human_score": 1, "ai_score": 1}
        ]
    }
    res = client.post("/api/benchmark/evaluate", json=body)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total_samples"] == 5
    assert data["overall_qwk"] > 0.80

def test_benchmark_export_excel(client):
    res = client.get("/api/benchmark/export")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(res.content) > 1000
