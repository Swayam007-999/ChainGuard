"""Allowlist management endpoints for CIDR network blocks."""


from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import require_admin, require_admin_or_api_key
from app.database import get_db
from app.models import AllowlistEntry
from app.schemas import AllowlistCreate, AllowlistResponse

router = APIRouter(prefix="/allowlist", tags=["Allowlist"])


@router.get(
    "",
    response_model=list[AllowlistResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_api_key)],
)
def list_allowlist(
    db: Annotated[Session, Depends(get_db)],
) -> list[AllowlistResponse]:
    """Retrieve all configured CIDR network blocks exempt from containment actions."""
    entries = db.query(AllowlistEntry).order_by(AllowlistEntry.id.asc()).all()
    return entries  # type: ignore[return-value]


@router.post(
    "",
    response_model=AllowlistResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def add_allowlist_entry(
    payload: AllowlistCreate,
    db: Annotated[Session, Depends(get_db)],
) -> AllowlistResponse:
    """Add a network CIDR to the containment allowlist (operator action)."""
    existing = db.query(AllowlistEntry).filter(AllowlistEntry.cidr == payload.cidr).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"CIDR block '{payload.cidr}' is already allowlisted",
        )

    entry = AllowlistEntry(
        cidr=payload.cidr,
        note=payload.note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry  # type: ignore[return-value]
