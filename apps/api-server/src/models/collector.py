import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User


class CollectorProfile(Base, TimestampMixin):
    __tablename__ = "collector_profiles"

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
    collector_type: Mapped[str] = mapped_column(
        String(50),
        default="INDIVIDUAL_PICKER",
        nullable=False,
    )
    national_id_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    national_id_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ifsc_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    upi_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    trust_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("1.00"),
        nullable=False,
    )
    total_lots_collected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        default=Decimal("0.000"),
        nullable=False,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationship to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="collector_profile",
    )
