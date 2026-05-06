import pytest

from app.services.translation_service import TranslationService


class TestTranslationService:
    """Tests for TranslationService."""

    @pytest.fixture
    def service(self) -> TranslationService:
        return TranslationService()

    @pytest.mark.parametrize("sector", ["agro", "energy", "logistics", "insurance", "citizen"])
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


class TestCitizenSector:
    """Tests for citizen sector specifics."""

    @pytest.fixture
    def service(self) -> TranslationService:
        return TranslationService()

    def test_citizen_high_temp(self, service):
        weather = {"temperature_2m": 38.0, "precipitation": 0.0}
        impact = service.translate_weather_to_impact(weather, "citizen")
        assert impact.risk_level in ("high", "very_high")

    def test_citizen_freezing(self, service):
        weather = {"temperature_2m": -5.0, "precipitation": 10.0}
        impact = service.translate_weather_to_impact(weather, "citizen")
        assert impact.risk_level in ("high", "very_high")

    def test_citizen_normal_conditions(self, service):
        weather = {"temperature_2m": 22.0, "precipitation": 5.0}
        impact = service.translate_weather_to_impact(weather, "citizen")
        assert impact.risk_level == "low"

    def test_citizen_heavy_rain(self, service):
        weather = {"temperature_2m": 20.0, "precipitation": 50.0}
        impact = service.translate_weather_to_impact(weather, "citizen")
        assert impact.risk_level in ("high", "very_high")

    def test_citizen_actions_differ_from_default(self, service):
        weather = {"temperature_2m": 38.0, "precipitation": 0.0}
        citizen_impact = service.translate_weather_to_impact(weather, "citizen")
        agro_impact = service.translate_weather_to_impact(weather, "agro")
        assert citizen_impact.recommended_actions != agro_impact.recommended_actions


class TestI18n:
    """Tests for language support in translation service."""

    @pytest.fixture
    def service(self) -> TranslationService:
        return TranslationService()

    def test_spanish_no_data(self, service):
        impact = service.translate_weather_to_impact(None, "agro", lang="es")
        assert "No hay datos climáticos" in impact.impact_description
        assert "Obtenga datos climáticos primero" in impact.recommended_actions

    def test_english_no_data(self, service):
        impact = service.translate_weather_to_impact(None, "agro", lang="en")
        assert "No weather data available" in impact.impact_description

    def test_spanish_with_weather(self, service):
        weather = {"temperature_2m": 22.0, "precipitation": 10.0}
        impact = service.translate_weather_to_impact(weather, "agro", lang="es")
        assert "Agricultura" in impact.impact_description
        assert "bajo" in impact.impact_description

    def test_english_with_weather(self, service):
        weather = {"temperature_2m": 22.0, "precipitation": 10.0}
        impact = service.translate_weather_to_impact(weather, "agro", lang="en")
        assert "Agriculture" in impact.impact_description
        assert "low" in impact.impact_description

    def test_spanish_citizen(self, service):
        weather = {"temperature_2m": 22.0, "precipitation": 5.0}
        impact = service.translate_weather_to_impact(weather, "citizen", lang="es")
        assert "Pronóstico general" in impact.impact_description

    def test_english_citizen(self, service):
        weather = {"temperature_2m": 22.0, "precipitation": 5.0}
        impact = service.translate_weather_to_impact(weather, "citizen", lang="en")
        assert "General forecast" in impact.impact_description

    def test_spanish_actions(self, service):
        weather = {"temperature_2m": 38.0, "precipitation": 0.0}
        impact = service.translate_weather_to_impact(weather, "citizen", lang="es")
        assert any("Evitar" in a or "Permanecer" in a for a in impact.recommended_actions)

    def test_unsupported_lang_defaults_english(self, service):
        weather = {"temperature_2m": 22.0, "precipitation": 10.0}
        impact = service.translate_weather_to_impact(weather, "agro", lang="fr")
        assert "Agriculture" in impact.impact_description
