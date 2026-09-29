from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.bootstrap import CATALOG
from ....models import WasteCategory, Material, MaterialPriceBand
from ....schemas.response import ApiResponse
from ....schemas.pricing import (
    CreatePriceObservationRequest,
    CreateRecyclerOfferRequest,
    ObservedPriceDetail,
    RecyclerOfferDetail,
    MaterialPriceIntelligenceResponse,
    LotValuationResponse,
    BenchmarkPriceItem,
    BenchmarkPriceListResponse,
)
from ....services.price_intelligence_service import price_intelligence_service

router = APIRouter(prefix="/prices", tags=["Price Intelligence"])


@router.get(
    "",
    response_model=ApiResponse[BenchmarkPriceListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All E-Waste Benchmark Prices",
    description="Returns current active benchmark prices, price bands, and safety hazard severity for the standard 8 e-waste categories.",
)
async def get_all_benchmark_prices(
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[BenchmarkPriceListResponse]:
    result = await db.execute(
        select(Material, WasteCategory, MaterialPriceBand)
        .join(WasteCategory, Material.category_id == WasteCategory.id)
        .outerjoin(MaterialPriceBand, MaterialPriceBand.material_id == Material.id)
    )
    rows = result.all()

    items = []
    seen_codes = set()
    for mat, cat, pb in rows:
        if cat.code in seen_codes:
            continue
        seen_codes.add(cat.code)
        rate = float(pb.benchmark_price_per_unit) if pb and pb.benchmark_price_per_unit is not None else 0.0
        min_p = float(pb.min_price_per_unit) if pb and pb.min_price_per_unit is not None else rate
        max_p = float(pb.max_price_per_unit) if pb and pb.max_price_per_unit is not None else rate
        eff = pb.effective_from.isoformat() if pb and pb.effective_from else None
        items.append(BenchmarkPriceItem(
            category_code=cat.code,
            material_code=mat.code or f"{cat.code}_MAT",
            name=cat.name,
            benchmark_price_per_kg=rate,
            min_price_per_kg=min_p,
            max_price_per_kg=max_p,
            default_hazard=cat.default_hazard or "NORMAL",
            effective_from=eff,
        ))

    if not items:
        for code, name, rate, hazard in CATALOG:
            items.append(BenchmarkPriceItem(
                category_code=code,
                material_code=f"{code}_MAT",
                name=name,
                benchmark_price_per_kg=rate,
                min_price_per_kg=rate * 0.9,
                max_price_per_kg=rate * 1.1,
                default_hazard=hazard,
            ))

    return ApiResponse.create_success(BenchmarkPriceListResponse(items=items))


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
