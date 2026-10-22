import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from server.main import app
from server.utils import get_current_user
import json
from datetime import datetime, timedelta, timezone

# Create a test client
client = TestClient(app)

# Override dependencies helper
def override_get_current_user(user_data):
    def _override():
        return user_data
    app.dependency_overrides[get_current_user] = _override

def clear_overrides():
    app.dependency_overrides.clear()

# --- Basic Tests ---
def test_ping():
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert "pong" in str(response.json())

def test_docs_page():
    response = client.get("/docs")
    assert response.status_code == 200

def test_cors_preflight_for_production_origin():
    """Verify that OPTIONS preflight requests from Netlify production origin succeed with CORS headers."""
    response = client.options(
        "/api/auth/register",
        headers={
            "Origin": "https://llms-auto-score-systems.netlify.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://llms-auto-score-systems.netlify.app"
    assert response.headers.get("access-control-allow-credentials") == "true"

# --- Authentication Tests ---
@patch("server.routes.auth_routes.get_db_connection")
def test_auth_register_success(mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock user check (none exists) and insert success
    mock_cursor.fetchone.return_value = None
    
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "name": "Test User"
    })
    assert response.status_code == 200
    assert "message" in response.json() or "access_token" in response.json()

@patch("server.routes.auth_routes.get_db_connection")
def test_auth_login_fail(mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None # User not found
    
    response = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401


@patch("server.routes.auth_routes.get_firebase_auth", return_value=None)
def test_firebase_login_initializes_admin_lazily(mock_get_firebase_auth):
    """The route must initialize Firebase at request time, not use a stale import."""
    response = client.post("/api/auth/firebase-login", json={
        "firebase_token": "test-token"
    })
    assert response.status_code == 503
    assert response.json()["detail"] == "Firebase Admin SDK not configured"
    mock_get_firebase_auth.assert_called_once_with()


@patch("server.routes.auth_routes.get_db_connection")
@patch("server.routes.auth_routes.get_firebase_auth")
def test_link_google_cannot_replace_existing_google_account(mock_firebase, mock_db):
    override_get_current_user({"id": 1, "email": "first@example.com", "role": "student"})
    mock_firebase.return_value.verify_id_token.return_value = {
        "uid": "google-account-b", "email": "second@example.com"
    }
    cursor = mock_db.return_value.cursor.return_value
    cursor.fetchone.return_value = {"google_id": "google-account-a", "avatar_url": None}

    try:
        response = client.post(
            "/api/auth/link-google", json={"firebase_token": "verified-token"},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 400
        assert "ผูกกับ Google อื่น" in response.json()["detail"]
        assert not any(
            call.args[0].startswith("UPDATE users SET google_id")
            for call in cursor.execute.call_args_list
        )
    finally:
        clear_overrides()


@pytest.mark.parametrize("google_id,credentials", [
    ("google-account-a", {}),
    (None, {}),
    ("google-account-a", {"otp": "123456"}),
])
@patch("server.routes.auth_routes.get_db_connection")
def test_delete_account_requires_fresh_verification(mock_db, google_id, credentials):
    override_get_current_user({"id": 1, "email": "person@example.com", "role": "student"})
    cursor = mock_db.return_value.cursor.return_value
    cursor.fetchone.side_effect = [
        {"id": 1, "password": "hashed-password", "google_id": google_id},
        None,
    ]
    try:
        response = client.request(
            "DELETE", "/api/auth/account", json=credentials,
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 400
        assert not any(
            call.args[0].startswith("DELETE FROM users")
            for call in cursor.execute.call_args_list
        )
    finally:
        clear_overrides()


@patch("server.routes.auth_routes.get_db_connection")
def test_verify_email_accepts_database_datetime(mock_db):
    cursor = mock_db.return_value.cursor.return_value
    cursor.fetchone.return_value = {
        "id": 3, "user_id": 7,
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    response = client.post('/api/auth/verify-email', json={"token": "test-token"})
    assert response.status_code == 200
    assert any(call.args[0].startswith('UPDATE users SET is_verified')
               for call in cursor.execute.call_args_list)


@patch("server.routes.auth_routes.verify_password", return_value=True)
@patch("server.routes.auth_routes.get_db_connection")
def test_delete_teacher_account_removes_owned_rooms(mock_db, mock_verify):
    override_get_current_user({"id": 1, "email": "teacher@example.test", "role": "teacher"})
    cursor = mock_db.return_value.cursor.return_value
    cursor.fetchone.return_value = {"id": 1, "password": "hash", "google_id": None}
    try:
        response = client.request("DELETE", "/api/auth/account", json={"password": "password"})
        assert response.status_code == 200
        statements = [call.args[0] for call in cursor.execute.call_args_list]
        assert statements.index('DELETE FROM rooms WHERE teacher_id = ?') < statements.index('DELETE FROM users WHERE id = ?')
    finally:
        clear_overrides()

# --- Room Management Tests ---
@patch("server.routes.room_routes.get_db_connection")
def test_create_room(mock_db):
    override_get_current_user({"id": 1, "email": "teacher@test.com", "role": "teacher"})
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"id": 1, "name": "Science 101", "section": "A1"}
    
    response = client.post("/api/rooms", 
        json={"name": "Science 101", "section": "A1"},
        headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Science 101"
    clear_overrides()

@patch("server.routes.room_routes.get_db_connection")
def test_get_rooms(mock_db):
    override_get_current_user({"id": 1, "email": "user@test.com", "role": "teacher"})
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock returning a list of rooms
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Room 1", "section": "S1", "class_code": "CODE1"},
        {"id": 2, "name": "Room 2", "section": "S2", "class_code": "CODE2"}
    ]
    
    response = client.get("/api/rooms", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    clear_overrides()

# --- Exam & Question Bank Tests ---
@patch("server.routes.room_routes.get_db_connection")
def test_room_members_do_not_expose_login_emails(mock_db):
    override_get_current_user({"id": 1, "role": "teacher"})
    cursor = mock_db.return_value.cursor.return_value
    cursor.fetchone.side_effect = [
        {"id": 1},
        {"id": 1, "name": "Teacher", "student_id": "teacher-01", "avatar_url": None},
    ]
    cursor.fetchall.return_value = [
        {"id": 2, "name": "Student", "student_id": "student-01", "avatar_url": None, "joined_at": None},
    ]
    try:
        response = client.get("/api/rooms/1/members")
        assert response.status_code == 200
        assert all("email" not in member for member in response.json())
        assert all("u.email" not in call.args[0] for call in cursor.execute.call_args_list)
    finally:
        clear_overrides()


@patch("server.routes.exam_routes.get_db_connection")
def test_get_exams(mock_db):
    override_get_current_user({"id": 1, "role": "teacher"})
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [
        {"id": 101, "title": "Midterm Exam", "total_score": 50, "created_at": "2026-10-22 10:00:00"}
    ]
    
    response = client.get("/api/rooms/1/exams", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Midterm Exam"
    clear_overrides()

# --- Gemini rubric route (provider call mocked, transport tested separately) ---
@patch("server.routes.ai_routes._get_gemini_api_key", return_value="test-only")
@patch("server.routes.ai_routes.generate_rubric_with_gemini")
def test_generate_rubric_mock(mock_generate, mock_key):
    override_get_current_user({"id": 1, "role": "teacher"})
    mock_generate.return_value = {
        "answer_key": "LIFO",
        "rubrics": [{"name": "Accuracy", "description": "Good", "score": 10}],
    }
    response = client.post("/api/ai/generate-rubric", json={"question_text": "Explain Stack", "total_score": 10})
    assert response.status_code == 200
    assert response.json()["answer_key"] == "LIFO"
    mock_generate.assert_awaited_once()
