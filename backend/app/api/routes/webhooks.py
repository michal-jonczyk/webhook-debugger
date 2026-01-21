from fastapi import APIRouter,Request
from services.endpoint_service import endpoint_service

router = APIRouter(
    prefix="/w",
    tags=["webhooks"],
)

@router.api_route(
    "/{endpoint_id}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    summary="Receive Webhook"
)
async def receive_webhook(endpoint_id: str, request: Request):
    result = await endpoint_service.receive_webhook(endpoint_id, request)
    return result