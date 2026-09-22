import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.models import (
    WasteCategory,
    Material,
    MaterialPriceBand,
    PriceObservation,
    RecyclerOffer,
    Lot,
    LotItem,
    User,
    CollectorProfile,
)


@pytest_asyncio.fixture
async def seed_pricing_data(init_test_db):
    """Seed sample materials, price bands, and test collector for pricing tests."""
    from tests.conftest import TestSessionFactory

    async with TestSessionFactory() as session:
        cat = WasteCategory(
            code="CAT_PCB",
            name="Printed Circuit Boards",
            description="Electronic circuit boards and components",
            default_hazard="WARNING",
        )
        session.add(cat)
        await session.flush()

        mat = Material(
            category_id=cat.id,
            code="PCB_HIGH_GRADE",
            name="High Grade Gold-Finger PCB",
            base_unit="KG",
        )
        session.add(mat)
        await session.flush()

        pb = MaterialPriceBand(
            material_id=mat.id,
            grade="GRADE_A",
            min_price_per_unit=Decimal("1000.00"),
            max_price_per_unit=Decimal("1800.00"),
            benchmark_price_per_unit=Decimal("1400.00"),
            currency="INR",
            effective_from=datetime.now(timezone.utc),
            is_active=True,
        )
        session.add(pb)

        # Collector & Profile
        user = User(
            phone="+919876543210",
            full_name="Pricing Test Collector",
            role="COLLECTOR",
            status="ACTIVE",
        )
        session.add(user)
        await session.flush()

        prof = CollectorProfile(
            user_id=user.id,
            collector_type="INDIVIDUAL_PICKER",
            verified_at=datetime.now(timezone.utc),
        )
        session.add(prof)
        await session.flush()

        await session.commit()

        return {
            "category_id": str(cat.id),
            "material_id": str(mat.id),
            "material_code": mat.code,
            "collector_id": str(prof.id),
            "user_id": str(user.id),
        }


@pytest.mark.asyncio
async def test_record_price_observation(client: AsyncClient, seed_pricing_data):
    """Verify recording an empirical market transaction observation."""
    mat_id = seed_pricing_data["material_id"]

    payload = {
        "material_id": mat_id,
        "price_per_unit": 1380.50,
        "currency": "INR",
        "unit": "KG",
        "source_type": "OBSERVED_TRANSACTION",
        "source_name": "Kurla Scrap Mandi",
        "region": "Mumbai",
        "confidence_weight": 0.95,
    }

    response = await client.post("/api/v1/prices/observations", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["price_per_unit"] == 1380.50
    assert data["source_name"] == "Kurla Scrap Mandi"
    assert data["region"] == "Mumbai"
    assert data["confidence_weight"] == 0.95


@pytest.mark.asyncio
async def test_record_price_observation_invalid_material(client: AsyncClient):
    """Verify error handling when recording observation for non-existent material."""
    payload = {
        "material_id": str(uuid.uuid4()),
        "price_per_unit": 500.0,
        "source_name": "Unknown Yard",
    }
    response = await client.post("/api/v1/prices/observations", json=payload)
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_observed_metrics_and_model_estimate_calculation(client: AsyncClient, seed_pricing_data):
    """Verify empirical metrics and statistical model estimates are calculated and strictly separated."""
    mat_id = seed_pricing_data["material_id"]

    # Ingest 5 observed prices: 1200, 1300, 1350, 1400, 1500
    prices = [1200.0, 1300.0, 1350.0, 1400.0, 1500.0]
    for p in prices:
        obs_payload = {
            "material_id": mat_id,
            "price_per_unit": p,
            "source_type": "LOCAL_SCRAPYARD_QUOTE",
            "source_name": f"Yard {p}",
            "region": "National",
            "confidence_weight": 1.0,
        }
        res = await client.post("/api/v1/prices/observations", json=obs_payload)
        assert res.status_code == 201

    # Fetch price intelligence
    response = await client.get(f"/api/v1/prices/intelligence/{mat_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]

    # 1. Verify Observed Metrics
    obs = data["observed_metrics"]
    assert obs["data_type"] == "EMPIRICAL_OBSERVATIONS"
    assert obs["sample_size"] == 5
    assert obs["market_min"] == 1200.0
    assert obs["market_max"] == 1500.0
    assert obs["local_median"] == 1350.0
    assert obs["mean"] == 1350.0
    assert len(obs["observations"]) == 5

    # 2. Verify Statistical Model Estimate
    model = data["model_estimate"]
    assert model["data_type"] == "STATISTICAL_MODEL_ESTIMATE"
    assert model["method"] == "WEIGHTED_MEDIAN_IQR"
    assert model["fair_price"] == 1350.0
    assert model["confidence_level"] == "MEDIUM"
    assert model["recommended_floor"] is not None
    assert model["recommended_ceiling"] is not None
    assert model["recommended_floor"] <= model["fair_price"]
    assert model["recommended_ceiling"] >= model["fair_price"]
    assert "disclaimer" in model


@pytest.mark.asyncio
async def test_recycler_offers_aggregation(client: AsyncClient, seed_pricing_data):
    """Verify certified recycler offers aggregation, highest and average offer math."""
    mat_id = seed_pricing_data["material_id"]
    recycler_1 = str(uuid.uuid4())
    recycler_2 = str(uuid.uuid4())

    # Submit offer 1: 1450/unit
    offer1 = {
        "material_id": mat_id,
        "recycler_id": recycler_1,
        "recycler_name": "EcoClean Recyclers Ltd",
        "offered_price_per_unit": 1450.0,
        "offered_total_price": 14500.0,
        "pickup_cost_deduction": 500.0,
        "currency": "INR",
    }
    r1 = await client.post("/api/v1/prices/offers", json=offer1)
    assert r1.status_code == 201
    assert r1.json()["data"]["net_collector_earning"] == 14000.0

    # Submit offer 2: 1550/unit
    offer2 = {
        "material_id": mat_id,
        "recycler_id": recycler_2,
        "recycler_name": "GreenTech E-Waste Processors",
        "offered_price_per_unit": 1550.0,
        "offered_total_price": 15500.0,
        "pickup_cost_deduction": 0.0,
        "currency": "INR",
    }
    r2 = await client.post("/api/v1/prices/offers", json=offer2)
    assert r2.status_code == 201

    # Query price intelligence
    response = await client.get(f"/api/v1/prices/intelligence/{mat_id}")
    assert response.status_code == 200
    offers = response.json()["data"]["active_recycler_offers"]

    assert offers["data_type"] == "ACTIVE_RECYCLER_OFFERS"
    assert offers["active_offers_count"] == 2
    assert offers["highest_offer_price"] == 1550.0
    assert offers["average_offer_price"] == 1500.0
    # Must be ordered descending by price
    assert offers["offers"][0]["offered_price_per_unit"] == 1550.0
    assert offers["offers"][1]["offered_price_per_unit"] == 1450.0


@pytest.mark.asyncio
async def test_regional_filtering(client: AsyncClient, seed_pricing_data):
    """Verify observations are filtered by region while retaining national benchmarks."""
    mat_id = seed_pricing_data["material_id"]

    # Mumbai observation
    await client.post(
        "/api/v1/prices/observations",
        json={
            "material_id": mat_id,
            "price_per_unit": 1420.0,
            "source_name": "Dharavi",
            "region": "Mumbai",
        },
    )
    # Delhi observation
    await client.post(
        "/api/v1/prices/observations",
        json={
            "material_id": mat_id,
            "price_per_unit": 1390.0,
            "source_name": "Mayapuri",
            "region": "Delhi",
        },
    )
    # National observation
    await client.post(
        "/api/v1/prices/observations",
        json={
            "material_id": mat_id,
            "price_per_unit": 1400.0,
            "source_name": "National Index",
            "region": "National",
        },
    )

    # Filter for Mumbai
    res_mumbai = await client.get(f"/api/v1/prices/intelligence/{mat_id}?region=Mumbai")
    assert res_mumbai.status_code == 200
    mumbai_data = res_mumbai.json()["data"]["observed_metrics"]
    assert mumbai_data["sample_size"] == 2  # Mumbai (1420) + National (1400)
    regions = [o["region"] for o in mumbai_data["observations"]]
    assert "Mumbai" in regions
    assert "National" in regions
    assert "Delhi" not in regions


@pytest.mark.asyncio
async def test_dynamic_lot_valuation(client: AsyncClient, seed_pricing_data):
    """Verify dynamic lot valuation against current market intelligence."""
    from tests.conftest import TestSessionFactory

    mat_id = seed_pricing_data["material_id"]
    prof_id = seed_pricing_data["collector_id"]

    # Seed an empirical observation for this material: 1400/KG
    await client.post(
        "/api/v1/prices/observations",
        json={
            "material_id": mat_id,
            "price_per_unit": 1400.0,
            "source_name": "Observed Spot",
            "region": "National",
        },
    )

    # Create a test lot directly in DB
    async with TestSessionFactory() as session:
        lot = Lot(
            collector_id=uuid.UUID(prof_id),
            lot_code="EB-TEST-VAL-001",
            total_estimated_weight_kg=Decimal("10.000"),
            estimated_value=Decimal("14000.00"),
            currency="INR",
            offline_created_at=datetime.now(timezone.utc),
        )
        session.add(lot)
        await session.flush()

        item = LotItem(
            lot_id=lot.id,
            material_id=uuid.UUID(mat_id),
            quantity=1,
            unit="KG",
            estimated_weight_kg=Decimal("10.000"),
            unit_price_estimated=Decimal("1400.00"),
            subtotal_estimated=Decimal("14000.00"),
            detected_hazard="NORMAL",
        )
        session.add(item)
        await session.commit()
        lot_id = str(lot.id)

    # Fetch lot valuation
    val_res = await client.get(f"/api/v1/prices/lot-valuation/{lot_id}")
    assert val_res.status_code == 200
    val_data = val_res.json()["data"]

    assert val_data["lot_id"] == lot_id
    assert val_data["total_weight_kg"] == 10.0
    assert len(val_data["items_valuation"]) == 1
    assert val_data["items_valuation"][0]["weight_kg"] == 10.0
    assert val_data["items_valuation"][0]["observed_median_rate"] == 1400.0
    assert val_data["total_estimated_value"] > 0
    assert "floor" in val_data["model_estimate_range"]
    assert "fair" in val_data["model_estimate_range"]
    assert "ceiling" in val_data["model_estimate_range"]
