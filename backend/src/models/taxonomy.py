import uuid
from decimal import Decimal
from typing import Optional,List
from sqlalchemy import String,Text,ForeignKey,Numeric,Boolean,DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .base import Base,TimestampMixin
from .types import GUID
class WasteCategory(Base):
 __tablename__='waste_categories'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); code:Mapped[str]=mapped_column(String(50),unique=True); name:Mapped[str]=mapped_column(String(200)); description:Mapped[Optional[str]]=mapped_column(Text,nullable=True); default_hazard:Mapped[str]=mapped_column(String(50),default='NORMAL'); materials=relationship('Material',back_populates='category',lazy='selectin',cascade='all, delete-orphan')
class Material(Base):
 __tablename__='materials'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); category_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('waste_categories.id')); code:Mapped[str]=mapped_column(String(80),unique=True); name:Mapped[str]=mapped_column(String(200)); base_unit:Mapped[str]=mapped_column(String(20),default='KG'); category=relationship('WasteCategory',back_populates='materials'); price_bands=relationship('MaterialPriceBand',back_populates='material',lazy='selectin',cascade='all, delete-orphan'); lot_items=relationship('LotItem',back_populates='material')
class MaterialPriceBand(Base):
 __tablename__='material_price_bands'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); material_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('materials.id')); grade:Mapped[str]=mapped_column(String(50)); min_price_per_unit:Mapped[Decimal]=mapped_column(Numeric(12,2)); max_price_per_unit:Mapped[Decimal]=mapped_column(Numeric(12,2)); benchmark_price_per_unit:Mapped[Decimal]=mapped_column(Numeric(12,2)); currency:Mapped[str]=mapped_column(String(10),default='INR'); effective_from:Mapped[object]=mapped_column(DateTime(timezone=True)); is_active:Mapped[bool]=mapped_column(Boolean,default=True); material=relationship('Material',back_populates='price_bands')
