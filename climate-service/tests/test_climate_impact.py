import pytest


class TestClimateImpactEndpoint:
    """Tests for GET /api/v1/climate/impact."""

    @pytest.mark.parametrize("sector", ["agro", "energy", "logistics", "insurance", "citizen"])
    def test_valid_sectors(self, client, sector):
        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": sector}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sector"] == sector
        assert "risk_level" in data
        assert "impact_description" in data
        assert "recommended_actions" in data

    def test_invalid_sector(self, client):
        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "invalid"}
        )
        assert response.status_code == 422

    def test_missing_params(self, client):
        response = client.get("/api/v1/climate/impact")
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "lat,lon",
        [(-91, 0), (91, 0), (0, -181), (0, 181)],
    )
    def test_invalid_coordinates(self, client, lat, lon):
        response = client.get(
            "/api/v1/climate/impact", params={"lat": lat, "lon": lon, "sector": "agro"}
        )
        assert response.status_code == 422


class TestLanguageParam:
    """Tests for lang query parameter."""

    def test_default_lang_is_english(self, client):
        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "No weather data available" in data["impact_description"]

    def test_spanish_response(self, client):
        response = client.get(
            "/api/v1/climate/impact",
            params={"lat": -31.0, "lon": -64.0, "sector": "agro", "lang": "es"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "No hay datos climáticos" in data["impact_description"]

    def test_english_explicit(self, client):
        response = client.get(
            "/api/v1/climate/impact",
            params={"lat": -31.0, "lon": -64.0, "sector": "citizen", "lang": "en"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "General Population" in data["impact_description"] or "No weather data" in data["impact_description"]

    def test_invalid_lang(self, client):
        response = client.get(
            "/api/v1/climate/impact",
            params={"lat": -31.0, "lon": -64.0, "sector": "agro", "lang": "fr"},
        )
        assert response.status_code == 422

    def test_citizen_spanish(self, client):
        response = client.get(
            "/api/v1/climate/impact",
            params={"lat": -31.0, "lon": -64.0, "sector": "citizen", "lang": "es"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "Población General" in data["impact_description"] or "No hay datos" in data["impact_description"]
