from unittest.mock import MagicMock, patch

from app.services.conversation import ConversationService
from app.services.message import MessageService


class TestMessageService:
    def test_list_by_conversation_delegates_to_repository(self):
        db = MagicMock()
        expected = [MagicMock(), MagicMock()]

        with patch(
            "app.services.message.get_messages_by_conversation",
            return_value=expected,
        ) as mocked:
            result = MessageService.list_by_conversation(
                db,
                conversation_id=22,
                user_id=5,
                skip=10,
                limit=20,
            )

        mocked.assert_called_once_with(db, 22, user_id=5, skip=10, limit=20)
        assert result == expected

    def test_update_delegates_to_repository(self):
        db = MagicMock()
        payload = MagicMock()
        expected = MagicMock()

        with patch("app.services.message.update_message", return_value=expected) as mocked:
            result = MessageService.update(db, message_id=3, user_id=9, payload=payload)

        mocked.assert_called_once_with(db, 3, 9, payload)
        assert result is expected


class TestConversationService:
    def test_get_or_create_returns_existing_conversation(self):
        db = MagicMock()
        existing = MagicMock()

        with (
            patch(
                "app.services.conversation.get_conversation_by_listing_and_users",
                return_value=existing,
            ) as get_existing,
            patch("app.services.conversation.create_conversation") as create_new,
        ):
            result = ConversationService.get_or_create(
                db,
                listing_id=12,
                user_a_id=1,
                user_b_id=2,
            )

        get_existing.assert_called_once_with(db, 12, 1, 2)
        create_new.assert_not_called()
        assert result is existing

    def test_get_or_create_creates_when_missing(self):
        db = MagicMock()
        created = MagicMock()

        with (
            patch(
                "app.services.conversation.get_conversation_by_listing_and_users",
                return_value=None,
            ) as get_existing,
            patch(
                "app.services.conversation.create_conversation",
                return_value=created,
            ) as create_new,
        ):
            result = ConversationService.get_or_create(
                db,
                listing_id=12,
                user_a_id=1,
                user_b_id=2,
            )

        get_existing.assert_called_once_with(db, 12, 1, 2)
        create_new.assert_called_once()
        created_payload = create_new.call_args.args[1]
        assert created_payload.listing_id == 12
        assert created_payload.user_one_id == 1
        assert created_payload.user_two_id == 2
        assert result is created
