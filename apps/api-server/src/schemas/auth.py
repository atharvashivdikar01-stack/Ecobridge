import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def normalize_phone(v: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)]", "", v)
    if not re.match(r"^\+?[0-9]{10,15}$", cleaned):
        raise ValueError("Invalid phone number format. Must be between 10 and 15 digits.")
    return cleaned


class SendOtpRequest(BaseModel):
    phone: str = Field(..., description="Mobile phone number with optional country code")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)


class SendOtpResponse(BaseModel):
    phone: str
    message: str
    expires_in_seconds: int


class VerifyOtpRequest(BaseModel):
    phone: str = Field(..., description="Mobile phone number")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification OTP")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name if new user registration")
    collector_type: Optional[str] = Field("INDIVIDUAL_PICKER", description="Collector category")
    preferred_language: Optional[str] = Field("en", max_length=10, description="Preferred language code")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        if not re.match(r"^[0-9]{6}$", v):
            raise ValueError("OTP must be exactly 6 numeric digits")
        return v


class UserSummary(BaseModel):
    id: str
    phone: str
    full_name: str
    role: str
    status: str
    preferred_language: str
    avatar_url: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserSummary


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid refresh token")


class DemoLoginRequest(BaseModel):
    role: str = Field("VERIFIED_RECYCLER", description="Role to switch into: VERIFIED_RECYCLER, UNVERIFIED_RECYCLER, or COLLECTOR")
