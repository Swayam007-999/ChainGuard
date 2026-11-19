"""Log parser for Nginx custom access log format."""

import ipaddress
import logging
import re
from datetime import UTC, datetime
from typing import Any

from agent.detector import AttackDetector

logger = logging.getLogger(__name__)

# Standard Nginx log regex
NGINX_LOG_REGEX = re.compile(
    r'^(?P<ip>\S+)\s+-\s+\[(?P<ts>[^\]]+)\]\s+"(?P<method>[A-Za-z]+)"\s+"(?P<uri>[^"]*)"\s+(?P<status>\d{3})\s+"(?P<ua>.*?)"\s+"(?P<auth>.*?)"\s+"(?P<x_api_key>.*?)"\s*$',
    re.DOTALL,
)


class LogParser:
    """Parses Nginx access logs and generates sanitized event dictionaries."""

    def __init__(self, detector: AttackDetector) -> None:
        self.detector = detector

    def parse_line(self, line: str) -> dict[str, Any] | None:
        """Parse a single raw log line into a sanitized event dict.

        Returns None if the line is unparseable, malformed, or empty.
        Safely truncates hostile long payloads (e.g. 1MB User-Agents or URIs).
        """
        line = line.strip()
        if not line:
            return None

        # Try fast structured quote split first for extreme resilience and memory safety
        parsed = self._parse_by_tokens(line)
        if parsed:
            return parsed

        # Fallback to regex for standard lines
        match = NGINX_LOG_REGEX.match(line)
        if match:
            return self._build_event_from_fields(
                raw_ip=match.group("ip"),
                raw_ts=match.group("ts"),
                raw_method=match.group("method"),
                raw_uri=match.group("uri"),
                raw_status=match.group("status"),
                raw_ua=match.group("ua"),
                raw_auth=match.group("auth"),
                raw_x_api_key=match.group("x_api_key"),
                raw_line=line,
            )

        return None

    def _parse_by_tokens(self, line: str) -> dict[str, Any] | None:
        """Splits line on quote delimiters, robust against 1MB payloads and strange characters."""
        try:
            parts = line.split('"')
            # Expecting at least: prefix "method" "uri" status "ua" "auth" "key"
            if len(parts) >= 7:
                prefix = parts[0].strip()
                if " - [" not in prefix or not prefix.endswith("]"):
                    return None

                ip_part = prefix.split(" - [")[0].strip()
                ts_part = prefix.split(" - [")[1].rstrip("]").strip()
                method = parts[1].strip()
                uri = parts[3].strip()
                status_part = parts[4].strip().split(" ")[0].strip()
                ua = parts[5].strip()
                auth = parts[7].strip() if len(parts) > 7 else "-"
                x_api_key = parts[9].strip() if len(parts) > 9 else "-"

                return self._build_event_from_fields(
                    raw_ip=ip_part,
                    raw_ts=ts_part,
                    raw_method=method,
                    raw_uri=uri,
                    raw_status=status_part,
                    raw_ua=ua,
                    raw_auth=auth,
                    raw_x_api_key=x_api_key,
                    raw_line=line,
                )
        except (ValueError, IndexError, KeyError):
            pass
        return None

    def _build_event_from_fields(
        self,
        raw_ip: str,
        raw_ts: str,
        raw_method: str,
        raw_uri: str,
        raw_status: str,
        raw_ua: str,
        raw_auth: str,
        raw_x_api_key: str,
        raw_line: str,
    ) -> dict[str, Any] | None:
        """Validate fields, sanitize lengths, run attack detector, and build event."""
        # 1. Validate IP address
        try:
            ipaddress.ip_address(raw_ip.strip())
        except ValueError:
            return None

        # 2. Validate and convert status code
        try:
            status_code = int(raw_status)
            if not (100 <= status_code <= 599):
                return None
        except ValueError:
            return None

        # 3. Parse timestamp to ISO-8601 UTC
        try:
            ts_dt = datetime.fromisoformat(raw_ts)
        except ValueError:
            ts_dt = datetime.now(UTC)

        method = raw_method.strip().upper()
        if not (1 <= len(method) <= 16):
            return None

        # Rule 5: Hostile log content. Truncate User-Agent to max 200 chars.
        sanitized_ua = raw_ua[:200] if raw_ua else ""
        sanitized_uri = raw_uri[:2048] if raw_uri else "/"

        # Detect attack heuristic flags
        flags = self.detector.detect_flags(
            ip=raw_ip,
            path=sanitized_uri,
            status=status_code,
            ua=sanitized_ua,
            raw_line=raw_line[:1000],
        )

        # Extract and locally hash token fingerprints
        token_fps = self.detector.extract_token_fingerprints(
            auth_header=raw_auth[:500] if raw_auth else None,
            x_api_key_header=raw_x_api_key[:500] if raw_x_api_key else None,
            uri=sanitized_uri,
        )

        return {
            "ts": ts_dt.isoformat(),
            "ip": raw_ip,
            "method": method,
            "path": sanitized_uri,
            "status": status_code,
            "ua": sanitized_ua,
            "flags": flags,
            "token_fps": token_fps,
        }
