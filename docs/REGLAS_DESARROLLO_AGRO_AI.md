# REGLAS DE DESARROLLO - AGRO-AI ECOSISTEMA

**Propósito:** Documento central de reglas para desarrollo en el ecosistema Agro-AI. Aplica a TODOS los microservicios y componentes.

**Versión:** 1.0
**Fecha:** 2026-05-06
**Aplica a:** C#, Python, Docker, Git, CI/CD, Testing

---

## 📋 REGLAS FUNDAMENTALES (NO NEGOCIABLES)

### 1. ENGLÉS EN TODO EL CÓDIGO
- **TODOS** los nombres de variables, funciones, clases, archivos, comentarios DEBEN ser en inglés
- **NINGUNA** palabra en español en el código
- **NO** usar nombres en español: `prepararDatos`, `obtenerUsuario`, `calcularMargen`
- **SÍ** usar: `prepare_data`, `get_user`, `calculate_margin`

### 2. CIUDADO CON LOS SECRETOS
- **NUNCA** commitear archivos `.env`, `secrets.json`, `config.py` con credenciales reales
- **SIEMPRE** usar `.env.example` con placeholders
- **NUNCA** hardcodear API keys en el código fuente
- **SIEMPRE** usar GitHub Secrets para CI/CD

### 3. GIT WORKFLOW ESTRCTO
- **main** → Producción (protegida, requiere PR + 2 aprobaciones)
- **develop** → Desarrollo (rama base para features)
- **feature/nombre** → Features individuales
- **hotfix/nombre** → Parches urgentes
- **Convención commits:** `feat:`, `fix:`, `refactor:`, `test:`, `docs:`

### 4. CODE REVIEW OBLIGATORIO
- **NUNCA** merge directo a main/develop
- **SIEMPRE** Pull Request con descripción detallada
- **SIEMPRE** 2 aprobaciones mínimo
- **SIEMPRE** CI pipeline verde

### 5. TESTING EXHAUSTIVO
- **TODOS** los servicios deben tener tests
- **MINIMO** 80% coverage (pytest-cov para Python, Coverlet para C#)
- **NUNCA** enviar código sin tests
- **SIEMPRE** tests pasan antes de PR

---

## 🔧 REGLAS POR TECNOLOGÍA

### REGLAS C# (AgroFin)

#### 5.1 Arquitectura CQRS (Estricta)
```
Microservicio/
├── Api/ (ASP.NET Core)
├── Application/ (Commands, Queries, Handlers, Validators)
├── Domain/ (Entities, Interfaces)
├── Infrastructure.Persistence/ (EF Configs, Repositories)
├── Infrastructure.Shared/ (Extensions, Helpers)
├── UnitTest/
├── IntegrationTest/
└── CliTool/
```

#### 5.2 Entidades (Clases OBLIGATORIAS)
```csharp
// ✅ CORRECTO - Entity como CLASE
public class FarmLot : BaseEntity
{
    public string Name { get; set; } = string.Empty;
}

// ❌ INCORRECTO - Entity como RECORD
public record FarmLot(string Name);  // NO PERMITIDO
```

#### 5.3 Configuración EF (SetupSchemaAndName OBLIGATORIO)
```csharp
// SIEMPRE en EntityConfiguration.cs
builder.SetupSchemaAndName();  // PRIMERA LINEA
builder.HasKey(e => e.Id);
builder.DefineColumn(e => e.Id);  // Para CADA propiedad
```

#### 5.4 Repository Pattern (UnitOfWork OBLIGATORIO)
```csharp
// ✅ CORRECTO - Obtener via UnitOfWork
var repository = UnitOfWork.GetRepository<FarmLot>();

// ❌ INCORRECTO - Inyección directa
public class Service(IRepository<FarmLot> repo)  // NO PERMITIDO
```

#### 5.5 Commands/Queries (Records vs Clases)
```csharp
// ✅ Commands → RECORDS (inmutables)
public record CreateFarmLotCommand(string Name, decimal Hectares)
    : ICommandBase<FarmLotDto>;

// ✅ Queries → RECORDS
public record GetFarmLotByIdQuery(long Id)
    : IQueryBase<FarmLotDto>;

// ✅ Handlers → CLASES
public class CreateFarmLotCommandHandler
    : CommandHandlerBase<CreateFarmLotCommand, FarmLotDto>;
```

#### 5.6 Tests (Theory + AAA PATTERN OBLIGATORIO)
```csharp
// ✅ CORRECTO - Theory + AAA
[Theory]
[InlineData("Test 1", 100.5)]
[InlineData("Test 2", 250.0)]
public async Task Create_WithValidData_ShouldCreate(string name, decimal hectares)
{
    // Arrange
    var command = new CreateFarmLotCommand(name, hectares);
    
    // Act
    var result = await handler.Handle(command, CancellationToken.None);
    
    // Assert
    Assert.True(result.Succeeded);
}

// ❌ INCORRECTO - Fact with comments
[Fact]
public async Task Test() // Comentarios no permitidos
{
    // Arrange (NO)
    // Act (NO)
    // Assert (NO)
}
```

#### 5.7 Migrations (Process estricto)
```bash
# 1. Crear entity
# 2. Crear Configuration
# 3. Add DbSet a DbContext
# 4. Generar migración
dotnet ef migrations add AddNewEntity \
  --project Microservicio/Microservicio.Infrastructure.Persistence \
  --startup-project Microservicio/Microservicio.Api \
  --context MicroservicioDbContext

# 5. Aplicar
dotnet ef database update \
  --project Microservicio/Microservicio.Infrastructure.Persistence \
  --startup-project Microservicio/Microservicio.Api \
  --context MicroservicioDbContext
```

---

### REGLAS PYTHON (ClimateService)

#### 6.1 Estructura de directorios (Estricta)
```
service-name/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── routes/
│   │           └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── *.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── *.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── *.py
│   └── clients/
│       ├── __init__.py
│       └── *.py
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── scripts/
├── .github/
│   └── workflows/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── .env
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

#### 6.2 Dominio y tipos
```python
# ✅ CORRECTO - Usar Pydantic BaseModel
from pydantic import BaseModel, Field

class WeatherData(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
```

#### 6.3 Tests con pytest (OBLIGATORIO)
```python
# ✅ CORRECTO
import pytest
from fastapi.testclient import TestClient

def test_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200

# ✅ async tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

# ❌ NO skipped tests sin razón
@pytest.mark.skip  # Solo con razón documentada
```

#### 6.4 Typing (Estricto)
```python
# ✅ CORRECTO - Anotaciones de tipos explícitas
from typing import Dict, List, Optional, Any

def process_data(data: Dict[str, Any]) -> List[WeatherData]:
    return [WeatherData(**item) for item in data]

# ❌ NO Any sin razón
# ❌ NO omitir tipos de retorno
```

#### 6.5 Clientes HTTP (httpx OBLIGATORIO)
```python
# ✅ CORRECTO - Usar httpx.AsyncClient
import httpx

class NasaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def fetch(self, url: str) -> dict:
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
```

#### 6.6 Environment Variables (pydantic-settings OBLIGATORIO)
```python
# ✅ CORRECTO - pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    base_url: str
    
    model_config = SettingsConfigDict(env_file=".env")
```

---

## 📁 REGLAS GENERALES (Todas tecnologías)

### 7.1 Nombres de archivos
- **SIEMPRE** minúsculas y guiones bajos: `weather_data.py`, `api_client.py`
- **NUNCA** espacios: `weather data.py`
- **NUNCA** camelCase: `WeatherData.py`
- **EXCEPTIÓN:** Archivos de clase en C#: `FarmLot.cs`

### 7.2 Imports organizados
```python
# ✅ CORRECTO Python
import os
import sys

from fastapi import FastAPI
from pydantic import BaseModel

from app.models import WeatherData

# ✅ CORRECTO C#
using System;
using Microsoft.EntityFrameworkCore;
using AgroFin.Domain.Entities;

// ❌ NO System.* sin filtrar
```

### 7.3 Documentación
- **TODOS** métodos públicos DEBEN tener docstrings/xml comments
- **TODOS** endpoints DEBEN tener descripción
- **EJEMPLO Python:**
```python
async def get_weather(lat: float, lon: float) -> WeatherData:
    """Fetch current weather for coordinates."""
    ...
```
- **EJEMPLO C#:**
```csharp
/// <summary>
/// Calculate margin for farm lot
/// </summary>
public async Task<MarginDto> CalculateMargin(long farmLotId) { ... }
```

### 7.4 Git y commits
- **SIEMPRE** commits descriptivos: `feat: Add NASA POWER client`  
- **NUNCA** commits vacíos o "fix bug"
- **SIEMPRE` branches descriptivas: `feature/nasa-power-ingestion`
- **NUNCA** `feature/fix-1`, `bug/ticket`

### 7.5 Pull Requests
- Descripción clara de qué hace y por qué
- Checklist de tests pasando
- Screenshots si aplica
- Link a issue relacionado

### 7.6 Versionado
- **Version:** `0.x.x` → beta
- **Version:** `1.x.x` → producción
- **CHANGELOG.md** mantenido con conventional commits

### 7.7 Linters y formatters
```bash
# Python (OBLIGATORIO)
black . --check  # Formateo
isort . --check-only  # Orden imports
flake8 .  # Linting
mypy .  # Type checking

# C# (OBLIGATORIO)
dotnet format --verify-no-changes
dotnet build --no-restore
dotnet test --no-build
```

---

## 🐳 REGLAS DOCKER

### 8.1 Dockerfile standards
```dockerfile
# ✅ CORRECTO - Multi-stage build para C#
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore
RUN dotnet publish -c Release -o /app
FROM base AS final
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "Microservicio.Api.dll"]
```

```dockerfile
# ✅ CORRECTO - Python 3.14
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 docker-compose.yml
```yaml
# ✅ CORRECTO - Services con nombres claros
services:
  agro-fin-api:
    build: ./microservices/AgroFin
  
  climate-service:
    build: ./microservices/ClimateService
  
  postgres:
    image: postgres:16-alpine

# ✅ OBLIGATORIO - Volumenes nombrados
volumes:
  agro-postgres:
  climate-postgres:
```

### 8.3 Environment variables
```yaml
# ✅ CORRECTO - Variables en docker-compose, no en Dockerfile
environment:
  - DATABASE_URL=postgresql://user:pass@postgres:5432/db
  - API_KEY=${API_KEY}  # From host .env
```

---

## 🔍 REGLAS DE CALIDAD Y SEGURIDAD

### 9.1 Security checks
- **NUNCA** exponer secrets en logs
- **SIEMPRE` validar input en endpoints (pydantic, FluentValidation)
- **SIEMPRE** sanitize data antes de DB queries (SQL injection)
- **SIEMPRE** HTTPS en producción
- **NUNCA** deshabilitar certificado SSL verify

### 9.2 Performance
- **SIEMPRE** paginar queries con más de 100 registros
- **SIEMPRE** usar `IQueryable` en C# o generadores en Python
- **NUNCA** N+1 queries pattern
- **SIEMPRE** implementar caching (Redis)

### 9.3 Error handling
```python
# ✅ CORRECTO Python
from fastapi import HTTPException

try:
    result = await process_data()
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail="Internal error")
```

```csharp
// ✅ CORRECTO C#
try { ... }
catch (ValidationException ex)
{
    return new Response<T>(ex.Message);
}
catch (Exception ex)
{
    return new Response<T>("Internal error");
}
```

### 9.4 Monitoring
- **SIEMPRE** loggear errores importantes
- **SIEMPRE** métricas con Prometheus/Grafana
- **SIEMPRE** health checks endpoints

---

## 📊 CHECKLIST DE CALIDAD PRE-COMMIT

### Antes de cada commit
- [ ] Código en inglés
- [ ] Tests pasan
- [ ] Coverage > 80%
- [ ] Linters sin errores (black, flake8, dotnet format)
- [ ] Typing correcto (mypy, compiler)
- [ ] Imports organizados
- [ ] .env no commiteado
- [ ] No secretos en código
- [ ] PR description completo
- [ ] CI pipeline verde

### Antes de merge a develop
- [ ] 2 aprobaciones
- [ ] Todos los tests pasan
- [ ] Review de seguridad
- [ ] Review de performance

### Antes de merge a main
- [ ] 3 aprobaciones
- [ ] QA aprobado
- [ ] Performance test pasado
- [ ] Security audit pasado

---

## 📝 PLANTILLAS DE CÓDIGO

### Plantilla de Entity (C#)
```csharp
namespace Microservicio.Domain.Entities;

public class EntityName : BaseEntity
{
    public string PropertyName { get; set; } = string.Empty;
    public decimal NumericProperty { get; set; }
}
```

### Plantilla de Configuration (C#)
```csharp
namespace Microservicio.Infrastructure.Persistence.Configurations;

public class EntityNameConfiguration : IEntityTypeConfiguration<EntityName>
{
    public void Configure(EntityTypeBuilder<EntityName> builder)
    {
        builder.SetupSchemaAndName();
        builder.HasKey(e => e.Id);
        builder.DefineColumn(e => e.Id);
        builder.DefineColumn(e => e.PropertyName).HasMaxLength(200);
        builder.DefineColumn(e => e.NumericProperty);
    }
}
```

### Plantilla de Model (Python)
```python
from pydantic import BaseModel, Field

class ModelName(BaseModel):
    property_name: str = Field(..., description="Property description")
    numeric_property: float = Field(..., description="Numeric property")
```

### Plantilla de Test (Python)
```python
import pytest

class ServiceName:
    def method(self):
        pass

def test_method():
    service = ServiceName()
    result = service.method()
    assert result is not None
```

---

## 🚀 GIT COMMANDS REFERENCE

### Crear feature
```bash
git checkout -b feature/nombre-descriptivo
git commit -m "feat: Add new domain logic"
git push origin feature/nombre-descriptivo
```

### Actualizar develop
```bash
git checkout develop
git pull --rebase origin develop
```

### Merge feature a develop (via PR)
```bash
git checkout develop
git merge --squash feature/nombre-descriptivo
git push origin develop
git branch -d feature/nombre-descriptivo
git push origin --delete feature/nombre-descriptivo
```

### Hotfix (via PR)
```bash
git checkout -b hotfix/urgent-fix main
# ... fixes ...
git checkout main
git merge hotfix/urgent-fix
git push origin main
git checkout develop
git merge main
git push origin develop
```

---

## 📦 COMANDOS ÚTILES SAVE

### C# CQRS New Entity (Copy-paste)
```bash
# Entity
cd Microservicio/Microservicio.Domain/Entities
touch EntityName.cs

# Configuration
cd Microservicio/Microservicio.Infrastructure.Persistence/Configurations
touch EntityNameConfiguration.cs

# Command
cd Microservicio/Microservicio.Application/Commands
public record CreateEntityNameCommand(...) : ICommandBase<EntityNameDto>;

# Handler
cd Microservicio/Microservicio.Application/Features/Handlers
public class CreateEntityNameCommandHandler : CommandHandlerBase<...> { ... }

# DTO
cd Microservicio/Microservicio.Application/DTOs
public record EntityNameDto(...);

# Test
cd Microservicio/Microservicio.UnitTest/Handlers
public class CreateEntityNameCommandHandlerTests : BaseUnitTest { ... }

# Migration
cd Microservicio
dotnet ef migrations add AddEntityName --project Microservicio.Infrastructure.Persistence --startup-project Microservicio.Api --context MicroservicioDbContext
dotnet ef database update --project Microservicio.Infrastructure.Persistence --startup-project Microservicio.Api --context MicroservicioDbContext
```

### Python New API Component
```bash
# Model
cd app/models
touch new_model.py

# Service
cd app/services
touch new_service.py

# Test
cd tests/ touch test_new_service.py

# Route
cd app/api/v1/routes
touch new_route.py

# Add to main.py
# Import y app.include_router(...)
```

---

## 📚 DOCUMENTACIÓN REQUERIDA

### Cada microservicio debe tener:
- [ ] README.md (instalación, configuración, uso)
- [ ] CONTRIBUTING.md (guía de desarrollo)
- [ ] CHANGELOG.md (versiones y cambios)
- [ ] LICENSE (AGPL-3.0)
- [ ] `.cursorrules` (copia de reglas)
- [ ] `/docs/` folder (ADR, decisiones técnicas)

### ADR (Architectural Decision Records)
```
/docs/adr/
├── adr-001-cqrs-selection.md
├── adr-002-python-3-14.md
├── adr-003-fastapi-vs-flask.md
└── adr-004-postgres-vs-mongodb.md
```

---

## 🎯 METAS DE CALIDAD

### Coverage mínimo
- **Unit tests:** 80%
- **Integration tests:** 70%
- **Acceptance tests:** 60%

### Performance en producción
- **Response time:** <200ms p95
- **Availability:** 99.9%
- **Concurrent users:** 1000+

### Seguridad
- **No vulnerabilities** (Snyk scan)
- **Penetration test** aprobado
- **Dependencias actualizadas** (dependabot)

---

## 🚨 ERRORES COMUNES Y SOLUCIONES

### Error: "dotnet build failed"
**Solución:** Verificar packages, restore con `dotnet restore`

### Error: "ImportError Python"
**Solución:** Reinstall venv, check Python 3.14 is active

### Error: "docker-compose up fails"
**Solución:** Check ports, volumes, .env missing

### Error: "tests fail in CI but pass local"
**Solución:** Check environment variables in GitHub Secrets