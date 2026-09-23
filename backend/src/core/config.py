from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    PROJECT_NAME: str = "ECOBRIDGE API Server"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql://ecobridge:ecobridge@localhost:5432/ecobridge"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ]
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 5
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    @property
    def ASYNC_DATABASE_URL(self):
        if self.DATABASE_URL.startswith('sqlite'):
            return self.DATABASE_URL.replace('sqlite://', 'sqlite+aiosqlite://', 1)
        if self.DATABASE_URL.startswith('postgresql+asyncpg://'): return self.DATABASE_URL
        if self.DATABASE_URL.startswith('postgresql://'):
            return self.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
        if self.DATABASE_URL.startswith('postgres://'):
            return self.DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)
        return self.DATABASE_URL
settings=Settings()
