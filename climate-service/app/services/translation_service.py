from typing import Any, Optional

from app.core.i18n import get_translation
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
        "citizen": {
            "high_temp": 32.0,
            "low_temp": 0.0,
            "high_precipitation": 30.0,
            "high_wind": 50.0,
            "high_uv": 8.0,
        },
    }

    def translate_weather_to_impact(
        self,
        weather: Optional[dict[str, Any]],
        sector: str,
        lang: str = "en",
    ) -> ClimateImpact:
        """Translate raw weather data to sector-specific impact."""
        t = get_translation(lang)
        sector_name = t["sectors"].get(sector, sector)

        if weather is None:
            return ClimateImpact(
                sector=sector,
                risk_level="unknown",
                impact_description=t["no_data"].format(sector=sector_name),
                probability=0.0,
                recommended_actions=[t["fetch_first"]],
                timeframe_hours=0,
            )

        risk_level = self._assess_risk(weather, sector)
        actions = self._recommend_actions(risk_level, sector, lang)
        risk_label = t["risk_levels"].get(risk_level, risk_level)

        return ClimateImpact(
            sector=sector,
            risk_level=risk_level,
            impact_description=self._build_description(
                weather, sector, risk_label, sector_name, lang
            ),
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
        if "low_temp" in thresholds and temp < thresholds["low_temp"]:
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

    def _recommend_actions(
        self, risk_level: str, sector: str, lang: str = "en"
    ) -> list[str]:
        """Generate recommended actions based on risk, sector, and language."""
        t = get_translation(lang)
        actions_map = t.get("actions", {})
        level_actions = actions_map.get(risk_level, {})

        if sector == "citizen":
            return level_actions.get("citizen", level_actions.get("default", []))
        return level_actions.get("default", [])

    def _build_description(
        self,
        weather: dict[str, Any],
        sector: str,
        risk_label: str,
        sector_name: str,
        lang: str = "en",
    ) -> str:
        """Build human-readable impact description."""
        t = get_translation(lang)
        temp = weather.get("temperature_2m", "N/A")
        precip = weather.get("precipitation", "N/A")

        if sector == "citizen":
            template = t.get("citizen_description", t["description"])
        else:
            template = t["description"]

        return template.format(
            sector=sector_name,
            risk_level=risk_label,
            temp=temp,
            precip=precip,
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
