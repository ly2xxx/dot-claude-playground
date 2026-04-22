"""
Rate limiting middleware using Redis.

Implements a sliding window counter strategy:
- Key format: rate_limit:<ip>
- Max 100 requests per minute per IP
- Returns 429 Too Many Requests with Retry-After header when limit exceeded
"""

import math
import time
from typing import Optional

import redis


RATE_LIMIT_MAX = 100       # max requests per window
RATE_LIMIT_WINDOW = 60     # window size in seconds


class RateLimiter:
    """
    Redis-backed rate limiter using a fixed window counter per IP.

    Each IP address gets a counter key that expires after RATE_LIMIT_WINDOW
    seconds.  On every request:
      1. INCR the counter atomically.
      2. If the counter is 1 (first hit in this window) set EXPIRE.
      3. If the counter exceeds RATE_LIMIT_MAX, return a 429 response.
    """

    def __init__(self, redis_client: redis.Redis, max_requests: int = RATE_LIMIT_MAX,
                 window_seconds: int = RATE_LIMIT_WINDOW):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _key(self, ip: str) -> str:
        return f"rate_limit:{ip}"

    def check(self, ip: str) -> tuple[bool, int]:
        """
        Check whether the IP is within the rate limit.

        Returns:
            (allowed, retry_after)
            - allowed: True if the request should proceed, False if rejected.
            - retry_after: seconds until the window resets (only meaningful when
              allowed is False).
        """
        key = self._key(ip)
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        count, ttl = pipe.execute()

        # First request in this window — set the expiry
        if count == 1:
            self.redis.expire(key, self.window_seconds)
            ttl = self.window_seconds

        if ttl < 0:
            # Key exists but has no TTL (shouldn't happen normally) — fix it.
            self.redis.expire(key, self.window_seconds)
            ttl = self.window_seconds

        if count > self.max_requests:
            retry_after = ttl if ttl > 0 else self.window_seconds
            return False, retry_after

        return True, 0

    def remaining(self, ip: str) -> int:
        """Return how many requests remain in the current window."""
        key = self._key(ip)
        count = self.redis.get(key)
        if count is None:
            return self.max_requests
        return max(0, self.max_requests - int(count))

    def reset(self, ip: str) -> None:
        """Reset the rate limit counter for an IP (useful in tests)."""
        self.redis.delete(self._key(ip))
