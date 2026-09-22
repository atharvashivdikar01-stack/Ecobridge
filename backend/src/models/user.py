import uuid
from typing import Optional
from sqlalchemy import String,Boolean
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .base import Base,TimestampMixin
from .types import GUID
class User(Base,TimestampMixin):
 __tablename__='users'; id:Mapped[uuid.UUID]=mapped_column(GUID(),primary_key=True,default=uuid.uuid4); phone:Mapped[str]=mapped_column(String(30),unique=True,index=True); full_name:Mapped[str]=mapped_column(String(200)); role:Mapped[str]=mapped_column(String(40),default='COLLECTOR'); status:Mapped[str]=mapped_column(String(30),default='ACTIVE'); preferred_language:Mapped[str]=mapped_column(String(10),default='en'); avatar_url:Mapped[Optional[str]]=mapped_column(String(500),nullable=True)
 collector_profile=relationship('CollectorProfile',back_populates='user',uselist=False,lazy='selectin',cascade='all, delete-orphan')
 recycler_company=relationship('RecyclerCompany',back_populates='user',uselist=False,lazy='selectin',cascade='all, delete-orphan')
