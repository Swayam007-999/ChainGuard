"""SQLAlchemy models for ChainGuard database schema."""

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow() -> datetime:
    """Helper to return UTC datetime with timezone awareness."""
    return datetime.now(UTC)


class Fingerprint(Base):
    __tablename__ = "fingerprints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fp_hex = Column(String(64), nullable=False, index=True)
    kind = Column(String(64), nullable=False)
    source = Column(String(128), nullable=False)
    detected_at = Column(DateTime, default=utcnow, nullable=False)


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app = Column(String(128), nullable=False)
    ecosystem = Column(String(32), nullable=False)  # npm, pypi
    name = Column(String(256), nullable=False)
    version = Column(String(64), nullable=False)

    vulns = relationship("Vuln", back_populates="dependency", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("app", "ecosystem", "name", "version", name="uq_dependency_version"),
    )


class Vuln(Base):
    __tablename__ = "vulns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dependency_id = Column(
        Integer, ForeignKey("dependencies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    osv_id = Column(String(64), nullable=False)
    summary = Column(Text, nullable=False)
    severity = Column(String(32), nullable=False)
    fixed_in = Column(String(64), nullable=True)
    exploit_keywords = Column(JSON, nullable=False, default=list)

    dependency = relationship("Dependency", back_populates="vulns")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False, index=True)
    ip = Column(String(45), nullable=False, index=True)  # Supports IPv4 and IPv6 strings
    method = Column(String(16), nullable=False)
    path = Column(Text, nullable=False)
    status = Column(Integer, nullable=False)
    ua = Column(String(200), nullable=False)
    flags = Column(JSON, nullable=False, default=list)
    token_fps = Column(JSON, nullable=False, default=list)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    severity = Column(String(32), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(32), nullable=False, default="open")  # open, contained, resolved, dismissed
    title = Column(String(256), nullable=False)
    evidence = Column(JSON, nullable=False, default=dict)
    explanation = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    actions = relationship("Action", back_populates="incident", cascade="all, delete-orphan")


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type = Column(String(64), nullable=False)  # rate_limit_ip, revoke_token, isolate_service
    reversible = Column(Boolean, nullable=False, default=True)
    status = Column(String(32), nullable=False, default="pending", index=True)
    target = Column(String(256), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="actions")


class AllowlistEntry(Base):
    __tablename__ = "allowlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cidr = Column(String(64), nullable=False, unique=True, index=True)
    note = Column(String(256), nullable=False)
