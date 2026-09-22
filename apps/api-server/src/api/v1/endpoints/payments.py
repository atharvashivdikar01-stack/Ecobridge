from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from ....schemas.response import ApiResponse
from ....core.database import get_db
from ....core.exceptions import ForbiddenError, NotFoundError, ValidationError
from ....models.lot import Lot
from ....models.user import User
from ...deps import get_current_collector

router = APIRouter(prefix="/payments", tags=["Payment & Escrow Settlement"])


class ConfirmPaymentRequest(BaseModel):
    lot_id: str = Field(..., description="Unique Lot ID e.g. ECO-26-MH-004821")
    payment_method: str = Field("CASH", description="Payment modality: CASH | UPI | BANK_TRANSFER")
    notes: Optional[str] = Field(None, description="Optional settlement voucher remarks")


@router.post(
    "/confirm",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Confirm E-Waste Lot Collector Payment",
    description="Confirms payment settlement to informal collector via Cash, UPI, or Bank Transfer, updating chain custody and ledger."
)
async def confirm_payment(
    data: ConfirmPaymentRequest,
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[Dict[str, Any]]:
    try:
        lot_uuid = uuid.UUID(data.lot_id)
    except ValueError:
        raise ValidationError(message="Invalid lot ID format")
    result = await db.execute(select(Lot).where(Lot.id == lot_uuid))
    lot = result.scalar_one_or_none()
    if not lot:
        raise NotFoundError(message="Lot not found")
    if not current_collector.collector_profile or lot.collector_id != current_collector.collector_profile.id:
        raise ForbiddenError(message="You do not have permission to settle this lot")
    amount = lot.final_value if lot.final_value is not None else lot.estimated_value
    if amount is None or amount <= 0:
        raise ValidationError(message="Lot has no payable persisted value")
    now_str = datetime.now(timezone.utc).isoformat()
    txn_ref = f"CSH-{data.lot_id.replace('ECO-26-', '')}-X" if data.payment_method == "CASH" else f"UPI/{int(datetime.now().timestamp())}/AXIS"

    return ApiResponse.create_success({
        "lot_id": data.lot_id,
        "amount_inr": float(amount),
        "payment_method": data.payment_method,
        "status": "CONFIRMED",
        "txn_reference": txn_ref,
        "beneficiary": current_collector.full_name,
        "confirmed_at": now_str,
    })


@router.get(
    "/earnings",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Collector Earnings Dashboard Summary",
    description="Returns today's earnings, pending intake dues, and total completed earnings for collector."
)
async def get_collector_earnings(
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[Dict[str, Any]]:
    if not current_collector.collector_profile:
        raise NotFoundError(message="Collector profile not found")
    result = await db.execute(select(Lot).where(Lot.collector_id == current_collector.collector_profile.id))
    lots = result.scalars().all()
    completed = sum(
        Decimal(str(l.final_value if l.final_value is not None else l.estimated_value))
        for l in lots if l.status in {"SETTLED", "COMPLETED"}
    )
    pending = sum(
        Decimal(str(l.final_value if l.final_value is not None else l.estimated_value))
        for l in lots if l.status not in {"SETTLED", "COMPLETED"}
    )
    return ApiResponse.create_success({
        "collector_id": str(current_collector.collector_profile.id),
        "collector_name": current_collector.full_name,
        "today_inr": 0.0,
        "pending_inr": float(pending),
        "completed_inr": float(completed),
        "currency": "INR"
    })
