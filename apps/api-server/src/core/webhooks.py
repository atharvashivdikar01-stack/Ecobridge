"""Provider-neutral webhook authenticity and replay-window validation."""
import hashlib
import hmac
import time


def verify_hmac_signature(
    payload: bytes,
    signature: str,
    secret: str,
    timestamp: int,
    *,
    tolerance_seconds: int = 300,
) -> bool:
    if not secret or not signature or abs(int(time.time()) - timestamp) > tolerance_seconds:
        return False
    signed = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
