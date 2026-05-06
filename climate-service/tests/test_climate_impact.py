from unittest.mock import AsyncMock

import pytest

MOCK_WEATHER = {
    "date": "20260503",
    "temperature_2m": 16.97,
    "precipitation": 0.0,
    "humidity": 68.55,
    "wind_speed": 2.43,
    "solar_radiation": 16.39,
}

MOCK_FORECAST = {
    "timezone": "America/Argentina/Cordoba",
    "daily_forecast": [
        {
            "date": "2026-05-06",
            "temp_max": 18.0,
            "temp_min": 10.0,
            "apparent_temp_max": 16.0,
            "apparent_temp_min": 8.0,
            "precipitation_sum": 0.0,
            "precipitation_probability": 10,
            "wind_max": 3.0,
            "wind_gusts_max": 8.0,
            "wind_direction": 180,
            "uv_index_max": 4.0,
            "weather_code": 1,
            "sunrise": "2026-05-06T07:15",
            "sunset": "2026-05-06T18:00",
        }
    ],
    "next_24h_hourly": [],
    "pressure_trend": "stable",
}

MOCK_AI_RESPONSE = {
    "risk_level": "low",
    "impact_description": "AI: Favorable conditions for agriculture",
    "probability": 0.8,
    "recommended_actions": ["Monitor soil moisture", "Continue fieldwork"],
    "timeframe_hours": 72,
    "detailed_analysis": "Expert AI analysis of weather patterns.",
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


@pytest.fixture(autouse=True)
def mock_open_meteo(monkeypatch):
    """Mock Open-Meteo client for all endpoint tests."""
    mock = AsyncMock(return_value=MOCK_FORECAST)
    monkeypatch.setattr(
        "app.api.v1.routes.climate.OpenMeteoClient.get_forecast", mock
    )
    mock_close = AsyncMock()
    monkeypatch.setattr(
        "app.api.v1.routes.climate.OpenMeteoClient.close", mock_close
    )
    return mock


@pytest.fixture(autouse=True)
def mock_nvidia_disabled(monkeypatch):
    """Disable NVIDIA by default (empty key) → tests use rule-based fallback."""
    monkeypatch.setattr("app.api.v1.routes.climate.settings.nvidia_api_key", "")


class TestClimateImpactEndpoint:
    """Tests for GET /api/v1/climate/impact with rule-based fallback."""

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


class TestAIAnalysis:
    """Tests for NVIDIA LLM AI-powered analysis."""

    def test_ai_analysis_used_when_key_present(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.routes.climate.settings.nvidia_api_key", "test-key"
        )
        mock_analyze = AsyncMock(return_value=MOCK_AI_RESPONSE)
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.analyze_weather", mock_analyze
        )
        mock_close = AsyncMock()
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.close", mock_close
        )

        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "AI:" in data["impact_description"]
        assert data["detailed_analysis"] is not None

    def test_fallback_on_ai_failure(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.routes.climate.settings.nvidia_api_key", "test-key"
        )
        mock_analyze = AsyncMock(side_effect=Exception("LLM down"))
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.analyze_weather", mock_analyze
        )
        mock_close = AsyncMock()
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.close", mock_close
        )

        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detailed_analysis"] is None

    def test_fallback_on_ai_parse_failure(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.routes.climate.settings.nvidia_api_key", "test-key"
        )
        mock_analyze = AsyncMock(return_value=None)
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.analyze_weather", mock_analyze
        )
        mock_close = AsyncMock()
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.close", mock_close
        )

        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detailed_analysis"] is None

    def test_ai_invalid_risk_level_normalized(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.routes.climate.settings.nvidia_api_key", "test-key"
        )
        bad_response = {**MOCK_AI_RESPONSE, "risk_level": "extreme"}
        mock_analyze = AsyncMock(return_value=bad_response)
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.analyze_weather", mock_analyze
        )
        mock_close = AsyncMock()
        monkeypatch.setattr(
            "app.api.v1.routes.climate.NvidiaLlmClient.close", mock_close
        )

        response = client.get(
            "/api/v1/climate/impact", params={"lat": -31.0, "lon": -64.0, "sector": "agro"}
        )
        data = response.json()
        assert data["risk_level"] == "medium"


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
