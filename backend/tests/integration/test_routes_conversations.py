from app.core.dependencies import get_current_user
from app.main import app
from app.models.user import User


class TestListConversations:
    def test_requires_auth(self, client):
        resp = client.get("/api/v1/conversations/")
        assert resp.status_code == 401

    def test_returns_empty_list(self, client, make_user):
        user = make_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.get("/api/v1/conversations/")
            assert resp.status_code == 200
            assert resp.json() == []
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_returns_conversations(
        self, client, make_user, make_listing, make_conversation
    ):
        user1 = make_user()
        user2 = make_user()
        listing = make_listing(user1.id)
        make_conversation(listing.id, user1.id, user2.id)
        app.dependency_overrides[get_current_user] = lambda: user1
        try:
            resp = client.get("/api/v1/conversations/")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 1
            assert data[0]["listing_id"] == listing.id
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestCreateConversation:
    def test_requires_auth(self, client):
        resp = client.post(
            "/api/v1/conversations/", json={"listing_id": 1, "other_user_id": 2}
        )
        assert resp.status_code == 401

    def test_success(self, client, make_user, make_listing):
        user1 = make_user()
        user2 = make_user()
        listing = make_listing(user1.id)
        app.dependency_overrides[get_current_user] = lambda: user1
        try:
            resp = client.post(
                "/api/v1/conversations/",
                json={"listing_id": listing.id, "other_user_id": user2.id},
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["listing_id"] == listing.id
            assert "id" in data
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_idempotent(self, client, make_user, make_listing):
        user1 = make_user()
        user2 = make_user()
        listing = make_listing(user1.id)
        app.dependency_overrides[get_current_user] = lambda: user1
        try:
            resp1 = client.post(
                "/api/v1/conversations/",
                json={"listing_id": listing.id, "other_user_id": user2.id},
            )
            resp2 = client.post(
                "/api/v1/conversations/",
                json={"listing_id": listing.id, "other_user_id": user2.id},
            )
            assert resp1.json()["id"] == resp2.json()["id"]
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_cannot_converse_with_self(self, client, make_user, make_listing):
        user = make_user()
        listing = make_listing(user.id)
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.post(
                "/api/v1/conversations/",
                json={"listing_id": listing.id, "other_user_id": user.id},
            )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_other_user_not_found(self, client, make_user, make_listing):
        user = make_user()
        listing = make_listing(user.id)
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.post(
                "/api/v1/conversations/",
                json={"listing_id": listing.id, "other_user_id": 9999},
            )
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_listing_not_found(self, client, make_user):
        user1 = make_user()
        user2 = make_user()
        app.dependency_overrides[get_current_user] = lambda: user1
        try:
            resp = client.post(
                "/api/v1/conversations/",
                json={"listing_id": 9999, "other_user_id": user2.id},
            )
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestListMessages:
    def test_returns_empty_list(self, client, db_session):
        user = User(email="msg@example.com", username="msguser", password_hash="fake")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.get("/api/v1/conversations/1/messages")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestSendMessage:
    def test_returns_placeholder(self, client, db_session):
        user = User(email="msg2@example.com", username="msguser2", password_hash="fake")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.post(
                "/api/v1/conversations/1/messages",
                json={"content": "hello"},
            )
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestConversationMessagePermissionsWithAuth:
    def _register_and_login(self, client, *, email: str, username: str):
        password = "password123"
        client.post(
            "/api/v1/auth/signup",
            json={"email": email, "username": username, "password": password},
        )
        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_listing(self, client, headers, title: str):
        resp = client.post(
            "/api/v1/listings/",
            headers=headers,
            json={
                "title": title,
                "description": "Listing for conversation tests",
                "price": 900,
                "location": "Test City",
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-02-01T00:00:00Z",
                "latitude": 40.0,
                "longitude": -74.0,
            },
        )
        assert resp.status_code == 201
        return resp.json()["id"]

    def _create_conversation(self, client, headers, listing_id: int, other_user_id: int):
        resp = client.post(
            "/api/v1/conversations/",
            headers=headers,
            json={"listing_id": listing_id, "other_user_id": other_user_id},
        )
        assert resp.status_code == 201
        return resp.json()["id"]

    def test_non_participant_cannot_list_messages(self, client):
        owner_headers = self._register_and_login(
            client,
            email="conv_owner@example.com",
            username="conv_owner",
        )
        listing_id = self._create_listing(client, owner_headers, "Conversation Listing")

        participant_headers = self._register_and_login(
            client,
            email="conv_participant@example.com",
            username="conv_participant",
        )
        participant_id = client.get("/api/v1/users/me", headers=participant_headers).json()["id"]
        conversation_id = self._create_conversation(
            client,
            owner_headers,
            listing_id,
            participant_id,
        )

        outsider_headers = self._register_and_login(
            client,
            email="conv_outsider@example.com",
            username="conv_outsider",
        )
        resp = client.get(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=outsider_headers,
        )
        assert resp.status_code == 403

    def test_non_participant_cannot_send_message(self, client):
        owner_headers = self._register_and_login(
            client,
            email="conv_owner2@example.com",
            username="conv_owner2",
        )
        listing_id = self._create_listing(client, owner_headers, "Conversation Listing")

        participant_headers = self._register_and_login(
            client,
            email="conv_participant2@example.com",
            username="conv_participant2",
        )
        participant_id = client.get("/api/v1/users/me", headers=participant_headers).json()["id"]
        conversation_id = self._create_conversation(
            client,
            owner_headers,
            listing_id,
            participant_id,
        )

        outsider_headers = self._register_and_login(
            client,
            email="conv_outsider2@example.com",
            username="conv_outsider2",
        )
        resp = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=outsider_headers,
            json={"content": "I should not be allowed in this conversation"},
        )
        assert resp.status_code == 403

    def test_participant_can_send_and_list_messages(self, client):
        owner_headers = self._register_and_login(
            client,
            email="conv_owner3@example.com",
            username="conv_owner3",
        )
        listing_id = self._create_listing(client, owner_headers, "Conversation Listing")

        participant_headers = self._register_and_login(
            client,
            email="conv_participant3@example.com",
            username="conv_participant3",
        )
        participant_id = client.get("/api/v1/users/me", headers=participant_headers).json()["id"]
        conversation_id = self._create_conversation(
            client,
            owner_headers,
            listing_id,
            participant_id,
        )

        send_resp = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=participant_headers,
            json={"content": "Hello listing owner"},
        )
        assert send_resp.status_code == 201
        body = send_resp.json()
        assert body["conversation_id"] == conversation_id
        assert body["content"] == "Hello listing owner"

        list_resp = client.get(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=owner_headers,
        )
        assert list_resp.status_code == 200
        messages = list_resp.json()
        assert len(messages) == 1
        assert messages[0]["content"] == "Hello listing owner"
