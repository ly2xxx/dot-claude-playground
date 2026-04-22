# Rate Limiting Implementation Summary

## What Was Built

A Redis-backed per-IP rate limiter was added to the REST API at `/home/user/dot-claude-playground/api/`.

### Key behaviours
- **Limit**: 100 requests per minute per IP address (configurable via `create_app()` params or env vars)
- **Algorithm**: Fixed-window counter using Redis `INCR` + `EXPIRE` (atomic increment, expiry set on first hit)
- **Rejection response**: HTTP 429 Too Many Requests with `Retry-After` header (value = remaining TTL in seconds)
- **IP identification**: `X-Forwarded-For` header is honoured (for proxy deployments); falls back to `remote_addr`
- **Response body** on rejection includes `error`, `message`, and `retry_after` fields

---

## Files Changed / Created

| File | Status | Description |
|------|--------|-------------|
| `api/rate_limiter.py` | Created | `RateLimiter` class — Redis fixed-window counter, `check()`, `remaining()`, `reset()` |
| `api/app.py` | Created | Flask application factory (`create_app()`), `before_request` rate-limit hook, `/health`, `/api/items` CRUD endpoints |
| `api/config.py` | Created | `Config` / `TestingConfig` / `DevelopmentConfig` / `ProductionConfig` dataclasses |
| `api/__init__.py` | Created | Package marker |
| `api/requirements.txt` | Created | Production deps: `flask>=3.0.0`, `redis>=5.0.0` |
| `api/requirements-dev.txt` | Created | Dev deps: adds `pytest>=8.0.0`, `fakeredis>=2.0.0` |
| `api/tests/test_rate_limiter.py` | Created | Unit tests for `RateLimiter` (uses `fakeredis`) |
| `api/tests/test_api.py` | Created | Integration tests for Flask endpoints + rate-limiting behaviour |

---

## Tests Added

### `tests/test_rate_limiter.py` — 12 unit tests
Tests the `RateLimiter` class in isolation using `fakeredis`:

| Test class | Tests |
|------------|-------|
| `TestCheck` | First request allowed, below limit allowed, boundary, over limit returns `(False, retry_after)`, independent IPs, retry_after is positive int, reset clears counter |
| `TestRemaining` | Equals max before any requests, decreases with each request, never below zero |
| `TestDefaults` | Default max is 100, default window is 60 s |

### `tests/test_api.py` — 18 integration tests
Tests the Flask app end-to-end with `fakeredis` injection via `monkeypatch`:

| Test class | Tests |
|------------|-------|
| `TestHealthEndpoint` | 200 OK, `status: ok`, `version` field, version matches config, JSON content-type, POST returns 405 |
| `TestItemsEndpoints` | Empty list, create 201, ID returned, get by ID, 404 for missing |
| `TestRateLimiting` | Within limit allowed, exceeds → 429, Retry-After header present, body has error/message/retry_after, different IPs independent, X-Forwarded-For used, retry_after ≤ window |

**Total: 30 tests, 30 passing**

---

## Redis Key Design

```
rate_limit:<ip>   →   integer counter
TTL               →   60 seconds (reset on first request in window)
```

Pipeline (`INCR` + `TTL`) is used to read both values atomically in two round-trips; `EXPIRE` is set only on the first request (`count == 1`) to avoid resetting the window mid-flight.

---

## Caveats

1. **No live Redis required for tests** — `fakeredis` is used throughout; no external service dependency.
2. **Fixed-window (not sliding-window)** — a burst of 100 requests at the very end of a window followed by 100 at the start of the next is technically 200 requests in 2 seconds.  A sliding-window or token-bucket approach would be stricter.
3. **In-memory item store** — the `/api/items` endpoints use a Python `dict` rather than a real database; data is lost on restart.
4. **No authentication** — rate limiting is purely IP-based.
5. **Proxy trust** — `X-Forwarded-For` is trusted unconditionally; in production, only headers from trusted proxies should be accepted to prevent IP spoofing.
