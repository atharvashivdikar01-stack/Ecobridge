import uuid
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta
import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.models import (
    User,
    CollectorProfile,
    WasteCategory,
    Material,
    MaterialPriceBand,
    Lot,
    LotItem,
    RecyclerCompany,
    RecyclerFacility,
    AuthorizationRecord,
    RecyclerAcceptedMaterial,
)
from src.core.security import create_access_token


@pytest_asyncio.fixture
async def seed_matching_environment(init_test_db):
    """Seed materials, collector profile, and two distinct recyclers with varying pickup/hazard profiles."""
    from tests.conftest import TestSessionFactory

    async with TestSessionFactory() as session:
        # 1. Taxonomy & Materials
        cat = WasteCategory(
            code="CAT_ITEW",
            name="IT Equipment",
            description="Laptops, motherboards, batteries",
            default_hazard="WARNING",
        )
        session.add(cat)
        await session.flush()

        # Material 1: Standard PCB
        mat_pcb = Material(
            category_id=cat.id,
            code="PCB_SERVER_GRADE_A",
            name="Server Motherboard Grade A",
            base_unit="KG",
        )
        session.add(mat_pcb)

        # Material 2: Li-Ion Battery (Hazardous)
        mat_batt = Material(
            category_id=cat.id,
            code="BATT_LI_ION_POUCH",
            name="Lithium-Ion Pouch Battery",
            base_unit="KG",
        )
        session.add(mat_batt)
        await session.flush()

        # 2. Collector & Staged Lot at Mumbai (19.0760, 72.8777)
        collector_user = User(
            phone="+919811119999",
            full_name="Rajesh Aggregator",
            role="COLLECTOR",
            status="ACTIVE",
        )
        session.add(collector_user)
        await session.flush()

        prof = CollectorProfile(
            user_id=collector_user.id,
            collector_type="SCRAP_AGGREGATOR",
            verified_at=datetime.now(timezone.utc),
        )
        session.add(prof)
        await session.flush()

        # Lot with 10kg PCB (Normal)
        lot_normal = Lot(
            collector_id=prof.id,
            lot_code="EB-MATCH-NORM-01",
            origin_latitude=Decimal("19.0760"),
            origin_longitude=Decimal("72.8777"),
            origin_address="Kurla Scrap Market, Mumbai",
            total_estimated_weight_kg=Decimal("10.000"),
            estimated_value=Decimal("14000.00"),
            currency="INR",
            offline_created_at=datetime.now(timezone.utc),
        )
        session.add(lot_normal)
        await session.flush()

        item_pcb = LotItem(
            lot_id=lot_normal.id,
            material_id=mat_pcb.id,
            quantity=1,
            unit="KG",
            estimated_weight_kg=Decimal("10.000"),
            unit_price_estimated=Decimal("1400.00"),
            subtotal_estimated=Decimal("14000.00"),
            detected_hazard="NORMAL",
        )
        session.add(item_pcb)

        # Lot with 10kg Swollen Battery (Hazardous)
        lot_hazardous = Lot(
            collector_id=prof.id,
            lot_code="EB-MATCH-HAZ-02",
            origin_latitude=Decimal("19.0760"),
            origin_longitude=Decimal("72.8777"),
            origin_address="Kurla Scrap Market, Mumbai",
            total_estimated_weight_kg=Decimal("10.000"),
            estimated_value=Decimal("4000.00"),
            currency="INR",
            offline_created_at=datetime.now(timezone.utc),
        )
        session.add(lot_hazardous)
        await session.flush()

        item_batt = LotItem(
            lot_id=lot_hazardous.id,
            material_id=mat_batt.id,
            quantity=1,
            unit="KG",
            estimated_weight_kg=Decimal("10.000"),
            unit_price_estimated=Decimal("400.00"),
            subtotal_estimated=Decimal("4000.00"),
            detected_hazard="SWOLLEN_BATTERY",
        )
        session.add(item_batt)

        # 3. Recycler A (CleanEarth):
        # Located in Navi Mumbai (~15 km away). Offers ₹1400/kg.
        # Pickup available (free <= 25km). Net = 1400 * 10 - 0 = ₹14,000.
        # Certified for hazardous waste with active CPCB permit.
        user_a = User(phone="+919811119901", full_name="Admin A", role="RECYCLER_ADMIN", status="ACTIVE")
        session.add(user_a)
        await session.flush()

        comp_a = RecyclerCompany(
            user_id=user_a.id,
            company_name="CleanEarth E-Waste Solutions",
            trade_license_number="TL-CE-2026-01",
            cpcb_registration_no="CPCB-CE-001",
            contact_person="Ramesh Gupta",
            contact_phone="+919811119901",
            operating_status="VERIFIED",
        )
        session.add(comp_a)
        await session.flush()

        fac_a = RecyclerFacility(
            recycler_id=comp_a.id,
            facility_name="Navi Mumbai Green Hub",
            address_line1="MIDC Turbhe",
            city="Navi Mumbai",
            state="Maharashtra",
            postal_code="400705",
            latitude=Decimal("19.0800"),
            longitude=Decimal("73.0100"),  # ~14 km from (19.0760, 72.8777)
            accepts_hazardous=True,
            pickup_available=True,
            min_pickup_weight_kg=Decimal("5.00"),
            max_pickup_distance_km=Decimal("50.00"),
            lead_time_hours=24,
            is_active=True,
        )
        session.add(fac_a)
        await session.flush()

        # Auth for Recycler A
        auth_a = AuthorizationRecord(
            facility_id=fac_a.id,
            authority_name="CPCB",
            permit_type="HAZARDOUS_WASTE_AUTHORIZATION",
            permit_number="CPCB-HAZ-2026-99",
            issued_date=date(2026, 1, 1),
            expiry_date=date(2030, 1, 1),
            status="ACTIVE",
        )
        session.add(auth_a)

        # Accepted materials for Recycler A
        acc_a1 = RecyclerAcceptedMaterial(
            facility_id=fac_a.id,
            material_id=mat_pcb.id,
            standard_rate_per_unit=Decimal("1400.00"),
            is_active=True,
        )
        acc_a2 = RecyclerAcceptedMaterial(
            facility_id=fac_a.id,
            material_id=mat_batt.id,
            standard_rate_per_unit=Decimal("450.00"),
            is_active=True,
        )
        session.add_all([acc_a1, acc_a2])

        # 4. Recycler B (SuratMetals):
        # Located in Pune (~120 km away). Offers ₹1420/kg (slightly higher nominal rate).
        # Pickup NOT available (requires self-transport).
        # Transport cost = 150 + (120 * 12) + (10 * 1.5) = ₹1,605.
        # Net = 14200 - 1605 = ₹12,595 (Lower than Recycler A!).
        # Does NOT accept hazardous materials.
        user_b = User(phone="+919811119902", full_name="Admin B", role="RECYCLER_ADMIN", status="ACTIVE")
        session.add(user_b)
        await session.flush()

        comp_b = RecyclerCompany(
            user_id=user_b.id,
            company_name="Surat Precious Metals Ltd",
            trade_license_number="TL-SPM-2026-02",
            cpcb_registration_no="CPCB-SPM-002",
            contact_person="Kishore Shah",
            contact_phone="+919811119902",
            operating_status="VERIFIED",
        )
        session.add(comp_b)
        await session.flush()

        fac_b = RecyclerFacility(
            recycler_id=comp_b.id,
            facility_name="Pune Extraction Facility",
            address_line1="Bhosari MIDC",
            city="Pune",
            state="Maharashtra",
            postal_code="411026",
            latitude=Decimal("18.6279"),
            longitude=Decimal("73.8344"),  # ~115 km from Mumbai
            accepts_hazardous=False,
            pickup_available=False,
            lead_time_hours=48,
            is_active=True,
        )
        session.add(fac_b)
        await session.flush()

        acc_b1 = RecyclerAcceptedMaterial(
            facility_id=fac_b.id,
            material_id=mat_pcb.id,
            standard_rate_per_unit=Decimal("1420.00"),
            is_active=True,
        )
        session.add(acc_b1)

        await session.commit()

        return {
            "lot_normal_id": str(lot_normal.id),
            "lot_hazardous_id": str(lot_hazardous.id),
            "mat_pcb_id": str(mat_pcb.id),
            "mat_batt_id": str(mat_batt.id),
            "fac_a_id": str(fac_a.id),
            "fac_b_id": str(fac_b.id),
        }


@pytest.mark.asyncio
async def test_lot_matching_ranking_by_net_earnings(client: AsyncClient, seed_matching_environment):
    """Verify that Recycler A is ranked #1 because net earnings are higher due to free pickup."""
    lot_id = seed_matching_environment["lot_normal_id"]

    response = await client.post(f"/api/v1/matching/lots/{lot_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]

    assert data["lot_id"] == lot_id
    assert data["total_weight_kg"] == 10.0
    assert data["has_hazardous_items"] is False
    assert data["eligible_matches_count"] >= 2

    # Best match must be Recycler A (CleanEarth)
    best = data["best_match"]
    assert best is not None
    assert best["company_name"] == "CleanEarth E-Waste Solutions"
    assert best["rank"] == 1
    assert best["financial"]["gross_payout"] == 14000.0
    assert best["financial"]["transport_cost"] == 0.0  # Free pickup within 25km
    assert best["financial"]["net_collector_earnings"] == 14000.0
    assert best["logistics"]["pickup_mode"] == "FREE_RECYCLER_PICKUP"

    # Candidate 2 is Recycler B (Surat Precious Metals)
    cand2 = data["recommendations"][1]
    assert cand2["company_name"] == "Surat Precious Metals Ltd"
    assert cand2["rank"] == 2
    assert cand2["financial"]["gross_payout"] == 14200.0  # Higher gross
    assert cand2["financial"]["transport_cost"] > 1000.0   # But transport cost erodes profit
    assert cand2["financial"]["net_collector_earnings"] < best["financial"]["net_collector_earnings"]
    assert cand2["logistics"]["pickup_mode"] == "COLLECTOR_SELF_TRANSPORT"


@pytest.mark.asyncio
async def test_hazard_disqualification(client: AsyncClient, seed_matching_environment):
    """Verify that facilities lacking hazardous authorization are disqualified with explicit warnings."""
    lot_id = seed_matching_environment["lot_hazardous_id"]

    response = await client.post(f"/api/v1/matching/lots/{lot_id}")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["has_hazardous_items"] is True
    # CleanEarth is authorized and accepts batteries
    assert data["best_match"]["company_name"] == "CleanEarth E-Waste Solutions"
    assert data["best_match"]["compliance"]["accepts_hazardous"] is True
    assert data["best_match"]["compliance"]["hazard_compatibility_cleared"] is True

    # Surat Precious Metals is DISQUALIFIED_HAZARD
    disqualified = next(
        (c for c in data["recommendations"] if c["company_name"] == "Surat Precious Metals Ltd"),
        None,
    )
    assert disqualified is not None
    assert disqualified["compatibility_status"] == "DISQUALIFIED_HAZARD"
    assert "hazardous" in disqualified["explanation"].lower()
    assert "Disqualified" in disqualified["explanation"]
    assert any("hazardous" in c.lower() for c in disqualified["cons"])


@pytest.mark.asyncio
async def test_explainable_narrative_and_tradeoffs(client: AsyncClient, seed_matching_environment):
    """Verify that the engine returns transparent, human-readable explanations rather than opaque scores."""
    lot_id = seed_matching_environment["lot_normal_id"]

    response = await client.post(f"/api/v1/matching/lots/{lot_id}")
    assert response.status_code == 200
    recommendations = response.json()["data"]["recommendations"]

    for rec in recommendations:
        # Check transparent narrative
        assert isinstance(rec["explanation"], str)
        assert len(rec["explanation"]) > 20
        assert "₹" in rec["explanation"] or "Disqualified" in rec["explanation"]

        # Check pros and cons
        assert isinstance(rec["pros"], list)
        assert isinstance(rec["cons"], list)

        # Check breakdown
        assert rec["financial"]["currency"] == "INR"
        assert rec["logistics"]["distance_km"] > 0


@pytest.mark.asyncio
async def test_evaluate_manifest_before_lot_creation(client: AsyncClient, seed_matching_environment):
    """Verify on-the-fly manifest evaluation before lot creation."""
    mat_pcb_id = seed_matching_environment["mat_pcb_id"]

    payload = {
        "items": [
            {
                "material_id": mat_pcb_id,
                "weight_kg": 25.0,
                "detected_hazard": "NORMAL",
            }
        ],
        "origin_latitude": 19.0760,
        "origin_longitude": 72.8777,
        "require_pickup": False,
    }

    response = await client.post("/api/v1/matching/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["lot_id"] is None
    assert data["total_weight_kg"] == 25.0
    assert data["eligible_matches_count"] >= 1
    assert data["best_match"] is not None
    assert len(data["best_match"]["materials"]) == 1
    assert data["best_match"]["materials"][0]["weight_kg"] == 25.0
    assert data["best_match"]["financial"]["gross_payout"] > 0


@pytest.mark.asyncio
async def test_pickup_and_distance_filters(client: AsyncClient, seed_matching_environment):
    """Verify require_pickup and max_distance_km filters in matching endpoint."""
    lot_id = seed_matching_environment["lot_normal_id"]

    # Filter with max_distance_km = 30km: Recycler B (Pune ~115km) must be filtered out of eligible matches
    res_dist = await client.post(f"/api/v1/matching/lots/{lot_id}?max_distance_km=30.0")
    assert res_dist.status_code == 200
    data_dist = res_dist.json()["data"]
    assert data_dist["eligible_matches_count"] == 1
    assert data_dist["best_match"]["company_name"] == "CleanEarth E-Waste Solutions"

    # Filter with require_pickup = True: Recycler B has no pickup and must be ineligible
    res_pick = await client.post(f"/api/v1/matching/lots/{lot_id}?require_pickup=true")
    assert res_pick.status_code == 200
    data_pick = res_pick.json()["data"]
    assert data_pick["eligible_matches_count"] == 1
    assert data_pick["best_match"]["logistics"]["pickup_available"] is True
