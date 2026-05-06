from app.core.i18n import SUPPORTED_LANGUAGES, get_translation


class TestI18nModule:
    """Tests for i18n module."""

    def test_supported_languages(self):
        assert "en" in SUPPORTED_LANGUAGES
        assert "es" in SUPPORTED_LANGUAGES

    def test_get_english(self):
        t = get_translation("en")
        assert "sectors" in t
        assert "citizen" in t["sectors"]

    def test_get_spanish(self):
        t = get_translation("es")
        assert t["sectors"]["citizen"] == "Población General"

    def test_unsupported_falls_back_to_english(self):
        t = get_translation("fr")
        assert t["sectors"]["agro"] == "Agriculture"

    def test_all_sectors_have_translations(self):
        sectors = ["agro", "energy", "logistics", "insurance", "citizen"]
        for lang in SUPPORTED_LANGUAGES:
            t = get_translation(lang)
            for sector in sectors:
                assert sector in t["sectors"]

    def test_all_risk_levels_have_actions(self):
        risk_levels = ["low", "medium", "high", "very_high"]
        for lang in SUPPORTED_LANGUAGES:
            t = get_translation(lang)
            for level in risk_levels:
                assert level in t["actions"]
                assert "default" in t["actions"][level]
                assert "citizen" in t["actions"][level]
