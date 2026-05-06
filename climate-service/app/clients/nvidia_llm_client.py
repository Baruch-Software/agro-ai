import json
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = "meta/llama-3.3-70b-instruct"


class NvidiaLlmClient:
    """NVIDIA NIM LLM client for AI-powered weather analysis."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)

    async def analyze_weather(
        self,
        weather_data: dict[str, Any],
        sector: str,
        lat: float,
        lon: float,
        lang: str = "en",
    ) -> Optional[dict[str, Any]]:
        """Send weather data to LLM for expert analysis."""
        system_prompt = self._build_system_prompt(lang)
        user_prompt = self._build_user_prompt(weather_data, sector, lat, lon, lang)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 800,
        }

        response = await self.client.post(
            NVIDIA_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return self._parse_response(response.json())

    def _build_system_prompt(self, lang: str) -> str:
        """Build system prompt for weather analysis."""
        lang_instruction = "Response in Spanish." if lang == "es" else "Response in English."

        return (
            "You are an expert meteorologist and climate risk analyst with 20 years of experience. "
            "You analyze weather data with the precision of a professional forecaster, considering "
            "seasonal context, regional climate patterns, and sector-specific impacts.\n\n"
            "Return ONLY valid JSON with this exact structure:\n"
            "{\n"
            '  "risk_level": "low|medium|high|very_high",\n'
            '  "impact_description": "concise 1-2 sentence impact summary",\n'
            '  "probability": 0.0-1.0,\n'
            '  "recommended_actions": ["action1", "action2", "action3"],\n'
            '  "timeframe_hours": 72,\n'
            '  "detailed_analysis": "expert meteorological analysis paragraph"\n'
            "}\n\n"
            "IMPORTANT: Return ONLY the JSON object. No markdown, no code blocks, no extra text.\n"
            f"{lang_instruction}"
        )

    def _build_user_prompt(
        self,
        weather: dict[str, Any],
        sector: str,
        lat: float,
        lon: float,
        lang: str,
    ) -> str:
        """Build user prompt with weather data and context."""
        sector_labels = {
            "agro": "AGRICULTURE (crops, livestock, irrigation)",
            "energy": "ENERGY (solar/wind generation, demand)",
            "logistics": "LOGISTICS (transport, routes, delivery)",
            "insurance": "INSURANCE (claims risk, parametric triggers)",
            "citizen": "GENERAL POPULATION (daily life, health, safety)",
        }
        sector_label = sector_labels.get(sector, sector.upper())

        hemisphere = "Southern" if lat < 0 else "Northern"
        temp = weather.get("temperature_2m", "N/A")
        precip = weather.get("precipitation", "N/A")
        humidity = weather.get("humidity", "N/A")
        wind = weather.get("wind_speed", "N/A")
        solar = weather.get("solar_radiation", "N/A")
        date = weather.get("date", "unknown")

        return (
            f"Analyze this weather data for the {sector_label} sector "
            f"at coordinates ({lat}, {lon}):\n\n"
            f"Date: {date}\n"
            f"Temperature: {temp}°C\n"
            f"Precipitation: {precip}mm\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind} m/s\n"
            f"Solar Radiation: {solar} MJ/m²/day\n\n"
            f"Hemisphere: {hemisphere}\n"
            f"Consider seasonal context, regional patterns, "
            f"and {sector_label.lower()} specific risks."
        )

    def _parse_response(self, raw: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Extract and parse JSON from LLM response."""
        choices = raw.get("choices", [])
        if not choices:
            return None

        content = choices[0].get("message", {}).get("content", "")
        content = content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON: %s", content[:200])
            return None

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
