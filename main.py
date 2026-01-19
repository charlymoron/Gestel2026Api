from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
import logging


from app.api.v1 import api_v1_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
app = FastAPI(
    title="Trap Processor API",
    description="API para procesar archivos de traps de telecomunicaciones",
    version="1.0.0",
)

# Agregar middleware de logging
app.add_middleware(LoggingMiddleware)

# Opcional: CORS si tenés frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustá según necesites
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_v1_router)



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
