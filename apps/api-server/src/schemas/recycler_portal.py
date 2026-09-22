from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class AvailableMaterialItem(BaseModel):
    lot_id: str
    lot_code: str
    collector_id: str
    collector_name: str
    collector_phone: str
    material_id: str
    material_code: str
    material_name: str
    category_name: str
    estimated_weight_kg: float
    verified_weight_kg: Optional[float] = None
    ai_classification: str
    ai_confidence_score: Optional[float] = None
    detected_hazard: str
    hazard_severity: str = "INFO"  # INFO, WARNING, DANGER, CRITICAL
    safety_advisory: Optional[str] = None
    required_ppe: List[str] = Field(default_factory=list)
    benchmark_price_per_kg: float
    min_price_per_kg: float
    max_price_per_kg: float
    agreed_price_per_kg: Optional[float] = None
    final_value: Optional[float] = None  # verified_weight * agreed_price
    currency: str = "INR"
    status: str  # AVAILABLE, OFFER_ACCEPTED, HANDOVER_PENDING, COMPLETED
    origin_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    thumbnail_url: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    created_at: str


class AvailableMaterialsListResponse(BaseModel):
    items: List[AvailableMaterialItem]
    total: int


class AcceptOfferRequest(BaseModel):
    agreed_price_per_kg: float = Field(..., gt=0, description="Agreed recycler purchase price per kg")
    verified_weight_kg: Optional[float] = Field(None, gt=0, description="Scale weight if weighed at inspection")
    notes: Optional[str] = None


class ConfirmHandoverRequest(BaseModel):
    weighbridge_slip_number: str = Field(..., min_length=2, description="Physical scale/weighbridge voucher number")
    weighbridge_gross_kg: Optional[float] = None
    weighbridge_tare_kg: Optional[float] = None
    verified_weight_kg: float = Field(..., gt=0, description="Net certified scale weight in kg")
    scale_calibration_id: Optional[str] = None
    facility_id: Optional[str] = None
    notes: Optional[str] = None


class RecordPaymentRequest(BaseModel):
    payment_method: str = Field("CASH", description="Payment method: CASH, UPI, IMPS, or BANK_TRANSFER")
    amount: float = Field(..., gt=0, description="Amount paid in INR (must equal verified weight x agreed price)")
    gateway_reference: Optional[str] = Field(None, description="Receipt voucher ID for cash or transaction UTR for digital")
    notes: Optional[str] = None


class RecyclerTransactionResponse(BaseModel):
    transaction_id: str
    reference_number: str
    lot_id: str
    lot_code: str
    collector_id: str
    collector_name: str
    collector_phone: str
    material_name: str
    verified_weight_kg: float
    agreed_price_per_kg: float
    total_amount: float
    currency: str = "INR"
    payment_method: str
    payment_status: str
    gateway_reference: Optional[str] = None
    weighbridge_slip: Optional[str] = None
    custody_hash: Optional[str] = None
    handed_over_at: Optional[str] = None
    settled_at: Optional[str] = None
    created_at: str


class RecyclerLedgerResponse(BaseModel):
    transactions: List[RecyclerTransactionResponse]
    total_volume_kg: float
    total_disbursed_inr: float
    total_transactions: int


class RecyclerDashboardSummary(BaseModel):
    company_name: str
    cpcb_registration_no: str
    operating_status: str  # VERIFIED, PENDING_VERIFICATION, SUSPENDED, REJECTED
    is_verified: bool
    available_lots_count: int
    pending_offers_count: int
    pending_handovers_count: int
    completed_transactions_count: int
    total_weight_recycled_kg: float
    total_payouts_inr: float
