"""Thread-safe in-memory sliding window rate limiter.

Justification for in-memory limiter:
1. Zero external dependencies: Does not require Redis or external infrastructure in small-team/hackathon deployments.
2. Deterministic unit testing: Can be reset and controlled in test fixtures without state leakage across test cases.
3. Memory safety: Automatically evicts expired request timestamps from the sliding window to prevent unbounded growth.
4. RFC 6585 compliance: Emits standard HTTP 429 responses with Retry-After headers upon threshold violation.
"""

import threading
import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.config import settings


class SlidingWindowRateLimiter:
    """Thread-safe sliding window rate limiter."""

    def __init__(self, limit_per_minute: int = 120, burst_limit: int = 30) -> None:
        self.limit_per_minute = limit_per_minute
        self.burst_limit = burst_limit
        self.window_seconds = 60
        self._lock = threading.Lock()
        # Mapping: client_identifier -> list of timestamps
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check_rate_limit(self, client_key: str) -> tuple[bool, int]:
        """Check if request is allowed. Returns (is_allowed, retry_after_seconds)."""
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            # Filter out timestamps outside current sliding window
            timestamps = [ts for ts in self._requests[client_key] if ts > window_start]
            self._requests[client_key] = timestamps

            # Check minute limit
            if len(timestamps) >= self.limit_per_minute:
                oldest_ts = timestamps[0]
                retry_after = max(1, int(self.window_seconds - (now - oldest_ts)))
                return False, retry_after

            # Check short-burst limit (last 5 seconds)
            burst_window_start = now - 5.0
            burst_count = sum(1 for ts in timestamps if ts > burst_window_start)
            if burst_count >= self.burst_limit:
                return False, 2

            # Record this request
            self._requests[client_key].append(now)
            return True, 0

    def reset(self) -> None:
        """Reset all rate limiter state (used in testing)."""
        with self._lock:
            self._requests.clear()


rate_limiter = SlidingWindowRateLimiter(
    limit_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    burst_limit=settings.RATE_LIMIT_BURST,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing sliding window rate limiting on all incoming requests."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Determine client key from IP (or fall back to loopback)
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Check rate limit
        allowed, retry_after = rate_limiter.check_rate_limit(client_ip)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down.",
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
