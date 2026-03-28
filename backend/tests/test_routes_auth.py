import pytest


STUB_ENDPOINTS = [
    ("POST", "/api/v1/auth/signup"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/refresh"),
    ("POST", "/api/v1/auth/logout"),
    ("POST", "/api/v1/auth/forgot_password"),
    ("PUT", "/api/v1/auth/reset_password"),
]


class TestAuthStubs:
    @pytest.mark.parametrize("method,path", STUB_ENDPOINTS)
    def test_returns_501(self, client, method, path):
        resp = client.request(method, path)
        assert resp.status_code == 501
        assert resp.json()["detail"] == "Not implemented"
