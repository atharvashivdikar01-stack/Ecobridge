import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String,Text,ForeignKey,Integer,DateTime,JSON
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .base import Base
from .types import GUID
class CustodyEvent(Base):
 __tablename__='custody_events'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); lot_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('lots.id',ondelete='CASCADE')); sequence_number:Mapped[int]=mapped_column(Integer); event_type:Mapped[str]=mapped_column(String(50)); actor_id:Mapped[Optional[uuid.UUID]]=mapped_column(GUID(),nullable=True); actor_role:Mapped[Optional[str]]=mapped_column(String(50),nullable=True); event_timestamp:Mapped[datetime]=mapped_column(DateTime(timezone=True)); event_payload_json:Mapped[dict]=mapped_column(JSON,default=dict); previous_event_hash:Mapped[str]=mapped_column(String(64)); current_event_hash:Mapped[str]=mapped_column(String(64)); lot=relationship('Lot',back_populates='custody_events')
