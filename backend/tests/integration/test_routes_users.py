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
    def _register_and_login(self, client, email="caller@example.com", username="caller"):
        signup = {
            "email": email,
            "username": username,
            "password": "password123",
            "firstname": "Jane",
            "lastname": "Doe",
        }
        client.post("/api/v1/auth/signup", json=signup)
        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "password123"},
        )
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_found(self, client, make_user):
        headers = self._register_and_login(client)
        user = make_user(email="found@example.com", username="founduser")
        resp = client.get(f"/api/v1/users/{user.id}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == user.id
        assert data["username"] == "founduser"
        assert "email" not in data
        assert "account_disabled" not in data

    def test_not_found(self, client):
        headers = self._register_and_login(client)
        resp = client.get("/api/v1/users/9999", headers=headers)
        assert resp.status_code == 404

    def test_requires_auth(self, client, make_user):
        user = make_user(email="found@example.com", username="founduser")
        resp = client.get(f"/api/v1/users/{user.id}")
        assert resp.status_code == 401


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


class TestAuthenticatedUserRoutes:
    def _register_and_login(self, client):
        signup = {
            "email": "me@example.com",
            "username": "meuser",
            "password": "password123",
            "firstname": "Jane",
            "lastname": "Doe",
        }
        client.post("/api/v1/auth/signup", json=signup)
        login = client.post(
            "/api/v1/auth/login",
            json={"email": signup["email"], "password": signup["password"]},
        )
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_me_success(self, client):
        headers = self._register_and_login(client)
        resp = client.get("/api/v1/users/me", headers=headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "me@example.com"
        assert data["username"] == "meuser"

    def test_patch_me_success(self, client):
        headers = self._register_and_login(client)
        resp = client.patch(
            "/api/v1/users/me",
            headers=headers,
            json={"email": "updated@example.com"},
        )

        assert resp.status_code == 200
        assert resp.json()["email"] == "updated@example.com"

    def test_change_password_then_login_with_new_password(self, client):
        headers = self._register_and_login(client)
        change_resp = client.put(
            "/api/v1/users/me/password",
            headers=headers,
            json={
                "current_password": "password123",
                "new_password": "newpassword123",
                "confirm_new_password": "newpassword123",
            },
        )
        assert change_resp.status_code == 204

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "me@example.com", "password": "newpassword123"},
        )
        assert login_resp.status_code == 200

    def test_delete_me_then_me_is_unauthorized(self, client):
        headers = self._register_and_login(client)
        delete_resp = client.delete("/api/v1/users/me", headers=headers)
        assert delete_resp.status_code == 204

        me_resp = client.get("/api/v1/users/me", headers=headers)
        assert me_resp.status_code == 401

    def test_delete_me_with_full_data_graph(
        self, client, make_user, make_listing, make_conversation, db_session
    ):
        """A user with listings, conversations, and messages can still delete.

        Regression guard for the FK-cascade work in delete_user — without the
        manual cleanup in repository/user.py this would 500 on IntegrityError.
        """
        from app.models.conversations import Conversation
        from app.models.listing import Listing
        from app.models.messages import Message
        from app.models.profiles import Profile
        from app.models.token import Token
        from app.models.user import User

        headers = self._register_and_login(client)
        me_id = client.get("/api/v1/users/me", headers=headers).json()["id"]

        # Build out related data directly against the same test DB session.
        # Note: signup already created the Profile via register_with_profile,
        # so we don't manually insert one here.
        other = make_user()
        third = make_user()
        own_listing = make_listing(host_id=me_id)
        other_listing = make_listing(host_id=other.id)

        convo_as_participant = make_conversation(
            listing_id=other_listing.id,
            user_one_id=me_id,
            user_two_id=other.id,
        )
        convo_on_my_listing = make_conversation(
            listing_id=own_listing.id,
            user_one_id=other.id,
            user_two_id=third.id,
        )
        db_session.add(
            Message(
                conversation_id=convo_as_participant.id,
                sender_id=me_id,
                content="hi",
            )
        )
        db_session.add(
            Message(
                conversation_id=convo_on_my_listing.id,
                sender_id=other.id,
                content="chatting on my listing",
            )
        )
        db_session.commit()
        convo_on_my_listing_id = convo_on_my_listing.id

        delete_resp = client.delete("/api/v1/users/me", headers=headers)
        assert delete_resp.status_code == 204

        # User row and every dependent row are gone.
        assert db_session.query(User).filter(User.id == me_id).count() == 0
        assert db_session.query(Profile).filter(Profile.user_id == me_id).count() == 0
        assert db_session.query(Token).filter(Token.user_id == me_id).count() == 0
        assert db_session.query(Listing).filter(Listing.host_id == me_id).count() == 0
        assert (
            db_session.query(Conversation)
            .filter(
                (Conversation.user_one_id == me_id)
                | (Conversation.user_two_id == me_id)
                | (Conversation.id == convo_on_my_listing_id)
            )
            .count()
            == 0
        )
        assert db_session.query(Message).filter(Message.sender_id == me_id).count() == 0

        # Other users untouched, and old token is now 401.
        assert db_session.query(User).filter(User.id == other.id).count() == 1
        assert db_session.query(User).filter(User.id == third.id).count() == 1
        assert client.get("/api/v1/users/me", headers=headers).status_code == 401
