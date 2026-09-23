"""Create an isolated SQLite database with the mobile app's material catalog."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from src.core.database import SessionLocal, engine
from src.models import Base, Material, MaterialPriceBand, RecyclerCompany, User, WasteCategory


MATERIALS = {
    "Copper": 435.0,
    "Aluminium": 155.0,
    "Iron": 35.0,
    "Printed Circuit Board (PCB)": 347.5,
    "Mobile Phone": 300.0,
    "Computer / Laptop": 370.0,
    "Cables & Wire": 195.0,
    "Batteries": 105.0,
    "Mixed E-Waste": 82.5,
    "Other Scrap": 45.0,
}
LOCAL_RECYCLER_ID = uuid.UUID("00000000-0000-0000-0000-000000000101")


async def main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        category = (await session.execute(
            select(WasteCategory).where(WasteCategory.code == "GENERAL_EWASTE")
        )).scalar_one_or_none()
        if category is None:
            category = WasteCategory(
                code="GENERAL_EWASTE", name="E-Waste", description="Local development catalog"
            )
            session.add(category)
            await session.flush()

        for name, rate in MATERIALS.items():
            material = (await session.execute(
                select(Material).where(Material.name == name)
            )).scalar_one_or_none()
            if material is None:
                material = Material(
                    category_id=category.id,
                    code=name.upper().replace(" ", "_").replace("/", "_"),
                    name=name,
                )
                session.add(material)
                await session.flush()
                session.add(MaterialPriceBand(
                    material_id=material.id,
                    grade="LOCAL_DEV",
                    min_price_per_unit=rate,
                    max_price_per_unit=rate,
                    benchmark_price_per_unit=rate,
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

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
