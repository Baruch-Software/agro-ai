import pytest

from app.clients.nasa_power_client import NO_DATA_VALUE, NasaPowerClient
from app.clients.openweather_client import OpenWeatherClient

SAMPLE_NASA_RESPONSE = {
    "properties": {
        "parameter": {
            "T2M": {
                "20260501": 16.97,
                "20260502": 11.66,
                "20260503": NO_DATA_VALUE,
            },
            "PRECTOTCORR": {
                "20260501": 0.0,
                "20260502": 5.2,
                "20260503": NO_DATA_VALUE,
            },
            "RH2M": {
                "20260501": 68.55,
                "20260502": 39.09,
                "20260503": NO_DATA_VALUE,
            },
            "WS2M": {
                "20260501": 2.43,
                "20260502": 2.37,
                "20260503": NO_DATA_VALUE,
            },
            "ALLSKY_SFC_SW_DWN": {
                "20260501": 16.39,
                "20260502": NO_DATA_VALUE,
                "20260503": NO_DATA_VALUE,
            },
        }
    }
}


class TestNasaPowerClient:
    """Tests for NasaPowerClient."""

    def test_init(self):
        client = NasaPowerClient("https://power.larc.nasa.gov/api/v2")
        assert client.base_url == "https://power.larc.nasa.gov/api/v2"
        assert client.client is not None

    def test_extract_latest_valid(self):
        client = NasaPowerClient("https://power.larc.nasa.gov/api/v2")
        result = client._extract_latest_valid(SAMPLE_NASA_RESPONSE)
        assert result is not None
        assert result["date"] == "20260502"
        assert result["temperature_2m"] == 11.66
        assert result["precipitation"] == 5.2
        assert result["humidity"] == 39.09
        assert result["wind_speed"] == 2.37
        assert result["solar_radiation"] is None

    def test_extract_skips_no_data(self):
        client = NasaPowerClient("https://power.larc.nasa.gov/api/v2")
        all_invalid = {
            "properties": {
                "parameter": {
                    "T2M": {"20260501": NO_DATA_VALUE},
                    "PRECTOTCORR": {"20260501": NO_DATA_VALUE},
                }
            }
        }
        result = client._extract_latest_valid(all_invalid)
        assert result is None

    def test_extract_empty_response(self):
        client = NasaPowerClient("https://power.larc.nasa.gov/api/v2")
        result = client._extract_latest_valid({})
        assert result is None

    def test_extract_picks_most_recent(self):
        client = NasaPowerClient("https://power.larc.nasa.gov/api/v2")
        response = {
            "properties": {
                "parameter": {
                    "T2M": {"20260501": 10.0, "20260502": 20.0},
                    "PRECTOTCORR": {"20260501": 1.0, "20260502": 2.0},
                    "RH2M": {"20260501": 50.0, "20260502": 60.0},
                    "WS2M": {"20260501": 3.0, "20260502": 4.0},
                    "ALLSKY_SFC_SW_DWN": {"20260501": 100.0, "20260502": 200.0},
                }
            }
        }
        result = client._extract_latest_valid(response)
        assert result["date"] == "20260502"
        assert result["temperature_2m"] == 20.0


class TestOpenWeatherClient:
    """Tests for OpenWeatherClient initialization."""

    def test_init(self):
        client = OpenWeatherClient("https://api.openweathermap.org/data/2.5", "test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.openweathermap.org/data/2.5"
