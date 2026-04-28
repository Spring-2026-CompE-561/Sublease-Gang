from unittest.mock import MagicMock, patch

from app.services.listing import ListingService


class TestListingService:
    def test_create_delegates_to_repository(self):
        db = MagicMock()
        payload = MagicMock()
        expected = MagicMock()

        with patch("app.services.listing.create_listing", return_value=expected) as mocked:
            result = ListingService.create(db, host_id=7, payload=payload)

        mocked.assert_called_once_with(db, 7, payload)
        assert result is expected

    def test_search_delegates_to_repository(self):
        db = MagicMock()
        expected = (2, [MagicMock(), MagicMock()])

        with patch("app.services.listing.search_listings", return_value=expected) as mocked:
            result = ListingService.search(db, min_price=500, max_price=1500, limit=10)

        mocked.assert_called_once_with(db, min_price=500, max_price=1500, limit=10)
        assert result == expected

    def test_update_delegates_to_repository(self):
        db = MagicMock()
        updates = MagicMock()
        expected = MagicMock()

        with patch("app.services.listing.update_listing", return_value=expected) as mocked:
            result = ListingService.update(db, listing_id=12, host_id=3, updates=updates)

        mocked.assert_called_once_with(db, 12, 3, updates)
        assert result is expected

    def test_delete_delegates_to_repository(self):
        db = MagicMock()

        with patch("app.services.listing.delete_listing") as mocked:
            ListingService.delete(db, listing_id=12, host_id=3)

        mocked.assert_called_once_with(db, 12, 3)
