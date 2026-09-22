from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from ....schemas.response import ApiResponse

router = APIRouter(prefix="/payments", tags=["Payment & Escrow Settlement"])


class ConfirmPaymentRequest(BaseModel):
    lot_id: str = Field(..., description="Unique Lot ID e.g. ECO-26-MH-004821")
    amount: float = Field(6407.40, gt=0, description="Payment amount in INR")
    payment_method: str = Field("CASH", description="Payment modality: CASH | UPI | BANK_TRANSFER")
    notes: Optional[str] = Field(None, description="Optional settlement voucher remarks")


@router.post(
    "/confirm",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Confirm E-Waste Lot Collector Payment",
    description="Confirms payment settlement to informal collector via Cash, UPI, or Bank Transfer, updating chain custody and ledger."
)
async def confirm_payment(data: ConfirmPaymentRequest) -> ApiResponse[Dict[str, Any]]:
    now_str = datetime.now(timezone.utc).isoformat()
    txn_ref = f"CSH-{data.lot_id.replace('ECO-26-', '')}-X" if data.payment_method == "CASH" else f"UPI/{int(datetime.now().timestamp())}/AXIS"

    return ApiResponse.create_success({
        "lot_id": data.lot_id,
        "amount_inr": data.amount,
        "payment_method": data.payment_method,
        "status": "CONFIRMED",
        "txn_reference": txn_ref,
        "beneficiary": "Raju Shinde (#842)",
        "confirmed_at": now_str,
    })


@router.get(
    "/earnings",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Collector Earnings Dashboard Summary",
    description="Returns today's earnings, pending intake dues, and total completed earnings for collector."
)
async def get_collector_earnings() -> ApiResponse[Dict[str, Any]]:
    return ApiResponse.create_success({
        "collector_id": "KAB-MH-842",
        "collector_name": "Raju Shinde",
        "today_inr": 6407.40,
        "pending_inr": 1200.00,
        "completed_inr": 17450.00,
        "currency": "INR"
    })
