import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CreateLotItemRequest(BaseModel):
    material_id: str = Field(..., description="UUID of the selected e-waste material")
    estimated_weight_kg: float = Field(..., gt=0, description="Approximate weight in kilograms (must be positive)")
    quantity: int = Field(1, ge=1, description="Item piece count")
    unit: str = Field("KG", max_length=20)
    detected_hazard: str = Field("NORMAL", description="Detected condition e.g. NORMAL, SWOLLEN_BATTERY, BROKEN_CRT_GLASS")
    ai_confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI detection confidence score (0-1)")
    unit_price_estimated: Optional[float] = Field(None, ge=0.0, description="Estimated price per unit (auto-populated if None)")
    notes: Optional[str] = Field(None, max_length=1000)


class CreateLotImageRequest(BaseModel):
    image_url: str = Field(..., description="URL or storage path of photo")
    image_hash: Optional[str] = Field(None, description="SHA-256 integrity hash (auto-computed if omitted)")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    captured_at: Optional[datetime] = Field(None, description="Timestamp when photo was captured")
    is_proof_of_collection: bool = Field(True, description="True if this photo serves as proof of collection")

    @field_validator("image_hash", mode="before")
    @classmethod
    def default_hash(cls, v: Optional[str], info) -> str:
        if v and isinstance(v, str) and v.strip():
            return v.strip()
        data = info.data
        url = data.get("image_url", "ecobridge_default_image")
        return hashlib.sha256(url.encode("utf-8")).hexdigest()


class CreateLotRequest(BaseModel):
    lot_code: Optional[str] = Field(None, max_length=50, description="Optional custom or mobile offline lot code")
    origin_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Collection GPS latitude")
    origin_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Collection GPS longitude")
    origin_address: Optional[str] = Field(None, max_length=500, description="Physical address / landmark")
    offline_created_at: Optional[datetime] = Field(None, description="Timestamp created offline on mobile device")
    items: List[CreateLotItemRequest] = Field(..., min_length=1, description="Material items included in this collection batch")
    images: Optional[List[CreateLotImageRequest]] = Field(default_factory=list, description="Attached proof photos")


class LotItemResponse(BaseModel):
    id: str
    material_id: str
    material_name: str
    material_code: str
    category_name: str
    quantity: int
    unit: str
    estimated_weight_kg: float
    verified_weight_kg: Optional[float] = None
    unit_price_estimated: float
    subtotal_estimated: float
    detected_hazard: str
    ai_confidence_score: Optional[float] = None
    notes: Optional[str] = None


class LotImageResponse(BaseModel):
    id: str
    image_url: str
    image_hash: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    captured_at: str
    is_proof_of_collection: bool


class LotResponse(BaseModel):
    id: str
    lot_code: str
    collector_id: str
    collector_name: str
    status: str
    total_estimated_weight_kg: float
    total_verified_weight_kg: Optional[float] = None
    estimated_value: float
    final_value: Optional[float] = None
    currency: str
    origin_latitude: Optional[float] = None
    origin_longitude: Optional[float] = None
    origin_address: Optional[str] = None
    offline_created_at: str
    synced_at: Optional[str] = None
    created_at: str
    items_count: int
    items: List[LotItemResponse]
    images: List[LotImageResponse]


class LotListResponse(BaseModel):
    lots: List[LotResponse]
    total: int
    page: int
    page_size: int


class MaterialItemTaxonomy(BaseModel):
    id: str
    code: str
    name: str
    base_unit: str
    benchmark_price_per_unit: float
    min_price_per_unit: float
    max_price_per_unit: float
    default_hazard: str


class CategoryTaxonomyResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    materials: List[MaterialItemTaxonomy]


class TaxonomyListResponse(BaseModel):
    categories: List[CategoryTaxonomyResponse]
