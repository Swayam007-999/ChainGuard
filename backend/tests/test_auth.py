"""Tests for authentication and authorization across all API routes."""

import pytest
from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    """Admin login with correct password returns 200 and sets HttpOnly cookie."""
    response = client.post("/v1/auth/login", json={"password": "test_admin_password_strong_123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"
    assert data["expires_in"] == 28800

    # Verify cookie presence and security flags
    assert "access_token" in response.cookies
    cookie = response.cookies["access_token"]
    assert cookie is not None


def test_login_wrong_password(client: TestClient) -> None:
    """Admin login with incorrect password returns 401 Unauthorized."""
    response = client.post("/v1/auth/login", json={"password": "incorrect_password_attempt"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]
    assert "access_token" not in response.cookies


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("POST", "/v1/fingerprints", {"fp_hex": "a" * 64, "kind": "jwt", "source": "chat.openai.com"}),
        ("POST", "/v1/events/batch", {"events": [{"ts": "2026-11-10T02:00:00Z", "ip": "1.1.1.1", "method": "GET", "path": "/", "status": 200}]}),
        ("GET", "/v1/allowlist", None),
        ("POST", "/v1/allowlist", {"cidr": "10.0.0.0/24", "note": "Test"}),
        ("POST", "/v1/dependencies/scan", None),
        ("GET", "/v1/dependencies", None),
        ("GET", "/v1/incidents", None),
        ("GET", "/v1/incidents/1", None),
        ("POST", "/v1/actions/1/approve", None),
        ("POST", "/v1/actions/1/undo", None),
    ],
)
def test_auth_required_on_every_route(
    client: TestClient, method: str, path: str, payload: dict
) -> None:
    """Every route in /v1 must reject unauthenticated requests with HTTP 401."""
    if method == "POST":
        response = client.post(path, json=payload)
    else:
        response = client.get(path)

    assert response.status_code == 401, f"Route {method} {path} allowed unauthenticated access"


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("POST", "/v1/fingerprints", {"fp_hex": "a" * 64, "kind": "jwt", "source": "chat.openai.com"}),
        ("POST", "/v1/events/batch", {"events": [{"ts": "2026-11-10T02:00:00Z", "ip": "1.1.1.1", "method": "GET", "path": "/", "status": 200}]}),
        ("GET", "/v1/allowlist", None),
        ("GET", "/v1/dependencies", None),
    ],
)
def test_wrong_api_key_rejected(
    client: TestClient, invalid_api_headers: dict, method: str, path: str, payload: dict
) -> None:
    """Providing an invalid X-ChainGuard-Key header must return HTTP 401."""
    if method == "POST":
        response = client.post(path, json=payload, headers=invalid_api_headers)
    else:
        response = client.get(path, headers=invalid_api_headers)

    assert response.status_code == 401
