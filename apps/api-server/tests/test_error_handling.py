import pytest


@pytest.mark.asyncio
async def test_not_found_endpoint(client):
    response = await client.get("/api/v1/non-existent-endpoint-path")
    assert response.status_code == 404

    payload = response.json()
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["error"]["code"] == "NOT_FOUND"
    assert "timestamp" in payload


@pytest.mark.asyncio
async def test_validation_error_handler(client):
    # Missing required field "amount", and name is wrong type
    response = await client.post("/api/v1/test/validate", json={"name": 12345})
    assert response.status_code == 422

    payload = response.json()
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(payload["error"]["details"], list)
    assert len(payload["error"]["details"]) > 0


@pytest.mark.asyncio
async def test_custom_app_exception_handler(client):
    response = await client.get("/api/v1/test/app-exception")
    assert response.status_code == 400

    payload = response.json()
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["error"]["code"] == "CUSTOM_ERROR"
    assert payload["error"]["message"] == "Test custom exception"
    assert payload["error"]["details"] == {"info": "extra"}


@pytest.mark.asyncio
async def test_custom_not_found_error_handler(client):
    response = await client.get("/api/v1/test/not-found")
    assert response.status_code == 404

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "NOT_FOUND"
    assert "does not exist" in payload["error"]["message"]


@pytest.mark.asyncio
async def test_unhandled_exception_handler(client):
    response = await client.get("/api/v1/test/unhandled-error")
    assert response.status_code == 500

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "unexpected server error" in payload["error"]["message"]
