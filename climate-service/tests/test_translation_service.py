import pytest

from app.services.translation_service import TranslationService


class TestTranslationService:
    """Tests for TranslationService."""

    @pytest.fixture
    def service(self) -> TranslationService:
        return TranslationService()

    @pytest.mark.parametrize("sector", ["agro", "energy", "logistics", "insurance"])
    def test_translate_with_none_weather(self, service, sector):
        impact = service.translate_weather_to_impact(None, sector)
        assert impact.sector == sector
        assert impact.risk_level == "unknown"
        assert impact.probability == 0.0

    def test_translate_low_risk(self, service):
        weather = {"temperature_2m": 22.0, "precipitation": 10.0}
        impact = service.translate_weather_to_impact(weather, "agro")
        assert impact.sector == "agro"
        assert impact.risk_level == "low"
        assert impact.probability == 0.15

    def test_translate_high_risk_temp(self, service):
        weather = {"temperature_2m": 42.0, "precipitation": 0.0}
        impact = service.translate_weather_to_impact(weather, "agro")
        assert impact.risk_level in ("high", "very_high")
        assert impact.probability >= 0.72

    def test_translate_medium_risk_low_precip(self, service):
        weather = {"temperature_2m": 25.0, "precipitation": 2.0}
        impact = service.translate_weather_to_impact(weather, "agro")
        assert impact.risk_level == "medium"

    def test_recommended_actions_not_empty(self, service):
        weather = {"temperature_2m": 25.0, "precipitation": 10.0}
        impact = service.translate_weather_to_impact(weather, "agro")
        assert len(impact.recommended_actions) > 0

    def test_unknown_sector_defaults(self, service):
        weather = {"temperature_2m": 25.0, "precipitation": 10.0}
        impact = service.translate_weather_to_impact(weather, "unknown_sector")
        assert impact.sector == "unknown_sector"
        assert impact.risk_level == "low"
