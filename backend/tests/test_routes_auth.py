import pytest

from app.core.auth import hash_password


class TestSignup:
    def test_success(self, client):
        resp = client.post(
            "/api/v1/auth/signup",
            json={"email": "new@example.com", "username": "newuser", "password": "password123"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data

    def test_duplicate_email(self, client, make_user):
        make_user(email="dup@example.com")
        resp = client.post(
            "/api/v1/auth/signup",
            json={"email": "dup@example.com", "username": "other", "password": "password123"},
        )
        assert resp.status_code == 409

    def test_duplicate_username(self, client, make_user):
        make_user(username="taken")
        resp = client.post(
            "/api/v1/auth/signup",
            json={"email": "x@example.com", "username": "taken", "password": "password123"},
        )
        assert resp.status_code == 409


class TestLogin:
    def _create_user(self, client):
        client.post(
            "/api/v1/auth/signup",
            json={"email": "login@example.com", "username": "loginuser", "password": "password123"},
        )

    def test_success(self, client):
        self._create_user(client)
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "password123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_wrong_password(self, client):
        self._create_user(client)
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    def test_nonexistent_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )
        assert resp.status_code == 401


class TestLogout:
    def test_requires_auth(self, client):
        resp = client.post("/api/v1/auth/logout")
        assert resp.status_code in (401, 403)


STUB_ENDPOINTS = [
    ("POST", "/api/v1/auth/refresh"),
    ("POST", "/api/v1/auth/forgot_password"),
    ("PUT", "/api/v1/auth/reset_password"),
]


class TestAuthStubs:
    @pytest.mark.parametrize("method,path", STUB_ENDPOINTS)
    def test_returns_501(self, client, method, path):
        resp = client.request(method, path)
        assert resp.status_code == 501
        assert resp.json()["detail"] == "Not implemented"
