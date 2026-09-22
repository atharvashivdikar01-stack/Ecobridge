import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

JSON_FIELD = JSON().with_variant(JSONB, "postgresql")

if TYPE_CHECKING:
    from .lot import LotItem


class WasteCategory(Base):
    __tablename__ = "waste_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_hazard: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    materials: Mapped[List["Material"]] = relationship(
        "Material",
        back_populates="category",
        lazy="selectin",
    )


class Material(Base, TimestampMixin):
    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("waste_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_unit: Mapped[str] = mapped_column(String(20), default="KG", nullable=False)
    standard_yield_json: Mapped[Optional[dict]] = mapped_column(JSON_FIELD, nullable=True)
    requires_permit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    category: Mapped["WasteCategory"] = relationship(
        "WasteCategory",
        back_populates="materials",
        lazy="selectin",
    )
    price_bands: Mapped[List["MaterialPriceBand"]] = relationship(
        "MaterialPriceBand",
        back_populates="material",
        lazy="selectin",
    )
    lot_items: Mapped[List["LotItem"]] = relationship(
        "LotItem",
        back_populates="material",
    )


class MaterialPriceBand(Base):
    __tablename__ = "material_price_bands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    grade: Mapped[str] = mapped_column(String(50), default="STANDARD", nullable=False)
    min_price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    benchmark_price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    material: Mapped["Material"] = relationship(
        "Material",
        back_populates="price_bands",
    )
