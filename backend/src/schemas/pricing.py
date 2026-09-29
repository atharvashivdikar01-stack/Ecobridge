from pydantic import BaseModel
from typing import Optional,List
class CreatePriceObservationRequest(BaseModel): material_id:str; price_per_unit:float; region:Optional[str]=None
class CreateRecyclerOfferRequest(BaseModel): material_id:str; price_per_unit:float; recycler_id:Optional[str]=None
class ObservedPriceDetail(BaseModel): material_id:str; price_per_unit:float
class RecyclerOfferDetail(ObservedPriceDetail): pass
class MaterialPriceIntelligenceResponse(BaseModel): material_id:str; observations:list=[]; offers:list=[]
class LotValuationResponse(BaseModel): lot_id:str; estimated_value:float

class BenchmarkPriceItem(BaseModel):
    category_code: str
    material_code: str
    name: str
    benchmark_price_per_kg: float
    min_price_per_kg: float
    max_price_per_kg: float
    default_hazard: str
    effective_from: Optional[str] = None

class BenchmarkPriceListResponse(BaseModel):
    items: List[BenchmarkPriceItem]
    currency: str = "INR"
    unit: str = "kg"
