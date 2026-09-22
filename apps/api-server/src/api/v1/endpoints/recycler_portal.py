from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....models.user import User
from ....schemas.response import ApiResponse
from ....schemas.recycler_portal import (
    AvailableMaterialItem,
    AvailableMaterialsListResponse,
    AcceptOfferRequest,
    ConfirmHandoverRequest,
    RecordPaymentRequest,
    RecyclerTransactionResponse,
    RecyclerLedgerResponse,
    RecyclerDashboardSummary,
)
from ....services.recycler_portal_service import recycler_portal_service
from ...deps import get_current_user, get_current_recycler

router = APIRouter(prefix="/recycler-portal", tags=["Recycler Operations Portal"])


@router.get(
    "/dashboard",
    response_model=ApiResponse[RecyclerDashboardSummary],
    status_code=status.HTTP_200_OK,
    summary="Get Recycler Dashboard Overview",
    description="Retrieves KPI metrics: available lots, pending handovers, completed deals, total processed weight, and total disbursements.",
)
async def get_dashboard(
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerDashboardSummary]:
    result = await recycler_portal_service.get_dashboard_summary(
        db=db,
        current_user=current_recycler,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/materials",
    response_model=ApiResponse[AvailableMaterialsListResponse],
    status_code=status.HTTP_200_OK,
    summary="List Available Materials & Collections",
    description="Lists e-waste collection batches available for recycler procurement, with photographs, AI classification, safety hazard alerts, and verified weights.",
)
async def list_available_materials(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (AVAILABLE, OFFER_ACCEPTED, HANDOVER_PENDING, COMPLETED)"),
    material_type: Optional[str] = Query(None, description="Search filter by material name"),
    hazardous_only: bool = Query(False, description="Filter only materials with hazardous conditions"),
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AvailableMaterialsListResponse]:
    result = await recycler_portal_service.get_available_materials(
        db=db,
        status_filter=status_filter,
        material_type=material_type,
        hazardous_only=hazardous_only,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/materials/{lot_id}",
    response_model=ApiResponse[AvailableMaterialItem],
    status_code=status.HTTP_200_OK,
    summary="Get Material Collection Details",
    description="Retrieves detailed item breakdown, photos, AI advisory classifications, safety PPE alerts, collector details, and status.",
)
async def get_material_detail(
    lot_id: str,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AvailableMaterialItem]:
    result = await recycler_portal_service.get_material_detail(
        db=db,
        lot_id=lot_id,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/lots/{lot_id}/accept",
    response_model=ApiResponse[AvailableMaterialItem],
    status_code=status.HTTP_200_OK,
    summary="Accept Material Lot Offer",
    description="Accepts an offer on a lot. Validates that the recycler is CPCB-verified, sets agreed recycler price, calculates Final Value = Verified Weight x Agreed Price, and transitions status to ACCEPTED.",
)
async def accept_offer(
    lot_id: str,
    data: AcceptOfferRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AvailableMaterialItem]:
    result = await recycler_portal_service.accept_offer(
        db=db,
        current_user=current_recycler,
        lot_id=lot_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/lots/{lot_id}/handover",
    response_model=ApiResponse[AvailableMaterialItem],
    status_code=status.HTTP_200_OK,
    summary="Confirm Physical Handover & Weighbridge Scale",
    description="Confirms physical lot intake, records weighbridge slip number and gross/tare/net scale weight, locks final transaction value, and appends a SHA-256 custody event.",
)
async def confirm_handover(
    lot_id: str,
    data: ConfirmHandoverRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AvailableMaterialItem]:
    result = await recycler_portal_service.confirm_handover(
        db=db,
        current_user=current_recycler,
        lot_id=lot_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/lots/{lot_id}/payment",
    response_model=ApiResponse[RecyclerTransactionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record Payment & Add to Ledger",
    description="Records payment settlement (Cash payment works offline/without gateway, or Optional Digital UPI/IMPS), generates immutable transaction reference, appends final custody event, and logs into accounting ledger.",
)
async def record_payment(
    lot_id: str,
    data: RecordPaymentRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerTransactionResponse]:
    result = await recycler_portal_service.record_payment(
        db=db,
        current_user=current_recycler,
        lot_id=lot_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/ledger",
    response_model=ApiResponse[RecyclerLedgerResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Recycler Earnings & Audit Ledger",
    description="Returns auditable ledger of all completed transactions with material, verified weight, agreed rate, total payout, payment method, payment status, weighbridge slip, and tamper-evident custody hash.",
)
async def get_ledger(
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerLedgerResponse]:
    result = await recycler_portal_service.get_recycler_ledger(
        db=db,
        current_user=current_recycler,
    )
    return ApiResponse.create_success(result)
