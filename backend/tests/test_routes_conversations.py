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
