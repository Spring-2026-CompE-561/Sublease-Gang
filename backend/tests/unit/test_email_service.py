from app.services import email as email_service


def test_skips_send_when_api_key_missing(monkeypatch, caplog):
    """No key configured ⇒ skip send, log warning, return False, don't raise."""
    monkeypatch.setattr(email_service.settings, "resend_api_key", "")

    sent: list[dict] = []

    def fake_send(params):
        sent.append(params)
        return {"id": "should-not-happen"}

    monkeypatch.setattr(email_service.resend.Emails, "send", fake_send)
    with caplog.at_level("WARNING", logger="app.services.email"):
        result = email_service.send_password_reset_email(
            "user@example.com", "http://localhost:3000/reset-password?token=abc",
        )
    assert result is False
    assert sent == []
    assert any("RESEND_API_KEY" in r.getMessage() for r in caplog.records)


def test_sends_with_correct_params_when_configured(monkeypatch):
    """A configured key ⇒ resend.Emails.send is called with from/to/subject."""
    monkeypatch.setattr(email_service.settings, "resend_api_key", "re_test_key")
    monkeypatch.setattr(
        email_service.settings, "resend_from_email", "noreply@example.com",
    )

    captured: dict = {}

    def fake_send(params):
        captured.update(params)
        return {"id": "fake-message-id"}

    monkeypatch.setattr(email_service.resend.Emails, "send", fake_send)
    reset_url = "http://localhost:3000/reset-password?token=jwt.token.value"
    result = email_service.send_password_reset_email(
        "user@example.com", reset_url,
    )
    assert result is True
    assert captured["from"] == "noreply@example.com"
    assert captured["to"] == ["user@example.com"]
    assert reset_url in captured["text"]
    # The HTML body must escape the URL inside the href attribute.
    # (We pass a benign URL here, so it remains unchanged after escape().)
    assert reset_url in captured["html"]


def test_returns_false_when_resend_raises(monkeypatch, caplog):
    """A Resend SDK error must be caught and turned into False — never raised."""
    monkeypatch.setattr(email_service.settings, "resend_api_key", "re_test_key")

    def boom(_params):
        raise email_service.ResendError(
            code=500,
            error_type="api_error",
            message="boom",
            suggested_action="retry",
        )

    monkeypatch.setattr(email_service.resend.Emails, "send", boom)
    with caplog.at_level("ERROR", logger="app.services.email"):
        result = email_service.send_password_reset_email(
            "user@example.com", "http://localhost:3000/reset-password?token=x",
        )
    assert result is False
    assert any(
        "Failed to send password reset email" in r.getMessage()
        for r in caplog.records
    )
