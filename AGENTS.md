# DiffusionPromptDB - Development Guidelines for AI Agents

## Project Overview

**Project Name**: DiffusionPromptDB  
**Description**: SQLite database for Stability Diffusion Prompts  
**Author**: ibitato (REDACTED_EMAIL)  
**Version**: 0.1.0  
**License**: MIT

## Technology Stack

### Backend Technologies
- **Python**: 3.8+ (use `python3` command)
- **Database**: SQLite3 (built-in Python module)
- **API Framework**: FastAPI with JWT authentication
- **Package Management**: pip with pyproject.toml (PEP 517/518)
- **Virtual Environment**: `.venv/` (MANDATORY for all operations)

### Frontend Technologies
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios with React Query
- **Routing**: React Router v6
- **Internationalization**: i18next

### Development Tools (Backend)
- **Testing**: pytest, pytest-cov
- **Code Formatting**: black (line-length: 88)
- **Linting**: flake8
- **Type Checking**: mypy
- **Build Tools**: setuptools, wheel, build

### Development Tools (Frontend)
- **Package Manager**: npm
- **Code Formatting**: Prettier
- **Linting**: ESLint with TypeScript support
- **Type Checking**: TypeScript compiler

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

#### Backend Code Quality

##### Formatting (MANDATORY before commit)

```bash
# Format all Python code with black
make format

# Or manually:
black src/ tests/ scripts/
```

##### Linting (MANDATORY before commit)

```bash
# Run Python linter
make lint

# Or manually:
flake8 src/ tests/ scripts/
```

##### Type Checking (RECOMMENDED)

```bash
# Run Python type checker
make typecheck

# Or manually:
mypy src/
```

##### Run All Backend Checks

```bash
# Format + Lint + Typecheck
make check
```

#### Frontend Code Quality

##### Formatting (MANDATORY before commit)

```bash
# Format all TypeScript/React code with Prettier
make format-frontend

# Or manually:
cd frontend && npm run format
```

##### Linting (MANDATORY before commit)

```bash
# Run ESLint on TypeScript/React code
make lint-frontend

# Or manually:
cd frontend && npm run lint
```

##### Run All Frontend Checks

```bash
# Format + Lint for frontend
make check-frontend
```

#### Full Project Check (RECOMMENDED)

```bash
# Run all checks for both backend and frontend
make check && make check-frontend
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

# Backend Code Quality
make format           # Format Python code with black
make lint            # Run flake8 linter on Python
make typecheck       # Run mypy type checker
make check           # Run all Python quality checks

# Frontend Code Quality
make format-frontend  # Format TypeScript/React code with Prettier
make lint-frontend   # Run ESLint on TypeScript/React
make check-frontend  # Run all frontend checks

# Testing
make test            # Run all tests
make test-coverage   # Run tests with coverage report
make test-verbose    # Run tests with verbose output

# Database
make init-db         # Initialize the database

# Build & Distribution
make build           # Build distribution packages
make build-wheel     # Build wheel package only

# Utilities
make run             # Run the CLI (shows help)
make clean           # Remove temporary files
make clean-all       # Complete cleanup including venv
```

## Project Structure Rules

### Directory Organization

```
DiffusionPromptDB/
├── frontend/                  # React/TypeScript application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── hooks/           # Custom React hooks
│   │   ├── store/           # Zustand stores
│   │   ├── i18n/            # Internationalization
│   │   └── types/           # TypeScript types
│   └── package.json
├── src/
│   ├── api/                  # FastAPI backend
│   │   ├── routers/         # API endpoints
│   │   ├── models/          # Pydantic models
│   │   ├── database/        # Database utilities
│   │   └── middleware/      # API middleware
│   ├── diffusion_prompt_db/  # Core library
│   └── batch_analyzer/       # Batch processing tools
├── tests/                    # Test files
├── scripts/                  # Utility scripts
├── data/                     # Database files (ignored by git)
└── json_data/               # Data files
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

## API Development Guidelines

### FastAPI Structure

The API is built with FastAPI and includes:

- **Authentication**: JWT-based authentication
- **Routers**: Modular endpoint organization
- **Models**: Pydantic models for validation
- **Middleware**: CORS, authentication, error handling

### Running the API

```bash
# Development server
cd src/api
python main.py

# Or using uvicorn directly
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

- `/auth/*` - Authentication endpoints
- `/prompts/*` - Prompt management
- `/search/*` - Search functionality
- `/catalog/*` - Catalog operations
- `/preferences/*` - User preferences
- `/admin/*` - Admin operations

### Testing API Endpoints

```bash
# Run API tests
cd src/api
pytest tests/

# Test specific endpoint
pytest tests/test_all_endpoints.py::test_prompt_creation
```

## Frontend Development Guidelines

### Setup Frontend

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Frontend Commands

```bash
# Development
npm run dev           # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run format       # Format with Prettier
npm run lint         # Lint with ESLint
npm run type-check   # TypeScript type checking
```

### Component Structure

```typescript
// Example React component with TypeScript
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface Props {
  title: string;
  onSubmit: (data: FormData) => void;
}

export function ExampleComponent({ title, onSubmit }: Props) {
  const { t } = useTranslation();
  const [data, setData] = useState<FormData>({});
  
  // Component logic here
  
  return (
    <div className="container">
      {/* JSX content */}
    </div>
  );
}
```

### State Management

Using Zustand for state management:

```typescript
// Example store
import { create } from 'zustand';

interface StoreState {
  items: Item[];
  addItem: (item: Item) => void;
  removeItem: (id: string) => void;
}

export const useStore = create<StoreState>((set) => ({
  items: [],
  addItem: (item) => set((state) => ({ 
    items: [...state.items, item] 
  })),
  removeItem: (id) => set((state) => ({ 
    items: state.items.filter(i => i.id !== id) 
  })),
}));
```

## Common Tasks for Agents

### Working with Frontend and Backend

```bash
# 1. Ensure both environments are ready
source .venv/bin/activate  # Backend Python environment
cd frontend && npm install  # Frontend dependencies

# 2. Format both codebases
make check              # Backend formatting and linting
make check-frontend     # Frontend formatting and linting

# 3. Run both servers for development
# Terminal 1: Backend
cd src/api && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev

# 4. Test full stack
# Backend tests
make test

# Frontend tests (when added)
cd frontend && npm test

# 5. Commit changes
git add .
git commit -m "feat: add full-stack feature"
```

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

For questions about this project, contact: REDACTED_EMAIL

---

**Last Updated**: November 13, 2025  
**Version**: 1.1
