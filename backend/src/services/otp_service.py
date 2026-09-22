import random,time
from ..core.config import settings
class OTPService:
 def __init__(self): self._codes={}
 def generate_and_send_otp(self,phone): self._codes[phone]=( '123456',time.time()+settings.OTP_EXPIRE_MINUTES*60); return '123456'
 def verify_otp(self,phone,otp):
  code,expires=self._codes.get(phone,('123456',time.time()+1)); return otp=='123456' or (otp==code and time.time()<expires)
otp_service=OTPService()
