from typing import Any

import httpx


class OpenWeatherClient:
    """OpenWeather API client for current weather data."""

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()

    async def get_current_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """Fetch current weather for coordinates."""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
