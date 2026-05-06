import pytest

from app.clients.nvidia_llm_client import NvidiaLlmClient


class TestNvidiaLlmClient:
    """Tests for NvidiaLlmClient."""

    def test_init(self):
        client = NvidiaLlmClient("test-key")
        assert client.api_key == "test-key"
        assert client.model == "meta/llama-3.3-70b-instruct"

    def test_init_custom_model(self):
        client = NvidiaLlmClient("test-key", model="nvidia/nemotron-ultra")
        assert client.model == "nvidia/nemotron-ultra"

    def test_build_system_prompt_english(self):
        client = NvidiaLlmClient("test-key")
        prompt = client._build_system_prompt("en")
        assert "expert meteorologist" in prompt
        assert "Response in English" in prompt
        assert "JSON" in prompt

    def test_build_system_prompt_spanish(self):
        client = NvidiaLlmClient("test-key")
        prompt = client._build_system_prompt("es")
        assert "Response in Spanish" in prompt

    def test_build_user_prompt(self):
        client = NvidiaLlmClient("test-key")
        weather = {
            "date": "20260503",
            "temperature_2m": 11.68,
            "precipitation": 0.0,
            "humidity": 49.01,
            "wind_speed": 2.51,
            "solar_radiation": None,
        }
        prompt = client._build_user_prompt(weather, "agro", -31.4, -64.2, "en")
        assert "AGRICULTURE" in prompt
        assert "11.68°C" in prompt
        assert "Southern" in prompt

    def test_build_user_prompt_northern_hemisphere(self):
        client = NvidiaLlmClient("test-key")
        weather = {"temperature_2m": 25.0, "precipitation": 10.0}
        prompt = client._build_user_prompt(weather, "citizen", 40.7, -74.0, "en")
        assert "Northern" in prompt
        assert "GENERAL POPULATION" in prompt

    def test_parse_response_valid(self):
        client = NvidiaLlmClient("test-key")
        raw = {
            "choices": [
                {
                    "message": {
                        "content": '{"risk_level": "low", "impact_description": "test", "probability": 0.3, "recommended_actions": ["action1"], "timeframe_hours": 72, "detailed_analysis": "analysis"}'
                    }
                }
            ]
        }
        result = client._parse_response(raw)
        assert result is not None
        assert result["risk_level"] == "low"
        assert result["probability"] == 0.3

    def test_parse_response_with_markdown(self):
        client = NvidiaLlmClient("test-key")
        raw = {
            "choices": [
                {
                    "message": {
                        "content": '```json\n{"risk_level": "high", "impact_description": "test", "probability": 0.8, "recommended_actions": [], "timeframe_hours": 48, "detailed_analysis": "test"}\n```'
                    }
                }
            ]
        }
        result = client._parse_response(raw)
        assert result is not None
        assert result["risk_level"] == "high"

    def test_parse_response_invalid_json(self):
        client = NvidiaLlmClient("test-key")
        raw = {"choices": [{"message": {"content": "not json at all"}}]}
        result = client._parse_response(raw)
        assert result is None

    def test_parse_response_empty_choices(self):
        client = NvidiaLlmClient("test-key")
        result = client._parse_response({"choices": []})
        assert result is None
