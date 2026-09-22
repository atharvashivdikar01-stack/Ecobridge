import uuid
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta
import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.models import (
    User,
    WasteCategory,
    Material,
    MaterialPriceBand,
    RecyclerCompany,
    RecyclerFacility,
)
from src.core.security import create_access_token


async def create_user_and_token(phone: str, role: str, full_name: str) -> str:
    """Helper to create a test user directly in DB and return a JWT access token."""
    from tests.conftest import TestSessionFactory

    async with TestSessionFactory() as session:
        user = User(
            phone=phone,
            full_name=full_name,
            role=role,
            status="ACTIVE",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return create_access_token(subject=str(user.id), role=user.role)


@pytest_asyncio.fixture
async def seed_material(init_test_db):
    """Seed test waste category and material."""
    from tests.conftest import TestSessionFactory

    async with TestSessionFactory() as session:
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

        pb = MaterialPriceBand(
            material_id=mat.id,
            grade="GRADE_A",
            min_price_per_unit=Decimal("1100.00"),
            max_price_per_unit=Decimal("1600.00"),
            benchmark_price_per_unit=Decimal("1350.00"),
            currency="INR",
            effective_from=datetime.now(timezone.utc),
            is_active=True,
        )
        session.add(pb)
        await session.commit()

        return {
            "category_id": str(cat.id),
            "material_id": str(mat.id),
            "material_code": mat.code,
        }


@pytest.mark.asyncio
async def test_register_recycler_company_and_facility(client: AsyncClient):
    """Verify onboarding a recycler company and its primary processing facility."""
    token = await create_user_and_token("+919811111111", "COLLECTOR", "Ravi Patel")

    payload = {
        "company_name": "EcoGreen E-Waste Recyclers Pvt Ltd",
        "trade_license_number": "TL-MUM-2026-9999",
        "gst_number": "27AAACE1234F1Z5",
        "cpcb_registration_no": "CPCB/EW/2026/001",
        "contact_person": "Ravi Patel",
        "contact_phone": "+919811111111",
        "contact_email": "ravi@ecogreen.com",
        "primary_facility": {
            "facility_name": "Taloja MIDC Recycling Plant",
            "address_line1": "Plot 42, Sector 8, Taloja MIDC",
            "city": "Navi Mumbai",
            "state": "Maharashtra",
            "postal_code": "410208",
            "latitude": 19.0657,
            "longitude": 73.1256,
            "daily_capacity_kg": 5000.0,
            "accepts_hazardous": True,
            "pickup_available": True,
            "min_pickup_weight_kg": 100.0,
            "max_pickup_distance_km": 75.0,
            "lead_time_hours": 24,
            "pickup_operating_days": "MON-SAT",
        },
    }

    response = await client.post(
        "/api/v1/recyclers/register",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["company_name"] == "EcoGreen E-Waste Recyclers Pvt Ltd"
    assert data["operating_status"] == "PENDING_VERIFICATION"
    assert len(data["facilities"]) == 1

    fac = data["facilities"][0]
    assert fac["facility_name"] == "Taloja MIDC Recycling Plant"
    assert fac["city"] == "Navi Mumbai"
    assert fac["accepts_hazardous"] is True
    assert fac["pickup_available"] is True
    assert fac["min_pickup_weight_kg"] == 100.0

    # Duplicate registration on same account should fail
    dup_res = await client.post(
        "/api/v1/recyclers/register",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert dup_res.status_code == 409


@pytest.mark.asyncio
async def test_get_and_update_recycler_profile(client: AsyncClient):
    """Verify fetching and updating current recycler's profile."""
    token = await create_user_and_token("+919811111112", "COLLECTOR", "Anita Rao")

    reg_payload = {
        "company_name": "CleanEarth Solutions Ltd",
        "trade_license_number": "TL-DEL-2026-1234",
        "cpcb_registration_no": "CPCB/EW/2026/002",
        "contact_person": "Anita Rao",
        "contact_phone": "+919811111112",
        "primary_facility": {
            "facility_name": "Okhla Processing Hub",
            "address_line1": "Phase III, Okhla Industrial Area",
            "city": "New Delhi",
            "state": "Delhi",
            "postal_code": "110020",
            "latitude": 28.5355,
            "longitude": 77.2731,
        },
    }
    await client.post("/api/v1/recyclers/register", json=reg_payload, headers={"Authorization": f"Bearer {token}"})

    # Fetch profile
    get_res = await client.get("/api/v1/recyclers/me", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200
    assert get_res.json()["data"]["company_name"] == "CleanEarth Solutions Ltd"

    # Update profile
    update_payload = {
        "contact_person": "Anita Rao-Sharma",
        "gst_number": "07AAACC9876D1Z2",
    }
    put_res = await client.put("/api/v1/recyclers/me", json=update_payload, headers={"Authorization": f"Bearer {token}"})
    assert put_res.status_code == 200
    assert put_res.json()["data"]["contact_person"] == "Anita Rao-Sharma"
    assert put_res.json()["data"]["gst_number"] == "07AAACC9876D1Z2"


@pytest.mark.asyncio
async def test_authorization_record_management(client: AsyncClient):
    """Verify adding CPCB/SPCB permits, validating dates, and listing authorizations."""
    token = await create_user_and_token("+919811111113", "COLLECTOR", "Vikram Singh")

    reg_payload = {
        "company_name": "Apex Dismantlers",
        "trade_license_number": "TL-PUN-2026-5555",
        "cpcb_registration_no": "CPCB/EW/2026/003",
        "contact_person": "Vikram Singh",
        "contact_phone": "+919811111113",
        "primary_facility": {
            "facility_name": "Bhosari Plant",
            "address_line1": "MIDC Bhosari",
            "city": "Pune",
            "state": "Maharashtra",
            "postal_code": "411026",
            "latitude": 18.6279,
            "longitude": 73.8344,
        },
    }
    reg_res = await client.post("/api/v1/recyclers/register", json=reg_payload, headers={"Authorization": f"Bearer {token}"})
    facility_id = reg_res.json()["data"]["facilities"][0]["id"]

    # Invalid dates: expiry before issued
    bad_auth = {
        "authority_name": "MPCB",
        "permit_type": "E_WASTE_RECYCLER",
        "permit_number": "MPCB/E-WASTE/2026/001",
        "issued_date": "2026-05-01",
        "expiry_date": "2025-05-01",
    }
    bad_res = await client.post(
        f"/api/v1/recyclers/facilities/{facility_id}/authorizations",
        json=bad_auth,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bad_res.status_code == 422

    # Valid authorization
    valid_auth = {
        "authority_name": "Maharashtra Pollution Control Board (MPCB)",
        "permit_type": "E_WASTE_RECYCLER",
        "permit_number": "MPCB/E-WASTE/2026/001",
        "authorized_capacity_mta": 2400.0,
        "issued_date": "2026-01-01",
        "expiry_date": "2029-12-31",
        "document_url": "https://storage.ecobridge.in/permits/mpcb_001.pdf",
        "status": "ACTIVE",
    }
    auth_res = await client.post(
        f"/api/v1/recyclers/facilities/{facility_id}/authorizations",
        json=valid_auth,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert auth_res.status_code == 201
    auth_data = auth_res.json()["data"]
    assert auth_data["permit_number"] == "MPCB/E-WASTE/2026/001"
    assert auth_data["authorized_capacity_mta"] == 2400.0

    # List authorizations
    list_res = await client.get(f"/api/v1/recyclers/facilities/{facility_id}/authorizations")
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 1


@pytest.mark.asyncio
async def test_admin_verification_workflow(client: AsyncClient):
    """Verify administrator verification approval and status changes."""
    recycler_token = await create_user_and_token("+919811111114", "COLLECTOR", "Karan Johar")
    admin_token = await create_user_and_token("+919800000000", "PLATFORM_ADMIN", "Chief Auditor")

    reg_payload = {
        "company_name": "National Metal Extractors",
        "trade_license_number": "TL-BLR-2026-7777",
        "cpcb_registration_no": "CPCB/EW/2026/004",
        "contact_person": "Karan Johar",
        "contact_phone": "+919811111114",
        "primary_facility": {
            "facility_name": "Peenya Facility",
            "address_line1": "Peenya 2nd Stage",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560058",
            "latitude": 13.0285,
            "longitude": 77.5197,
        },
    }
    reg_res = await client.post("/api/v1/recyclers/register", json=reg_payload, headers={"Authorization": f"Bearer {recycler_token}"})
    company_id = reg_res.json()["data"]["id"]

    # Non-admin cannot verify
    unauth_res = await client.post(
        f"/api/v1/recyclers/{company_id}/verify",
        json={"operating_status": "VERIFIED"},
        headers={"Authorization": f"Bearer {recycler_token}"},
    )
    assert unauth_res.status_code == 403

    # Admin verifies company
    verify_payload = {
        "operating_status": "VERIFIED",
        "verification_notes": "Physical audit and CPCB consent certificates validated.",
    }
    ver_res = await client.post(
        f"/api/v1/recyclers/{company_id}/verify",
        json=verify_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert ver_res.status_code == 200
    ver_data = ver_res.json()["data"]
    assert ver_data["operating_status"] == "VERIFIED"
    assert ver_data["verified_at"] is not None


@pytest.mark.asyncio
async def test_accepted_materials_and_rates(client: AsyncClient, seed_material):
    """Verify configuring accepted scrap materials, standing rates, and minimum weights."""
    token = await create_user_and_token("+919811111115", "COLLECTOR", "Sameer Verma")
    mat_id = seed_material["material_id"]

    reg_payload = {
        "company_name": "Surat Precious Metals",
        "trade_license_number": "TL-SUR-2026-3333",
        "cpcb_registration_no": "CPCB/EW/2026/005",
        "contact_person": "Sameer Verma",
        "contact_phone": "+919811111115",
        "primary_facility": {
            "facility_name": "Sachin GIDC Unit",
            "address_line1": "Road 5, Sachin GIDC",
            "city": "Surat",
            "state": "Gujarat",
            "postal_code": "394230",
            "latitude": 21.0827,
            "longitude": 72.8712,
        },
    }
    reg_res = await client.post("/api/v1/recyclers/register", json=reg_payload, headers={"Authorization": f"Bearer {token}"})
    facility_id = reg_res.json()["data"]["facilities"][0]["id"]

    # Configure material
    mat_payload = {
        "material_id": mat_id,
        "standard_rate_per_unit": 1425.00,
        "minimum_accepted_weight_kg": 5.0,
        "currency": "INR",
        "is_active": True,
    }
    add_res = await client.post(
        f"/api/v1/recyclers/facilities/{facility_id}/materials",
        json=mat_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert add_res.status_code == 201
    m_data = add_res.json()["data"]
    assert m_data["material_code"] == "PCB_SERVER_GRADE_A"
    assert m_data["standard_rate_per_unit"] == 1425.0
    assert m_data["minimum_accepted_weight_kg"] == 5.0

    # List materials
    list_res = await client.get(f"/api/v1/recyclers/facilities/{facility_id}/materials")
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 1


@pytest.mark.asyncio
async def test_service_areas_and_pickup_logistics(client: AsyncClient):
    """Verify service area zones and pickup logistics configuration."""
    token = await create_user_and_token("+919811111116", "COLLECTOR", "Gaurav Mehta")

    reg_payload = {
        "company_name": "Western Recyclers",
        "trade_license_number": "TL-AHM-2026-4444",
        "cpcb_registration_no": "CPCB/EW/2026/006",
        "contact_person": "Gaurav Mehta",
        "contact_phone": "+919811111116",
        "primary_facility": {
            "facility_name": "Sanand Processing Plant",
            "address_line1": "Sanand GIDC",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "postal_code": "382110",
            "latitude": 22.9868,
            "longitude": 72.3814,
        },
    }
    reg_res = await client.post("/api/v1/recyclers/register", json=reg_payload, headers={"Authorization": f"Bearer {token}"})
    facility_id = reg_res.json()["data"]["facilities"][0]["id"]

    # Add service area
    area_payload = {
        "region_name": "Ahmedabad Urban Area",
        "state": "Gujarat",
        "city": "Ahmedabad",
        "postal_codes": "380001,380015,382110",
        "radius_km": 40.0,
    }
    area_res = await client.post(
        f"/api/v1/recyclers/facilities/{facility_id}/service-areas",
        json=area_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert area_res.status_code == 201
    assert area_res.json()["data"]["region_name"] == "Ahmedabad Urban Area"

    # Configure pickup logistics
    pickup_payload = {
        "pickup_available": True,
        "min_pickup_weight_kg": 75.0,
        "max_pickup_distance_km": 50.0,
        "lead_time_hours": 12,
        "pickup_operating_days": "MON-FRI",
    }
    pick_res = await client.put(
        f"/api/v1/recyclers/facilities/{facility_id}/pickup",
        json=pickup_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pick_res.status_code == 200
    pick_data = pick_res.json()["data"]
    assert pick_data["pickup_available"] is True
    assert pick_data["min_pickup_weight_kg"] == 75.0
    assert pick_data["lead_time_hours"] == 12


@pytest.mark.asyncio
async def test_recycler_directory_discovery(client: AsyncClient, seed_material):
    """Verify collector directory discovery filters and verified status enforcement."""
    rec_token = await create_user_and_token("+919811111117", "COLLECTOR", "Pooja Hegde")
    admin_token = await create_user_and_token("+919800000001", "PLATFORM_ADMIN", "Dir Auditor")
    mat_id = seed_material["material_id"]

    reg_payload = {
        "company_name": "Mumbai Green E-Waste Ltd",
        "trade_license_number": "TL-MUM-2026-8888",
        "cpcb_registration_no": "CPCB/EW/2026/007",
        "contact_person": "Pooja Hegde",
        "contact_phone": "+919811111117",
        "primary_facility": {
            "facility_name": "Kurla Hub",
            "address_line1": "Kurla West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400070",
            "latitude": 19.0728,
            "longitude": 72.8797,
            "pickup_available": True,
            "min_pickup_weight_kg": 50.0,
        },
    }
    reg_res = await client.post("/api/v1/recyclers/register", json=reg_payload, headers={"Authorization": f"Bearer {rec_token}"})
    comp_id = reg_res.json()["data"]["id"]
    fac_id = reg_res.json()["data"]["facilities"][0]["id"]

    # Configure material
    await client.post(
        f"/api/v1/recyclers/facilities/{fac_id}/materials",
        json={"material_id": mat_id, "standard_rate_per_unit": 1400.0},
        headers={"Authorization": f"Bearer {rec_token}"},
    )

    # Before verification: directory should return 0 verified recyclers
    dir_res1 = await client.get("/api/v1/recyclers/directory")
    assert dir_res1.status_code == 200
    assert dir_res1.json()["data"]["total"] == 0

    # Admin verifies recycler
    await client.post(
        f"/api/v1/recyclers/{comp_id}/verify",
        json={"operating_status": "VERIFIED"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # After verification: directory discovers the recycler
    dir_res2 = await client.get("/api/v1/recyclers/directory")
    assert dir_res2.status_code == 200
    assert dir_res2.json()["data"]["total"] >= 1

    # Filter by city
    dir_mumbai = await client.get("/api/v1/recyclers/directory?city=Mumbai")
    assert dir_mumbai.status_code == 200
    assert dir_mumbai.json()["data"]["total"] >= 1
    found = dir_mumbai.json()["data"]["recyclers"][0]
    assert found["city"] == "Mumbai"
    assert found["pickup_available"] is True
    assert found["rates"]["PCB_SERVER_GRADE_A"] == 1400.0

    # Filter by non-existent city
    dir_none = await client.get("/api/v1/recyclers/directory?city=Chennai")
    assert dir_none.status_code == 200
    assert dir_none.json()["data"]["total"] == 0
