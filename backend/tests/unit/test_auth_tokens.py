from datetime import UTC, datetime, timedelta

import jwt

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    verify_token,
)
from app.core.settings import settings


class TestTokenCreation:
    def test_create_access_token_contains_expected_claims(self):
        token = create_access_token({"sub": "123"})
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        assert payload["sub"] == "123"
        assert payload["type"] == "access"

    def test_create_refresh_token_contains_expected_claims(self):
        token = create_refresh_token({"sub": "123"})
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        assert payload["sub"] == "123"
        assert payload["type"] == "refresh"

    def test_create_reset_token_contains_expected_claims(self):
        token = create_reset_token({"sub": "123"})
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        assert payload["sub"] == "123"
        assert payload["type"] == "reset"


class TestVerifyToken:
    def test_returns_payload_for_valid_token(self):
        token = create_access_token({"sub": "42"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_returns_none_when_sub_claim_missing(self):
        token = jwt.encode(
            {
                "type": "access",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        assert verify_token(token) is None

    def test_returns_none_for_invalid_signature(self):
        token = jwt.encode(
            {
                "sub": "42",
                "type": "access",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            "not_the_real_secret_key_used_by_app",
            algorithm=settings.algorithm,
        )
        assert verify_token(token) is None
