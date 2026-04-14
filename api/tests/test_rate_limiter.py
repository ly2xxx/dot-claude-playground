"""
Unit tests for the RateLimiter class.

These tests use fakeredis so no real Redis server is required.
"""

import pytest
import fakeredis

from rate_limiter import RateLimiter, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW


@pytest.fixture
def fake_redis():
    """Return a fakeredis client that behaves like a real Redis client."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def limiter(fake_redis):
    return RateLimiter(fake_redis, max_requests=5, window_seconds=60)


# ---------------------------------------------------------------------------
# check() method
# ---------------------------------------------------------------------------

class TestCheck:
    def test_first_request_is_allowed(self, limiter):
        allowed, retry_after = limiter.check("192.168.1.1")
        assert allowed is True
        assert retry_after == 0

    def test_requests_below_limit_are_allowed(self, limiter):
        ip = "10.0.0.1"
        for _ in range(5):
            allowed, _ = limiter.check(ip)
            assert allowed is True

    def test_request_at_limit_boundary_is_allowed(self, limiter):
        ip = "10.0.0.2"
        # Exhaust all 5 slots
        for _ in range(5):
            limiter.check(ip)
        # 5th request should still be allowed
        # Re-use allowed from 5th iteration above — check 6th
        allowed, _ = limiter.check(ip)
        assert allowed is False

    def test_request_over_limit_returns_429_info(self, limiter):
        ip = "10.0.0.3"
        for _ in range(5):
            limiter.check(ip)
        allowed, retry_after = limiter.check(ip)
        assert allowed is False
        assert retry_after > 0

    def test_different_ips_are_tracked_independently(self, limiter):
        ip_a = "1.1.1.1"
        ip_b = "2.2.2.2"
        # Exhaust ip_a
        for _ in range(6):
            limiter.check(ip_a)
        allowed_a, _ = limiter.check(ip_a)
        allowed_b, _ = limiter.check(ip_b)
        assert allowed_a is False
        assert allowed_b is True

    def test_retry_after_is_positive_integer_when_limited(self, limiter):
        ip = "3.3.3.3"
        for _ in range(6):
            limiter.check(ip)
        _, retry_after = limiter.check(ip)
        assert isinstance(retry_after, int)
        assert retry_after > 0

    def test_reset_clears_counter(self, limiter):
        ip = "4.4.4.4"
        for _ in range(6):
            limiter.check(ip)
        limiter.reset(ip)
        allowed, _ = limiter.check(ip)
        assert allowed is True


# ---------------------------------------------------------------------------
# remaining() method
# ---------------------------------------------------------------------------

class TestRemaining:
    def test_remaining_equals_max_before_any_requests(self, limiter):
        assert limiter.remaining("5.5.5.5") == 5

    def test_remaining_decreases_with_each_request(self, limiter):
        ip = "6.6.6.6"
        limiter.check(ip)
        assert limiter.remaining(ip) == 4
        limiter.check(ip)
        assert limiter.remaining(ip) == 3

    def test_remaining_never_goes_below_zero(self, limiter):
        ip = "7.7.7.7"
        for _ in range(10):
            limiter.check(ip)
        assert limiter.remaining(ip) == 0


# ---------------------------------------------------------------------------
# Default constants
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_default_max_is_100(self, fake_redis):
        limiter = RateLimiter(fake_redis)
        assert limiter.max_requests == RATE_LIMIT_MAX == 100

    def test_default_window_is_60_seconds(self, fake_redis):
        limiter = RateLimiter(fake_redis)
        assert limiter.window_seconds == RATE_LIMIT_WINDOW == 60
