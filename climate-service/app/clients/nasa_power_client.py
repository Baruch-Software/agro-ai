from typing import Any

import httpx


class NasaPowerClient:
    """NASA POWER API client for historical climate data."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def get_daily_data(
        self,
        lat: float,
        lon: float,
        start: str,
        end: str,
        parameters: str = "T2M,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN",
        community: str = "AG",
    ) -> dict[str, Any]:
        """Fetch daily climate data for coordinates and date range."""
        url = f"{self.base_url}/temporal/daily/point"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start": start,
            "end": end,
            "parameters": parameters,
            "community": community,
            "format": "JSON",
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
