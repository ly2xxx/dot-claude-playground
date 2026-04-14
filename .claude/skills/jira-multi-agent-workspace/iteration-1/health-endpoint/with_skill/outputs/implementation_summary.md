## Implementation Summary — ENG-101: /health endpoint with version from config

### What was built

A `GET /health` endpoint was added to the existing Python Flask API (`api/app.py`). The endpoint returns `{"status": "ok", "version": "<from config>"}` with HTTP 200. The version value is read from `api/config.py` via `app.config["VERSION"]`, decoupling the version string from the endpoint implementation. A `Config` class with `VERSION = "1.0.0"` and a `TestingConfig` subclass were introduced.

### Files changed

| File | Change type | Description |
|------|-------------|-------------|
| `/home/user/dot-claude-playground/api/app.py` | Modified | Added `from config import Config`, loads Config via `app.config.from_object(Config)`, updated `/health` route to return version field, added `rate_limit_max`/`rate_limit_window` params to `create_app()` for testability |
| `/home/user/dot-claude-playground/api/config.py` | Created | Defines `Config` class with `VERSION = "1.0.0"`, `DEBUG`, and `TESTING` flags; `TestingConfig` subclass sets `TESTING = True` |
| `/home/user/dot-claude-playground/api/tests/test_api.py` | Modified | Added 6 new `TestHealthEndpoint` test cases; refactored `TestRateLimiting` to use a `make_app()` helper that passes `rate_limit_max`/`rate_limit_window` directly to `create_app()`, fixing previously-broken rate-limit tests; added `test_retry_after_value_is_positive` case |
| `/home/user/dot-claude-playground/api/requirements.txt` | Created | Runtime dependencies: `flask>=3.0.0`, `redis>=5.0.0` |
| `/home/user/dot-claude-playground/api/requirements-dev.txt` | Created | Dev/test dependencies: `-r requirements.txt`, `pytest>=8.0.0`, `fakeredis>=2.0.0` |

### Tests

| Test file | Coverage |
|-----------|----------|
| `api/tests/test_api.py` | 6 new health endpoint cases: HTTP 200 response, `status` field equals `"ok"`, `version` field present and non-empty string, version matches `app.config["VERSION"]`, `Content-Type: application/json`, POST returns 405; 1 new rate-limit case: `test_retry_after_value_is_positive`; existing 5 rate-limit cases fixed via `make_app()` refactor |

All 30 tests pass (`python -m pytest api/tests/ -v`).

### Acceptance criteria status

| Criterion | Status |
|-----------|--------|
| `GET /health` returns HTTP 200 | Implemented |
| Response body is `{"status": "ok", "version": "<from config>"}` | Implemented |
| Version value comes from config, not hardcoded in handler | Implemented |

### Caveats & follow-ups

- `VERSION` is currently hardcoded as `"1.0.0"` in `api/config.py`. In production, this should be sourced from a build artifact (e.g., a `VERSION` file, `pyproject.toml`, or an environment variable).
- The rate-limiting tests required a refactor of `create_app()` to accept `rate_limit_max`/`rate_limit_window` parameters directly; this is a clean improvement that makes the factory more testable without relying on module-level constant patching.
