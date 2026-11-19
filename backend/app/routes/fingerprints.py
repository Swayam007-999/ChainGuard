"""Fingerprint registration endpoints for browser extension."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Fingerprint
from app.schemas import FingerprintCreate, FingerprintResponse

router = APIRouter(prefix="/fingerprints", tags=["Fingerprints"])


@router.post(
    "",
    response_model=FingerprintResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_fingerprint(
    payload: FingerprintCreate,
    db: Annotated[Session, Depends(get_db)],
) -> FingerprintResponse:
    """Register an on-device HMAC fingerprint of a detected leaked secret.

    Raw secret strings are NEVER received or stored.
    """
    record = Fingerprint(
        fp_hex=payload.fp_hex,
        kind=payload.kind,
        source=payload.source,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record  # type: ignore[return-value]
