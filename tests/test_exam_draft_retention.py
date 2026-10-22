import json
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from server.main import app
from server.utils import get_current_user


def test_publishing_exam_keeps_saved_draft():
    app.dependency_overrides[get_current_user] = lambda: {"id": 7, "role": "teacher"}
    conn = MagicMock()
    cursor = conn.cursor.return_value
    cursor.lastrowid = 42
    cursor.fetchone.side_effect = [
        {"id": 3},
        {"questions": json.dumps([{"question_images_base64": [], "answer_key_images_base64": []}])},
        {"id": 42, "title": "Demo"},
    ]
    cursor.fetchall.return_value = []
    try:
        with patch("server.routes.exam_routes.get_db_connection", return_value=conn), patch(
            "server.routes.exam_routes.trigger_socket_notify", new_callable=AsyncMock
        ):
            response = TestClient(app).post(
                "/api/rooms/3/exams",
                json={"title": "Demo", "draft_id": 9, "questions": [{"text": "Question", "score": 1}]},
            )

        assert response.status_code == 200
        assert response.json()["id"] == 42
        assert not any(
            "DELETE FROM exam_drafts" in call.args[0] for call in cursor.execute.call_args_list
        )
        conn.commit.assert_called_once()
    finally:
        app.dependency_overrides.clear()
