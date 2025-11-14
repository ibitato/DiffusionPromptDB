# Test Suite Documentation

Comprehensive test suite for DiffusionPromptDB project.

## 📁 Test Structure

```
tests/
├── unit/                    # Unit tests (isolated components)
│   ├── api/                # API endpoint unit tests
│   │   └── test_api.py     # FastAPI unit tests
│   └── database/           # Database unit tests
│       └── test_database.py # SQLite database tests
│
├── integration/            # Integration tests (component interaction)
│   ├── test_all_endpoints.py    # Full API endpoint testing
│   └── test_live_endpoints.py   # Live server integration tests
│
└── __init__.py            # Test package initialization
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

Isolated component testing without external dependencies.

#### API Tests (`tests/unit/api/`)
- **test_api.py**: FastAPI route unit tests
  - Authentication endpoints
  - CRUD operations
  - Request/response validation
  - Error handling

#### Database Tests (`tests/unit/database/`)
- **test_database.py**: Database operations
  - Schema validation
  - CRUD operations
  - Query performance
  - Transaction handling

### Integration Tests (`tests/integration/`)

Tests that verify component interactions and full workflows.

- **test_all_endpoints.py**: Complete API endpoint testing
  - End-to-end request flows
  - Authentication workflows
  - Data persistence verification
  - Error propagation

- **test_live_endpoints.py**: Live server testing
  - Real server connections
  - Network operations
  - Performance benchmarks
  - Load testing

## 🚀 Running Tests

### Run All Tests
```bash
# From project root
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Unit Tests Only
```bash
pytest tests/unit/
```

### Run Integration Tests Only
```bash
pytest tests/integration/
```

### Run Specific Test Categories
```bash
# API tests only
pytest tests/unit/api/

# Database tests only
pytest tests/unit/database/

# Single test file
pytest tests/unit/api/test_api.py

# Single test function
pytest tests/unit/api/test_api.py::test_create_prompt
```

## 📊 Coverage Reports

Generate test coverage reports:

```bash
# HTML report
pytest --cov=src --cov-report=html

# Terminal report
pytest --cov=src --cov-report=term

# XML report (for CI/CD)
pytest --cov=src --cov-report=xml
```

View HTML coverage report:
```bash
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

## 🔧 Test Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    api: API related tests
    database: Database related tests
```

### conftest.py (Fixtures)
```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    """Test client fixture"""
    from src.api.main import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Authenticated headers fixture"""
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def test_db():
    """Test database fixture"""
    # Setup test database
    yield db
    # Cleanup
```

## 🏷️ Test Markers

Use markers to categorize and filter tests:

```python
@pytest.mark.unit
def test_unit_example():
    pass

@pytest.mark.integration
def test_integration_example():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.api
def test_api_endpoint():
    pass

@pytest.mark.database
def test_database_operation():
    pass
```

Run tests by marker:
```bash
# Run only unit tests
pytest -m unit

# Run only slow tests
pytest -m slow

# Run all except slow tests
pytest -m "not slow"

# Run API and database tests
pytest -m "api or database"
```

## 📝 Writing Tests

### Test Structure Template
```python
"""
Test module description
"""

import pytest
from unittest.mock import Mock, patch

class TestFeatureName:
    """Test suite for FeatureName"""
    
    def setup_method(self):
        """Setup before each test"""
        self.fixture_data = {...}
    
    def teardown_method(self):
        """Cleanup after each test"""
        pass
    
    @pytest.mark.unit
    def test_feature_success(self):
        """Test successful case"""
        # Arrange
        expected = "expected_result"
        
        # Act
        result = function_under_test()
        
        # Assert
        assert result == expected
    
    @pytest.mark.unit
    def test_feature_failure(self):
        """Test failure case"""
        with pytest.raises(ExpectedException):
            function_under_test(invalid_input)
```

### Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Naming**: Use descriptive test names
3. **AAA Pattern**: Arrange, Act, Assert
4. **Single Responsibility**: Test one thing per test
5. **Fast Execution**: Mock external dependencies
6. **Comprehensive Coverage**: Test happy path and edge cases
7. **Documentation**: Add docstrings to test functions

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest -vv tests/
```

### Show Print Statements
```bash
pytest -s tests/
```

### Debug on Failure
```bash
pytest --pdb tests/
```

### Run Last Failed
```bash
pytest --lf tests/
```

### Run Failed First
```bash
pytest --ff tests/
```

## 📊 Test Metrics

Target metrics for the test suite:

- **Code Coverage**: > 80%
- **Unit Test Execution**: < 5 seconds
- **Integration Test Execution**: < 30 seconds
- **Test/Code Ratio**: 1.5:1
- **Critical Path Coverage**: 100%

## 🔗 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Test-Driven Development](https://testdriven.io/)

---

**Last Updated**: November 14, 2024  
**Maintained by**: Development Team
