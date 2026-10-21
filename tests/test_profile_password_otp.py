import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from server.routes import auth_routes


def test_profile_otp_cannot_be_used_as_public_reset_token(monkeypatch):
    def unexpected_database_access():
        raise AssertionError("Profile OTP must be rejected before database access")

    monkeypatch.setattr(auth_routes, "get_db_connection", unexpected_database_access)
    with pytest.raises(HTTPException) as error:
        asyncio.run(auth_routes.reset_password(SimpleNamespace(token="otp:123456", new_password="new-password")))
    assert error.value.status_code == 400
