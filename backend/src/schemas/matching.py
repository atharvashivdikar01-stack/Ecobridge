from pydantic import BaseModel
class EvaluateManifestRequest(BaseModel): items:list; origin_latitude:float|None=None; origin_longitude:float|None=None
class LotMatchingResponse(BaseModel): matches:list=[]
