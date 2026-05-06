import pytest

from app.clients.nvidia_llm_client import NvidiaLlmClient


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
        },
        {
            "date": "2026-05-07",
            "temp_max": 8.0,
            "temp_min": 2.0,
            "apparent_temp_max": 5.0,
            "apparent_temp_min": -1.0,
            "precipitation_sum": 15.0,
            "precipitation_probability": 80,
            "wind_max": 12.0,
            "wind_gusts_max": 25.0,
            "wind_direction": 200,
            "uv_index_max": 2.0,
            "weather_code": 63,
            "sunrise": "2026-05-07T07:16",
            "sunset": "2026-05-07T17:59",
        },
    ],
    "next_24h_hourly": [
        {
            "time": "2026-05-06T00:00",
            "temp": 12.0,
            "apparent_temp": 10.0,
            "humidity": 60,
            "precipitation": 0.0,
            "precip_probability": 0,
            "pressure_msl": 1020.0,
            "cloud_cover": 30,
            "wind_speed": 2.0,
            "wind_gusts": 4.0,
            "wind_direction": 180,
            "weather_code": 0,
        }
    ],
    "pressure_trend": "falling_rapidly",
}


class TestNvidiaLlmClient:
    """Tests for NvidiaLlmClient."""

    def test_init(self):
        client = NvidiaLlmClient("test-key")
        assert client.api_key == "test-key"
        assert client.model == "meta/llama-3.3-70b-instruct"

    def test_init_custom_model(self):
        client = NvidiaLlmClient("test-key", model="nvidia/nemotron-ultra")
        assert client.model == "nvidia/nemotron-ultra"

    def test_build_system_prompt_english(self):
        client = NvidiaLlmClient("test-key")
        prompt = client._build_system_prompt("en", "agro")
        assert "senior meteorologist" in prompt
        assert "Response in English" in prompt
        assert "JSON" in prompt
        assert "daily_outlook" in prompt

    def test_build_system_prompt_spanish(self):
        client = NvidiaLlmClient("test-key")
        prompt = client._build_system_prompt("es", "agro")
        assert "Response in Spanish" in prompt

    def test_build_system_prompt_agro_sector(self):
        client = NvidiaLlmClient("test-key")
        prompt = client._build_system_prompt("en", "agro")
        assert "AGRICULTURE" in prompt
        assert "frost" in prompt.lower()

    def test_build_system_prompt_citizen_sector(self):
        client = NvidiaLlmClient("test-key")
        prompt = client._build_system_prompt("en", "citizen")
        assert "GENERAL PUBLIC" in prompt
        assert "umbrella" in prompt.lower()

    def test_build_user_prompt_without_forecast(self):
        client = NvidiaLlmClient("test-key")
        weather = {
            "date": "20260503",
            "temperature_2m": 11.68,
            "precipitation": 0.0,
            "humidity": 49.01,
            "wind_speed": 2.51,
            "solar_radiation": None,
        }
        prompt = client._build_user_prompt(weather, "agro", -31.4, -64.2, "en")
        assert "AGRICULTURE" in prompt
        assert "11.68°C" in prompt
        assert "Southern" in prompt
        assert "SECTION 1" in prompt
        assert "SECTION 2" not in prompt

    def test_build_user_prompt_with_forecast(self):
        client = NvidiaLlmClient("test-key")
        weather = {
            "date": "20260503",
            "temperature_2m": 11.68,
            "precipitation": 0.0,
        }
        prompt = client._build_user_prompt(
            weather, "agro", -31.4, -64.2, "en", MOCK_FORECAST
        )
        assert "SECTION 1" in prompt
        assert "SECTION 2" in prompt
        assert "ECMWF/GFS/ICON" in prompt
        assert "falling_rapidly" in prompt
        assert "2026-05-07" in prompt
        assert "2.0°C" in prompt

    def test_build_user_prompt_northern_hemisphere(self):
        client = NvidiaLlmClient("test-key")
        weather = {"temperature_2m": 25.0, "precipitation": 10.0}
        prompt = client._build_user_prompt(weather, "citizen", 40.7, -74.0, "en")
        assert "Northern" in prompt
        assert "GENERAL POPULATION" in prompt

    def test_format_forecast_data(self):
        client = NvidiaLlmClient("test-key")
        result = client._format_forecast_data(MOCK_FORECAST)
        assert "DAILY FORECAST" in result
        assert "NEXT 24H HOURLY" in result
        assert "Moderate rain" in result
        assert "1020.0hPa" in result

    def test_parse_response_valid(self):
        client = NvidiaLlmClient("test-key")
        raw = {
            "choices": [
                {
                    "message": {
                        "content": '{"risk_level": "low", "impact_description": "test", "probability": 0.3, "recommended_actions": ["action1"], "timeframe_hours": 72, "detailed_analysis": "analysis"}'
                    }
                }
            ]
        }
        result = client._parse_response(raw)
        assert result is not None
        assert result["risk_level"] == "low"
        assert result["probability"] == 0.3

    def test_parse_response_with_markdown(self):
        client = NvidiaLlmClient("test-key")
        raw = {
            "choices": [
                {
                    "message": {
                        "content": '```json\n{"risk_level": "high", "impact_description": "test", "probability": 0.8, "recommended_actions": [], "timeframe_hours": 48, "detailed_analysis": "test"}\n```'
                    }
                }
            ]
        }
        result = client._parse_response(raw)
        assert result is not None
        assert result["risk_level"] == "high"

    def test_parse_response_invalid_json(self):
        client = NvidiaLlmClient("test-key")
        raw = {"choices": [{"message": {"content": "not json at all"}}]}
        result = client._parse_response(raw)
        assert result is None

    def test_parse_response_empty_choices(self):
        client = NvidiaLlmClient("test-key")
        result = client._parse_response({"choices": []})
        assert result is None
