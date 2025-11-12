# DiffusionPromptDB Makefile
# Virtual environment aware - automatically uses .venv/

.PHONY: help setup install clean clean-all format lint typecheck check test test-coverage init-db build run

# Detect OS
ifeq ($(OS),Windows_NT)
	VENV_BIN := .venv\Scripts
	PYTHON := $(VENV_BIN)\python.exe
	PIP := $(VENV_BIN)\pip.exe
	ACTIVATE := $(VENV_BIN)\activate.bat
	RM := del /Q
	RMDIR := rmdir /S /Q
else
	VENV_BIN := .venv/bin
	PYTHON := $(VENV_BIN)/python
	PIP := $(VENV_BIN)/pip
	ACTIVATE := . $(VENV_BIN)/activate
	RM := rm -f
	RMDIR := rm -rf
endif

# Default target
help:
	@echo "DiffusionPromptDB - Available Make Targets"
	@echo "=========================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Create virtual environment and install all dependencies"
	@echo "  make install        - Install package in development mode"
	@echo "  make install-dev    - Install with development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format         - Format code with black"
	@echo "  make lint           - Run flake8 linter"
	@echo "  make typecheck      - Run mypy type checker"
	@echo "  make check          - Run all quality checks (format + lint + typecheck)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo ""
	@echo "Database:"
	@echo "  make init-db        - Initialize the database"
	@echo ""
	@echo "Build & Distribution:"
	@echo "  make build          - Build distribution packages"
	@echo "  make build-wheel    - Build wheel package only"
	@echo ""
	@echo "Utilities:"
	@echo "  make run            - Run the CLI (shows help)"
	@echo "  make clean          - Remove temporary files and caches"
	@echo "  make clean-all      - Remove everything including venv"
	@echo ""

# Setup virtual environment and install dependencies
setup:
	@echo "Creating virtual environment..."
	python -m venv .venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"
	@echo ""
	@echo "Setup complete! Activate virtual environment with:"
ifeq ($(OS),Windows_NT)
	@echo "  .venv\Scripts\activate"
else
	@echo "  source .venv/bin/activate"
endif

# Install package in development mode
install:
	@echo "Installing package in development mode..."
	$(PIP) install -e .

# Install with development dependencies
install-dev:
	@echo "Installing package with development dependencies..."
	$(PIP) install -e ".[dev]"

# Format code with black
format:
	@echo "Formatting code with black..."
	$(PYTHON) -m black src/ tests/ scripts/
	@echo "Code formatting complete!"

# Run linter
lint:
	@echo "Running flake8 linter..."
	$(PYTHON) -m flake8 src/ tests/ scripts/ --max-line-length=88 --extend-ignore=E203
	@echo "Linting complete!"

# Run type checker
typecheck:
	@echo "Running mypy type checker..."
	$(PYTHON) -m mypy src/
	@echo "Type checking complete!"

# Run all quality checks
check: format lint typecheck
	@echo ""
	@echo "All quality checks passed!"

# Run tests
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v
	@echo "Tests complete!"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest tests/ --cov=diffusion_prompt_db --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

# Run tests with verbose output
test-verbose:
	@echo "Running tests (verbose)..."
	$(PYTHON) -m pytest tests/ -vv

# Initialize database
init-db:
	@echo "Initializing database..."
	$(PYTHON) scripts/init_db.py
	@echo "Database initialized!"

# Build distribution packages
build:
	@echo "Building distribution packages..."
	$(PIP) install --upgrade build
	$(PYTHON) -m build
	@echo ""
	@echo "Distribution packages created in dist/"

# Build wheel only
build-wheel:
	@echo "Building wheel package..."
	$(PIP) install --upgrade build
	$(PYTHON) -m build --wheel
	@echo ""
	@echo "Wheel package created in dist/"

# Run the CLI
run:
	@echo "Running DiffusionPromptDB CLI..."
	$(PYTHON) -m diffusion_prompt_db

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
ifeq ($(OS),Windows_NT)
	-$(RMDIR) build 2>nul
	-$(RMDIR) dist 2>nul
	-$(RMDIR) htmlcov 2>nul
	-$(RMDIR) .pytest_cache 2>nul
	-$(RMDIR) .mypy_cache 2>nul
	-$(RMDIR) src\diffusion_prompt_db.egg-info 2>nul
	-for /d /r . %%d in (__pycache__) do @if exist "%%d" $(RMDIR) "%%d" 2>nul
	-for /r . %%f in (*.pyc) do @if exist "%%f" $(RM) "%%f" 2>nul
	-for /r . %%f in (*.pyo) do @if exist "%%f" $(RM) "%%f" 2>nul
	-if exist .coverage $(RM) .coverage 2>nul
else
	-$(RMDIR) build dist htmlcov .pytest_cache .mypy_cache *.egg-info 2>/dev/null
	-find . -type d -name __pycache__ -exec $(RMDIR) {} + 2>/dev/null
	-find . -type f -name "*.pyc" -delete 2>/dev/null
	-find . -type f -name "*.pyo" -delete 2>/dev/null
	-$(RM) .coverage 2>/dev/null
endif
	@echo "Cleanup complete!"

# Complete cleanup including venv
clean-all: clean
	@echo "Removing virtual environment..."
ifeq ($(OS),Windows_NT)
	-$(RMDIR) .venv 2>nul
	-if exist data\prompts.db $(RM) data\prompts.db 2>nul
else
	-$(RMDIR) .venv 2>/dev/null
	-$(RM) data/prompts.db 2>/dev/null
endif
	@echo "Complete cleanup done!"
	@echo ""
	@echo "Run 'make setup' to recreate the environment."
