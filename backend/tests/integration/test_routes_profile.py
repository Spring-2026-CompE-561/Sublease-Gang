"""Integration tests for /api/v1/profiles routes."""

from app.core.auth import create_access_token
from app.repository.profile import create_profile
from app.schemas.profile import ProfileCreate


def _register_and_login(client, email="profile@example.com", username="authuser"):
    """Sign up a user (which auto-creates their profile) and return auth headers."""
    r = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "username": username,
            "password": "password123",
            "firstname": "Jane",
            "lastname": "Doe",
        },
    )
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _user_no_profile_and_token(make_user, **user_overrides):
    """Create a User with no Profile and return (user, auth headers).

    Used to exercise POST /profiles/me, which is unreachable through normal
    signup (register_with_profile creates the profile atomically).
    """
    user = make_user(**user_overrides)
    token = create_access_token(data={"sub": str(user.id)})
    return user, {"Authorization": f"Bearer {token}"}


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
        # Signup auto-creates a profile under the signup username.
        _register_and_login(client)
        r = client.get("/api/v1/profiles/authuser")
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "authuser"
        assert data["firstname"] == "Jane"

    def test_public_get_not_found(self, client):
        r = client.get("/api/v1/profiles/doesnotexist999")
        assert r.status_code == 404


class TestProfileMeCrud:
    def test_get_patch_delete_flow(self, client):
        """Signup auto-creates the profile; verify GET/PATCH/DELETE work on it."""
        headers = _register_and_login(client)

        get_me = client.get("/api/v1/profiles/me", headers=headers)
        assert get_me.status_code == 200
        assert get_me.json()["firstname"] == "Jane"
        assert get_me.json()["username"] == "authuser"

        # The auto-created profile has no contact info; the PATCH must include
        # one because update_profile rejects a final state with no contact.
        patch = client.patch(
            "/api/v1/profiles/me",
            headers=headers,
            json={
                "firstname": "Janet",
                "description": "Hello",
                "contact_email": "janet@example.com",
            },
        )
        assert patch.status_code == 200
        assert patch.json()["firstname"] == "Janet"
        assert patch.json()["description"] == "Hello"

        delete = client.delete("/api/v1/profiles/me", headers=headers)
        assert delete.status_code == 204

        after = client.get("/api/v1/profiles/me", headers=headers)
        assert after.status_code == 404

    def test_post_when_profile_already_exists_returns_409(self, client):
        """Signup created the profile already; POST /profiles/me must 409."""
        headers = _register_and_login(client)
        r = client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json=_valid_create_body(),
        )
        assert r.status_code == 409

    def test_get_returns_404_when_no_profile(self, client, make_user):
        """GET /profiles/me → 404 when the user has no profile."""
        _, headers = _user_no_profile_and_token(make_user)
        r = client.get("/api/v1/profiles/me", headers=headers)
        assert r.status_code == 404

    def test_post_creates_profile_for_profileless_user(self, client, make_user):
        """A profileless user can create a profile via POST /profiles/me → 201."""
        _, headers = _user_no_profile_and_token(make_user)
        r = client.post(
            "/api/v1/profiles/me",
            headers=headers,
            json=_valid_create_body(),
        )
        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "janedoe"
        assert data["firstname"] == "Jane"
        assert data["contact_email"] == "jane.public@example.com"

    def test_create_username_conflict_returns_409(self, client, make_user):
        """A profileless user can't claim a profile username already in use."""
        # First user signs up and gets a profile with username "authuser".
        _register_and_login(client)

        # Second user is created without a profile so POST /profiles/me is reachable.
        _, headers2 = _user_no_profile_and_token(make_user, username="user2")

        clash = client.post(
            "/api/v1/profiles/me",
            headers=headers2,
            json=_valid_create_body(username="authuser"),
        )
        assert clash.status_code == 409

    def test_create_invalid_body_no_contact(self, client, make_user):
        """POST /profiles/me with no contact info → 400."""
        _, headers = _user_no_profile_and_token(make_user)
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
        """PATCH /profiles/me to a username taken by another profile → 409."""
        _register_and_login(client, email="alice@example.com", username="alice_prof")
        headers2 = _register_and_login(
            client, email="bob@example.com", username="bobuser"
        )

        # The patch must include a contact field because the auto-created
        # profile has none and update_profile rejects a contactless result.
        r = client.patch(
            "/api/v1/profiles/me",
            headers=headers2,
            json={"username": "alice_prof", "contact_email": "bob@example.com"},
        )
        assert r.status_code == 409

    def test_patch_clears_contacts_returns_400(self, client):
        """PATCH that explicitly nulls both contact fields → 400."""
        headers = _register_and_login(client)
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


class TestProfileIconUpload:
    def test_unauthorized(self, client):
        r = client.post(
            "/api/v1/profiles/me/icon",
            files={"file": ("a.jpg", b"x", "image/jpeg")},
        )
        assert r.status_code == 401

    def test_invalid_content_type_returns_415(self, client):
        headers = _register_and_login(client)
        r = client.post(
            "/api/v1/profiles/me/icon",
            headers=headers,
            files={"file": ("a.txt", b"hello", "text/plain")},
        )
        assert r.status_code == 415

    def test_oversized_file_returns_413(self, client, monkeypatch):
        from app.routes import profile as profile_route

        # Shrink the cap so we don't allocate 5MB just to fail it.
        monkeypatch.setattr(profile_route, "MAX_ICON_BYTES", 16)
        headers = _register_and_login(client)
        r = client.post(
            "/api/v1/profiles/me/icon",
            headers=headers,
            files={"file": ("a.jpg", b"x" * 32, "image/jpeg")},
        )
        assert r.status_code == 413

    def test_valid_upload_updates_profile_and_writes_file(
        self, client, tmp_path, monkeypatch
    ):
        from app.routes import profile as profile_route

        icon_dir = tmp_path / "icons"
        monkeypatch.setattr(profile_route, "ICON_DIR", icon_dir)

        headers = _register_and_login(client)
        r = client.post(
            "/api/v1/profiles/me/icon",
            headers=headers,
            files={"file": ("a.png", b"fake-image-bytes", "image/png")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["icon"] is not None
        assert data["icon"].startswith("/media/icons/")
        assert data["icon"].endswith(".png")

        get_me = client.get("/api/v1/profiles/me", headers=headers)
        assert get_me.json()["icon"] == data["icon"]

        written = list(icon_dir.iterdir())
        assert len(written) == 1
        assert written[0].read_bytes() == b"fake-image-bytes"

    def test_user_without_profile_returns_404(
        self, client, make_user, tmp_path, monkeypatch
    ):
        from app.routes import profile as profile_route

        icon_dir = tmp_path / "icons"
        monkeypatch.setattr(profile_route, "ICON_DIR", icon_dir)

        _, headers = _user_no_profile_and_token(make_user)
        r = client.post(
            "/api/v1/profiles/me/icon",
            headers=headers,
            files={"file": ("a.png", b"fake-image-bytes", "image/png")},
        )
        assert r.status_code == 404
        # The route unlinks the file on failure; directory should be empty.
        if icon_dir.exists():
            assert list(icon_dir.iterdir()) == []
