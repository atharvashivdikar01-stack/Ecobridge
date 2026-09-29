import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_benchmark_prices(client: AsyncClient, init_test_db):
    """Test that GET /api/v1/prices returns the 8 benchmark e-waste categories."""
    response = await client.get("/api/v1/prices")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]

    items = data["data"]["items"]
    assert len(items) >= 8

    # Verify standard catalog codes exist
    codes = {item["category_code"] for item in items}
    assert "CAT_BATTERY" in codes
    assert "CAT_PCB" in codes
    assert "CAT_CRT" in codes
    assert "CAT_CABLES" in codes

    # Check structure of a price item
    for item in items:
        assert "benchmark_price_per_kg" in item
        assert item["benchmark_price_per_kg"] > 0
        assert "default_hazard" in item
        assert item["default_hazard"] in ["HAZARD", "WARNING", "NORMAL"]
