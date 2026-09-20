from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MatchingItemInput(BaseModel):
    material_id: str = Field(..., description="UUID of material")
    weight_kg: float = Field(..., gt=0.0, description="Weight in kilograms")
    detected_hazard: str = Field("NORMAL", description="Condition e.g. NORMAL, SWOLLEN_BATTERY, BROKEN_CRT_GLASS")


class EvaluateManifestRequest(BaseModel):
    items: List[MatchingItemInput] = Field(..., min_length=1, description="Material items to evaluate")
    origin_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Collection GPS latitude")
    origin_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Collection GPS longitude")
    require_pickup: bool = Field(False, description="Filter for recyclers with active doorstep pickup")
    max_distance_km: Optional[float] = Field(None, gt=0.0, description="Maximum search distance in km")


class MaterialCompatibilityItem(BaseModel):
    material_id: str
    material_code: str
    material_name: str
    weight_kg: float
    is_accepted: bool
    offered_rate_per_unit: Optional[float] = None
    subtotal: float
    detected_hazard: str


class MatchingFinancialBreakdown(BaseModel):
    gross_payout: float
    transport_cost: float
    pickup_subsidy: float
    net_collector_earnings: float
    currency: str = "INR"


class MatchingLogisticsBreakdown(BaseModel):
    distance_km: float
    pickup_available: bool
    pickup_mode: str  # FREE_RECYCLER_PICKUP, SUBSIDIZED_RECYCLER_PICKUP, COLLECTOR_SELF_TRANSPORT
    min_pickup_weight_kg: float
    lead_time_hours: int
    pickup_operating_days: str


class MatchingComplianceBreakdown(BaseModel):
    is_verified_recycler: bool
    cpcb_authorized: bool
    accepts_hazardous: bool
    active_permits_count: int
    hazard_compatibility_cleared: bool


class RecyclerMatchCandidate(BaseModel):
    rank: int
    facility_id: str
    company_id: str
    company_name: str
    facility_name: str
    city: str
    state: str
    compatibility_status: str  # FULLY_COMPATIBLE, PARTIALLY_COMPATIBLE, DISQUALIFIED_HAZARD, OUT_OF_RANGE
    financial: MatchingFinancialBreakdown
    logistics: MatchingLogisticsBreakdown
    compliance: MatchingComplianceBreakdown
    materials: List[MaterialCompatibilityItem]
    explanation: str
    pros: List[str]
    cons: List[str]


class LotMatchingResponse(BaseModel):
    lot_id: Optional[str] = None
    total_weight_kg: float
    has_hazardous_items: bool
    origin_coordinates: Optional[Dict[str, float]] = None
    total_candidates_evaluated: int
    eligible_matches_count: int
    best_match: Optional[RecyclerMatchCandidate] = None
    recommendations: List[RecyclerMatchCandidate]
