import logging

from fastapi import APIRouter, HTTPException, Query

from app.clients.nasa_power_client import NasaPowerClient
from app.config import settings
from app.models.weather_datapoint import ClimateImpact
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/climate", tags=["climate"])


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
    client = NasaPowerClient(settings.nasa_power_base_url)
    service = TranslationService()

    try:
        weather = await client.get_recent_weather(lat, lon)
    except Exception as e:
        logger.error("NASA POWER API error: %s", str(e))
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch weather data from NASA POWER: {str(e)}",
        )
    finally:
        await client.close()

    return service.translate_weather_to_impact(weather, sector, lang)
