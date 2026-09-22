from pydantic import BaseModel
from typing import Optional
class CollectorProfileUpdate(BaseModel): full_name:Optional[str]=None; preferred_language:Optional[str]=None; upi_id:Optional[str]=None; bank_account_number:Optional[str]=None
class CollectorKycSubmission(BaseModel): national_id_number:str; national_id_type:str
class CollectorProfileResponse(BaseModel): id:str; user_id:str; full_name:str; phone:str; collector_type:str; trust_score:float; total_lots_collected:int; total_weight_kg:float
class CollectorStatsResponse(BaseModel): total_lots_collected:int; total_weight_kg:float; trust_score:float
