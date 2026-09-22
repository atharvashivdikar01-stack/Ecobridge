from typing import Generic,TypeVar,Optional
from pydantic import BaseModel
T=TypeVar('T')
class ApiResponse(BaseModel,Generic[T]):
    success:bool=True
    data:Optional[T]=None
    error:Optional[dict]=None
    @classmethod
    def create_success(cls,data): return cls(success=True,data=data)
