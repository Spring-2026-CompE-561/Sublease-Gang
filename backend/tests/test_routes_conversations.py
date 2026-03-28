class TestListConversations:
    def test_returns_empty_list(self, client):
        resp = client.get("/api/v1/conversations/")
        assert resp.status_code == 200
        assert resp.json() == []


class TestCreateConversation:
    def test_returns_placeholder(self, client):
        resp = client.post("/api/v1/conversations/")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "listing_id" in data


class TestListMessages:
    def test_returns_empty_list(self, client, db_session):
        from app.models.user import User
        from app.core.dependencies import get_current_user
        from app.main import app

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
        from app.models.user import User
        from app.core.dependencies import get_current_user
        from app.main import app

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
