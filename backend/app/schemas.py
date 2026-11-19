"""Pydantic V2 schemas for request validation and response serialization."""

import ipaddress
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

HEX_64_REGEX = re.compile(r"^[a-f0-9]{64}$")
ALLOWED_FLAGS = {"sqli", "traversal", "jndi", "bruteforce"}


# -----------------------------------------------------------------------------
# Fingerprints
# -----------------------------------------------------------------------------
class FingerprintCreate(BaseModel):
    fp_hex: str = Field(..., description="64-character lowercase HMAC-SHA256 hex string")
    kind: str = Field(..., min_length=1, max_length=64, description="Secret classification")
    source: str = Field(..., min_length=1, max_length=128, description="Source domain or surface")

    @field_validator("fp_hex")
    @classmethod
    def validate_hex(cls, v: str) -> str:
        v_clean = v.strip()
        if not HEX_64_REGEX.match(v_clean):
            raise ValueError("fp_hex must be exactly 64 lowercase hexadecimal characters")
        return v_clean


class FingerprintResponse(BaseModel):
    id: int
    fp_hex: str
    kind: str
    source: str
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# Events
# -----------------------------------------------------------------------------
class SingleEvent(BaseModel):
    ts: datetime
    ip: str = Field(..., min_length=1, max_length=45)
    method: str = Field(..., min_length=1, max_length=16)
    path: str = Field(..., min_length=1, max_length=2048)
    status: int = Field(..., ge=100, le=599)
    ua: str = Field(default="", description="User-Agent string, truncated to max 200 chars")
    flags: list[str] = Field(default_factory=list)
    token_fps: list[str] = Field(default_factory=list)

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        v_clean = v.strip()
        try:
            ipaddress.ip_address(v_clean)
        except ValueError as exc:
            raise ValueError(f"Invalid IP address format: {v_clean}") from exc
        return v_clean

    @field_validator("ua")
    @classmethod
    def sanitize_ua(cls, v: str) -> str:
        # Rule 5: Hostile log content. Truncate long fields to max 200 chars.
        if v and len(v) > 200:
            return v[:200]
        return v or ""

    @field_validator("flags")
    @classmethod
    def validate_flags(cls, v: list[str]) -> list[str]:
        for flag in v:
            if flag not in ALLOWED_FLAGS:
                raise ValueError(
                    f"Invalid flag '{flag}'. Allowed flags: {sorted(ALLOWED_FLAGS)}"
                )
        return v

    @field_validator("token_fps")
    @classmethod
    def validate_token_fps(cls, v: list[str]) -> list[str]:
        cleaned = []
        for token_hex in v:
            token_clean = token_hex.strip()
            if not HEX_64_REGEX.match(token_clean):
                raise ValueError(
                    f"token_fp '{token_hex}' must be 64 lowercase hexadecimal characters"
                )
            cleaned.append(token_clean)
        return cleaned


class EventBatchCreate(BaseModel):
    events: list[SingleEvent] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Batch of event objects (maximum 500 per batch)",
    )


class EventBatchResponse(BaseModel):
    status: str
    stored: int


# -----------------------------------------------------------------------------
# Allowlist
# -----------------------------------------------------------------------------
class AllowlistCreate(BaseModel):
    cidr: str = Field(..., min_length=3, max_length=64, description="CIDR network block notation")
    note: str = Field(..., min_length=1, max_length=256, description="Descriptive label or reason")

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        v_clean = v.strip()
        try:
            ipaddress.ip_network(v_clean, strict=False)
        except ValueError as exc:
            raise ValueError(f"Invalid CIDR notation: {v_clean}") from exc
        return v_clean


class AllowlistResponse(BaseModel):
    id: int
    cidr: str
    note: str

    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------
class LoginRequest(BaseModel):
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    status: str
    expires_in: int
