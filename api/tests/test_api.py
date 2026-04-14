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

class FakeRedisFactory:
    """Returns a single shared FakeRedis instance (simulates one Redis server)."""

    def __init__(self):
        self._server = fakeredis.FakeServer()

    def from_url(self, url, **kwargs):
        return fakeredis.FakeRedis(server=self._server, decode_responses=True)


@pytest.fixture
def app(monkeypatch):
    """Create a test Flask application backed by fakeredis."""
    fake_factory = FakeRedisFactory()

    import redis as _redis
    monkeypatch.setattr(_redis, "from_url", fake_factory.from_url)

    application = create_app(redis_url="redis://localhost/0", testing=True)
    return application


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
    """Tests that the rate limit is applied and the correct headers are set."""

    def _exhaust_limit(self, client, ip: str, limit: int):
        """Make `limit` requests from the given IP."""
        for _ in range(limit):
            client.get("/health", headers={"X-Forwarded-For": ip})

    def test_requests_within_limit_are_allowed(self, app, client):
        """The first N requests (up to the limit) should all succeed."""
        # The test app uses the real RateLimiter with default settings (100).
        # We just verify a modest number of requests succeeds.
        ip = "10.1.1.1"
        for _ in range(10):
            resp = client.get("/health", headers={"X-Forwarded-For": ip})
            assert resp.status_code == 200

    def test_exceeding_limit_returns_429(self, monkeypatch, app, client):
        """The (max+1)th request from the same IP should get 429."""
        # Lower the limit to 3 so the test runs fast
        import rate_limiter as rl_module
        original_max = rl_module.RATE_LIMIT_MAX
        original_window = rl_module.RATE_LIMIT_WINDOW

        ip = "10.2.2.2"

        # Patch the limiter on the app to use a 3-request limit
        fake_redis = fakeredis.FakeRedis(decode_responses=True)
        small_limiter = RateLimiter(fake_redis, max_requests=3, window_seconds=60)

        # Inject the small limiter by patching before_request
        with app.test_request_context():
            pass  # ensure request context works

        # We patch via a new app with custom limiter
        import redis as _redis

        def mock_from_url(url, **kwargs):
            return fake_redis

        monkeypatch.setattr(_redis, "from_url", mock_from_url)
        monkeypatch.setattr(rl_module, "RATE_LIMIT_MAX", 3)

        small_app = create_app(redis_url="redis://localhost/0", testing=True)
        test_client = small_app.test_client()

        # 3 allowed
        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})
            assert resp.status_code == 200

        # 4th should be rejected
        resp = test_client.get("/health", headers={"X-Forwarded-For": ip})
        assert resp.status_code == 429

    def test_429_response_has_retry_after_header(self, monkeypatch, app, client):
        """HTTP 429 response must include a Retry-After header."""
        import rate_limiter as rl_module
        import redis as _redis

        ip = "10.3.3.3"
        fake_redis = fakeredis.FakeRedis(decode_responses=True)

        def mock_from_url(url, **kwargs):
            return fake_redis

        monkeypatch.setattr(_redis, "from_url", mock_from_url)
        monkeypatch.setattr(rl_module, "RATE_LIMIT_MAX", 2)

        small_app = create_app(redis_url="redis://localhost/0", testing=True)
        test_client = small_app.test_client()

        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})

        assert resp.status_code == 429
        assert "Retry-After" in resp.headers
        assert int(resp.headers["Retry-After"]) > 0

    def test_429_response_body_contains_error_info(self, monkeypatch, client):
        """The 429 body must contain error, message, and retry_after fields."""
        import rate_limiter as rl_module
        import redis as _redis

        ip = "10.4.4.4"
        fake_redis = fakeredis.FakeRedis(decode_responses=True)

        def mock_from_url(url, **kwargs):
            return fake_redis

        monkeypatch.setattr(_redis, "from_url", mock_from_url)
        monkeypatch.setattr(rl_module, "RATE_LIMIT_MAX", 2)

        small_app = create_app(redis_url="redis://localhost/0", testing=True)
        test_client = small_app.test_client()

        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})

        data = resp.get_json()
        assert data["error"] == "Too Many Requests"
        assert "message" in data
        assert "retry_after" in data

    def test_different_ips_do_not_share_quota(self, monkeypatch):
        """Exhausting the quota for one IP must not affect another IP."""
        import rate_limiter as rl_module
        import redis as _redis

        fake_redis = fakeredis.FakeRedis(decode_responses=True)

        def mock_from_url(url, **kwargs):
            return fake_redis

        monkeypatch.setattr(_redis, "from_url", mock_from_url)
        monkeypatch.setattr(rl_module, "RATE_LIMIT_MAX", 2)

        app = create_app(redis_url="redis://localhost/0", testing=True)
        test_client = app.test_client()

        ip_a = "10.5.5.5"
        ip_b = "10.6.6.6"

        # Exhaust ip_a
        for _ in range(3):
            test_client.get("/health", headers={"X-Forwarded-For": ip_a})

        last_a = test_client.get("/health", headers={"X-Forwarded-For": ip_a})
        first_b = test_client.get("/health", headers={"X-Forwarded-For": ip_b})

        assert last_a.status_code == 429
        assert first_b.status_code == 200

    def test_x_forwarded_for_header_is_used_for_ip(self, monkeypatch):
        """The middleware must use X-Forwarded-For to identify the client IP."""
        import rate_limiter as rl_module
        import redis as _redis

        fake_redis = fakeredis.FakeRedis(decode_responses=True)

        def mock_from_url(url, **kwargs):
            return fake_redis

        monkeypatch.setattr(_redis, "from_url", mock_from_url)
        monkeypatch.setattr(rl_module, "RATE_LIMIT_MAX", 2)

        app = create_app(redis_url="redis://localhost/0", testing=True)
        test_client = app.test_client()

        ip = "10.7.7.7"
        for _ in range(3):
            resp = test_client.get("/health", headers={"X-Forwarded-For": ip})

        assert resp.status_code == 429
