import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import settings
from .core.database import close_database_connection
from .core.exceptions import AppException
from .core.logging import get_logger, setup_logging
from .schemas.response import ApiResponse
from .api.v1.router import v1_router

logger = get_logger("ecobridge.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown."""
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    yield
    logger.info("Shutting down application, cleaning up resources...")
    await close_database_connection()
    logger.info("Shutdown completed.")


def create_application() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Core API backend for ECOBRIDGE - connecting informal collectors with certified recyclers.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ----------------------------------------------------
    # Middleware
    # ----------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ----------------------------------------------------
    # Centralized Exception Handlers (AGENTS.md contract)
    # ----------------------------------------------------
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(f"AppException: [{exc.code}] {exc.message} on {request.url.path}")
        response_body = ApiResponse.create_error(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_body.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info(f"Validation error on {request.url.path}: {exc.errors()}")
        formatted_errors = [
            {
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        response_body = ApiResponse.create_error(
            code="VALIDATION_ERROR",
            message="Input validation failed",
            details=formatted_errors,
        )
        return JSONResponse(
            status_code=422,
            content=response_body.model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code_map = {
            404: "NOT_FOUND",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            405: "METHOD_NOT_ALLOWED",
        }
        error_code = code_map.get(exc.status_code, "HTTP_ERROR")
        response_body = ApiResponse.create_error(
            code=error_code,
            message=str(exc.detail),
            details=None,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_body.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
        response_body = ApiResponse.create_error(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred",
            details=str(exc) if settings.DEBUG else None,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_body.model_dump(),
        )

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as exc:
            response = await unhandled_exception_handler(request, exc)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response

    # ----------------------------------------------------
    # Router Mounts
    # ----------------------------------------------------
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
