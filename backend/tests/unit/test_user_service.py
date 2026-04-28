from unittest.mock import MagicMock, patch

import pytest

from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.services.user import UserService


class TestUserServiceRegister:
    def test_register_raises_when_email_exists(self):
        db = MagicMock()
        payload = MagicMock(email="taken@example.com", username="newuser")

        with (
            patch("app.services.user.get_user_by_email", return_value=MagicMock()),
            patch("app.services.user.get_user_by_username") as by_username,
            patch("app.services.user.create_user") as create_user,
            pytest.raises(ResourceConflictError, match="Email already registered"),
        ):
            UserService.register(db, payload)

        by_username.assert_not_called()
        create_user.assert_not_called()

    def test_register_raises_when_username_exists(self):
        db = MagicMock()
        payload = MagicMock(email="free@example.com", username="taken")

        with (
            patch("app.services.user.get_user_by_email", return_value=None),
            patch("app.services.user.get_user_by_username", return_value=MagicMock()),
            patch("app.services.user.create_user") as create_user,
            pytest.raises(ResourceConflictError, match="Username already taken"),
        ):
            UserService.register(db, payload)

        create_user.assert_not_called()


class TestUserServiceAuthenticate:
    def test_authenticate_raises_for_missing_user(self):
        db = MagicMock()
        with (
            patch("app.services.user.get_user_by_email", return_value=None),
            pytest.raises(ResourceNotFoundError, match="Invalid email or password"),
        ):
            UserService.authenticate(db, "missing@example.com", "password123")

    def test_authenticate_raises_for_disabled_user(self):
        db = MagicMock()
        user = MagicMock(id=4, account_disabled=True, password_hash="hashed")

        with (
            patch("app.services.user.get_user_by_email", return_value=user),
            patch("app.services.user.verify_password", return_value=True),
            pytest.raises(ResourceNotFoundError, match="Account is disabled"),
        ):
            UserService.authenticate(db, "disabled@example.com", "password123")

    def test_authenticate_returns_token_payload(self):
        db = MagicMock()
        user = MagicMock(id=9, account_disabled=False, password_hash="hashed")

        with (
            patch("app.services.user.get_user_by_email", return_value=user),
            patch("app.services.user.verify_password", return_value=True),
            patch("app.services.user.create_access_token", return_value="access_tok"),
            patch("app.services.user.create_refresh_token", return_value="refresh_tok"),
        ):
            result = UserService.authenticate(db, "ok@example.com", "password123")

        assert result["access_token"] == "access_tok"
        assert result["refresh_token"] == "refresh_tok"
        assert result["token_type"] == "bearer"
