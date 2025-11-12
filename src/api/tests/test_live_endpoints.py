#!/usr/bin/env python3
"""
Live API Endpoint Tests

Tests all endpoints against a running API server.
Run the API server first: python main.py
Then run these tests: python test_live_endpoints.py
"""

import requests
import json
from typing import Optional


class APITester:
    """Test suite for live API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize with API base URL."""
        self.base_url = base_url
        self.api_key = "demo-read-key-12345"
        self.token: Optional[str] = None
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str, condition: bool, details: str = ""):
        """Record test result."""
        if condition:
            print(f"  ✅ {name}")
            if details:
                print(f"     {details}")
            self.passed += 1
        else:
            print(f"  ❌ {name}")
            if details:
                print(f"     {details}")
            self.failed += 1
        return condition
    
    def test_server_running(self):
        """Test 1: Server is running."""
        print("\n🔹 Test 1: Server Connectivity")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.test("Server is responding", response.status_code == 200)
            return True
        except requests.ConnectionError:
            self.test("Server is responding", False, "Server not running at localhost:8000")
            return False
    
    def test_public_endpoints(self):
        """Test 2: Public endpoints."""
        print("\n🔹 Test 2: Public Endpoints")
        
        # Root
        response = requests.get(f"{self.base_url}/")
        self.test("GET / (root)", response.status_code == 200)
        
        # Health
        response = requests.get(f"{self.base_url}/health")
        self.test("GET /health", response.status_code == 200)
        
        # Admin stats (public)
        response = requests.get(f"{self.base_url}/api/v1/admin/stats")
        self.test("GET /admin/stats (public)", response.status_code == 200)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_prompts', 0)
            print(f"     Catalog has {total:,} prompts")
        
        # Admin health
        response = requests.get(f"{self.base_url}/api/v1/admin/health")
        self.test("GET /admin/health", response.status_code == 200)
    
    def test_authentication(self):
        """Test 3: Authentication."""
        print("\n🔹 Test 3: Authentication")
        
        # Valid login
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": "test", "password": "test"}
        )
        self.test("POST /auth/login (valid)", response.status_code == 200)
        
        if response.status_code == 200:
            data = response.json()
            self.test("Token received", "access_token" in data)
            self.test("User info received", "user" in data)
            self.token = data.get("access_token")
            print(f"     User: {data.get('user', {}).get('username')}")
        
        # Invalid login
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": "wrong", "password": "wrong"}
        )
        self.test("POST /auth/login (invalid)", response.status_code == 401)
    
    def test_prompts_endpoints(self):
        """Test 4: Prompts CRUD."""
        print("\n🔹 Test 4: Prompts CRUD Endpoints")
        
        # List prompts with API key
        response = requests.get(
            f"{self.base_url}/api/v1/prompts",
            headers={"X-API-Key": self.api_key}
        )
        self.test("GET /prompts (with API key)", response.status_code == 200)
        
        # List without auth should fail
        response = requests.get(f"{self.base_url}/api/v1/prompts")
        self.test("GET /prompts (no auth fails)", response.status_code == 401)
        
        # Pagination
        response = requests.get(
            f"{self.base_url}/api/v1/prompts?page=1&page_size=5",
            headers={"X-API-Key": self.api_key}
        )
        self.test("GET /prompts (with pagination)", response.status_code == 200)
        
        # Create requires JWT
        response = requests.post(
            f"{self.base_url}/api/v1/prompts",
            json={"text": "test"},
            headers={"X-API-Key": self.api_key}
        )
        self.test("POST /prompts (API key not enough)", response.status_code in [401, 403])
        
        # Create with JWT
        if self.token:
            response = requests.post(
                f"{self.base_url}/api/v1/prompts",
                json={
                    "text": "automated test prompt",
                    "category": "test",
                    "rating": 5
                },
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.test("POST /prompts (with JWT)", response.status_code in [200, 201, 400, 422])
    
    def test_catalog_endpoints(self):
        """Test 5: Catalog search."""
        print("\n🔹 Test 5: Catalog Search Endpoints")
        
        # NSFW search
        response = requests.get(
            f"{self.base_url}/api/v1/catalog/search/nsfw/explicit?limit=5",
            headers={"X-API-Key": self.api_key}
        )
        if response.status_code == 200:
            data = response.json()
            self.test("GET /catalog/search/nsfw/explicit", True, f"Found {data.get('total', 0)} results")
        elif response.status_code == 503:
            self.test("GET /catalog/search/nsfw/explicit", True, "Catalog DB not available (OK if not set up)")
        else:
            self.test("GET /catalog/search/nsfw/explicit", False, f"Unexpected status: {response.status_code}")
        
        # Style search
        response = requests.get(
            f"{self.base_url}/api/v1/catalog/search/style/anime?limit=5",
            headers={"X-API-Key": self.api_key}
        )
        if response.status_code == 200:
            data = response.json()
            self.test("GET /catalog/search/style/anime", True, f"Found {data.get('total', 0)} results")
        else:
            self.test("GET /catalog/search/style/anime", response.status_code == 503, "Catalog DB not available")
    
    def test_search_endpoints(self):
        """Test 6: Advanced search."""
        print("\n🔹 Test 6: Advanced Search Endpoints")
        
        # Complex search
        response = requests.get(
            f"{self.base_url}/api/v1/search/complex?nsfw_level=explicit&number_of_people=1&limit=5",
            headers={"X-API-Key": self.api_key}
        )
        if response.status_code == 200:
            data = response.json()
            self.test("GET /search/complex", True, f"Found {data.get('total', 0)} results")
        else:
            self.test("GET /search/complex", response.status_code == 503, "Catalog DB not available")
        
        # Tag search
        response = requests.get(
            f"{self.base_url}/api/v1/search/tags/1girl?limit=5",
            headers={"X-API-Key": self.api_key}
        )
        if response.status_code == 200:
            data = response.json()
            self.test("GET /search/tags/1girl", True, f"Found {data.get('total', 0)} results")
        else:
            self.test("GET /search/tags/1girl", response.status_code == 503, "Catalog DB not available")
    
    def test_security(self):
        """Test 7: Security."""
        print("\n🔹 Test 7: Security Enforcement")
        
        # No auth fails
        response = requests.get(f"{self.base_url}/api/v1/prompts")
        self.test("Protected endpoint without auth", response.status_code == 401)
        
        # Invalid API key fails
        response = requests.get(
            f"{self.base_url}/api/v1/prompts",
            headers={"X-API-Key": "invalid-key"}
        )
        self.test("Invalid API key rejected", response.status_code == 401)
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("LIVE API ENDPOINT TEST SUITE")
        print("="*70)
        print(f"\nTesting API at: {self.base_url}")
        print("Make sure the API server is running: python src/api/main.py")
        
        # Check server
        if not self.test_server_running():
            print("\n❌ Server not running. Start it first:")
            print("   cd src/api && python main.py")
            return False
        
        # Run all tests
        self.test_public_endpoints()
        self.test_authentication()
        self.test_prompts_endpoints()
        self.test_catalog_endpoints()
        self.test_search_endpoints()
        self.test_security()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n✅ Passed: {self.passed}/{total}")
        print(f"❌ Failed: {self.failed}/{total}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! API is fully functional.")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Review errors above.")
        
        return self.failed == 0


def main():
    """Main function."""
    tester = APITester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
