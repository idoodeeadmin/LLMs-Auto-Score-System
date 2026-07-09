import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from server.main import app
from server.utils import get_current_user
import json

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
@patch("server.routes.exam_routes.get_db_connection")
def test_get_exams(mock_db):
    override_get_current_user({"id": 1, "role": "teacher"})
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [
        {"id": 101, "title": "Midterm Exam", "total_score": 50}
    ]
    
    response = client.get("/api/rooms/1/exams", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Midterm Exam"
    clear_overrides()

# --- AI & Rubric Generation Mock Test ---
@patch("server.routes.ai_routes._genai_client")
def test_generate_rubric_mock(mock_genai):
    override_get_current_user({"id": 1, "role": "teacher"})
    # Mock AI response
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "answer_key": "Correct Answer",
        "rubrics": [{"name": "Accuracy", "description": "Good", "score": 10}]
    })
    mock_genai.models.generate_content.return_value = mock_response
    
    response = client.post("/api/gemini/generate-rubric", 
        json={"question_text": "What is AI?", "total_score": 10},
        headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 200
    assert "answer_key" in response.json()
    clear_overrides()


