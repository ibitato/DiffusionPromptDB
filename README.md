# DiffusionPromptDB

SQLite database for Stability Diffusion Prompts

**Author**: ibitato (REDACTED_EMAIL)  
**License**: Apache 2.0

## Features

- 🗄️ **SQLite Database**: Lightweight, serverless, portable database
- 📦 **Self-Contained**: All dependencies included, no external services required
- 🐍 **Python 3.8+**: Modern Python with type hints and dataclasses
- 🔧 **CLI Interface**: Easy-to-use command-line interface
- 🧪 **Tested**: Unit tests with pytest
- 📝 **Well Documented**: Comprehensive docstrings and examples
- 🔄 **Version Control**: Git-ready with proper .gitignore
- 🔐 **Account Management**: JWT auth with profile page, password rotation, and admin tooling
- 📈 **Personalized Metrics**: “Only my prompts” preference automatically scopes Dashboard, Search, and Prompts to your own catalog
- 🧰 **Model-Aware Filters**: When browsing “My prompts”, pick from your personal Stable Diffusion models to focus the list instantly
- 🖼️ **Prompt Ingestion Pipeline**: Upload Stable Diffusion PNGs, auto-extract metadata, and persist lightweight thumbnails only

## NEW: Complete Catalogation System 🚀

### 1️⃣ Batch Analyzer

**Analyze thousands of Stable Diffusion prompts using AWS Bedrock's Claude 3.5 Sonnet.**

The Batch Analyzer is a powerful tool that automatically extracts and categorizes information from your prompt collection, including:

- **15 Main Categories**: Characters, poses, clothing, settings, lighting, art style, technical details, NSFW content, sexual content, relationships, references, camera composition, mood, and more
- **Detailed Subcategories**: Over 50 specific attributes extracted per prompt
- **AWS Bedrock Integration**: Uses Claude 3.5 Sonnet via Batch API for cost-effective processing
- **Structured Output**: JSON schema optimized for indexing and cataloging

### Quick Start

```bash
cd src/batch_analyzer
pip install -r requirements.txt
cp config.yaml.example config.yaml
# Edit config.yaml with your AWS settings
python verify_setup.py

# Option 1: Real-time (fast, immediate results)
python run_realtime.py --count 10

# Option 2: Batch (cost-effective for large datasets)
python run_analysis.py --dry-run
```

### Features

✨ **Two analysis modes**: Batch (cost-effective) and Real-time (fast)  
💰 50% cost savings with Batch API  
🤖 **Recommended Model: Claude 3.5 Sonnet** (best accuracy, batch & realtime)  
⚡ Real-time alternative: Claude Haiku 4.5 (faster, good quality)  
📊 Structured JSON output  
🔄 Resumable processing  
📈 Automatic statistics generation  
🔍 Dry-run testing mode  
🎯 **99.5% success rate** (tested with 10,386 prompts)

### Documentation

- [Batch Analyzer README](src/batch_analyzer/README.md) - Complete usage guide
- [Setup Guide](src/batch_analyzer/SETUP.md) - AWS configuration instructions
- [Cleanup Guide](src/batch_analyzer/CLEANUP.md) - Resource cleanup instructions

### Cost Example

**Tested with 10,386 prompts:**
- Claude 3.5 Sonnet (Batch API): ~$67 USD
- Result: 10,334 prompts successfully cataloged (99.5% success rate)
- Recommended for best accuracy and structure compliance

### 2️⃣ SQLite Catalog Database

**Unified database with 10,388 pre-cataloged prompts.**

- **Location**: `src/api/database/prompts_catalog.db` (centralized in API module)
- **Normalized Schema**: 20+ tables for efficient querying
- **10,388 Prompts**: Production database pre-filled and cleaned
- **Advanced Search**: Multi-filter queries combining any categories
- **CLI Tools**: Interactive search and SQL query examples
- **Data Quality**: Cleaned BREAK patterns, normalized, 100% tested

```bash
cd src/batch_analyzer

# For batch results: Convert → Normalize → Import
python convert_batch_output.py results/batch_output_XXX.jsonl
python normalize_data.py results/converted_batch_XXX.jsonl
python import_to_db.py results/normalized_batch_XXX.jsonl --db prompts_catalog.db --stats

# For realtime results: Import directly
python import_to_db.py results/realtime_results_XXX.jsonl --db prompts_catalog.db --stats

# Test database
python test_catalog_integration.py --db prompts_catalog.db

# Interactive search
python search_catalog.py

# Example queries
python example_queries.py

#### Sanitizing narrative/non-prompt rows

Some legacy dumps ship with descriptive stories instead of actual prompts. Use the cleanup
helper to purge them (a timestamped backup is created under `database/backups/`):

```bash
python3 scripts/clean_invalid_prompts.py          # dry-run, shows matches
python3 scripts/clean_invalid_prompts.py --apply  # delete + backup
```
```

### 3️⃣ REST API 📡

**Secure REST API for CRUD operations and advanced searches.**

- **FastAPI**: Modern, fast, with auto-generated docs
- **Secure**: API Keys (read) + JWT tokens (write)
- **15 Endpoints**: Auth + Prompts CRUD + Catalog search + Stats
- **Authentication**: Login endpoint with JWT tokens
- **Tested**: Unit tests with pytest
- **Rate Limited**: 100/min, 1000/hour
- **Auto Docs**: Swagger UI + ReDoc

```bash
cd src/api

# Install
pip install -r requirements.txt

# Run
python start_server.py

# API: http://localhost:8000 (pre-filled with 10,388 prompts)
# Docs: http://localhost:8000/docs
```

**Quick Example:**
```bash
# Login to obtain JWT
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq -r '.access_token')

# Get stats (requires Authorization header)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/stats

# Search with API key
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/search/complex?nsfw_level=explicit&art_style=anime"
```

### 4️⃣ Prompt Ingestion & Thumbnail Pipeline

**Backend (`POST /api/v1/prompts/ingest`)**

- Accepts up to 5 Stable Diffusion PNGs per request plus optional `tags`, `category`, `art_style`, `rating` (1‑5) and `notes`.
- `src/api/services/image_metadata.py` reads the `parameters` chunk to capture positive prompt, negative prompt, and sampler/model settings. The payload that lands in the DB keeps the raw text plus a parsed `settings` dict.
- New tags are **no longer rejected**: `_infer_tags_from_prompt()` merges catalog hits with any brand-new keywords (perfect for LoRA names such as `annitaxyz`), so every ingestion stays searchable immediately.
- `_infer_art_style()` inspects the prompt/model metadata and fills `art_styles.primary_style` whenever the user did not pick a value manually.
- `src/api/services/image_storage.py` throws away the original PNG and only persists an optimized JPEG thumbnail (`MEDIA_ROOT/MEDIA_THUMBNAILS_SUBDIR/YYYY/MM/DD/<uuid>.jpg`). Configure the storage knobs via:

| Env var | Default | Notes |
|---------|---------|-------|
| `MEDIA_ROOT` | `media` | Base folder created automatically (git-ignored) |
| `MEDIA_THUMBNAILS_SUBDIR` | `thumbnails` | Nested directory that keeps the JPEG previews |
| `THUMBNAIL_MAX_SIZE` | `512` | Longest thumbnail edge (px) |
| `INGESTION_DEFAULT_TAGS` | _(empty)_ | Comma-separated tags always appended to ingested prompts |

**Frontend (`/ingest`)**

- Protected route; any authenticated user can drop up to five PNGs (other types are rejected in-browser).
- Client-side parser (`frontend/src/utils/pngMetadata.ts`) previews the metadata and suggests tags/art styles in real time. Suggestions are only applied when the user clicks “Apply”.
- Art-style selection now uses the same dropdown styling as the rest of the app and auto-populates from `/api/v1/admin/filters`.
- Upload progress, per-file status messages, and the resulting prompt IDs are rendered immediately so the user can jump to the prompt detail modal.

**CLI helper**

Need to triage thousands of PNGs first? `tools/sd_metadata_dump/export_sd_metadata.py` walks any folder (e.g., SD-Matrix’s `Data/Images`) and dumps every `parameters` block to JSONL so you can pre-filter before uploading.

### Local Hot-Reload Setup

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python src/api/init_users_db.py
python src/api/init_preferences_table.py
JWT_SECRET_KEY=devsecret \
API_KEYS='["test_key"]' \
USERS_DB_PATH="data/users.db" \
MEDIA_ROOT="media" \
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm install
VITE_API_KEY=test_key npm run dev -- --host 0.0.0.0 --port 5173
```

Visit `http://localhost:5173/ingest` and sign in as `test / REDACTED_PASSWORD` to exercise the ingestion flow end-to-end; prompts appear under “My Prompts” instantly.

### Account & User Management

- `/api/v1/user/profile` – read/update profile fields, change password, select default landing page, update preferences, and self-delete accounts (with secure data dumps).
- `/api/v1/admin/users/*` – admin-only CRUD for users: invite/create, update roles/status, reset passwords, and delete accounts.
- Password rotation is enforced via configurable environment variables (`PASSWORD_ROTATION_DAYS`, `PASSWORD_MIN_LENGTH`, `PASSWORD_HISTORY_LIMIT`), and users with expired credentials are redirected through `/api/v1/auth/password/expired` to verify their previous password and set a compliant replacement before logging back in.
- User preferences now drive every surface: if “Only my prompts” is enabled, Dashboard cards and charts, advanced Search, and the Prompts list automatically scope results to `created_by = current_user`.

#### Self-service registration

1. El usuario abre `https://www.diffusionprompt.net/register`, completa usuario/correo/contraseña y envía el formulario.
2. El backend envía un correo firmado con el enlace de verificación (`PUBLIC_APP_URL` controla la URL del botón). El Paso 2 de la página solo muestra las instrucciones y el estado del correo; no se pide token manual.
3. Tras hacer clic en el enlace, el endpoint `/api/v1/auth/verify` activa la cuenta y ya se puede iniciar sesión desde `/login`.

> Para automatizaciones o pruebas locales puedes seguir usando la API directamente:

```bash
# Registro vía API
curl -X POST https://www.diffusionprompt.net/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"newuser@example.com","password":"StrongPass!42"}'

# Verificación manual (solo necesaria cuando EMAIL_DEBUG_MODE=True y la API devuelve el token en la respuesta)
curl -X POST https://www.diffusionprompt.net/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_FROM_DEBUG_RESPONSE"}'
```

**Configurar envío de correos**

| Variable `.env` | Descripción |
|-----------------|-------------|
| `SMTP_HOST`     | Servidor SMTP de tu proveedor (Mailgun, SendGrid, etc.) |
| `SMTP_PORT`     | Puerto TLS (587) o SSL (465) |
| `SMTP_USERNAME` | Usuario/API key del servicio |
| `SMTP_PASSWORD` | Contraseña/API key |
| `SMTP_SENDER`   | Remitente (ej. `noreply@tudominio.com`) |
| `SMTP_USE_TLS`  | `True` para STARTTLS, `False` para SSL puro |
| `PUBLIC_APP_URL`| URL pública usada en los enlaces (ej. `https://www.diffusionprompt.net`) |

Si aún no cuentas con correo en GoDaddy, crea un remitente en un proveedor transaccional (Mailgun, SendGrid, Postmark), añade los registros SPF/DKIM que te indiquen en la zona DNS del dominio y coloca las credenciales en `.env`. Mientras `SMTP_*` no esté completo, la API seguirá devolviendo el `verification_token` en la respuesta para que puedas compartirlo manualmente (`EMAIL_DEBUG_MODE=True` por defecto).

#### Password expiry flow

```bash
# 1) User attempts login and receives 403 with X-Password-Expired: true

# 2) They submit their current + new password to renew the credential:
curl -X POST https://www.diffusionprompt.net/api/v1/auth/password/expired \
  -H "Content-Type: application/json" \
  -d '{
        "username": "test",
        "current_password": "REDACTED_PASSWORD",
        "new_password": "NewPassword!123"
      }'

# 3) On success they can log in again with the new password.
```

See [API README](src/api/README.md) and [Authentication Setup](AUTHENTICATION_SETUP.md) for complete documentation.

### 4️⃣ Frontend Web Application 🌐

**Modern React application for managing prompts with full internationalization.**

- **React 18 + TypeScript**: Modern frontend with full type safety
- **Multi-language Support**: Full i18n in 4 languages (ES, EN, FR, DE)
- **Authentication**: JWT-based login system with protected routes
- **CRUD Interface**: Complete prompt management with modals
- **Advanced Search**: Multi-filter search with complex queries
- **User Preferences**: Customizable settings with tag blacklisting
- **Data Export**: Export prompts to JSON/CSV formats
- **Interactive Charts**: Recharts visualizations for stats
- **Responsive Design**: Mobile-first, works on all devices
- **Performance**: TanStack Query for intelligent caching

```bash
cd frontend

# Install dependencies
npm install

# Configure
cp .env.example .env

# Run development server
npm run dev

# Frontend: http://localhost:5173
# Demo Login accounts (JWT):
# - test / REDACTED_PASSWORD
# - admin / REDACTED_PASSWORD
# - user / REDACTED_PASSWORD (seed account, disabled by default)
```

**Features:**
- 🌍 **4 Languages**: Spanish, English, French, German
- 📊 **Dashboard**: Real-time statistics with interactive charts
- 🔍 **Advanced Search**: Text, tags, NSFW level, art style filters
- ⚙️ **Settings**: User preferences and display customization
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- 🎨 **Dark Theme**: Modern dark mode interface
- 👤 **Profile & Preferences**: Dedicated page to manage personal data, password rotation, landing page, and account deletion
- 🛠️ **Admin Console**: Manage users (create/reset/disable) directly from the UI

See [Frontend README](frontend/FRONTEND_README.md) and [I18N Guide](frontend/I18N_GUIDE.md) for complete documentation.

## Project Structure

```
DiffusionPromptDB/
├── .git/                          # Git repository
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── pyproject.toml                 # Modern Python package configuration
├── setup.py                       # Backward compatibility
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── src/
│   ├── diffusion_prompt_db/      # Main package
│   │   ├── __init__.py           # Package initialization
│   │   ├── __main__.py           # CLI entry point
│   │   ├── database.py           # Database operations
│   │   ├── models.py             # Data models
│   │   └── config.py             # Configuration
│   ├── batch_analyzer/           # Batch analysis tool
│   │   ├── core/                 # 6 analysis modules
│   │   ├── schemas/              # JSON input/output schemas
│   │   ├── db_schema.sql         # SQLite catalog schema
│   │   ├── import_to_db.py       # JSONL → SQLite importer
│   │   ├── search_catalog.py     # Interactive search tool
│   │   ├── run_analysis.py       # Batch mode (Claude 3.5 Sonnet)
│   │   ├── run_realtime.py       # Real-time mode (Haiku 4.5)
│   │   ├── README.md             # Complete documentation
│   │   ├── SETUP.md              # AWS setup guide
│   │   └── CLEANUP.md            # Resource cleanup
│   └── api/                      # REST API
│       ├── main.py               # FastAPI application
│       ├── config.py             # API configuration
│       ├── auth.py               # Authentication
│       ├── models/               # Pydantic models
│       ├── routers/              # API endpoints (4 routers)
│       ├── tests/                # Unit tests (20 tests)
│       └── README.md             # API documentation
├── tests/                        # Unit tests
│   ├── __init__.py
│   └── test_database.py
├── scripts/                      # Utility scripts
│   └── init_db.py               # Database initialization
├── data/                        # SQLite database location
│   └── .gitkeep
└── json_data/                   # Additional data files
    └── prompts.jsonl
```

## Installation

### 1. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Package

```bash
# Development mode (recommended for development)
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### 3. Initialize Database

```bash
# Using the CLI
diffusion-prompt-db init

# Or using the script
python scripts/init_db.py
```

## Usage

### Command Line Interface

```bash
# Initialize database
diffusion-prompt-db init

# Add a new prompt (interactive)
diffusion-prompt-db add

# List all prompts
diffusion-prompt-db list

# Search prompts (interactive)
diffusion-prompt-db search
```

### Python API

```python
from diffusion_prompt_db import Database, Prompt

# Create/connect to database
with Database() as db:
    # Add a prompt
    prompt = Prompt(
        text="A beautiful landscape with mountains",
        negative_prompt="ugly, blurry, low quality",
        model="stable-diffusion-v1.5",
        category="landscape",
        tags="nature, mountains, scenic",
        rating=5,
        notes="Great for wallpapers"
    )
    prompt_id = db.add_prompt(prompt)
    print(f"Added prompt with ID: {prompt_id}")
    
    # Get a prompt
    retrieved = db.get_prompt(prompt_id)
    print(f"Prompt text: {retrieved.text}")
    
    # Search prompts
    landscapes = db.search_prompts(category="landscape", min_rating=4)
    print(f"Found {len(landscapes)} landscape prompts")
    
    # Update a prompt
    retrieved.rating = 4
    db.update_prompt(prompt_id, retrieved)
    
    # Delete a prompt
    db.delete_prompt(prompt_id)
```

## Database Schema

The database includes a single `prompts` table with the following fields:

- **id**: INTEGER PRIMARY KEY (auto-increment)
- **text**: TEXT NOT NULL (the prompt text)
- **negative_prompt**: TEXT (optional negative prompt)
- **model**: TEXT (model identifier)
- **parameters**: TEXT (JSON string with generation parameters)
- **tags**: TEXT (comma-separated tags)
- **category**: TEXT (category classification)
- **rating**: INTEGER (1-5 rating)
- **notes**: TEXT (additional notes)
- **created_at**: TIMESTAMP (creation timestamp)
- **updated_at**: TIMESTAMP (last update timestamp)

Indexes are created on `category`, `model`, and `rating` for efficient queries.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run entire backend test suite
pytest

# Run with coverage
pytest --cov=diffusion_prompt_db --cov-report=html

# Targeted suites
pytest tests/unit/database/test_database.py
pytest tests/unit/api/test_profile_admin.py

# Frontend unit tests (Vitest)
cd frontend && npm run test

# Keep locale files aligned with English source
cd frontend && npm run check:i18n
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Packaging and Distribution

### Build the Package

```bash
# Install build tools
pip install build

# Build distribution files
python -m build
```

This creates `.whl` and `.tar.gz` files in the `dist/` directory.

### Install from Package

```bash
# Install from wheel file
pip install dist/diffusion_prompt_db-0.1.0-py3-none-any.whl

# Or install from source distribution
pip install dist/diffusion-prompt-db-0.1.0.tar.gz
```

## Portability

This project is designed to be portable:

- **Self-contained**: All code and dependencies are in one place
- **SQLite**: No external database server required
- **Virtual environment**: Isolated Python environment
- **No absolute paths**: All paths are relative
- **Cross-platform**: Works on Windows, Linux, and macOS

To move the project:
1. Copy the entire directory
2. Create virtual environment: `python -m venv .venv`
3. Activate it and install: `pip install -e .`
4. The database file (`data/prompts.db`) can be copied with your data

## License

Apache License 2.0 - See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass
- New features include tests
- Documentation is updated

## Version History

- **2.0.0** (Current - November 2024)
  - Full internationalization support (4 languages)
  - Complete frontend application with React 18
  - Advanced search and filtering capabilities
  - User preferences and settings system
  - Interactive data visualizations
  - Export functionality (JSON/CSV)
  - JWT authentication system
  - Comprehensive documentation updates

- **1.5.0** (October 2024)
  - Batch Analyzer with AWS Bedrock integration
  - SQLite Catalog Database with 10,388 prompts
  - REST API with FastAPI
  - Authentication system
  - Rate limiting

- **0.1.0** (Initial Release)
  - SQLite database with prompts table
  - Basic CLI interface
  - Python API for database operations
  - Unit tests with pytest
  - Complete documentation
