from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

