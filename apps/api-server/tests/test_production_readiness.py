import time

import pytest
from pydantic import ValidationError

from src.core.config import Settings
from src.core.idempotency import (
    IdempotencyConflict,
    InMemoryIdempotencyStore,
    request_fingerprint,
)
from src.core.security import create_access_token, decode_token
from src.core.webhooks import verify_hmac_signature
from src.api.v1.endpoints import health as health_endpoint
from src.services.otp_service import OtpService


def test_production_settings_reject_development_values():
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="production", DEBUG=False)


def test_jwt_has_and_validates_audience_and_issuer():
    token = create_access_token("user-id", "COLLECTOR")
    claims = decode_token(token)
    assert claims["iss"] == "ecobridge-api"
    assert claims["aud"] == "ecobridge-clients"


def test_idempotency_fingerprint_conflict_is_detected():
    store = InMemoryIdempotencyStore()
    first = request_fingerprint("actor", "key", b"{}")
    second = request_fingerprint("actor", "key", b'{"changed":true}')
    store.save("key", type("Record", (), {"fingerprint": first})())
    with pytest.raises(IdempotencyConflict):
        store.get_or_reserve("key", second)


def test_webhook_signature_checks_payload_and_replay_window():
    payload = b'{"event":"paid"}'
    timestamp = int(time.time())
    import hmac
    import hashlib

    signature = hmac.new(
        b"secret", f"{timestamp}.".encode() + payload, hashlib.sha256
    ).hexdigest()
    assert verify_hmac_signature(payload, signature, "secret", timestamp)
    assert not verify_hmac_signature(b"tampered", signature, "secret", timestamp)


@pytest.mark.asyncio
async def test_readiness_returns_structured_ready_response(client, monkeypatch):
    async def database_is_ready():
        return True

    monkeypatch.setattr(health_endpoint, "check_database_connection", database_is_ready)
    response = await client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "READY"


@pytest.mark.asyncio
async def test_otp_is_one_time_and_attempt_limited():
    service = OtpService()
    phone = "+919876543211"
    code = await service.generate_and_send_otp(phone)
    assert service.verify_otp(phone, code) is True
    assert service.verify_otp(phone, code) is False

    service = OtpService()
    phone = "+919876543212"
    code = await service.generate_and_send_otp(phone)
    assert service.verify_otp(phone, "000000") is False
    assert service.verify_otp(phone, "000000") is False
    assert service.verify_otp(phone, "000000") is False
    assert service.verify_otp(phone, "000000") is False
    assert service.verify_otp(phone, "000000") is False
    assert service.verify_otp(phone, code) is False


@pytest.mark.asyncio
async def test_payment_fallback_never_fabricates_transaction_reference(client):
    response = await client.post(
        "/api/v1/payments/confirm",
        json={"lot_id": "ECO-26-MH-004821", "amount": 10, "payment_method": "UPI"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "PENDING_PROVIDER_CONFIGURATION"
    assert data["provider_configured"] is False
    assert data["txn_reference"] is None
