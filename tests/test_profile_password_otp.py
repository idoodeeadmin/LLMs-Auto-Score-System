import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from server.routes import auth_routes
from server.models import ForgotPasswordRequest


def test_profile_otp_cannot_be_used_as_public_reset_token(monkeypatch):
    def unexpected_database_access():
        raise AssertionError("Profile OTP must be rejected before database access")

    monkeypatch.setattr(auth_routes, "get_db_connection", unexpected_database_access)
    with pytest.raises(HTTPException) as error:
        asyncio.run(auth_routes.reset_password(SimpleNamespace(token="otp:123456", new_password="new-password")))
    assert error.value.status_code == 400


def test_delete_otp_cannot_be_used_as_public_reset_token(monkeypatch):
    monkeypatch.setattr(auth_routes, 'get_db_connection', lambda: (_ for _ in ()).throw(AssertionError('Database must not be read')))
    with pytest.raises(HTTPException) as error:
        asyncio.run(auth_routes.reset_password(SimpleNamespace(token='delete:123456', new_password='new-password')))
    assert error.value.status_code == 400


def test_unverified_email_cannot_receive_reset_token(monkeypatch):
    db = MagicMock()
    db.cursor.return_value.fetchone.return_value = {
        'id': 7, 'email': 'fake@example.test', 'google_email': None,
        'is_verified': 0, 'name': 'Test', 'student_id': '123',
    }
    monkeypatch.setattr(auth_routes, 'get_db_connection', lambda: db)
    monkeypatch.setattr(auth_routes, 'check_rate_limit', lambda *args, **kwargs: True)
    with pytest.raises(HTTPException) as error:
        asyncio.run(auth_routes.forgot_password(ForgotPasswordRequest(email='fake@example.test', name='Test')))
    assert error.value.status_code == 400
    assert not any(call.args[0].startswith('INSERT INTO password_resets')
                   for call in db.cursor.return_value.execute.call_args_list)


def test_linked_google_email_is_reset_destination(monkeypatch):
    db = MagicMock()
    db.cursor.return_value.fetchone.return_value = {
        'id': 7, 'email': 'fake@example.test', 'google_email': 'real@example.test',
        'is_verified': 0, 'name': 'Test', 'student_id': '123',
    }
    sent_to = []
    monkeypatch.setattr(auth_routes, 'get_db_connection', lambda: db)
    monkeypatch.setattr(auth_routes, 'check_rate_limit', lambda *args, **kwargs: True)
    monkeypatch.setattr(auth_routes, '_send_smtp_email_sync', lambda to, subject, body: sent_to.append(to) or True)
    for key in ('SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD'):
        monkeypatch.setenv(key, 'test-only')
    result = asyncio.run(auth_routes.forgot_password(ForgotPasswordRequest(email='fake@example.test')))
    assert sent_to == ['real@example.test']
    assert 'reset_token' not in result and 'dev_reset_link' not in result
