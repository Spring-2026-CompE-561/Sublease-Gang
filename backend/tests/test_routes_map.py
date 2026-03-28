class TestMapListings:
    def test_valid_bounds_empty(self, client):
        resp = client.get(
            "/api/v1/map/listings",
            params={"north": 41, "south": 40, "east": -73, "west": -75},
        )
        assert resp.status_code == 200
        assert resp.json()["results"] == []

    def test_returns_listings_in_bounds(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, latitude=40.7, longitude=-74.0)
        make_listing(user.id, latitude=35.0, longitude=-80.0)  # outside bounds
        resp = client.get(
            "/api/v1/map/listings",
            params={"north": 41, "south": 40, "east": -73, "west": -75},
        )
        results = resp.json()["results"]
        assert len(results) == 1
        assert results[0]["lat"] == 40.7

    def test_invalid_bounds_north_le_south(self, client):
        resp = client.get(
            "/api/v1/map/listings",
            params={"north": 30, "south": 40, "east": -73, "west": -75},
        )
        assert resp.status_code == 400

    def test_latitude_out_of_range(self, client):
        resp = client.get(
            "/api/v1/map/listings",
            params={"north": 100, "south": 40, "east": -73, "west": -75},
        )
        assert resp.status_code == 400

    def test_longitude_out_of_range(self, client):
        resp = client.get(
            "/api/v1/map/listings",
            params={"north": 41, "south": 40, "east": -73, "west": -200},
        )
        assert resp.status_code == 400

    def test_with_filters(self, client, make_user, make_listing):
        user = make_user()
        make_listing(user.id, latitude=40.7, longitude=-74.0, price=500)
        make_listing(user.id, latitude=40.8, longitude=-74.0, price=2000)
        resp = client.get(
            "/api/v1/map/listings",
            params={
                "north": 41,
                "south": 40,
                "east": -73,
                "west": -75,
                "max_price": 1000,
            },
        )
        results = resp.json()["results"]
        assert len(results) == 1
        assert results[0]["price"] == 500.0


class TestGeocode:
    def test_with_address(self, client):
        resp = client.get("/api/v1/map/geocode", params={"address": "New York"})
        assert resp.status_code == 200
        assert resp.json()["results"] == []

    def test_without_address(self, client):
        resp = client.get("/api/v1/map/geocode")
        assert resp.status_code == 400
