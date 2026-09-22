import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .lot import Lot
    from .recycler import RecyclerCompany, RecyclerFacility
    from .collector import CollectorProfile


class Handover(Base, TimestampMixin):
    __tablename__ = "handovers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    lot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    facility_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recycler_facilities.id", ondelete="SET NULL"),
        nullable=True,
    )
    recycler_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recycler_companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    collector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("collector_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    handover_type: Mapped[str] = mapped_column(
        String(50),
        default="COLLECTOR_TO_FACILITY",
        nullable=False,
    )
    weighbridge_slip_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    weighbridge_gross_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    weighbridge_tare_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    weighbridge_net_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    scale_calibration_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    signed_manifest_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="COMPLETED",
        nullable=False,
        index=True,
    )  # PENDING, COMPLETED, DISPUTED
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    handed_over_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    lot: Mapped["Lot"] = relationship("Lot", lazy="selectin")
    facility: Mapped[Optional["RecyclerFacility"]] = relationship("RecyclerFacility", lazy="selectin")
    recycler: Mapped["RecyclerCompany"] = relationship("RecyclerCompany", lazy="selectin")
    collector: Mapped["CollectorProfile"] = relationship("CollectorProfile", lazy="selectin")


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    reference_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        default="COLLECTOR_PAYOUT",
        nullable=False,
    )
    lot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recycler_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recycler_companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    collector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("collector_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    material_name: Mapped[str] = mapped_column(String(200), nullable=False)
    verified_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    agreed_price_per_kg: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)  # Verified Weight x Agreed Price
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    payment_method: Mapped[str] = mapped_column(
        String(50),
        default="CASH",
        nullable=False,
    )  # CASH, UPI, IMPS, BANK_TRANSFER
    payment_status: Mapped[str] = mapped_column(
        String(50),
        default="PAID",
        nullable=False,
        index=True,
    )  # PENDING, PAID, FAILED
    gateway_reference: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="SETTLED",
        nullable=False,
        index=True,
    )  # PENDING, SETTLED, REFUNDED
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    settled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    lot: Mapped["Lot"] = relationship("Lot", lazy="selectin")
    recycler: Mapped["RecyclerCompany"] = relationship("RecyclerCompany", lazy="selectin")
    collector: Mapped["CollectorProfile"] = relationship("CollectorProfile", lazy="selectin")
