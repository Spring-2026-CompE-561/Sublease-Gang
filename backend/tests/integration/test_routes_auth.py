from app.models.profiles import Profile
from app.models.user import User


def _signup_payload(**overrides) -> dict:
    """Build a valid SignupRequest body for tests; overrides any field."""
    payload = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "password123",
        "firstname": "Jane",
        "lastname": "Doe",
    }
    payload.update(overrides)
    return payload


class TestSignup:
    def test_success(self, client, db_session):
        resp = client.post("/api/v1/auth/signup", json=_signup_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # User and profile rows should have been created in the same transaction.
        user = db_session.query(User).filter(User.email == "new@example.com").first()
        assert user is not None
        assert user.username == "newuser"
        profile = (
            db_session.query(Profile).filter(Profile.username == "newuser").first()
        )
        assert profile is not None
        assert profile.firstname == "Jane"
        assert profile.lastname == "Doe"

    def test_duplicate_email(self, client, make_user):
        make_user(email="dup@example.com")
        resp = client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="dup@example.com", username="other"),
        )
        assert resp.status_code == 409

    def test_duplicate_username(self, client, make_user):
        make_user(username="taken")
        resp = client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="x@example.com", username="taken"),
        )
        assert resp.status_code == 409


class TestLogin:
    def _create_user(self, client):
        client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="login@example.com", username="loginuser"),
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
    def _signup_and_get_tokens(self, client, *, email, username):
        resp = client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email=email, username=username),
        )
        return resp.json()

    def test_requires_auth(self, client):
        resp = client.post("/api/v1/auth/logout")
        assert resp.status_code in (401, 403)

    def test_revokes_only_supplied_refresh_token(self, client, db_session):
        from app.models.token import Token

        # Sign up once for one session, then log in again to mint a second
        # refresh token (simulating two devices).
        first = self._signup_and_get_tokens(
            client, email="logout1@example.com", username="logout1"
        )
        client.post(
            "/api/v1/auth/login",
            json={"email": "logout1@example.com", "password": "password123"},
        )

        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {first['access_token']}"},
            json={"refresh_token": first["refresh_token"]},
        )
        assert resp.status_code == 204

        # Exactly one refresh row should be revoked, the other still active.
        # We assert at the DB layer because hitting /refresh with the revoked
        # token would (correctly) trigger reuse detection and cascade-burn
        # the other session — that's a different code path.
        rows = db_session.query(Token).filter(Token.token_type == "refresh").all()
        revoked = [r for r in rows if r.revoked_at is not None]
        active = [r for r in rows if r.revoked_at is None]
        assert len(revoked) == 1
        assert len(active) == 1

    def test_logout_without_body_revokes_all_refresh_tokens(self, client, db_session):
        from app.models.token import Token

        first = self._signup_and_get_tokens(
            client, email="logout2@example.com", username="logout2"
        )
        client.post(
            "/api/v1/auth/login",
            json={"email": "logout2@example.com", "password": "password123"},
        )

        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {first['access_token']}"},
        )
        assert resp.status_code == 204

        active = (
            db_session.query(Token)
            .filter(Token.token_type == "refresh", Token.revoked_at.is_(None))
            .count()
        )
        assert active == 0

    def test_logout_with_other_users_refresh_token_falls_back_to_revoke_all(
        self, client, db_session
    ):
        from app.models.token import Token

        attacker = self._signup_and_get_tokens(
            client, email="atk@example.com", username="atkuser"
        )
        victim = self._signup_and_get_tokens(
            client, email="vic@example.com", username="vicuser"
        )

        # Attacker tries to log out using the victim's refresh token. Should
        # fall back to revoking all of the *attacker's* refresh tokens, never
        # the victim's.
        resp = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {attacker['access_token']}"},
            json={"refresh_token": victim["refresh_token"]},
        )
        assert resp.status_code == 204

        active = (
            db_session.query(Token)
            .filter(Token.token_type == "refresh", Token.revoked_at.is_(None))
            .all()
        )
        # Only the victim's token should remain active.
        assert len(active) == 1


class TestRefresh:
    def _login(self, client):
        client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="ref@example.com", username="refuser"),
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

    def test_refresh_token_issued_before_password_change_rejected(
        self, client, db_session
    ):
        from datetime import UTC, datetime, timedelta

        tokens = self._login(client)
        user = db_session.query(User).filter(User.email == "ref@example.com").first()
        assert user is not None
        # Simulate a password change after the refresh token was minted.
        user.password_changed_at = datetime.now(UTC) + timedelta(days=1)
        db_session.commit()

        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert resp.status_code == 401
        assert "Invalid or expired refresh token" in resp.json()["detail"]

    def test_refresh_rotates_and_old_token_is_revoked(self, client):
        tokens = self._login(client)
        first = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert first.status_code == 200
        new_tokens = first.json()
        assert new_tokens["refresh_token"] != tokens["refresh_token"]

        # Replaying the now-rotated original refresh should fail.
        replay = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert replay.status_code == 401

    def test_refresh_reuse_detection_burns_all_user_tokens(self, client):
        tokens = self._login(client)
        rotated = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert rotated.status_code == 200
        new_refresh = rotated.json()["refresh_token"]

        # Replay the original — triggers reuse detection.
        replay = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert replay.status_code == 401

        # The most recent (legitimate) refresh token must now also be dead.
        followup = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": new_refresh},
        )
        assert followup.status_code == 401

    def test_refresh_token_without_jti_rejected(self, client, db_session):
        import jwt
        from datetime import UTC, datetime, timedelta

        from app.core.auth import ALGORITHM, SECRET_KEY

        self._login(client)
        user = db_session.query(User).filter(User.email == "ref@example.com").first()
        # Hand-craft a refresh token missing the jti claim entirely.
        forged = jwt.encode(
            {
                "sub": str(user.id),
                "type": "refresh",
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(days=1),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": forged},
        )
        assert resp.status_code == 401

    def test_refresh_token_with_unknown_jti_rejected(self, client, db_session):
        import jwt
        from datetime import UTC, datetime, timedelta

        from app.core.auth import ALGORITHM, SECRET_KEY

        self._login(client)
        user = db_session.query(User).filter(User.email == "ref@example.com").first()
        forged = jwt.encode(
            {
                "sub": str(user.id),
                "type": "refresh",
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(days=1),
                "jti": "this-jti-was-never-issued",
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": forged},
        )
        assert resp.status_code == 401


class TestForgotPassword:
    def test_registered_email(self, client):
        client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="forgot@example.com", username="forgotuser"),
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

    def test_production_mode_omits_token_from_response_and_logs(
        self, client, monkeypatch, caplog
    ):
        from app.routes import auth as auth_routes

        monkeypatch.setattr(auth_routes.settings, "environment", "production")
        client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="prod@example.com", username="produser"),
        )
        with caplog.at_level("INFO", logger="app.routes.auth"):
            resp = client.post(
                "/api/v1/auth/forgot_password",
                json={"email": "prod@example.com"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "reset_token" not in data
        # No log record should contain a JWT (three dot-separated base64 segments).
        for record in caplog.records:
            assert record.getMessage().count(".") < 2 or "eyJ" not in record.getMessage()


class TestResetPassword:
    def _get_reset_token(self, client):
        client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="reset@example.com", username="resetuser"),
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

    def test_reset_token_is_single_use(self, client):
        token = self._get_reset_token(client)
        first = client.put(
            "/api/v1/auth/reset_password",
            json={"token": token, "new_password": "newpassword123"},
        )
        assert first.status_code == 200

        # Replaying the same reset token must fail.
        replay = client.put(
            "/api/v1/auth/reset_password",
            json={"token": token, "new_password": "anotherpassword456"},
        )
        assert replay.status_code == 400

    def test_consuming_one_reset_token_burns_peers(self, client):
        # User requests two reset tokens (e.g., spammy "forgot password" clicks).
        first_token = self._get_reset_token(client)
        second_resp = client.post(
            "/api/v1/auth/forgot_password",
            json={"email": "reset@example.com"},
        )
        second_token = second_resp.json()["reset_token"]
        assert first_token != second_token

        # Consuming the first should also dead-end the second.
        consumed = client.put(
            "/api/v1/auth/reset_password",
            json={"token": first_token, "new_password": "newpassword123"},
        )
        assert consumed.status_code == 200

        leftover = client.put(
            "/api/v1/auth/reset_password",
            json={"token": second_token, "new_password": "yetanother456"},
        )
        assert leftover.status_code == 400

    def test_reset_token_without_jti_rejected(self, client, db_session):
        import jwt
        from datetime import UTC, datetime, timedelta

        from app.core.auth import ALGORITHM, SECRET_KEY

        # Sign up a user, then hand-craft a reset token without a jti claim.
        client.post(
            "/api/v1/auth/signup",
            json=_signup_payload(email="rj@example.com", username="rjuser"),
        )
        user = db_session.query(User).filter(User.email == "rj@example.com").first()
        forged = jwt.encode(
            {
                "sub": str(user.id),
                "type": "reset",
                "iat": datetime.now(UTC),
                "exp": datetime.now(UTC) + timedelta(minutes=10),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        resp = client.put(
            "/api/v1/auth/reset_password",
            json={"token": forged, "new_password": "newpassword123"},
        )
        assert resp.status_code == 400
