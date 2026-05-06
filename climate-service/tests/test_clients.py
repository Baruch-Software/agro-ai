from app.clients.nasa_power_client import NasaPowerClient
from app.clients.openweather_client import OpenWeatherClient


class TestNasaPowerClient:
    """Tests for NasaPowerClient initialization."""

    def test_init(self):
        client = NasaPowerClient("https://power.larc.nasa.gov/api/v2")
        assert client.base_url == "https://power.larc.nasa.gov/api/v2"
        assert client.client is not None


class TestOpenWeatherClient:
    """Tests for OpenWeatherClient initialization."""

    def test_init(self):
        client = OpenWeatherClient("https://api.openweathermap.org/data/2.5", "test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.openweathermap.org/data/2.5"
