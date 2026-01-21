from fastapi import APIRouter, HTTPException
from schemas.endpoint import EndpointCreate,EndpointResponse
from services.endpoint_service import endpoint_service

router = APIRouter(
    prefix="/endpoints",
    tags=["endpoints"]
)

@router.post(
    "",
    response_model=EndpointResponse,
    summary="Create Webhook Endpoint",
    status_code=201
)

async def create_endpoint(endpoint: EndpointCreate):
    endpoint_data = endpoint_service.create_endpoint(name=endpoint.name)
    return EndpointResponse(**endpoint_data)


@router.get(
    "/{endpoint_id}",
    response_model=EndpointResponse,
    summary="Get Endpoint Details"
)
async def get_endpoint(endpoint_id: str):
    endpoint_data = endpoint_service.get_endpoint(endpoint_id)

    if not endpoint_data:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    return EndpointResponse(**endpoint_data)
