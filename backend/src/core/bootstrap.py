"""Create tables and seed the 8-class catalog used by the Android app."""
from datetime import datetime, timezone
from decimal import Decimal
import uuid

from sqlalchemy import select

from ..models import Base, Material, MaterialPriceBand, RecyclerCompany, User, WasteCategory
from .database import SessionLocal, engine

LOCAL_RECYCLER_ID = uuid.UUID("00000000-0000-0000-0000-000000000101")
CATALOG = [
    ("CAT_CRT", "CRT Monitors & TVs", 45.0, "HAZARD"),
    ("CAT_LCD_LED", "LCD / LED Panels", 85.0, "WARNING"),
    ("CAT_PCB", "Printed Circuit Boards (PCBs)", 330.0, "WARNING"),
    ("CAT_CABLES", "Copper Cables & Wires", 195.0, "NORMAL"),
    ("CAT_BATTERY", "Batteries", 105.0, "HAZARD"),
    ("CAT_MOTORS", "Motors & Magnet Assemblies", 55.0, "NORMAL"),
    ("CAT_PLASTICS", "Mixed E-Waste Plastics", 22.0, "NORMAL"),
    ("CAT_OTHER", "Other Electronic Scrap", 40.0, "NORMAL"),
]


async def bootstrap_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        for code, name, rate, hazard in CATALOG:
            category = (await session.execute(select(WasteCategory).where(WasteCategory.code == code))).scalar_one_or_none()
            if category is None:
                category = WasteCategory(code=code, name=name, description=name, default_hazard=hazard)
                session.add(category)
                await session.flush()
            material = (await session.execute(select(Material).where(Material.name == name))).scalar_one_or_none()
            if material is None:
                material = Material(category_id=category.id, code=code + "_MAT", name=name)
                session.add(material)
                await session.flush()
                session.add(MaterialPriceBand(
                    material_id=material.id,
                    grade="BENCHMARK",
                    min_price_per_unit=Decimal(str(rate)),
                    max_price_per_unit=Decimal(str(rate)),
                    benchmark_price_per_unit=Decimal(str(rate)),
                    effective_from=datetime.now(timezone.utc),
                ))
        user = (await session.execute(select(User).where(User.phone == "+919811111111"))).scalar_one_or_none()
        if user is None:
            user = User(phone="+919811111111", full_name="Local Test Recycler", role="RECYCLER_ADMIN")
            session.add(user)
            await session.flush()
        company = (await session.execute(select(RecyclerCompany).where(RecyclerCompany.id == LOCAL_RECYCLER_ID))).scalar_one_or_none()
        if company is None:
            session.add(RecyclerCompany(
                id=LOCAL_RECYCLER_ID,
                user_id=user.id,
                company_name="Local Test Recycler",
                operating_status="VERIFIED",
            ))
        await session.commit()
