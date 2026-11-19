"""Correlation Engine, plain-English incident synthesis, and containment orchestrator."""

import logging
from datetime import UTC, datetime, timedelta

from app.containment.adapters import get_containment_adapter
from app.models import Action, Event, Fingerprint, Incident, Vuln
from app.security import is_ip_allowlisted
from app.services.explanation_service import ExplanationService
from sqlalchemy.orm import Session

logger = logging.getLogger("chainguard-correlator")
explanation_service = ExplanationService()
containment_adapter = get_containment_adapter()


def utcnow() -> datetime:
    return datetime.now(UTC)


class CorrelatorEngine:
    """Evaluates incoming web traffic events against leaked fingerprints and dependency vulns."""

    def __init__(self) -> None:
        pass

    def evaluate_event(self, event: Event, db: Session) -> Incident | None:
        """Correlate event with database state using deterministic rules R1, R2, R3."""
        # Check Rule R1: Confirmed Chain (Leaked secret replay)
        incident_r1 = self._check_rule_r1(event, db)
        if incident_r1:
            return incident_r1

        # Check Rule R2: Exploitable Vulnerability
        incident_r2 = self._check_rule_r2(event, db)
        if incident_r2:
            return incident_r2

        # Check Rule R3: Brute Force Attack
        incident_r3 = self._check_rule_r3(event, db)
        if incident_r3:
            return incident_r3

        return None

    def _check_rule_r1(self, event: Event, db: Session) -> Incident | None:
        """R1: If event token_fps contains a stored fingerprint -> CRITICAL incident."""
        token_fps: list[str] = event.token_fps or []
        if not token_fps:
            return None

        # Search for matched leaked fingerprint
        matched_fp = (
            db.query(Fingerprint).filter(Fingerprint.fp_hex.in_(token_fps)).first()
        )
        if not matched_fp:
            return None

        evidence = {
            "fingerprint_id": matched_fp.id,
            "kind": matched_fp.kind,
            "source": matched_fp.source,
            "paste_time": matched_fp.detected_at.isoformat(),
            "request_time": event.ts.isoformat(),
            "ip": event.ip,
            "path": event.path,
            "method": event.method,
            "matched_token_fp": matched_fp.fp_hex,
        }

        explanation = explanation_service.explain_incident(rule_id="R1", evidence=evidence)

        incident = Incident(
            severity="CRITICAL",
            status="open",
            title=f"Confirmed Chain: Leaked {matched_fp.kind} Used Against {event.path}",
            evidence=evidence,
            explanation=explanation,
            created_at=utcnow(),
        )
        db.add(incident)
        db.flush()

        # Generate disruptive action: Rotate credentials (requires human approval)
        action = Action(
            incident_id=incident.id,
            type="rotate_credentials",
            reversible=False,
            status="pending",
            target=matched_fp.kind,
            expires_at=None,
        )
        db.add(action)
        db.commit()
        db.refresh(incident)

        logger.warning(
            "CRITICAL: Rule R1 triggered for IP %s using leaked %s", event.ip, matched_fp.kind
        )
        return incident

    def _check_rule_r2(self, event: Event, db: Session) -> Incident | None:
        """R2: Exploit keyword matching installed dependency raises severity; unmatched lowers."""
        flags: list[str] = event.flags or []
        exploit_flags = [f for f in flags if f in ("sqli", "traversal", "jndi")]
        if not exploit_flags:
            return None

        # Query all vulnerabilities in DB
        vulns = db.query(Vuln).all()
        matched_vuln: Vuln | None = None

        for v in vulns:
            kw_list = v.exploit_keywords or []
            if any(f in kw_list for f in exploit_flags):
                matched_vuln = v
                break

        if matched_vuln:
            # Rule R2: Match with installed dependency -> Raise severity to CRITICAL
            dep = matched_vuln.dependency
            evidence = {
                "dependency_id": dep.id,
                "dependency": dep.name,
                "version": dep.version,
                "vuln_id": matched_vuln.osv_id,
                "flags": exploit_flags,
                "ip": event.ip,
                "path": event.path,
                "is_installed": True,
            }
            explanation = explanation_service.explain_incident(rule_id="R2", evidence=evidence)
            incident = Incident(
                severity="CRITICAL",
                status="open",
                title=f"Exploitable Flaw Target: {dep.name} ({matched_vuln.osv_id})",
                evidence=evidence,
                explanation=explanation,
                created_at=utcnow(),
            )
        else:
            # Rule R2: Exploit flag present, but NO installed package has that keyword -> Lower severity to LOW
            evidence = {
                "flags": exploit_flags,
                "ip": event.ip,
                "path": event.path,
                "is_installed": False,
            }
            explanation = explanation_service.explain_incident(rule_id="R2", evidence=evidence)
            incident = Incident(
                severity="LOW",
                status="open",
                title=f"Scanner Probe (Not Vulnerable): {', '.join(exploit_flags)}",
                evidence=evidence,
                explanation=explanation,
                created_at=utcnow(),
            )

        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    def _check_rule_r3(self, event: Event, db: Session) -> Incident | None:
        """R3: Bruteforce flag -> HIGH incident + reversible block_ip with 15-min TTL."""
        flags: list[str] = event.flags or []
        if "bruteforce" not in flags:
            return None

        evidence = {
            "ip": event.ip,
            "path": event.path,
            "status": event.status,
            "count": 8,
        }
        explanation = explanation_service.explain_incident(rule_id="R3", evidence=evidence)

        incident = Incident(
            severity="HIGH",
            status="open",
            title=f"Brute Force Authentication Probe from {event.ip}",
            evidence=evidence,
            explanation=explanation,
            created_at=utcnow(),
        )
        db.add(incident)
        db.flush()

        # Check allowlist safety guardrails
        ip_protected = is_ip_allowlisted(event.ip, db)

        if ip_protected:
            # Rule 7: Never auto-block localhost, RFC 1918 private subnets, or allowlisted CIDRs
            action = Action(
                incident_id=incident.id,
                type="block_ip",
                reversible=True,
                status="pending",  # Pending human review due to allowlist protection
                target=event.ip,
                expires_at=None,
            )
            logger.info("IP %s is protected by allowlist/private range. Auto-block skipped.", event.ip)
        else:
            # Auto-applied reversible action with 15-min TTL
            expires = utcnow() + timedelta(minutes=15)
            action = Action(
                incident_id=incident.id,
                type="block_ip",
                reversible=True,
                status="applied",
                target=event.ip,
                expires_at=expires,
            )
            # Enforce block via active containment adapter
            containment_adapter.apply_block(event.ip)
            incident.status = "contained"

        db.add(action)
        db.commit()
        db.refresh(incident)
        return incident

    def sweep_expired_actions(self, db: Session) -> int:
        """Find and expire active rate limits that have reached their TTL."""
        now = utcnow()
        expired_actions = (
            db.query(Action)
            .filter(
                Action.status == "applied",
                Action.reversible.is_(True),
                Action.expires_at.is_not(None),
                Action.expires_at <= now,
            )
            .all()
        )

        count = 0
        for act in expired_actions:
            act.status = "expired"
            if act.type == "block_ip":
                containment_adapter.remove_block(act.target)
            count += 1

        if count > 0:
            db.commit()
            logger.info("Swept and expired %d containment actions", count)

        return count


correlator_engine = CorrelatorEngine()
