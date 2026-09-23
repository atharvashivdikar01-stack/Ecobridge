import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    PROJECT_NAME: str = "ECOBRIDGE API Server"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./ecobridge.db"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "*"]
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 5
    MEDIA_ROOT: str = "media"
    MAX_IMAGE_UPLOAD_BYTES: int = 5 * 1024 * 1024
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if value is None or value == "*":
            return ["*"]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value
    @property
    def ASYNC_DATABASE_URL(self):
        if self.DATABASE_URL.startswith('sqlite+aiosqlite://'):
            return self.DATABASE_URL
        if self.DATABASE_URL.startswith('sqlite'):
            return self.DATABASE_URL.replace('sqlite://', 'sqlite+aiosqlite://', 1)
        if self.DATABASE_URL.startswith('postgresql+asyncpg://'): return self.DATABASE_URL
        if self.DATABASE_URL.startswith('postgresql://'):
            return self.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
        if self.DATABASE_URL.startswith('postgres://'):
            return self.DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)
        return self.DATABASE_URL
settings=Settings()
