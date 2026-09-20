from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CreatePriceObservationRequest(BaseModel):
    material_id: str = Field(..., description="UUID of the material")
    price_per_unit: float = Field(..., gt=0, description="Observed price per unit")
    currency: str = Field("INR", max_length=10)
    unit: str = Field("KG", max_length=20)
    source_type: str = Field(
        "LOCAL_SCRAPYARD_QUOTE",
        description="Type of source e.g. OBSERVED_TRANSACTION, LOCAL_SCRAPYARD_QUOTE, COMMODITY_EXCHANGE",
    )
    source_name: str = Field(..., max_length=100, description="Source name e.g. Dharavi Mandi, Seelampur Market")
    region: str = Field("National", max_length=100, description="Geographic region e.g. Mumbai, Delhi, National")
    observed_at: Optional[datetime] = Field(None, description="Time of observation (defaults to current time)")
    confidence_weight: float = Field(1.0, ge=0.0, le=1.0, description="Confidence weight (0.0 to 1.0)")


class CreateRecyclerOfferRequest(BaseModel):
    material_id: Optional[str] = Field(None, description="UUID of the material (if generic offer)")
    lot_id: Optional[str] = Field(None, description="UUID of specific lot (if lot-specific offer)")
    recycler_id: str = Field(..., description="UUID of certified recycler")
    recycler_name: str = Field(..., max_length=255, description="Name of the recycler company/facility")
    offered_price_per_unit: float = Field(..., gt=0, description="Offered price per unit")
    offered_total_price: float = Field(..., gt=0, description="Total offer value")
    pickup_cost_deduction: float = Field(0.0, ge=0.0, description="Deduction for logistics/pickup")
    currency: str = Field("INR", max_length=10)
    expires_at: Optional[datetime] = Field(None, description="Expiry timestamp of this offer")


class ObservedPriceDetail(BaseModel):
    id: str
    price_per_unit: float
    currency: str
    unit: str
    source_type: str
    source_name: str
    region: str
    observed_at: str
    confidence_weight: float


class ObservedMetricsResponse(BaseModel):
    data_type: str = "EMPIRICAL_OBSERVATIONS"
    sample_size: int
    market_min: Optional[float] = None
    market_max: Optional[float] = None
    local_median: Optional[float] = None
    mean: Optional[float] = None
    latest_price: Optional[float] = None
    observations: List[ObservedPriceDetail]


class ModelEstimateResponse(BaseModel):
    data_type: str = "STATISTICAL_MODEL_ESTIMATE"
    fair_price: Optional[float] = None
    recommended_floor: Optional[float] = None
    recommended_ceiling: Optional[float] = None
    method: str = "WEIGHTED_MEDIAN_IQR"
    confidence_level: str  # "HIGH", "MEDIUM", "LOW", "INSUFFICIENT_DATA"
    disclaimer: str = (
        "Statistical model estimate derived from deterministic quantile distribution. Not a guaranteed quote."
    )


class RecyclerOfferDetail(BaseModel):
    id: str
    recycler_id: str
    recycler_name: str
    offered_price_per_unit: float
    offered_total_price: float
    pickup_cost_deduction: float
    net_collector_earning: float
    currency: str
    status: str
    expires_at: str
    created_at: str


class RecyclerOffersResponse(BaseModel):
    data_type: str = "ACTIVE_RECYCLER_OFFERS"
    active_offers_count: int
    highest_offer_price: Optional[float] = None
    average_offer_price: Optional[float] = None
    offers: List[RecyclerOfferDetail]


class MaterialPriceIntelligenceResponse(BaseModel):
    material_id: str
    material_code: str
    material_name: str
    base_unit: str
    region: str
    benchmark_price: float
    observed_metrics: ObservedMetricsResponse
    model_estimate: ModelEstimateResponse
    active_recycler_offers: RecyclerOffersResponse


class LotValuationItemResponse(BaseModel):
    material_id: str
    material_name: str
    weight_kg: float
    observed_median_rate: Optional[float] = None
    estimated_model_rate: float
    subtotal_estimated: float


class LotValuationResponse(BaseModel):
    lot_id: str
    total_weight_kg: float
    currency: str
    items_valuation: List[LotValuationItemResponse]
    total_estimated_value: float
    highest_active_offer: Optional[float] = None
    model_estimate_range: Dict[str, float]
