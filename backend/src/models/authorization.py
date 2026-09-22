import uuid
from sqlalchemy import String,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from .base import Base
from .types import GUID
class AuthorizationRecord(Base):
 __tablename__='authorization_records'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); facility_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('recycler_facilities.id')); authorization_type:Mapped[str]=mapped_column(String(80)); authorization_number:Mapped[str]=mapped_column(String(120))
