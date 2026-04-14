"""
Simple REST API with Redis-backed rate limiting.

Endpoints:
  GET  /health           — liveness check (returns status and version from config)
  GET  /api/items        — list items
  POST /api/items        — create an item
  GET  /api/items/<id>   — get a single item

Rate limit: 100 requests per minute per IP.
Exceeded requests receive HTTP 429 with a Retry-After header.
"""

import os

import redis
from flask import Flask, jsonify, request, g

from rate_limiter import RateLimiter
from config import Config

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(redis_url: str = None, testing: bool = False, app_config=None,
               rate_limit_max: int = None, rate_limit_window: int = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["TESTING"] = testing

    if app_config is not None:
        if isinstance(app_config, dict):
            app.config.update(app_config)
        else:
            app.config.from_object(app_config)

    # ------------------------------------------------------------------
    # Redis connection
    # ------------------------------------------------------------------
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    redis_client = redis.from_url(redis_url, decode_responses=True)

    from rate_limiter import RATE_LIMIT_MAX, RATE_LIMIT_WINDOW
    limiter = RateLimiter(
        redis_client,
        max_requests=rate_limit_max if rate_limit_max is not None else RATE_LIMIT_MAX,
        window_seconds=rate_limit_window if rate_limit_window is not None else RATE_LIMIT_WINDOW,
    )

    # ------------------------------------------------------------------
    # Rate-limiting before_request hook
    # ------------------------------------------------------------------
    @app.before_request
    def apply_rate_limit():
        # Use X-Forwarded-For if behind a proxy, otherwise remote_addr
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip:
            ip = ip.split(",")[0].strip()

        allowed, retry_after = limiter.check(ip)
        if not allowed:
            response = jsonify({
                "error": "Too Many Requests",
                "message": (
                    f"Rate limit exceeded. Maximum {limiter.max_requests} requests "
                    f"per {limiter.window_seconds} seconds per IP."
                ),
                "retry_after": retry_after,
            })
            response.status_code = 429
            response.headers["Retry-After"] = str(retry_after)
            return response

        # Stash remaining quota on g for optional use in responses
        g.rate_limit_remaining = limiter.remaining(ip)

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    # In-memory store so the example works without a database
    _items: dict = {}
    _next_id: list = [1]   # mutable container to allow mutation in closures

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "version": app.config["VERSION"]}), 200

    @app.route("/api/items", methods=["GET"])
    def list_items():
        return jsonify({"items": list(_items.values())})

    @app.route("/api/items", methods=["POST"])
    def create_item():
        body = request.get_json(silent=True) or {}
        item_id = _next_id[0]
        _next_id[0] += 1
        item = {"id": item_id, **body}
        _items[item_id] = item
        return jsonify(item), 201

    @app.route("/api/items/<int:item_id>", methods=["GET"])
    def get_item(item_id: int):
        item = _items.get(item_id)
        if item is None:
            return jsonify({"error": "Not Found"}), 404
        return jsonify(item)

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
