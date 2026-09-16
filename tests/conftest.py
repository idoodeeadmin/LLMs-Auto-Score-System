"""Tests use no developer secrets and cannot connect to external services."""
import os
os.environ['PYTHON_DOTENV_DISABLED'] = '1'
os.environ['JWT_SECRET_KEY'] = 'local-tests-only-not-a-production-secret'
os.environ['OPENAI_API_KEY'] = ''
os.environ['OPENAI_MODEL'] = 'gpt-5.6-luna'
os.environ['SMTP_HOST'] = ''
os.environ['SMTP_USER'] = ''
os.environ['SMTP_PASSWORD'] = ''

import socket
import pytest

@pytest.fixture(autouse=True)
def isolate_tests(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError('External network is disabled in automated tests')
    original_connect = socket.socket.connect
    def local_only(sock, address):
        if isinstance(address, tuple) and address[0] in ('127.0.0.1', '::1', 'localhost'):
            return original_connect(sock, address)
        return no_network()
    monkeypatch.setattr(socket.socket, 'connect', local_only)
    monkeypatch.setattr(socket, 'create_connection', no_network)
    from server.main import app
    from server.utils import REQUEST_LOGS
    app.dependency_overrides.clear()
    REQUEST_LOGS.clear()
    yield
    app.dependency_overrides.clear()
