import pytest


@pytest.mark.asyncio
async def test_health_check_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert "timestamp" in payload

    data = payload["data"]
    assert "status" in data
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "database_connected" in data
    assert isinstance(data["database_connected"], bool)
    assert data["version"] == "0.1.0"
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0

    # Header check
    assert "x-process-time" in response.headers


@pytest.mark.asyncio
async def test_liveness_probe_endpoint(client):
    response = await client.get("/api/v1/health/liveness")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["alive"] is True
