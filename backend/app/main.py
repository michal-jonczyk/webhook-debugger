from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, List

from api.routes import endpoints, webhooks
from core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Test webhooks in real-time with AI-generated mock responses",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

allowed_origins = settings.get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, endpoint_id: str, websocket: WebSocket):
        await websocket.accept()
        if endpoint_id not in self.active_connections:
            self.active_connections[endpoint_id] = []
        self.active_connections[endpoint_id].append(websocket)
        print(f"✅ WebSocket connected for endpoint: {endpoint_id}")

    def disconnect(self, endpoint_id: str, websocket: WebSocket):
        if endpoint_id in self.active_connections:
            self.active_connections[endpoint_id].remove(websocket)
            if not self.active_connections[endpoint_id]:
                del self.active_connections[endpoint_id]
        print(f"❌ WebSocket disconnected for endpoint: {endpoint_id}")

    async def broadcast_new_request(self, endpoint_id: str, request_data: dict):
        if endpoint_id in self.active_connections:
            dead_connections = []

            for connection in self.active_connections[endpoint_id]:
                try:
                    await connection.send_json({
                        "type": "new_request",
                        "data": request_data
                    })
                    print(f"📤 Sent notification to WebSocket for {endpoint_id}")
                except Exception as e:
                    print(f"❌ Error sending to WebSocket: {e}")
                    dead_connections.append(connection)

            for dead in dead_connections:
                self.disconnect(endpoint_id, dead)


manager = ConnectionManager()


app.include_router(endpoints.router)
app.include_router(webhooks.router)


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
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "webhook-debugger",
    }


@app.websocket("/ws/{endpoint_id}")
async def websocket_endpoint(websocket: WebSocket, endpoint_id: str):
    await manager.connect(endpoint_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(endpoint_id, websocket)
        print(f"🔌 Client disconnected from {endpoint_id}")


from services.endpoint_service import endpoint_service

endpoint_service.set_websocket_manager(manager)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
