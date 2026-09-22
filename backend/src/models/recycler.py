import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy import String,Text,ForeignKey,Numeric,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .base import Base,TimestampMixin
from .types import GUID
class RecyclerCompany(Base,TimestampMixin):
 __tablename__='recycler_companies'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),unique=True); company_name:Mapped[str]=mapped_column(String(250)); trade_license_number:Mapped[Optional[str]]=mapped_column(String(100),nullable=True); gst_number:Mapped[Optional[str]]=mapped_column(String(50),nullable=True); cpcb_registration_no:Mapped[Optional[str]]=mapped_column(String(100),nullable=True); contact_person:Mapped[Optional[str]]=mapped_column(String(150),nullable=True); contact_phone:Mapped[Optional[str]]=mapped_column(String(30),nullable=True); operating_status:Mapped[str]=mapped_column(String(40),default='PENDING_VERIFICATION'); user=relationship('User',back_populates='recycler_company'); facilities=relationship('RecyclerFacility',back_populates='recycler',lazy='selectin',cascade='all, delete-orphan')
class RecyclerFacility(Base,TimestampMixin):
 __tablename__='recycler_facilities'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); recycler_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('recycler_companies.id')); facility_name:Mapped[str]=mapped_column(String(200)); address_line1:Mapped[Optional[str]]=mapped_column(Text,nullable=True); city:Mapped[Optional[str]]=mapped_column(String(100),nullable=True); state:Mapped[Optional[str]]=mapped_column(String(100),nullable=True); postal_code:Mapped[Optional[str]]=mapped_column(String(20),nullable=True); latitude:Mapped[Optional[Decimal]]=mapped_column(Numeric(10,7),nullable=True); longitude:Mapped[Optional[Decimal]]=mapped_column(Numeric(10,7),nullable=True); daily_capacity_kg:Mapped[Optional[Decimal]]=mapped_column(Numeric(12,2),nullable=True); accepts_hazardous:Mapped[bool]=mapped_column(Boolean,default=False); recycler=relationship('RecyclerCompany',back_populates='facilities')
