from fastapi import FastAPI,Request
from datetime import datetime
from fastapi import HTTPException
import json
import uuid

from schemas.endpoint import EndpointCreate, EndpointResponse
from services.endpoint_service import endpoint_service
from storage.store import endpoint_store

app = FastAPI(
    title="Webhook Debugger",
    description="Test webhooks in real-time with AI-generated mock responses",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/")
async def root():
    return {
        "app": "Webhook Debugger",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
             },
        "message": "Welcome! Check /docs for API documentation."
         },


@app.get("/health")
async def health_check():
    return {
        "status" : "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "webhook-debugger",
    }


@app.post("/endpoints",response_model=EndpointResponse,summary="Create Endpoint")
async def create_endpoint(endpoint: EndpointCreate):
    endpoint_data = endpoint_service.create_endpoint(name=endpoint.name)

    return EndpointResponse(**endpoint_data)


@app.get("/endpoints/{endpoint_id}", response_model=EndpointResponse,summary="Get Endpoint Details")
async def get_endpoint(endpoint_id: str):
    endpoint_data = endpoint_service.get_endpoint(endpoint_id)

    if not endpoint_data:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    return EndpointResponse(**endpoint_data)

@app.api_route("/w/{endpoint_id}", methods=["GET", "POST", "PATCH", "PUT", "DELETE"],summary="Receive Webhook")
async def receive_webhook(endpoint_id: str, request: Request):
   result = await endpoint_service.receive_webhook(endpoint_id,request)
   return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

