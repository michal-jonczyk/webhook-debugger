from fastapi import FastAPI
from datetime import datetime
import uuid
from fastapi import HTTPException

from models import EndpointCreate, EndpointResponse
from storage import endpoint_store

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


@app.post("/endpoints",response_model=EndpointResponse)
async def create_endpoint(endpoint: EndpointCreate):
    endpoint_id = str(uuid.uuid4())

    endpoint_data = endpoint_store.create(
        endpoint_id=endpoint_id,
        name=endpoint.name
    )

    webhook_url = f"http://localhost:8000/w/{endpoint_id}"

    return EndpointResponse(
        id = endpoint_data["id"],
        url = webhook_url,
        name = endpoint_data["name"],
        created_at = endpoint_data["created_at"]
    )


@app.get("/endpoints/{endpoint_id}", response_model=EndpointResponse)
async def get_endpoint(endpoint_id: str):
    endpoint_data = endpoint_store.get(endpoint_id)

    if not endpoint_data:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    webhook_url = f"http://localhost:8000/w/{endpoint_id}"

    return EndpointResponse(
        id=endpoint_data["id"],
        url=webhook_url,
        name=endpoint_data["name"],
        created_at=endpoint_data["created_at"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
