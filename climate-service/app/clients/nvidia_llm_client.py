import json
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = "meta/llama-3.3-70b-instruct"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
    82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


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
        forecast: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Send weather + forecast data to LLM for expert analysis."""
        system_prompt = self._build_system_prompt(lang)
        user_prompt = self._build_user_prompt(
            weather_data, sector, lat, lon, lang, forecast
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1200,
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
            "You are a senior meteorologist with 25 years of operational forecasting experience, "
            "specializing in mesoscale weather analysis and sector-specific climate risk assessment. "
            "You interpret raw weather data the way a human forecaster at a national weather service would: "
            "identifying synoptic patterns, frontal passages, pressure tendencies, and their cascading "
            "impacts on specific economic sectors.\n\n"
            "YOUR METHODOLOGY:\n"
            "1. SYNOPTIC ANALYSIS: Read pressure trends, wind shifts, and temperature changes to identify "
            "weather systems (cold fronts, warm fronts, low-pressure centers, anticyclones).\n"
            "2. TEMPORAL PATTERN: Compare recent observations vs forecast to detect approaching changes "
            "(temperature drops = cold front, pressure falling = approaching low, wind direction shifts).\n"
            "3. SEVERITY ASSESSMENT: Quantify the magnitude — is this a minor cool-down or a major polar "
            "outbreak? Use thresholds relevant to the region and season.\n"
            "4. SECTOR IMPACT: Translate meteorological events into specific sector consequences with "
            "actionable detail (not generic advice).\n"
            "5. TIMING: Be precise about WHEN impacts will occur (tonight, tomorrow morning, next 48h).\n\n"
            "CRITICAL RULES:\n"
            "- If forecast shows a significant weather change (temp drop >8°C, front passage, storm), "
            "this MUST dominate your analysis. Do NOT focus on current calm conditions when a major "
            "change is forecast.\n"
            "- Be SPECIFIC: mention actual temperatures, wind speeds, precipitation amounts from the data.\n"
            "- Risk level MUST reflect the FORECAST, not just current conditions.\n"
            "- recommended_actions must be CONCRETE and ACTIONABLE for the specific sector.\n\n"
            "Return ONLY valid JSON with this exact structure:\n"
            "{\n"
            '  "risk_level": "low|medium|high|very_high",\n'
            '  "impact_description": "concise 2-3 sentence impact summary focusing on the most important change",\n'
            '  "probability": 0.0-1.0,\n'
            '  "recommended_actions": ["specific action 1", "specific action 2", "specific action 3"],\n'
            '  "timeframe_hours": 24-168,\n'
            '  "detailed_analysis": "Full professional meteorological briefing (3-4 paragraphs): '
            "synoptic situation, expected evolution, sector impacts, and timing. "
            'Write as if briefing a client who needs to make operational decisions."\n'
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
        forecast: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build enriched prompt with historical + forecast data."""
        sector_labels = {
            "agro": "AGRICULTURE (crops, livestock, irrigation, frost risk, harvest windows)",
            "energy": "ENERGY (solar/wind generation, demand peaks, grid stress, renewable output)",
            "logistics": "LOGISTICS (transport safety, route conditions, delivery schedules, port operations)",
            "insurance": "INSURANCE (parametric trigger assessment, claims probability, loss estimation)",
            "citizen": "GENERAL POPULATION (daily planning, health risks, outdoor safety, commute impact)",
        }
        sector_label = sector_labels.get(sector, sector.upper())

        hemisphere = "Southern" if lat < 0 else "Northern"
        parts = []

        parts.append(
            f"WEATHER ANALYSIS REQUEST for {sector_label} sector\n"
            f"Location: ({lat}, {lon}) — {hemisphere} Hemisphere\n"
            f"{'=' * 60}"
        )

        parts.append(self._format_recent_observations(weather))

        if forecast:
            parts.append(self._format_forecast_data(forecast))

        parts.append(
            f"\nINSTRUCTION: Analyze ALL data above as a professional meteorologist. "
            f"Focus on what CHANGES are coming and their impact on {sector_label.lower()}. "
            f"If a significant weather event is approaching (front, storm, heat wave, polar outbreak), "
            f"make it the CENTER of your analysis."
        )

        return "\n\n".join(parts)

    def _format_recent_observations(self, weather: dict[str, Any]) -> str:
        """Format NASA POWER historical data."""
        date = weather.get("date", "unknown")
        temp = weather.get("temperature_2m", "N/A")
        precip = weather.get("precipitation", "N/A")
        humidity = weather.get("humidity", "N/A")
        wind = weather.get("wind_speed", "N/A")
        solar = weather.get("solar_radiation", "N/A")

        return (
            f"SECTION 1 — RECENT OBSERVATIONS (NASA POWER satellite data)\n"
            f"Date: {date}\n"
            f"Temperature (2m): {temp}°C\n"
            f"Precipitation: {precip} mm\n"
            f"Relative Humidity: {humidity}%\n"
            f"Wind Speed (2m): {wind} m/s\n"
            f"Solar Radiation: {solar} MJ/m²/day"
        )

    def _format_forecast_data(self, forecast: dict[str, Any]) -> str:
        """Format Open-Meteo forecast data for LLM consumption."""
        parts = []
        timezone = forecast.get("timezone", "UTC")
        pressure_trend = forecast.get("pressure_trend", "unknown")

        parts.append(
            f"SECTION 2 — 7-DAY FORECAST (ECMWF/GFS/ICON models via Open-Meteo)\n"
            f"Timezone: {timezone}\n"
            f"Barometric Pressure Trend (24h): {pressure_trend}"
        )

        daily = forecast.get("daily_forecast", [])
        if daily:
            parts.append("DAILY FORECAST:")
            for day in daily:
                wc = day.get("weather_code")
                weather_desc = WEATHER_CODES.get(wc, "Unknown") if wc is not None else "N/A"
                parts.append(
                    f"  {day['date']}: "
                    f"{day.get('temp_min', '?')}°C → {day.get('temp_max', '?')}°C "
                    f"(feels {day.get('apparent_temp_min', '?')}→{day.get('apparent_temp_max', '?')}°C) | "
                    f"Precip: {day.get('precipitation_sum', 0)}mm ({day.get('precipitation_probability', 0)}%) | "
                    f"Wind: {day.get('wind_max', '?')}m/s gusts {day.get('wind_gusts_max', '?')}m/s "
                    f"dir {day.get('wind_direction', '?')}° | "
                    f"UV: {day.get('uv_index_max', '?')} | {weather_desc}"
                )

        hourly = forecast.get("next_24h_hourly", [])
        if hourly:
            parts.append("NEXT 24H HOURLY DETAIL:")
            for h in hourly:
                wc = h.get("weather_code")
                weather_desc = WEATHER_CODES.get(wc, "") if wc is not None else ""
                parts.append(
                    f"  {h['time']}: {h.get('temp', '?')}°C "
                    f"(feels {h.get('apparent_temp', '?')}°C) | "
                    f"Humidity: {h.get('humidity', '?')}% | "
                    f"Precip: {h.get('precipitation', 0)}mm ({h.get('precip_probability', 0)}%) | "
                    f"Pressure: {h.get('pressure_msl', '?')}hPa | "
                    f"Cloud: {h.get('cloud_cover', '?')}% | "
                    f"Wind: {h.get('wind_speed', '?')}m/s gusts {h.get('wind_gusts', '?')} "
                    f"dir {h.get('wind_direction', '?')}° "
                    f"{'| ' + weather_desc if weather_desc else ''}"
                )

        return "\n".join(parts)

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
