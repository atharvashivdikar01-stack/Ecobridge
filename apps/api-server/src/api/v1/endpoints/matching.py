from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....schemas.response import ApiResponse
from ....schemas.matching import (
    EvaluateManifestRequest,
    LotMatchingResponse,
)
from ....services.matching_service import matching_service
from ....models.user import User
from ...deps import get_current_user, get_current_collector

router = APIRouter(prefix="/matching", tags=["Recycler Matching Engine"])


@router.post(
    "/lots/{lot_id}",
    response_model=ApiResponse[LotMatchingResponse],
    status_code=status.HTTP_200_OK,
    summary="Match Lot with Certified Recyclers",
    description="Intelligently matches a staged e-waste collection lot with certified recyclers based on regulatory authorization, hazardous compliance, GPS distance, pickup logistics, gross payout, transport cost, and net collector earnings. Returns an explainable recommendation.",
)
async def match_lot(
    lot_id: str,
    require_pickup: bool = Query(False, description="Filter for recyclers with active doorstep pickup"),
    max_distance_km: Optional[float] = Query(None, description="Maximum search distance in km"),
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotMatchingResponse]:
    result = await matching_service.match_lot(
        db=db,
        lot_id=lot_id,
        require_pickup=require_pickup,
        max_distance_km=max_distance_km,
        current_user=current_collector,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/evaluate",
    response_model=ApiResponse[LotMatchingResponse],
    status_code=status.HTTP_200_OK,
    summary="Evaluate Manifest Against Certified Recyclers",
    description="Evaluates an ad-hoc list of e-waste materials and approximate weights with optional collection coordinates against certified recyclers before lot staging.",
)
async def evaluate_manifest(
    data: EvaluateManifestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotMatchingResponse]:
    result = await matching_service.evaluate_manifest(
        db=db,
        request=data,
    )
    return ApiResponse.create_success(result)
