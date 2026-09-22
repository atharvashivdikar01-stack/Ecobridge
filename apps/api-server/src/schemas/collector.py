import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CollectorProfileResponse(BaseModel):
    id: str
    user_id: str
    phone: str
    full_name: str
    collector_type: str
    preferred_language: str
    national_id_number: Optional[str] = None
    national_id_type: Optional[str] = None
    bank_account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    upi_id: Optional[str] = None
    trust_score: float
    total_lots_collected: int
    total_weight_kg: float
    is_verified: bool
    verified_at: Optional[str] = None
    created_at: str


class CollectorProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    preferred_language: Optional[str] = Field(None, min_length=2, max_length=10)
    upi_id: Optional[str] = Field(None, max_length=100)
    bank_account_number: Optional[str] = Field(None, min_length=9, max_length=30)
    ifsc_code: Optional[str] = Field(None, min_length=11, max_length=11)

    @field_validator("upi_id")
    @classmethod
    def validate_upi(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v = v.strip()
            if not re.match(r"^[\w\.\-]+@[\w\-]+$", v):
                raise ValueError("Invalid UPI ID format. Expected format: username@bank")
            return v
        return None

    @field_validator("ifsc_code")
    @classmethod
    def validate_ifsc(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v = v.strip().upper()
            if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", v):
                raise ValueError("Invalid IFSC code format. Expected 4 letters, 0, followed by 6 alphanumeric characters")
            return v
        return None


class CollectorKycSubmission(BaseModel):
    national_id_type: str = Field(..., description="ID document type: AADHAAR, PAN, VOTER_ID")
    national_id_number: str = Field(..., min_length=4, max_length=100, description="Document identifier number")

    @field_validator("national_id_type")
    @classmethod
    def validate_id_type(cls, v: str) -> str:
        v = v.upper()
        allowed = ["AADHAAR", "PAN", "VOTER_ID", "DRIVING_LICENSE"]
        if v not in allowed:
            raise ValueError(f"national_id_type must be one of: {', '.join(allowed)}")
        return v


class CollectorStatsResponse(BaseModel):
    total_lots_collected: int
    total_weight_kg: float
    trust_score: float
