from pydantic import BaseModel
from datetime import datetime


class EndpointCreate(BaseModel):
    name: str = None


class EndpointResponse(BaseModel):
    id: str
    url: str
    name: str = None
    created_at: datetime
    