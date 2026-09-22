import os
from typing import List, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ECOBRIDGE API Server"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "postgresql://localhost:5432/ecobridge_dev"
    ASYNC_DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    REDIS_URL: str = "redis://localhost:6379"

    JWT_SECRET_KEY: str = "ecobridge_dev_secret_key_change_in_production_32bytes"
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "ecobridge-api"
    JWT_AUDIENCE: str = "ecobridge-clients"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    OTP_EXPIRE_MINUTES: int = 10
    TEST_OTP: str = "123456"
    OTP_MAX_ATTEMPTS: int = 5
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", "http://localhost:3001",
        "http://localhost:3002", "http://localhost:8000",
    ]
    LOG_LEVEL: str = "INFO"

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        normalized = str(value).strip().lower()
        if normalized not in {"development", "test", "staging", "production"}:
            raise ValueError("ENVIRONMENT must be development, test, staging, or production")
        return normalized

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        if value not in {"HS256", "HS384", "HS512"}:
            raise ValueError("JWT_ALGORITHM must be one of HS256, HS384, or HS512")
        return value

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_secret_length(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")
        return value

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, value: List[str]) -> List[str]:
        if "*" in value:
            raise ValueError("Wildcard CORS origins are not allowed")
        return value

    @model_validator(mode="after")
    def validate_deployment_settings(self) -> "Settings":
        if self.ENVIRONMENT in {"production", "staging"}:
            if self.DEBUG:
                raise ValueError("DEBUG must be false in staging and production")
            if self.JWT_SECRET_KEY == "ecobridge_dev_secret_key_change_in_production_32bytes":
                raise ValueError("JWT_SECRET_KEY must be replaced in staging and production")
            if self.TEST_OTP:
                raise ValueError("TEST_OTP must be empty in staging and production")
            if "localhost" in self.DATABASE_URL or "localhost" in self.REDIS_URL:
                raise ValueError("staging and production require non-local service URLs")
        return self

    @field_validator("ASYNC_DATABASE_URL", mode="before")
    @classmethod
    def assemble_async_db_connection(cls, v: Union[str, None], info) -> str:
        if v and isinstance(v, str) and v.strip():
            return v
        data = info.data
        db_url = data.get("DATABASE_URL", "") or os.getenv("DATABASE_URL", "postgresql://localhost:5432/ecobridge_dev")
        if db_url.startswith("postgresql://"):
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        return db_url

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
