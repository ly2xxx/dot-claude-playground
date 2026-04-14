# Implementation Summary — Rate Limiting (no-ticket)

## What was built

Redis-backed rate limiting middleware was added to the Flask REST API. Each incoming request is counted per IP address using a fixed-window Redis counter. When an IP exceeds 100 requests within a 60-second window, the API returns HTTP 429 Too Many Requests with a `Retry-After` header indicating how many seconds remain until the window resets. The implementation supports X-Forwarded-For headers so it correctly identifies real client IPs behind proxies.

## Files changed

| File | Change type | Description |
|------|-------------|-------------|
| api/rate_limiter.py | Created | `RateLimiter` class using Redis INCR + EXPIRE pipeline; `check()` returns `(allowed, retry_after)` tuple; `remaining()` returns quota left; `reset()` for test helpers |
| api/app.py | Created | Flask application factory (`create_app()`); `before_request` hook enforcing rate limit; REST endpoints `/health`, `/api/items`, `/api/items/<id>`; `X-Forwarded-For` IP extraction |
| api/config.py | Created | `Config` class with `VERSION`, `DEBUG`, `TESTING`; `TestingConfig` subclass |
| api/__init__.py | Created | Package marker |
| api/requirements.txt | Created | Runtime dependencies: `flask>=2.3`, `redis>=5.0` |
| api/requirements-dev.txt | Created | Dev dependencies including `fakeredis>=2.20`, `pytest>=7.0` |
| api/tests/test_rate_limiter.py | Created | Unit tests for `RateLimiter` class (12 tests) |
| api/tests/test_api.py | Created | Integration tests for Flask app with rate limiting (18 tests) |

## Tests

| Test file | Coverage |
|-----------|----------|
| api/tests/test_rate_limiter.py | Unit tests for `RateLimiter.check()`, `remaining()`, defaults; 12 test cases covering first request allowed, below-limit requests, over-limit rejection, retry_after value, IP isolation, reset |
| api/tests/test_api.py | Integration tests across health endpoint, items CRUD, and rate limiting; 18 test cases including 429 status, Retry-After header, body structure, cross-endpoint counting, X-Forwarded-For IP extraction |

**Total: 30 tests, all passing.**

## Acceptance criteria status

| Criterion | Status |
|-----------|--------|
| Max 100 requests per minute per IP address | Implemented — `RATE_LIMIT_MAX = 100`, `RATE_LIMIT_WINDOW = 60` |
| Return HTTP 429 when limit exceeded | Implemented — `before_request` hook returns 429 |
| Include Retry-After header on 429 | Implemented — `response.headers["Retry-After"] = str(retry_after)` |
| Use Redis for the counter | Implemented — Redis INCR + EXPIRE pipeline in `RateLimiter.check()` |

## Caveats & follow-ups

- **Fixed-window algorithm**: The implementation uses a fixed-window counter (not sliding window). A burst of requests at the end of one window plus the start of the next can effectively double the rate — up to 200 requests in ~1 second across the window boundary. A sliding window (using Redis sorted sets with timestamps) would be more precise but adds complexity.
- **No rate-limit response headers on allowed requests**: The current implementation does not return `X-RateLimit-Remaining` or `X-RateLimit-Reset` headers on successful responses. These are common API conventions and could be added using `g.rate_limit_remaining` which is already computed.
- **IP spoofing via X-Forwarded-For**: Trusting `X-Forwarded-For` without validation allows clients to spoof their IP if not behind a trusted proxy. In production, only trust this header from known proxy IPs.
