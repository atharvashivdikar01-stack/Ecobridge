import pytest


@pytest.mark.asyncio
async def test_send_otp_success(client):
    response = await client.post("/api/v1/auth/otp/send", json={"phone": "+919876543210"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert payload["data"]["phone"] == "+919876543210"
    assert "expires_in_seconds" in payload["data"]


@pytest.mark.asyncio
async def test_send_otp_invalid_phone(client):
    response = await client.post("/api/v1/auth/otp/send", json={"phone": "123"})
    assert response.status_code == 422

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_verify_otp_new_collector_registration(client):
    # Send OTP first
    phone = "+919876500001"
    await client.post("/api/v1/auth/otp/send", json={"phone": phone})

    # Verify using the default test OTP in test environment
    verify_resp = await client.post(
        "/api/v1/auth/otp/verify",
        json={
            "phone": phone,
            "otp": "123456",
            "full_name": "Ramesh Kumar",
            "collector_type": "KABADIWALA",
            "preferred_language": "hi",
        },
    )
    assert verify_resp.status_code == 200

    payload = verify_resp.json()
    assert payload["success"] is True
    data = payload["data"]

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

    user = data["user"]
    assert user["phone"] == phone
    assert user["full_name"] == "Ramesh Kumar"
    assert user["role"] == "COLLECTOR"
    assert user["preferred_language"] == "hi"


@pytest.mark.asyncio
async def test_verify_otp_existing_collector_login(client):
    phone = "+919876500002"

    # Register first
    await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": phone, "otp": "123456", "full_name": "Sita Devi"},
    )

    # Login again
    login_resp = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": phone, "otp": "123456"},
    )
    assert login_resp.status_code == 200

    payload = login_resp.json()
    assert payload["success"] is True
    user = payload["data"]["user"]
    assert user["full_name"] == "Sita Devi"
    assert user["phone"] == phone


@pytest.mark.asyncio
async def test_verify_otp_invalid_code(client):
    response = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+919876500003", "otp": "000000"},
    )
    assert response.status_code == 400

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INVALID_OTP"


@pytest.mark.asyncio
async def test_refresh_token_flow(client):
    # Register collector to get tokens
    auth_resp = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+919876500004", "otp": "123456", "full_name": "Anil Aggregator"},
    )
    refresh_token = auth_resp.json()["data"]["refresh_token"]

    # Refresh
    refresh_resp = await client.post(
        "/api/v1/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200

    payload = refresh_resp.json()
    assert payload["success"] is True
    assert "access_token" in payload["data"]
    assert "refresh_token" in payload["data"]


@pytest.mark.asyncio
async def test_auth_me_endpoint(client):
    # 1. Without token -> 401
    resp_unauth = await client.get("/api/v1/auth/me")
    assert resp_unauth.status_code == 401

    # 2. With valid token -> 200
    auth_resp = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+919876500005", "otp": "123456", "full_name": "Meera Waste Picker"},
    )
    token = auth_resp.json()["data"]["access_token"]

    resp_auth = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_auth.status_code == 200

    payload = resp_auth.json()
    assert payload["success"] is True
    assert payload["data"]["phone"] == "+919876500005"
    assert payload["data"]["full_name"] == "Meera Waste Picker"
