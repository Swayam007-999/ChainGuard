"""Tests for dependency scanning and OSV.dev vulnerability lookup."""

import json
from unittest.mock import MagicMock, patch

from app.models import Dependency, Vuln
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

SAMPLE_PACKAGE_JSON = json.dumps(
    {
        "name": "sample-app",
        "version": "1.0.0",
        "dependencies": {
            "lodash": "^4.17.15",
            "express": "4.17.1",
        },
        "devDependencies": {
            "jest": "^29.0.0",
        },
    }
).encode("utf-8")

SAMPLE_PACKAGE_LOCK_JSON = json.dumps(
    {
        "name": "sample-app",
        "lockfileVersion": 3,
        "packages": {
            "": {"name": "sample-app", "version": "1.0.0"},
            "node_modules/lodash": {"version": "4.17.15"},
            "node_modules/express": {"version": "4.17.1"},
        },
    }
).encode("utf-8")

SAMPLE_REQUIREMENTS_TXT = b"""
# Core dependencies
fastapi==0.115.8
log4j-core==2.14.1
requests>=2.25.0; python_version > '3.7'
"""


def test_unsupported_file_rejected(client: TestClient, valid_api_headers: dict) -> None:
    """Non-manifest files (e.g., .exe, .sh) must be rejected with HTTP 400."""
    files = {"file": ("malicious.exe", b"binarycontent", "application/octet-stream")}
    response = client.post("/v1/dependencies/scan", files=files, headers=valid_api_headers)
    assert response.status_code == 400
    assert "Unsupported manifest file" in response.json()["detail"]


def test_oversized_manifest_rejected(client: TestClient, valid_api_headers: dict) -> None:
    """Files exceeding 5MB size limit must be rejected with HTTP 400."""
    huge_content = b"a" * (6 * 1024 * 1024)  # 6 MB
    files = {"file": ("package.json", huge_content, "application/json")}
    response = client.post("/v1/dependencies/scan", files=files, headers=valid_api_headers)
    assert response.status_code == 400
    assert "exceeds 5MB" in response.json()["detail"]


@patch("app.services.osv_client.OSVClient._get_vuln_detail")
@patch("app.services.osv_client.OSVClient._post_querybatch")
def test_scan_package_json_success(
    mock_post_batch: MagicMock,
    mock_get_detail: MagicMock,
    client: TestClient,
    valid_api_headers: dict,
    db_session: Session,
) -> None:
    """Scanning a valid package.json queries OSV, stores vulns, and derives exploit keywords."""
    mock_post_batch.return_value = {
        "results": [
            {
                "vulns": [
                    {
                        "id": "GHSA-jf85-cpcp-j695",
                        "summary": "Prototype pollution in lodash causing command injection and path traversal",
                        "database_specific": {"severity": "HIGH"},
                        "affected": [{"ranges": [{"events": [{"fixed": "4.17.21"}]}]}],
                    }
                ]
            },
            {"vulns": []},  # express
            {"vulns": []},  # jest
        ]
    }
    mock_get_detail.return_value = {
        "id": "GHSA-jf85-cpcp-j695",
        "summary": "Prototype pollution in lodash causing command injection and path traversal",
        "details": "Directory traversal and arbitrary code execution possible via deep object merge.",
        "aliases": ["CVE-2020-8203"],
        "database_specific": {"severity": "HIGH"},
        "affected": [{"ranges": [{"events": [{"fixed": "4.17.21"}]}]}],
    }

    files = {"file": ("package.json", SAMPLE_PACKAGE_JSON, "application/json")}
    response = client.post(
        "/v1/dependencies/scan",
        files=files,
        data={"app_name": "acme-frontend"},
        headers=valid_api_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["app"] == "acme-frontend"
    assert data["ecosystem"] == "npm"
    assert data["dependencies_tracked"] == 3
    assert data["vulnerabilities_detected"] >= 1
    assert data["cached"] is False

    # Check GET /v1/dependencies
    get_resp = client.get("/v1/dependencies?app=acme-frontend", headers=valid_api_headers)
    assert get_resp.status_code == 200
    dep_list = get_resp.json()
    assert len(dep_list) == 3

    lodash_entry = next((d for d in dep_list if d["name"] == "lodash"), None)
    assert lodash_entry is not None
    assert len(lodash_entry["vulns"]) == 1
    vuln = lodash_entry["vulns"][0]
    assert vuln["osv_id"] == "GHSA-jf85-cpcp-j695"
    assert vuln["severity"] == "HIGH"
    assert vuln["fixed_in"] == "4.17.21"
    # Derived exploit keywords must include traversal and rce
    assert "traversal" in vuln["exploit_keywords"]
    assert "rce" in vuln["exploit_keywords"]


@patch("app.services.osv_client.OSVClient._get_vuln_detail")
@patch("app.services.osv_client.OSVClient._post_querybatch")
def test_scan_requirements_txt_with_log4j(
    mock_post_batch: MagicMock,
    mock_get_detail: MagicMock,
    client: TestClient,
    valid_api_headers: dict,
) -> None:
    """Scanning requirements.txt with a log4j vuln derives the 'jndi' exploit keyword."""
    mock_post_batch.return_value = {
        "results": [
            {"vulns": []},  # fastapi
            {
                "vulns": [
                    {
                        "id": "GHSA-j2ge-4vd3-q558",
                        "summary": "Log4j JNDI remote code execution vulnerability",
                        "database_specific": {"severity": "CRITICAL"},
                        "affected": [{"ranges": [{"events": [{"fixed": "2.17.0"}]}]}],
                    }
                ]
            },
            {"vulns": []},  # requests
        ]
    }
    mock_get_detail.return_value = {
        "id": "GHSA-j2ge-4vd3-q558",
        "summary": "Log4j JNDI remote code execution vulnerability",
        "details": "JNDI lookup allows LDAP deserialization and code execution.",
        "aliases": ["CVE-2021-44228"],
        "database_specific": {"severity": "CRITICAL"},
        "affected": [{"ranges": [{"events": [{"fixed": "2.17.0"}]}]}],
    }

    files = {"file": ("requirements.txt", SAMPLE_REQUIREMENTS_TXT, "text/plain")}
    response = client.post(
        "/v1/dependencies/scan",
        files=files,
        data={"app_name": "acme-backend"},
        headers=valid_api_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ecosystem"] == "pypi"

    get_resp = client.get("/v1/dependencies?app=acme-backend", headers=valid_api_headers)
    assert get_resp.status_code == 200
    dep_list = get_resp.json()
    log4j_entry = next((d for d in dep_list if "log4j" in d["name"]), None)
    assert log4j_entry is not None
    assert "jndi" in log4j_entry["vulns"][0]["exploit_keywords"]


@patch("app.services.osv_client.OSVClient._post_querybatch")
def test_osv_500_error_fallback_to_cache(
    mock_post_batch: MagicMock,
    client: TestClient,
    valid_api_headers: dict,
    db_session: Session,
) -> None:
    """When OSV returns HTTP 500, scan gracefully falls back to cached results."""
    # Pre-populate dependency and vuln in DB
    dep = Dependency(app="test-app", ecosystem="npm", name="lodash", version="4.17.15")
    db_session.add(dep)
    db_session.commit()
    db_session.refresh(dep)

    vuln = Vuln(
        dependency_id=dep.id,
        osv_id="CACHED-VULN-001",
        summary="Cached Vulnerability",
        severity="MEDIUM",
        fixed_in="4.17.21",
        exploit_keywords=["traversal"],
    )
    db_session.add(vuln)
    db_session.commit()

    # Simulate OSV unreachable by returning None from _post_querybatch
    mock_post_batch.return_value = None

    files = {"file": ("package.json", SAMPLE_PACKAGE_JSON, "application/json")}
    response = client.post(
        "/v1/dependencies/scan",
        files=files,
        data={"app_name": "test-app"},
        headers=valid_api_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cached"] is True
    assert "warning" in data
    assert "unreachable" in data["warning"].lower()
    assert data["vulnerabilities_detected"] >= 1


@patch("app.services.osv_client.OSVClient._post_querybatch")
def test_osv_malformed_json_fallback(
    mock_post_batch: MagicMock,
    client: TestClient,
    valid_api_headers: dict,
) -> None:
    """When OSV returns malformed non-JSON data, system does not crash and handles safely."""
    # In OSVClient, a malformed JSON error causes _post_querybatch to catch ValueError and return None
    mock_post_batch.return_value = None

    files = {"file": ("package.json", SAMPLE_PACKAGE_JSON, "application/json")}
    response = client.post(
        "/v1/dependencies/scan",
        files=files,
        headers=valid_api_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cached"] is True
