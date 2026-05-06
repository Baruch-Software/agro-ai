# FASE 1: API DE CLIMATE-AS-A-SERVICE (Python 3.14) - PLAN COMPLETO

## 🎯 OBJETIVO
Crear **SOLO** la API de clima: **Climate-as-a-Service** en Python 3.14 + FastAPI. **Nada de C#**, **Nada de AgroFin**, **Nada de monorepo**.

---

## 📋 REQUISITOS PREVIOS

1. **Python 3.14 instalado**
   ```bash
   python3.14 --version  # Debe mostrar 3.14.x
   ```

2. **GitHub CLI autenticado**
   ```bash
   gh auth status
   ```

3. **Docker instalado**
   ```bash
   docker --version
   ```

4. **Acceso a org Baruch-Software en GitHub**

---

## 🏁 PASO 0: SETUP INICIAL

### Paso 0.1: Crear directorio del proyecto
```bash
mkdir -p /Users/federicobenedetto/Documents/proyectos-propios/climate-service
cd /Users/federicobenedetto/Documents/proyectos-propios/climate-service
```

### Paso 0.2: Inicializar Git
```bash
git init
git branch -M main
```

### Paso 0.3: Crear repo en GitHub (Org Baruch-Software)
```bash
gh repo create Baruch-Software/climate-service --public \
  --description "Climate-as-a-Service API - Python 3.14 + FastAPI" \
  --source=. --remote=origin --push
```
**Resultado:** Repo creado en https://github.com/Baruch-Software/climate-service

### Paso 0.4: Crear ramas de desarrollo
```bash
git checkout -b develop
git push origin develop
git checkout -b feature/climate-ingestion
git push origin feature/climate-ingestion
```

---

## 📁 PASO 1: ESTRUCTURA DE DIRECTORIOS

### Paso 1.1: Crear directorios principales
```bash
cd /Users/federicobenedetto/Documents/proyectos-propios/climate-service

mkdir -p app/{api/v1/routes,models,services,repositories,clients,core}
mkdir -p tests
mkdir -p scripts
mkdir -p .github/workflows
```

**Verificación:**
```bash
tree -L 3  # Debe mostrar la estructura creada
```

Estructura esperada:
```
climate-service/
├── app/
│   ├── api/v1/routes/
│   ├── models/
│   ├── services/
│   ├── repositories/
│   ├── clients/
│   └── core/
├── tests/
├── scripts/
└── .github/workflows/
```

---

## ⚙️ PASO 2: CONFIGURACIÓN PYTHON 3.14

### Paso 2.1: pyproject.toml
**Archivo:** `/Users/federicobenedetto/Documents/proyectos-propios/climate-service/pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "climate-service"
version = "0.1.0"
description = "Climate-as-a-Service API with Python 3.14"
authors = [{name = "Federico Benedetto", email = "fede@example.com"}]
requires-python = ">=3.14"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.32.0",
  "pydantic>=2.9.0",
  "pydantic-settings>=2.2.0",
  "httpx>=0.27.0",
  "pandas>=2.2.0",
  "numpy>=1.26.0",
  "xarray>=2024.7.0",
  "requests>=2.32.0",
  "python-dotenv>=1.0.0",
  "redis>=5.0.1",
  "celery>=5.4.0",
  "pytest>=8.3.0",
  "pytest-asyncio>=0.24.0",
  "pytest-cov>=5.0.0",
  "factory-boy>=3.3.0"
]

[project.optional-dependencies]
dev = [
  "black>=24.8.0",
  "isort>=5.13.0",
  "flake8>=7.0.0",
  "mypy>=1.13.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=app --cov-report=html"

[tool.black]
line-length = 88
target-version = ["py314"]

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Paso 2.2: requirements.txt
```bash
cd /Users/federicobenedetto/Documents/proyectos-propios/climate-service
pip3.14 install pip-tools
pip-compile pyproject.toml  # Esto genera requirements.txt
```

### Paso 2.3: Entorno virtual Python 3.14
```bash
cd /Users/federicobenedetto/Documents/proyectos-propios/climate-service
python3.14 -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate
```

**Verificación:**
```bash
which python  # Debe mostrar .../climate-service/venv/bin/python
python --version  # Debe mostrar 3.14.x
```

### Paso 2.4: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 2.5: .env
**Archivo:** `/Users/federicobenedetto/Documents/proyectos-propios/climate-service/.env`

```bash
# API Keys
OPENWEATHER_API_KEY=your_openweather_key_here
NASA_POWER_API_KEY=

# URLs de APIs
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5
NASA_POWER_BASE_URL=https://power.larc.nasa.gov/api/v2

# Base de datos
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/climate_service

# Redis
REDIS_URL=redis://localhost:6379

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Logging
LOG_LEVEL=INFO
```

### Paso 2.6: .env.example
```bash
cp .env .env.example
# Luego editar .env.example y reemplazar keys con "YOUR_KEY_HERE"
```

---

## 📝 PASO 3: CÓDIGO BASE

### Paso 3.1: Crear `app/__init__.py`
**Archivo:** `/Users/federicobenedetto/Documents/proyectos-propios/climate-service/app/__init__.py`
```python
"""Climate-as-a-Service API."""
__version__ = "0.1.0"
```

### Paso 3.2: Crear `app/main.py`
**Archivo:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    print("🚀 ClimateService starting...")
    yield
    print("🔴 ClimateService shutting down...")

app = FastAPI(
    title="Climate-as-a-Service API",
    description="Interprets weather data into business impact",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}

@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Climate-as-a-Service API",
        "version": "0.1.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

### Paso 3.3: Crear `app/config.py`
**Archivo:**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    # APIs externas
    openweather_api_key: str
    nasa_power_api_key: Optional[str] = None
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    nasa_power_base_url: str = "https://power.larc.nasa.gov/api/v2"
    
    # Base de datos
    database_url: str
    
    # Redis
    redis_url: str
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

### Paso 3.4: Crear `app/models/__init__.py`
```python
"""Data models."""
```

### Paso 3.5: Crear `app/models/weather_datapoint.py`
**Archivo:**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WeatherDataPoint(BaseModel):
    """Weather data point from external APIs."""
    
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    timestamp: datetime = Field(..., description="Measurement timestamp")
    temperature_2m: Optional[float] = Field(None, description="Temperature at 2m (°C)")
    precipitation: Optional[float] = Field(None, description="Precipitation (mm)")
    humidity: Optional[float] = Field(None, description="Relative humidity (%)")
    wind_speed: Optional[float] = Field(None, description="Wind speed (m/s)")
    solar_radiation: Optional[float] = Field(None, description="Solar radiation (W/m²)")

class ClimateImpact(BaseModel):
    """Interpreted climate impact for specific sector."""
    
    sector: str = Field(..., description="Target sector (agro/energy/logistics/insurance)")
    risk_level: str = Field(..., description="Risk level: low/medium/high/very_high")
    impact_description: str = Field(..., description="Human-readable impact")
    probability: float = Field(..., ge=0, le=1, description="Probability 0-1")
    recommended_actions: list[str] = Field(default_factory=list)
    timeframe_hours: int = Field(..., description="Impact timeframe in hours")
```

### Paso 3.6: Crear `app/clients/__init__.py`
```python
"""External API clients."""
```

### Paso 3.7: Crear `app/clients/nasa_power_client.py`
**Archivo:**
```python
import httpx
from typing import Dict, Any

class NasaPowerClient:
    """NASA POWER API client."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_daily_data(self, lat: float, lon: float, start: str, end: str, **params) -> Dict[str, Any]:
        url = f"{self.base_url}/daily/point"
        params = {"latitude": lat, "longitude": lon, "start": start, "end": end, **params}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
```

### Paso 3.8: Crear `app/clients/openweather_client.py`
**Archivo:**
```python
import httpx
from typing import Dict, Any

class OpenWeatherClient:
    """OpenWeather API client."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        url = f"{self.base_url}/weather"
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
```

### Paso 3.9: Crear `app/services/__init__.py`
```python
"""Service layer."""
```

### Paso 3.10: Crear `app/services/translation_service.py`
**Archivo:**
```python
from app.models.weather_datapoint import ClimateImpact

class TranslationService:
    def translate_weather_to_impact(self, weather, sector: str) -> ClimateImpact:
        """Translate raw weather data to sector-specific impact."""
        # TODO: Implement actual logic
        return ClimateImpact(
            sector=sector,
            risk_level="medium",
            impact_description=f"Impact for {sector}",
            probability=0.5,
            recommended_actions=["Monitor closely", "Prepare contingencies"],
            timeframe_hours=72
        )
```

### Paso 3.11: Crear `app/repositories/__init__.py`
```python
"""Data persistence."""
```

### Paso 3.12: Crear `app/repositories/climate_repo.py`
**Archivo:**
```python
class ClimateRepository:
    """Repository for climate data storage."""
    
    async def save_weather_data(self, data):
        """Save weather data to PostgreSQL."""
        pass
    
    async def get_historical_data(self, lat, lon, start_date, end_date):
        """Retrieve historical data."""
        pass
```

### Paso 3.13: Crear `app/api/v1/routes/__init__.py`
```python
from fastapi import APIRouter

router = APIRouter()
```

### Paso 3.14: Crear `app/api/v1/routes/climate.py`
**Archivo:**
```python
from fastapi import APIRouter
from app.models.weather_datapoint import ClimateImpact
from app.services.translation_service import TranslationService

router = APIRouter(prefix="/api/v1/climate", tags=["climate"])

@router.get("/impact", response_model=ClimateImpact)
async def get_climate_impact(lat: float, lon: float, sector: str):
    service = TranslationService()
    # Mock data for now
    return service.translate_weather_to_impact(None, sector)
```

---

## 🧪 PASO 4: PRUEBAS

### Paso 4.1: Crear `tests/__init__.py`
```python
"""Test suite."""
```

### Paso 4.2: Crear `tests/conftest.py`
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
```

### Paso 4.3: Crear `tests/test_nasa_power_client.py`
```python
import pytest
from app.clients.nasa_power_client import NasaPowerClient

@pytest.mark.asyncio
async def test_nasa_power_client():
    client = NasaPowerClient("https://power.larc.nasa.gov/api/v2")
    data = await client.get_daily_data(lat=-31.0, lon=-64.0, start="20240101", end="20240131")
    assert "parameters" in data
```

### Paso 4.4: Crear `tests/test_openweather_client.py`
```python
import pytest
from app.clients.openweather_client import OpenWeatherClient

@pytest.mark.asyncio
async def test_openweather_client():
    client = OpenWeatherClient("https://api.openweathermap.org/data/2.5", "test_key")
    assert client.api_key == "test_key"
```

### Paso 4.5: Crear `tests/test_translation_service.py`
```python
from app.services.translation_service import TranslationService

def test_translation_service():
    service = TranslationService()
    impact = service.translate_weather_to_impact(None, "agro")
    assert impact.sector == "agro"
```

---

## 🐳 PASO 5: DOCKER

### Paso 5.1: Crear Dockerfile
```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Paso 5.2: Crear docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: climate-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: climate_service
    ports:
      - "5432:5432"
    volumes:
      - climate-postgres:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: climate-redis
    ports:
      - "6379:6379"

  climate-api:
    build: .
    container_name: climate-service
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/climate_service
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  climate-postgres:
```

### Paso 5.3: Build y run
```bash
docker-compose up -d --build
docker ps  # Ver containers corriendo
```

---

## ✅ CHECKLIST DE COMPLETADO

### Setup
- [ ] Directorio creado
- [ ] Git repo inicializado
- [ ] GitHub repo creado en Baruch-Software
- [ ] Ramas develop y feature creadas
- [ ] Estructura de directorios completa

### Python 3.14
- [ ] pyproject.toml creado
- [ ] requirements.txt generado
- [ ] venv creado y activado
- [ ] Dependencias instaladas
- [ ] .env creado

### Código
- [ ] app/__init__.py creado
- [ ] app/main.py creado
- [ ] app/config.py creado
- [ ] app/models creado
- [ ] app/clients creado
- [ ] app/services creado
- [ ] app/repositories creado
- [ ] app/api creado

### Tests
- [ ] tests/__init__.py creado
- [ ] tests/conftest.py creado
- [ ] tests test files creados
- [ ] pytest ejecuta sin errores

### Docker
- [ ] Dockerfile creado
- [ ] docker-compose.yml creado
- [ ] docker-compose up funciona

---

## 📊 ESTADO FINAL ESPERADO

```bash
# Verificar directorios
ls -la
# Debe mostrar: app/, tests/, scripts/, .github/, venv/, .env, pyproject.toml, requirements.txt

# Verificar archivos clave
ls app/api/v1/routes/climate.py  # Debe existir
ls app/clients/nasa_power_client.py  # Debe existir
ls app/main.py  # Debe existir

# Verificar tests
pytest -v  # Debe pasar (o al menos no fallar por imports)

# Verificar API
uvicorn app.main:app --reload --port 8000
# Abrir http://localhost:8000/docs  # Debe mostrar Swagger
```

---

## 🚀 PRÓXIMOS PASOS (CUANDO COMPLETES FASE 1)

1. **Probar API:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   # Abrir http://localhost:8000/docs
   # Probar endpoint: GET /api/v1/climate/impact?lat=-31&lon=-64&sector=agro
   ```

2. **Implementar NASA POWER ingestion:**
   - Crear `scripts/ingest_nasa.py` (daily cron)
   - Almacenar en PostgreSQL

3. **Implementar OpenWeather:**
   - Current weather endpoint
   - Forecast endpoint

4. **Implementar cálculo impacto:**
   - Traducir datos climáticos a impacto por sector
   - Mejorar `translation_service.py`

5. **Tests de integración:**
   - Mock external APIs
   - Testear traducción

6. **CI/CD con GitHub Actions:**
   - Run tests en PR
   - Deploy to Docker registry

7. **Base de datos PostgreSQL:**
   - Redis para cache
   - Tablas para datos climáticos

8. **API Key Management:**
   - Sistema de rate limiting
   - Billing por llamada

---

## 📚 DOCUMENTACIÓN

**Repo:** https://github.com/Baruch-Software/climate-service

**Endpoints:**
- `GET /health` - Health check
- `GET /` - Root
- `GET /api/v1/climate/impact` - Climate impact (requiere lat, lon, sector)

**Postman Collection:** Crear colección con:
- Base URL: http://localhost:8000
- GET /health
- GET /api/v1/climate/impact?lat=-31&lon=-64&sector=agro

**Environment Variables:**
- `OPENWEATHER_API_KEY`: Key de OpenWeather
- `NASA_POWER_API_KEY`: Key de NASA POWER (opcional)
- `DATABASE_URL`: PostgreSQL
- `REDIS_URL`: Redis

---

## 🎯 OBJETIVO DE LA FASE 1

**Entregables:**
- ✅ Repo GitHub con rama develop
- ✅ API FastAPI con Python 3.14
- ✅ Endpoints básicos funcionando
- ✅ Conexión a NASA POWER y OpenWeather
- ✅ Tests unitarios estructurados
- ✅ Docker configurado
- ✅ CI/CD preparado

**No incluye (Fase 2):**
- PostgreSQL integration
- Redis cache
- Ingestión diaria automática
- Billing system
- White-label customizations

---

## 📖 QUÉ HACER AHORA

1. **Leer** este documento completo
2. **Ejecutar** comandos Paso 0.1 a Paso 0.4
3. **Ejecutar** comandos Paso 1.1 a Paso 2.6
4. **Crear** todos los archivos de código (sección 3)
5. **Crear** todos los archivos de test (sección 4)
6. **Crear** Dockerfile y docker-compose.yml (sección 5)
7. **Ejecutar:** pytest
8. **Ejecutar:** docker-compose up -d --build
9. **Probar:** uvicorn app.main:app --reload --port 8000
10. **Abrir:** http://localhost:8000/docs

**Preguntas?** Revisar el checklist y verificar cada paso.

---

**Documento creado:** `/Users/federicobenedetto/Documents/proyectos-propios/agro-ai/PLAN_CLIMATE_SERVICE_PY314_COMPLETO.md`
**Fase:** 1 - Solo API Climate
**Python:** 3.14
**Fecha:** 2026-05-06
