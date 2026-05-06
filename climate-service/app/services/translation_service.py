from typing import Any, Optional

from app.models.weather_datapoint import ClimateImpact


class TranslationService:
    """Translates raw weather data into sector-specific business impact."""

    SECTOR_THRESHOLDS: dict[str, dict[str, Any]] = {
        "agro": {
            "high_temp": 35.0,
            "low_precipitation": 5.0,
            "high_wind": 60.0,
        },
        "energy": {
            "high_temp": 38.0,
            "low_solar": 100.0,
            "high_wind": 80.0,
        },
        "logistics": {
            "high_precipitation": 50.0,
            "high_wind": 70.0,
            "low_visibility": 1000.0,
        },
        "insurance": {
            "high_precipitation": 80.0,
            "high_wind": 90.0,
            "high_temp": 40.0,
        },
    }

    def translate_weather_to_impact(
        self, weather: Optional[dict[str, Any]], sector: str
    ) -> ClimateImpact:
        """Translate raw weather data to sector-specific impact."""
        if weather is None:
            return ClimateImpact(
                sector=sector,
                risk_level="unknown",
                impact_description=f"No weather data available for {sector} analysis",
                probability=0.0,
                recommended_actions=["Fetch weather data first"],
                timeframe_hours=0,
            )

        risk_level = self._assess_risk(weather, sector)
        actions = self._recommend_actions(risk_level, sector)

        return ClimateImpact(
            sector=sector,
            risk_level=risk_level,
            impact_description=self._build_description(weather, sector, risk_level),
            probability=self._calculate_probability(risk_level),
            recommended_actions=actions,
            timeframe_hours=72,
        )

    def _assess_risk(self, weather: dict[str, Any], sector: str) -> str:
        """Assess risk level based on weather and sector thresholds."""
        thresholds = self.SECTOR_THRESHOLDS.get(sector, {})
        temp = weather.get("temperature_2m", 0)
        precip = weather.get("precipitation", 0)

        risk_score = 0
        if temp > thresholds.get("high_temp", 40):
            risk_score += 2
        if precip > thresholds.get("high_precipitation", 80):
            risk_score += 2
        if precip < thresholds.get("low_precipitation", 5):
            risk_score += 1

        if risk_score >= 3:
            return "very_high"
        if risk_score >= 2:
            return "high"
        if risk_score >= 1:
            return "medium"
        return "low"

    def _recommend_actions(self, risk_level: str, sector: str) -> list[str]:
        """Generate recommended actions based on risk and sector."""
        actions: dict[str, list[str]] = {
            "low": ["Continue monitoring"],
            "medium": ["Monitor closely", "Review contingency plans"],
            "high": ["Activate contingency plans", "Notify stakeholders"],
            "very_high": [
                "Immediate action required",
                "Activate emergency protocols",
                "Notify all stakeholders",
            ],
        }
        return actions.get(risk_level, ["Monitor closely"])

    def _build_description(
        self, weather: dict[str, Any], sector: str, risk_level: str
    ) -> str:
        """Build human-readable impact description."""
        temp = weather.get("temperature_2m", "N/A")
        precip = weather.get("precipitation", "N/A")
        return (
            f"{sector.capitalize()} sector: {risk_level} risk. "
            f"Temperature: {temp}°C, Precipitation: {precip}mm."
        )

    def _calculate_probability(self, risk_level: str) -> float:
        """Map risk level to probability."""
        mapping = {
            "low": 0.15,
            "medium": 0.45,
            "high": 0.72,
            "very_high": 0.90,
            "unknown": 0.0,
        }
        return mapping.get(risk_level, 0.0)
