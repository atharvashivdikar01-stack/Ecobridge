import sys
from pathlib import Path

# Ensure project root is in sys.path when running directly
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import asyncio
import uuid
import hashlib
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.src.core.config import settings
from backend.src.models.base import Base
from backend.src.models.user import User
from backend.src.models.collector import CollectorProfile
from backend.src.models.taxonomy import WasteCategory, Material
from backend.src.models.recycler import RecyclerCompany, RecyclerFacility
from backend.src.models.lot import Lot, LotItem
from backend.src.models.traceability import CustodyEvent
from backend.src.models.payment import RecyclerPayment


async def seed():
    print(f"Connecting to database: {settings.ASYNC_DATABASE_URL}")
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    
    # 1. Create all schema tables
    print("Creating tables in PostgreSQL...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        # Check if already seeded
        existing_collectors = (await session.execute(select(CollectorProfile))).scalars().all()
        if len(existing_collectors) >= 12:
            print(f"Database already contains {len(existing_collectors)} collectors. Truncating / refreshing seed...")
            await session.execute(text("TRUNCATE TABLE recycler_payments, custody_events, lot_items, lots, recycler_facilities, recycler_companies, collector_profiles, materials, waste_categories, users CASCADE;"))
            await session.commit()

        print("Seeding Waste Categories & Materials...")
        cat_pcb = WasteCategory(id=uuid.uuid4(), name="Printed Circuit Boards", code="PCB", description="Multi-layer PCBs and motherboards")
        cat_bat = WasteCategory(id=uuid.uuid4(), name="Batteries", code="BAT", description="Lithium-ion and alkaline cells")
        cat_crt = WasteCategory(id=uuid.uuid4(), name="Glass & Displays", code="CRT", description="Cathode ray tubes and lead glass")
        cat_tel = WasteCategory(id=uuid.uuid4(), name="Telecom Equipment", code="TEL", description="Radio transceivers, relays, copper coils")
        session.add_all([cat_pcb, cat_bat, cat_crt, cat_tel])
        await session.flush()

        mat_server_pcb = Material(id=uuid.uuid4(), category_id=cat_pcb.id, name="High-Grade Server Multi-Layer PCB", code="PCB-SRV", base_unit="KG")
        mat_desktop_pcb = Material(id=uuid.uuid4(), category_id=cat_pcb.id, name="Mid-Grade Desktop Motherboard", code="PCB-DSK", base_unit="KG")
        mat_power_pcb = Material(id=uuid.uuid4(), category_id=cat_pcb.id, name="Low-Grade Power Supply PCB", code="PCB-PWR", base_unit="KG")
        mat_phone_pcb = Material(id=uuid.uuid4(), category_id=cat_pcb.id, name="Gold-Plated Smartphone Logic Board", code="PCB-MOB", base_unit="KG")
        mat_li_pouch = Material(id=uuid.uuid4(), category_id=cat_bat.id, name="Swollen Li-Ion Pouch Cell", code="BAT-LPO", base_unit="KG")
        mat_18650 = Material(id=uuid.uuid4(), category_id=cat_bat.id, name="18650 Cylindrical Battery Module", code="BAT-186", base_unit="KG")
        mat_crt_glass = Material(id=uuid.uuid4(), category_id=cat_crt.id, name="Leaded CRT Funnel Glass", code="CRT-FUN", base_unit="KG")
        mat_copper_wire = Material(id=uuid.uuid4(), category_id=cat_tel.id, name="Telecom Copper Deflection Wire", code="TEL-COP", base_unit="KG")
        mat_relay_unit = Material(id=uuid.uuid4(), category_id=cat_tel.id, name="Telecom Radio Relay Transceiver", code="TEL-RAD", base_unit="KG")

        session.add_all([mat_server_pcb, mat_desktop_pcb, mat_power_pcb, mat_phone_pcb, mat_li_pouch, mat_18650, mat_crt_glass, mat_copper_wire, mat_relay_unit])
        await session.flush()

        # 2. Seed the 12 Collectors
        print("Seeding 12 Informal Collectors...")
        collectors_data = [
            ("Ramesh Kumar", "+919820114201", "Dharavi 13th Compound", Decimal("0.98"), Decimal("34.2"), 6, "AADHAAR"),
            ("Sunita Devi", "+919833091823", "Kurla West E-Cluster", Decimal("0.96"), Decimal("28.5"), 5, "AADHAAR"),
            ("Imran Sheikh", "+919769044109", "Sakinaka Aggregator Guild", Decimal("0.99"), Decimal("42.1"), 7, "VOTER_ID"),
            ("Vijay Mane", "+919819987621", "Chembur Scrap Depot", Decimal("0.94"), Decimal("22.4"), 4, "AADHAAR"),
            ("Rajeshwari P.", "+919821234509", "Bandra Reclamation Guild", Decimal("0.95"), Decimal("19.3"), 3, "PAN"),
            ("Amit Jadhav", "+919702289012", "Goregaon West Hub", Decimal("0.97"), Decimal("26.0"), 4, "AADHAAR"),
            ("Mohammad Arif", "+919892065123", "Govandi Perimeter", Decimal("0.98"), Decimal("31.8"), 5, "AADHAAR"),
            ("Anita Shinde", "+919867012984", "Mulund Aggregator", Decimal("0.93"), Decimal("18.2"), 3, "AADHAAR"),
            ("Santosh Kadam", "+919930078219", "Kalyan Scrap Yard", Decimal("0.92"), Decimal("21.0"), 3, "VOTER_ID"),
            ("Fatima Begum", "+919819167234", "Mankhurd Guild", Decimal("0.94"), Decimal("15.4"), 2, "AADHAAR"),
            ("Ganesh Patil", "+919820590128", "Thane MIDC Wagle", Decimal("0.96"), Decimal("25.1"), 4, "AADHAAR"),
            ("Deepak Chauhan", "+919870034190", "Andheri East Industrial Hub", Decimal("0.99"), Decimal("33.0"), 5, "PAN"),
        ]

        collector_models = []
        for name, phone_num, hub, trust, staged_kg, lots_count, id_type in collectors_data:
            user = User(
                id=uuid.uuid4(),
                phone=phone_num,
                full_name=name,
                role="COLLECTOR",
                status="ACTIVE",
            )
            session.add(user)
            await session.flush()

            profile = CollectorProfile(
                id=uuid.uuid4(),
                user_id=user.id,
                collector_type="INDIVIDUAL_PICKER",
                national_id_type=id_type,
                national_id_number=hub,
                trust_score=trust,
                total_lots_collected=lots_count,
                total_weight_kg=staged_kg,
                verified_at=datetime.now(timezone.utc),
            )
            session.add(profile)
            collector_models.append(profile)

        await session.flush()
        print(f"Created {len(collector_models)} collectors.")

        # 3. Seed the 8 Verified Recyclers
        print("Seeding 8 CPCB-Verified Recyclers...")
        recyclers_data = [
            ("EcoRecycle Maharashtra Pvt Ltd", "CPCB-MH-2024-0891", "Navi Mumbai, TTC Area", Decimal("500.00")),
            ("Western Smelting & Refining Corp", "CPCB-MH-2023-0412", "Taloja MIDC, Raigad", Decimal("800.00")),
            ("GreenTech Circular Alloys Ltd", "CPCB-MH-2024-1102", "Mahape, Navi Mumbai", Decimal("350.00")),
            ("Apex Urban Mining & E-Waste Ltd", "CPCB-MH-2022-0199", "Dombivli MIDC Phase II", Decimal("1000.00")),
            ("MahaEwaste Hydrometallurgical", "CPCB-MH-2024-1422", "Rabale MIDC", Decimal("400.00")),
            ("Phoenix Metallurgical Solutions", "CPCB-MH-2023-0781", "Ambernath Industrial Belt", Decimal("650.00")),
            ("CleanEarth Hydrometallurgy Ltd", "CPCB-MH-2024-0988", "Turbhe MIDC Sector 20", Decimal("250.00")),
            ("Sahyadri Precious Metals Recovery", "CPCB-MH-2023-0301", "Panvel Industrial Zone", Decimal("600.00")),
        ]

        recycler_models = []
        for idx, (cname, cpcb, loc, cap) in enumerate(recyclers_data):
            r_user = User(
                id=uuid.uuid4(),
                phone=f"+91228800{idx:04d}",
                full_name=f"{cname} Authorized Rep",
                role="RECYCLER",
                status="ACTIVE",
            )
            session.add(r_user)
            await session.flush()

            company = RecyclerCompany(
                id=uuid.uuid4(),
                user_id=r_user.id,
                company_name=cname,
                cpcb_registration_no=cpcb,
                operating_status="VERIFIED",
            )
            session.add(company)
            await session.flush()

            facility = RecyclerFacility(
                id=uuid.uuid4(),
                recycler_id=company.id,
                facility_name=f"{cname} Plant 1",
                city=loc.split(",")[0],
                state="Maharashtra",
                daily_capacity_kg=cap,
                accepts_hazardous=True,
            )
            session.add(facility)
            recycler_models.append(company)

        await session.flush()
        print(f"Created {len(recycler_models)} verified recyclers.")

        # 4. Seed the 47 Lots
        # Target:
        # - Exactly 32 lots SETTLED
        # - 15 lots in earlier stages (ACCEPTED, HANDED_OVER, COLLECTED)
        # - Total verified weight of settled lots = EXACTLY 284.000 kg!
        # - Exactly 45 lots with SHA-256 custody events (45/47 = 95.74% ≈ 96% traceable)
        print("Seeding 47 Lots totaling exactly 284 kg formalized volume...")

        # 32 weights that sum up EXACTLY to 284.0 kg
        settled_weights = [
            Decimal("11.2"), Decimal("6.5"), Decimal("17.6"), Decimal("14.2"),
            Decimal("11.8"), Decimal("8.2"), Decimal("14.8"), Decimal("5.0"),
            Decimal("8.8"),  Decimal("7.4"), Decimal("9.6"),  Decimal("6.2"),
            Decimal("11.5"), Decimal("9.0"), Decimal("7.4"),  Decimal("6.0"),
            Decimal("8.0"),  Decimal("7.5"), Decimal("10.0"), Decimal("5.8"),
            Decimal("6.5"),  Decimal("7.0"), Decimal("9.2"),  Decimal("5.4"),
            Decimal("8.2"),  Decimal("6.8"), Decimal("7.6"),  Decimal("8.4"),
            Decimal("6.0"),  Decimal("7.5"), Decimal("9.5"),  Decimal("15.4"),
        ]
        assert sum(settled_weights) == Decimal("284.0"), f"Sum is {sum(settled_weights)}"

        all_materials = [
            mat_server_pcb, mat_li_pouch, mat_crt_glass, mat_copper_wire,
            mat_desktop_pcb, mat_power_pcb, mat_relay_unit, mat_phone_pcb,
            mat_18650, mat_copper_wire, mat_server_pcb, mat_desktop_pcb,
        ]

        lot_models = []
        payments = []

        now = datetime.now(timezone.utc)

        for i in range(1, 48):
            lot_code = f"LOT-2026-{48 - i:03d}"
            collector = collector_models[(i - 1) % len(collector_models)]
            recycler = recycler_models[(i - 1) % len(recycler_models)]
            mat = all_materials[(i - 1) % len(all_materials)]

            is_settled = (i <= 32)
            is_traceable = (i <= 45)  # 45 out of 47 lots = 95.74% ≈ 96%

            if is_settled:
                status = "SETTLED"
                weight = settled_weights[i - 1]
                rate = Decimal(str(450 + (i * 35) % 1200))
                final_val = weight * rate
                slip = f"WB-2026-{9850 - i}"
            elif i <= 38:
                status = "HANDED_OVER"
                weight = Decimal(str(8.0 + (i % 5)))
                rate = Decimal("650.00")
                final_val = weight * rate
                slip = f"WB-2026-{9850 - i}"
            elif i <= 43:
                status = "ACCEPTED"
                weight = Decimal(str(7.0 + (i % 6)))
                rate = Decimal("550.00")
                final_val = weight * rate
                slip = None
            else:
                status = "COLLECTED"
                weight = Decimal(str(6.0 + (i % 7)))
                rate = Decimal("400.00")
                final_val = weight * rate
                slip = None

            lot = Lot(
                id=uuid.uuid4(),
                lot_code=lot_code,
                collector_id=collector.id,
                status=status,
                total_estimated_weight_kg=weight,
                total_verified_weight_kg=weight if is_settled else (weight if status == "HANDED_OVER" else None),
                estimated_value=final_val,
                final_value=final_val if is_settled else None,
                agreed_price_per_kg=rate if status != "COLLECTED" else None,
                weighbridge_slip_number=slip,
                origin_address=collector.national_id_number,
                offline_created_at=now - timedelta(hours=i * 2),
                synced_at=now - timedelta(hours=i * 2 - 1),
            )
            session.add(lot)
            await session.flush()

            # Add primary lot item
            detected_hazard = "SWOLLEN_BATTERY" if "BAT" in mat.code else ("BROKEN_CRT_LEAD" if "CRT" in mat.code else "NORMAL")
            item = LotItem(
                id=uuid.uuid4(),
                lot_id=lot.id,
                material_id=mat.id,
                quantity=1,
                unit="KG",
                estimated_weight_kg=weight,
                verified_weight_kg=weight if is_settled else None,
                ai_confidence_score=Decimal(str(0.92 + ((i * 3) % 8) / 100)),
                detected_hazard=detected_hazard,
                unit_price_estimated=rate,
                unit_price_verified=rate if is_settled else None,
                subtotal_estimated=final_val,
                subtotal_final=final_val if is_settled else None,
            )
            session.add(item)

            # Add Cryptographic Custody Event if traceable
            if is_traceable:
                event_hash = hashlib.sha256(f"{lot_code}:{weight}:{rate}:{slip}".encode()).hexdigest()
                event = CustodyEvent(
                    id=uuid.uuid4(),
                    lot_id=lot.id,
                    sequence_number=1,
                    event_type=f"STATUS_{status}",
                    actor_id=recycler.id if is_settled else collector.id,
                    actor_role="RECYCLER" if is_settled else "COLLECTOR",
                    event_timestamp=now - timedelta(hours=i * 2),
                    event_payload_json={"lot_code": lot_code, "weight_kg": float(weight), "weighbridge_slip": slip},
                    previous_event_hash="0" * 64,
                    current_event_hash=event_hash,
                )
                session.add(event)

            # If settled, add RecyclerPayment
            if is_settled:
                pay_method = "IMMEDIATE_UPI" if (i % 2 == 0) else "WEIGHBRIDGE_CASH"
                payment_hash = hashlib.sha256(f"PAYMENT:{lot_code}:{final_val}:{slip}".encode()).hexdigest()
                pmt = RecyclerPayment(
                    id=uuid.uuid4(),
                    lot_id=lot.id,
                    recycler_id=recycler.id,
                    payment_method=pay_method,
                    payment_status="PAID",
                    total_amount=final_val,
                    gateway_reference=f"TXN-2026-{33 - i:03d}",
                    weighbridge_slip=slip or f"WB-SLIP-{i}",
                    custody_hash=payment_hash,
                )
                session.add(pmt)
                payments.append(pmt)

            lot_models.append(lot)

        await session.commit()
        print(f"Successfully seeded:")
        print(f" - Collectors: {len(collector_models)}")
        print(f" - Recyclers: {len(recycler_models)}")
        print(f" - Lots: {len(lot_models)}")
        print(f" - Settled Payments: {len(payments)}")
        print(f" - Formalized Volume: {sum(settled_weights)} kg")
        print("SEEDING COMPLETE!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
