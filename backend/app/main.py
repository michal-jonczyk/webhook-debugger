from fastapi import FastAPI
from datetime import datetime

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
