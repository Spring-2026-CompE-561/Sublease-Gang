import pytest
from fastapi import HTTPException

from app.core.auth import create_access_token
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
