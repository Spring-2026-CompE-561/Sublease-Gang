from datetime import UTC

from app.core.dependencies import get_current_user
from app.main import app


class TestSearchListings:
    def test_empty(self, client):
        resp = client.get("/api/v1/listings/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_returns_listings(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, price=500)
        make_listing(user.id, price=1500)
        resp = client.get("/api/v1/listings/")
        data = resp.json()
        assert data["count"] == 2
        assert len(data["results"]) == 2

    def test_price_filter(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, price=500)
        make_listing(user.id, price=1500)
        resp = client.get("/api/v1/listings/", params={"min_price": 1000})
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["price"] == 1500.0

    def test_max_price_filter(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, price=500)
        make_listing(user.id, price=1500)
        resp = client.get("/api/v1/listings/", params={"max_price": 1000})
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["price"] == 500.0

    def test_location_filter(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, location="New York")
        make_listing(user.id, location="Chicago")
        resp = client.get("/api/v1/listings/", params={"location": "New York"})
        data = resp.json()
        assert data["count"] == 1

    def test_room_type_filter(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, room_type="single")
        make_listing(user.id, room_type="double")
        resp = client.get("/api/v1/listings/", params={"room_type": "single"})
        data = resp.json()
        assert data["count"] == 1

    def test_college_id_filter(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, college_id=1)
        make_listing(user.id, college_id=2)
        resp = client.get("/api/v1/listings/", params={"college_id": 1})
        data = resp.json()
        assert data["count"] == 1

    def test_min_sqft_filter(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, sqft=400)
        make_listing(user.id, sqft=800)
        resp = client.get("/api/v1/listings/", params={"min_sqft": 600})
        data = resp.json()
        assert data["count"] == 1

    def test_max_sqft_filter(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, sqft=400)
        make_listing(user.id, sqft=800)
        resp = client.get("/api/v1/listings/", params={"max_sqft": 600})
        data = resp.json()
        assert data["count"] == 1

    def test_date_range_filter(self, client, make_user, make_listing):
        from datetime import datetime

        user = make_user()
        make_listing(
            user.id,
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 2, 1, tzinfo=UTC),
        )
        make_listing(
            user.id,
            start_date=datetime(2026, 6, 1, tzinfo=UTC),
            end_date=datetime(2026, 7, 1, tzinfo=UTC),
        )
        resp = client.get(
            "/api/v1/listings/",
            params={
                "start_date": "2026-05-01T00:00:00Z",
                "end_date": "2026-08-01T00:00:00Z",
            },
        )
        data = resp.json()
        assert data["count"] == 1

    def test_pagination(self, client, make_user, make_listing):
        user = make_user()
        for _ in range(5):
            make_listing(user.id)
        resp = client.get("/api/v1/listings/", params={"limit": 2, "offset": 0})
        data = resp.json()
        assert data["count"] == 5
        assert len(data["results"]) == 2

    def test_pagination_offset(self, client, make_user, make_listing):
        user = make_user()
        for _ in range(5):
            make_listing(user.id)
        resp = client.get("/api/v1/listings/", params={"limit": 2, "offset": 4})
        data = resp.json()
        assert len(data["results"]) == 1


class TestGetListing:
    def test_found(self, client, make_user, make_listing):
        user = make_user()
        listing = make_listing(user.id)
        resp = client.get(f"/api/v1/listings/{listing.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == listing.id

    def test_not_found(self, client):
        resp = client.get("/api/v1/listings/9999")
        assert resp.status_code == 404


class TestGetFilters:
    def test_empty_db(self, client):
        resp = client.get("/api/v1/listings/filters")
        assert resp.status_code == 200
        data = resp.json()
        assert data["room_types"] == []
        assert data["colleges"] == []

    def test_with_data(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, room_type="single", college_id=1, price=500, sqft=400)
        make_listing(user.id, room_type="double", college_id=2, price=1500, sqft=800)
        resp = client.get("/api/v1/listings/filters")
        data = resp.json()
        assert set(data["room_types"]) == {"single", "double"}
        assert data["price_min"] == 500.0
        assert data["price_max"] == 1500.0
        assert data["sqft_min"] == 400
        assert data["sqft_max"] == 800


class TestUpdateListing:
    def test_success(self, client, make_user, make_listing):
        user = make_user()
        listing = make_listing(user.id, title="Old Title")
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.put(
                f"/api/v1/listings/{listing.id}",
                json={"title": "New Title"},
            )
            assert resp.status_code == 200
            assert resp.json()["title"] == "New Title"
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_not_found(self, client, make_user):
        user = make_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.put("/api/v1/listings/9999", json={"title": "X"})
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_requires_auth(self, client):
        resp = client.put("/api/v1/listings/1", json={"title": "X"})
        assert resp.status_code == 401


class TestDeleteListing:
    def test_success(self, client, make_user, make_listing):
        user = make_user()
        listing = make_listing(user.id)
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.delete(f"/api/v1/listings/{listing.id}")
            assert resp.status_code == 204
            assert client.get(f"/api/v1/listings/{listing.id}").status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_not_found(self, client, make_user):
        user = make_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.delete("/api/v1/listings/9999")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_requires_auth(self, client):
        resp = client.delete("/api/v1/listings/1")
        assert resp.status_code == 401


class TestCreateListing:
    def test_requires_auth(self, client):
        resp = client.post(
            "/api/v1/listings/",
            json={
                "title": "T",
                "description": "D",
                "price": 100,
                "location": "L",
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-02-01T00:00:00Z",
                "latitude": 40.0,
                "longitude": -74.0,
            },
        )
        assert resp.status_code == 401

    def test_success(self, client, make_user):
        user = make_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            resp = client.post(
                "/api/v1/listings/",
                json={
                    "title": "My Listing",
                    "description": "A great place",
                    "price": 1000,
                    "location": "Test City",
                    "start_date": "2026-01-01T00:00:00Z",
                    "end_date": "2026-02-01T00:00:00Z",
                    "latitude": 40.0,
                    "longitude": -74.0,
                },
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["title"] == "My Listing"
            assert data["host_id"] == user.id
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestListingOwnershipWithAuth:
    def _register_and_login(self, client, *, email: str, username: str, password: str):
        client.post(
            "/api/v1/auth/signup",
            json={"email": email, "username": username, "password": password},
        )
        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_listing(self, client, headers, title: str):
        resp = client.post(
            "/api/v1/listings/",
            headers=headers,
            json={
                "title": title,
                "description": "Owned listing",
                "price": 1200,
                "location": "Campus",
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-02-01T00:00:00Z",
                "latitude": 40.0,
                "longitude": -74.0,
            },
        )
        assert resp.status_code == 201
        return resp.json()["id"]

    def test_non_owner_cannot_update_listing(self, client):
        owner_headers = self._register_and_login(
            client,
            email="owner@example.com",
            username="owneruser",
            password="password123",
        )
        listing_id = self._create_listing(client, owner_headers, "Owner Listing")

        other_headers = self._register_and_login(
            client,
            email="other@example.com",
            username="otheruser",
            password="password123",
        )
        resp = client.put(
            f"/api/v1/listings/{listing_id}",
            headers=other_headers,
            json={"title": "Hijacked Title"},
        )
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Not allowed to modify this listing"

    def test_non_owner_cannot_delete_listing(self, client):
        owner_headers = self._register_and_login(
            client,
            email="owner2@example.com",
            username="owneruser2",
            password="password123",
        )
        listing_id = self._create_listing(client, owner_headers, "Owner Listing")

        other_headers = self._register_and_login(
            client,
            email="other2@example.com",
            username="otheruser2",
            password="password123",
        )
        resp = client.delete(f"/api/v1/listings/{listing_id}", headers=other_headers)
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Not allowed to delete this listing"
