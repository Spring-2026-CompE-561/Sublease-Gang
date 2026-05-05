"""Production-mode safety checks for the Settings model."""

import pytest

from app.core.settings import Settings


def _set_env(monkeypatch, **env):
    for k in ("ENVIRONMENT", "SECRET_KEY", "CORS_ORIGINS"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)


def test_production_rejects_wildcard_cors(monkeypatch):
    _set_env(
        monkeypatch,
        ENVIRONMENT="production",
        SECRET_KEY="x" * 64,
        CORS_ORIGINS='["*"]',
    )
    with pytest.raises(Exception, match="Wildcard"):
        Settings(_env_file=None)


def test_production_rejects_http_origin(monkeypatch):
    _set_env(
        monkeypatch,
        ENVIRONMENT="production",
        SECRET_KEY="x" * 64,
        CORS_ORIGINS='["http://example.com"]',
    )
    with pytest.raises(Exception, match="http://"):
        Settings(_env_file=None)


def test_production_rejects_localhost_origin(monkeypatch):
    _set_env(
        monkeypatch,
        ENVIRONMENT="production",
        SECRET_KEY="x" * 64,
        CORS_ORIGINS='["https://localhost:3000"]',
    )
    with pytest.raises(Exception, match="localhost"):
        Settings(_env_file=None)


def test_production_accepts_https_origin(monkeypatch):
    _set_env(
        monkeypatch,
        ENVIRONMENT="production",
        SECRET_KEY="x" * 64,
        CORS_ORIGINS='["https://app.example.com"]',
    )
    s = Settings(_env_file=None)
    assert s.cors_origins == ["https://app.example.com"]


def test_development_keeps_localhost_default(monkeypatch):
    _set_env(monkeypatch, ENVIRONMENT="development")
    s = Settings(_env_file=None)
    # localhost is fine in dev — no validator should fire.
    assert "localhost" in s.cors_origins[0]
