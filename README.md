# Agro-AI: Agricultural Intelligence & Climate-as-a-Service Ecosystem

## Project Structure

```
agro-ai/
├── docs/                    # Business & strategy documentation
├── climate-service/         # CaaS API (Python 3.14 + FastAPI)
├── agro-fin/                # [future] Agri-Financial Intelligence (C# .NET 10)
├── docker-compose.yml       # [future] Global orchestration
└── README.md
```

## Services

| Service | Tech | Port | Status |
|---------|------|------|--------|
| climate-service | Python 3.14 + FastAPI | 8000 | ✅ MVP |
| agro-fin | .NET 10 + CQRS | TBD | 🔜 Planned |

---

## Climate Service

### Quick Start

#### Option 1: Docker (recommended)

```bash
cd climate-service
docker-compose up -d --build
```

This starts 3 containers:

| Container | Port | Description |
|-----------|------|-------------|
| climate-service | 8000 | FastAPI API |
| climate-db | 5432 | PostgreSQL 16 |
| climate-redis | 6380 | Redis 7 |

#### Option 2: Local

```bash
cd climate-service
python3.14 -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Root / API info |
| GET | `/docs` | Swagger UI (interactive) |
| GET | `/redoc` | ReDoc documentation |
| GET | `/api/v1/climate/impact` | Climate impact assessment |

### Testing the API

#### Swagger UI (browser)

Open http://localhost:8000/docs — interactive UI to test all endpoints.

#### curl examples

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"healthy","version":"0.1.0"}

# Climate impact for agriculture in Córdoba, Argentina
curl "http://localhost:8000/api/v1/climate/impact?lat=-31&lon=-64&sector=agro"

# Climate impact for energy sector in Buenos Aires
curl "http://localhost:8000/api/v1/climate/impact?lat=-34.6&lon=-58.4&sector=energy"

# Climate impact for logistics
curl "http://localhost:8000/api/v1/climate/impact?lat=-32.9&lon=-60.6&sector=logistics"

# Climate impact for insurance
curl "http://localhost:8000/api/v1/climate/impact?lat=-31.4&lon=-64.2&sector=insurance"

# Invalid sector → 422 validation error
curl "http://localhost:8000/api/v1/climate/impact?lat=-31&lon=-64&sector=invalid"

# Invalid coordinates → 422 validation error
curl "http://localhost:8000/api/v1/climate/impact?lat=999&lon=-64&sector=agro"
```

### /api/v1/climate/impact

Returns climate impact assessment for a given location and sector.

**Query Parameters:**

| Param | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `lat` | float | yes | -90 to 90 | Latitude |
| `lon` | float | yes | -180 to 180 | Longitude |
| `sector` | string | yes | `agro`, `energy`, `logistics`, `insurance` | Target sector |

**Response:**

```json
{
  "sector": "agro",
  "risk_level": "unknown",
  "impact_description": "No weather data available for agro analysis",
  "probability": 0.0,
  "recommended_actions": ["Fetch weather data first"],
  "timeframe_hours": 0
}
```

**Risk levels:** `low`, `medium`, `high`, `very_high`, `unknown`

### Running Tests

```bash
cd climate-service
source ../venv/bin/activate
pytest tests/ -v
```

27 tests covering models, services, clients, and endpoint validation.

### Project Layout

```
climate-service/
├── app/
│   ├── api/v1/routes/       # API endpoints
│   │   └── climate.py       # /api/v1/climate/*
│   ├── clients/             # External API clients
│   │   ├── nasa_power_client.py
│   │   └── openweather_client.py
│   ├── models/              # Pydantic models
│   │   └── weather_datapoint.py
│   ├── services/            # Business logic
│   │   └── translation_service.py
│   ├── repositories/        # Data persistence
│   │   └── climate_repo.py
│   ├── core/                # Shared utilities
│   ├── config.py            # Settings (pydantic-settings)
│   └── main.py              # FastAPI app entrypoint
├── tests/                   # pytest test suite
├── scripts/                 # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── .env.example             # Environment template
└── .env                     # Local environment (git-ignored)
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp climate-service/.env.example climate-service/.env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENWEATHER_API_KEY` | yes | OpenWeather API key |
| `NASA_POWER_API_KEY` | no | NASA POWER API key |
| `DATABASE_URL` | yes | PostgreSQL connection string |
| `REDIS_URL` | yes | Redis connection string |
| `API_HOST` | no | Default: 0.0.0.0 |
| `API_PORT` | no | Default: 8000 |
| `LOG_LEVEL` | no | Default: INFO |

### Docker Commands

```bash
# Start all services
cd climate-service && docker-compose up -d --build

# View logs
docker-compose logs -f climate-service

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

---

## Documentation

Business and strategy docs in `docs/`:

| Document | Description |
|----------|-------------|
| [README_V2.md](docs/README_V2.md) | Project overview |
| [Propuesta_AgriFinancial_Intelligence.md](docs/Propuesta_AgriFinancial_Intelligence.md) | AgriFinancial module proposal |
| [Modelo_Negocio_Agro_Detallado.md](docs/Modelo_Negocio_Agro_Detallado.md) | Detailed business model |
| [Plan_Negocio_y_Monetizacion.md](docs/Plan_Negocio_y_Monetizacion.md) | Monetization strategy |
| [Estrategia_Climate_as_a_Service.md](docs/Estrategia_Climate_as_a_Service.md) | CaaS strategy |
| [REGLAS_DESARROLLO_AGRO_AI.md](docs/REGLAS_DESARROLLO_AGRO_AI.md) | Development rules |

## License

AGPL-3.0
