from typing import Any, Optional


class ClimateRepository:
    """Repository for climate data storage."""

    async def save_weather_data(self, data: dict[str, Any]) -> None:
        """Save weather data to PostgreSQL."""
        pass

    async def get_historical_data(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
    ) -> Optional[list[dict[str, Any]]]:
        """Retrieve historical data for coordinates and date range."""
        pass
