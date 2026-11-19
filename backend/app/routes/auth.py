"""Authentication endpoints for admin operator dashboard."""

from fastapi import APIRouter, HTTPException, Response, status

from app.auth import constant_time_compare, create_access_token
from app.config import settings
from app.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(request: LoginRequest, response: Response) -> LoginResponse:
    """Authenticate admin operator and issue short-lived JWT in HttpOnly cookie."""
    if not constant_time_compare(request.password, settings.ADMIN_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate 8-hour access token
    token = create_access_token({"sub": "admin", "role": "admin"})

    # Set hardened cookie: HttpOnly, SameSite=Strict
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=28800,
        httponly=True,
        samesite="strict",
        secure=not settings.DEBUG,  # True in production; False only when DEBUG=true for local dev
        path="/",
    )

    return LoginResponse(status="authenticated", expires_in=28800)
