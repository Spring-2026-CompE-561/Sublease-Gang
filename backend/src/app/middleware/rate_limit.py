import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# path prefix -> (max_requests, window_seconds)
RATE_LIMIT_RULES: dict[str, tuple[int, int]] = {
    "/api/v1/auth/login": (5, 60),        # 5 requests per minute
    "/api/v1/auth/signup": (3, 60),       # 3 requests per minute
    "/api/v1/conversations": (30, 60),    # 30 messages per minute
    "/api/v1/listings": (10, 60),         # 10 posts per minute
}

# Buckets inactive for longer than this (in seconds) are pruned
_BUCKET_TTL = 3600


class _TokenBucket:
    __slots__ = ("tokens", "last_refill", "max_tokens", "refill_rate")

    def __init__(self, max_tokens: int, refill_rate: float) -> None:
        self.tokens = float(max_tokens)
        self.last_refill = time.monotonic()
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate  # tokens per second

    def consume(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Protect auth, messaging, and posting endpoints from spam using in-memory token buckets."""

    def __init__(self, app, rules: dict[str, tuple[int, int]] | None = None) -> None:
        super().__init__(app)
        self.rules = rules or RATE_LIMIT_RULES
        # key: (client_ip, rule_prefix) -> _TokenBucket
        self.buckets: dict[tuple[str, str], _TokenBucket] = {}

    def _cleanup(self) -> None:
        """Remove buckets that have been inactive for longer than _BUCKET_TTL."""
        now = time.monotonic()
        stale = [k for k, b in self.buckets.items() if now - b.last_refill > _BUCKET_TTL]
        for k in stale:
            del self.buckets[k]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        for prefix, (max_req, window_sec) in self.rules.items():
            if path.startswith(prefix):
                key = (client_ip, prefix)
                bucket = self.buckets.get(key)
                if bucket is None:
                    # Periodically prune stale buckets before adding new ones
                    self._cleanup()
                    refill_rate = max_req / window_sec
                    bucket = _TokenBucket(max_tokens=max_req, refill_rate=refill_rate)
                    self.buckets[key] = bucket

                if not bucket.consume():
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests. Please try again later."},
                        headers={"Retry-After": str(window_sec)},
                    )
                break  # only match the first rule

        return await call_next(request)
