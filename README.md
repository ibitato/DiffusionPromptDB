# DiffusionPromptDB

SQLite database for Stability Diffusion Prompts

**Author**: ibitato (ibitato@gmail.com)  
**License**: Apache 2.0

## Features

- 🗄️ **SQLite Database**: Lightweight, serverless, portable database
- 📦 **Self-Contained**: All dependencies included, no external services required
- 🐍 **Python 3.8+**: Modern Python with type hints and dataclasses
- 🔧 **CLI Interface**: Easy-to-use command-line interface
- 🧪 **Tested**: Unit tests with pytest
- 📝 **Well Documented**: Comprehensive docstrings and examples
- 🔄 **Version Control**: Git-ready with proper .gitignore

## NEW: Batch Analyzer 🚀

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
⚡ **Real-time processing with Claude Haiku 4.5** (fastest, recommended)  
📊 Structured JSON output  
🔄 Resumable processing  
📈 Automatic statistics generation  
🔍 Dry-run testing mode  
🎯 **100% success rate** (tested with 30 prompts)  

### Documentation

- [Batch Analyzer README](src/batch_analyzer/README.md) - Complete usage guide
- [Setup Guide](src/batch_analyzer/SETUP.md) - AWS configuration instructions
- [Cleanup Guide](src/batch_analyzer/CLEANUP.md) - Resource cleanup instructions

### Cost Example

For the included dataset (10,386 prompts): ~$67 USD using Claude 3.5 Sonnet with Batch API discount.

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
│   └── batch_analyzer/           # NEW: Batch analysis tool
│       ├── core/                 # Core library
│       ├── schemas/              # JSON schemas
│       ├── examples/             # Examples
│       ├── README.md             # Full documentation
│       ├── SETUP.md              # Setup guide
│       ├── CLEANUP.md            # Cleanup guide
│       └── run_analysis.py       # Main script
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

# Run tests
pytest

# Run with coverage
pytest --cov=diffusion_prompt_db --cov-report=html
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

- **0.1.0** (Initial Release)
  - SQLite database with prompts table
  - Basic CLI interface
  - Python API for database operations
  - Unit tests with pytest
  - Complete documentation
