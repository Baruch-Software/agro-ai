from typing import Any

TRANSLATIONS: dict[str, dict[str, Any]] = {
    "en": {
        "sectors": {
            "agro": "Agriculture",
            "energy": "Energy",
            "logistics": "Logistics",
            "insurance": "Insurance",
            "citizen": "General Population",
        },
        "risk_levels": {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "very_high": "very high",
            "unknown": "unknown",
        },
        "no_data": "No weather data available for {sector} analysis",
        "fetch_first": "Fetch weather data first",
        "description": "{sector} sector: {risk_level} risk. Temperature: {temp}°C, Precipitation: {precip}mm.",
        "citizen_description": "General forecast: {risk_level} risk. Temperature: {temp}°C, Precipitation: {precip}mm.",
        "actions": {
            "low": {
                "default": ["Continue monitoring"],
                "citizen": ["Normal conditions, no precautions needed"],
            },
            "medium": {
                "default": ["Monitor closely", "Review contingency plans"],
                "citizen": [
                    "Stay hydrated and protect from sun exposure",
                    "Check forecast updates regularly",
                ],
            },
            "high": {
                "default": ["Activate contingency plans", "Notify stakeholders"],
                "citizen": [
                    "Avoid prolonged outdoor exposure",
                    "Keep emergency supplies ready",
                    "Follow local authority advisories",
                ],
            },
            "very_high": {
                "default": [
                    "Immediate action required",
                    "Activate emergency protocols",
                    "Notify all stakeholders",
                ],
                "citizen": [
                    "Stay indoors if possible",
                    "Follow evacuation orders if issued",
                    "Keep emergency kit accessible",
                    "Check on vulnerable neighbors",
                ],
            },
        },
    },
    "es": {
        "sectors": {
            "agro": "Agricultura",
            "energy": "Energía",
            "logistics": "Logística",
            "insurance": "Seguros",
            "citizen": "Población General",
        },
        "risk_levels": {
            "low": "bajo",
            "medium": "medio",
            "high": "alto",
            "very_high": "muy alto",
            "unknown": "desconocido",
        },
        "no_data": "No hay datos climáticos disponibles para análisis de {sector}",
        "fetch_first": "Obtenga datos climáticos primero",
        "description": "Sector {sector}: riesgo {risk_level}. Temperatura: {temp}°C, Precipitación: {precip}mm.",
        "citizen_description": "Pronóstico general: riesgo {risk_level}. Temperatura: {temp}°C, Precipitación: {precip}mm.",
        "actions": {
            "low": {
                "default": ["Continuar monitoreando"],
                "citizen": ["Condiciones normales, sin precauciones necesarias"],
            },
            "medium": {
                "default": ["Monitorear de cerca", "Revisar planes de contingencia"],
                "citizen": [
                    "Mantenerse hidratado y protegerse del sol",
                    "Consultar actualizaciones del pronóstico regularmente",
                ],
            },
            "high": {
                "default": [
                    "Activar planes de contingencia",
                    "Notificar a las partes interesadas",
                ],
                "citizen": [
                    "Evitar exposición prolongada al aire libre",
                    "Tener suministros de emergencia listos",
                    "Seguir avisos de autoridades locales",
                ],
            },
            "very_high": {
                "default": [
                    "Acción inmediata requerida",
                    "Activar protocolos de emergencia",
                    "Notificar a todas las partes interesadas",
                ],
                "citizen": [
                    "Permanecer en interiores si es posible",
                    "Seguir órdenes de evacuación si se emiten",
                    "Mantener kit de emergencia accesible",
                    "Verificar el estado de vecinos vulnerables",
                ],
            },
        },
    },
}

SUPPORTED_LANGUAGES = list(TRANSLATIONS.keys())


def get_translation(lang: str) -> dict[str, Any]:
    """Get translation dict for language, default to English."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])
