import uuid
from decimal import Decimal
from datetime import datetime, timezone
import pytest
import pytest_asyncio
from sqlalchemy import select

from src.models import (
    WasteCategory,
    Material,
    MaterialPriceBand,
    CustodyEvent,
)


@pytest_asyncio.fixture
async def seed_taxonomy(init_test_db):
    """Seed sample categories and materials with price bands into test DB."""
    from tests.conftest import TestSessionFactory

    async with TestSessionFactory() as session:
        cat = WasteCategory(
            code="CAT_ITEW",
            name="IT & Telecom Equipment",
            description="Servers, laptops, and circuit boards",
            default_hazard="WARNING",
        )
        session.add(cat)
        await session.flush()

        # Material 1: Grade A PCB
        mat1 = Material(
            category_id=cat.id,
            code="PCB_SERVER_GRADE_A",
            name="Server Motherboard Grade A",
            base_unit="KG",
        )
        session.add(mat1)
        await session.flush()

        pb1 = MaterialPriceBand(
            material_id=mat1.id,
            grade="GRADE_A",
            min_price_per_unit=Decimal("1100.00"),
            max_price_per_unit=Decimal("1600.00"),
            benchmark_price_per_unit=Decimal("1350.00"),
            currency="INR",
            effective_from=datetime.now(timezone.utc),
            is_active=True,
        )
        session.add(pb1)

        # Material 2: Li-Ion battery
        mat2 = Material(
            category_id=cat.id,
            code="BATT_LI_ION_POUCH",
            name="Lithium-Ion Pouch Battery",
            base_unit="KG",
        )
        session.add(mat2)
        await session.flush()

        pb2 = MaterialPriceBand(
            material_id=mat2.id,
            grade="STANDARD",
            min_price_per_unit=Decimal("250.00"),
            max_price_per_unit=Decimal("400.00"),
            benchmark_price_per_unit=Decimal("320.00"),
            currency="INR",
            effective_from=datetime.now(timezone.utc),
            is_active=True,
        )
        session.add(pb2)

        await session.commit()

        return {
            "category_id": str(cat.id),
            "mat1_id": str(mat1.id),
            "mat2_id": str(mat2.id),
        }


async def get_collector_token(client, phone: str = "+919876588801") -> str:
    resp = await client.post(
        "/api/v1/auth/otp/verify",
        json={
            "phone": phone,
            "otp": "123456",
            "full_name": "Kavita Aggregator",
            "collector_type": "KABADIWALA",
        },
    )
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_taxonomy_materials_endpoint(client, seed_taxonomy):
    response = await client.get("/api/v1/lots/taxonomy/materials")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    categories = payload["data"]["categories"]
    assert len(categories) >= 1

    cat = categories[0]
    assert cat["code"] == "CAT_ITEW"
    assert len(cat["materials"]) == 2
    assert cat["materials"][0]["benchmark_price_per_unit"] == 1350.0
    assert cat["materials"][1]["benchmark_price_per_unit"] == 320.0


@pytest.mark.asyncio
async def test_create_lot_success(client, seed_taxonomy):
    token = await get_collector_token(client, "+919876588802")
    mat1_id = seed_taxonomy["mat1_id"]
    mat2_id = seed_taxonomy["mat2_id"]

    lot_payload = {
        "origin_latitude": 19.0760,
        "origin_longitude": 72.8777,
        "origin_address": "Dharavi Scrap Yard, Mumbai",
        "offline_created_at": "2026-09-20T10:00:00Z",
        "items": [
            {
                "material_id": mat1_id,
                "estimated_weight_kg": 5.0,
                "quantity": 3,
                "unit": "KG",
                "detected_hazard": "NORMAL",
                "ai_confidence_score": 0.94,
                "unit_price_estimated": 1400.0,  # 5.0 * 1400 = 7000.00
                "notes": "Grade A server boards from telecom decommission",
            },
            {
                "material_id": mat2_id,
                "estimated_weight_kg": 2.5,
                "quantity": 10,
                "unit": "KG",
                "detected_hazard": "SWOLLEN_BATTERY",
                "ai_confidence_score": 0.88,
                # unit_price_estimated omitted -> should auto-price at 320.0 (2.5 * 320 = 800.00)
            },
        ],
        "images": [
            {
                "image_url": "https://storage.ecobridge.org/lots/batch_photo_1.webp",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "captured_at": "2026-09-20T10:05:00Z",
                "is_proof_of_collection": True,
            }
        ],
    }

    create_resp = await client.post(
        "/api/v1/lots",
        json=lot_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_resp.status_code == 201

    payload = create_resp.json()
    assert payload["success"] is True
    data = payload["data"]

    # Validations
    assert data["lot_code"].startswith("EB-")
    assert data["status"] == "COLLECTED"
    assert data["total_estimated_weight_kg"] == 7.5
    # Total value = 7000 + 800 = 7800.00
    assert data["estimated_value"] == 7800.0
    assert data["currency"] == "INR"
    assert data["origin_address"] == "Dharavi Scrap Yard, Mumbai"
    assert data["items_count"] == 2
    assert len(data["items"]) == 2
    assert len(data["images"]) == 1

    # Check image SHA-256 hash was generated
    assert len(data["images"][0]["image_hash"]) == 64

    # Verify custody event in database
    from tests.conftest import TestSessionFactory
    async with TestSessionFactory() as session:
        custody_res = await session.execute(
            select(CustodyEvent).where(CustodyEvent.lot_id == uuid.UUID(data["id"]))
        )
        events = custody_res.scalars().all()
        assert len(events) == 1
        genesis_event = events[0]
        assert genesis_event.event_type == "CREATION"
        assert genesis_event.sequence_number == 1
        assert genesis_event.previous_event_hash == "0" * 64
        assert len(genesis_event.current_event_hash) == 64


@pytest.mark.asyncio
async def test_create_lot_validation_errors(client, seed_taxonomy):
    token = await get_collector_token(client, "+919876588803")
    mat1_id = seed_taxonomy["mat1_id"]

    # 1. Empty items list
    resp1 = await client.post(
        "/api/v1/lots",
        json={"items": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 422
    assert resp1.json()["error"]["code"] == "VALIDATION_ERROR"

    # 2. Negative weight
    resp2 = await client.post(
        "/api/v1/lots",
        json={
            "items": [
                {"material_id": mat1_id, "estimated_weight_kg": -5.0}
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 422

    # 3. Invalid GPS Latitude (> 90)
    resp3 = await client.post(
        "/api/v1/lots",
        json={
            "origin_latitude": 120.0,
            "items": [
                {"material_id": mat1_id, "estimated_weight_kg": 1.0}
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp3.status_code == 422


@pytest.mark.asyncio
async def test_get_lot_by_id_and_code(client, seed_taxonomy):
    token = await get_collector_token(client, "+919876588804")
    mat1_id = seed_taxonomy["mat1_id"]

    # Create lot
    create_resp = await client.post(
        "/api/v1/lots",
        json={
            "items": [
                {"material_id": mat1_id, "estimated_weight_kg": 3.0}
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    lot_data = create_resp.json()["data"]
    lot_uuid = lot_data["id"]
    lot_code = lot_data["lot_code"]

    # Fetch by UUID
    get_by_uuid = await client.get(
        f"/api/v1/lots/{lot_uuid}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_by_uuid.status_code == 200
    assert get_by_uuid.json()["data"]["id"] == lot_uuid

    # Fetch by Lot Code
    get_by_code = await client.get(
        f"/api/v1/lots/{lot_code}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_by_code.status_code == 200
    assert get_by_code.json()["data"]["lot_code"] == lot_code


@pytest.mark.asyncio
async def test_list_collector_lots(client, seed_taxonomy):
    token = await get_collector_token(client, "+919876588805")
    mat1_id = seed_taxonomy["mat1_id"]

    # Create 2 lots
    await client.post(
        "/api/v1/lots",
        json={"items": [{"material_id": mat1_id, "estimated_weight_kg": 2.0}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/api/v1/lots",
        json={"items": [{"material_id": mat1_id, "estimated_weight_kg": 4.0}]},
        headers={"Authorization": f"Bearer {token}"},
    )

    # List lots
    list_resp = await client.get(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200

    payload = list_resp.json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 2
    assert len(payload["data"]["lots"]) == 2


@pytest.mark.asyncio
async def test_attach_image_to_lot(client, seed_taxonomy):
    token = await get_collector_token(client, "+919876588806")
    mat1_id = seed_taxonomy["mat1_id"]

    # Create lot without images
    create_resp = await client.post(
        "/api/v1/lots",
        json={"items": [{"material_id": mat1_id, "estimated_weight_kg": 10.0}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    lot_id = create_resp.json()["data"]["id"]

    # Attach photo
    img_resp = await client.post(
        f"/api/v1/lots/{lot_id}/images",
        json={
            "image_url": "https://storage.ecobridge.org/lots/weigh_scale_proof.webp",
            "is_proof_of_collection": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert img_resp.status_code == 201

    img_data = img_resp.json()["data"]
    assert img_data["image_url"] == "https://storage.ecobridge.org/lots/weigh_scale_proof.webp"
    assert len(img_data["image_hash"]) == 64

    # Verify lot now has 1 image
    get_resp = await client.get(
        f"/api/v1/lots/{lot_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(get_resp.json()["data"]["images"]) == 1
