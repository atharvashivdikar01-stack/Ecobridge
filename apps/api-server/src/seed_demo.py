"""ECOBRIDGE Demo Seed Script.
Populates realistic seed data for the Recycler Portal:
- Waste categories and benchmark materials
- CPCB-verified recycler company & facility (EcoGreen Recyclers)
- Unverified recycler company (Pending Scrap Co.)
- Active collector profile (Raju Shinde)
- Staged e-waste lots across all lifecycle stages:
  * Available lots (with AI classifications, confidence, photos, and safety alerts)
  * Offer Accepted lot (awaiting scale handover)
  * Handed Over lot (weighed at scale, awaiting payment)
  * Completed Cash Transaction in ledger
  * Completed Digital UPI Transaction in ledger
"""

import asyncio
import hashlib
import json
import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .core.database import async_engine, AsyncSessionFactory
from .models import (
    Base,
    User,
    CollectorProfile,
    WasteCategory,
    Material,
    MaterialPriceBand,
    RecyclerCompany,
    RecyclerFacility,
    AuthorizationRecord,
    RecyclerAcceptedMaterial,
    Lot,
    LotItem,
    LotImage,
    CustodyEvent,
    RecyclerOffer,
    Handover,
    Transaction,
)


async def seed_database():
    print("🌱 Initializing database schema...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionFactory() as session:
        # Check if already seeded
        existing_cat = await session.execute(select(WasteCategory))
        if existing_cat.scalars().first():
            print("Database already contains seed taxonomy. Ensuring demo lots and recyclers exist...")
        else:
            print("Creating Waste Categories & Materials...")
            # 1. Categories
            cat_it = WasteCategory(
                code="CAT_ITEW",
                name="IT & Telecom Equipment",
                description="Servers, laptops, smartphones, networking equipment, and high-value PCBs.",
                default_hazard="WARNING",
            )
            cat_ce = WasteCategory(
                code="CAT_CEEW",
                name="Consumer Electronics",
                description="Televisions, CRT displays, audio equipment, household electronics.",
                default_hazard="WARNING",
            )
            cat_batt = WasteCategory(
                code="CAT_BATT",
                name="Batteries & Energy Storage",
                description="Lithium-ion batteries, lead-acid cells, pouch packs.",
                default_hazard="DANGER",
            )
            cat_comp = WasteCategory(
                code="CAT_COMP",
                name="Separated Metal Components",
                description="Copper yokes, windings, heatsinks, chassis.",
                default_hazard="INFO",
            )
            session.add_all([cat_it, cat_ce, cat_batt, cat_comp])
            await session.flush()

            # 2. Materials
            now_utc = datetime.now(timezone.utc)
            m_server_pcb = Material(
                category_id=cat_it.id,
                code="PCB_SERVER_GRADE_A",
                name="Server Motherboard Grade A",
                description="Dual-socket gold-plated server motherboards with high precious metal yield.",
                base_unit="KG",
            )
            m_pc_pcb = Material(
                category_id=cat_it.id,
                code="PCB_PC_GRADE_B",
                name="Laptop & PC Motherboards",
                description="Consumer-grade computing logic boards.",
                base_unit="KG",
            )
            m_phone_pcb = Material(
                category_id=cat_it.id,
                code="SMARTPHONE_LOGIC_BOARD",
                name="Smartphone Logic Boards Grade A+",
                description="High-density multilayer boards from smartphones.",
                base_unit="KG",
            )
            m_crt = Material(
                category_id=cat_ce.id,
                code="CRT_MONITOR_LEADED",
                name="Leaded CRT Display Units",
                description="Cathode ray tubes containing funnel leaded glass.",
                base_unit="KG",
                requires_permit=True,
            )
            m_consumer_pcb = Material(
                category_id=cat_ce.id,
                code="PCB_CONSUMER_GRADE_C",
                name="Consumer Brown Single-Sided PCBs",
                description="Phenolic resin boards from home appliances.",
                base_unit="KG",
            )
            m_batt_li = Material(
                category_id=cat_batt.id,
                code="BATT_LI_ION_POUCH",
                name="Lithium-Ion Pouch Batteries",
                description="Rechargeable Li-ion batteries requiring specialized hazard handling.",
                base_unit="KG",
                requires_permit=True,
            )
            m_copper_yoke = Material(
                category_id=cat_comp.id,
                code="COPPER_TRANSFORMER_YOKE",
                name="High-Purity Copper Deflection Yokes",
                description="Stripped clean electrolytic copper windings.",
                base_unit="KG",
            )
            session.add_all([m_server_pcb, m_pc_pcb, m_phone_pcb, m_crt, m_consumer_pcb, m_batt_li, m_copper_yoke])
            await session.flush()

            # Price bands
            bands = [
                MaterialPriceBand(material_id=m_server_pcb.id, grade="GRADE_A", min_price_per_unit=Decimal("1100.00"), max_price_per_unit=Decimal("1600.00"), benchmark_price_per_unit=Decimal("1350.00"), effective_from=now_utc),
                MaterialPriceBand(material_id=m_pc_pcb.id, grade="GRADE_B", min_price_per_unit=Decimal("420.00"), max_price_per_unit=Decimal("680.00"), benchmark_price_per_unit=Decimal("550.00"), effective_from=now_utc),
                MaterialPriceBand(material_id=m_phone_pcb.id, grade="GRADE_A_PLUS", min_price_per_unit=Decimal("1500.00"), max_price_per_unit=Decimal("2200.00"), benchmark_price_per_unit=Decimal("1850.00"), effective_from=now_utc),
                MaterialPriceBand(material_id=m_crt.id, grade="STANDARD", min_price_per_unit=Decimal("30.00"), max_price_per_unit=Decimal("60.00"), benchmark_price_per_unit=Decimal("45.00"), effective_from=now_utc),
                MaterialPriceBand(material_id=m_consumer_pcb.id, grade="GRADE_C", min_price_per_unit=Decimal("80.00"), max_price_per_unit=Decimal("160.00"), benchmark_price_per_unit=Decimal("120.00"), effective_from=now_utc),
                MaterialPriceBand(material_id=m_batt_li.id, grade="HAZARDOUS", min_price_per_unit=Decimal("220.00"), max_price_per_unit=Decimal("350.00"), benchmark_price_per_unit=Decimal("280.00"), effective_from=now_utc),
                MaterialPriceBand(material_id=m_copper_yoke.id, grade="HIGH_PURITY", min_price_per_unit=Decimal("520.00"), max_price_per_unit=Decimal("720.00"), benchmark_price_per_unit=Decimal("620.00"), effective_from=now_utc),
            ]
            session.add_all(bands)
            await session.commit()

        # Fetch materials for lot creation
        m_server = (await session.execute(select(Material).where(Material.code == "PCB_SERVER_GRADE_A"))).scalar_one()
        m_batt = (await session.execute(select(Material).where(Material.code == "BATT_LI_ION_POUCH"))).scalar_one()
        m_phone = (await session.execute(select(Material).where(Material.code == "SMARTPHONE_LOGIC_BOARD"))).scalar_one()
        m_pc = (await session.execute(select(Material).where(Material.code == "PCB_PC_GRADE_B"))).scalar_one()
        m_cu = (await session.execute(select(Material).where(Material.code == "COPPER_TRANSFORMER_YOKE"))).scalar_one()

        print("Checking / creating verified & unverified recycler accounts...")
        # 1. Verified Recycler (EcoGreen E-Waste Recyclers)
        rec_res = await session.execute(select(User).where(User.phone == "+919811111111"))
        rec_user = rec_res.scalar_one_or_none()
        if not rec_user:
            rec_user = User(
                phone="+919811111111",
                full_name="Ravi Patel (Operations Head)",
                email="ravi@ecogreenrecyclers.in",
                role="RECYCLER_ADMIN",
                status="ACTIVE",
            )
            session.add(rec_user)
            await session.flush()

        comp_res = await session.execute(select(RecyclerCompany).where(RecyclerCompany.user_id == rec_user.id))
        verified_company = comp_res.scalar_one_or_none()
        if not verified_company:
            verified_company = RecyclerCompany(
                user_id=rec_user.id,
                company_name="EcoGreen E-Waste Recyclers Pvt Ltd",
                trade_license_number="TL-MUM-2026-9999",
                gst_number="27AAACE1234F1Z5",
                cpcb_registration_no="CPCB/EW/2026/001",
                contact_person="Ravi Patel",
                contact_phone="+919811111111",
                contact_email="ravi@ecogreenrecyclers.in",
                operating_status="VERIFIED",
                verified_at=datetime.now(timezone.utc),
            )
            session.add(verified_company)
            await session.flush()

            primary_fac = RecyclerFacility(
                recycler_id=verified_company.id,
                facility_name="Taloja MIDC Advanced Dismantling Plant",
                address_line1="Plot 42, Sector 8, Taloja MIDC Industrial Zone",
                city="Navi Mumbai",
                state="Maharashtra",
                postal_code="410208",
                latitude=Decimal("19.06570000"),
                longitude=Decimal("73.12560000"),
                daily_capacity_kg=Decimal("10000.00"),
                accepts_hazardous=True,
                is_active=True,
                pickup_available=True,
                min_pickup_weight_kg=Decimal("50.00"),
            )
            session.add(primary_fac)
            await session.flush()

            auth_rec = AuthorizationRecord(
                facility_id=primary_fac.id,
                authority_name="Central Pollution Control Board (CPCB)",
                permit_type="E_WASTE_RECYCLER",
                permit_number="CPCB/EWR/MH/2026/089",
                authorized_capacity_mta=Decimal("3500.00"),
                issued_date=datetime(2024, 1, 1).date(),
                expiry_date=datetime(2029, 12, 31).date(),
                status="ACTIVE",
            )
            session.add(auth_rec)
            await session.commit()

        # 2. Unverified Recycler (Pending Scrap Co.)
        unv_res = await session.execute(select(User).where(User.phone == "+919822222222"))
        unv_user = unv_res.scalar_one_or_none()
        if not unv_user:
            unv_user = User(
                phone="+919822222222",
                full_name="Vikram Shah",
                email="vikram@pendingscrap.in",
                role="RECYCLER_ADMIN",
                status="ACTIVE",
            )
            session.add(unv_user)
            await session.flush()

            unv_company = RecyclerCompany(
                user_id=unv_user.id,
                company_name="Pending Scrap & Dismantling Co.",
                trade_license_number="TL-PUN-2026-1044",
                cpcb_registration_no="CPCB/EW/2026/PENDING-99",
                contact_person="Vikram Shah",
                contact_phone="+919822222222",
                operating_status="PENDING_VERIFICATION",
            )
            session.add(unv_company)
            await session.commit()

        # 3. Collector (Raju Shinde)
        col_res = await session.execute(select(User).where(User.phone == "+919800000001"))
        col_user = col_res.scalar_one_or_none()
        if not col_user:
            col_user = User(
                phone="+919800000001",
                full_name="Raju Shinde (Kabadiwala)",
                role="COLLECTOR",
                status="ACTIVE",
                preferred_language="hi",
            )
            session.add(col_user)
            await session.flush()

            collector_profile = CollectorProfile(
                user_id=col_user.id,
                collector_type="INDIVIDUAL_PICKER",
                trust_score=Decimal("4.85"),
                total_lots_collected=24,
                total_weight_kg=Decimal("1850.500"),
            )
            session.add(collector_profile)
            await session.commit()
        else:
            collector_profile = (
                await session.execute(select(CollectorProfile).where(CollectorProfile.user_id == col_user.id))
            ).scalar_one()

        # Check existing lots
        existing_lots = await session.execute(select(Lot))
        if existing_lots.scalars().first():
            print("Lots already exist. Demo seeding complete!")
            return

        print("Generating realistic demo lots across full lifecycle...")
        now = datetime.now(timezone.utc)

        # Helper to create lot with items, image, and initial custody hash
        async def make_lot(
            lot_code: str,
            mat: Material,
            weight_kg: float,
            status_str: str,
            hazard: str,
            ai_conf: float,
            address: str,
            lat: float,
            lng: float,
            img_url: str,
            benchmark_rate: float,
            agreed_rate: Optional[float] = None,
            verified_weight: Optional[float] = None,
        ) -> Lot:
            weight_dec = Decimal(str(weight_kg))
            bench_dec = Decimal(str(benchmark_rate))
            subtotal_est = Decimal(str(round(float(weight_dec * bench_dec), 2)))

            final_val_dec = None
            if agreed_rate and verified_weight:
                final_val_dec = Decimal(str(round(float(Decimal(str(verified_weight)) * Decimal(str(agreed_rate))), 2)))
            elif agreed_rate:
                final_val_dec = Decimal(str(round(float(weight_dec * Decimal(str(agreed_rate))), 2)))

            lot = Lot(
                lot_code=lot_code,
                collector_id=collector_profile.id,
                status=status_str,
                total_estimated_weight_kg=weight_dec,
                total_verified_weight_kg=Decimal(str(verified_weight)) if verified_weight else None,
                estimated_value=subtotal_est,
                final_value=final_val_dec,
                currency="INR",
                origin_latitude=Decimal(str(lat)),
                origin_longitude=Decimal(str(lng)),
                origin_address=address,
                offline_created_at=now - timedelta(hours=4),
                synced_at=now - timedelta(hours=3),
            )
            session.add(lot)
            await session.flush()

            item = LotItem(
                lot_id=lot.id,
                material_id=mat.id,
                quantity=1,
                unit="KG",
                estimated_weight_kg=weight_dec,
                verified_weight_kg=Decimal(str(verified_weight)) if verified_weight else None,
                ai_confidence_score=Decimal(str(ai_conf)),
                detected_hazard=hazard,
                unit_price_estimated=bench_dec,
                unit_price_verified=Decimal(str(agreed_rate)) if agreed_rate else None,
                subtotal_estimated=subtotal_est,
                subtotal_final=final_val_dec,
            )
            session.add(item)

            img_hash = hashlib.sha256(f"{lot_code}:{img_url}".encode("utf-8")).hexdigest()
            img = LotImage(
                lot_id=lot.id,
                image_url=img_url,
                image_hash=img_hash,
                captured_at=now - timedelta(hours=4),
                is_proof_of_collection=True,
            )
            session.add(img)

            # Genesis custody event
            gen_hash = "0" * 64
            payload = {"lot_code": lot_code, "weight_kg": float(weight_dec), "status": status_str}
            ser = json.dumps(payload, sort_keys=True)
            cur_hash = hashlib.sha256(f"{gen_hash}:{lot.id}:{col_user.id}:CREATION:{ser}".encode("utf-8")).hexdigest()

            evt = CustodyEvent(
                lot_id=lot.id,
                sequence_number=1,
                event_type="CREATION",
                actor_id=col_user.id,
                actor_role="COLLECTOR",
                event_timestamp=now - timedelta(hours=4),
                event_payload_json=payload,
                previous_event_hash=gen_hash,
                current_event_hash=cur_hash,
            )
            session.add(evt)
            return lot

        # 1. Available: Server PCBs
        await make_lot(
            lot_code="EB-202609-1001",
            mat=m_server,
            weight_kg=42.500,
            status_str="COLLECTED",
            hazard="NORMAL",
            ai_conf=0.942,
            address="Dharavi 13th Compound E-Waste Yard, Mumbai",
            lat=19.0434,
            lng=72.8570,
            img_url="https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
            benchmark_rate=1350.0,
        )

        # 2. Available (Hazardous): Swollen Li-ion batteries
        await make_lot(
            lot_code="EB-202609-1002",
            mat=m_batt,
            weight_kg=18.200,
            status_str="COLLECTED",
            hazard="SWOLLEN_BATTERY",
            ai_conf=0.897,
            address="Kurla Scrap Aggregation Shed 4, Mumbai",
            lat=19.0688,
            lng=72.8790,
            img_url="https://images.unsplash.com/photo-1619725002198-6a689b72f41d?w=800&auto=format&fit=crop&q=80",
            benchmark_rate=280.0,
        )

        # 3. Available: Smartphone PCBs
        await make_lot(
            lot_code="EB-202609-1003",
            mat=m_phone,
            weight_kg=12.800,
            status_str="COLLECTED",
            hazard="NORMAL",
            ai_conf=0.961,
            address="Andheri East MIDC Aggregator Centre, Mumbai",
            lat=19.1136,
            lng=72.8697,
            img_url="https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800&auto=format&fit=crop&q=80",
            benchmark_rate=1850.0,
        )

        # 4. Offer Accepted: PC/Laptop PCBs (Awaiting Scale Handover)
        lot4 = await make_lot(
            lot_code="EB-202609-1004",
            mat=m_pc,
            weight_kg=65.000,
            status_str="ACCEPTED",
            hazard="NORMAL",
            ai_conf=0.925,
            address="Bhiwandi Warehouse Cluster, Thane",
            lat=19.2967,
            lng=73.0631,
            img_url="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&auto=format&fit=crop&q=80",
            benchmark_rate=550.0,
            agreed_rate=560.0,
        )
        # Add Offer record
        offer4 = RecyclerOffer(
            lot_id=lot4.id,
            recycler_id=verified_company.id,
            recycler_name=verified_company.company_name,
            offered_price_per_unit=Decimal("560.00"),
            offered_total_price=Decimal("36400.00"),
            pickup_cost_deduction=Decimal("0.00"),
            net_collector_earning=Decimal("36400.00"),
            status="ACCEPTED",
            expires_at=now + timedelta(days=2),
        )
        session.add(offer4)

        # 5. Handed Over: Copper Deflection Yokes (Scale Weighed, Pending Payment)
        lot5 = await make_lot(
            lot_code="EB-202609-1005",
            mat=m_cu,
            weight_kg=85.000,
            status_str="HANDED_OVER",
            hazard="NORMAL",
            ai_conf=0.950,
            address="Taloja MIDC Plant Gate Inward, Navi Mumbai",
            lat=19.0657,
            lng=73.1256,
            img_url="https://images.unsplash.com/photo-1605371924599-2d0365da1ae0?w=800&auto=format&fit=crop&q=80",
            benchmark_rate=620.0,
            agreed_rate=615.0,
            verified_weight=84.500,
        )
        fac_res = await session.execute(select(RecyclerFacility).where(RecyclerFacility.recycler_id == verified_company.id))
        fac = fac_res.scalars().first()
        fac_id = fac.id if fac else None

        ho5 = Handover(
            lot_id=lot5.id,
            facility_id=fac_id,
            recycler_id=verified_company.id,
            collector_id=collector_profile.id,
            handover_type="COLLECTOR_TO_FACILITY",
            weighbridge_slip_number="WB-TALOJA-2026-8812",
            weighbridge_gross_kg=Decimal("124.500"),
            weighbridge_tare_kg=Decimal("40.000"),
            weighbridge_net_kg=Decimal("84.500"),
            status="COMPLETED",
            handed_over_at=now - timedelta(hours=1),
        )
        session.add(ho5)

        # 6. Completed Cash Transaction in Ledger
        lot6 = await make_lot(
            lot_code="EB-202609-1006",
            mat=m_server,
            weight_kg=55.000,
            status_str="SETTLED",
            hazard="NORMAL",
            ai_conf=0.978,
            address="Taloja Processing Unit 1",
            lat=19.0657,
            lng=73.1256,
            img_url="https://images.unsplash.com/photo-1597733336794-12d05021d510?w=800&auto=format&fit=crop&q=80",
            benchmark_rate=1350.0,
            agreed_rate=1380.0,
            verified_weight=55.000,
        )
        ho6 = Handover(
            lot_id=lot6.id,
            facility_id=fac_id,
            recycler_id=verified_company.id,
            collector_id=collector_profile.id,
            handover_type="COLLECTOR_TO_FACILITY",
            weighbridge_slip_number="WB-TALOJA-2026-7491",
            weighbridge_gross_kg=Decimal("95.000"),
            weighbridge_tare_kg=Decimal("40.000"),
            weighbridge_net_kg=Decimal("55.000"),
            status="COMPLETED",
            handed_over_at=now - timedelta(days=1),
        )
        session.add(ho6)
        tx6 = Transaction(
            reference_number="EB-CASH-20260921-44192",
            transaction_type="COLLECTOR_PAYOUT",
            lot_id=lot6.id,
            recycler_id=verified_company.id,
            collector_id=collector_profile.id,
            material_name=m_server.name,
            verified_weight_kg=Decimal("55.000"),
            agreed_price_per_kg=Decimal("1380.00"),
            amount=Decimal("75900.00"),  # 55 x 1380
            payment_method="CASH",
            payment_status="PAID",
            gateway_reference="CASH-VOUCHER-TAL-9941",
            status="SETTLED",
            settled_at=now - timedelta(days=1),
        )
        session.add(tx6)

        # 7. Completed Digital UPI Transaction in Ledger
        lot7 = await make_lot(
            lot_code="EB-202609-1007",
            mat=m_phone,
            weight_kg=25.000,
            status_str="SETTLED",
            hazard="NORMAL",
            ai_conf=0.965,
            address="Taloja Processing Unit 1",
            lat=19.0657,
            lng=73.1256,
            img_url="https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800&auto=format&fit=crop&q=80",
            benchmark_rate=1850.0,
            agreed_rate=1820.0,
            verified_weight=25.000,
        )
        ho7 = Handover(
            lot_id=lot7.id,
            facility_id=fac_id,
            recycler_id=verified_company.id,
            collector_id=collector_profile.id,
            handover_type="COLLECTOR_TO_FACILITY",
            weighbridge_slip_number="WB-TALOJA-2026-6102",
            weighbridge_gross_kg=Decimal("45.000"),
            weighbridge_tare_kg=Decimal("20.000"),
            weighbridge_net_kg=Decimal("25.000"),
            status="COMPLETED",
            handed_over_at=now - timedelta(days=2),
        )
        session.add(ho7)
        tx7 = Transaction(
            reference_number="EB-DIGITAL-20260920-81920",
            transaction_type="COLLECTOR_PAYOUT",
            lot_id=lot7.id,
            recycler_id=verified_company.id,
            collector_id=collector_profile.id,
            material_name=m_phone.name,
            verified_weight_kg=Decimal("25.000"),
            agreed_price_per_kg=Decimal("1820.00"),
            amount=Decimal("45500.00"),  # 25 x 1820
            payment_method="UPI",
            payment_status="PAID",
            gateway_reference="UPI/428819208491/RAJU-SHINDE",
            status="SETTLED",
            settled_at=now - timedelta(days=2),
        )
        session.add(tx7)

        await session.commit()
        print("🎉 Demo data seeding successfully finished!")


if __name__ == "__main__":
    asyncio.run(seed_database())
