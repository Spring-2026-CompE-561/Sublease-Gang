import time
from collections.abc import Iterable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# path prefix -> (max_requests, window_seconds)
# More-specific prefixes must come BEFORE more-general ones — first match wins.
RATE_LIMIT_RULES: dict[str, tuple[int, int]] = {
    "/api/v1/auth/login": (5, 60),
    "/api/v1/auth/signup": (3, 60),
    "/api/v1/auth/forgot_password": (3, 60),
    "/api/v1/auth/reset_password": (5, 60),
    "/api/v1/auth/refresh": (10, 60),
    "/api/v1/users/me/password": (5, 60),
    "/api/v1/conversations": (30, 60),
    "/api/v1/listings": (10, 60),
}

# Buckets inactive for longer than this (in seconds) are pruned
_BUCKET_TTL = 3600

# Only throttle write requests. GET/HEAD/OPTIONS pass through so page reloads
# and dev-mode double-mounts don't accidentally hit the limit.
_RATE_LIMITED_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class _TokenBucket:
    __slots__ = ("last_refill", "max_tokens", "refill_rate", "tokens")

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


def _resolve_client_ip(request: Request, trusted_proxies: frozenset[str]) -> str:
    """Resolve the rate-limit key. Trusts X-Forwarded-For only when the
    immediate peer is in `trusted_proxies` — preserves spoofing protection
    when the app is exposed directly without a reverse proxy.
    """
    direct = request.client.host if request.client else "unknown"
    if trusted_proxies and direct in trusted_proxies:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    return direct


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Protect auth, messaging, and posting endpoints from spam using in-memory token buckets."""

    def __init__(
        self,
        app,
        rules: dict[str, tuple[int, int]] | None = None,
        trusted_proxies: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.rules = rules or RATE_LIMIT_RULES
        self.trusted_proxies = frozenset(trusted_proxies or ())
        # key: (client_ip, rule_prefix) -> _TokenBucket
        self.buckets: dict[tuple[str, str], _TokenBucket] = {}

    def _cleanup(self) -> None:
        """Remove buckets that have been inactive for longer than _BUCKET_TTL."""
        now = time.monotonic()
        stale = [
            k for k, b in self.buckets.items() if now - b.last_refill > _BUCKET_TTL
        ]
        for k in stale:
            del self.buckets[k]

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.method not in _RATE_LIMITED_METHODS:
            return await call_next(request)

        path = request.url.path
        client_ip = _resolve_client_ip(request, self.trusted_proxies)

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
                        content={
                            "detail": "Too many requests. Please try again later."
                        },
                        headers={"Retry-After": str(window_sec)},
                    )
                break  # only match the first rule

        return await call_next(request)
