import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin
from .types import GUID


class HandoverRecord(Base, TimestampMixin):
    __tablename__ = "handover_records"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("lots.id", ondelete="CASCADE"), index=True)
    collector_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("collector_profiles.id"), index=True)
    reference_no: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    requested_recycler_id: Mapped[str] = mapped_column(String(100))
    declared_weight_kg: Mapped[float] = mapped_column(Numeric(12, 3))
    declared_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    payment_mode: Mapped[str] = mapped_column(String(30))
    payment_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    record_hash: Mapped[str] = mapped_column(String(64))
    collector_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="PENDING_RECYCLER_CONFIRMATION", index=True)
    recycler_note: Mapped[str | None] = mapped_column(Text, nullable=True)
