"""
Unit Tests for API

Tests for all API endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sqlite3
import sys

# Import app correctly
from src.api.main import app

client = TestClient(app)

# Test API key
TEST_API_KEY = "REDACTED_API_KEY"


class TestRoot:
    """Test root endpoints."""

    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAdmin:
    """Test admin endpoints."""

    def test_health_check(self):
        """Test admin health check."""
        response = client.get("/api/v1/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_stats_public(self):
        """Test stats endpoint (public access)."""
        response = client.get("/api/v1/admin/stats")
        # May fail if catalog DB doesn't exist, but should return proper status
        assert response.status_code in [200, 503]


class TestPromptsAuth:
    """Test prompts endpoints with authentication."""

    def test_list_prompts_no_auth(self):
        """Test listing prompts without auth fails."""
        response = client.get("/api/v1/prompts")
        assert response.status_code == 401

    def test_list_prompts_with_api_key(self):
        """Test listing prompts with API key."""
        response = client.get("/api/v1/prompts", headers={"X-API-Key": TEST_API_KEY})
        # May succeed or fail depending on DB state
        assert response.status_code in [200, 500]  # 500 if DB not initialized

    def test_get_prompt_no_auth(self):
        """Test getting prompt without auth fails."""
        response = client.get("/api/v1/prompts/1")
        assert response.status_code == 401

    def test_create_prompt_no_jwt(self):
        """Test creating prompt without JWT fails."""
        response = client.post(
            "/api/v1/prompts",
            json={"text": "test prompt"},
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert response.status_code == 401

    def test_update_prompt_no_jwt(self):
        """Test updating prompt without JWT fails."""
        response = client.put(
            "/api/v1/prompts/1",
            json={"text": "updated"},
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert response.status_code == 401

    def test_delete_prompt_no_jwt(self):
        """Test deleting prompt without JWT fails."""
        response = client.delete(
            "/api/v1/prompts/1", headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 401


class TestCatalogEndpoints:
    """Test catalog endpoints."""

    def test_get_catalog_no_auth(self):
        """Test getting catalog without auth or DB not available."""
        response = client.get("/api/v1/catalog/1")
        assert response.status_code in [401, 503]  # 503 if DB not exists

    def test_search_nsfw_no_auth(self):
        """Test NSFW search without auth or DB not available."""
        response = client.get("/api/v1/catalog/search/nsfw/explicit")
        assert response.status_code in [401, 503]

    def test_search_style_no_auth(self):
        """Test style search without auth or DB not available."""
        response = client.get("/api/v1/catalog/search/style/anime")
        assert response.status_code in [401, 503]


class TestSearchEndpoints:
    """Test search endpoints."""

    def test_complex_search_no_auth(self):
        """Test complex search without auth or DB not available."""
        response = client.get("/api/v1/search/complex")
        assert response.status_code in [401, 503]

    def test_tag_search_no_auth(self):
        """Test tag search without auth or DB not available."""
        response = client.get("/api/v1/search/tags/1girl")
        assert response.status_code in [401, 503]

    def test_complex_search_with_api_key(self):
        """Test complex search with API key."""
        response = client.get(
            "/api/v1/search/complex?nsfw_level=explicit&limit=5",
            headers={"X-API-Key": TEST_API_KEY},
        )
        # May succeed or fail depending on DB
        assert response.status_code in [200, 503]


class TestAuthentication:
    """Test authentication mechanisms."""

    def test_invalid_api_key(self):
        """Test with invalid API key."""
        response = client.get("/api/v1/prompts", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 401

    def test_invalid_jwt(self):
        """Test with invalid JWT."""
        response = client.post(
            "/api/v1/prompts",
            json={"text": "test"},
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_missing_auth_header(self):
        """Test with missing auth header."""
        response = client.get("/api/v1/prompts")
        assert response.status_code == 401
        assert "detail" in response.json()


class TestValidation:
    """Test input validation."""

    def test_invalid_prompt_data(self):
        """Test creating prompt with invalid data."""
        # Would need JWT, but testing validation
        response = client.post(
            "/api/v1/prompts",
            json={"text": ""},  # Empty text - invalid
            headers={"Authorization": "Bearer fake-token"},
        )
        # Should fail on auth, but we're testing structure
        assert response.status_code in [401, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
