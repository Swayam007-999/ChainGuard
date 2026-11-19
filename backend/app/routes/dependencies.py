"""Dependency inventory and vulnerability scanning endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import require_admin_or_api_key
from app.database import get_db
from app.models import Dependency
from app.parsers.manifest_parser import parse_manifest_file
from app.services.osv_client import OSVClient

router = APIRouter(prefix="/dependencies", tags=["Dependencies"])
osv_client = OSVClient()


class VulnResponse(BaseModel):
    id: int
    osv_id: str
    summary: str
    severity: str
    fixed_in: str | None
    exploit_keywords: list[str]


class DependencyResponse(BaseModel):
    id: int
    app: str
    ecosystem: str
    name: str
    version: str
    vulns: list[VulnResponse] = []


class ScanSummaryResponse(BaseModel):
    status: str
    app: str
    ecosystem: str
    dependencies_tracked: int
    vulnerabilities_detected: int
    cached: bool
    warning: str | None = None


@router.post(
    "/scan",
    response_model=ScanSummaryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_api_key)],
)
async def scan_dependencies_manifest(
    file: Annotated[
        UploadFile,
        File(description="Manifest file (package.json, package-lock.json, requirements.txt)"),
    ],
    app_name: Annotated[
        str,
        Form(description="Application or service identifier"),
    ] = "web-app",
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> ScanSummaryResponse:
    """Upload and scan project dependency manifest against OSV.dev advisories.

    Extracts runtime packages, matches vulnerabilities, and derives exploit keywords.
    """
    content_bytes = await file.read()
    ecosystem, parsed_deps = parse_manifest_file(file.filename or "unknown", content_bytes)

    dep_records: list[Dependency] = []

    for item in parsed_deps:
        name = item["name"]
        version = item["version"]

        # Upsert dependency record
        existing = (
            db.query(Dependency)
            .filter(
                Dependency.app == app_name,
                Dependency.ecosystem == ecosystem,
                Dependency.name == name,
                Dependency.version == version,
            )
            .first()
        )
        if not existing:
            new_dep = Dependency(
                app=app_name,
                ecosystem=ecosystem,
                name=name,
                version=version,
            )
            db.add(new_dep)
            db.flush()
            dep_records.append(new_dep)
        else:
            dep_records.append(existing)

    db.commit()

    # Query OSV.dev for advisories and cache
    scan_result = osv_client.scan_dependencies(dep_records, db)

    return ScanSummaryResponse(
        status="completed",
        app=app_name,
        ecosystem=ecosystem,
        dependencies_tracked=len(dep_records),
        vulnerabilities_detected=scan_result.get("vulns_found", 0),
        cached=scan_result.get("cached", False),
        warning=scan_result.get("warning"),
    )


@router.get(
    "",
    response_model=list[DependencyResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_api_key)],
)
def list_dependencies(
    app: str | None = None,
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> list[dict[str, Any]]:
    """List all tracked third-party dependencies and their known security advisories."""
    query = db.query(Dependency)
    if app:
        query = query.filter(Dependency.app == app)

    deps = query.order_by(Dependency.name.asc()).all()

    results = []
    for d in deps:
        vuln_list = [
            {
                "id": v.id,
                "osv_id": v.osv_id,
                "summary": v.summary,
                "severity": v.severity,
                "fixed_in": v.fixed_in,
                "exploit_keywords": v.exploit_keywords or [],
            }
            for v in d.vulns
        ]
        results.append(
            {
                "id": d.id,
                "app": d.app,
                "ecosystem": d.ecosystem,
                "name": d.name,
                "version": d.version,
                "vulns": vuln_list,
            }
        )

    return results
