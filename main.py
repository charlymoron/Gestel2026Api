from fastapi import FastAPI

from app.api.v1.cliente_router import cliente_router
from app.api.v1.process_routes import process_router

app = FastAPI(
    title="Trap Processor API",
    description="API para procesar archivos de traps de telecomunicaciones",
    version="1.0.0",
)

app.include_router(process_router)
app.include_router(cliente_router)

@app.get("/")
async def root():
    return {
        "message": "Trap Processor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "trapProcessor": "/trapProcessor/"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
