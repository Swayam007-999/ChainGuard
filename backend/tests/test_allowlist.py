"""Tests for allowlist CIDR helper function and /v1/allowlist endpoints."""

from app.models import AllowlistEntry
from app.security import is_ip_allowlisted
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_allowlist_helper_inherent_protections(db_session: Session) -> None:
    """Rule 7: Containment safety. Never block localhost or RFC 1918 private subnets."""
    # Loopback addresses
    assert is_ip_allowlisted("127.0.0.1", db_session) is True
    assert is_ip_allowlisted("::1", db_session) is True

    # RFC 1918 private ranges
    assert is_ip_allowlisted("10.0.4.15", db_session) is True
    assert is_ip_allowlisted("172.16.5.99", db_session) is True
    assert is_ip_allowlisted("192.168.1.100", db_session) is True

    # Public un-allowlisted IP should return False
    assert is_ip_allowlisted("203.0.113.45", db_session) is False


def test_allowlist_helper_database_cidr(db_session: Session) -> None:
    """Custom operator CIDR in database properly allowlists matching IPs."""
    # Insert custom CIDR into database
    entry = AllowlistEntry(cidr="203.0.113.0/24", note="Payment Gateway Webhooks")
    db_session.add(entry)
    db_session.commit()

    # IPs within the 203.0.113.0/24 network should now be allowlisted
    assert is_ip_allowlisted("203.0.113.1", db_session) is True
    assert is_ip_allowlisted("203.0.113.254", db_session) is True

    # IP outside the network remains blockable
    assert is_ip_allowlisted("203.0.114.1", db_session) is False


def test_add_allowlist_entry_success(client: TestClient, admin_cookie: dict) -> None:
    """Admin operator can add a valid CIDR network to allowlist."""
    payload = {"cidr": "198.51.100.0/24", "note": "Office VPN Static IP Range"}
    response = client.post("/v1/allowlist", json=payload, cookies=admin_cookie)
    assert response.status_code == 201
    data = response.json()
    assert data["cidr"] == "198.51.100.0/24"
    assert data["note"] == "Office VPN Static IP Range"
    assert "id" in data


def test_add_allowlist_entry_invalid_cidr(client: TestClient, admin_cookie: dict) -> None:
    """Invalid CIDR notation must be rejected with HTTP 422."""
    payload = {"cidr": "not_a_valid_cidr_notation", "note": "Test Note"}
    response = client.post("/v1/allowlist", json=payload, cookies=admin_cookie)
    assert response.status_code == 422


def test_add_allowlist_entry_duplicate_rejected(client: TestClient, admin_cookie: dict) -> None:
    """Adding an existing CIDR must return HTTP 409 Conflict."""
    payload = {"cidr": "198.51.100.0/24", "note": "First Entry"}
    r1 = client.post("/v1/allowlist", json=payload, cookies=admin_cookie)
    assert r1.status_code == 201

    # Duplicate attempt
    r2 = client.post("/v1/allowlist", json=payload, cookies=admin_cookie)
    assert r2.status_code == 409


def test_get_allowlist(client: TestClient, valid_api_headers: dict, admin_cookie: dict) -> None:
    """Allowlist entries can be retrieved with valid credentials."""
    client.post(
        "/v1/allowlist",
        json={"cidr": "198.51.100.0/24", "note": "VPN"},
        cookies=admin_cookie,
    )

    response = client.get("/v1/allowlist", headers=valid_api_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["cidr"] == "198.51.100.0/24"
