from datetime import datetime

import pytest

from app.models.weather_datapoint import ClimateImpact, WeatherDataPoint


class TestWeatherDataPoint:
    """Tests for WeatherDataPoint model."""

    def test_create_minimal(self):
        point = WeatherDataPoint(
            latitude=-31.0, longitude=-64.0, timestamp=datetime.now()
        )
        assert point.latitude == -31.0
        assert point.temperature_2m is None

    def test_create_full(self):
        point = WeatherDataPoint(
            latitude=-31.0,
            longitude=-64.0,
            timestamp=datetime.now(),
            temperature_2m=25.5,
            precipitation=10.2,
            humidity=65.0,
            wind_speed=12.3,
            solar_radiation=450.0,
        )
        assert point.temperature_2m == 25.5
        assert point.precipitation == 10.2


class TestClimateImpact:
    """Tests for ClimateImpact model."""

    def test_create(self):
        impact = ClimateImpact(
            sector="agro",
            risk_level="medium",
            impact_description="Test impact",
            probability=0.5,
            timeframe_hours=72,
        )
        assert impact.sector == "agro"
        assert impact.recommended_actions == []

    def test_probability_bounds(self):
        with pytest.raises(ValueError):
            ClimateImpact(
                sector="agro",
                risk_level="high",
                impact_description="Test",
                probability=1.5,
                timeframe_hours=24,
            )

        with pytest.raises(ValueError):
            ClimateImpact(
                sector="agro",
                risk_level="high",
                impact_description="Test",
                probability=-0.1,
                timeframe_hours=24,
            )
