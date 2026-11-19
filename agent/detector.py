"""Attack signature detection and on-agent token fingerprinting."""

import hashlib
import hmac
import re
import threading
import time
import urllib.parse
from collections import defaultdict

# Pre-compiled regex patterns for attack heuristics
SQLI_PATTERNS = [
    re.compile(r"('\s*or\s*'?1'?\s*=\s*'?1)", re.IGNORECASE),
    re.compile(r"('\s*or\s*'[a-z0-9]'\s*=\s*'[a-z0-9]')", re.IGNORECASE),
    re.compile(r"(union\s+(?:all\s+)?select)", re.IGNORECASE),
    re.compile(r"(information_schema\.)", re.IGNORECASE),
    re.compile(r"(--|/\*|\*/|;\s*drop\s+table)", re.IGNORECASE),
]

TRAVERSAL_PATTERNS = [
    re.compile(r"(\.\./|\.\.\\)", re.IGNORECASE),
    re.compile(r"(%2e%2e%2f|%2e%2e/|\.\.%2f)", re.IGNORECASE),
    re.compile(r"(%2e%2e%5c|%2e%2e\\|\.\.%5c)", re.IGNORECASE),
]

JNDI_PATTERN = re.compile(r"(\$\{jndi:)", re.IGNORECASE)

LOGIN_PATH_INDICATORS = ["/login", "/auth", "/signin", "/user/login", "/rest/user/login"]


def compute_token_fingerprint(secret: str, key: str) -> str:
    """Compute HMAC-SHA256 lowercase hex fingerprint of secret.

    Rule 9: Never store or transmit raw secrets.
    """
    key_bytes = key.encode("utf-8")
    msg_bytes = secret.strip().encode("utf-8")
    return hmac.new(key_bytes, msg_bytes, hashlib.sha256).hexdigest().lower()


class AttackDetector:
    """Detects attack heuristics and computes token HMAC fingerprints."""

    def __init__(self, fingerprint_key: str) -> None:
        self.fingerprint_key = fingerprint_key
        # Tracks failed login timestamps: ip -> list of float timestamps
        self._login_failures: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def extract_token_fingerprints(
        self,
        auth_header: str | None,
        x_api_key_header: str | None,
        uri: str,
    ) -> list[str]:
        """Extract and immediately hash authorization tokens and API keys locally."""
        fingerprints: list[str] = []

        # 1. Authorization header (Bearer or Raw)
        if auth_header and auth_header != "-":
            raw_token = auth_header
            if raw_token.lower().startswith("bearer "):
                raw_token = raw_token[7:].strip()
            elif raw_token.lower().startswith("basic "):
                raw_token = raw_token[6:].strip()
            if raw_token:
                fingerprints.append(compute_token_fingerprint(raw_token, self.fingerprint_key))

        # 2. X-API-Key header
        if x_api_key_header and x_api_key_header != "-":
            token = x_api_key_header.strip()
            if token:
                fingerprints.append(compute_token_fingerprint(token, self.fingerprint_key))

        # 3. Query string tokens (?key=, ?token=, ?api_key=)
        try:
            parsed_url = urllib.parse.urlparse(uri)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            for param_name in ("key", "token", "api_key", "apikey"):
                if param_name in query_params:
                    for val in query_params[param_name]:
                        if val.strip():
                            fingerprints.append(
                                compute_token_fingerprint(val.strip(), self.fingerprint_key)
                            )
        except (ValueError, KeyError, AttributeError):
            pass

        # Return unique lowercase hex fingerprints
        return list(dict.fromkeys(fingerprints))

    def detect_flags(
        self,
        ip: str,
        path: str,
        status: int,
        ua: str,
        raw_line: str,
    ) -> list[str]:
        """Evaluate request metadata against attack signatures."""
        flags: list[str] = []

        # Decode path for inspectable payload detection
        decoded_path = urllib.parse.unquote_plus(path)
        combined_text = f"{decoded_path} {ua} {raw_line}"

        # 1. JNDI exploit inspection
        if JNDI_PATTERN.search(combined_text):
            flags.append("jndi")

        # 2. Path Traversal inspection
        if any(pat.search(decoded_path) for pat in TRAVERSAL_PATTERNS) or any(
            pat.search(path) for pat in TRAVERSAL_PATTERNS
        ):
            flags.append("traversal")

        # 3. SQL Injection inspection
        if any(pat.search(decoded_path) for pat in SQLI_PATTERNS):
            flags.append("sqli")

        # 4. Brute Force inspection (>=8 responses with 401 on login path within 60s)
        is_login_path = any(lp in path.lower() for lp in LOGIN_PATH_INDICATORS)
        if status == 401 and is_login_path:
            now = time.time()
            window_start = now - 60.0

            with self._lock:
                # Retain only timestamps from the last 60 seconds
                failures = [t for t in self._login_failures[ip] if t > window_start]
                failures.append(now)
                self._login_failures[ip] = failures

                if len(failures) >= 8:
                    flags.append("bruteforce")

        return sorted(set(flags))

    def reset_bruteforce_tracker(self) -> None:
        """Reset failed login history (used in test isolation)."""
        with self._lock:
            self._login_failures.clear()
