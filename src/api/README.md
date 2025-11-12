# DiffusionPromptDB REST API

REST API segura para gestionar prompts de Stable Diffusion y su catalogación.

## 🚀 Características

- ✅ **CRUD Completo**: Create, Read, Update, Delete para prompts
- ✅ **Búsquedas Avanzadas**: Filtros multi-categoría en catálogo
- ✅ **Seguridad**: API Keys (lectura) + JWT Tokens (escritura)
- ✅ **Rate Limiting**: Protección contra abuso
- ✅ **Documentación Auto-generada**: Swagger UI + ReDoc
- ✅ **CORS Configurado**: Acceso desde frontends
- ✅ **Validación**: Pydantic models automáticos
- ✅ **Estadísticas**: Endpoints públicos de stats

## 📦 Instalación

```bash
cd src/api

# Instalar dependencias
pip install -r requirements.txt

# Configurar
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar
python -m uvicorn main:app --reload
# O: python main.py
```

## 🔐 Autenticación

### 3 Niveles de Acceso

**1. Público (Sin auth):**
- `GET /health`
- `GET /api/v1/admin/stats`

**2. API Key (Solo Lectura):**
```bash
curl -H "X-API-Key: REDACTED_API_KEY" http://localhost:8000/api/v1/prompts
```

**3. JWT Token (Lectura/Escritura):**
```bash
cd src/api

# Instalar
pip install -r requirements.txt

# Ejecutar (IMPORTANTE: usar start_server.py para evitar errores de imports)
python start_server.py

# O desde el root del proyecto:
python -m src.api.start_server

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📡 Endpoints Principales

### Prompts Originales

```
GET    /api/v1/prompts              # Listar con paginación
GET    /api/v1/prompts/{id}         # Obtener uno
POST   /api/v1/prompts              # Crear (JWT)
PUT    /api/v1/prompts/{id}         # Actualizar (JWT)
DELETE /api/v1/prompts/{id}         # Eliminar (JWT)
```

### Catálogo

```
GET    /api/v1/catalog/{id}                # Prompt catalogado
GET    /api/v1/catalog/search/nsfw/{level} # Por NSFW
GET    /api/v1/catalog/search/style/{style} # Por estilo
```

### Búsqueda Avanzada

```
GET    /api/v1/search/complex       # Búsqueda multi-filtro
GET    /api/v1/search/tags/{tag}    # Por tag específico
```

### Admin

```
GET    /api/v1/admin/health         # Health check
GET    /api/v1/admin/stats          # Estadísticas
```

## 💡 Ejemplos de Uso

### 1. Listar Prompts

```bash
curl -H "X-API-Key: REDACTED_API_KEY" \
  "http://localhost:8000/api/v1/prompts?page=1&page_size=10"
```

**Response:**
```json
{
  "total": 150,
  "page": 1,
  "page_size": 10,
  "results": [
    {
      "id": 1,
      "text": "score_9, 1girl, portrait...",
      "category": "portrait",
      "rating": 5,
      "created_at": "2025-11-12T08:00:00"
    }
  ]
}
```

### 2. Crear Prompt (Requiere JWT)

```bash
curl -X POST http://localhost:8000/api/v1/prompts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "masterpiece, landscape, mountains",
    "category": "landscape",
    "rating": 5,
    "tags": "nature,mountains,scenic"
  }'
```

### 3. Búsqueda en Catálogo por NSFW

```bash
curl -H "X-API-Key: REDACTED_API_KEY" \
  "http://localhost:8000/api/v1/catalog/search/nsfw/explicit?limit=10"
```

**Response:**
```json
{
  "total": 10,
  "results": [
    {
      "id": 1,
      "original_prompt": "..."
    }
  ]
}
```

### 4. Búsqueda Compleja

```bash
curl -H "X-API-Key: REDACTED_API_KEY" \
  "http://localhost:8000/api/v1/search/complex?nsfw_level=explicit&number_of_people=1&art_style=anime&limit=20"
```

### 5. Estadísticas (Público)

```bash
curl http://localhost:8000/api/v1/admin/stats
```

**Response:**
```json
{
  "total_prompts": 30,
  "nsfw_distribution": {
    "explicit": 29,
    "suggestive": 1
  },
  "top_tags": [
    {"tag": "1girl", "count": 15},
    {"tag": "masterpiece", "count": 11}
  ],
  "top_art_styles": [
    {"style": "anime", "count": 11},
    {"style": "photorealistic", "count": 11}
  ]
}
```

## 🔒 Seguridad

### Cambiar API Keys

Edita `.env`:
```
API_KEYS=["my-secure-key-1","my-secure-key-2"]
```

### Generar JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el resultado a `.env`:
```
JWT_SECRET_KEY=tu-secret-generado-aqui
```

### Rate Limiting

Configurado por defecto:
- 100 requests/minuto
- 1000 requests/hora

Editar en `.env` o `config.py`

## 📚 Documentación Interactiva

Una vez iniciada la API:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🏗️ Estructura

```
src/api/
├── main.py                    # FastAPI app
├── config.py                  # Configuración
├── auth.py                    # Autenticación
├── requirements.txt           # Dependencias
├── .env.example              # Template config
├── models/                    # Pydantic models
│   ├── prompt_models.py      # Modelos de prompts
│   └── catalog_models.py     # Modelos de catálogo
└── routers/                   # Endpoints
    ├── prompts.py            # CRUD prompts
    ├── catalog.py            # Lectura catálogo
    ├── search.py             # Búsquedas avanzadas
    └── admin.py              # Admin/stats
```

## 🚀 Deployment

### Desarrollo

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
# Con Gunicorn + Uvicorn workers
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY src/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/api/ ./src/api/
COPY src/diffusion_prompt_db/ ./src/diffusion_prompt_db/
COPY data/ ./data/
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Stats (público)
curl http://localhost:8000/api/v1/admin/stats

# Con API key
curl -H "X-API-Key: REDACTED_API_KEY" \
  http://localhost:8000/api/v1/prompts

# Con autenticación JWT
# (primero obtener token con /auth/login)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/prompts/1
```

## 📊 Bases de Datos

La API gestiona 2 bases de datos:

**1. prompts.db** - Prompts originales
- Tabla: prompts
- CRUD completo
- Schema: ver `src/diffusion_prompt_db/database.py`

**2. prompts_catalog.db** - Catalogación
- 20+ tablas categorizadas
- Solo lectura via API
- Schema: ver `src/batch_analyzer/db_schema.sql`

## 🔧 Configuración

Ver `config.py` y `.env.example` para todas las opciones.

## 📖 API Endpoints Completos

### Root
- `GET /` - API info
- `GET /health` - Health check

### Prompts (require API Key o JWT)
- `GET /api/v1/prompts?page=1&page_size=20&category=landscape`
- `GET /api/v1/prompts/{id}`
- `POST /api/v1/prompts` (JWT)
- `PUT /api/v1/prompts/{id}` (JWT)
- `DELETE /api/v1/prompts/{id}` (JWT)

### Catalog (require API Key)
- `GET /api/v1/catalog/{id}`
- `GET /api/v1/catalog/search/nsfw/{level}`
- `GET /api/v1/catalog/search/style/{style}`

### Search (require API Key)
- `GET /api/v1/search/complex?nsfw_level=explicit&number_of_people=1&art_style=anime`
- `GET /api/v1/search/tags/{tag}`

### Admin (público o API Key)
- `GET /api/v1/admin/health`
- `GET /api/v1/admin/stats`

## 🎯 Próximos Pasos

1. Configurar `.env` con tus credenciales
2. Iniciar API: `python main.py`
3. Abrir docs: http://localhost:8000/docs
4. Probar endpoints con Swagger UI
5. Integrar con tu frontend

## 📝 Notas

- Los prompts del catálogo deben existir en `prompts_catalog.db`
- Para crear catálogo, usar `batch_analyzer/import_to_db.py`
- Los JWT tokens expiran en 60 minutos (configurable)
- Rate limits aplicados por IP

## Version

1.0.0 - Initial release
