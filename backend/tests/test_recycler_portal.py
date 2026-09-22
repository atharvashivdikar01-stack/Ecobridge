import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.models import (
    User,
    CollectorProfile,
    WasteCategory,
    Material,
    MaterialPriceBand,
    RecyclerCompany,
    RecyclerFacility,
    AuthorizationRecord,
    Lot,
    LotItem,
    CustodyEvent,
)
from src.core.security import create_access_token


@pytest_asyncio.fixture
async def setup_recycler_portal_test_data(init_test_db):
    """Sets up verified recycler, unverified recycler, collector, and staged lots."""
    from tests.conftest import TestSessionFactory

    async with TestSessionFactory() as session:
        # Category and Material
        cat = WasteCategory(
            code="CAT_ITEW",
            name="IT & Telecom Equipment",
            description="Laptops, motherboards, servers",
            default_hazard="WARNING",
        )
        session.add(cat)
        await session.flush()

        mat = Material(
            category_id=cat.id,
            code="PCB_SERVER_GRADE_A",
            name="Server Motherboard Grade A",
            base_unit="KG",
        )
        session.add(mat)
        await session.flush()

        now_utc = datetime.now(timezone.utc)
        pb = MaterialPriceBand(
            material_id=mat.id,
            grade="GRADE_A",
            min_price_per_unit=Decimal("1100.00"),
            max_price_per_unit=Decimal("1600.00"),
            benchmark_price_per_unit=Decimal("1350.00"),
            effective_from=now_utc,
            is_active=True,
        )
        session.add(pb)

        # 1. Verified Recycler
        rec_user = User(
            phone="+919811111111",
            full_name="Ravi Patel (EcoGreen)",
            role="RECYCLER_ADMIN",
            status="ACTIVE",
        )
        session.add(rec_user)
        await session.flush()

        rec_company = RecyclerCompany(
            user_id=rec_user.id,
            company_name="EcoGreen E-Waste Recyclers Pvt Ltd",
            trade_license_number="TL-MUM-2026-9999",
            gst_number="27AAACE1234F1Z5",
            cpcb_registration_no="CPCB/EW/2026/001",
            contact_person="Ravi Patel",
            contact_phone="+919811111111",
            operating_status="VERIFIED",
        )
        session.add(rec_company)
        await session.flush()

        fac = RecyclerFacility(
            recycler_id=rec_company.id,
            facility_name="Taloja Plant",
            address_line1="Plot 42, Sector 8",
            city="Navi Mumbai",
            state="Maharashtra",
            postal_code="410208",
            latitude=Decimal("19.0657"),
            longitude=Decimal("73.1256"),
            daily_capacity_kg=Decimal("5000.00"),
            accepts_hazardous=True,
        )
        session.add(fac)

        # 2. Unverified Recycler
        unv_user = User(
            phone="+919822222222",
            full_name="Vikram Shah",
            role="RECYCLER_ADMIN",
            status="ACTIVE",
        )
        session.add(unv_user)
        await session.flush()

        unv_company = RecyclerCompany(
            user_id=unv_user.id,
            company_name="Pending Scrap Co.",
            trade_license_number="TL-PUN-2026-1044",
            cpcb_registration_no="CPCB/EW/2026/PENDING-99",
            contact_person="Vikram Shah",
            contact_phone="+919822222222",
            operating_status="PENDING_VERIFICATION",
        )
        session.add(unv_company)

        # 3. Collector
        col_user = User(
            phone="+919800000001",
            full_name="Raju Shinde",
            role="COLLECTOR",
            status="ACTIVE",
        )
        session.add(col_user)
        await session.flush()

        col_profile = CollectorProfile(
            user_id=col_user.id,
            collector_type="INDIVIDUAL_PICKER",
        )
        session.add(col_profile)
        await session.flush()

        # 4. Available Lot
        lot = Lot(
            lot_code="EB-202609-9001",
            collector_id=col_profile.id,
            status="COLLECTED",
            total_estimated_weight_kg=Decimal("50.000"),
            estimated_value=Decimal("67500.00"),
            currency="INR",
            offline_created_at=now_utc,
            synced_at=now_utc,
        )
        session.add(lot)
        await session.flush()

        item = LotItem(
            lot_id=lot.id,
            material_id=mat.id,
            quantity=1,
            unit="KG",
            estimated_weight_kg=Decimal("50.000"),
            unit_price_estimated=Decimal("1350.00"),
            subtotal_estimated=Decimal("67500.00"),
            ai_confidence_score=Decimal("0.9450"),
            detected_hazard="NORMAL",
        )
        session.add(item)

        evt = CustodyEvent(
            lot_id=lot.id,
            sequence_number=1,
            event_type="CREATION",
            actor_id=col_user.id,
            actor_role="COLLECTOR",
            event_timestamp=now_utc,
            event_payload_json={"lot_code": lot.lot_code, "weight_kg": 50.0},
            previous_event_hash="0" * 64,
            current_event_hash="hash_genesis_0001",
        )
        session.add(evt)
        await session.commit()

        verified_token = create_access_token(subject=str(rec_user.id), role=rec_user.role)
        unverified_token = create_access_token(subject=str(unv_user.id), role=unv_user.role)

        return {
            "verified_token": verified_token,
            "unverified_token": unverified_token,
            "lot_id": str(lot.id),
            "lot_code": lot.lot_code,
        }


@pytest.mark.asyncio
async def test_get_dashboard_summary(client: AsyncClient, setup_recycler_portal_test_data):
    """Test retrieving dashboard metrics as verified recycler."""
    token = setup_recycler_portal_test_data["verified_token"]
    response = await client.get(
        "/api/v1/recycler-portal/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["company_name"] == "EcoGreen E-Waste Recyclers Pvt Ltd"
    assert res["data"]["is_verified"] is True
    assert res["data"]["operating_status"] == "VERIFIED"


@pytest.mark.asyncio
async def test_list_available_materials(client: AsyncClient, setup_recycler_portal_test_data):
    """Test listing available materials with classification and confidence."""
    token = setup_recycler_portal_test_data["verified_token"]
    response = await client.get(
        "/api/v1/recycler-portal/materials",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]["items"]) >= 1
    item = res["data"]["items"][0]
    assert item["lot_code"] == "EB-202609-9001"
    assert item["estimated_weight_kg"] == 50.0
    assert item["ai_confidence_score"] == 0.945


@pytest.mark.asyncio
async def test_unverified_recycler_cannot_accept_offer(client: AsyncClient, setup_recycler_portal_test_data):
    """Verify that unverified/pending recyclers are blocked from accepting offers (403 Forbidden)."""
    unverified_token = setup_recycler_portal_test_data["unverified_token"]
    lot_id = setup_recycler_portal_test_data["lot_id"]

    response = await client.post(
        f"/api/v1/recycler-portal/lots/{lot_id}/accept",
        headers={"Authorization": f"Bearer {unverified_token}"},
        json={"agreed_price_per_kg": 1400.0},
    )
    assert response.status_code == 403
    res = response.json()
    assert res["success"] is False
    assert "Only authorized and CPCB-verified recyclers" in res["error"]["message"]


@pytest.mark.asyncio
async def test_complete_recycler_journey(client: AsyncClient, setup_recycler_portal_test_data):
    """Verify end-to-end journey:
    Accept Offer -> Confirm Handover with Weighbridge -> Record Cash Payment -> Check Ledger.
    """
    token = setup_recycler_portal_test_data["verified_token"]
    lot_id = setup_recycler_portal_test_data["lot_id"]

    # 1. Accept Offer with Agreed Price (₹1400/kg)
    # Expected Final Value = 50 kg * ₹1400 = ₹70,000
    accept_res = await client.post(
        f"/api/v1/recycler-portal/lots/{lot_id}/accept",
        headers={"Authorization": f"Bearer {token}"},
        json={"agreed_price_per_kg": 1400.0, "notes": "Tested Grade A motherboards"},
    )
    assert accept_res.status_code == 200
    acc_data = accept_res.json()["data"]
    assert acc_data["status"] == "ACCEPTED"
    assert acc_data["agreed_price_per_kg"] == 1400.0
    assert acc_data["final_value"] == 70000.0

    # 2. Duplicate Acceptance Check (Should be rejected with 409 Conflict)
    dup_res = await client.post(
        f"/api/v1/recycler-portal/lots/{lot_id}/accept",
        headers={"Authorization": f"Bearer {token}"},
        json={"agreed_price_per_kg": 1400.0},
    )
    assert dup_res.status_code == 409

    # 3. Confirm Handover with Weighbridge Scale
    # Verified Net Weight = 48.5 kg (Scale reconciled)
    # New Final Value = 48.5 * 1400 = ₹67,900
    handover_res = await client.post(
        f"/api/v1/recycler-portal/lots/{lot_id}/handover",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "weighbridge_slip_number": "WB-TALOJA-2026-9901",
            "weighbridge_gross_kg": 88.5,
            "weighbridge_tare_kg": 40.0,
            "verified_weight_kg": 48.5,
            "scale_calibration_id": "SCALE-CAL-2026-A1",
        },
    )
    assert handover_res.status_code == 200
    ho_data = handover_res.json()["data"]
    assert ho_data["status"] == "HANDED_OVER"
    assert ho_data["verified_weight_kg"] == 48.5
    assert ho_data["final_value"] == 67900.0

    # 4. Record Cash Payment (₹67,900)
    pay_res = await client.post(
        f"/api/v1/recycler-portal/lots/{lot_id}/payment",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "payment_method": "CASH",
            "amount": 67900.0,
            "gateway_reference": "CASH-REC-20260922-001",
            "notes": "Paid in cash upon physical inspection",
        },
    )
    assert pay_res.status_code == 201
    pay_data = pay_res.json()["data"]
    assert pay_data["payment_method"] == "CASH"
    assert pay_data["payment_status"] == "PAID"
    assert pay_data["total_amount"] == 67900.0
    assert pay_data["weighbridge_slip"] == "WB-TALOJA-2026-9901"
    assert pay_data["custody_hash"] is not None

    # 5. Verify Transaction in Recycler Ledger
    ledger_res = await client.get(
        "/api/v1/recycler-portal/ledger",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ledger_res.status_code == 200
    ledger_data = ledger_res.json()["data"]
    assert ledger_data["total_transactions"] >= 1
    assert ledger_data["total_volume_kg"] == 48.5
    assert ledger_data["total_disbursed_inr"] == 67900.0

    matched_tx = next((t for t in ledger_data["transactions"] if t["lot_id"] == lot_id), None)
    assert matched_tx is not None
    assert matched_tx["payment_method"] == "CASH"
    assert matched_tx["verified_weight_kg"] == 48.5
    assert matched_tx["agreed_price_per_kg"] == 1400.0
    assert matched_tx["total_amount"] == 67900.0


@pytest.mark.asyncio
async def test_demo_login_endpoint(client: AsyncClient, setup_recycler_portal_test_data):
    """Test switching accounts via demo login endpoint."""
    res_ver = await client.post("/api/v1/auth/demo-login", json={"role": "VERIFIED_RECYCLER"})
    assert res_ver.status_code == 200
    assert res_ver.json()["data"]["user"]["role"] == "RECYCLER_ADMIN"
    assert "EcoGreen" in res_ver.json()["data"]["user"]["full_name"]

    res_unv = await client.post("/api/v1/auth/demo-login", json={"role": "UNVERIFIED_RECYCLER"})
    assert res_unv.status_code == 200
    assert "Vikram" in res_unv.json()["data"]["user"]["full_name"]
