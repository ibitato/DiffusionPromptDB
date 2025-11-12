# DiffusionPromptDB - Development Guidelines for AI Agents

## Project Overview

**Project Name**: DiffusionPromptDB  
**Description**: SQLite database for Stability Diffusion Prompts  
**Author**: ibitato (ibitato@gmail.com)  
**Version**: 0.1.0  
**License**: MIT

## Technology Stack

### Core Technologies
- **Python**: 3.8+ (use `python3` command)
- **Database**: SQLite3 (built-in Python module)
- **Package Management**: pip with pyproject.toml (PEP 517/518)
- **Virtual Environment**: `.venv/` (MANDATORY for all operations)

### Development Tools
- **Testing**: pytest, pytest-cov
- **Code Formatting**: black (line-length: 88)
- **Linting**: flake8
- **Type Checking**: mypy
- **Build Tools**: setuptools, wheel, build

## Development Workflow

### 1. Environment Setup (MANDATORY)

**ALWAYS work within the virtual environment**:

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate

# Verify activation
python --version  # Should show Python 3.8+
which python     # Should point to .venv/
```

### 2. Dependencies Management

**NEVER install packages globally**. Always install within `.venv/`:

```bash
# Install project in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install specific package
pip install <package-name>

# Update requirements files when adding dependencies
pip freeze > requirements.txt  # Production
# Edit requirements-dev.txt manually for dev dependencies
```

### 3. Code Quality Standards

#### Formatting (MANDATORY before commit)

```bash
# Format all code with black
make format

# Or manually:
black src/ tests/ scripts/
```

#### Linting (MANDATORY before commit)

```bash
# Run linter
make lint

# Or manually:
flake8 src/ tests/ scripts/
```

#### Type Checking (RECOMMENDED)

```bash
# Run type checker
make typecheck

# Or manually:
mypy src/
```

### 4. Testing Standards

**All code must have tests**:

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_database.py

# Run specific test
pytest tests/test_database.py::test_add_prompt
```

**Test Coverage Requirements**:
- Minimum 80% code coverage
- All new features must include tests
- All bug fixes must include regression tests

### 5. Documentation Standards

**Keep documentation updated**:

1. **Docstrings**: All modules, classes, and functions must have docstrings
2. **README.md**: Update when adding features or changing usage
3. **AGENTS.md**: Update when changing development workflow
4. **Comments**: Use for complex logic only, prefer self-documenting code

```python
def example_function(param: str) -> int:
    """
    Brief description of function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When parameter is invalid
    """
    pass
```

### 6. Git Workflow

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in database"
git commit -m "docs: update README"
git commit -m "test: add tests for search functionality"

# Commit message format:
# - feat: New feature
# - fix: Bug fix
# - docs: Documentation changes
# - test: Test additions/changes
# - refactor: Code refactoring
# - style: Code style changes (formatting)
# - chore: Maintenance tasks
```

## Makefile Usage

**The Makefile is virtual environment aware** - it automatically activates `.venv/`.

### Common Make Targets

```bash
# Show all available targets
make help

# Setup: Create venv and install dependencies
make setup

# Install package in development mode
make install

# Code formatting
make format

# Linting
make lint

# Type checking
make typecheck

# Run all quality checks (format + lint + typecheck)
make check

# Run tests
make test

# Run tests with coverage
make test-coverage

# Initialize database
make init-db

# Build distribution packages
make build

# Clean temporary files
make clean

# Complete cleanup (including venv)
make clean-all
```

## Project Structure Rules

### Directory Organization

```
DiffusionPromptDB/
├── src/diffusion_prompt_db/   # Source code ONLY
├── tests/                     # Test files ONLY
├── scripts/                   # Utility scripts
├── data/                      # Database files (ignored by git)
├── json_data/                 # Data files
└── docs/                      # Additional documentation (future)
```

### File Naming Conventions

- **Python files**: `snake_case.py`
- **Test files**: `test_*.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Import Organization

```python
# 1. Standard library imports
import os
import sys
from pathlib import Path

# 2. Third-party imports
import pytest

# 3. Local application imports
from diffusion_prompt_db.database import Database
from diffusion_prompt_db.models import Prompt
```

## Database Development Guidelines

### Schema Changes

1. **NEVER** delete columns or tables without migration
2. **ALWAYS** create migration scripts for schema changes
3. **TEST** migrations on test database first
4. **DOCUMENT** all schema changes in comments

### Query Best Practices

1. Use parameterized queries (ALWAYS)
2. Create indexes for frequently queried columns
3. Use transactions for multiple operations
4. Close connections properly (use context managers)

```python
# GOOD - Using context manager
with Database() as db:
    db.add_prompt(prompt)

# BAD - Manual connection management
db = Database()
db.add_prompt(prompt)
db.close()  # Easy to forget!
```

## Code Review Checklist

Before submitting code, ensure:

- [ ] Code is formatted with black
- [ ] Code passes flake8 linting
- [ ] Code passes mypy type checking
- [ ] All tests pass
- [ ] Test coverage is maintained/improved
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] No hardcoded paths or credentials
- [ ] Virtual environment was used for all operations

## Common Tasks for Agents

### Adding a New Feature

```bash
# 1. Ensure venv is active
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Create feature branch (if using git flow)
git checkout -b feature/new-feature

# 3. Write code with tests
# Edit src/diffusion_prompt_db/...
# Edit tests/test_...

# 4. Format and check
make check

# 5. Run tests
make test

# 6. Update documentation
# Edit README.md, AGENTS.md, or docstrings

# 7. Commit
git add .
git commit -m "feat: add new feature description"
```

### Fixing a Bug

```bash
# 1. Write failing test that reproduces bug
# Edit tests/test_...

# 2. Run test to confirm it fails
make test

# 3. Fix the bug
# Edit src/diffusion_prompt_db/...

# 4. Run test to confirm fix
make test

# 5. Format and check
make check

# 6. Commit
git commit -m "fix: resolve issue with specific functionality"
```

### Adding Dependencies

```bash
# 1. Install in venv
pip install <package-name>

# 2. Add to pyproject.toml
# Edit [project.dependencies] for production
# Edit [project.optional-dependencies.dev] for development

# 3. Update requirements files
pip freeze > requirements.txt

# 4. Document why dependency was added
# Add comment in pyproject.toml

# 5. Commit
git commit -m "chore: add <package-name> dependency"
```

## Error Handling Standards

```python
# Use specific exceptions
try:
    db.add_prompt(prompt)
except sqlite3.IntegrityError as e:
    logger.error(f"Duplicate prompt: {e}")
    raise ValueError("Prompt already exists")
except sqlite3.Error as e:
    logger.error(f"Database error: {e}")
    raise DatabaseError("Failed to add prompt")

# Always provide context in error messages
if not prompt.text:
    raise ValueError("Prompt text cannot be empty")
```

## Performance Guidelines

1. **Database**: Use indexes, batch operations, transactions
2. **Memory**: Use generators for large datasets
3. **I/O**: Use context managers, close resources
4. **Caching**: Cache expensive operations when appropriate

## Security Considerations

1. **SQL Injection**: Always use parameterized queries
2. **Input Validation**: Validate all user inputs
3. **File Paths**: Use Path objects, validate paths
4. **Secrets**: Never commit credentials or API keys
5. **Dependencies**: Keep dependencies updated

## Continuous Integration

When CI/CD is set up:

```yaml
# Example CI pipeline
- setup: Create venv and install
- format: Check code formatting
- lint: Run linting
- typecheck: Run type checking
- test: Run tests with coverage
- build: Build distribution packages
```

## Resources

- **Python Docs**: https://docs.python.org/3/
- **SQLite Docs**: https://www.sqlite.org/docs.html
- **pytest Docs**: https://docs.pytest.org/
- **black Docs**: https://black.readthedocs.io/
- **PEP 8**: https://pep8.org/

## Questions?

For questions about this project, contact: ibitato@gmail.com

---

**Last Updated**: November 12, 2025  
**Version**: 1.0
