from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiError(BaseModel):
    """Structured error payload adhering to AGENTS.md."""
    code: str
    message: str
    details: Optional[Any] = None


class ApiResponse(BaseModel, Generic[T]):
    """Unified API response envelope matching AGENTS.md invariant."""
    success: bool
    data: Optional[T] = None
    error: Optional[ApiError] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def create_success(cls, data: T) -> "ApiResponse[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def create_error(
        cls,
        code: str,
        message: str,
        details: Optional[Any] = None
    ) -> "ApiResponse[None]":
        return cls(
            success=False,
            data=None,
            error=ApiError(code=code, message=message, details=details)
        )
