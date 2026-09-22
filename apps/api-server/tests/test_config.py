import os
from src.core.config import Settings


def test_settings_default():
    s = Settings()
    assert s.PROJECT_NAME == "ECOBRIDGE API Server"
    assert s.VERSION == "0.1.0"
    assert s.API_V1_PREFIX == "/api/v1"
    assert "postgresql+asyncpg://" in s.ASYNC_DATABASE_URL


def test_settings_async_url_generation():
    s = Settings(DATABASE_URL="postgresql://user:pass@host:5432/testdb")
    assert s.ASYNC_DATABASE_URL == "postgresql+asyncpg://user:pass@host:5432/testdb"

    s2 = Settings(DATABASE_URL="postgres://user:pass@host:5432/testdb")
    assert s2.ASYNC_DATABASE_URL == "postgresql+asyncpg://user:pass@host:5432/testdb"


def test_settings_cors_origins():
    s = Settings(CORS_ORIGINS=["http://localhost:3000", "https://ecobridge.org"])
    assert len(s.CORS_ORIGINS) == 2
    assert "https://ecobridge.org" in s.CORS_ORIGINS
