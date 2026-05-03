"""Integration tests for /api/v1/profiles routes."""

from app.repository.profile import create_profile
from app.schemas.profile import ProfileCreate


def _register_and_login(client):
    signup = {
        "email": "profile@example.com",
        "username": "authuser",
        "password": "password123",
    }
    client.post("/api/v1/auth/signup", json=signup)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": signup["email"], "password": signup["password"]},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _valid_create_body(**overrides):
    body = {
        "firstname": "Jane",
        "lastname": "Doe",
        "username": "janedoe",
        "contact_email": "jane.public@example.com",
    }
    body.update(overrides)
    return body


class TestProfileAuthRequired:
    def test_post_me_unauthorized(self, client):
        r = client.post(
            "/api/v1/profiles/me",
            json=_valid_create_body(),
        )
        assert r.status_code == 401

    def test_get_me_unauthorized(self, client):
        r = client.get("/api/v1/profiles/me")
        assert r.status_code == 401

    def test_patch_me_unauthorized(self, client):
        r = client.patch(
            "/api/v1/profiles/me",
            json={"firstname": "X"},
        )
        assert r.status_code == 401

    def test_delete_me_unauthorized(self, client):
        r = client.delete("/api/v1/profiles/me")
        assert r.status_code == 401


class TestGetProfileByUsername:
    def test_public_get_found(self, client):
        headers = _register_and_login(client)
        create = client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json=_valid_create_body(username="publichandle"),
        )
        assert create.status_code == 201

        r = client.get("/api/v1/profiles/publichandle")
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "publichandle"
        assert data["firstname"] == "Jane"

    def test_public_get_not_found(self, client):
        r = client.get("/api/v1/profiles/doesnotexist999")
        assert r.status_code == 404


class TestProfileMeCrud:
    def test_create_get_patch_delete_flow(self, client):
        headers = _register_and_login(client)

        missing = client.get("/api/v1/profiles/me", headers=headers)
        assert missing.status_code == 404

        post = client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json=_valid_create_body(),
        )
        assert post.status_code == 201
        created = post.json()
        assert created["user_id"] is not None
        assert created["username"] == "janedoe"
        assert created["contact_email"] == "jane.public@example.com"

        get_me = client.get("/api/v1/profiles/me", headers=headers)
        assert get_me.status_code == 200
        assert get_me.json()["firstname"] == "Jane"

        patch = client.patch(
            "/api/v1/profiles/me",
            headers=headers,
            json={"firstname": "Janet", "description": "Hello"},
        )
        assert patch.status_code == 200
        assert patch.json()["firstname"] == "Janet"
        assert patch.json()["description"] == "Hello"

        delete = client.delete("/api/v1/profiles/me", headers=headers)
        assert delete.status_code == 204

        after = client.get("/api/v1/profiles/me", headers=headers)
        assert after.status_code == 404

    def test_create_duplicate_returns_409(self, client):
        headers = _register_and_login(client)
        first = client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json=_valid_create_body(),
        )
        assert first.status_code == 201

        second = client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json=_valid_create_body(username="othername"),
        )
        assert second.status_code == 409

    def test_create_username_conflict_returns_409(self, client):
        """Another user already took the profile username."""
        h1 = _register_and_login(client)
        first = client.post(
            "/api/v1/profiles/me",
            headers=h1,
            json=_valid_create_body(),
        )
        assert first.status_code == 201

        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "second@example.com",
                "username": "user2",
                "password": "password123",
            },
        )
        login2 = client.post(
            "/api/v1/auth/login",
            json={"email": "second@example.com", "password": "password123"},
        )
        h2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

        clash = client.post(
            "/api/v1/profiles/me",
            headers=h2,
            json=_valid_create_body(),
        )
        assert clash.status_code == 409

    def test_create_invalid_body_no_contact(self, client):
        headers = _register_and_login(client)
        r = client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json={
                "firstname": "A",
                "lastname": "B",
                "username": "ab_user",
            },
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "validation_error"

    def test_patch_username_conflict(self, client):
        headers1 = _register_and_login(client)
        client.post(
            "/api/v1/profiles/me",
            headers=headers1,
            json=_valid_create_body(username="alice_prof"),
        )

        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "bob@example.com",
                "username": "bobuser",
                "password": "password123",
            },
        )
        login_bob = client.post(
            "/api/v1/auth/login",
            json={"email": "bob@example.com", "password": "password123"},
        )
        headers2 = {"Authorization": f"Bearer {login_bob.json()['access_token']}"}
        client.post(
            "/api/v1/profiles/me",
            headers=headers2,
            json=_valid_create_body(username="bob_prof", contact_email="bob@x.com"),
        )

        r = client.patch(
            "/api/v1/profiles/me",
            headers=headers2,
            json={"username": "alice_prof"},
        )
        assert r.status_code == 409

    def test_patch_clears_contacts_returns_400(self, client):
        headers = _register_and_login(client)
        client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json=_valid_create_body(),
        )
        r = client.patch(
            "/api/v1/profiles/me",
            headers=headers,
            json={"contact_email": None, "contact_phone": None},
        )
        assert r.status_code == 400


class TestSeedPublicProfile:
    """Public username lookup works for profiles created via repository."""

    def test_get_by_username_db_only(self, client, db_session, make_user):
        user = make_user()
        create_profile(
            db_session,
            user.id,
            ProfileCreate(
                firstname="Seed",
                lastname="User",
                username="seeduser",
                contact_email="seed@example.com",
            ),
        )
        r = client.get("/api/v1/profiles/seeduser")
        assert r.status_code == 200
        assert r.json()["firstname"] == "Seed"
