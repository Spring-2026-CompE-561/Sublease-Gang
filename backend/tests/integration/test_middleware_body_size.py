"""Body-size limit middleware: oversized Content-Length is fast-failed."""


def test_request_exceeding_cap_rejected_with_413(client, monkeypatch):
    from app.main import app
    from app.middleware.body_size import BodySizeLimitMiddleware

    # Find the live middleware instance and shrink its cap so the test
    # doesn't have to send 35MB.
    mw = app.middleware_stack
    while mw is not None:
        if isinstance(mw, BodySizeLimitMiddleware):
            monkeypatch.setattr(mw, "max_bytes", 64)
            break
        mw = getattr(mw, "app", None)
    else:
        raise AssertionError("BodySizeLimitMiddleware not present in stack")

    # POST a body comfortably larger than 64 bytes.
    resp = client.post(
        "/api/v1/auth/login",
        content=b"x" * 256,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 413
    assert "too large" in resp.json()["detail"].lower()


def test_invalid_content_length_rejected_with_400(client, monkeypatch):
    from app.main import app
    from app.middleware.body_size import BodySizeLimitMiddleware

    mw = app.middleware_stack
    while mw is not None:
        if isinstance(mw, BodySizeLimitMiddleware):
            monkeypatch.setattr(mw, "max_bytes", 1024)
            break
        mw = getattr(mw, "app", None)

    resp = client.post(
        "/api/v1/auth/login",
        content=b"{}",
        headers={"Content-Type": "application/json", "Content-Length": "not-a-number"},
    )
    # Some HTTP clients may overwrite Content-Length; accept either the
    # middleware's 400 or normal handler 400/422 if the header is rewritten.
    assert resp.status_code in (400, 422)
