class TestCreateUser:
    def test_success(self, client):
        resp = client.post(
            "/api/v1/users/",
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
        assert "password_hash" not in data

    def test_duplicate_email(self, client):
        payload = {
            "email": "dup@example.com",
            "username": "user1",
            "password": "password123",
        }
        client.post("/api/v1/users/", json=payload)
        resp = client.post(
            "/api/v1/users/",
            json={**payload, "username": "user2"},
        )
        assert resp.status_code == 409

    def test_duplicate_username(self, client):
        payload = {
            "email": "a@example.com",
            "username": "sameuser",
            "password": "password123",
        }
        client.post("/api/v1/users/", json=payload)
        resp = client.post(
            "/api/v1/users/",
            json={**payload, "email": "b@example.com"},
        )
        assert resp.status_code == 409

    def test_invalid_email(self, client):
        resp = client.post(
            "/api/v1/users/",
            json={
                "email": "bad-email",
                "username": "testuser",
                "password": "password123",
            },
        )
        assert resp.status_code == 400


class TestGetUser:
    def test_found(self, client, make_user):
        user = make_user(email="found@example.com", username="founduser")
        resp = client.get(f"/api/v1/users/{user.id}")
        assert resp.status_code == 200
        assert resp.json()["email"] == "found@example.com"

    def test_not_found(self, client):
        resp = client.get("/api/v1/users/9999")
        assert resp.status_code == 404


class TestAuthProtectedEndpoints:
    """Endpoints behind get_current_user should return 401 without a token."""

    def test_get_me(self, client):
        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401

    def test_patch_me(self, client):
        resp = client.patch("/api/v1/users/me", json={"email": "x@y.com"})
        assert resp.status_code == 401

    def test_delete_me(self, client):
        resp = client.delete("/api/v1/users/me")
        assert resp.status_code == 401

    def test_change_password(self, client):
        resp = client.put(
            "/api/v1/users/me/password",
            json={
                "current_password": "old",
                "new_password": "newpass123",
                "confirm_new_password": "newpass123",
            },
        )
        assert resp.status_code == 401
