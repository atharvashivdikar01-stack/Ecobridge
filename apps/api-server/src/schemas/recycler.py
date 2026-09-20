from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class RegisterFacilityRequest(BaseModel):
    facility_name: str = Field(..., max_length=255, description="Name of processing facility")
    address_line1: str = Field(..., max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    daily_capacity_kg: float = Field(0.0, ge=0.0)
    accepts_hazardous: bool = Field(False)
    pickup_available: bool = Field(False)
    min_pickup_weight_kg: float = Field(50.0, ge=0.0)
    max_pickup_distance_km: float = Field(50.0, ge=0.0)
    lead_time_hours: int = Field(24, ge=1)
    pickup_operating_days: str = Field("MON-SAT", max_length=100)


class RegisterRecyclerRequest(BaseModel):
    company_name: str = Field(..., max_length=255, description="Registered legal name of recycler company")
    trade_license_number: str = Field(..., max_length=100, description="Municipal trade license number")
    gst_number: Optional[str] = Field(None, max_length=50, description="GST identification number")
    cpcb_registration_no: str = Field(..., max_length=100, description="CPCB/SPCB registration number")
    contact_person: str = Field(..., max_length=100)
    contact_phone: str = Field(..., max_length=20)
    contact_email: Optional[str] = Field(None, max_length=255)
    primary_facility: RegisterFacilityRequest


class UpdateRecyclerCompanyRequest(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=255)
    gst_number: Optional[str] = Field(None, max_length=50)


class CreateFacilityRequest(RegisterFacilityRequest):
    pass


class UpdateFacilityRequest(BaseModel):
    facility_name: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    daily_capacity_kg: Optional[float] = Field(None, ge=0.0)
    accepts_hazardous: Optional[bool] = None
    is_active: Optional[bool] = None


class CreateAuthorizationRequest(BaseModel):
    authority_name: str = Field(..., max_length=100, description="Issuing authority (e.g. CPCB, SPCB, MPCB)")
    permit_type: str = Field(
        ...,
        max_length=100,
        description="Permit type e.g. HAZARDOUS_WASTE_AUTHORIZATION, E_WASTE_DISMANTLER, E_WASTE_RECYCLER",
    )
    permit_number: str = Field(..., max_length=100, description="Government permit/license number")
    authorized_capacity_mta: Optional[float] = Field(None, ge=0.0, description="Authorized capacity in Metric Tonnes per Annum")
    issued_date: date = Field(..., description="Date of issuance (YYYY-MM-DD)")
    expiry_date: date = Field(..., description="Date of expiry (YYYY-MM-DD)")
    document_url: Optional[str] = Field(None, description="URL to scanned permit certificate")
    status: str = Field("ACTIVE", max_length=50)

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry(cls, v: date, info) -> date:
        data = info.data
        issued = data.get("issued_date")
        if issued and v <= issued:
            raise ValueError("expiry_date must be after issued_date")
        return v


class AuthorizationResponse(BaseModel):
    id: str
    facility_id: str
    authority_name: str
    permit_type: str
    permit_number: str
    authorized_capacity_mta: Optional[float] = None
    issued_date: str
    expiry_date: str
    status: str
    document_url: Optional[str] = None
    verified_at: Optional[str] = None
    created_at: str


class ConfigureAcceptedMaterialRequest(BaseModel):
    material_id: str = Field(..., description="UUID of material")
    standard_rate_per_unit: float = Field(..., gt=0.0, description="Standard standing rate offered per unit")
    minimum_accepted_weight_kg: float = Field(1.0, gt=0.0, description="Minimum lot weight accepted in kg")
    currency: str = Field("INR", max_length=10)
    is_active: bool = Field(True)


class UpdateAcceptedMaterialRateRequest(BaseModel):
    standard_rate_per_unit: Optional[float] = Field(None, gt=0.0)
    minimum_accepted_weight_kg: Optional[float] = Field(None, gt=0.0)
    is_active: Optional[bool] = None


class AcceptedMaterialResponse(BaseModel):
    id: str
    facility_id: str
    material_id: str
    material_name: str
    material_code: str
    base_unit: str
    standard_rate_per_unit: float
    minimum_accepted_weight_kg: float
    currency: str
    is_active: bool


class CreateServiceAreaRequest(BaseModel):
    region_name: str = Field(..., max_length=150, description="Region or hub name e.g. Mumbai Metropolitan Region")
    state: str = Field(..., max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    postal_codes: Optional[str] = Field(None, description="Comma-separated postal codes")
    radius_km: Optional[float] = Field(None, ge=0.0, description="Coverage radius from facility in km")
    is_active: bool = Field(True)


class ServiceAreaResponse(BaseModel):
    id: str
    facility_id: str
    region_name: str
    state: str
    city: Optional[str] = None
    postal_codes: Optional[str] = None
    radius_km: Optional[float] = None
    is_active: bool


class UpdatePickupAvailabilityRequest(BaseModel):
    pickup_available: bool = Field(..., description="Whether facility dispatches vehicles for lot pickup")
    min_pickup_weight_kg: Optional[float] = Field(None, ge=0.0)
    max_pickup_distance_km: Optional[float] = Field(None, ge=0.0)
    lead_time_hours: Optional[int] = Field(None, ge=1)
    pickup_operating_days: Optional[str] = Field(None, max_length=100)


class PickupAvailabilityResponse(BaseModel):
    facility_id: str
    pickup_available: bool
    min_pickup_weight_kg: float
    max_pickup_distance_km: float
    lead_time_hours: int
    pickup_operating_days: str


class VerifyRecyclerRequest(BaseModel):
    operating_status: str = Field(..., description="Status to set: VERIFIED, SUSPENDED, REJECTED")
    verification_notes: Optional[str] = Field(None, max_length=1000)

    @field_validator("operating_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"VERIFIED", "SUSPENDED", "REJECTED", "PENDING_VERIFICATION"}
        val = v.strip().upper()
        if val not in allowed:
            raise ValueError(f"operating_status must be one of: {', '.join(allowed)}")
        return val


class VerificationStatusResponse(BaseModel):
    company_id: str
    company_name: str
    operating_status: str
    verification_notes: Optional[str] = None
    verified_at: Optional[str] = None


class FacilityResponse(BaseModel):
    id: str
    recycler_id: str
    facility_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float
    daily_capacity_kg: float
    accepts_hazardous: bool
    is_active: bool
    pickup_available: bool
    min_pickup_weight_kg: float
    max_pickup_distance_km: float
    lead_time_hours: int
    pickup_operating_days: str
    authorizations: List[AuthorizationResponse] = []
    accepted_materials: List[AcceptedMaterialResponse] = []
    service_areas: List[ServiceAreaResponse] = []


class RecyclerCompanyResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    trade_license_number: str
    gst_number: Optional[str] = None
    cpcb_registration_no: str
    contact_person: str
    contact_phone: str
    contact_email: Optional[str] = None
    operating_status: str
    verification_notes: Optional[str] = None
    verified_at: Optional[str] = None
    created_at: str
    facilities: List[FacilityResponse] = []


class RecyclerDirectoryItemResponse(BaseModel):
    facility_id: str
    company_id: str
    company_name: str
    facility_name: str
    operating_status: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float
    accepts_hazardous: bool
    pickup_available: bool
    min_pickup_weight_kg: float
    lead_time_hours: int
    accepted_materials_count: int
    active_authorizations_count: int
    service_regions: List[str]
    rates: Dict[str, float] = {}


class RecyclerDirectoryListResponse(BaseModel):
    total: int
    recyclers: List[RecyclerDirectoryItemResponse]
