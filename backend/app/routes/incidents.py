"""Incidents API endpoints for retrieving prioritized security briefings."""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import require_admin_or_api_key
from app.database import get_db
from app.models import Incident

router = APIRouter(prefix="/incidents", tags=["Incidents"])


class ActionSummary(BaseModel):
    id: int
    incident_id: int
    type: str
    reversible: bool
    status: str
    target: str
    expires_at: datetime | None = None


class IncidentDetailResponse(BaseModel):
    id: int
    severity: str
    status: str
    title: str
    evidence: dict[str, Any]
    explanation: dict[str, Any]
    created_at: datetime
    actions: list[ActionSummary] = []


SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


@router.get(
    "",
    response_model=list[IncidentDetailResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_api_key)],
)
def list_incidents(
    status_filter: str | None = Query(None, alias="status"),
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> list[Incident]:
    """Retrieve correlated security incidents sorted by exploitability severity and recency."""
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter)

    incidents = query.order_by(Incident.created_at.desc()).all()
    # Sort in-memory by severity rank
    return sorted(incidents, key=lambda inc: SEVERITY_ORDER.get(inc.severity, 99))


@router.get(
    "/{incident_id}",
    response_model=IncidentDetailResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_api_key)],
)
def get_incident_detail(
    incident_id: int,
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> Incident:
    """Retrieve full incident evidence, plain-English explanation, and containment status."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )
    return incident
