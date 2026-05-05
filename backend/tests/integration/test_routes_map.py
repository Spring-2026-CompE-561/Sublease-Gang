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


    def test_limit_above_cap_rejected(self, client):
        resp = client.get(
            "/api/v1/map/listings",
            params={
                "north": 41, "south": 40, "east": -73, "west": -75,
                "limit": 10_000_000,
            },
        )
        assert resp.status_code in (400, 422)


class TestGeocode:
    def test_without_address(self, client):
        resp = client.get("/api/v1/map/geocode")
        assert resp.status_code == 400

    def test_blank_address_rejected(self, client):
        resp = client.get("/api/v1/map/geocode", params={"address": "   "})
        assert resp.status_code == 400

    def test_oversized_query_rejected(self, client):
        resp = client.get(
            "/api/v1/map/geocode",
            params={"address": "x" * 500},
        )
        assert resp.status_code == 400

    def test_proxies_to_nominatim_with_proper_user_agent(self, client, monkeypatch):
        from app.routes import map as map_route

        captured: dict = {}

        class _FakeResponse:
            ok = True
            content = b"[]"
            status_code = 200

            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        def fake_get(url, params, headers, timeout):
            captured["url"] = url
            captured["params"] = params
            captured["headers"] = headers
            return _FakeResponse(
                [
                    {"lat": "40.71", "lon": "-74.0", "display_name": "New York, NY"},
                    {"lat": "ignored"},
                ]
            )

        monkeypatch.setattr(map_route.requests, "get", fake_get)
        # Reset the cache so the fake_get actually runs.
        map_route._geocode_cache.clear()
        resp = client.get("/api/v1/map/geocode", params={"address": "New York"})
        assert resp.status_code == 200
        assert resp.json()["results"] == [
            {"lat": 40.71, "lon": -74.0, "display_name": "New York, NY"}
        ]
        assert captured["url"] == map_route._NOMINATIM_URL
        assert captured["params"]["q"] == "New York"
        assert "Sublease-Gang" in captured["headers"]["User-Agent"]

    def test_upstream_failure_returns_502(self, client, monkeypatch):
        import requests as requests_lib

        from app.routes import map as map_route

        def boom(*_args, **_kwargs):
            raise requests_lib.ConnectionError("nope")

        monkeypatch.setattr(map_route.requests, "get", boom)
        map_route._geocode_cache.clear()
        resp = client.get(
            "/api/v1/map/geocode", params={"address": "anywhere unique"}
        )
        assert resp.status_code == 502
