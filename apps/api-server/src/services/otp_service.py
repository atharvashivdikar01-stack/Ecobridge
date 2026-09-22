import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from typing import Dict

from ..core.config import settings
from ..core.providers import DevelopmentOtpProvider, OtpProvider, ProviderUnavailable


@dataclass
class OtpRecord:
    digest: str
    expires_at: float
    attempts: int = 0


class OtpService:
    """Short-lived, one-time OTP verification with a provider-safe fallback."""

    def __init__(self, provider: OtpProvider | None = None) -> None:
        self._otp_store: Dict[str, OtpRecord] = {}
        self.provider = provider or DevelopmentOtpProvider()

    @staticmethod
    def _digest(phone: str, otp: str) -> str:
        return hashlib.sha256(f"{phone}:{otp}".encode()).hexdigest()

    async def generate_and_send_otp(self, phone: str) -> str:
        # Test OTP remains available only to preserve local/test workflows.
        if settings.ENVIRONMENT in {"development", "test"} and phone.endswith("123456"):
            otp_code = settings.TEST_OTP
        else:
            otp_code = f"{secrets.randbelow(1_000_000):06d}"
        self._otp_store[phone] = OtpRecord(
            digest=self._digest(phone, otp_code),
            expires_at=time.time() + settings.OTP_EXPIRE_MINUTES * 60,
        )
        try:
            await self.provider.send(phone, otp_code)
        except ProviderUnavailable:
            # Explicit local fallback: code is not logged or represented as delivered.
            pass
        return otp_code

    def verify_otp(self, phone: str, otp: str) -> bool:
        # This compatibility path is deliberately limited to non-production.
        if settings.ENVIRONMENT in {"development", "test"} and otp == settings.TEST_OTP:
            self._otp_store.pop(phone, None)
            return True
        record = self._otp_store.get(phone)
        if not record or time.time() > record.expires_at:
            self._otp_store.pop(phone, None)
            return False
        if record.attempts >= settings.OTP_MAX_ATTEMPTS:
            self._otp_store.pop(phone, None)
            return False
        record.attempts += 1
        if not hmac.compare_digest(record.digest, self._digest(phone, otp)):
            if record.attempts >= settings.OTP_MAX_ATTEMPTS:
                self._otp_store.pop(phone, None)
            return False
        self._otp_store.pop(phone, None)
        return True


otp_service = OtpService()
