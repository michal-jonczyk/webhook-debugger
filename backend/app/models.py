from pydantic import BaseModel
from datetime import datetime
from typing import Optional,Dict,Any

class EndpointCreate(BaseModel):
    name: str = None


class EndpointResponse(BaseModel):
    id: str
    url: str
    name: str = None
    created_at: datetime


class WebhookRequest(BaseModel):
    id: str
    timestamp: datetime
    method: str
    headers: Dict[str, str]
    body_raw: str
    body_json: Optional[Dict[str, Any]] = None
    content_type: Optional[str] = None
    content_length: int = 0
    ip_address: Optional[str] = None
    query_params: Dict[str, str] = {}