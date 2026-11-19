"""Tests for /v1/fingerprints endpoint: hex validation and storage."""

from app.models import Fingerprint
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_valid_fingerprint(
    client: TestClient, valid_api_headers: dict, db_session: Session
) -> None:
    """Valid HMAC-SHA256 hex string registers successfully with HTTP 201."""
    fp_hex = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    payload = {
        "fp_hex": fp_hex,
        "kind": "stripe_live_key",
        "source": "chatgpt.com",
    }

    response = client.post("/v1/fingerprints", json=payload, headers=valid_api_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["fp_hex"] == fp_hex
    assert data["kind"] == "stripe_live_key"
    assert data["source"] == "chatgpt.com"
    assert "id" in data
    assert "detected_at" in data

    # Verify directly from SQLite
    record = db_session.query(Fingerprint).filter(Fingerprint.fp_hex == fp_hex).first()
    assert record is not None
    assert record.kind == "stripe_live_key"
    assert record.source == "chatgpt.com"


def test_invalid_fingerprint_hex_rejected(
    client: TestClient, valid_api_headers: dict
) -> None:
    """Fingerprints that are not 64-character lowercase hex strings must be rejected."""
    invalid_fps = [
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85",  # 63 chars
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555",  # 65 chars
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",  # Uppercase
        "g" * 64,  # Non-hex character 'g'
        "",  # Empty
    ]

    for bad_fp in invalid_fps:
        payload = {
            "fp_hex": bad_fp,
            "kind": "generic_token",
            "source": "claude.ai",
        }
        response = client.post("/v1/fingerprints", json=payload, headers=valid_api_headers)
        assert response.status_code == 422, f"Failed to reject invalid hex: {bad_fp}"
