"""Application settings and environment configuration."""

import os


def _load_dotenv() -> None:
    """Load key-value pairs from .env into os.environ if not already set."""
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
    ]
    for env_path in candidates:
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            key = k.strip()
                            val = v.strip().strip('"').strip("'")
                            if key and key not in os.environ:
                                os.environ[key] = val
                break
            except OSError:
                pass


_load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.CHAINGUARD_API_KEY: str = os.getenv(
            "CHAINGUARD_API_KEY", "cg_live_sample_fake_key_00000000000000000000000000000000"
        )
        self.ADMIN_PASSWORD: str = os.getenv(
            "ADMIN_PASSWORD", "change_this_fake_admin_password_in_prod"
        )
        self.JWT_SECRET: str = os.getenv(
            "JWT_SECRET", "fake_jwt_secret_key_minimum_32_characters_long_for_security_12345"
        )
        self.FINGERPRINT_KEY: str = os.getenv(
            "FINGERPRINT_KEY", "fake_fingerprint_hmac_secret_key_1234567890abcdef"
        )
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", "sqlite:///./chainguard.db"
        )
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1")

        # Parse CORS allowlist
        raw_cors: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
        self.CORS_ORIGINS: list[str] = [
            origin.strip() for origin in raw_cors.split(",") if origin.strip()
        ]

        # Rate limiting configuration (requests per minute window)
        self.RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
        self.RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "30"))


settings = Settings()
