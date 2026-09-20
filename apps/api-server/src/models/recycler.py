import uuid
from decimal import Decimal
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .taxonomy import Material


class RecyclerCompany(Base, TimestampMixin):
    __tablename__ = "recycler_companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_license_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    gst_number: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True
    )
    cpcb_registration_no: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    operating_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING_VERIFICATION",
        nullable=False,
        index=True,
    )  # PENDING_VERIFICATION, VERIFIED, SUSPENDED, REJECTED
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )
    facilities: Mapped[List["RecyclerFacility"]] = relationship(
        "RecyclerFacility",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RecyclerFacility(Base, TimestampMixin):
    __tablename__ = "recycler_facilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    recycler_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recycler_companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    facility_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    daily_capacity_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    accepts_hazardous: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Pickup availability & logistics
    pickup_available: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    min_pickup_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("50.00"), nullable=False
    )
    max_pickup_distance_km: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), default=Decimal("50.00"), nullable=False
    )
    lead_time_hours: Mapped[int] = mapped_column(
        Integer, default=24, nullable=False
    )
    pickup_operating_days: Mapped[str] = mapped_column(
        String(100), default="MON-SAT", nullable=False
    )

    # Relationships
    company: Mapped["RecyclerCompany"] = relationship(
        "RecyclerCompany",
        back_populates="facilities",
    )
    authorizations: Mapped[List["AuthorizationRecord"]] = relationship(
        "AuthorizationRecord",
        back_populates="facility",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    accepted_materials: Mapped[List["RecyclerAcceptedMaterial"]] = relationship(
        "RecyclerAcceptedMaterial",
        back_populates="facility",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    service_areas: Mapped[List["RecyclerServiceArea"]] = relationship(
        "RecyclerServiceArea",
        back_populates="facility",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AuthorizationRecord(Base, TimestampMixin):
    __tablename__ = "authorization_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recycler_facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    authority_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g. CPCB, MPCB, SPCB
    permit_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g. HAZARDOUS_WASTE_AUTHORIZATION, E_WASTE_DISMANTLER, E_WASTE_RECYCLER
    permit_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    authorized_capacity_mta: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50), default="ACTIVE", nullable=False, index=True
    )  # ACTIVE, EXPIRED, REVOKED, SUSPENDED
    document_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    facility: Mapped["RecyclerFacility"] = relationship(
        "RecyclerFacility",
        back_populates="authorizations",
    )


class RecyclerAcceptedMaterial(Base, TimestampMixin):
    __tablename__ = "recycler_accepted_materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recycler_facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materials.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    minimum_accepted_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("1.00"), nullable=False
    )
    standard_rate_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    facility: Mapped["RecyclerFacility"] = relationship(
        "RecyclerFacility",
        back_populates="accepted_materials",
    )
    material: Mapped["Material"] = relationship(
        "Material",
        lazy="selectin",
    )


class RecyclerServiceArea(Base, TimestampMixin):
    __tablename__ = "recycler_service_areas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recycler_facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    region_name: Mapped[str] = mapped_column(
        String(150), nullable=False, index=True
    )  # e.g. "Mumbai Metropolitan Region"
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    city: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    postal_codes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Comma-separated postal codes: "400001,400017,400028"
    radius_km: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    facility: Mapped["RecyclerFacility"] = relationship(
        "RecyclerFacility",
        back_populates="service_areas",
    )
