import random
import time
from ..core.config import settings


class OTPService:
    def __init__(self):
        self._codes: dict[str, tuple[str, float]] = {}

    def generate_and_send_otp(self, phone: str) -> str:
        if settings.DEMO_MODE:
            code = "123456"
        else:
            code = f"{random.randint(100000, 999999)}"
        self._codes[phone] = (code, time.time() + settings.OTP_EXPIRE_MINUTES * 60)
        return code

    def verify_otp(self, phone: str, otp: str) -> bool:
        record = self._codes.get(phone)
        if record:
            code, expires = record
            if time.time() <= expires and otp == code:
                return True
        # Static demo fallback ONLY allowed when DEMO_MODE is True
        if settings.DEMO_MODE and otp == "123456":
            return True
        return False


otp_service = OTPService()
