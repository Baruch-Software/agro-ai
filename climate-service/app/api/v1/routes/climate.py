from fastapi import APIRouter, Query

from app.models.weather_datapoint import ClimateImpact
from app.services.translation_service import TranslationService

router = APIRouter(prefix="/api/v1/climate", tags=["climate"])


@router.get("/impact", response_model=ClimateImpact)
async def get_climate_impact(
    lat: float = Query(..., description="Latitude coordinate", ge=-90, le=90),
    lon: float = Query(..., description="Longitude coordinate", ge=-180, le=180),
    sector: str = Query(
        ..., description="Target sector", pattern="^(agro|energy|logistics|insurance)$"
    ),
) -> ClimateImpact:
    """Get climate impact assessment for coordinates and sector."""
    service = TranslationService()
    return service.translate_weather_to_impact(None, sector)
