from typing import Optional
from pydantic import BaseModel,Field
class SendOtpRequest(BaseModel): phone:str
class SendOtpResponse(BaseModel): phone:str; message:str; expires_in_seconds:int
class VerifyOtpRequest(BaseModel): phone:str; otp:str; full_name:Optional[str]=None; collector_type:Optional[str]=None; preferred_language:Optional[str]='en'
class RefreshTokenRequest(BaseModel): refresh_token:str
class DemoLoginRequest(BaseModel): role:str='VERIFIED_RECYCLER'
class UserSummary(BaseModel): id:str; phone:str; full_name:str; role:str; status:str; preferred_language:str; avatar_url:Optional[str]=None
class TokenResponse(BaseModel): access_token:str; refresh_token:str; token_type:str; expires_in:int; user:UserSummary
