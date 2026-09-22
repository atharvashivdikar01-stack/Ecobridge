from pydantic import BaseModel
from typing import Optional,List
class RegisterRecyclerRequest(BaseModel): company_name:str; trade_license_number:Optional[str]=None; gst_number:Optional[str]=None; cpcb_registration_no:Optional[str]=None; contact_person:Optional[str]=None; contact_phone:Optional[str]=None; facility_name:str='Primary Facility'
class UpdateRecyclerCompanyRequest(BaseModel): company_name:Optional[str]=None; gst_number:Optional[str]=None; contact_person:Optional[str]=None; contact_phone:Optional[str]=None
class CreateFacilityRequest(BaseModel): facility_name:str; address_line1:Optional[str]=None; city:Optional[str]=None; state:Optional[str]=None; postal_code:Optional[str]=None; latitude:Optional[float]=None; longitude:Optional[float]=None; daily_capacity_kg:Optional[float]=None; accepts_hazardous:bool=False
class CreateAuthorizationRequest(BaseModel): authorization_type:str; authorization_number:str
class VerifyRecyclerRequest(BaseModel): status:str
class ConfigureAcceptedMaterialRequest(BaseModel): material_id:str; price_per_kg:float; min_weight_kg:float=0
class CreateServiceAreaRequest(BaseModel): city:str; state:Optional[str]=None; postal_codes:List[str]=[]
class UpdatePickupAvailabilityRequest(BaseModel): pickup_available:bool; minimum_weight_kg:float=0; max_distance_km:float=0
class RecyclerCompanyResponse(BaseModel): id:str; company_name:str; operating_status:str
class FacilityResponse(BaseModel): id:str; facility_name:str
class AuthorizationResponse(BaseModel): id:str; authorization_type:str; authorization_number:str
class AcceptedMaterialResponse(BaseModel): id:str; material_id:str; price_per_kg:float
class ServiceAreaResponse(BaseModel): id:str; city:str
class PickupAvailabilityResponse(BaseModel): facility_id:str; pickup_available:bool
class VerificationStatusResponse(BaseModel): id:str; operating_status:str
class RecyclerDirectoryListResponse(BaseModel): recyclers:list
