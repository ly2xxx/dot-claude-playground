"""
Integration tests for the Flask REST API with rate limiting.

Uses fakeredis so no live Redis is required.
"""

import pytest
import fakeredis

from app import create_app
from rate_limiter import RateLimiter


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def make_app(monkeypatch, rate_limit_max: int = 100, rate_limit_window: int = 60):
    """Helper that creates a test Flask app backed by a fresh FakeRedis instance."""
    fake_redis = fakeredis.FakeRedis(decode_responses=True)

    import redis as _redis
    monkeypatch.setattr(_redis, "from_url", lambda url, **kw: fake_redis)

    return create_app(
        redis_url="redis://localhost/0",
        testing=True,
        rate_limit_max=rate_limit_max,
        rate_limit_window=rate_limit_window,
    )


@pytest.fixture
def app(monkeypatch):
    """Default test app with a 100-request limit."""
    return make_app(monkeypatch, rate_limit_max=100)


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_ok_status(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_health_returns_version_field(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_health_version_matches_config(self, app, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["version"] == app.config["VERSION"]

    def test_health_response_is_json(self, client):
        resp = client.get("/health")
        assert resp.content_type == "application/json"

    def test_health_post_returns_405(self, client):
        resp = client.post("/health")
        assert resp.status_code == 405


# ---------------------------------------------------------------------------
# Items endpoints
# ---------------------------------------------------------------------------

class TestItemsEndpoints:
    def test_list_items_returns_empty_list_initially(self, client):
        resp = client.get("/api/items")
        assert resp.status_code == 200
        assert resp.get_json() == {"items": []}

    def test_create_item_returns_201(self, client):
        resp = client.post("/api/items", json={"name": "widget"})
        assert resp.status_code == 201

    def test_create_item_returns_item_with_id(self, client):
        resp = client.post("/api/items", json={"name": "gadget"})
        data = resp.get_json()
        assert "id" in data
        assert data["name"] == "gadget"

    def test_get_item_returns_created_item(self, client):
        created = client.post("/api/items", json={"name": "thing"}).get_json()
        resp = client.get(f"/api/items/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "thing"

    def test_get_nonexistent_item_returns_404(self, client):
        resp = client.get("/api/items/9999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Rate limiting behaviour
# ---------------------------------------------------------------------------

class TestRateLimiting:
    """Tests that the rate limit is applied and the correct headers are returned."""

    def test_requests_within_limit_are_allowed(self, monkeypatch):
        """The first N requests (up to the limit) should all succeed."""
        small_app = make_app(monkeypatch, rate_limit_max=5)
        test_client = small_app.test_client()
        ip = "10.1.1.1"
        for _ in range(5):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})
            assert resp.status_code == 200

    def test_exceeding_limit_returns_429(self, monkeypatch):
        """The (max+1)th request from the same IP should get 429."""
        small_app = make_app(monkeypatch, rate_limit_max=3)
        test_client = small_app.test_client()
        ip = "10.2.2.2"

        # First 3 allowed
        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})
            assert resp.status_code == 200

        # 4th should be rejected
        resp = test_client.get("/health", headers={"X-Forwarded-For": ip})
        assert resp.status_code == 429

    def test_429_response_has_retry_after_header(self, monkeypatch):
        """HTTP 429 response must include a Retry-After header."""
        small_app = make_app(monkeypatch, rate_limit_max=2)
        test_client = small_app.test_client()
        ip = "10.3.3.3"

        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})

        assert resp.status_code == 429
        assert "Retry-After" in resp.headers
        assert int(resp.headers["Retry-After"]) > 0

    def test_429_response_body_contains_error_info(self, monkeypatch):
        """The 429 body must contain error, message, and retry_after fields."""
        small_app = make_app(monkeypatch, rate_limit_max=2)
        test_client = small_app.test_client()
        ip = "10.4.4.4"

        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})

        data = resp.get_json()
        assert data["error"] == "Too Many Requests"
        assert "message" in data
        assert "retry_after" in data
        assert isinstance(data["retry_after"], int)
        assert data["retry_after"] > 0

    def test_different_ips_do_not_share_quota(self, monkeypatch):
        """Exhausting the quota for one IP must not affect another IP."""
        small_app = make_app(monkeypatch, rate_limit_max=2)
        test_client = small_app.test_client()

        ip_a = "10.5.5.5"
        ip_b = "10.6.6.6"

        # Exhaust ip_a (3 requests, limit is 2)
        for _ in range(3):
            test_client.get("/health", headers={"X-Forwarded-For": ip_a})

        last_a = test_client.get("/health", headers={"X-Forwarded-For": ip_a})
        first_b = test_client.get("/health", headers={"X-Forwarded-For": ip_b})

        assert last_a.status_code == 429
        assert first_b.status_code == 200

    def test_x_forwarded_for_header_is_used_for_ip(self, monkeypatch):
        """The middleware must use X-Forwarded-For to identify the client IP."""
        small_app = make_app(monkeypatch, rate_limit_max=2)
        test_client = small_app.test_client()
        ip = "10.7.7.7"

        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})

        assert resp.status_code == 429

    def test_retry_after_value_is_positive(self, monkeypatch):
        """Retry-After header value must be a positive integer (seconds)."""
        small_app = make_app(monkeypatch, rate_limit_max=1, rate_limit_window=30)
        test_client = small_app.test_client()
        ip = "10.8.8.8"

        test_client.get("/health", headers={"X-Forwarded-For": ip})
        resp = test_client.get("/health", headers={"X-Forwarded-For": ip})

        assert resp.status_code == 429
        retry_after = int(resp.headers["Retry-After"])
        assert 0 < retry_after <= 30
