from unittest.mock import MagicMock, patch

import pytest

from app.repository.exceptions import ResourceConflictError, ResourceNotFoundError
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.services.profile import ProfileService


class TestProfileServiceCreate:
    def test_create_delegates_to_repository(self):
        db = MagicMock()
        payload = ProfileCreate(
            firstname="A",
            lastname="B",
            username="ab_user",
            contact_email="a@b.com",
        )
        expected = MagicMock()

        with patch(
            "app.services.profile.create_profile", return_value=expected
        ) as create_fn:
            result = ProfileService.create(db, 5, payload)

        create_fn.assert_called_once_with(db, 5, payload)
        assert result is expected

    def test_create_propagates_not_found(self):
        db = MagicMock()
        payload = ProfileCreate(
            firstname="A",
            lastname="B",
            username="ab_user",
            contact_email="a@b.com",
        )
        with (
            patch(
                "app.services.profile.create_profile",
                side_effect=ResourceNotFoundError("User not found"),
            ),
            pytest.raises(ResourceNotFoundError, match="User not found"),
        ):
            ProfileService.create(db, 99, payload)

    def test_create_propagates_conflict(self):
        db = MagicMock()
        payload = ProfileCreate(
            firstname="A",
            lastname="B",
            username="ab_user",
            contact_email="a@b.com",
        )
        with (
            patch(
                "app.services.profile.create_profile",
                side_effect=ResourceConflictError("Profile already exists"),
            ),
            pytest.raises(ResourceConflictError, match="Profile already exists"),
        ):
            ProfileService.create(db, 1, payload)


class TestProfileServiceRead:
    def test_get_delegates(self):
        db = MagicMock()
        profile = MagicMock()
        with patch(
            "app.services.profile.get_profile", return_value=profile
        ) as get_fn:
            assert ProfileService.get(db, 3) is profile
        get_fn.assert_called_once_with(db, 3)

    def test_get_or_raise_delegates(self):
        db = MagicMock()
        profile = MagicMock()
        with patch(
            "app.services.profile.get_profile_or_raise", return_value=profile
        ) as get_fn:
            assert ProfileService.get_or_raise(db, 3) is profile
        get_fn.assert_called_once_with(db, 3)

    def test_get_by_username_delegates(self):
        db = MagicMock()
        profile = MagicMock()
        with patch(
            "app.services.profile.get_profile_by_username", return_value=profile
        ) as get_fn:
            assert ProfileService.get_by_username(db, "alpha") is profile
        get_fn.assert_called_once_with(db, "alpha")


class TestProfileServiceUpdate:
    def test_update_delegates(self):
        db = MagicMock()
        updates = ProfileUpdate(firstname="New")
        expected = MagicMock()
        with patch(
            "app.services.profile.update_profile", return_value=expected
        ) as update_fn:
            result = ProfileService.update(db, 7, updates)
        update_fn.assert_called_once_with(db, 7, updates)
        assert result is expected


class TestProfileServiceDelete:
    def test_delete_delegates(self):
        db = MagicMock()
        with patch("app.services.profile.delete_profile") as delete_fn:
            ProfileService.delete(db, 2)
        delete_fn.assert_called_once_with(db, 2)
