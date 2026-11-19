"""Tests for /v1/events/batch endpoint: batch sizing, IP validation, SQLi safety."""

from app.models import Event
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_oversized_batch_rejected(client: TestClient, valid_api_headers: dict) -> None:
    """A batch exceeding 500 events must be rejected with HTTP 422 Unprocessable Entity."""
    oversized_events = [
        {
            "ts": "2026-11-10T02:00:00Z",
            "ip": "198.51.100.1",
            "method": "GET",
            "path": f"/test/{i}",
            "status": 200,
            "ua": "TestAgent/1.0",
            "flags": [],
            "token_fps": [],
        }
        for i in range(501)  # Exceeds max 500
    ]

    response = client.post(
        "/v1/events/batch",
        json={"events": oversized_events},
        headers=valid_api_headers,
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("events" in str(err) for err in errors)


def test_malformed_ip_rejected(client: TestClient, valid_api_headers: dict) -> None:
    """Events containing non-compliant IP addresses must be rejected with HTTP 422."""
    bad_ips = [
        "999.999.999.999",
        "invalid_ip_string",
        "192.168.1.1/24",  # CIDR notation is not a single host IP
        "1.2.3.4.5",
        "300.1.1.1",
        "fe80:::1",
    ]

    for bad_ip in bad_ips:
        payload = {
            "events": [
                {
                    "ts": "2026-11-10T02:00:00Z",
                    "ip": bad_ip,
                    "method": "GET",
                    "path": "/api/v1/test",
                    "status": 200,
                    "ua": "Mozilla/5.0",
                }
            ]
        }
        response = client.post(
            "/v1/events/batch",
            json=payload,
            headers=valid_api_headers,
        )
        assert response.status_code == 422, f"Failed to reject malformed IP: {bad_ip}"


def test_sqli_strings_stored_harmlessly(
    client: TestClient, valid_api_headers: dict, db_session: Session
) -> None:
    """Hostile SQL-injection strings in log fields must be safely parameterized and stored."""
    sqli_ua = "Mozilla/5.0'; DROP TABLE events; SELECT * FROM '1'='1"
    sqli_path = "/rest/products?search=' UNION SELECT id, password, email FROM users WHERE '1'='1"

    payload = {
        "events": [
            {
                "ts": "2026-11-10T02:00:00Z",
                "ip": "203.0.113.195",
                "method": "GET",
                "path": sqli_path,
                "status": 500,
                "ua": sqli_ua,
                "flags": ["sqli"],
                "token_fps": ["f" * 64],
            }
        ]
    }

    response = client.post(
        "/v1/events/batch",
        json=payload,
        headers=valid_api_headers,
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "stored": 1}

    # Verify directly from database session that the table was NOT dropped
    # and the literal attack string is stored unmodified
    stored_event = db_session.query(Event).filter(Event.ip == "203.0.113.195").first()
    assert stored_event is not None
    assert stored_event.ua == sqli_ua
    assert stored_event.path == sqli_path
    assert stored_event.flags == ["sqli"]
    assert stored_event.token_fps == ["f" * 64]


def test_user_agent_truncated_to_max_200(
    client: TestClient, valid_api_headers: dict, db_session: Session
) -> None:
    """Overly long User-Agent strings (e.g., 500 chars) must be truncated to max 200 chars."""
    huge_ua = "A" * 500
    payload = {
        "events": [
            {
                "ts": "2026-11-10T02:00:00Z",
                "ip": "198.51.100.99",
                "method": "POST",
                "path": "/login",
                "status": 401,
                "ua": huge_ua,
                "flags": ["bruteforce"],
            }
        ]
    }

    response = client.post("/v1/events/batch", json=payload, headers=valid_api_headers)
    assert response.status_code == 200

    stored = db_session.query(Event).filter(Event.ip == "198.51.100.99").first()
    assert stored is not None
    assert len(stored.ua) == 200
    assert stored.ua == "A" * 200


def test_invalid_flags_rejected(client: TestClient, valid_api_headers: dict) -> None:
    """Flags outside the allowed enum set must be rejected with HTTP 422."""
    payload = {
        "events": [
            {
                "ts": "2026-11-10T02:00:00Z",
                "ip": "198.51.100.1",
                "method": "GET",
                "path": "/",
                "status": 200,
                "flags": ["invalid_custom_flag"],
            }
        ]
    }
    response = client.post("/v1/events/batch", json=payload, headers=valid_api_headers)
    assert response.status_code == 422
