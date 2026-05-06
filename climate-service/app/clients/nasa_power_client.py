from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

NO_DATA_VALUE = -999.0


class NasaPowerClient:
    """NASA POWER API client for historical and recent climate data."""

    PARAMETERS = "T2M,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN"

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_daily_data(
        self,
        lat: float,
        lon: float,
        start: str,
        end: str,
        parameters: str = PARAMETERS,
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

    async def get_recent_weather(
        self, lat: float, lon: float, days_back: int = 7
    ) -> Optional[dict[str, Any]]:
        """Fetch most recent valid weather data for coordinates."""
        end = datetime.now()
        start = end - timedelta(days=days_back)
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")

        raw = await self.get_daily_data(lat, lon, start_str, end_str)
        return self._extract_latest_valid(raw)

    def _extract_latest_valid(
        self, raw_response: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Extract most recent day with valid data from NASA response."""
        params = raw_response.get("properties", {}).get("parameter", {})
        if not params:
            return None

        t2m = params.get("T2M", {})
        dates = sorted(t2m.keys(), reverse=True)

        for date_key in dates:
            temp = t2m.get(date_key, NO_DATA_VALUE)
            if temp == NO_DATA_VALUE:
                continue

            precip = params.get("PRECTOTCORR", {}).get(date_key, NO_DATA_VALUE)
            humidity = params.get("RH2M", {}).get(date_key, NO_DATA_VALUE)
            wind = params.get("WS2M", {}).get(date_key, NO_DATA_VALUE)
            solar = params.get("ALLSKY_SFC_SW_DWN", {}).get(date_key, NO_DATA_VALUE)

            return {
                "date": date_key,
                "temperature_2m": temp if temp != NO_DATA_VALUE else None,
                "precipitation": precip if precip != NO_DATA_VALUE else None,
                "humidity": humidity if humidity != NO_DATA_VALUE else None,
                "wind_speed": wind if wind != NO_DATA_VALUE else None,
                "solar_radiation": solar if solar != NO_DATA_VALUE else None,
            }

        return None

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
