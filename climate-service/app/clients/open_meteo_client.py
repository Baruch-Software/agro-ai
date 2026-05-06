import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoClient:
    """Open-Meteo API client for weather forecasts (ECMWF/GFS/ICON models)."""

    HOURLY_PARAMS = (
        "temperature_2m,relative_humidity_2m,precipitation,precipitation_probability,"
        "pressure_msl,surface_pressure,cloud_cover,wind_speed_10m,wind_gusts_10m,"
        "wind_direction_10m,apparent_temperature,weather_code"
    )
    DAILY_PARAMS = (
        "temperature_2m_max,temperature_2m_min,apparent_temperature_max,"
        "apparent_temperature_min,precipitation_sum,precipitation_probability_max,"
        "wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,"
        "sunrise,sunset,uv_index_max,weather_code"
    )

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_forecast(
        self,
        lat: float,
        lon: float,
        forecast_days: int = 7,
    ) -> Optional[dict[str, Any]]:
        """Fetch weather forecast with hourly and daily data."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": self.HOURLY_PARAMS,
            "daily": self.DAILY_PARAMS,
            "forecast_days": forecast_days,
            "timezone": "auto",
            "wind_speed_unit": "ms",
        }

        try:
            response = await self.client.get(OPEN_METEO_FORECAST_URL, params=params)
            response.raise_for_status()
            raw = response.json()
            return self._process_forecast(raw)
        except Exception as e:
            logger.error("Open-Meteo API error: %s", str(e))
            return None

    def _process_forecast(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Process raw Open-Meteo response into structured forecast."""
        daily = raw.get("daily", {})
        hourly = raw.get("hourly", {})
        timezone = raw.get("timezone", "UTC")

        daily_forecast = []
        dates = daily.get("time", [])
        for i, date in enumerate(dates):
            daily_forecast.append({
                "date": date,
                "temp_max": daily.get("temperature_2m_max", [None])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
                "temp_min": daily.get("temperature_2m_min", [None])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
                "apparent_temp_max": daily.get("apparent_temperature_max", [None])[i] if i < len(daily.get("apparent_temperature_max", [])) else None,
                "apparent_temp_min": daily.get("apparent_temperature_min", [None])[i] if i < len(daily.get("apparent_temperature_min", [])) else None,
                "precipitation_sum": daily.get("precipitation_sum", [None])[i] if i < len(daily.get("precipitation_sum", [])) else None,
                "precipitation_probability": daily.get("precipitation_probability_max", [None])[i] if i < len(daily.get("precipitation_probability_max", [])) else None,
                "wind_max": daily.get("wind_speed_10m_max", [None])[i] if i < len(daily.get("wind_speed_10m_max", [])) else None,
                "wind_gusts_max": daily.get("wind_gusts_10m_max", [None])[i] if i < len(daily.get("wind_gusts_10m_max", [])) else None,
                "wind_direction": daily.get("wind_direction_10m_dominant", [None])[i] if i < len(daily.get("wind_direction_10m_dominant", [])) else None,
                "uv_index_max": daily.get("uv_index_max", [None])[i] if i < len(daily.get("uv_index_max", [])) else None,
                "weather_code": daily.get("weather_code", [None])[i] if i < len(daily.get("weather_code", [])) else None,
                "sunrise": daily.get("sunrise", [None])[i] if i < len(daily.get("sunrise", [])) else None,
                "sunset": daily.get("sunset", [None])[i] if i < len(daily.get("sunset", [])) else None,
            })

        next_24h_hourly = []
        times = hourly.get("time", [])
        for i in range(min(24, len(times))):
            next_24h_hourly.append({
                "time": times[i],
                "temp": hourly.get("temperature_2m", [None])[i] if i < len(hourly.get("temperature_2m", [])) else None,
                "apparent_temp": hourly.get("apparent_temperature", [None])[i] if i < len(hourly.get("apparent_temperature", [])) else None,
                "humidity": hourly.get("relative_humidity_2m", [None])[i] if i < len(hourly.get("relative_humidity_2m", [])) else None,
                "precipitation": hourly.get("precipitation", [None])[i] if i < len(hourly.get("precipitation", [])) else None,
                "precip_probability": hourly.get("precipitation_probability", [None])[i] if i < len(hourly.get("precipitation_probability", [])) else None,
                "pressure_msl": hourly.get("pressure_msl", [None])[i] if i < len(hourly.get("pressure_msl", [])) else None,
                "cloud_cover": hourly.get("cloud_cover", [None])[i] if i < len(hourly.get("cloud_cover", [])) else None,
                "wind_speed": hourly.get("wind_speed_10m", [None])[i] if i < len(hourly.get("wind_speed_10m", [])) else None,
                "wind_gusts": hourly.get("wind_gusts_10m", [None])[i] if i < len(hourly.get("wind_gusts_10m", [])) else None,
                "wind_direction": hourly.get("wind_direction_10m", [None])[i] if i < len(hourly.get("wind_direction_10m", [])) else None,
                "weather_code": hourly.get("weather_code", [None])[i] if i < len(hourly.get("weather_code", [])) else None,
            })

        pressure_trend = self._calc_pressure_trend(hourly)

        return {
            "timezone": timezone,
            "daily_forecast": daily_forecast,
            "next_24h_hourly": next_24h_hourly,
            "pressure_trend": pressure_trend,
        }

    def _calc_pressure_trend(self, hourly: dict[str, Any]) -> Optional[str]:
        """Detect pressure trend from hourly data — key for front detection."""
        pressures = hourly.get("pressure_msl", [])
        valid = [p for p in pressures[:24] if p is not None]
        if len(valid) < 6:
            return None

        first_6h = sum(valid[:6]) / 6
        last_6h = sum(valid[-6:]) / 6
        diff = last_6h - first_6h

        if diff < -3:
            return "falling_rapidly"
        elif diff < -1:
            return "falling"
        elif diff > 3:
            return "rising_rapidly"
        elif diff > 1:
            return "rising"
        return "stable"

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
