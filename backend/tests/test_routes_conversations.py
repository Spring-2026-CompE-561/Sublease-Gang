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
    def test_returns_empty_list(self, client):
        resp = client.get("/api/v1/conversations/1/messages")
        assert resp.status_code == 200
        assert resp.json() == []


class TestSendMessage:
    def test_returns_placeholder(self, client):
        resp = client.post("/api/v1/conversations/1/messages")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "sender_id" in data
        assert "content" in data
