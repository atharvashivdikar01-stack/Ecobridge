from typing import Any, Optional


class AppException(Exception):
    """Base application exception with structured error envelope metadata."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
            details=details,
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details=details,
        )


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required", details: Optional[Any] = None):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
            details=details,
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access forbidden", details: Optional[Any] = None):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
            details=details,
        )


class DatabaseConnectionError(AppException):
    def __init__(self, message: str = "Database service unavailable", details: Optional[Any] = None):
        super().__init__(
            code="DATABASE_UNAVAILABLE",
            message=message,
            status_code=503,
            details=details,
        )
