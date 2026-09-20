import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .taxonomy import Material
    from .lot import Lot


class PriceObservation(Base, TimestampMixin):
    __tablename__ = "price_observations"

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
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="KG", nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50),
        default="LOCAL_SCRAPYARD_QUOTE",
        nullable=False,
    )  # e.g. OBSERVED_TRANSACTION, LOCAL_SCRAPYARD_QUOTE, COMMODITY_EXCHANGE, OFFICIAL_INDEX
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Dharavi Mandi", "LME Cash"
    region: Mapped[str] = mapped_column(String(100), default="National", nullable=False, index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    confidence_weight: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("1.00"), nullable=False)

    # Relationship
    material: Mapped["Material"] = relationship(
        "Material",
        lazy="selectin",
    )


class RecyclerOffer(Base, TimestampMixin):
    __tablename__ = "recycler_offers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    lot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    recycler_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    recycler_name: Mapped[str] = mapped_column(String(255), nullable=False)
    offered_price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    offered_total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    pickup_cost_deduction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    net_collector_earning: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OFFERED", nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Relationships
    lot: Mapped[Optional["Lot"]] = relationship(
        "Lot",
        lazy="selectin",
    )
    material: Mapped[Optional["Material"]] = relationship(
        "Material",
        lazy="selectin",
    )
