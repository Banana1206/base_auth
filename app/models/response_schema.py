from typing import Any, Optional
from pydantic import BaseModel

class ResponseModel(BaseModel):
    status: bool
    data: Optional[Any] = None
    message: str
