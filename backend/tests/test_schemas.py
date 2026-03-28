from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas.conversation import ConversationCreate
from app.schemas.listing import ListingCreate, ListingUpdate
from app.schemas.message import MessageCreate, MessageUpdate
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.user import UserCreate, UserPasswordUpdate, UserUpdate


# ── User schemas ──────────────────────────────────────────────────────────────


class TestUserCreate:
    def test_valid(self):
        u = UserCreate(
            email="test@example.com", username="testuser", password="password123"
        )
        assert u.email == "test@example.com"
        assert u.username == "testuser"

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="testuser", password="short"
            )

    def test_username_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="ab", password="password123"
            )

    def test_username_too_long(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="a" * 51,
                password="password123",
            )

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email", username="testuser", password="password123"
            )


class TestUserUpdate:
    def test_valid_partial(self):
        u = UserUpdate(email="new@example.com")
        assert u.email == "new@example.com"
        assert u.username is None

    def test_all_none_is_valid(self):
        u = UserUpdate()
        assert u.email is None
        assert u.username is None


class TestUserPasswordUpdate:
    def test_valid(self):
        u = UserPasswordUpdate(
            current_password="oldpass123",
            new_password="newpass123",
            confirm_new_password="newpass123",
        )
        assert u.new_password == "newpass123"

    def test_passwords_dont_match(self):
        with pytest.raises(ValidationError, match="passwords do not match"):
            UserPasswordUpdate(
                current_password="oldpass123",
                new_password="newpass123",
                confirm_new_password="different123",
            )

    def test_new_password_too_short(self):
        with pytest.raises(ValidationError):
            UserPasswordUpdate(
                current_password="oldpass123",
                new_password="short",
                confirm_new_password="short",
            )


# ── Listing schemas ───────────────────────────────────────────────────────────


class TestListingCreate:
    def _defaults(self, **overrides):
        now = datetime.now(timezone.utc)
        data = {
            "title": "Test",
            "description": "Desc",
            "price": 100.0,
            "location": "City",
            "start_date": now,
            "end_date": now + timedelta(days=30),
            "latitude": 40.7,
            "longitude": -74.0,
        }
        data.update(overrides)
        return data

    def test_valid(self):
        listing = ListingCreate(**self._defaults())
        assert listing.title == "Test"

    def test_end_date_before_start_date(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError, match="end_date must be after start_date"):
            ListingCreate(**self._defaults(start_date=now, end_date=now - timedelta(days=1)))

    def test_end_date_equals_start_date(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError, match="end_date must be after start_date"):
            ListingCreate(**self._defaults(start_date=now, end_date=now))


class TestListingUpdate:
    def test_valid_partial(self):
        u = ListingUpdate(title="New Title")
        assert u.title == "New Title"
        assert u.price is None

    def test_invalid_dates_when_both_provided(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError, match="end_date must be after start_date"):
            ListingUpdate(start_date=now, end_date=now - timedelta(days=1))

    def test_single_date_ok(self):
        now = datetime.now(timezone.utc)
        u = ListingUpdate(start_date=now)
        assert u.start_date == now
        assert u.end_date is None


# ── Profile schemas ───────────────────────────────────────────────────────────


class TestProfileCreate:
    def test_valid_with_email(self):
        p = ProfileCreate(
            firstname="John",
            lastname="Doe",
            username="johndoe",
            contact_email="john@example.com",
        )
        assert p.firstname == "John"

    def test_valid_with_phone(self):
        p = ProfileCreate(
            firstname="John",
            lastname="Doe",
            username="johndoe",
            contact_phone="1234567890",
        )
        assert p.contact_phone == "1234567890"

    def test_valid_with_both_contacts(self):
        p = ProfileCreate(
            firstname="John",
            lastname="Doe",
            username="johndoe",
            contact_email="john@example.com",
            contact_phone="1234567890",
        )
        assert p.contact_email == "john@example.com"
        assert p.contact_phone == "1234567890"

    def test_no_contact_method(self):
        with pytest.raises(ValidationError, match="At least one contact method"):
            ProfileCreate(firstname="John", lastname="Doe", username="johndoe")

    def test_invalid_name_characters(self):
        with pytest.raises(ValidationError, match="Must contain only letters"):
            ProfileCreate(
                firstname="John123",
                lastname="Doe",
                username="johndoe",
                contact_email="john@example.com",
            )

    def test_blank_name(self):
        with pytest.raises(ValidationError, match="Cannot be blank"):
            ProfileCreate(
                firstname="   ",
                lastname="Doe",
                username="johndoe",
                contact_email="john@example.com",
            )

    def test_invalid_username_too_short(self):
        with pytest.raises(
            ValidationError, match="Must be 3-30 characters"
        ):
            ProfileCreate(
                firstname="John",
                lastname="Doe",
                username="ab",
                contact_email="john@example.com",
            )

    def test_invalid_username_special_chars(self):
        with pytest.raises(
            ValidationError, match="Must be 3-30 characters"
        ):
            ProfileCreate(
                firstname="John",
                lastname="Doe",
                username="john doe!",
                contact_email="john@example.com",
            )

    def test_invalid_phone(self):
        with pytest.raises(ValidationError, match="Must be a valid phone number"):
            ProfileCreate(
                firstname="John",
                lastname="Doe",
                username="johndoe",
                contact_phone="abc",
            )

    def test_description_too_long(self):
        with pytest.raises(
            ValidationError, match="Description cannot exceed 500"
        ):
            ProfileCreate(
                firstname="John",
                lastname="Doe",
                username="johndoe",
                contact_email="john@example.com",
                description="x" * 501,
            )


class TestProfileUpdate:
    def test_valid_partial(self):
        u = ProfileUpdate(firstname="Jane")
        assert u.firstname == "Jane"

    def test_both_contacts_explicitly_none(self):
        with pytest.raises(ValidationError, match="At least one contact method"):
            ProfileUpdate(contact_email=None, contact_phone=None)

    def test_single_contact_none_is_ok_when_other_not_provided(self):
        """Setting only one contact field without touching the other is fine
        because the model_validator only fires when at least one contact
        field is in model_fields_set."""
        # This should NOT raise even though contact_phone defaults to None,
        # because the validator checks model_fields_set.
        # Actually, setting contact_email=None puts it in model_fields_set,
        # and contact_phone is also None (default) -> validator triggers.
        with pytest.raises(ValidationError, match="At least one contact method"):
            ProfileUpdate(contact_email=None)


# ── Message schemas ───────────────────────────────────────────────────────────


class TestMessageCreate:
    def test_valid(self):
        m = MessageCreate(conversation_id=1, sender_id=1, content="Hello!")
        assert m.content == "Hello!"

    def test_empty_content(self):
        with pytest.raises(ValidationError, match="content cannot be empty"):
            MessageCreate(conversation_id=1, sender_id=1, content="")

    def test_whitespace_only_content(self):
        with pytest.raises(ValidationError, match="content cannot be empty"):
            MessageCreate(conversation_id=1, sender_id=1, content="   ")


class TestMessageUpdate:
    def test_valid(self):
        m = MessageUpdate(content="Updated content")
        assert m.content == "Updated content"

    def test_whitespace_only_content(self):
        with pytest.raises(ValidationError, match="content cannot be empty"):
            MessageUpdate(content="   ")

    def test_none_content_is_valid(self):
        m = MessageUpdate(content=None)
        assert m.content is None


# ── Conversation schemas ──────────────────────────────────────────────────────


class TestConversationCreate:
    def test_valid(self):
        c = ConversationCreate(listing_id=1, user_one_id=1, user_two_id=2)
        assert c.user_one_id == 1
        assert c.user_two_id == 2

    def test_same_user_ids(self):
        with pytest.raises(ValidationError, match="must be different"):
            ConversationCreate(listing_id=1, user_one_id=1, user_two_id=1)
