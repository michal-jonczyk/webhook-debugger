from fastapi import FastAPI,Request
from datetime import datetime
import uuid
from fastapi import HTTPException
import json

from schemas.endpoint import EndpointCreate, EndpointResponse
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


@app.get("/endpoints/{endpoint_id}", response_model=EndpointResponse,summary="Get Endpoint Details")
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


@app.api_route("/w/{endpoint_id}", methods=["GET", "POST", "PATCH", "PUT", "DELETE"],summary="Receive Webhook")
async def receive_webhook(endpoint_id: str, request: Request):
    endpoint_data = endpoint_store.get(endpoint_id)
    if not endpoint_data:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    body_raw = await request.body()
    body_text = body_raw.decode("utf-8")

    body_json = None
    try:
        if body_text:
            body_json = json.loads(body_text)
    except json.decoder.JSONDecodeError:
        pass

    client_ip = request.client.host if request.client else None

    request_id = str(uuid.uuid4())
    webhook_data = {
        "id": request_id,
        "timestamp": datetime.now(),
        "method": request.method,
        "headers": dict(request.headers),
        "body_raw": body_text,
        "body_json": body_json,
        "content_type": request.headers.get("content-type"),
        "content_length": len(body_raw),
        "ip_address": client_ip,
        "query_params": dict(request.query_params),
    }

    endpoint_store.add_request(endpoint_id, webhook_data)
    return {
        "status": "received",
        "endpoint_id": endpoint_id,
        "request_id": request_id,
        "received_at": datetime.now().isoformat(),
        "total_requests": endpoint_data["request_count"] + 1
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
