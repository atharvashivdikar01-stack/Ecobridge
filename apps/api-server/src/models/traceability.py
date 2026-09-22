import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

JSON_FIELD = JSON().with_variant(JSONB, "postgresql")

if TYPE_CHECKING:
    from .lot import Lot
    from .user import User


class CustodyEvent(Base):
    __tablename__ = "custody_events"

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
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    actor_role: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
    event_payload_json: Mapped[dict] = mapped_column(JSON_FIELD, nullable=False)
    previous_event_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_event_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    digital_signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    lot: Mapped["Lot"] = relationship(
        "Lot",
        back_populates="custody_events",
    )
    actor: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )
