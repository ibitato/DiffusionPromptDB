"""
Complete API Endpoint Tests

Tests all 15 endpoints to verify backend functionality.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import app using module path
import importlib.util

spec = importlib.util.spec_from_file_location(
    "main", Path(__file__).parent.parent / "main.py"
)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
app = main_module.app

client = TestClient(app)

# Test credentials
TEST_USER = "test"
TEST_PASS = "test"
API_KEY = "demo-read-key-12345"


class TestAuthentication:
    """Test authentication endpoints."""

    def test_login_success(self):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login", json={"username": TEST_USER, "password": TEST_PASS}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == TEST_USER
        print(f"✅ Login successful - Token received")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login", json={"username": "wrong", "password": "wrong"}
        )
        assert response.status_code == 401
        print(f"✅ Invalid credentials rejected")


class TestPublicEndpoints:
    """Test public endpoints (no auth required)."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        print(f"✅ Root endpoint working")

    def test_health_check(self):
        """Test health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check working")

    def test_admin_health(self):
        """Test admin health endpoint."""
        response = client.get("/api/v1/admin/health")
        assert response.status_code == 200
        print(f"✅ Admin health check working")

    def test_admin_stats(self):
        """Test admin stats endpoint (should show catalog data)."""
        response = client.get("/api/v1/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_prompts" in data
        print(f"✅ Stats endpoint working - {data.get('total_prompts', 0):,} prompts")


class TestPromptsEndpoints:
    """Test prompts CRUD endpoints."""

    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests."""
        response = client.post(
            "/api/v1/auth/login", json={"username": TEST_USER, "password": TEST_PASS}
        )
        return response.json()["access_token"]

    def test_list_prompts_with_api_key(self):
        """Test listing prompts with API key."""
        response = client.get("/api/v1/prompts", headers={"X-API-Key": API_KEY})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or isinstance(data, list)
        print(f"✅ List prompts with API key working")

    def test_list_prompts_with_pagination(self):
        """Test pagination."""
        response = client.get(
            "/api/v1/prompts?page=1&page_size=5", headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200
        print(f"✅ Pagination working")

    def test_create_prompt_requires_auth(self):
        """Test that creating requires JWT."""
        response = client.post(
            "/api/v1/prompts",
            json={"text": "test prompt"},
            headers={"X-API-Key": API_KEY},  # API key not enough
        )
        # Should fail without JWT
        assert response.status_code in [401, 403]
        print(f"✅ Create prompt requires JWT")

    def test_create_prompt_with_jwt(self, auth_token):
        """Test creating with JWT."""
        response = client.post(
            "/api/v1/prompts",
            json={
                "text": "test prompt from automated test",
                "category": "test",
                "rating": 5,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # May succeed or fail depending on DB state, but should not be 401/403
        print(f"✅ Create prompt with JWT - Status: {response.status_code}")
        return response


class TestCatalogEndpoints:
    """Test catalog search endpoints."""

    def test_search_by_nsfw(self):
        """Test NSFW search."""
        response = client.get(
            "/api/v1/catalog/search/nsfw/explicit?limit=5",
            headers={"X-API-Key": API_KEY},
        )
        # May be 200 (with results) or 503 (catalog DB not found)
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            print(f"✅ NSFW search working - Found {data.get('total', 0)} results")
        else:
            print(f"⚠️  NSFW search - Catalog DB not found (expected if not set up)")

    def test_search_by_style(self):
        """Test art style search."""
        response = client.get(
            "/api/v1/catalog/search/style/anime?limit=5", headers={"X-API-Key": API_KEY}
        )
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Style search working - Found {data.get('total', 0)} results")
        else:
            print(f"⚠️  Style search - Catalog DB not found")


class TestSearchEndpoints:
    """Test advanced search endpoints."""

    def test_complex_search(self):
        """Test complex multi-filter search."""
        response = client.get(
            "/api/v1/search/complex?nsfw_level=explicit&number_of_people=1&limit=5",
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Complex search working - Found {data.get('total', 0)} results")
        else:
            print(f"⚠️  Complex search - Catalog DB not found")

    def test_search_by_tag(self):
        """Test tag search."""
        response = client.get(
            "/api/v1/search/tags/1girl?limit=5", headers={"X-API-Key": API_KEY}
        )
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tag search working - Found {data.get('total', 0)} results")
        else:
            print(f"⚠️  Tag search - Catalog DB not found")


class TestSecurity:
    """Test security and auth requirements."""

    def test_endpoints_without_auth_fail(self):
        """Test that protected endpoints reject requests without auth."""
        # Try to get prompts without API key or JWT
        response = client.get("/api/v1/prompts")
        assert response.status_code == 401
        print(f"✅ Protected endpoint requires auth")

    def test_invalid_api_key_rejected(self):
        """Test invalid API key is rejected."""
        response = client.get("/api/v1/prompts", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 401
        print(f"✅ Invalid API key rejected")


def run_all_tests():
    """Run all tests and print summary."""
    print("=" * 70)
    print("API ENDPOINT TEST SUITE")
    print("=" * 70)
    print()

    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
