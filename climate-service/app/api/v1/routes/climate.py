import logging

from fastapi import APIRouter, HTTPException, Query

from app.clients.nasa_power_client import NasaPowerClient
from app.clients.nvidia_llm_client import NvidiaLlmClient
from app.config import settings
from app.models.weather_datapoint import ClimateImpact
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/climate", tags=["climate"])

VALID_RISK_LEVELS = {"low", "medium", "high", "very_high"}


@router.get("/impact", response_model=ClimateImpact)
async def get_climate_impact(
    lat: float = Query(..., description="Latitude coordinate", ge=-90, le=90),
    lon: float = Query(..., description="Longitude coordinate", ge=-180, le=180),
    sector: str = Query(
        ...,
        description="Target sector",
        pattern="^(agro|energy|logistics|insurance|citizen)$",
    ),
    lang: str = Query(
        "en",
        description="Response language",
        pattern="^(en|es)$",
    ),
) -> ClimateImpact:
    """Get climate impact assessment for coordinates and sector."""
    nasa_client = NasaPowerClient(settings.nasa_power_base_url)
    fallback_service = TranslationService()

    try:
        weather = await nasa_client.get_recent_weather(lat, lon)
    except Exception as e:
        logger.error("NASA POWER API error: %s", str(e))
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch weather data from NASA POWER: {str(e)}",
        )
    finally:
        await nasa_client.close()

    if weather is None:
        return fallback_service.translate_weather_to_impact(None, sector, lang)

    if settings.nvidia_api_key:
        ai_result = await _analyze_with_ai(weather, sector, lat, lon, lang)
        if ai_result is not None:
            return ai_result

    logger.info("Using rule-based fallback for %s at (%s, %s)", sector, lat, lon)
    return fallback_service.translate_weather_to_impact(weather, sector, lang)


async def _analyze_with_ai(
    weather: dict,
    sector: str,
    lat: float,
    lon: float,
    lang: str,
) -> ClimateImpact | None:
    """Attempt AI-powered analysis, return None on failure."""
    llm_client = NvidiaLlmClient(settings.nvidia_api_key, settings.nvidia_model)
    try:
        analysis = await llm_client.analyze_weather(weather, sector, lat, lon, lang)
        if analysis is None:
            logger.warning("LLM returned unparseable response, falling back")
            return None

        risk_level = analysis.get("risk_level", "medium")
        if risk_level not in VALID_RISK_LEVELS:
            risk_level = "medium"

        probability = analysis.get("probability", 0.5)
        if not (0.0 <= probability <= 1.0):
            probability = 0.5

        return ClimateImpact(
            sector=sector,
            risk_level=risk_level,
            impact_description=analysis.get("impact_description", ""),
            probability=probability,
            recommended_actions=analysis.get("recommended_actions", []),
            timeframe_hours=analysis.get("timeframe_hours", 72),
            detailed_analysis=analysis.get("detailed_analysis"),
        )
    except Exception as e:
        logger.error("NVIDIA LLM error: %s — falling back to rules", str(e))
        return None
    finally:
        await llm_client.close()
