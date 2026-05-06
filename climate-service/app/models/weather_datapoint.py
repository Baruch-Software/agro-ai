from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WeatherDataPoint(BaseModel):
    """Weather data point from external APIs."""

    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    timestamp: datetime = Field(..., description="Measurement timestamp")
    temperature_2m: Optional[float] = Field(None, description="Temperature at 2m (°C)")
    precipitation: Optional[float] = Field(None, description="Precipitation (mm)")
    humidity: Optional[float] = Field(None, description="Relative humidity (%)")
    wind_speed: Optional[float] = Field(None, description="Wind speed (m/s)")
    solar_radiation: Optional[float] = Field(None, description="Solar radiation (W/m²)")


class ClimateImpact(BaseModel):
    """Interpreted climate impact for a specific sector."""

    sector: str = Field(..., description="Target sector (agro/energy/logistics/insurance)")
    risk_level: str = Field(..., description="Risk level: low/medium/high/very_high")
    impact_description: str = Field(..., description="Human-readable impact")
    probability: float = Field(..., ge=0, le=1, description="Probability 0-1")
    recommended_actions: list[str] = Field(default_factory=list)
    timeframe_hours: int = Field(..., description="Impact timeframe in hours")
