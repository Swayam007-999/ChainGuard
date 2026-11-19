"""Web traffic event ingestion endpoints for the Python Log Agent."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.correlator.engine import correlator_engine
from app.database import get_db
from app.models import Event
from app.schemas import EventBatchCreate, EventBatchResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/batch",
    response_model=EventBatchResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_api_key)],
)
def ingest_event_batch(
    payload: EventBatchCreate,
    db: Annotated[Session, Depends(get_db)],
) -> EventBatchResponse:
    """Ingest a batch of normalized, sanitized log events from the Log Agent.

    Enforces batch limits (max 500), input validation, parameterized ORM persistence,
    and triggers the real-time correlation engine for incident synthesis.
    """
    records = [
        Event(
            ts=e.ts,
            ip=e.ip,
            method=e.method,
            path=e.path,
            status=e.status,
            ua=e.ua,
            flags=e.flags,
            token_fps=e.token_fps,
        )
        for e in payload.events
    ]

    db.add_all(records)
    db.commit()

    # Real-time correlation evaluation and expiry sweeping
    for rec in records:
        correlator_engine.evaluate_event(rec, db)
    correlator_engine.sweep_expired_actions(db)

    return EventBatchResponse(status="success", stored=len(records))
