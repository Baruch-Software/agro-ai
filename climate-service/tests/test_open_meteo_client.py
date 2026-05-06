import pytest

from app.clients.nvidia_llm_client import WEATHER_CODES
from app.clients.open_meteo_client import OpenMeteoClient


class TestOpenMeteoClient:
    """Tests for OpenMeteoClient."""

    def test_init(self):
        client = OpenMeteoClient()
        assert client.client is not None

    def test_process_forecast_basic(self):
        client = OpenMeteoClient()
        raw = {
            "timezone": "America/Argentina/Cordoba",
            "daily": {
                "time": ["2026-05-06", "2026-05-07"],
                "temperature_2m_max": [18.0, 8.0],
                "temperature_2m_min": [10.0, 2.0],
                "apparent_temperature_max": [16.0, 5.0],
                "apparent_temperature_min": [8.0, -1.0],
                "precipitation_sum": [0.0, 15.0],
                "precipitation_probability_max": [10, 80],
                "wind_speed_10m_max": [3.0, 12.0],
                "wind_gusts_10m_max": [8.0, 25.0],
                "wind_direction_10m_dominant": [180, 200],
                "uv_index_max": [4.0, 2.0],
                "weather_code": [1, 63],
                "sunrise": ["2026-05-06T07:15", "2026-05-07T07:16"],
                "sunset": ["2026-05-06T18:00", "2026-05-07T17:59"],
            },
            "hourly": {
                "time": [f"2026-05-06T{h:02d}:00" for h in range(24)],
                "temperature_2m": [12.0 - i * 0.5 for i in range(24)],
                "apparent_temperature": [10.0 - i * 0.5 for i in range(24)],
                "relative_humidity_2m": [60 + i for i in range(24)],
                "precipitation": [0.0] * 24,
                "precipitation_probability": [0] * 24,
                "pressure_msl": [1020.0 - i * 0.3 for i in range(24)],
                "cloud_cover": [30 + i * 2 for i in range(24)],
                "wind_speed_10m": [2.0 + i * 0.2 for i in range(24)],
                "wind_gusts_10m": [4.0 + i * 0.3 for i in range(24)],
                "wind_direction_10m": [180] * 24,
                "weather_code": [0] * 24,
            },
        }
        result = client._process_forecast(raw)

        assert result["timezone"] == "America/Argentina/Cordoba"
        assert len(result["daily_forecast"]) == 2
        assert result["daily_forecast"][0]["temp_max"] == 18.0
        assert result["daily_forecast"][1]["temp_min"] == 2.0
        assert len(result["next_24h_hourly"]) == 24

    def test_process_forecast_empty(self):
        client = OpenMeteoClient()
        result = client._process_forecast({"daily": {}, "hourly": {}})
        assert result["daily_forecast"] == []
        assert result["next_24h_hourly"] == []

    def test_pressure_trend_falling_rapidly(self):
        client = OpenMeteoClient()
        hourly = {"pressure_msl": [1020.0 - i * 0.5 for i in range(24)]}
        trend = client._calc_pressure_trend(hourly)
        assert trend == "falling_rapidly"

    def test_pressure_trend_stable(self):
        client = OpenMeteoClient()
        hourly = {"pressure_msl": [1015.0] * 24}
        trend = client._calc_pressure_trend(hourly)
        assert trend == "stable"

    def test_pressure_trend_rising(self):
        client = OpenMeteoClient()
        hourly = {"pressure_msl": [1010.0 + i * 0.1 for i in range(24)]}
        trend = client._calc_pressure_trend(hourly)
        assert trend == "rising"

    def test_pressure_trend_insufficient_data(self):
        client = OpenMeteoClient()
        hourly = {"pressure_msl": [1015.0, 1014.0]}
        trend = client._calc_pressure_trend(hourly)
        assert trend is None

    def test_weather_codes_exist(self):
        assert WEATHER_CODES[0] == "Clear sky"
        assert WEATHER_CODES[95] == "Thunderstorm"
        assert WEATHER_CODES[75] == "Heavy snow"

    def test_daily_forecast_fields(self):
        client = OpenMeteoClient()
        raw = {
            "daily": {
                "time": ["2026-05-06"],
                "temperature_2m_max": [20.0],
                "temperature_2m_min": [5.0],
                "apparent_temperature_max": [18.0],
                "apparent_temperature_min": [3.0],
                "precipitation_sum": [10.0],
                "precipitation_probability_max": [70],
                "wind_speed_10m_max": [8.0],
                "wind_gusts_10m_max": [15.0],
                "wind_direction_10m_dominant": [225],
                "uv_index_max": [3.0],
                "weather_code": [63],
                "sunrise": ["2026-05-06T07:15"],
                "sunset": ["2026-05-06T18:00"],
            },
            "hourly": {"time": [], "pressure_msl": []},
        }
        result = client._process_forecast(raw)
        day = result["daily_forecast"][0]
        assert day["precipitation_sum"] == 10.0
        assert day["precipitation_probability"] == 70
        assert day["wind_gusts_max"] == 15.0
        assert day["uv_index_max"] == 3.0
        assert day["weather_code"] == 63
