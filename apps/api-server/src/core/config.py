import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ECOBRIDGE API Server"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database Configuration
    DATABASE_URL: str = "postgresql://ecobridge:ecobridge_dev_password@localhost:5432/ecobridge_dev"
    ASYNC_DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"

    # JWT Authentication
    JWT_SECRET_KEY: str = "ecobridge_dev_secret_key_change_in_production_32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for mobile collectors
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # OTP Configuration
    OTP_EXPIRE_MINUTES: int = 10
    TEST_OTP: str = "123456"

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator("ASYNC_DATABASE_URL", mode="before")
    @classmethod
    def assemble_async_db_connection(cls, v: Union[str, None], info) -> str:
        if v and isinstance(v, str) and v.strip():
            return v
        data = info.data
        db_url = data.get("DATABASE_URL", "")
        if not db_url:
            db_url = os.getenv("DATABASE_URL", "postgresql://ecobridge:ecobridge_dev_password@localhost:5432/ecobridge_dev")
        if db_url.startswith("postgresql://"):
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        return db_url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
