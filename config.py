import os
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-me")
    JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "12"))

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "dna_secure_vault")
    USE_INMEMORY_DB = _bool("USE_INMEMORY_DB", True)

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))

    # Brute-force protection
    LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
    LOGIN_LOCKOUT_SECONDS = int(os.getenv("LOGIN_LOCKOUT_SECONDS", "300"))  # 5 min

    # Global rate limits (per client IP) — used by Flask-Limiter
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per minute")
    RATE_LIMIT_AUTH = os.getenv("RATE_LIMIT_AUTH", "10 per minute")
    RATE_LIMIT_ATTACK = os.getenv("RATE_LIMIT_ATTACK", "20 per minute")

    # CORS allowed origins (comma-separated). Use "*" to allow all.
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
