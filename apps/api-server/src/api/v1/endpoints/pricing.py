from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....schemas.response import ApiResponse
from ....schemas.pricing import (
    CreatePriceObservationRequest,
    CreateRecyclerOfferRequest,
    ObservedPriceDetail,
    RecyclerOfferDetail,
    MaterialPriceIntelligenceResponse,
    LotValuationResponse,
)
from ....services.price_intelligence_service import price_intelligence_service

router = APIRouter(prefix="/prices", tags=["Price Intelligence"])


@router.get(
    "/intelligence/{material_id}",
    response_model=ApiResponse[MaterialPriceIntelligenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Material Price Intelligence",
    description="Returns empirical market observations, deterministic statistical model estimates, and active recycler offers. Strictly distinguishes observed prices from model estimates without machine learning.",
)
async def get_material_price_intelligence(
    material_id: str,
    region: Optional[str] = Query(None, description="Filter observations by geographic region (e.g., 'Mumbai', 'Delhi', 'National')"),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MaterialPriceIntelligenceResponse]:
    result = await price_intelligence_service.get_material_price_intelligence(
        db=db,
        material_id=material_id,
        region=region,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/lot-valuation/{lot_id}",
    response_model=ApiResponse[LotValuationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dynamic Lot Valuation",
    description="Calculates comprehensive lot valuation combining individual item weights with latest observed median rates, statistical fair model prices, and active recycler offers.",
)
async def get_lot_valuation(
    lot_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotValuationResponse]:
    result = await price_intelligence_service.get_lot_valuation(
        db=db,
        lot_id=lot_id,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/observations",
    response_model=ApiResponse[ObservedPriceDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Record Market Price Observation",
    description="Records an empirical scrap yard transaction quote, commodity exchange price, or field market observation.",
)
async def record_price_observation(
    data: CreatePriceObservationRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ObservedPriceDetail]:
    result = await price_intelligence_service.record_observation(
        db=db,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/offers",
    response_model=ApiResponse[RecyclerOfferDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Submit Recycler Offer",
    description="Submits an active certified recycler quote for a specific material or lot, factoring in pickup logistics deductions.",
)
async def submit_recycler_offer(
    data: CreateRecyclerOfferRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerOfferDetail]:
    result = await price_intelligence_service.submit_recycler_offer(
        db=db,
        data=data,
    )
    return ApiResponse.create_success(result)
