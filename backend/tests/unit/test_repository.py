from datetime import UTC, datetime, timedelta

import pytest

from app.repository.exceptions import (
    PermissionDeniedError,
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.repository.message import (
    create_message,
    delete_message,
    get_message,
    get_message_or_raise,
    get_messages_by_conversation,
    update_message,
)
from app.repository.profile import (
    create_profile,
    delete_profile,
    get_profile,
    get_profile_by_username,
    get_profile_or_raise,
    update_profile,
)
from app.repository.token import (
    create_token,
    delete_token,
    delete_tokens_by_user,
    get_token_by_access,
    get_token_by_id,
    get_token_by_refresh,
    get_tokens_by_user,
)
from app.repository.user import (
    create_user,
    delete_user,
    disable_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_password,
    update_user,
)
from app.schemas.message import MessageCreate, MessageUpdate
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.token import TokenCreate
from app.schemas.user import UserCreate, UserUpdate

# ── User Repository ──────────────────────────────────────────────────────────


class TestUserRepository:
    def test_create_user(self, db_session):
        schema = UserCreate(
            email="new@example.com",
            username="newuser",
            password="password123",
        )
        user = create_user(db_session, schema)
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert user.password_hash != "password123"

    def test_get_user_by_id(self, db_session, make_user):
        user = make_user()
        found = get_user_by_id(db_session, user.id)
        assert found is not None
        assert found.id == user.id

    def test_get_user_by_id_not_found(self, db_session):
        assert get_user_by_id(db_session, 9999) is None

    def test_get_user_by_email(self, db_session, make_user):
        user = make_user(email="findme@example.com")
        found = get_user_by_email(db_session, "findme@example.com")
        assert found is not None
        assert found.id == user.id

    def test_get_user_by_email_not_found(self, db_session):
        assert get_user_by_email(db_session, "nonexistent@example.com") is None

    def test_get_user_by_username(self, db_session, make_user):
        user = make_user(username="findme")
        found = get_user_by_username(db_session, "findme")
        assert found is not None
        assert found.id == user.id

    def test_get_user_by_username_not_found(self, db_session):
        assert get_user_by_username(db_session, "nobody") is None

    def test_update_user(self, db_session, make_user):
        user = make_user()
        updates = UserUpdate(email="updated@example.com")
        updated = update_user(db_session, user, updates)
        assert updated.email == "updated@example.com"

    def test_update_password(self, db_session, make_user):
        user = make_user()
        old_hash = user.password_hash
        updated = update_password(db_session, user, "new_hashed_password")
        assert updated.password_hash == "new_hashed_password"
        assert updated.password_hash != old_hash

    def test_disable_user(self, db_session, make_user):
        user = make_user()
        disabled = disable_user(db_session, user)
        assert disabled.account_disabled is True

    def test_delete_user(self, db_session, make_user):
        user = make_user()
        uid = user.id
        delete_user(db_session, user)
        assert get_user_by_id(db_session, uid) is None


# ── Token Repository ─────────────────────────────────────────────────────────


class TestTokenRepository:
    def _expiration(self):
        return datetime.now(UTC) + timedelta(hours=1)

    def test_create_token(self, db_session, make_user):
        user = make_user()
        token = create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="access_abc",
            refresh_token="refresh_xyz",
            expiration_time=self._expiration(),
        )
        assert token.id is not None
        assert token.access_token == "access_abc"
        assert token.refresh_token == "refresh_xyz"
        assert token.user_id == user.id

    def test_create_token_user_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="User not found"):
            create_token(
                db_session,
                TokenCreate(user_id=9999),
                access_token="x",
                expiration_time=self._expiration(),
            )

    def test_get_token_by_id(self, db_session, make_user):
        user = make_user()
        token = create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="tok",
            expiration_time=self._expiration(),
        )
        found = get_token_by_id(db_session, token.id)
        assert found is not None
        assert found.id == token.id

    def test_get_token_by_access(self, db_session, make_user):
        user = make_user()
        create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="unique_access",
            expiration_time=self._expiration(),
        )
        found = get_token_by_access(db_session, "unique_access")
        assert found is not None
        assert found.access_token == "unique_access"

    def test_get_token_by_refresh(self, db_session, make_user):
        user = make_user()
        create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="a",
            refresh_token="unique_refresh",
            expiration_time=self._expiration(),
        )
        found = get_token_by_refresh(db_session, "unique_refresh")
        assert found is not None
        assert found.refresh_token == "unique_refresh"

    def test_get_tokens_by_user(self, db_session, make_user):
        user = make_user()
        exp = self._expiration()
        create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="t1",
            expiration_time=exp,
        )
        create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="t2",
            expiration_time=exp,
        )
        tokens = get_tokens_by_user(db_session, user.id)
        assert len(tokens) == 2

    def test_delete_token(self, db_session, make_user):
        user = make_user()
        token = create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="del",
            expiration_time=self._expiration(),
        )
        delete_token(db_session, token.id)
        assert get_token_by_id(db_session, token.id) is None

    def test_delete_token_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Token not found"):
            delete_token(db_session, 9999)

    def test_delete_tokens_by_user(self, db_session, make_user):
        user = make_user()
        exp = self._expiration()
        create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="t1",
            expiration_time=exp,
        )
        create_token(
            db_session,
            TokenCreate(user_id=user.id),
            access_token="t2",
            expiration_time=exp,
        )
        delete_tokens_by_user(db_session, user.id)
        assert len(get_tokens_by_user(db_session, user.id)) == 0


# ── Profile Repository ────────────────────────────────────────────────────────


class TestProfileRepository:
    def _profile_schema(self, **overrides):
        defaults = {
            "firstname": "John",
            "lastname": "Doe",
            "username": "johndoe",
            "contact_email": "john@example.com",
        }
        defaults.update(overrides)
        return ProfileCreate(**defaults)

    def test_create_profile(self, db_session, make_user):
        user = make_user()
        profile = create_profile(db_session, user.id, self._profile_schema())
        assert profile.user_id == user.id
        assert profile.firstname == "John"

    def test_create_profile_user_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="User not found"):
            create_profile(db_session, 9999, self._profile_schema())

    def test_create_profile_duplicate(self, db_session, make_user):
        user = make_user()
        create_profile(db_session, user.id, self._profile_schema())
        with pytest.raises(ResourceConflictError, match="Profile already exists"):
            create_profile(
                db_session,
                user.id,
                self._profile_schema(username="other_user"),
            )

    def test_create_profile_duplicate_username(self, db_session, make_user):
        user1 = make_user()
        user2 = make_user()
        create_profile(db_session, user1.id, self._profile_schema(username="taken"))
        with pytest.raises(ResourceConflictError, match="Username already taken"):
            create_profile(
                db_session,
                user2.id,
                self._profile_schema(username="taken"),
            )

    def test_get_profile(self, db_session, make_user):
        user = make_user()
        create_profile(db_session, user.id, self._profile_schema())
        profile = get_profile(db_session, user.id)
        assert profile is not None
        assert profile.firstname == "John"

    def test_get_profile_not_found(self, db_session):
        assert get_profile(db_session, 9999) is None

    def test_get_profile_or_raise_found(self, db_session, make_user):
        user = make_user()
        create_profile(db_session, user.id, self._profile_schema())
        profile = get_profile_or_raise(db_session, user.id)
        assert profile.user_id == user.id

    def test_get_profile_or_raise_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Profile not found"):
            get_profile_or_raise(db_session, 9999)

    def test_get_profile_by_username(self, db_session, make_user):
        user = make_user()
        create_profile(db_session, user.id, self._profile_schema())
        found = get_profile_by_username(db_session, "johndoe")
        assert found is not None
        assert found.username == "johndoe"

    def test_update_profile(self, db_session, make_user):
        user = make_user()
        create_profile(db_session, user.id, self._profile_schema())
        updated = update_profile(
            db_session,
            user.id,
            ProfileUpdate(firstname="Jane"),
        )
        assert updated.firstname == "Jane"

    def test_update_profile_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Profile not found"):
            update_profile(db_session, 9999, ProfileUpdate(firstname="Jane"))

    def test_update_profile_duplicate_username(self, db_session, make_user):
        user1 = make_user()
        user2 = make_user()
        create_profile(
            db_session,
            user1.id,
            self._profile_schema(username="alice"),
        )
        create_profile(
            db_session,
            user2.id,
            self._profile_schema(username="bob"),
        )
        with pytest.raises(ResourceConflictError, match="Username already taken"):
            update_profile(
                db_session,
                user2.id,
                ProfileUpdate(username="alice"),
            )

    def test_update_profile_removes_all_contacts(self, db_session, make_user):
        user = make_user()
        create_profile(
            db_session,
            user.id,
            self._profile_schema(contact_phone="1234567890"),
        )
        with pytest.raises(ValueError, match="At least one contact method"):
            update_profile(
                db_session,
                user.id,
                ProfileUpdate(contact_email=None, contact_phone=None),
            )

    def test_delete_profile(self, db_session, make_user):
        user = make_user()
        create_profile(db_session, user.id, self._profile_schema())
        delete_profile(db_session, user.id)
        assert get_profile(db_session, user.id) is None

    def test_delete_profile_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Profile not found"):
            delete_profile(db_session, 9999)


# ── Message Repository ────────────────────────────────────────────────────────


class TestMessageRepository:
    def _setup(self, make_user, make_listing, make_conversation):
        """Create two users, a listing, and a conversation for message tests."""
        user1 = make_user()
        user2 = make_user()
        listing = make_listing(user1.id)
        convo = make_conversation(listing.id, user1.id, user2.id)
        return user1, user2, convo

    def test_create_message(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        msg = create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="Hello!",
            ),
        )
        assert msg.id is not None
        assert msg.content == "Hello!"
        assert msg.sender_id == user1.id

    def test_create_message_user_not_found(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        _user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        with pytest.raises(ResourceNotFoundError, match="User not found"):
            create_message(
                db_session,
                MessageCreate(
                    conversation_id=convo.id,
                    sender_id=9999,
                    content="Hi",
                ),
            )

    def test_create_message_conversation_not_found(
        self,
        db_session,
        make_user,
    ):
        user = make_user()
        with pytest.raises(ResourceNotFoundError, match="Conversation not found"):
            create_message(
                db_session,
                MessageCreate(
                    conversation_id=9999,
                    sender_id=user.id,
                    content="Hi",
                ),
            )

    def test_create_message_not_participant(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        _user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        outsider = make_user()
        with pytest.raises(PermissionDeniedError, match="(?i)not a participant"):
            create_message(
                db_session,
                MessageCreate(
                    conversation_id=convo.id,
                    sender_id=outsider.id,
                    content="Hi",
                ),
            )

    def test_get_message(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        msg = create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="Test",
            ),
        )
        found = get_message(db_session, msg.id)
        assert found is not None
        assert found.id == msg.id

    def test_get_message_not_found(self, db_session):
        assert get_message(db_session, 9999) is None

    def test_get_message_or_raise_found(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        msg = create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="Test",
            ),
        )
        found = get_message_or_raise(db_session, msg.id)
        assert found.id == msg.id

    def test_get_message_or_raise_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Message not found"):
            get_message_or_raise(db_session, 9999)

    def test_get_messages_by_conversation(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="First",
            ),
        )
        create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user2.id,
                content="Second",
            ),
        )
        messages = get_messages_by_conversation(db_session, convo.id, user_id=user1.id)
        assert len(messages) == 2
        assert messages[0].content == "First"
        assert messages[1].content == "Second"

    def test_get_messages_by_conversation_with_skip(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        for i in range(5):
            create_message(
                db_session,
                MessageCreate(
                    conversation_id=convo.id,
                    sender_id=user1.id,
                    content=f"Msg {i}",
                ),
            )
        messages = get_messages_by_conversation(
            db_session, convo.id, user_id=user1.id, skip=2
        )
        assert len(messages) == 3
        assert messages[0].content == "Msg 2"

    def test_get_messages_by_conversation_with_limit(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        for i in range(5):
            create_message(
                db_session,
                MessageCreate(
                    conversation_id=convo.id,
                    sender_id=user1.id,
                    content=f"Msg {i}",
                ),
            )
        messages = get_messages_by_conversation(
            db_session, convo.id, user_id=user1.id, limit=2
        )
        assert len(messages) == 2
        assert messages[0].content == "Msg 0"
        assert messages[1].content == "Msg 1"

    def test_get_messages_by_conversation_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Conversation not found"):
            get_messages_by_conversation(db_session, 9999, user_id=1)

    def test_update_message(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        msg = create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="Original",
            ),
        )
        updated = update_message(
            db_session,
            msg.id,
            user1.id,
            MessageUpdate(content="Edited"),
        )
        assert updated.content == "Edited"

    def test_update_message_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Message not found"):
            update_message(
                db_session,
                9999,
                1,
                MessageUpdate(content="Edit"),
            )

    def test_update_message_wrong_sender(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        msg = create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="Mine",
            ),
        )
        with pytest.raises(PermissionDeniedError, match="Not allowed to modify"):
            update_message(
                db_session,
                msg.id,
                user2.id,
                MessageUpdate(content="Hacked"),
            )

    def test_delete_message(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, _user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        msg = create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="Bye",
            ),
        )
        mid = msg.id
        delete_message(db_session, mid, user1.id)
        assert get_message(db_session, mid) is None

    def test_delete_message_not_found(self, db_session):
        with pytest.raises(ResourceNotFoundError, match="Message not found"):
            delete_message(db_session, 9999, 1)

    def test_delete_message_wrong_sender(
        self,
        db_session,
        make_user,
        make_listing,
        make_conversation,
    ):
        user1, user2, convo = self._setup(
            make_user,
            make_listing,
            make_conversation,
        )
        msg = create_message(
            db_session,
            MessageCreate(
                conversation_id=convo.id,
                sender_id=user1.id,
                content="Mine",
            ),
        )
        with pytest.raises(PermissionDeniedError, match="Not allowed to delete"):
            delete_message(db_session, msg.id, user2.id)
