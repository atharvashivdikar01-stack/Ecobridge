from typing import Optional
from pydantic import BaseModel, Field


class HealthCheckData(BaseModel):
    """Payload for health check responses."""
    status: str = Field(description="Overall system status (HEALTHY, DEGRADED, UNHEALTHY)")
    database_connected: bool = Field(description="True if PostgreSQL connection test succeeded")
    version: str = Field(description="API Server version")
    environment: str = Field(description="Deployment environment (development, staging, production)")
    uptime_seconds: float = Field(description="Server uptime in seconds")


class LivenessData(BaseModel):
    """Payload for lightweight liveness probes."""
    alive: bool = True
