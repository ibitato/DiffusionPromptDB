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

# Configurar (credenciales + bases SQLite)
cp .env.example .env
# Editar .env con tus configuraciones y luego inicializa:
python init_users_db.py
python init_preferences_table.py

# Ejecutar
python -m uvicorn main:app --reload
# O: python main.py
```

## 🔐 Autenticación

### 3 Niveles de Acceso

**1. Público (Sin auth):**
- `GET /health`
- `GET /api/v1/admin/health`

**2. API Key (Solo Lectura):**
```bash
curl -H "X-API-Key: $API_KEY" http://localhost:8000/api/v1/prompts
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
Requerido para:
- POST/PUT/DELETE de prompts
- Endpoints sensibles dentro de `/api/v1/admin`, como `/admin/stats` y `/admin/filters`

### Registro y verificación

```bash
# Crear cuenta
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
        "username": "nuevo",
        "email": "nuevo@example.com",
        "password": "StrongPass!42"
      }'

# Completar verificación (normalmente se hace desde el enlace recibido por email)
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN"}'

# Nota: configura SMTP_* en .env para que el token se envíe automáticamente.
# Solo en entornos con EMAIL_DEBUG_MODE=True verás el token en la respuesta/UI.
```
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
GET    /api/v1/admin/health         # Health check (público)
GET    /api/v1/admin/stats          # Estadísticas (JWT)
GET    /api/v1/admin/filters        # Valores para filtros (JWT)
POST   /api/v1/prompts/ingest       # Ingestar PNGs de SD en prompts (JWT)
```

## 🖼️ Ingesta de PNGs (SD → Catalog)

- **Endpoint**: `POST /api/v1/prompts/ingest`
- **Auth**: JWT (cualquier usuario autenticado puede importar a su propio catálogo).
- **Payload**: `multipart/form-data` con hasta 5 archivos (`files=@imagen.png`) más campos opcionales `tags`, `category`, `art_style`, `rating` (1-5) y `notes`.
- **Metadatos**: `src/api/services/image_metadata.py` lee el chunk `parameters` de cada PNG para extraer prompt positivo, prompt negativo y configuraciones (Steps, Seed, Sampler, modelo, etc.). Esa información se guarda como JSON (`parameters`).
- **Etiquetas / estilos**:
  - `_infer_tags_from_prompt()` agrega automáticamente tokens relevantes y **ya no exige** que existan en `main_tags`, por lo que LoRAs como `annitaxyz` quedan disponibles para búsqueda desde el primer upload.
  - `_infer_art_style()` completa estilos conocidos cuando el usuario no elige uno manualmente.
  - Las etiquetas manuales se combinan con `INGESTION_DEFAULT_TAGS` (si está configurado).
- **Imágenes**: `src/api/services/image_storage.py` descarta el PNG original y genera únicamente un thumbnail JPEG (`MEDIA_ROOT/MEDIA_THUMBNAILS_SUBDIR/AAAA/MM/DD/<uuid>.jpg`). Controla la ruta y el tamaño con las variables `MEDIA_ROOT`, `MEDIA_THUMBNAILS_SUBDIR` y `THUMBNAIL_MAX_SIZE`.
- **Respuesta**: `BatchImageIngestionResponse` con conteo `created/failed` y detalle por archivo.

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"<your-password>"}' | jq -r '.access_token')

curl -X POST http://localhost:8000/api/v1/prompts/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@sample.png" \
  -F "tags=annitaxyz,portrait" \
  -F "category=portrait" \
  -F "rating=5" \
  -F "notes=Import via CLI"
```

> Consejo: Usa `tools/sd_metadata_dump/export_sd_metadata.py` para explorar directorios masivos (p.ej. SD-Matrix) y decidir qué PNGs merecen ser ingeridos antes de subirlos.

## 💡 Ejemplos de Uso

### 1. Listar Prompts

```bash
curl -H "X-API-Key: $API_KEY" \
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
curl -H "X-API-Key: $API_KEY" \
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
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/search/complex?nsfw_level=explicit&number_of_people=1&art_style=anime&limit=20"
```

### 5. Estadísticas (requiere JWT)

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/admin/stats
```
Batch Size: 5 archivos subidos, 5 procesados correctamente
```

## 🖼️ Importación de PNGs (Backoffice)

Nuevo endpoint para convertir las imágenes generadas por Stable Diffusion en prompts del catálogo.

1. **Configura almacenamiento** (opcional):
   - `MEDIA_ROOT` (env: `MEDIA_ROOT`): carpeta donde guardar los thumbnails (default: `media/`)
   - `MEDIA_THUMBNAILS_SUBDIR`: subcarpeta donde se almacenan los JPEG reducidos (default: `thumbnails`)
   - `THUMBNAIL_MAX_SIZE`: tamaño máximo del lado mayor en píxeles (default: 512)
   - `INGESTION_DEFAULT_TAGS`: lista separada por comas con tags ya existentes que quieras aplicar automáticamente
   - Las imágenes originales se descartan después de generar el thumbnail para minimizar almacenamiento; solo se guarda la versión reducida.

2. **Migración** (si tu base ya existía):
   ```bash
   cd src/api
   python add_prompt_image_fields.py
   ```

3. **Llamada al endpoint (cualquier usuario autenticado)**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/prompts/ingest \
     -H "Authorization: Bearer USER_JWT" \
     -F "files=@/ruta/imagen1.png" \
     -F "files=@/ruta/imagen2.png" \
     -F "tags=portrait,studio" \
     -F "art_style=realistic" \
     -F "rating=4"
   ```
   - Solo acepta PNGs con el chunk `parameters` (como los generados por Stability Matrix / A1111).
   - Extrae prompt positivo, negativo y settings (steps, sampler, seed, etc.) y los guarda en `parameters` como JSON.
   - Genera un JPEG reducido y lo referencia en `thumbnail_path`.
   - Solo permite tags que ya existan en `main_tags`. Si necesitas nuevos, créalos primero desde tools o DB.

4. **Entorno de desarrollo local**:
   - Copia algunas imágenes con metadatos a una carpeta local (ej. `/mnt/d/sd-matrix/Data/Images/...`).
   - Ejecuta la API con `python src/api/start_server.py` (usar `.venv` activado).
   - Usa el mismo endpoint anterior apuntando al servidor local. Los thumbnails quedarán en `media/thumbnails/...`.


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

# Stats (requiere JWT)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/admin/stats

# Con API key
curl -H "X-API-Key: $API_KEY" \
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
- `POST /api/v1/prompts/{id}/copy` (JWT) – duplicate catalog prompt into the authenticated user's collection
- `PUT /api/v1/prompts/{id}` (JWT)
- `DELETE /api/v1/prompts/{id}` (JWT)

### Catalog (require API Key)
- `GET /api/v1/catalog/{id}`
- `GET /api/v1/catalog/search/nsfw/{level}`
- `GET /api/v1/catalog/search/style/{style}`

### Search (require API Key)
- `GET /api/v1/search/complex?nsfw_level=explicit&number_of_people=1&art_style=anime`
- `GET /api/v1/search/tags/{tag}`

### Admin (health público, resto con JWT)
- `GET /api/v1/admin/health`
- `GET /api/v1/admin/stats` (JWT)
- `GET /api/v1/admin/filters` (JWT)

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
