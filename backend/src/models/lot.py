import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from .types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .collector import CollectorProfile
    from .taxonomy import Material
    from .traceability import CustodyEvent


class Lot(Base, TimestampMixin):
    __tablename__ = "lots"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    lot_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    collector_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("collector_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    designated_facility_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="COLLECTED", nullable=False, index=True)
    total_estimated_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        default=Decimal("0.000"),
        nullable=False,
    )
    total_verified_weight_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    estimated_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    final_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    agreed_price_per_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    weighbridge_slip_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    verified_weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3), nullable=True)
    origin_latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    origin_longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    origin_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    offline_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    collector: Mapped["CollectorProfile"] = relationship(
        "CollectorProfile",
        lazy="selectin",
    )
    items: Mapped[List["LotItem"]] = relationship(
        "LotItem",
        back_populates="lot",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    images: Mapped[List["LotImage"]] = relationship(
        "LotImage",
        back_populates="lot",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    custody_events: Mapped[List["CustodyEvent"]] = relationship(
        "CustodyEvent",
        back_populates="lot",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class LotItem(Base, TimestampMixin):
    __tablename__ = "lot_items"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    lot_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("materials.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="KG", nullable=False)
    estimated_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    verified_weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3), nullable=True)
    ai_confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    detected_hazard: Mapped[str] = mapped_column(String(50), default="NORMAL", nullable=False)
    safety_guidance_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), nullable=True)
    unit_price_estimated: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    unit_price_verified: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    subtotal_estimated: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    subtotal_final: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    lot: Mapped["Lot"] = relationship(
        "Lot",
        back_populates="items",
    )
    material: Mapped["Material"] = relationship(
        "Material",
        back_populates="lot_items",
        lazy="selectin",
    )


class LotImage(Base):
    __tablename__ = "lot_images"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    lot_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lot_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        ForeignKey("lot_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    image_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_proof_of_collection: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    lot: Mapped["Lot"] = relationship(
        "Lot",
        back_populates="images",
    )
