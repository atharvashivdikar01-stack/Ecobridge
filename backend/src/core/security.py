from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from .config import settings
from .exceptions import UnauthorizedError
def create_access_token(subject,role,extra_claims=None):
 p={'sub':str(subject),'role':role,'type':'access','exp':datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}; p.update(extra_claims or {}); return jwt.encode(p,settings.SECRET_KEY,algorithm='HS256')
def create_refresh_token(subject): return jwt.encode({'sub':str(subject),'type':'refresh','exp':datetime.now(timezone.utc)+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)},settings.SECRET_KEY,algorithm='HS256')
def decode_token(token):
 try:return jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
 except JWTError as e: raise UnauthorizedError('Invalid or expired token') from e
