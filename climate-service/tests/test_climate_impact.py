from unittest.mock import AsyncMock, patch

import pytest

MOCK_WEATHER = {
    "date": "20260503",
    "temperature_2m": 16.97,
    "precipitation": 0.0,
    "humidity": 68.55,
    "wind_speed": 2.43,
    "solar_radiation": 16.39,
}


@pytest.fixture(autouse=True)
def mock_nasa(monkeypatch):
    """Mock NASA POWER client for all endpoint tests."""
    mock = AsyncMock(return_value=MOCK_WEATHER)
    monkeypatch.setattr(
        "app.api.v1.routes.climate.NasaPowerClient.get_recent_weather", mock
    )
    mock_close = AsyncMock()
    monkeypatch.setattr(
        "app.api.v1.routes.climate.NasaPowerClient.close", mock_close
    )
    return mock


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
        assert data["risk_level"] != "unknown"
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

    def test_response_has_real_data(self, client):
        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        data = response.json()
        assert "16.97°C" in data["impact_description"]

    def test_nasa_failure_returns_502(self, client, monkeypatch):
        mock = AsyncMock(side_effect=Exception("NASA API down"))
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NasaPowerClient.get_recent_weather", mock
        )
        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        assert response.status_code == 502

    def test_nasa_returns_none(self, client, monkeypatch):
        mock = AsyncMock(return_value=None)
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NasaPowerClient.get_recent_weather", mock
        )
        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "unknown"


class TestLanguageParam:
    """Tests for lang query parameter."""

    def test_default_lang_is_english(self, client):
        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Agriculture" in data["impact_description"]

    def test_spanish_response(self, client):
        response = client.get(
            "/api/v1/climate/impact",
            params={"lat": -31.0, "lon": -64.0, "sector": "agro", "lang": "es"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "Agricultura" in data["impact_description"]

    def test_english_citizen(self, client):
        response = client.get(
            "/api/v1/climate/impact",
            params={"lat": -31.0, "lon": -64.0, "sector": "citizen", "lang": "en"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "General forecast" in data["impact_description"]

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
        assert "Pronóstico general" in data["impact_description"]
