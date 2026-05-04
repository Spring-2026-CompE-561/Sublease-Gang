from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
)
from app.core.dependencies import get_current_user


class TestGetCurrentUser:
    def test_returns_user_for_valid_token(self, db_session, make_user):
        user = make_user()
        token = create_access_token({"sub": str(user.id)})

        resolved = get_current_user(token=token, db=db_session)

        assert resolved.id == user.id
        assert resolved.email == user.email

    def test_raises_for_invalid_token(self, db_session):
        with pytest.raises(HTTPException, match="Invalid or expired token"):
            get_current_user(token="not.a.valid.jwt", db=db_session)

    def test_raises_for_missing_user(self, db_session):
        token = create_access_token({"sub": "99999"})

        with pytest.raises(HTTPException, match="User not found"):
            get_current_user(token=token, db=db_session)

    def test_raises_for_disabled_user(self, db_session, make_user):
        user = make_user()
        user.account_disabled = True
        db_session.commit()
        token = create_access_token({"sub": str(user.id)})

        with pytest.raises(HTTPException, match="Account disabled"):
            get_current_user(token=token, db=db_session)

    def test_rejects_refresh_token(self, db_session, make_user):
        user = make_user()
        token = create_refresh_token({"sub": str(user.id)})

        with pytest.raises(HTTPException, match="Invalid or expired token"):
            get_current_user(token=token, db=db_session)

    def test_rejects_reset_token(self, db_session, make_user):
        user = make_user()
        token = create_reset_token({"sub": str(user.id)})

        with pytest.raises(HTTPException, match="Invalid or expired token"):
            get_current_user(token=token, db=db_session)

    def test_rejects_token_issued_before_password_change(
        self, db_session, make_user
    ):
        user = make_user()
        token = create_access_token({"sub": str(user.id)})
        # Simulate the user changing their password after the token was issued.
        user.password_changed_at = datetime.now(UTC) + timedelta(days=1)
        db_session.commit()

        with pytest.raises(HTTPException, match="Invalid or expired token"):
            get_current_user(token=token, db=db_session)

    def test_rejects_token_without_iat(self, db_session, make_user):
        import jwt

        from app.core.auth import ALGORITHM, SECRET_KEY

        user = make_user()
        # Hand-craft a token with the right type/sub but no iat claim.
        token = jwt.encode(
            {
                "sub": str(user.id),
                "type": "access",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        with pytest.raises(HTTPException, match="Invalid or expired token"):
            get_current_user(token=token, db=db_session)
