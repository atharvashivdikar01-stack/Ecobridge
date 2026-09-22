import time
from fastapi import APIRouter, status
from ....core.config import settings
from ....core.database import check_database_connection
from ....schemas.response import ApiResponse
from ....schemas.health import HealthCheckData, LivenessData

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])

# Record server start time
START_TIME = time.time()


@router.get(
    "",
    response_model=ApiResponse[HealthCheckData],
    status_code=status.HTTP_200_OK,
    summary="Comprehensive Health Check",
    description="Probes system readiness, database connectivity, and returns operational metadata."
)
async def health_check() -> ApiResponse[HealthCheckData]:
    db_ok = await check_database_connection()
    uptime = round(time.time() - START_TIME, 2)
    overall_status = "HEALTHY" if db_ok else "DEGRADED"

    data = HealthCheckData(
        status=overall_status,
        database_connected=db_ok,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=uptime,
    )
    return ApiResponse.create_success(data)


@router.get(
    "/liveness",
    response_model=ApiResponse[LivenessData],
    status_code=status.HTTP_200_OK,
    summary="Container Liveness Probe",
    description="Lightweight check for Kubernetes / container liveness probes."
)
async def liveness_probe() -> ApiResponse[LivenessData]:
    return ApiResponse.create_success(LivenessData(alive=True))
