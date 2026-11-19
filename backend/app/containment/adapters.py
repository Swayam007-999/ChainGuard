"""Containment adapters for automated and operator-approved network mitigations."""

import ipaddress
import logging
import os
import tempfile
from abc import ABC, abstractmethod

logger = logging.getLogger("chainguard-containment")


class ContainmentAdapter(ABC):
    """Abstract interface for IP containment enforcement."""

    @abstractmethod
    def apply_block(self, ip_str: str) -> bool:
        """Enforce rate-limiting or block on target IP."""

    @abstractmethod
    def remove_block(self, ip_str: str) -> bool:
        """Revert block on target IP."""


class DryRunAdapter(ContainmentAdapter):
    """Default observe-only containment adapter that records intended actions without altering network."""

    def __init__(self) -> None:
        self.blocked_ips: set[str] = set()

    def apply_block(self, ip_str: str) -> bool:
        logger.info("[OBSERVE-ONLY] Would block IP: %s (DryRunAdapter active)", ip_str)
        self.blocked_ips.add(ip_str)
        return True

    def remove_block(self, ip_str: str) -> bool:
        logger.info("[OBSERVE-ONLY] Would unblock IP: %s (DryRunAdapter active)", ip_str)
        self.blocked_ips.discard(ip_str)
        return True


class NginxBlocklistAdapter(ContainmentAdapter):
    """Production enforcement adapter writing atomic Nginx deny include files."""

    def __init__(self, blocklist_file_path: str = "./lab/blocklist.conf") -> None:
        self.blocklist_file_path = blocklist_file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        dir_name = os.path.dirname(self.blocklist_file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.blocklist_file_path):
            with open(self.blocklist_file_path, "w", encoding="utf-8") as f:
                f.write("# ChainGuard Automated Nginx Deny Rules\n")

    def _read_blocked_ips(self) -> set[str]:
        ips: set[str] = set()
        if not os.path.exists(self.blocklist_file_path):
            return ips
        with open(self.blocklist_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("deny ") and line.endswith(";"):
                    ip = line[5:-1].strip()
                    try:
                        ipaddress.ip_address(ip)
                        ips.add(ip)
                    except ValueError:
                        pass
        return ips

    def _write_blocked_ips_atomically(self, ips: set[str]) -> bool:
        dir_name = os.path.dirname(os.path.abspath(self.blocklist_file_path))
        try:
            with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
                tf.write("# ChainGuard Automated Nginx Deny Rules\n")
                for ip in sorted(ips):
                    tf.write(f"deny {ip};\n")
                temp_name = tf.name

            # Atomic replace
            os.replace(temp_name, self.blocklist_file_path)
            return True
        except OSError as exc:
            logger.error("Failed to update Nginx blocklist atomically: %s", exc)
            return False

    def apply_block(self, ip_str: str) -> bool:
        # Rule 4: Strictly validate IP format
        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
            valid_ip = str(ip_obj)
        except ValueError:
            logger.error("Rejected malformed IP for Nginx block: %s", ip_str)
            return False

        ips = self._read_blocked_ips()
        if valid_ip in ips:
            return True
        ips.add(valid_ip)
        success = self._write_blocked_ips_atomically(ips)
        if success:
            logger.info("Enforced Nginx deny for IP: %s", valid_ip)
        return success

    def remove_block(self, ip_str: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
            valid_ip = str(ip_obj)
        except ValueError:
            return False

        ips = self._read_blocked_ips()
        if valid_ip not in ips:
            return True
        ips.discard(valid_ip)
        success = self._write_blocked_ips_atomically(ips)
        if success:
            logger.info("Removed Nginx deny for IP: %s", valid_ip)
        return success


def get_containment_adapter() -> ContainmentAdapter:
    """Factory selecting active containment adapter based on environment variable."""
    mode = os.getenv("CONTAINMENT_MODE", "dry_run").lower()
    if mode == "enforce":
        blocklist_path = os.getenv("NGINX_BLOCKLIST_PATH", "./lab/blocklist.conf")
        return NginxBlocklistAdapter(blocklist_file_path=blocklist_path)
    return DryRunAdapter()
