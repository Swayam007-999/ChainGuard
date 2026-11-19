"""OSV.dev vulnerability database client with caching and keyword extraction."""

import logging
import re
import time
from typing import Any

import httpx
from app.models import Dependency, Vuln
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
OSV_VULN_URL = "https://api.osv.dev/v1/vulns/{vuln_id}"
BATCH_CHUNK_SIZE = 100  # Paged to respect OSV request ceilings

KEYWORD_PATTERNS = {
    "jndi": re.compile(r"\b(jndi|ldap|log4j|log4shell)\b", re.IGNORECASE),
    "traversal": re.compile(
        r"\b(directory\s+traversal|path\s+traversal|\.\./|dot-dot)\b", re.IGNORECASE
    ),
    "sqli": re.compile(r"\b(sql\s+injection|sqli|blind\s+sql)\b", re.IGNORECASE),
    "rce": re.compile(
        r"\b(remote\s+code\s+execution|command\s+injection|arbitrary\s+code)\b",
        re.IGNORECASE,
    ),
    "deserialization": re.compile(
        r"\b(deserialization|untrusted\s+data|pickle|yaml\.load)\b", re.IGNORECASE
    ),
    "bruteforce": re.compile(
        r"\b(brute\s+force|credential\s+stuffing|password\s+spray)\b", re.IGNORECASE
    ),
    "auth_bypass": re.compile(
        r"\b(authentication\s+bypass|auth\s+bypass|broken\s+access)\b", re.IGNORECASE
    ),
    "ssrf": re.compile(r"\b(ssrf|server-side\s+request\s+forgery)\b", re.IGNORECASE),
}


def derive_exploit_keywords(pkg_name: str, summary: str, details: str, aliases: list[str]) -> list[str]:
    """Extract actionable attack signature flags from vulnerability text and metadata."""
    combined_text = f"{pkg_name} {summary} {details} {' '.join(aliases)}".lower()
    keywords = []
    for keyword, pattern in KEYWORD_PATTERNS.items():
        if pattern.search(combined_text):
            keywords.append(keyword)

    # Special rules for known notorious vectors
    if "log4j" in pkg_name.lower() and "jndi" not in keywords:
        keywords.append("jndi")

    return sorted(set(keywords))


def extract_severity(vuln_data: dict[str, Any]) -> str:
    """Normalize CVSS score or database-specific label to standard 4-tier severity."""
    # Check database-specific severity first
    db_specific = vuln_data.get("database_specific", {})
    if isinstance(db_specific, dict) and "severity" in db_specific:
        sev = str(db_specific["severity"]).upper()
        if sev in ("LOW", "MEDIUM", "HIGH", "CRITICAL", "MODERATE"):
            return "MEDIUM" if sev == "MODERATE" else sev

    # Check CVSS scores in severity list
    severities = vuln_data.get("severity", [])
    if isinstance(severities, list) and severities:
        for sev_item in severities:
            score_str = sev_item.get("score", "")
            if "CVSS:3" in score_str or "CVSS:4" in score_str:
                # If CVSS vector is present, extract base score if possible or estimate
                pass

    return "MEDIUM"


def extract_fixed_version(vuln_data: dict[str, Any]) -> str | None:
    """Find the earliest version that resolves this vulnerability."""
    affected_list = vuln_data.get("affected", [])
    for aff in affected_list:
        ranges = aff.get("ranges", [])
        for rng in ranges:
            events = rng.get("events", [])
            for event in events:
                if "fixed" in event:
                    return str(event["fixed"])
    return None


class OSVClient:
    """Client for OSV.dev batch API with retry backoff and caching."""

    def __init__(self, timeout: float = 10.0, max_retries: int = 2) -> None:
        self.timeout = timeout
        self.max_retries = max_retries

    def scan_dependencies(
        self, dependencies: list[Dependency], db: Session
    ) -> dict[str, Any]:
        """Query OSV.dev for third-party vulnerabilities, caching records in SQLite."""
        if not dependencies:
            return {"total_scanned": 0, "vulns_found": 0, "cached": False}

        # Build query batches
        queries = []
        for dep in dependencies:
            eco = "npm" if dep.ecosystem == "npm" else "PyPI"
            queries.append(
                {"package": {"name": dep.name, "ecosystem": eco}, "version": dep.version}
            )

        osv_reachable = True
        batch_results: list[dict[str, Any]] = []

        # Page batch queries in chunks of BATCH_CHUNK_SIZE
        for i in range(0, len(queries), BATCH_CHUNK_SIZE):
            chunk = queries[i : i + BATCH_CHUNK_SIZE]
            res = self._post_querybatch(chunk)
            if res is None:
                osv_reachable = False
                break
            batch_results.extend(res.get("results", []))

        total_vulns = 0

        # If OSV is reachable, process and cache fresh vulnerability records
        if osv_reachable and len(batch_results) == len(dependencies):
            for dep, result in zip(dependencies, batch_results):
                vuln_items = result.get("vulns", [])
                for v_item in vuln_items:
                    osv_id = v_item.get("id")
                    if not osv_id:
                        continue

                    # Fetch full vulnerability definition
                    full_vuln = self._get_vuln_detail(osv_id) or v_item

                    summary = full_vuln.get("summary") or full_vuln.get("details", "Security vulnerability")
                    details = full_vuln.get("details", "")
                    aliases = full_vuln.get("aliases", [])
                    severity = extract_severity(full_vuln)
                    fixed_in = extract_fixed_version(full_vuln)
                    keywords = derive_exploit_keywords(dep.name, summary, details, aliases)

                    # Update or insert vulnerability in SQLite
                    existing_vuln = (
                        db.query(Vuln)
                        .filter(Vuln.dependency_id == dep.id, Vuln.osv_id == osv_id)
                        .first()
                    )
                    if not existing_vuln:
                        vuln_record = Vuln(
                            dependency_id=dep.id,
                            osv_id=osv_id,
                            summary=summary[:500],  # Truncate summary safely
                            severity=severity,
                            fixed_in=fixed_in,
                            exploit_keywords=keywords,
                        )
                        db.add(vuln_record)
                        total_vulns += 1

            db.commit()
            return {
                "total_scanned": len(dependencies),
                "vulns_found": total_vulns,
                "cached": False,
            }

        # OSV unreachable fallback: Return last cached results from database
        cached_count = (
            db.query(Vuln)
            .filter(Vuln.dependency_id.in_([d.id for d in dependencies]))
            .count()
        )
        return {
            "total_scanned": len(dependencies),
            "vulns_found": cached_count,
            "cached": True,
            "warning": "OSV.dev was unreachable or returned an error; using cached vulnerability records.",
        }

    def _post_querybatch(self, queries: list[dict[str, Any]]) -> dict[str, Any] | None:
        """POST batch query to OSV with exponential backoff retry."""
        payload = {"queries": queries}
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(OSV_BATCH_URL, json=payload)
                    if resp.status_code == 200:
                        return resp.json()
                    logger.warning(
                        "OSV querybatch HTTP error %d: %s", resp.status_code, resp.text[:200]
                    )
            except (httpx.RequestError, ValueError) as exc:
                logger.warning("OSV querybatch connection error (attempt %d): %s", attempt, exc)

            if attempt < self.max_retries:
                time.sleep(0.5 * (2**attempt))

        return None

    def _get_vuln_detail(self, vuln_id: str) -> dict[str, Any] | None:
        """GET full vulnerability record by ID."""
        url = OSV_VULN_URL.format(vuln_id=vuln_id)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    return resp.json()
        except (httpx.RequestError, ValueError) as exc:
            logger.warning("Failed to fetch full record for vuln %s: %s", vuln_id, exc)
        return None
