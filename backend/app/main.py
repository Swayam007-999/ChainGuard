"""Main FastAPI application entrypoint for ChainGuard."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.rate_limiter import RateLimitMiddleware
from app.routes.actions import router as actions_router
from app.routes.allowlist import router as allowlist_router
from app.routes.auth import router as auth_router
from app.routes.dependencies import router as dependencies_router
from app.routes.events import router as events_router
from app.routes.fingerprints import router as fingerprints_router
from app.routes.incidents import router as incidents_router
from app.security import SecurityHeadersMiddleware

logger = logging.getLogger("chainguard")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context: initialize database tables."""
    # Ensure SQLite tables exist on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ChainGuard API",
    description="Defensive security co-pilot REST API for small development teams.",
    version="1.0.0",
    docs_url=None if not settings.DEBUG else "/docs",
    redoc_url=None if not settings.DEBUG else "/redoc",
    openapi_url=None if not settings.DEBUG else "/openapi.json",
    lifespan=lifespan,
)

# Rule 8: CORS allowlist from environment configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-ChainGuard-Key"],
)

# Rule 8: Enforce defensive security headers on all responses
app.add_middleware(SecurityHeadersMiddleware)

# Rule 8: In-memory sliding window rate limiting
app.add_middleware(RateLimitMiddleware)


# Rule 8: No stack traces in responses; generic 500 error handler
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact the administrator."},
    )


# Mount API routers under /v1
app.include_router(auth_router, prefix="/v1")
app.include_router(fingerprints_router, prefix="/v1")
app.include_router(events_router, prefix="/v1")
app.include_router(dependencies_router, prefix="/v1")
app.include_router(allowlist_router, prefix="/v1")
app.include_router(incidents_router, prefix="/v1")
app.include_router(actions_router, prefix="/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Public unauthenticated health probe."""
    return {"status": "ok", "service": "chainguard-backend"}
