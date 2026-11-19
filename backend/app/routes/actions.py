"""Containment actions approval and reversal endpoints."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import require_admin_or_api_key
from app.containment.adapters import get_containment_adapter
from app.database import get_db
from app.models import Action

router = APIRouter(prefix="/actions", tags=["Containment Actions"])
containment_adapter = get_containment_adapter()


class ActionResponse(BaseModel):
    id: int
    incident_id: int
    type: str
    reversible: bool
    status: str
    target: str
    expires_at: datetime | None = None


@router.post(
    "/{action_id}/approve",
    response_model=ActionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_api_key)],
)
def approve_action(
    action_id: int,
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> Action:
    """Approve and apply a pending containment action (Speed 2 human approval)."""
    action = db.query(Action).filter(Action.id == action_id).first()
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found",
        )

    if action.status == "applied":
        return action

    # Enforce action if it is an IP block
    if action.type == "block_ip":
        containment_adapter.apply_block(action.target)

    action.status = "applied"
    db.commit()
    db.refresh(action)
    return action


@router.post(
    "/{action_id}/undo",
    response_model=ActionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_or_api_key)],
)
def undo_action(
    action_id: int,
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
) -> Action:
    """Revert an applied containment action (1-click rollback)."""
    action = db.query(Action).filter(Action.id == action_id).first()
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found",
        )

    if not action.reversible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Action type '{action.type}' is permanent and cannot be automatically undone",
        )

    if action.status == "undone":
        return action

    # Remove network restriction if it is an IP block
    if action.type == "block_ip":
        containment_adapter.remove_block(action.target)

    action.status = "undone"
    db.commit()
    db.refresh(action)
    return action
