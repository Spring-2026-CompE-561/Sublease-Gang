from app.models.user import User


class TestSignup:
    def test_success(self, client):
        resp = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "password123",
            },
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
            json={
                "email": "dup@example.com",
                "username": "other",
                "password": "password123",
            },
        )
        assert resp.status_code == 409

    def test_duplicate_username(self, client, make_user):
        make_user(username="taken")
        resp = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "x@example.com",
                "username": "taken",
                "password": "password123",
            },
        )
        assert resp.status_code == 409


class TestLogin:
    def _create_user(self, client):
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123",
            },
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
        assert "refresh_token" in data
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


class TestRefresh:
    def _login(self, client):
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "ref@example.com",
                "username": "refuser",
                "password": "password123",
            },
        )
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "ref@example.com", "password": "password123"},
        )
        return resp.json()

    def test_success(self, client):
        tokens = self._login(client)
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_invalid_token(self, client):
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "not.a.valid.token"},
        )
        assert resp.status_code == 401

    def test_access_token_rejected(self, client):
        tokens = self._login(client)
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["access_token"]},
        )
        assert resp.status_code == 401

    def test_missing_body(self, client):
        resp = client.post("/api/v1/auth/refresh")
        assert resp.status_code == 400

    def test_disabled_user_rejected(self, client, db_session):
        tokens = self._login(client)
        user = db_session.query(User).filter(User.email == "ref@example.com").first()
        assert user is not None
        user.account_disabled = True
        db_session.commit()

        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "User not found or account disabled"


class TestForgotPassword:
    def test_registered_email(self, client):
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "forgot@example.com",
                "username": "forgotuser",
                "password": "password123",
            },
        )
        resp = client.post(
            "/api/v1/auth/forgot_password",
            json={"email": "forgot@example.com"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert "reset_token" in data

    def test_unknown_email_still_200(self, client):
        resp = client.post(
            "/api/v1/auth/forgot_password",
            json={"email": "unknown@example.com"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert "reset_token" not in data


class TestResetPassword:
    def _get_reset_token(self, client):
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "reset@example.com",
                "username": "resetuser",
                "password": "password123",
            },
        )
        resp = client.post(
            "/api/v1/auth/forgot_password",
            json={"email": "reset@example.com"},
        )
        return resp.json()["reset_token"]

    def test_success(self, client):
        token = self._get_reset_token(client)
        resp = client.put(
            "/api/v1/auth/reset_password",
            json={"token": token, "new_password": "newpassword123"},
        )
        assert resp.status_code == 200
        assert "message" in resp.json()
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "reset@example.com", "password": "newpassword123"},
        )
        assert login_resp.status_code == 200

    def test_invalid_token(self, client):
        resp = client.put(
            "/api/v1/auth/reset_password",
            json={"token": "bad.token.value", "new_password": "newpassword123"},
        )
        assert resp.status_code == 400

    def test_password_too_short(self, client):
        token = self._get_reset_token(client)
        resp = client.put(
            "/api/v1/auth/reset_password",
            json={"token": token, "new_password": "short"},
        )
        assert resp.status_code == 400
