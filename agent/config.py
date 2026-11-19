"""Configuration settings for ChainGuard Log Agent."""

import os


class AgentConfig:
    def __init__(self) -> None:
        self.CHAINGUARD_API_KEY: str = os.getenv(
            "CHAINGUARD_API_KEY", "cg_live_sample_fake_key_00000000000000000000000000000000"
        )
        self.FINGERPRINT_KEY: str = os.getenv(
            "FINGERPRINT_KEY", "fake_fingerprint_hmac_secret_key_1234567890abcdef"
        )
        self.BACKEND_URL: str = os.getenv(
            "BACKEND_URL", "http://127.0.0.1:8000/v1"
        ).rstrip("/")
        self.LOG_FILE_PATH: str = os.getenv(
            "LOG_FILE_PATH", "./lab/logs/access.log"
        )
        self.BATCH_SIZE: int = int(os.getenv("AGENT_BATCH_SIZE", "50"))
        self.BATCH_INTERVAL_SECONDS: float = float(
            os.getenv("AGENT_BATCH_INTERVAL", "2.0")
        )
        self.MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))


config = AgentConfig()
