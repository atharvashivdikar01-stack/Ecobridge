import random
import time
from typing import Dict, Tuple
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger("ecobridge.otp")


class OtpService:
    """Manages OTP generation, time-to-live caching, and validation."""

    def __init__(self) -> None:
        # In-memory store: phone -> (otp_code, expires_at_timestamp)
        self._otp_store: Dict[str, Tuple[str, float]] = {}

    def generate_and_send_otp(self, phone: str) -> str:
        """Generates a 6-digit OTP code and records it with expiry."""
        # For testing / dev, support test phone or default test OTP if enabled
        if settings.ENVIRONMENT in ["development", "test"] and settings.TEST_OTP and phone.endswith("123456"):
            otp_code = settings.TEST_OTP
        else:
            otp_code = f"{random.randint(100000, 999999)}"

        expires_at = time.time() + (settings.OTP_EXPIRE_MINUTES * 60)
        self._otp_store[phone] = (otp_code, expires_at)

        logger.info(f"Generated OTP for phone {phone}: {otp_code} (Expires in {settings.OTP_EXPIRE_MINUTES}m)")
        # In production, this dispatches via SMS provider (Twilio / AWS SNS / Gupshup)
        return otp_code

    def verify_otp(self, phone: str, otp: str) -> bool:
        """Validates provided OTP against stored record or static test code in dev mode."""
        # Always allow test OTP in test / dev environment for testing convenience
        if settings.ENVIRONMENT in ["development", "test"] and settings.TEST_OTP and otp == settings.TEST_OTP:
            logger.info(f"Verified via default test OTP for phone: {phone}")
            return True

        record = self._otp_store.get(phone)
        if not record:
            logger.warning(f"No OTP record found for phone: {phone}")
            return False

        stored_otp, expires_at = record
        if time.time() > expires_at:
            logger.warning(f"OTP expired for phone: {phone}")
            self._otp_store.pop(phone, None)
            return False

        if stored_otp != otp:
            logger.warning(f"Invalid OTP entered for phone: {phone}")
            return False

        # One-time use: invalidate on successful verification
        self._otp_store.pop(phone, None)
        logger.info(f"OTP successfully verified for phone: {phone}")
        return True


otp_service = OtpService()
