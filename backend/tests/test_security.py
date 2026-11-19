"""Tests for security headers, rate limiting, and 501 stub endpoints."""

from app.rate_limiter import rate_limiter
from fastapi.testclient import TestClient


def test_security_headers_present(client: TestClient) -> None:
    """Rule 8: Verify defensive security headers on all responses."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "0"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")


def test_rate_limiter_exceeded_returns_429(client: TestClient) -> None:
    """Burst of requests exceeding threshold must trigger HTTP 429 with Retry-After header."""
    rate_limiter.reset()

    # The burst limit is 30 requests in a 5-second window
    # Send 35 rapid requests from client
    got_429 = False
    for i in range(35):
        resp = client.get("/health")
        if resp.status_code == 429:
            got_429 = True
            assert "Retry-After" in resp.headers
            assert int(resp.headers["Retry-After"]) >= 1
            data = resp.json()
            assert "Too many requests" in data["detail"]
            break

    assert got_429 is True, "Rate limiter did not trigger HTTP 429 on aggressive burst"



