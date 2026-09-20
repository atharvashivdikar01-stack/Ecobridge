import pytest


async def get_authenticated_collector_token(client, phone: str = "+919876599901") -> str:
    """Helper to authenticate a test collector and return access token."""
    resp = await client.post(
        "/api/v1/auth/otp/verify",
        json={
            "phone": phone,
            "otp": "123456",
            "full_name": "Deepak Scrappy",
            "collector_type": "SCRAP_AGGREGATOR",
            "preferred_language": "hi",
        },
    )
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_get_collector_profile_success(client):
    token = await get_authenticated_collector_token(client, "+919876599901")
    resp = await client.get(
        "/api/v1/collectors/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    payload = resp.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["phone"] == "+919876599901"
    assert data["full_name"] == "Deepak Scrappy"
    assert data["collector_type"] == "SCRAP_AGGREGATOR"
    assert data["trust_score"] == 1.0
    assert data["total_lots_collected"] == 0
    assert data["total_weight_kg"] == 0.0
    assert data["is_verified"] is False


@pytest.mark.asyncio
async def test_update_collector_profile_success(client):
    token = await get_authenticated_collector_token(client, "+919876599902")

    update_payload = {
        "full_name": "Deepak Sharma",
        "preferred_language": "mr",
        "upi_id": "deepak@okaxis",
        "bank_account_number": "123456789012",
        "ifsc_code": "SBIN0001234",
    }
    patch_resp = await client.patch(
        "/api/v1/collectors/profile",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 200

    data = patch_resp.json()["data"]
    assert data["full_name"] == "Deepak Sharma"
    assert data["preferred_language"] == "mr"
    assert data["upi_id"] == "deepak@okaxis"
    assert data["bank_account_number"] == "123456789012"
    assert data["ifsc_code"] == "SBIN0001234"


@pytest.mark.asyncio
async def test_update_collector_profile_invalid_upi(client):
    token = await get_authenticated_collector_token(client, "+919876599903")

    patch_resp = await client.patch(
        "/api/v1/collectors/profile",
        json={"upi_id": "not-a-valid-upi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 422

    payload = patch_resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_update_collector_profile_invalid_ifsc(client):
    token = await get_authenticated_collector_token(client, "+919876599904")

    patch_resp = await client.patch(
        "/api/v1/collectors/profile",
        json={"ifsc_code": "12345"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_resp.status_code == 422

    payload = patch_resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_submit_collector_kyc_success(client):
    token = await get_authenticated_collector_token(client, "+919876599905")

    kyc_payload = {
        "national_id_type": "AADHAAR",
        "national_id_number": "9876-5432-1098",
    }
    kyc_resp = await client.post(
        "/api/v1/collectors/profile/kyc",
        json=kyc_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert kyc_resp.status_code == 200

    data = kyc_resp.json()["data"]
    assert data["national_id_type"] == "AADHAAR"
    assert data["national_id_number"] == "9876-5432-1098"
    assert data["is_verified"] is True
    assert data["verified_at"] is not None


@pytest.mark.asyncio
async def test_get_collector_stats(client):
    token = await get_authenticated_collector_token(client, "+919876599906")

    stats_resp = await client.get(
        "/api/v1/collectors/profile/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_resp.status_code == 200

    data = stats_resp.json()["data"]
    assert "total_lots_collected" in data
    assert "total_weight_kg" in data
    assert "trust_score" in data
    assert data["trust_score"] == 1.0


@pytest.mark.asyncio
async def test_collector_profile_unauthorized(client):
    resp = await client.get("/api/v1/collectors/profile")
    assert resp.status_code == 401

    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "UNAUTHORIZED"
