"""Security middleware and CIDR allowlist verification helpers."""

import ipaddress
import logging

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.models import AllowlistEntry

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforce strict defensive security headers on all HTTP responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


# Inherent safety guardrails: Loopback and RFC 1918 private subnets
INHERENT_SAFE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 Unique Local Address (ULA)
]


def is_ip_allowlisted(ip_str: str, db: Session | None = None) -> bool:
    """Determine whether an IP address is exempt from containment actions.

    Rule 7: Never block localhost, RFC 1918 private ranges, or operator allowlisted IPs.
    Returns True if the IP must NOT be blocked, False if blockable.
    """
    try:
        ip_obj = ipaddress.ip_address(ip_str.strip())
    except ValueError:
        logger.warning("Attempted allowlist check on malformed IP string: %s", ip_str)
        return False

    # Check loopback and RFC 1918 private networks
    if ip_obj.is_loopback:
        return True
    for safe_net in INHERENT_SAFE_NETWORKS:
        if ip_obj in safe_net:
            return True

    # Database check against operator allowlisted CIDRs
    if db is not None:
        entries = db.query(AllowlistEntry).all()
        for entry in entries:
            try:
                network = ipaddress.ip_network(entry.cidr, strict=False)
                if ip_obj in network:
                    return True
            except ValueError:
                logger.error("Corrupted CIDR in allowlist table: %s", entry.cidr)
                continue

    return False
