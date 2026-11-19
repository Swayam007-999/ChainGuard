"""Stub endpoints for future modules, returning HTTP 501 Not Implemented."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_admin_or_api_key

router = APIRouter(tags=["Stubs"])


@router.get(
    "/incidents",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    dependencies=[Depends(require_admin_or_api_key)],
)
def stub_incidents_list() -> None:
    """Stub for Prompt 5: Incident correlation engine."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Incident correlation module is not yet implemented (Scheduled for Prompt 5)",
    )


@router.get(
    "/incidents/{incident_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    dependencies=[Depends(require_admin_or_api_key)],
)
def stub_incident_detail(incident_id: int) -> None:
    """Stub for Prompt 5: Incident detail retrieval."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Incident detail module is not yet implemented (Scheduled for Prompt 5)",
    )


@router.post(
    "/actions/{action_id}/approve",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    dependencies=[Depends(require_admin_or_api_key)],
)
def stub_action_approve(action_id: int) -> None:
    """Stub for Prompt 5: Two-speed containment action approval."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Containment action approval is not yet implemented (Scheduled for Prompt 5)",
    )


@router.post(
    "/actions/{action_id}/undo",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    dependencies=[Depends(require_admin_or_api_key)],
)
def stub_action_undo(action_id: int) -> None:
    """Stub for Prompt 5: Two-speed containment action reversal."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Containment action undo is not yet implemented (Scheduled for Prompt 5)",
    )
