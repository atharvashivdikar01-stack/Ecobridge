import uuid
from decimal import Decimal
from sqlalchemy import String,Numeric,ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from .base import Base
from .types import GUID
class RecyclerPayment(Base):
 __tablename__='recycler_payments'; __table_args__=(UniqueConstraint('gateway_reference', name='uq_recycler_payment_gateway_reference'),); id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); lot_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('lots.id')); recycler_id:Mapped[uuid.UUID]=mapped_column(GUID()); payment_method:Mapped[str]=mapped_column(String(30)); payment_status:Mapped[str]=mapped_column(String(30),default='PAID'); total_amount:Mapped[Decimal]=mapped_column(Numeric(12,2)); gateway_reference:Mapped[str]=mapped_column(String(100)); weighbridge_slip:Mapped[str]=mapped_column(String(100)); custody_hash:Mapped[str]=mapped_column(String(64))
