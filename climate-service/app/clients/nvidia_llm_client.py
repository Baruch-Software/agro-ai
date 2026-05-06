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
        system_prompt = self._build_system_prompt(lang, sector)
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
            "max_tokens": 2000,
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

    def _build_system_prompt(self, lang: str, sector: str = "citizen") -> str:
        """Build system prompt for weather analysis."""
        lang_instruction = "Response in Spanish." if lang == "es" else "Response in English."

        sector_prompts = {
            "agro": (
                "FOR AGRICULTURE: Think like an agronomist. Each day say: "
                "can I spray? can I harvest? frost risk tonight? soil too wet for machinery? "
                "ideal sowing/planting window? wind too strong for fumigation (>15km/h)? "
                "Use farmer language: 'helada', 'ventana de fumigación', 'piso para maquinaria'."
            ),
            "energy": (
                "FOR ENERGY: Each day say: solar generation outlook (cloud cover %), "
                "wind generation potential (sustained wind speed), peak demand risk (extreme temps), "
                "grid stress probability. Be specific with generation percentages."
            ),
            "logistics": (
                "FOR LOGISTICS: Each day say: road conditions, visibility risk (fog/rain), "
                "wind restrictions for high-profile vehicles, flood risk for low routes, "
                "optimal departure windows. Think like a fleet dispatcher."
            ),
            "insurance": (
                "FOR INSURANCE: Each day say: parametric trigger probability, "
                "hail/frost/flood claim risk, crop damage probability, "
                "property damage risk. Quantify expected loss severity."
            ),
            "citizen": (
                "FOR GENERAL PUBLIC: Each day say in simple language: "
                "what to wear, umbrella needed?, outdoor plans safe?, "
                "health risks (heat/cold/UV/allergy), commute impact. "
                "Think like a friendly TV weather presenter giving practical advice."
            ),
        }
        sector_hint = sector_prompts.get(sector, "")

        return (
            "You are a senior meteorologist and sector consultant. Your job is to give "
            "PRACTICAL, DAY-BY-DAY forecasts that help people make real decisions.\n\n"
            "ANALYSIS METHOD:\n"
            "1. Read pressure trends, wind shifts, temp changes to identify weather systems.\n"
            "2. Compare current observations vs forecast to detect approaching changes.\n"
            "3. Translate each day into CONCRETE actions for the specific sector.\n\n"
            "CRITICAL RULES:\n"
            "- DO NOT write generic meteorological essays. Be DIRECT and PRACTICAL.\n"
            "- Each day in daily_outlook must have a one-line summary and 2-3 specific actions.\n"
            "- Use ACTUAL numbers from the data (temperatures, mm of rain, wind speed).\n"
            "- If a major weather change is coming (front, storm, polar outbreak), "
            "make it the CENTER of your response.\n"
            "- impact_description: 2 sentences MAX. What's the headline? What should they do NOW?\n"
            "- detailed_analysis: 2 short paragraphs MAX. Synoptic situation + practical outlook.\n"
            "- recommended_actions: TOP 3 most urgent actions, not generic advice.\n\n"
            f"{sector_hint}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "risk_level": "low|medium|high|very_high",\n'
            '  "impact_description": "2-sentence headline: what is happening + what to do now",\n'
            '  "probability": 0.0-1.0,\n'
            '  "recommended_actions": ["urgent action 1", "urgent action 2", "urgent action 3"],\n'
            '  "timeframe_hours": 24-168,\n'
            '  "detailed_analysis": "2 short paragraphs: synoptic situation + practical outlook",\n'
            '  "daily_outlook": [\n'
            "    {\n"
            '      "date": "YYYY-MM-DD",\n'
            '      "summary": "one-line: what happens this day + key number (temp/rain/wind)",\n'
            '      "risk_level": "low|medium|high|very_high",\n'
            '      "key_actions": ["concrete action 1", "concrete action 2"]\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "IMPORTANT: Return ONLY the JSON. No markdown, no code blocks.\n"
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
